# What Runs on Your Machine

This document describes what the codebase-analyzer scripts do. Note that these scripts are typically invoked by an LLM, which may have access to other tools and capabilities beyond what's described here.

## Scripts

| Script | Purpose | Data Accessed |
|--------|---------|---------------|
| `trace.py` | Trace imports from entry file | Reads Python files in traced dependency tree |
| `find_entries.py` | Find entry points (main blocks, CLI commands, web apps) | Reads Python files in specified directory |
| `analyze.py` | Extract classes/functions, search patterns | Reads Python files in specified directory |
| `compare.py` | Compare two import traces | Reads JSON files or runs trace on specified files |

## How the Scripts Work

The scripts use Python's `ast.parse()` for static analysis - parsing source code into an Abstract Syntax Tree without executing it. This is the same technique used by linters and IDEs.

```python
# What happens in the scripts:
tree = ast.parse(file_content)  # Parse, don't execute
for node in ast.walk(tree):     # Walk the tree structure
    # Extract imports, classes, functions, etc.
```

## External Dependencies

The scripts depend on [`llmfiles`](https://github.com/fblissjr/llmfiles), which also uses AST-based analysis.

## Data Flow (Scripts Only)

```
File paths you specify
        |
        v
  [AST parsing]
        |
        v
  JSON to stdout
```

When running just the scripts directly:
- **Input**: File/directory paths you provide
- **Processing**: Static AST parsing
- **Output**: JSON printed to stdout

When invoked by an LLM with other tools available, the LLM may perform additional operations.

## Optional Logging

By default, the scripts don't write to disk. With the `--log` flag:

- Output is written to `scripts/internal/log/`
- Log files are timestamped JSON (e.g., `trace_2024-01-15_10-30-45.json`)

## Excluded Directories

These directories are skipped during analysis:

- `.venv`, `venv` - Virtual environments
- `.git` - Git metadata
- `__pycache__` - Python cache
- `node_modules` - Node.js dependencies
- `.tox`, `.pytest_cache`, `.mypy_cache` - Test/type caches
- `dist`, `build`, `.eggs`, `*.egg-info` - Build artifacts

## Subprocess Calls

Two scripts spawn subprocesses:

| Script | Subprocess | Purpose |
|--------|------------|---------|
| `trace.py` | `llmfiles` | Dependency resolution |
| `compare.py` | `trace.py` | Generate traces for comparison |

## Important Context

These scripts are designed to be invoked by Claude Code or similar LLM tools. The LLM itself may have broader capabilities (shell access, file writing, network access via other tools). This documentation only describes what the codebase-analyzer scripts themselves do - not what the LLM orchestrating them might do.
