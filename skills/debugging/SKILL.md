---
description: Debug complex issues through import tracing and execution path analysis
triggers:
  - debug
  - not working
  - trace the bug
  - find the issue
  - unexpected behavior
  - wrong result
  - broken
---

# Debugging Skill

Use this skill when debugging complex issues that span multiple files. Import tracing helps you find the actual code that runs, not what you think runs.

## The Tracing Debugging Method

### Step 1: Identify the Entry Point

Find where the problematic behavior starts:

```bash
# If it's a script
llmfiles failing_script.py --deps

# If it's a test
llmfiles tests/test_failing.py --deps

# If it's an API endpoint
llmfiles . --grep-content "def endpoint_name\|@app.route.*endpoint"
```

### Step 2: Trace the Full Path

Use `--deps --all` to see all possible imports including lazy ones:

```bash
llmfiles entry_point.py --deps --all
```

This reveals:
- Conditional imports (inside if/try blocks)
- Lazy imports (inside functions)
- Plugin loading patterns

### Step 3: Verify Resolution

Check that imports resolve to the files you expect:

```bash
# See where a specific module comes from
llmfiles . --grep-content "from module import\|import module"
```

Common issues:
- **Shadowing**: Local file named same as stdlib/package
- **Stale .pyc**: Compiled bytecode from deleted files
- **Virtualenv confusion**: Wrong environment activated

### Step 4: Compare Expected vs Actual

If behavior diverges from expectation:

```bash
# Trace what you think runs
llmfiles expected_entry.py --deps

# Trace what actually runs
llmfiles actual_entry.py --deps

# Diff the results
```

## Common Debugging Patterns

### "The test passes but production fails"

```bash
# Trace test
llmfiles tests/test_feature.py --deps

# Trace production entry
llmfiles src/main.py --deps

# Look for differences in dependency graph
```

### "Changes have no effect"

Check for:
1. **Wrong file**: Trace to verify you're editing the right file
2. **Caching**: Clear __pycache__ directories
3. **Import caching**: Python caches imports within a process

```bash
# Verify which file is imported
llmfiles entry.py --deps | grep "module_name"

# Clear cache
find . -type d -name "__pycache__" -exec rm -rf {} +
```

### "ImportError but file exists"

```bash
# Check if file is in the trace
llmfiles entry.py --deps --all

# Verify PYTHONPATH/src layout
python -c "import sys; print(sys.path)"
```

### "Circular import error"

```bash
# Full trace shows import order
llmfiles entry.py --deps --all

# Look for A->B->A patterns in output
```

### "Different behavior in different environments"

```bash
# Trace in each environment and compare
# Environment A:
llmfiles entry.py --deps > trace_a.txt

# Environment B:
llmfiles entry.py --deps > trace_b.txt

diff trace_a.txt trace_b.txt
```

## Quick Debugging Checklist

1. [ ] Trace from the failing entry point
2. [ ] Verify imports resolve to expected files
3. [ ] Check for lazy imports with `--deps --all`
4. [ ] Clear __pycache__ if changes seem ignored
5. [ ] Compare trace output between working/failing cases

## Advanced: Grep Before Trace

Find where something is defined, then trace from there:

```bash
# Find where the bug might originate
llmfiles . --grep-content "def buggy_function"

# Trace from callers to see context
llmfiles caller.py --deps
```

## Prerequisites

Requires `llmfiles` CLI:
```bash
uv add git+https://github.com/fblissjr/llmfiles
```
