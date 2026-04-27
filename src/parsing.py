import re
from pydantic import BaseModel, Field
from typing import Dict, Literal

ParamType = Literal["number", "string", "boolean"]

class Parameter(BaseModel):
    type: ParamType = Field(..., description="Type of the parameter")

class FunctionSpec(BaseModel):
    name: str = Field(...,min_length=1, pattern=r"^[a-zA-Z0-9_]$")
    description: str = Field(..., min_length=1)
    parameters: Dict[str, Parameter] = Field(...)
    returns: Parameter = Field(...)

def is_valid_filename(filename: str) -> None:
    pattern: str = r'^[a-zA-Z0-9_-]+\.json$'
    if not re.match(pattern,filename):
        raise ValueError("Json name invalide. Please rename it in something like: [a-zA-Z0-9_-]+\.json")

