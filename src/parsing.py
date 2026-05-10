import json
from pathlib import Path
import re
from enum import Enum
from typing import Any


from pydantic import BaseModel, Field, field_validator


class AllowedType(str, Enum):
    """Enumeration of allowed JSON schema types.
    Attributes:
        NUMBER: Represents a numeric type.
        STRING: Represents a string type.
        BOOLEAN: Represents a boolean type.
        INTEGER: Represents an integer type.
        ARRAY: Represents an array/list type.
        OBJECT: Represents an object/dict type.
        NULL: Represents a null type.
    """
    NUMBER = "number"
    STRING = "string"
    BOOLEAN = "boolean"
    INTEGER = "integer"
    ARRAY = "array"
    OBJECT = "object"
    NULL = "null"


class TypedField(BaseModel):
    """Represents a typed field with an allowed type.
    Attributes:
        type: The allowed type for this field.
    """
    type: AllowedType


class FunctionDefinition(BaseModel):
    """Schema definition for a function that can be called by an LLM.
    Attributes:
        name: The function name (non-empty string).
        description: A description of what the function does
            (non-empty string).
        parameters: Dictionary mapping parameter names to their
            typed fields.
        returns: The return type of the function.
    """
    name: str = Field(strict=True, min_length=1)
    description: str = Field(strict=True, min_length=1)
    parameters: dict[str, TypedField] = Field(strict=True, min_length=1)
    returns: TypedField

    @field_validator("parameters")
    @classmethod
    def parameter_names_must_not_be_blank(
        cls, value: dict[str, TypedField]
    ) -> dict[str, TypedField]:
        """Validate that parameter names are not empty or whitespace.
        Args:
            value: Dictionary of parameters to validate.
        Returns:
            The validated parameters dictionary.
        Raises:
            ValueError: If any parameter name is empty or contains
                only whitespace.
        """
        for key in value:
            if not key or not key.strip():
                raise ValueError("parameter names must not be null or blank")
        return value


class PromptDefinition(BaseModel):
    """Schema definition for a prompt.
    Attributes:
        prompt: The prompt text (non-empty, non-whitespace string).
    """
    prompt: str = Field(strict=True, min_length=1)

    @field_validator("prompt")
    @classmethod
    def prompt_must_not_be_blank(cls, value: str) -> str:
        """Validate that prompt is not empty or whitespace-only.
        Args:
            value: The prompt string to validate.
        Returns:
            The validated prompt string.
        Raises:
            ValueError: If prompt is empty or contains only whitespace.
        """
        if not value.strip():
            raise ValueError("prompt must not be empty or whitespace only")
        return value


class JSONFileService:
    """Service for handling JSON file operations and validation.
    Attributes:
        filename_pattern: Regex pattern for validating JSON filenames.
    """
    filename_pattern: str = r'^[-a-zA-Z0-9_./]+\.json$'

    def _is_valid_filename(self, filename: str) -> None:
        """Validate that a filename matches the expected JSON filename pattern.
        Args:
            filename: The filename to validate.
        Raises:
            ValueError: If filename does not match the expected pattern.
        """
        if not re.fullmatch(self.filename_pattern, filename):
            raise ValueError(
                r"Json name invalide. Please rename it in something like: "
                r"[a-zA-Z0-9_-]+\.json"
            )

    def _check_json_functions(
            self,
            list_function_dict: list[dict[str, Any]]
            ) -> None:
        """Validate function definitions against the schema.
        Args:
            list_function_dict: List of function definition dictionaries
                to validate.
        Raises:
            ValidationError: If any function definition is invalid.
        """
        for fx in list_function_dict:
            FunctionDefinition(**fx)

    def _check_json_prompts(self, prompts: list[dict[str, Any]]) -> None:
        """Validate a list of prompts against the PromptDefinition schema.
        Args:
            prompts: List of prompt dictionaries to validate.
        Raises:
            ValidationError: If any prompt definition is invalid.
        """
        for prompt in prompts:
            PromptDefinition(**prompt)

    def get_functions_json(
        self,
        filename: str = "functions_definition.json",
    ) -> list[dict[str, Any]]:
        """Load and validate a JSON file containing function definitions.
        Args:
            filename: Path to the JSON file containing function definitions.
                Defaults to "functions_definition.json".
        Returns:
            List of validated function definition dictionaries.
        Raises:
            SystemExit: If the file is invalid, empty, or cannot be read.
        """
        try:
            self._is_valid_filename(filename)
            with open(filename, "r") as file:
                available_functions: list[dict[str, Any]] = json.load(file)
                self._check_json_functions(available_functions)
                if len(available_functions) < 1:
                    raise ValueError("No functions available for the llm.")
                return available_functions
        except (FileNotFoundError, FileExistsError, ValueError, Exception):
            print(
                "Error in the Functions file, you need a none-empty correct",
                "json file with object with the proprieties 'name', ",
                "'description', 'parameters' and 'returns'",
            )
            raise SystemExit()

    def get_prompts_json(self, filename: str) -> list[dict[str, Any]]:
        """Load and validate a JSON file containing prompts.
        Args:
            filename: Path to the JSON file containing prompt definitions.
        Returns:
            List of validated prompt definition dictionaries.
        Raises:
            SystemExit: If the file is invalid, empty, or cannot be read.
        """
        try:
            self._is_valid_filename(filename)
            with open(filename, "r") as file:
                prompts: list[dict[str, Any]] = json.load(file)
                self._check_json_prompts(prompts)
                if len(prompts) < 1:
                    raise ValueError("No prompt available for the llm.")
                return prompts
        except (FileNotFoundError, FileExistsError, ValueError, Exception):
            print(
                "Error in the Prompts file, you need a none-empty correct",
                "json file with object with a none empty propriety 'prompt'",
            )
            raise SystemExit()

    def sanitize_llm_json_response(self, raw_response: str) -> str:
        """Sanitize an LLM JSON response by fixing invalid escape sequences.
        Args:
            raw_response: The raw JSON response string from the LLM.
        Returns:
            The sanitized JSON response string with valid escape sequences.
        """
        if len(raw_response) < 1:
            return raw_response
        return re.sub(
            r'\\(?!["\\/bfnrt]|u[0-9a-fA-F]{4})',
            r'\\\\',
            raw_response
            )

    def convert_ints_to_floats(self, value: Any) -> Any:
        """Convert all integer values to floats recursively.
        Recursively processes nested structures to convert all integers
        to floats while preserving the overall structure.
        Args:
            value: A value that may be an integer, list, dict, or
                other type.
        Returns:
            The value with all integers converted to floats, preserving
            structure.
        """
        if type(value) is int:
            return float(value)
        if isinstance(value, list):
            return [self.convert_ints_to_floats(item) for item in value]
        if isinstance(value, dict):
            return {
                key: self.convert_ints_to_floats(item)
                for key, item in value.items()
            }
        return value

    def make_output(self, anwsers: list[str], filename: str) -> bool:
        """Write processed answers to a JSON output file.
        Args:
            anwsers: List of JSON string answers to write.
            filename: Path to the output JSON file.
        Returns:
            True if the file was written successfully, False otherwise.
        """
        try:
            self._is_valid_filename(filename)
            output = Path(filename)
            output.parent.mkdir(parents=True, exist_ok=True)
            with open(filename, "w") as file:
                result: list[Any] = []
                for answer in anwsers:
                    print(answer)
                    try:
                        result.append(
                            self.convert_ints_to_floats(json.loads(answer))
                        )
                    except Exception:
                        result.append(
                            {"prompt": "", "name": "", "parameters": {}}
                            )
                json.dump(result, file, indent=2)
                return True
        except (
                FileNotFoundError,
                FileExistsError,
                ValueError,
                Exception
                ) as e:
            print(e)
            return False
