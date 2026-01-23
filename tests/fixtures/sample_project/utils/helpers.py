"""Helper utilities."""

import json


def validate_input(data: str) -> bool:
    """Validate input data.

    Args:
        data: Input to validate

    Returns:
        True if valid, False otherwise
    """
    if not data:
        return False
    if not isinstance(data, str):
        return False
    return len(data) > 0


def format_output(result: dict) -> str:
    """Format result for output.

    Args:
        result: Result dictionary

    Returns:
        Formatted JSON string
    """
    return json.dumps(result, indent=2)
