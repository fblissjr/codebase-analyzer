"""Tests for analyze.py script."""

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


class TestAnalyzeBasic:
    """Basic analyze.py tests."""

    def test_analyze_structure(self):
        """Test structure analysis."""
        result = run_script("analyze.py", str(FIXTURES_DIR), "--structure")
        assert result.returncode == 0

        data = json.loads(result.stdout)
        assert data["status"] == "success"
        assert "files_analyzed" in data
        assert "structure" in data

    def test_analyze_nonexistent_directory(self):
        """Test with non-existent directory."""
        result = run_script("analyze.py", "/nonexistent/directory", "--structure")
        assert result.returncode == 1

        data = json.loads(result.stdout)
        assert data["status"] == "error"
        assert data["error_type"] == "directory_not_found"


class TestAnalyzePattern:
    """Test analyze.py pattern searching."""

    def test_pattern_search_class(self):
        """Test searching for class names."""
        result = run_script("analyze.py", str(FIXTURES_DIR), "--pattern", "Engine")
        assert result.returncode == 0

        data = json.loads(result.stdout)
        assert "matches" in data
        assert data["match_count"] > 0

        # Should find Engine class
        matches = data["matches"]
        engine_matches = [m for m in matches if m["name"] == "Engine"]
        assert len(engine_matches) > 0

    def test_pattern_search_function(self):
        """Test searching for function names."""
        result = run_script("analyze.py", str(FIXTURES_DIR), "--pattern", "validate")
        assert result.returncode == 0

        data = json.loads(result.stdout)
        assert "matches" in data

        # Should find validate_input function
        matches = data["matches"]
        validate_matches = [m for m in matches if "validate" in m["name"].lower()]
        assert len(validate_matches) > 0

    def test_pattern_no_matches(self):
        """Test pattern that doesn't match anything."""
        result = run_script("analyze.py", str(FIXTURES_DIR), "--pattern", "NonExistentXYZ")
        assert result.returncode == 0

        data = json.loads(result.stdout)
        assert data["match_count"] == 0
        assert data["matches"] == []


class TestAnalyzeStructure:
    """Test analyze.py structure extraction."""

    def test_extract_classes(self):
        """Test extracting class information."""
        result = run_script("analyze.py", str(FIXTURES_DIR), "--structure")
        assert result.returncode == 0

        data = json.loads(result.stdout)
        structure = data["structure"]

        # Find engine.py structure
        engine_file = None
        for filename, content in structure.items():
            if "engine.py" in filename:
                engine_file = content
                break

        assert engine_file is not None
        assert "classes" in engine_file
        assert len(engine_file["classes"]) > 0

        # Check Engine class
        engine_class = engine_file["classes"][0]
        assert engine_class["name"] == "Engine"
        assert "methods" in engine_class
        assert "process" in engine_class["methods"]

    def test_extract_functions(self):
        """Test extracting function information."""
        result = run_script("analyze.py", str(FIXTURES_DIR), "--structure")
        assert result.returncode == 0

        data = json.loads(result.stdout)
        structure = data["structure"]

        # Find helpers.py structure
        helpers_file = None
        for filename, content in structure.items():
            if "helpers.py" in filename:
                helpers_file = content
                break

        assert helpers_file is not None
        assert "functions" in helpers_file
        assert len(helpers_file["functions"]) > 0

        # Check function details
        func_names = [f["name"] for f in helpers_file["functions"]]
        assert "validate_input" in func_names
        assert "format_output" in func_names


class TestAnalyzeStats:
    """Test analyze.py statistics."""

    def test_stats_present(self):
        """Test that stats are included in output."""
        result = run_script("analyze.py", str(FIXTURES_DIR), "--structure")
        assert result.returncode == 0

        data = json.loads(result.stdout)
        assert "stats" in data

        stats = data["stats"]
        assert "files_with_structure" in stats
        assert "total_classes" in stats
        assert "total_functions" in stats
