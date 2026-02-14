# What Runs on Your Machine

last updated: 2026-02-14

This document describes exactly what the codebase-analyzer scripts do when invoked. These scripts are typically run by Claude Code (an LLM), which may have access to other tools and capabilities beyond what's described here.

## Scripts Overview

| Script | Purpose | Inputs | Outputs | Subprocesses |
|--------|---------|--------|---------|--------------|
| `trace.py` | Trace imports from entry file | Python file path | JSON to stdout | None (library import) |
| `find_entries.py` | Find entry points | Directory path | JSON to stdout | None |
| `analyze.py` | Extract code structure, search patterns | Directory path | JSON to stdout | None |
| `compare.py` | Compare two traces | Two JSON files or two entry files | JSON to stdout | `trace.py` (when using `--entry`) |

## Data Flow

```
File/directory paths you specify
        |
        v
  [ast.parse() -- static parsing, no execution]
        |
        v
  Structured JSON to stdout
```

No code is executed. No network calls are made. No files are written (unless `--log`).

## File Access

### What Gets Read
- Only `.py` files at paths you explicitly specify (or within directories you specify)
- For `compare.py` with `--entry`: the two entry files you specify
- For `compare.py` with positional args: the two JSON trace files you specify

### What Gets Written
- **By default**: Nothing. All output goes to stdout
- **With `--log` flag**: Timestamped JSON files to `scripts/internal/log/` (e.g., `trace_2026-02-14_10-30-45.json`)

### Directories Excluded from Scanning
When scanning directories (`find_entries.py`, `analyze.py`), these are always skipped:
- `.venv`, `venv` -- Virtual environments
- `.git` -- Git metadata
- `__pycache__` -- Python bytecode cache
- `node_modules` -- Node.js dependencies
- `.tox`, `.pytest_cache`, `.mypy_cache` -- Test/type check caches
- `dist`, `build`, `.eggs`, `*.egg-info` -- Build artifacts

## Subprocess Calls

| Script | Subprocess | Purpose | What It Does |
|--------|------------|---------|--------------|
| `trace.py` | None | Import resolution | Imports llmfiles `CallTracer` directly as a Python library (subprocess fallback via `llmfiles_wrapper.py` exists but is not the default path) |
| `compare.py` | `python trace.py <file>` | Generate trace for comparison | Runs trace.py via `sys.executable` as a subprocess (only with `--entry` flag) |

`llmfiles` is an AST-based library that resolves Python imports without executing code. It uses the same `ast.parse()` approach as the other scripts.

## Optional Logging

When any script is run with `--log`:
- Output is written to `scripts/internal/log/`
- Files are named `{script}_{timestamp}.json`
- Contains the same JSON that was printed to stdout
- No personal data or environment information is logged

## Important Context

These scripts are designed to be invoked by Claude Code or similar LLM tools. The LLM itself may have broader capabilities (shell access, file writing, network access via other tools). This documentation only describes what the codebase-analyzer scripts themselves do -- not what the LLM orchestrating them might do.

See [security.md](security.md) for the full security model.
