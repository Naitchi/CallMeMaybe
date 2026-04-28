import re
from pydantic import BaseModel, Field
from enum import Enum

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
    prompt:str = Field()

def check_json_functions(list_function_dict:list[dict])->None:
    for fx in list_function_dict:
        FunctionDefinition(**fx)


def is_valid_filename(filename: str) -> None:
    pattern: str = r'^[a-zA-Z0-9_-]+\.json$'
    if not re.fullmatch(pattern, filename):
        raise ValueError(r"Json name invalide. Please rename it in something like: [a-zA-Z0-9_-]+\.json")

