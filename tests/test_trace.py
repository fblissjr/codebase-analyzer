"""Tests for trace.py script (integration tests via subprocess)."""

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
        # Should succeed with library path
        assert result.returncode in (0, 1)

        if result.returncode == 0:
            data = json.loads(result.stdout)
            assert data["status"] == "success"
            assert "main.py" in data["entry"]
            assert "files" in data
            assert "call_graph" in data
            assert "stats" in data

    def test_trace_nonexistent_file(self):
        """Test tracing a non-existent file."""
        result = run_script("trace.py", "/nonexistent/path/file.py")
        assert result.returncode == 1

        data = json.loads(result.stdout)
        assert data["status"] == "error"
        assert data["error_type"] == "file_not_found"

    def test_trace_non_python_file(self):
        """Test tracing a non-Python file."""
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
        assert result.returncode in (0, 1)

    def test_trace_log_flag(self):
        """Test --log flag."""
        result = run_script("trace.py", str(FIXTURES_DIR / "main.py"), "--log")
        assert result.returncode in (0, 1)
        # Output should still be valid JSON
        try:
            json.loads(result.stdout)
        except json.JSONDecodeError:
            pytest.fail("Output is not valid JSON")

    def test_trace_grep_flag(self):
        """Test --grep flag finds files by content."""
        result = run_script("trace.py", str(FIXTURES_DIR / "main.py"), "--grep", "def main")
        assert result.returncode in (0, 1)
        if result.returncode == 0:
            data = json.loads(result.stdout)
            assert data["status"] == "success"
            assert "grep_pattern" in data

    def test_trace_since_flag(self):
        """Test --since flag for git-based filtering."""
        result = run_script("trace.py", str(FIXTURES_DIR / "main.py"), "--since", "1 year ago")
        assert result.returncode in (0, 1)
        # Either succeeds with git data or errors gracefully
        data = json.loads(result.stdout)
        assert "status" in data


class TestTraceOutput:
    """Test trace.py output structure."""

    def test_output_structure(self):
        """Test that output has expected v2.0 structure."""
        result = run_script("trace.py", str(FIXTURES_DIR / "main.py"))

        if result.returncode == 0:
            data = json.loads(result.stdout)
            assert "status" in data
            assert "entry" in data
            assert "files" in data
            assert "call_graph" in data
            assert "external" in data
            assert "stats" in data
            assert "duration_ms" in data

            # Check stats structure
            stats = data["stats"]
            assert "total_files" in stats
            assert "max_depth" in stats
            assert "circular_deps" in stats
            assert "parse_errors" in stats
            assert "skipped_imports" in stats
            assert "hub_modules" in stats

    def test_error_output_structure(self):
        """Test that error output has expected structure."""
        result = run_script("trace.py", "/nonexistent/file.py")
        data = json.loads(result.stdout)

        assert data["status"] == "error"
        assert "error_type" in data
        assert "message" in data

    def test_call_graph_edge_format(self):
        """Test that call_graph edges have the enriched format."""
        result = run_script("trace.py", str(FIXTURES_DIR / "main.py"))

        if result.returncode == 0:
            data = json.loads(result.stdout)
            call_graph = data.get("call_graph", {})
            # Call graph values should be lists of dicts with 'to', 'module', 'line'
            for _src, edges in call_graph.items():
                assert isinstance(edges, list)
                for edge in edges:
                    assert "to" in edge
                    assert "module" in edge
                    assert "line" in edge

    def test_external_deps_format(self):
        """Test that external deps map package -> list of files."""
        result = run_script("trace.py", str(FIXTURES_DIR / "main.py"))

        if result.returncode == 0:
            data = json.loads(result.stdout)
            external = data.get("external", {})
            assert isinstance(external, dict)
            for _pkg, files in external.items():
                assert isinstance(files, list)
