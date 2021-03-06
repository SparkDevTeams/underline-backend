# pylint: disable=no-self-argument
#       - pydantic models are technically class models, so they dont use self.
# pylint: disable=no-self-use
#       - pydantic validators use cls instead of self; theyre not instance based
# pylint: disable=no-name-in-module
#       - Need to whitelist pydantic locally
"""
Holds common modeling classes or utility functions that can be used
in any single module in `models/`.

Any function that achieves the same goal but is written more than once should
be in this file instead and imported when needed.
"""

from enum import Enum
from uuid import uuid4
from typing import Dict, Any
from datetime import datetime

from pydantic import BaseModel, validator, Field

# Type aliases
EventId = str
UserId = str
FeedbackId = str


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


class CustomBaseModel(BaseModel):
    """
    Custom but non-breaking version of the basemodel that has some
    niceties of the `ExtendedBaseModel` but not all of the same
    breaking features.
    """
    class Config:
        use_enum_values = True

    def dict(self, *args, **kwargs) -> Dict[str, Any]:
        """
        Override the base `dict` method in order to turn all of the
        datetimes to string.
        """
        parent_dict = super().dict(*args, **kwargs)

        for key, val in parent_dict.items():
            if isinstance(val, datetime):
                parent_dict[key] = str(val)
        return parent_dict


class ExtendedBaseModel(BaseModel):
    """
    Configured version of the pydantic BaseModel that has common
    functions/config values that should be shared accross code.
    """
    id: str = Field("", alias="_id")  # pylint: disable=invalid-name

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
