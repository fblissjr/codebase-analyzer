"""Tests for compare.py script."""

import json
import subprocess
import sys
import tempfile
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


def create_trace_file(content: dict, directory: Path) -> Path:
    """Create a temporary trace JSON file."""
    trace_file = directory / "trace.json"
    with open(trace_file, "w") as f:
        json.dump(content, f)
    return trace_file


class TestCompareBasic:
    """Basic compare.py tests."""

    def test_compare_two_trace_files(self):
        """Test comparing two trace JSON files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            trace1 = {
                "status": "success",
                "entry": "main.py",
                "files": ["main.py", "utils.py", "old_module.py"],
                "graph": {"main.py": ["utils.py"]},
                "external": ["requests"],
            }
            trace2 = {
                "status": "success",
                "entry": "main.py",
                "files": ["main.py", "utils.py", "new_module.py"],
                "graph": {"main.py": ["utils.py", "new_module.py"]},
                "external": ["requests", "httpx"],
            }

            # Create directories first
            (tmppath / "a").mkdir()
            (tmppath / "b").mkdir()
            file1 = create_trace_file(trace1, tmppath / "a")
            file2 = create_trace_file(trace2, tmppath / "b")

            result = run_script("compare.py", str(file1), str(file2))
            assert result.returncode == 0

            data = json.loads(result.stdout)
            assert data["status"] == "success"
            assert "only_in_first" in data
            assert "only_in_second" in data
            assert "common" in data

    def test_compare_missing_file(self):
        """Test with missing trace file."""
        result = run_script("compare.py", "/nonexistent/trace1.json", "/nonexistent/trace2.json")
        assert result.returncode == 1

        data = json.loads(result.stdout)
        assert data["status"] == "error"
        assert data["error_type"] == "file_not_found"

    def test_compare_no_arguments(self):
        """Test with no arguments."""
        result = run_script("compare.py")
        assert result.returncode == 1

        data = json.loads(result.stdout)
        assert data["status"] == "error"
        assert data["error_type"] == "invalid_args"


class TestCompareOutput:
    """Test compare.py output structure."""

    def test_comparison_structure(self):
        """Test that comparison output has expected structure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            (tmppath / "a").mkdir()
            (tmppath / "b").mkdir()

            trace1 = {
                "files": ["main.py", "shared.py"],
                "graph": {},
                "external": ["numpy"],
            }
            trace2 = {
                "files": ["main.py", "shared.py", "extra.py"],
                "graph": {},
                "external": ["numpy", "pandas"],
            }

            file1 = create_trace_file(trace1, tmppath / "a")
            file2 = create_trace_file(trace2, tmppath / "b")

            result = run_script("compare.py", str(file1), str(file2))
            assert result.returncode == 0

            data = json.loads(result.stdout)

            # Check required fields
            assert "only_in_first" in data
            assert "only_in_second" in data
            assert "common" in data
            assert "graph_diff" in data
            assert "external_diff" in data
            assert "summary" in data
            assert "stats" in data

    def test_graph_diff_structure(self):
        """Test graph diff output."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            (tmppath / "a").mkdir()
            (tmppath / "b").mkdir()

            trace1 = {
                "files": ["a.py", "b.py"],
                "graph": {"a.py": ["b.py"]},
                "external": [],
            }
            trace2 = {
                "files": ["a.py", "b.py", "c.py"],
                "graph": {"a.py": ["b.py", "c.py"]},
                "external": [],
            }

            file1 = create_trace_file(trace1, tmppath / "a")
            file2 = create_trace_file(trace2, tmppath / "b")

            result = run_script("compare.py", str(file1), str(file2))
            assert result.returncode == 0

            data = json.loads(result.stdout)
            graph_diff = data["graph_diff"]

            assert "added_edges" in graph_diff
            assert "removed_edges" in graph_diff


class TestCompareStats:
    """Test compare.py statistics."""

    def test_stats_accuracy(self):
        """Test that statistics are accurate."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            (tmppath / "a").mkdir()
            (tmppath / "b").mkdir()

            trace1 = {
                "files": ["a.py", "b.py", "c.py"],
                "graph": {},
                "external": [],
            }
            trace2 = {
                "files": ["b.py", "c.py", "d.py", "e.py"],
                "graph": {},
                "external": [],
            }

            file1 = create_trace_file(trace1, tmppath / "a")
            file2 = create_trace_file(trace2, tmppath / "b")

            result = run_script("compare.py", str(file1), str(file2))
            assert result.returncode == 0

            data = json.loads(result.stdout)
            stats = data["stats"]

            assert stats["files_in_first"] == 3
            assert stats["files_in_second"] == 4
            assert stats["common_files"] == 2  # b.py, c.py
            assert stats["unique_to_first"] == 1  # a.py
            assert stats["unique_to_second"] == 2  # d.py, e.py
