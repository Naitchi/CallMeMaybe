import json
import re
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


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
    prompt: str = Field()


def check_json_functions(list_function_dict: list[dict[str, Any]]) -> None:
    for fx in list_function_dict:
        FunctionDefinition(**fx)


def is_valid_filename(filename: str) -> None:
    pattern: str = r'^[-a-zA-Z0-9_./]+\.json$'
    if not re.fullmatch(pattern, filename):
        raise ValueError(
            r"Json name invalide. Please rename it in something like: "
            r"[a-zA-Z0-9_-]+\.json"
        )


def get_functions_json(
    filename: str = "functions_definition.json",
) -> list[dict[str, Any]]:
    try:
        is_valid_filename(filename)
        with open(
            filename,
            "r"
        ) as original:
            available_functions: list[dict[str, Any]] = json.load(original)
            check_json_functions(available_functions)
            return available_functions
    except (FileNotFoundError, FileExistsError, ValueError, Exception) as e:
        print(e)
        return []


def get_prompts_json(filename: str) -> list[dict[str, Any]]:
    try:
        is_valid_filename(filename)
        with open(
            filename,
            "r"
        ) as original:
            prompts: list[dict[str, Any]] = json.load(original)
            return prompts
    except (FileNotFoundError, FileExistsError, ValueError, Exception) as e:
        print(e)
        return []


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
        with open(
            f"./data/output/{filename}",
            "w"
        ) as file:
            result = []
            for answer in anwsers:
                print(answer)
                try:
                    result.append(convert_ints_to_floats(json.loads(answer)))
                except Exception:
                    result.append({})
            json.dump(result, file, indent=2)
            return True
    except (FileNotFoundError, FileExistsError, ValueError, Exception) as e:
        print(e)
        return False
