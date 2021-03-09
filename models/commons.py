"""
Holds common modeling classes or utility functions that can be used
in any single module in `models/`.

Any function that achieves the same goal but is written more than once should
be in this file instead and imported when needed.
"""

from enum import Enum
from uuid import uuid4
from typing import Dict, Any

from pydantic import BaseModel, validator


def generate_uuid4_str() -> str:
    """
    Generates a string representation of a UUID4.
    """
    return str(uuid4())


class AutoName(Enum):
    """
    Hacky but abstracted-enough solution to the dumb enum naming problem that
    python has. Basically returns enums in string form when referenced by value
    """

    # since this is a funky should-be-private method, we have to break
    # a couple of lint rules
    # pylint: disable=unused-argument, no-self-argument
    def _generate_next_value_(name, start, count, last_values):
        """
        Returns name of enum rather than assigned value.
        """
        return name


class ExtendedBaseModel(BaseModel):
    """
    Configured version of the pydantic BaseModel that has common
    functions/config values that should be shared accross code.
    """
    class Config:
        use_enum_values = True

    @validator("id", pre=True, always=True, check_fields=False)
    def set_id(cls, value) -> str:
        """
        Workaround on dynamic default setting for UUID.
        From: https://github.com/samuelcolvin/pydantic/issues/866
        """
        return value or generate_uuid4_str()

    def get_id(self) -> str:
        """
        Returns this instance's ID
        """
        return self.id

    def dict(self, *args, **kwargs) -> Dict[str, Any]:
        """
        Override the base `dict` method in order to get the mongo ID fix
        """
        parent_dict = super().dict(*args, **kwargs)
        parent_dict["_id"] = self.get_id()
        return parent_dict
