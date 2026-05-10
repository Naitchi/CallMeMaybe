import numpy as np
import argparse
import time
from typing import Any

from llm_sdk import Small_LLM_Model
from .parsing import JSONFileService


class CallMeMaybeApp:
    """Main application for function calling with a small LLM model.
    This application processes prompts and uses constrained decoding to
    generate JSON responses that call appropriate functions based on the
    available function definitions.
    Attributes:
        file_service: Service for handling JSON file I/O operations.
        model: The small LLM model used for generating responses.
    """
    def __init__(self) -> None:
        """Initialize the CallMeMaybeApp with file service and LLM model."""
        self.file_service = JSONFileService()
        self.model = Small_LLM_Model()

    def generate_next_token(self, tokens: list[int]) -> int:
        """Generate the next token based on logits without constraints.
        Args:
            tokens: List of token IDs to extend with the next token.
        Returns:
            The token ID with the highest logit value.
        """
        possible_token = np.asarray(
            self.model.get_logits_from_input_ids(tokens),
            dtype=float,
        )
        next_token: int = int(np.argmax(possible_token))
        tokens.append(next_token)
        return next_token

    def check_for_ended_response(self, response: str) -> bool:
        """Check if a JSON response has unclosed brackets or braces.
        Validates that all opening brackets/braces have matching closing ones.
        Returns True if there are still unclosed brackets or braces, indicating
        the response needs to continue being generated.
        Args:
            response: The JSON response string to check.
        Returns:
            True if there are unclosed brackets/braces, False otherwise.
        """
        accolades: list[str] = []
        for char in response:
            if char == '[' or char == '{':
                accolades.append(char)
            if char == ']' or char == '}':
                if not accolades:
                    return False
                if (
                    (accolades[-1] == '[' and char == ']')
                    or (accolades[-1] == '{' and char == '}')
                ):
                    accolades.pop(-1)
                else:
                    return False
        if len(accolades) < 1:
            return False
        return True

    def get_function_names(
            self,
            available_func: list[dict[str, Any]]
            ) -> list[int]:
        """Extract and tokenize function names for constrained decoding.
        Args:
            available_func: List of function definition dictionaries.
        Returns:
            A set of unique token IDs that make up the function names,
            including token 497 (likely a delimiter or special token).
        """
        token_names: list[int] = []
        for func in available_func:
            token_names.extend(
                [int(token) for token in self.model.encode(func["name"])[0]]
            )
        token_names.append(497)
        return list(set(token_names))

    def create_prompt(
            self,
            prompt: str,
            available_functions: str
            ) -> tuple[str, str]:
        """Create the full prompt and response prefix for the LLM.
        Args:
            prompt: The user prompt to include in the instruction.
            available_functions: String representation of available
                functions.
        Returns:
            A tuple containing:
            - The full instruction prompt for the model.
            - The response prefix to initialize generation.
        Raises:
            ValueError: If the prompt is empty.
        """
        if len(prompt) < 1:
            raise ValueError("Error the prompt cannot be empty")
        prompt = prompt.replace('"', "\\\"")
        return (
            "".join([
                "With this prompt:\"",
                prompt,
                "\"Use this list of function:",
                available_functions,
                "and return only JSON with prompt (prompt), the name of the "
                "function",
                " (name) you will use, and the parameters (parameters).",
                "The Answer:{",
                "\"prompt\":\"",
                prompt,
                "\",\"name\":\""
            ]),
            "".join([
                "{\"prompt\":\"",
                prompt,
                "\",\"name\":\""
            ])
        )

    def constained_decoding(
            self,
            tokens: list[int],
            tokens_func_name: list[int]
            ) -> int:
        """Generate next token constrained to function name tokens.
        Uses constrained decoding to ensure generated tokens correspond
        only to tokens that are part of available function names.
        Args:
            tokens: List of token IDs to extend with the next
                constrained token.
            tokens_func_name: List of valid token IDs for function names.
        Returns:
            The token ID with the highest logit among the constrained set.
        """
        possible_token = np.asarray(
            self.model.get_logits_from_input_ids(tokens),
            dtype=float,
        )
        constrained_token = np.full_like(
            possible_token,
            fill_value=-np.inf,
            dtype=float,
        )
        for token in tokens_func_name:
            constrained_token[token] = possible_token[token]
        next_token: int = int(np.argmax(constrained_token))
        tokens.append(next_token)
        return next_token

    def run(self) -> None:
        """Main execution method for the function calling workflow.
        Loads function definitions and prompts, performs constrained
        generation to produce JSON responses with function calls, and
        writes results to output. Processes command-line arguments for
        file paths and handles exceptions during processing.
        """
        parser = argparse.ArgumentParser(description="CallMeMaybe")

        parser.add_argument(
            "--functions_definition",
            type=str,
            default="./data/input/functions_definition.json",
            help="Input file for functions"
        )
        parser.add_argument(
            "--input",
            type=str,
            default="./data/input/function_calling_tests.json",
            help="Input file for prompt list"
        )
        parser.add_argument(
            "--output",
            type=str,
            default="./data/output/function_calling_results.json",
            help="Output file for results"
        )
        args = parser.parse_args()
        available_functions: list[dict[str, Any]] = (
            self.file_service.get_functions_json(
                args.functions_definition
            )
        )
        for funct in available_functions:
            del funct["returns"]
        prompts: list[dict[str, Any]] = self.file_service.get_prompts_json(
            args.input
        )
        answers: list[str] = []
        start = time.perf_counter()
        tokens_func_name: list[int] = self.get_function_names(
            available_functions
        )
        for user_prompt in prompts:
            try:
                response: str = ""
                prompt: str = ""
                generate_name: bool = True
                (prompt, response) = self.create_prompt(
                    user_prompt["prompt"],
                    str(available_functions)
                )
                tokens = self.model.encode(prompt)
                converted_list = list(tokens[0])
                while generate_name:
                    response = "".join([
                        response,
                        self.model.decode([
                            self.constained_decoding(
                                converted_list,
                                tokens_func_name
                            )
                        ])
                    ])
                    if response.count('"') % 2 < 1:
                        generate_name = False
                        response = "".join([response, '\"parameters\":{ '])
                        converted_list.extend(
                            self.model.encode('\"parameters\":{ ')[0]
                        )
                while self.check_for_ended_response(response):
                    response = "".join([
                        response,
                        self.model.decode(
                            [
                                self.generate_next_token(converted_list)
                            ]
                        )
                    ])
                response = self.file_service.sanitize_llm_json_response(
                    response
                )
                answers.append(response)
                print(response)
                print(time.perf_counter() - start)
            except (
                FileNotFoundError,
                FileExistsError,
                ValueError,
                Exception
            ) as e:
                print(e)
        try:
            print(time.perf_counter() - start)
            self.file_service.make_output(answers, args.output)
        except Exception as e:
            print(e)


def main() -> None:
    """Entry point for the CallMeMaybe application."""
    CallMeMaybeApp().run()


main()
