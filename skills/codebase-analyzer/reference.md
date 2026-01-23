# llmfiles Reference

Quick reference for llmfiles flags used by codebase-analyzer.

## Core Import Tracing

### --deps
Smart import tracing with unused symbol filtering.

```bash
llmfiles main.py --deps
```

Only follows imports for symbols actually used in code. Recommended for most use cases.

### --deps --all
Trace ALL imports without filtering.

```bash
llmfiles main.py --deps --all
```

Use when `--deps` misses something (lazy imports, dynamic imports).

### --trace-calls (Legacy)
Alias for `--deps --all`. Backward compatible.

```bash
llmfiles main.py --trace-calls
```

## File Selection

### --include
Include files matching glob pattern.

```bash
llmfiles . --include "**/*.py"
llmfiles . --include "src/**/*.py"
```

### --exclude
Exclude files matching pattern.

```bash
llmfiles . --exclude "**/test_*"
llmfiles . --exclude "**/__pycache__/**"
```

### --max-size
Exclude files larger than size.

```bash
llmfiles . --max-size 1MB
llmfiles . --max-size 500KB
```

## Content Filtering

### --grep-content
Include only files containing pattern.

```bash
llmfiles . --grep-content "class.*Handler"
llmfiles . --grep-content "import click"
```

## Structure-Aware Processing

### --chunk-strategy structure
Extract functions/classes instead of full files.

```bash
llmfiles --chunk-strategy structure --include "**/*.py"
```

Useful for semantic search and understanding.

## GitHub Support

### Direct Repository Processing
```bash
llmfiles https://github.com/user/repo
llmfiles https://github.com/user/repo --include "**/*.py"
```

Clones to temp directory, processes, auto-cleans.

## Ignore Behavior

### --no-ignore
Don't respect .gitignore.

```bash
llmfiles . --no-ignore
```

By default, llmfiles respects .gitignore patterns.

## Binary Files

### --include-binary
Include binary files (excluded by default).

```bash
llmfiles . --include-binary
```

## Combination Examples

### Python Project Analysis
```bash
llmfiles . --include "**/*.py" --exclude "**/test_*" --max-size 500KB
```

### Trace with Size Limit
```bash
llmfiles main.py --deps --max-size 1MB
```

### GitHub + Pattern
```bash
llmfiles https://github.com/user/repo --include "src/**/*.py" --grep-content "API"
```

## Output Format

llmfiles outputs concatenated file content with markers:

```
--- path/to/file.py ---
<file content>

--- path/to/other.py ---
<file content>
```

The codebase-analyzer scripts parse this format to extract file lists and build dependency graphs.
