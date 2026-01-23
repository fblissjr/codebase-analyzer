---
description: Systematic exploration of unfamiliar codebases using import tracing
triggers:
  - unfamiliar codebase
  - understand this project
  - how does this work
  - explore codebase
  - new to this repo
  - codebase overview
---

# Code Exploration Skill

Use this skill when you need to understand an unfamiliar codebase systematically. Instead of randomly reading files, use import tracing to follow the actual execution paths.

## Exploration Strategy

### Step 1: Find Entry Points

Look for common entry point patterns:

```bash
# Find main entry points
llmfiles . --grep-content "if __name__.*main" --include "**/*.py"

# Find CLI definitions
llmfiles . --grep-content "click.command\|argparse" --include "**/*.py"

# Find app entry points
llmfiles . --grep-content "app = Flask\|FastAPI\|create_app" --include "**/*.py"
```

Common entry point files:
- `main.py`, `__main__.py`
- `cli.py`, `cli/*.py`
- `app.py`, `wsgi.py`
- `manage.py` (Django)
- `setup.py`, `pyproject.toml` (for package entry points)

### Step 2: Trace from Entry Points

Once you find entry points, trace their dependencies:

```bash
# Trace the main entry point
llmfiles main.py --deps

# If it's a package with multiple entry points
llmfiles cli/main.py --deps
llmfiles api/app.py --deps
```

### Step 3: Extract Structure

Get the function/class hierarchy:

```bash
llmfiles main.py --deps --chunk-strategy structure
```

This shows you:
- Class definitions with methods
- Function signatures
- Module organization

### Step 4: Build Mental Model

From the trace output, identify:

1. **Core modules** - Frequently imported by many files
2. **Entry layers** - CLI, API, or UI code
3. **Business logic** - Domain-specific code
4. **Infrastructure** - Database, caching, external services
5. **Utilities** - Shared helpers

## Exploration Patterns

### "What does this project do?"

```bash
# Start with the main entry point
llmfiles main.py --deps --chunk-strategy structure

# Check the README for context
cat README.md
```

### "How is this organized?"

```bash
# List top-level structure
ls -la

# Trace from multiple entry points to see layer separation
llmfiles cli/main.py --deps
llmfiles api/routes.py --deps
```

### "Where is the business logic?"

```bash
# Trace and look for modules without framework code
llmfiles main.py --deps

# Often in: core/, domain/, services/, models/
```

### "What external dependencies are used?"

```bash
# Trace shows external deps separately
llmfiles main.py --deps --all

# Or check requirements
cat requirements.txt
cat pyproject.toml
```

## Red Flags to Watch For

When exploring, note:

1. **Circular dependencies** - A imports B imports A
2. **God modules** - One file imported everywhere
3. **Dead code** - Files not in any trace
4. **Layer violations** - UI importing database directly

## Quick Reference

```bash
# Full exploration workflow
llmfiles . --grep-content "def main\|if __name__" --include "**/*.py"  # Find entry
llmfiles <entry>.py --deps                                              # Trace deps
llmfiles <entry>.py --deps --chunk-strategy structure                   # Get structure
```

## Prerequisites

Requires `llmfiles` CLI:
```bash
uv add git+https://github.com/fblissjr/llmfiles
```
