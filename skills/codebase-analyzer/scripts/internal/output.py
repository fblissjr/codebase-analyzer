"""Structured output utilities for JSON emission and logging."""

from __future__ import annotations

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Any

# Log directory relative to this file
LOG_DIR = Path(__file__).parent / "log"


def emit(data: dict[str, Any], log: bool = False, log_name: str = "operation") -> None:
    """Emit JSON to stdout, optionally log to file.

    Args:
        data: Dictionary to emit as JSON
        log: Whether to also write to log file
        log_name: Prefix for the log filename
    """
    output = json.dumps(data, indent=2, default=str)
    print(output)

    if log:
        write_log(data, log_name)


def write_log(data: dict[str, Any], log_name: str = "operation") -> Path:
    """Write data to internal/log/ with timestamp.

    Args:
        data: Dictionary to log
        log_name: Prefix for the log filename

    Returns:
        Path to the created log file
    """
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_file = LOG_DIR / f"{log_name}_{timestamp}.json"

    with open(log_file, "w") as f:
        json.dump(data, f, indent=2, default=str)

    return log_file


def error_response(
    message: str,
    error_type: str = "error",
    details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Create a standardized error response.

    Args:
        message: Human-readable error message
        error_type: Type of error (e.g., "file_not_found", "parse_error")
        details: Additional error details

    Returns:
        Dictionary with error structure
    """
    response: dict[str, Any] = {
        "status": "error",
        "error_type": error_type,
        "message": message,
    }
    if details:
        response["details"] = details
    return response


def success_response(data: dict[str, Any], duration_ms: int | None = None) -> dict[str, Any]:
    """Create a standardized success response.

    Args:
        data: The response data
        duration_ms: Operation duration in milliseconds

    Returns:
        Dictionary with success structure
    """
    response = {"status": "success", **data}
    if duration_ms is not None:
        response["duration_ms"] = duration_ms
    return response


class Timer:
    """Context manager for timing operations."""

    def __init__(self):
        self.start_time: float = 0
        self.end_time: float = 0

    def __enter__(self) -> "Timer":
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        _ = exc_type, exc_val, exc_tb  # Unused but required by protocol
        self.end_time = time.perf_counter()

    @property
    def elapsed_ms(self) -> int:
        """Return elapsed time in milliseconds."""
        return int((self.end_time - self.start_time) * 1000)
