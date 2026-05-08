import json
from pathlib import Path
import re
import sys
from enum import Enum
from typing import Any


from pydantic import BaseModel, Field, field_validator


class AllowedType(str, Enum):
    NUMBER = "number"
    STRING = "string"
    BOOLEAN = "boolean"
    INTEGER = "integer"
    ARRAY = "array"
    OBJECT = "object"
    NULL = "null"


class TypedField(BaseModel):
    type: AllowedType


class FunctionDefinition(BaseModel):
    name: str = Field(strict=True, min_length=1)
    description: str = Field(strict=True, min_length=1)
    parameters: dict[str, TypedField] = Field(strict=True, min_length=1)
    returns: TypedField


class PromptDefinition(BaseModel):
    prompt: str = Field(strict=True, min_length=1)

    @field_validator("prompt")
    @classmethod
    def prompt_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("prompt must not be empty or whitespace only")
        return value


def is_valid_filename(filename: str) -> None:
    pattern: str = r'^[-a-zA-Z0-9_./]+\.json$'
    if not re.fullmatch(pattern, filename):
        raise ValueError(
            r"Json name invalide. Please rename it in something like: "
            r"[a-zA-Z0-9_-]+\.json"
        )


def check_json_functions(list_function_dict: list[dict[str, Any]]) -> None:
    for fx in list_function_dict:
        FunctionDefinition(**fx)


def check_json_prompts(prompts: list[dict[str, Any]]) -> None:
    for prompt in prompts:
        PromptDefinition(**prompt)


def get_functions_json(
    filename: str = "functions_definition.json",
) -> list[dict[str, Any]]:
    try:
        is_valid_filename(filename)
        with open(filename, "r") as file:
            available_functions: list[dict[str, Any]] = json.load(file)
            check_json_functions(available_functions)
            if len(available_functions) < 1:
                raise ValueError("No functions available for the llm.")
            return available_functions
    except (FileNotFoundError, FileExistsError, ValueError, Exception):
        print("Error in the Functions file, you need a none-empty correct",
              "json file with object with the proprieties 'name', ",
              "'description', 'parameters' and 'returns'")
        sys.exit()


def get_prompts_json(filename: str) -> list[dict[str, Any]]:
    try:
        is_valid_filename(filename)
        with open(filename, "r") as file:
            prompts: list[dict[str, Any]] = json.load(file)
            check_json_prompts(prompts)
            if len(prompts) < 1:
                raise ValueError("No prompt available for the llm.")
            return prompts
    except (FileNotFoundError, FileExistsError, ValueError, Exception):
        print("Error in the Prompts file, you need a none-empty correct",
              "json file with object with a none empty propriety 'prompt'")
        sys.exit()


def sanitize_llm_json_response(raw_response: str) -> str:
    if len(raw_response) < 1:
        return raw_response
    return re.sub(r'\\(?!["\\/bfnrt]|u[0-9a-fA-F]{4})', r'\\\\', raw_response)


def convert_ints_to_floats(value: Any) -> Any:
    if type(value) is int:
        return float(value)
    if isinstance(value, list):
        return [convert_ints_to_floats(item) for item in value]
    if isinstance(value, dict):
        return {
            key: convert_ints_to_floats(item)
            for key, item in value.items()
        }
    return value


def make_output(anwsers: list[str], filename: str) -> bool:
    try:
        is_valid_filename(filename)
        output = Path(filename)
        output.parent.mkdir(parents=True, exist_ok=True)
        with open(filename, "w") as file:
            result: list[Any] = []
            for answer in anwsers:
                print(answer)
                try:
                    result.append(convert_ints_to_floats(json.loads(answer)))
                except Exception:
                    result.append({"prompt": "", "name": "", "parameters": {}})
            json.dump(result, file, indent=2)
            return True
    except (FileNotFoundError, FileExistsError, ValueError, Exception) as e:
        print(e)
        return False
