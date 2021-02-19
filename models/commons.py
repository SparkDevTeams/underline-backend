"""
Holds common modeling classes or utility functions that can be used
in any single module in `models/`.

Any function that achieves the same goal but is written more than once should
be in this file instead and imported when needed.
"""

from uuid import uuid4


def generate_uuid4_str() -> str:
    """
    Generates a string representation of a UUID4.
    """
    return str(uuid4())
