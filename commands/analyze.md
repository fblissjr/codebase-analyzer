---
name: analyze
description: Analyze codebase structure and search for patterns
arguments:
  - name: directory
    description: Directory to analyze
    required: false
    default: "."
  - name: pattern
    description: Search pattern for class/function names
    required: false
  - name: structure
    description: Extract code structure (classes, functions)
    required: false
    default: "true"
  - name: parallel
    description: Number of parallel workers
    required: false
    default: "1"
---

# Codebase Analysis

Analyze Python codebase structure and search for patterns.

## Usage

```bash
cd ~/utils/codebase-analyzer/skills/codebase-analyzer
uv run scripts/analyze.py {{ directory }}{% if pattern %} --pattern "{{ pattern }}"{% endif %}{% if structure == "true" %} --structure{% endif %}{% if parallel != "1" %} --parallel {{ parallel }}{% endif %}
```

## Output

The script outputs JSON with:
- `files_analyzed`: Number of Python files processed
- `structure`: Map of file -> {classes, functions} (if --structure)
- `matches`: Pattern search results (if --pattern)
- `stats`: Summary statistics

## Examples

### Structure Analysis
```bash
uv run scripts/analyze.py /path/to/project --structure
```

Output:
```json
{
  "status": "success",
  "files_analyzed": 15,
  "structure": {
    "core/engine.py": {
      "classes": [
        {"name": "Engine", "line": 10, "methods": ["process", "validate"]}
      ],
      "functions": [
        {"name": "run", "line": 45, "params": ["config"]}
      ]
    }
  },
  "stats": {
    "files_with_structure": 12,
    "total_classes": 8,
    "total_functions": 35
  }
}
```

### Pattern Search
```bash
uv run scripts/analyze.py . --pattern "Handler"
```

Output:
```json
{
  "status": "success",
  "files_analyzed": 15,
  "pattern": "Handler",
  "matches": [
    {"type": "class", "name": "RequestHandler", "line": 25, "file": "api/handlers.py"},
    {"type": "class", "name": "ErrorHandler", "line": 10, "file": "core/errors.py"}
  ],
  "match_count": 2
}
```

## Flags

- `--structure`: Extract classes and functions from all files
- `--pattern <text>`: Search for pattern in class/function names (case-insensitive)
- `--parallel <n>`: Use n parallel workers for faster processing
- `--json`: Output as JSON (default)
- `--log`: Also write output to internal/log/
