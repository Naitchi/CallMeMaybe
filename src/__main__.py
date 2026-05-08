import numpy as np
import argparse
import time
from typing import Any

from llm_sdk import Small_LLM_Model
from .parsing import (
    get_functions_json,
    get_prompts_json,
    make_output,
    sanitize_llm_json_response,
)


def generate_next_token(llm: Small_LLM_Model, tokens: list[int]) -> int:
    possible_token = np.asarray(
        llm.get_logits_from_input_ids(tokens),
        dtype=float,
    )
    next_token: int = int(np.argmax(possible_token))
    tokens.append(next_token)
    return next_token


def check_for_ended_response(response: str) -> bool:
    accolades: list[str] = []
    for char in response:
        if char == '[' or char == '{':
            accolades.append(char)
        if char == ']' or char == '}':
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
        llm: Small_LLM_Model,
        available_func: list[dict[str, Any]]
        ) -> list[int]:
    token_names: list[int] = []
    for func in available_func:
        token_names.extend(
            [int(token) for token in llm.encode(func["name"])[0]]
            )
    token_names.append(497)
    return list(set(token_names))


def create_prompt(prompt: str, available_functions: str) -> tuple[str, str]:
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
        llm: Small_LLM_Model,
        tokens: list[int],
        tokens_func_name: list[int]
        ) -> int:
    possible_token = np.asarray(
        llm.get_logits_from_input_ids(tokens),
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


def main() -> None:
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
    available_functions: list[dict[str, Any]] = get_functions_json(
        args.functions_definition
        )
    for funct in available_functions:
        del funct["returns"]
    prompts: list[dict[str, Any]] = get_prompts_json(args.input)
    jarvis: Small_LLM_Model = Small_LLM_Model()
    anwsers: list[str] = []
    start = time.perf_counter()
    tokens_func_name: list[int] = (
        get_function_names(
            jarvis,
            available_functions,
            )
        )
    for user_prompt in prompts:
        try:
            response: str = ""
            prompt: str = ""
            generate_name: bool = True
            (prompt, response) = create_prompt(
                user_prompt["prompt"],
                str(available_functions)
            )
            tokens = jarvis.encode(prompt)
            converted_list = list(tokens[0])
            while generate_name:
                response = "".join([
                    response,
                    jarvis.decode([
                            constained_decoding(
                                jarvis,
                                converted_list,
                                tokens_func_name
                            )
                        ])
                    ])
                if response.count('"') % 2 < 1:
                    generate_name = False
                    response = "".join([response, '\"parameters\":{ '])
                    converted_list.extend(
                        jarvis.encode('\"parameters\":{ ')[0]
                    )
            while check_for_ended_response(response):
                response = "".join([
                        response,
                        jarvis.decode(
                            [
                                generate_next_token(jarvis, converted_list)
                            ]
                        )
                    ])
            response = sanitize_llm_json_response(response)
            anwsers.append(response)
            print(response)
            print(time.perf_counter() - start)
        except (
            FileNotFoundError,
            FileExistsError,
            ValueError,
            Exception
        )as e:
            print(e)
    try:
        print(time.perf_counter() - start)
        make_output(anwsers, args.output)
    except (Exception)as e:
        print(e)


main()
