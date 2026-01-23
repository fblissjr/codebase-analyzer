# llmfiles CLI Flag Reference

Quick reference for commonly used llmfiles flags.

## Import Tracing Flags

| Flag | Purpose | When to Use |
|------|---------|-------------|
| `--deps` | Smart filtered trace | Default choice - traces used imports only |
| `--deps --all` | Full trace | When smart filter misses something |
| `--trace-calls` | Legacy alias | Same as `--deps --all` |
| `-r` | Legacy dependency resolution | Older, less accurate than `--deps` |

## Content Filtering Flags

| Flag | Purpose | Example |
|------|---------|---------|
| `--include` | Glob pattern to include | `--include "**/*.py"` |
| `--exclude` | Glob pattern to exclude | `--exclude "**/test_*"` |
| `--grep-content` | Search for pattern in files | `--grep-content "class Config"` |
| `--max-size` | Exclude files larger than | `--max-size 1MB` |

## Output Control Flags

| Flag | Purpose | Example |
|------|---------|---------|
| `--chunk-strategy` | Parsing strategy | `--chunk-strategy structure` |
| `--no-ignore` | Ignore .gitignore | When you need gitignored files |
| `--include-binary` | Include binary files | Rarely needed |

## Common Combinations

```bash
# Trace with structure extraction
llmfiles main.py --deps --chunk-strategy structure

# Find and trace
llmfiles . --grep-content "pattern" --deps

# Trace specific file types
llmfiles main.py --deps --include "**/*.py"

# Full trace without size limits
llmfiles main.py --deps --all --max-size 10MB
```

## GitHub Repository Support

```bash
# Process a GitHub repo directly
llmfiles https://github.com/user/repo

# With filters
llmfiles https://github.com/user/repo --include "**/*.py" --deps
```
