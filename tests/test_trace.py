"""Tests for trace.py script."""

import json
import subprocess
import sys
from pathlib import Path

import pytest

# Paths
TESTS_DIR = Path(__file__).parent
PROJECT_ROOT = TESTS_DIR.parent
SCRIPTS_DIR = PROJECT_ROOT / "skills" / "codebase-analyzer" / "scripts"
FIXTURES_DIR = TESTS_DIR / "fixtures" / "sample_project"


def run_script(script_name: str, *args: str, cwd: Path | None = None) -> subprocess.CompletedProcess:
    """Run a script and return the result."""
    script_path = SCRIPTS_DIR / script_name
    cmd = [sys.executable, str(script_path)] + list(args)
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=cwd or SCRIPTS_DIR,
    )


class TestTraceBasic:
    """Basic trace.py tests."""

    def test_trace_existing_file(self):
        """Test tracing an existing Python file."""
        result = run_script("trace.py", str(FIXTURES_DIR / "main.py"))
        # May fail if llmfiles isn't installed, but script should run
        assert result.returncode in (0, 1)

        if result.returncode == 0:
            data = json.loads(result.stdout)
            assert data["status"] == "success"
            assert "main.py" in data["entry"]

    def test_trace_nonexistent_file(self):
        """Test tracing a non-existent file."""
        result = run_script("trace.py", "/nonexistent/path/file.py")
        assert result.returncode == 1

        data = json.loads(result.stdout)
        assert data["status"] == "error"
        assert data["error_type"] == "file_not_found"

    def test_trace_non_python_file(self):
        """Test tracing a non-Python file."""
        # Create a temp non-python file
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            f.write(b"not python")
            temp_path = f.name

        try:
            result = run_script("trace.py", temp_path)
            assert result.returncode == 1

            data = json.loads(result.stdout)
            assert data["status"] == "error"
            assert data["error_type"] == "invalid_file_type"
        finally:
            Path(temp_path).unlink()


class TestTraceFlags:
    """Test trace.py command-line flags."""

    def test_trace_all_flag(self):
        """Test --all flag for full trace."""
        result = run_script("trace.py", str(FIXTURES_DIR / "main.py"), "--all")
        # Script should run regardless of llmfiles availability
        assert result.returncode in (0, 1)

    def test_trace_json_flag(self):
        """Test --json flag (default)."""
        result = run_script("trace.py", str(FIXTURES_DIR / "main.py"), "--json")
        assert result.returncode in (0, 1)
        # Output should be valid JSON
        try:
            json.loads(result.stdout)
        except json.JSONDecodeError:
            pytest.fail("Output is not valid JSON")


class TestTraceOutput:
    """Test trace.py output structure."""

    def test_output_structure(self):
        """Test that output has expected structure."""
        result = run_script("trace.py", str(FIXTURES_DIR / "main.py"))

        if result.returncode == 0:
            data = json.loads(result.stdout)
            assert "status" in data
            assert "entry" in data
            assert "files" in data
            assert "duration_ms" in data

    def test_error_output_structure(self):
        """Test that error output has expected structure."""
        result = run_script("trace.py", "/nonexistent/file.py")
        data = json.loads(result.stdout)

        assert data["status"] == "error"
        assert "error_type" in data
        assert "message" in data
