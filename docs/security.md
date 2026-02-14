# Security

last updated: 2026-02-14

## Summary

| Property | Script Behavior |
|----------|-----------------|
| Code analysis method | AST parsing via `ast.parse()` -- no execution of analyzed code |
| Network access | None. Scripts make no network calls |
| File reads | Only Python files at paths you specify |
| File writes | None by default. Only with explicit `--log` flag (writes to `scripts/internal/log/`) |
| Subprocess calls | `trace.py` invokes `llmfiles` (also AST-based). `compare.py` invokes `trace.py` |

## How Analysis Works

The scripts use Python's `ast.parse()` function, which converts source code into an Abstract Syntax Tree -- a data structure representing the code's structure. This is the same technique used by:

- Linters (pylint, flake8, ruff)
- Formatters (black, autopep8)
- IDEs (PyCharm, VS Code Python extension)
- Type checkers (mypy, pyright)

```python
tree = ast.parse(file_content)  # Parse source text into tree structure
for node in ast.walk(tree):     # Walk the tree
    # Extract imports, classes, functions -- never execute anything
```

The analyzed code is never loaded as a module, never imported, and never executed.

## What Runs When

### trace.py
- **Reads**: The specified Python file and its imports (resolved via AST)
- **Writes**: Nothing (unless `--log` flag)
- **Subprocesses**: Calls `llmfiles` CLI for import resolution
- **Output**: JSON to stdout

### find_entries.py
- **Reads**: All `.py` files in the specified directory (excluding `.venv`, `__pycache__`, etc.)
- **Writes**: Nothing (unless `--log` flag)
- **Subprocesses**: None
- **Output**: JSON to stdout

### analyze.py
- **Reads**: All `.py` files in the specified directory
- **Writes**: Nothing (unless `--log` flag)
- **Subprocesses**: None
- **Output**: JSON to stdout

### compare.py
- **Reads**: Two JSON trace files, or traces two entry points
- **Writes**: Nothing (unless `--log` flag)
- **Subprocesses**: May call `trace.py` when using `--entry` flags
- **Output**: JSON to stdout

## Permissions Model

The plugin's SKILL.md declares `allowed-tools: Bash(uv:*)`, which means Claude can run commands prefixed with `uv` through this plugin. In practice, this is used exclusively to invoke the analysis scripts via `uv run`.

The scripts themselves have no special permissions beyond reading files you point them at.

## Dependencies

- **llmfiles** ([github.com/fblissjr/llmfiles](https://github.com/fblissjr/llmfiles)) -- Uses the same AST-based approach for import resolution. Does not execute analyzed code
- **orjson** -- JSON serialization library. No security implications

## Important Context: Plugin vs LLM

This documentation describes what the **scripts** do in isolation. When used as a Claude Code plugin:

- The LLM (Claude) orchestrates the scripts and has broader capabilities
- The LLM can run shell commands, read/write files, and use other tools
- The LLM interprets script output and decides what to do next
- The LLM's capabilities are governed by your Claude Code permission settings, not by this plugin

Review your Claude Code permission settings to understand what the LLM can do beyond running these scripts.
