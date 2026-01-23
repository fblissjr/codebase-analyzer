"""Wrapper for llmfiles CLI invocation."""

from __future__ import annotations

import subprocess
from pathlib import Path


class LlmfilesError(Exception):
    """Error from llmfiles execution."""

    def __init__(self, message: str, returncode: int, stderr: str = ""):
        super().__init__(message)
        self.returncode = returncode
        self.stderr = stderr


def run_llmfiles(
    args: list[str],
    cwd: Path | None = None,
    capture_output: bool = True,
) -> subprocess.CompletedProcess[str]:
    """Run llmfiles CLI and return the result.

    Args:
        args: Arguments to pass to llmfiles (e.g., ["main.py", "--deps"])
        cwd: Working directory for the command
        capture_output: Whether to capture stdout/stderr

    Returns:
        CompletedProcess with stdout, stderr, and returncode

    Raises:
        LlmfilesError: If llmfiles returns non-zero exit code
    """
    cmd = ["llmfiles"] + args

    try:
        result = subprocess.run(
            cmd,
            capture_output=capture_output,
            text=True,
            cwd=cwd,
        )
    except FileNotFoundError:
        raise LlmfilesError(
            "llmfiles not found. Install with: uv add llmfiles",
            returncode=127,
        )

    if result.returncode != 0:
        raise LlmfilesError(
            f"llmfiles failed with exit code {result.returncode}",
            returncode=result.returncode,
            stderr=result.stderr,
        )

    return result


def get_llmfiles_version() -> str | None:
    """Get the installed llmfiles version."""
    try:
        result = subprocess.run(
            ["llmfiles", "--version"],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except FileNotFoundError:
        pass
    return None
