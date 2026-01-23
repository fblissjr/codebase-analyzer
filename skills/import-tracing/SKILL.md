---
description: AST-based import tracing for understanding code execution paths and dependencies
triggers:
  - trace imports
  - what code runs
  - execution path
  - dependency chain
  - follow imports
  - import graph
---

# Import Tracing Skill

Use this skill when you need to understand what code actually executes starting from an entry point. This is essential for debugging, understanding unfamiliar code, and ensuring you're reading the right files.

## Core Concept

Import tracing follows the import statements in Python files to build a complete picture of what code runs. Unlike static file listing, tracing shows you the **actual execution path**.

## When to Use Each Flag

### `--deps` (Smart Filtered Tracing)

Use when you want imports that are **actually used** in the code:

```bash
llmfiles main.py --deps
```

**Best for:**
- Understanding what code a script uses
- Finding relevant files for a feature
- Building context for code changes

**How it works:** Traces imports but filters out symbols that aren't referenced in the code. If you `import foo` but never call `foo.anything()`, it won't trace into foo.

### `--deps --all` (Full Trace)

Use when you want **all imports** including lazy/conditional ones:

```bash
llmfiles main.py --deps --all
```

**Best for:**
- Debugging "where did this import come from?"
- Finding all possible code paths
- Understanding plugin/extension systems
- When `--deps` misses something you know exists

**How it works:** Traces ALL import statements, including those inside functions (lazy imports), inside try/except blocks, and conditional imports.

### `--trace-calls` (Legacy Alias)

This is the same as `--deps --all`. Kept for backward compatibility:

```bash
llmfiles main.py --trace-calls
```

## Combining with Other Flags

### Find-then-Trace Pattern

Find files containing a pattern, then trace from them:

```bash
# Find files with "Config" classes
llmfiles . --grep-content "class.*Config"

# Then trace from the config file you found
llmfiles src/config.py --deps
```

### Include Specific File Types

```bash
llmfiles main.py --deps --include "**/*.py"
```

### Extract Structure While Tracing

Get function/class hierarchy from traced files:

```bash
llmfiles main.py --deps --chunk-strategy structure
```

## Understanding Output

The trace output shows:
1. **Dependency graph** - Which files import which
2. **File list** - All discovered files in trace order
3. **External dependencies** - Third-party packages (not traced into)

## Common Patterns

### "What runs when I execute this script?"
```bash
llmfiles script.py --deps
```

### "Where is this function actually defined?"
```bash
llmfiles . --grep-content "def my_function"
# Then trace from the file that defines it
```

### "Why is this module being imported?"
```bash
llmfiles main.py --deps --all
# Look for the module in the dependency graph
```

### "Show me all code for this feature"
```bash
llmfiles feature/main.py --deps --chunk-strategy structure
```

## Gotchas

1. **Only traces Python** - JavaScript/TypeScript support is file-listing only
2. **Doesn't execute code** - Uses pure AST parsing, safe on untrusted code
3. **Respects src-layout** - Handles `src/package/` structure correctly
4. **Excludes noise** - Automatically skips venvs, __pycache__, node_modules

## Prerequisites

Requires `llmfiles` CLI:
```bash
uv add git+https://github.com/fblissjr/llmfiles
```

## See Also

- `references/llmfiles-flags.md` - Complete flag reference
