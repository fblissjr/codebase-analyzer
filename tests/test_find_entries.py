"""Tests for find_entries.py script."""

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


class TestFindEntriesBasic:
    """Basic find_entries.py tests."""

    def test_find_entries_in_fixture(self):
        """Test finding entries in sample project."""
        result = run_script("find_entries.py", str(FIXTURES_DIR))
        assert result.returncode == 0

        data = json.loads(result.stdout)
        assert data["status"] == "success"
        assert "entry_points" in data
        assert "files_scanned" in data
        assert data["files_scanned"] > 0

    def test_find_main_block(self):
        """Test detecting if __name__ == '__main__' block."""
        result = run_script("find_entries.py", str(FIXTURES_DIR), "--types", "main_block")
        assert result.returncode == 0

        data = json.loads(result.stdout)
        entry_points = data["entry_points"]

        # Should find main.py's main block
        main_entries = [e for e in entry_points if "main.py" in e["file"]]
        assert len(main_entries) > 0
        assert main_entries[0]["type"] == "main_block"

    def test_find_entries_nonexistent_directory(self):
        """Test with non-existent directory."""
        result = run_script("find_entries.py", "/nonexistent/directory")
        assert result.returncode == 1

        data = json.loads(result.stdout)
        assert data["status"] == "error"
        assert data["error_type"] == "directory_not_found"


class TestFindEntriesTypes:
    """Test find_entries.py type filtering."""

    def test_multiple_types(self):
        """Test filtering by multiple types."""
        result = run_script(
            "find_entries.py", str(FIXTURES_DIR),
            "--types", "main_block,argparse"
        )
        assert result.returncode == 0

        data = json.loads(result.stdout)
        for entry in data["entry_points"]:
            assert entry["type"] in ("main_block", "argparse")

    def test_invalid_type(self):
        """Test with invalid entry type."""
        result = run_script(
            "find_entries.py", str(FIXTURES_DIR),
            "--types", "invalid_type"
        )
        assert result.returncode == 1

        data = json.loads(result.stdout)
        assert data["status"] == "error"
        assert data["error_type"] == "invalid_types"


class TestFindEntriesOutput:
    """Test find_entries.py output structure."""

    def test_entry_point_structure(self):
        """Test that entry points have required fields."""
        result = run_script("find_entries.py", str(FIXTURES_DIR))
        assert result.returncode == 0

        data = json.loads(result.stdout)
        for entry in data["entry_points"]:
            assert "file" in entry
            assert "type" in entry
            assert "line" in entry
            assert isinstance(entry["line"], int)

    def test_duration_in_response(self):
        """Test that response includes duration."""
        result = run_script("find_entries.py", str(FIXTURES_DIR))
        assert result.returncode == 0

        data = json.loads(result.stdout)
        assert "duration_ms" in data
        assert isinstance(data["duration_ms"], int)
