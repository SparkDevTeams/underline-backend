
# pylint: disable=no-name-in-module;
"""
Dummy authentication class in order to use tokens where
necessary until implemented.

Akul's auth class is in the process of a PR, temporarily
substituting his models until his PR goes through.
"""

from pydantic import BaseModel


class Token(BaseModel):
    """
    Placeholder token model
    """
