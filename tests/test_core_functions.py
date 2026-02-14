"""Unit tests for core functions (not integration/subprocess tests).

Tests the actual Python functions directly rather than running scripts via subprocess.
"""

import ast
import sys
import tempfile
from pathlib import Path
from collections import defaultdict

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

class TestComputeHubScores:
    """Tests for compute_hub_scores."""

    def setup_method(self):
        from trace import compute_hub_scores
        self.compute = compute_hub_scores

    def test_empty_graph(self):
        scores = self.compute({})
        assert scores == []

    def test_single_edge(self):
        graph = {Path("a.py"): {Path("b.py")}}
        scores = self.compute(graph)
        assert len(scores) == 2
        # a.py has out_degree=1, b.py has in_degree=1
        files = {s["file"] for s in scores}
        assert Path("a.py") in files
        assert Path("b.py") in files

    def test_hub_detection(self):
        """Hub module should have highest score."""
        graph = {
            Path("a.py"): {Path("hub.py")},
            Path("b.py"): {Path("hub.py")},
            Path("c.py"): {Path("hub.py")},
            Path("hub.py"): {Path("d.py"), Path("e.py")},
        }
        scores = self.compute(graph)
        assert scores[0]["file"] == Path("hub.py")
        assert scores[0]["in_degree"] == 3
        assert scores[0]["out_degree"] == 2
        assert scores[0]["score"] == 5

    def test_returns_top_5(self):
        graph = {Path(f"{i}.py"): {Path(f"{i+1}.py")} for i in range(10)}
        scores = self.compute(graph)
        assert len(scores) <= 5


class TestDetectCycles:
    """Tests for detect_cycles."""

    def setup_method(self):
        from trace import detect_cycles
        self.detect = detect_cycles

    def test_no_cycles(self):
        graph = {Path("a.py"): {Path("b.py")}, Path("b.py"): {Path("c.py")}}
        cycles = self.detect(graph)
        assert cycles == []

    def test_simple_cycle(self):
        graph = {
            Path("a.py"): {Path("b.py")},
            Path("b.py"): {Path("a.py")},
        }
        cycles = self.detect(graph)
        assert len(cycles) > 0

    def test_self_loop(self):
        graph = {Path("a.py"): {Path("a.py")}}
        cycles = self.detect(graph)
        assert len(cycles) > 0

    def test_empty_graph(self):
        cycles = self.detect({})
        assert cycles == []

    def test_limits_to_10(self):
        """Should return at most 10 cycles."""
        # Create a graph with many small cycles
        graph = {}
        for i in range(20):
            a = Path(f"a{i}.py")
            b = Path(f"b{i}.py")
            graph[a] = {b}
            graph[b] = {a}
        cycles = self.detect(graph)
        assert len(cycles) <= 10


class TestRunTrace:
    """Tests for run_trace error handling."""

    def setup_method(self):
        from trace import run_trace
        self.run = run_trace

    def test_nonexistent_file(self):
        result = self.run("/nonexistent/path/file.py")
        assert result["status"] == "error"
        assert result["error_type"] == "file_not_found"

    def test_non_python_file(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("not python")
        result = self.run(str(f))
        assert result["status"] == "error"
        assert result["error_type"] == "invalid_file_type"

    def test_valid_python_file(self, tmp_path):
        f = tmp_path / "test.py"
        f.write_text("import os\nx = 1\n")
        result = self.run(str(f))
        # Should succeed (either via library or subprocess)
        assert "status" not in result or result.get("status") != "error"


class TestIsSubpath:
    """Tests for _is_subpath helper."""

    def setup_method(self):
        from trace import _is_subpath
        self.check = _is_subpath

    def test_child_path(self):
        assert self.check(Path("/a/b/c"), Path("/a/b"))

    def test_same_path(self):
        assert self.check(Path("/a/b"), Path("/a/b"))

    def test_unrelated_path(self):
        assert not self.check(Path("/x/y"), Path("/a/b"))

    def test_parent_of_child(self):
        assert not self.check(Path("/a"), Path("/a/b"))


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

    def test_class_inheritance(self, tmp_path):
        f = tmp_path / "test.py"
        f.write_text("class Child(Parent, Mixin):\n    pass\n")
        result = self.extract(f)
        assert result is not None
        assert result["classes"][0]["bases"] == ["Parent", "Mixin"]

    def test_class_no_bases(self, tmp_path):
        f = tmp_path / "test.py"
        f.write_text("class Simple:\n    pass\n")
        result = self.extract(f)
        assert result is not None
        assert "bases" not in result["classes"][0]

    def test_docstring_extraction(self, tmp_path):
        f = tmp_path / "test.py"
        f.write_text('class Foo:\n    """My class docstring."""\n    pass\n')
        result = self.extract(f)
        assert result is not None
        assert result["classes"][0]["docstring"] == "My class docstring."

    def test_function_docstring(self, tmp_path):
        f = tmp_path / "test.py"
        f.write_text('def foo():\n    """Does stuff."""\n    pass\n')
        result = self.extract(f)
        assert result is not None
        assert result["functions"][0]["docstring"] == "Does stuff."

    def test_no_docstring(self, tmp_path):
        f = tmp_path / "test.py"
        f.write_text("def foo():\n    pass\n")
        result = self.extract(f)
        assert result is not None
        assert "docstring" not in result["functions"][0]

    def test_decorator_extraction(self, tmp_path):
        f = tmp_path / "test.py"
        f.write_text("@dataclass\nclass Config:\n    pass\n")
        result = self.extract(f)
        assert result is not None
        assert result["classes"][0]["decorators"] == ["dataclass"]

    def test_function_decorators(self, tmp_path):
        f = tmp_path / "test.py"
        f.write_text("@app.route('/api')\ndef handler():\n    pass\n")
        result = self.extract(f)
        assert result is not None
        assert "app.route" in result["functions"][0]["decorators"]

    def test_type_annotations(self, tmp_path):
        f = tmp_path / "test.py"
        f.write_text("def greet(name: str, age: int) -> str:\n    pass\n")
        result = self.extract(f)
        assert result is not None
        func = result["functions"][0]
        assert func["type_hints"]["name"] == "str"
        assert func["type_hints"]["age"] == "int"
        assert func["returns"] == "str"

    def test_no_type_hints(self, tmp_path):
        f = tmp_path / "test.py"
        f.write_text("def foo(x, y):\n    pass\n")
        result = self.extract(f)
        assert result is not None
        assert "type_hints" not in result["functions"][0]
        assert "returns" not in result["functions"][0]

    def test_async_function(self, tmp_path):
        f = tmp_path / "test.py"
        f.write_text("async def fetch(url: str) -> dict:\n    pass\n")
        result = self.extract(f)
        assert result is not None
        func = result["functions"][0]
        assert func["name"] == "fetch"
        assert func["async"] is True
        assert func["returns"] == "dict"


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
