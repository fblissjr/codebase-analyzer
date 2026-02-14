"""Unit tests for core functions (not integration/subprocess tests).

Tests the actual Python functions directly rather than running scripts via subprocess.
"""

import ast
import sys
import tempfile
from pathlib import Path

import pytest

# Add scripts to path for direct imports
TESTS_DIR = Path(__file__).parent
PROJECT_ROOT = TESTS_DIR.parent
SCRIPTS_DIR = PROJECT_ROOT / "skills" / "codebase-analyzer" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from internal.file_utils import find_python_files
from internal.output import Timer, error_response, success_response


# --- file_utils tests ---

class TestFindPythonFiles:
    """Tests for shared find_python_files."""

    def test_finds_python_files(self, tmp_path):
        """Should find .py files in directory."""
        (tmp_path / "a.py").write_text("x = 1")
        (tmp_path / "b.py").write_text("y = 2")
        (tmp_path / "c.txt").write_text("not python")

        files = find_python_files(tmp_path)
        names = [f.name for f in files]
        assert "a.py" in names
        assert "b.py" in names
        assert "c.txt" not in names

    def test_excludes_venv(self, tmp_path):
        """Should skip .venv directories."""
        venv_dir = tmp_path / ".venv" / "lib"
        venv_dir.mkdir(parents=True)
        (venv_dir / "module.py").write_text("x = 1")
        (tmp_path / "real.py").write_text("y = 2")

        files = find_python_files(tmp_path)
        names = [f.name for f in files]
        assert "real.py" in names
        assert "module.py" not in names

    def test_excludes_git(self, tmp_path):
        """Should skip .git directories."""
        git_dir = tmp_path / ".git" / "hooks"
        git_dir.mkdir(parents=True)
        (git_dir / "pre-commit.py").write_text("x = 1")
        (tmp_path / "src.py").write_text("y = 2")

        files = find_python_files(tmp_path)
        names = [f.name for f in files]
        assert "src.py" in names
        assert "pre-commit.py" not in names

    def test_excludes_pycache(self, tmp_path):
        """Should skip __pycache__ directories."""
        cache_dir = tmp_path / "__pycache__"
        cache_dir.mkdir()
        (cache_dir / "module.cpython-311.pyc.py").write_text("x = 1")
        (tmp_path / "src.py").write_text("y = 2")

        files = find_python_files(tmp_path)
        names = [f.name for f in files]
        assert "src.py" in names
        assert len(files) == 1

    def test_excludes_egg_info(self, tmp_path):
        """Should skip .egg-info directories."""
        egg_dir = tmp_path / "mypackage.egg-info"
        egg_dir.mkdir()
        (egg_dir / "PKG-INFO.py").write_text("x = 1")
        (tmp_path / "src.py").write_text("y = 2")

        files = find_python_files(tmp_path)
        names = [f.name for f in files]
        assert "src.py" in names
        assert len(files) == 1

    def test_empty_directory(self, tmp_path):
        """Should return empty list for empty directory."""
        files = find_python_files(tmp_path)
        assert files == []

    def test_recursive(self, tmp_path):
        """Should find files in subdirectories."""
        sub = tmp_path / "pkg" / "sub"
        sub.mkdir(parents=True)
        (sub / "deep.py").write_text("x = 1")
        (tmp_path / "top.py").write_text("y = 2")

        files = find_python_files(tmp_path)
        names = [f.name for f in files]
        assert "top.py" in names
        assert "deep.py" in names

    def test_sorted_output(self, tmp_path):
        """Should return sorted list."""
        (tmp_path / "z.py").write_text("x = 1")
        (tmp_path / "a.py").write_text("y = 2")
        (tmp_path / "m.py").write_text("z = 3")

        files = find_python_files(tmp_path)
        assert files == sorted(files)


# --- output.py tests ---

class TestErrorResponse:
    """Tests for error_response."""

    def test_basic_error(self):
        result = error_response("something broke")
        assert result["status"] == "error"
        assert result["error_type"] == "error"
        assert result["message"] == "something broke"

    def test_custom_error_type(self):
        result = error_response("file missing", error_type="file_not_found")
        assert result["error_type"] == "file_not_found"

    def test_with_details(self):
        result = error_response("bad", details={"path": "/tmp/x"})
        assert result["details"]["path"] == "/tmp/x"

    def test_without_details(self):
        result = error_response("bad")
        assert "details" not in result


class TestSuccessResponse:
    """Tests for success_response."""

    def test_basic_success(self):
        result = success_response({"files": ["a.py"]})
        assert result["status"] == "success"
        assert result["files"] == ["a.py"]

    def test_with_duration(self):
        result = success_response({"count": 5}, duration_ms=123)
        assert result["duration_ms"] == 123

    def test_without_duration(self):
        result = success_response({"count": 5})
        assert "duration_ms" not in result


class TestTimer:
    """Tests for Timer context manager."""

    def test_timer_measures_time(self):
        import time
        with Timer() as t:
            time.sleep(0.01)
        assert t.elapsed_ms >= 10

    def test_timer_zero_for_fast_ops(self):
        with Timer() as t:
            pass
        assert t.elapsed_ms >= 0


# --- trace.py core function tests ---

class TestParseLlmfilesOutput:
    """Tests for parse_llmfiles_output."""

    def setup_method(self):
        from trace import parse_llmfiles_output
        self.parse = parse_llmfiles_output

    def test_file_marker_format(self):
        output = "--- path/to/a.py ---\ncode\n--- path/to/b.py ---\nmore code"
        result = self.parse(output, Path("entry.py"))
        # The parser extracts files from the --- markers
        file_names = [Path(f).name for f in result["files"]]
        assert "a.py" in file_names or "b.py" in file_names or len(result["files"]) > 0

    def test_hash_marker_format(self):
        output = "# File: src/main.py\nimport os\n# File: src/utils.py\nhelper()"
        result = self.parse(output, Path("main.py"))
        assert len(result["files"]) >= 1

    def test_empty_output(self):
        result = self.parse("", Path("entry.py"))
        assert result["files"] == []

    def test_returns_graph_and_external(self):
        result = self.parse("--- a.py ---\ncode", Path("a.py"))
        assert "graph" in result
        assert "external" in result


class TestAnalyzeImportsFromFile:
    """Tests for analyze_imports_from_file."""

    def setup_method(self):
        from trace import analyze_imports_from_file
        self.analyze = analyze_imports_from_file

    def test_standard_import(self, tmp_path):
        f = tmp_path / "test.py"
        f.write_text("import os\nimport json\n")
        local, external = self.analyze(f)
        assert "os" in external
        assert "json" in external

    def test_from_import(self, tmp_path):
        f = tmp_path / "test.py"
        f.write_text("from pathlib import Path\n")
        local, external = self.analyze(f)
        assert "pathlib" in external

    def test_relative_import(self, tmp_path):
        f = tmp_path / "test.py"
        f.write_text("from .utils import helper\n")
        local, external = self.analyze(f)
        assert "utils" in local

    def test_nonexistent_file(self, tmp_path):
        f = tmp_path / "missing.py"
        local, external = self.analyze(f)
        assert local == []
        assert external == []

    def test_syntax_error_file(self, tmp_path):
        f = tmp_path / "bad.py"
        f.write_text("def broken(\n")
        local, external = self.analyze(f)
        assert local == []
        assert external == []


class TestBuildDependencyGraph:
    """Tests for build_dependency_graph."""

    def setup_method(self):
        from trace import build_dependency_graph
        self.build = build_dependency_graph

    def test_basic_graph(self, tmp_path):
        # Create two files with an import relationship
        main = tmp_path / "main.py"
        main.write_text("from .utils import helper\n")
        utils = tmp_path / "utils.py"
        utils.write_text("def helper(): pass\n")

        graph, external, stats = self.build(
            main, [str(main), str(utils)], tmp_path
        )
        assert "total_files" in stats
        assert stats["total_files"] == 2

    def test_external_deps_exclude_stdlib(self, tmp_path):
        f = tmp_path / "test.py"
        f.write_text("import os\nimport click\n")

        graph, external, stats = self.build(f, [str(f)], tmp_path)
        assert "os" not in external
        assert "click" in external

    def test_circular_deps_detected(self, tmp_path):
        # Two files importing each other
        a = tmp_path / "a.py"
        b = tmp_path / "b.py"
        a.write_text("from .b import x\n")
        b.write_text("from .a import y\n")

        graph, external, stats = self.build(
            a, [str(a), str(b)], tmp_path
        )
        assert "circular_deps" in stats


# --- find_entries.py core function tests ---

class TestFindMainBlock:
    """Tests for find_main_block."""

    def setup_method(self):
        from find_entries import find_main_block
        self.find = find_main_block

    def test_detects_main_block(self):
        code = 'if __name__ == "__main__":\n    main()\n'
        tree = ast.parse(code)
        assert self.find(tree) is not None

    def test_no_main_block(self):
        code = "def foo(): pass\n"
        tree = ast.parse(code)
        assert self.find(tree) is None

    def test_returns_line_number(self):
        code = 'x = 1\nif __name__ == "__main__":\n    main()\n'
        tree = ast.parse(code)
        assert self.find(tree) == 2


class TestFindClickCommands:
    """Tests for find_click_commands."""

    def setup_method(self):
        from find_entries import find_click_commands
        self.find = find_click_commands

    def test_detects_click_command(self):
        code = "import click\n@click.command()\ndef cli(): pass\n"
        tree = ast.parse(code)
        lines = self.find(tree)
        assert len(lines) > 0

    def test_no_click(self):
        code = "def foo(): pass\n"
        tree = ast.parse(code)
        assert self.find(tree) == []


class TestFindFastapiApp:
    """Tests for find_fastapi_app."""

    def setup_method(self):
        from find_entries import find_fastapi_app
        self.find = find_fastapi_app

    def test_detects_fastapi(self):
        code = "from fastapi import FastAPI\napp = FastAPI()\n"
        tree = ast.parse(code)
        assert self.find(tree) is not None

    def test_no_fastapi(self):
        code = "x = 1\n"
        tree = ast.parse(code)
        assert self.find(tree) is None


# --- analyze.py core function tests ---

class TestExtractStructure:
    """Tests for extract_structure."""

    def setup_method(self):
        from analyze import extract_structure
        self.extract = extract_structure

    def test_extracts_class(self, tmp_path):
        f = tmp_path / "test.py"
        f.write_text("class Foo:\n    def bar(self): pass\n")
        result = self.extract(f)
        assert result is not None
        assert len(result["classes"]) == 1
        assert result["classes"][0]["name"] == "Foo"
        assert "bar" in result["classes"][0]["methods"]

    def test_extracts_function(self, tmp_path):
        f = tmp_path / "test.py"
        f.write_text("def hello(name, greeting='hi'): pass\n")
        result = self.extract(f)
        assert result is not None
        assert len(result["functions"]) == 1
        assert result["functions"][0]["name"] == "hello"
        assert "name" in result["functions"][0]["params"]

    def test_empty_file(self, tmp_path):
        f = tmp_path / "empty.py"
        f.write_text("")
        result = self.extract(f)
        assert result is None

    def test_syntax_error(self, tmp_path):
        f = tmp_path / "bad.py"
        f.write_text("class (\n")
        result = self.extract(f)
        assert result is None


# --- compare.py core function tests ---

class TestCompareTraces:
    """Tests for compare_traces."""

    def setup_method(self):
        from compare import compare_traces
        self.compare = compare_traces

    def test_identical_traces(self):
        trace = {"files": ["a.py", "b.py"], "graph": {}, "external": ["click"]}
        result = self.compare(trace, trace)
        assert result["only_in_first"] == []
        assert result["only_in_second"] == []
        assert len(result["common"]) == 2

    def test_different_files(self):
        t1 = {"files": ["a.py", "b.py"], "graph": {}, "external": []}
        t2 = {"files": ["a.py", "c.py"], "graph": {}, "external": []}
        result = self.compare(t1, t2)
        assert "b.py" in result["only_in_first"]
        assert "c.py" in result["only_in_second"]
        assert "a.py" in result["common"]

    def test_external_diff(self):
        t1 = {"files": [], "graph": {}, "external": ["click", "rich"]}
        t2 = {"files": [], "graph": {}, "external": ["click", "flask"]}
        result = self.compare(t1, t2)
        assert "rich" in result["external_diff"]["only_in_first"]
        assert "flask" in result["external_diff"]["only_in_second"]
        assert "click" in result["external_diff"]["common"]

    def test_graph_diff(self):
        t1 = {"files": ["a.py", "b.py"], "graph": {"a.py": ["b.py"]}, "external": []}
        t2 = {"files": ["a.py", "c.py"], "graph": {"a.py": ["c.py"]}, "external": []}
        result = self.compare(t1, t2)
        assert len(result["graph_diff"]["added_edges"]) > 0 or len(result["graph_diff"]["removed_edges"]) > 0

    def test_stats_present(self):
        t1 = {"files": ["a.py"], "graph": {}, "external": []}
        t2 = {"files": ["a.py", "b.py"], "graph": {}, "external": []}
        result = self.compare(t1, t2)
        assert result["stats"]["files_in_first"] == 1
        assert result["stats"]["files_in_second"] == 2

    def test_summary_string(self):
        t1 = {"files": ["a.py", "b.py"], "graph": {}, "external": []}
        t2 = {"files": ["a.py", "c.py"], "graph": {}, "external": []}
        result = self.compare(t1, t2)
        assert "common" in result["summary"]
