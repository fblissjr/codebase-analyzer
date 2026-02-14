---
name: codebase-analyzer
description: AST-based Python codebase analysis that traces imports, finds entry points, and extracts code structure without executing any code. Use when the user asks to understand how a codebase works, trace what code runs from an entry point, audit or verify untrusted code, find where code starts, compare implementations, document code architecture, or deep dive into a Python project. Handles questions like "what does this code actually do", "I just cloned this repo", "trace down from main.py", "I don't trust this code", or "compare my implementation to the reference".
allowed-tools: Bash(uv:*)
---

# Codebase Analyzer

AST-based import tracing and codebase analysis using llmfiles.

## When to Use

Use this skill when the user wants to:

**Understand code**
- Understand how a Python codebase works
- Figure out what code actually runs when they execute something
- Learn the architecture of an unfamiliar project
- See which files matter vs which are dead code
- Document every granular detail of how code works starting from a file
- Trace down from an entry point to understand all dependencies
- Deep dive into a codebase starting at a specific Python file
- Exhaustively analyze code structure and flow

**Verify and trust code**
- Verify code is doing what they think it's doing
- Audit untrusted Python code without executing it
- Confirm an implementation matches a reference
- Check if a refactor broke any dependencies

**Debug issues**
- Debug import or module resolution issues
- Find why a module isn't being found
- Trace unexpected behavior to its source

**Analyze structure**
- Find all entry points in a codebase (main blocks, CLI commands, web apps)
- Identify what would be affected by a change
- Find all the ways code can be invoked
- Compare their implementation to a reference

**Technical operations**
- Trace Python imports from an entry point
- Analyze codebase structure (classes, functions)
- Compare two import traces

## Quick Reference

### Trace Imports
```bash
# Smart filtered trace (recommended)
uv run ${CLAUDE_PLUGIN_ROOT}/skills/codebase-analyzer/scripts/trace.py main.py

# Full trace (all imports)
uv run ${CLAUDE_PLUGIN_ROOT}/skills/codebase-analyzer/scripts/trace.py main.py --all

# With logging
uv run ${CLAUDE_PLUGIN_ROOT}/skills/codebase-analyzer/scripts/trace.py main.py --log
```

### Find Entry Points
```bash
# Find all entry points
uv run ${CLAUDE_PLUGIN_ROOT}/skills/codebase-analyzer/scripts/find_entries.py /path/to/project

# Filter by type
uv run ${CLAUDE_PLUGIN_ROOT}/skills/codebase-analyzer/scripts/find_entries.py . --types main_block,click_command

# Available types: main_block, click_command, fastapi, flask, typer, argparse
```

### Analyze Structure
```bash
# Extract classes and functions
uv run ${CLAUDE_PLUGIN_ROOT}/skills/codebase-analyzer/scripts/analyze.py /path/to/project --structure

# Search for pattern
uv run ${CLAUDE_PLUGIN_ROOT}/skills/codebase-analyzer/scripts/analyze.py . --pattern "Config"

# Parallel processing
uv run ${CLAUDE_PLUGIN_ROOT}/skills/codebase-analyzer/scripts/analyze.py . --structure --parallel 4
```

### Compare Traces
```bash
# Compare two trace files
uv run ${CLAUDE_PLUGIN_ROOT}/skills/codebase-analyzer/scripts/compare.py trace1.json trace2.json

# Trace and compare two entry points
uv run ${CLAUDE_PLUGIN_ROOT}/skills/codebase-analyzer/scripts/compare.py --entry ref/main.py --entry impl/main.py
```

## Output Format

All scripts output JSON to stdout with this structure:

### Success
```json
{
  "status": "success",
  "duration_ms": 234,
  ...
}
```

### Error
```json
{
  "status": "error",
  "error_type": "file_not_found",
  "message": "Entry file not found: main.py"
}
```

## Interpreting Results

After running analysis:
- Report total file count and max import depth to summarize scope
- Identify hub modules (nodes with many graph edges) as architectural focal points
- Flag circular dependencies as potential design issues needing attention
- List external dependencies so the user knows third-party requirements
- For comparisons, highlight files only in one trace as gaps or extras
- When tracing for verification, confirm the traced path matches user expectations

## Limitations

- Python codebases only. For JavaScript, TypeScript, Go, etc., use standard file exploration
- Single-file scripts with no imports gain little from tracing -- direct reading is faster
- Dynamic imports (importlib, __import__) may not be detected even with --all
- Does not analyze runtime behavior -- only static import structure

### Error Recovery
- `dependency_missing`: llmfiles not installed. Run `uv add llmfiles`
- `file_not_found`: Check the file path exists and is accessible
- `invalid_file_type`: Only .py files can be traced
- `no_files`: Directory contains no Python files (check path)
- `llmfiles_error`: llmfiles returned an error -- check stderr in details

## Subagent Patterns

### Parallel Tracing
```bash
# Trace multiple entry points in parallel
entries=("main.py" "cli.py" "api/app.py")
for entry in "${entries[@]}"; do
  uv run ${CLAUDE_PLUGIN_ROOT}/skills/codebase-analyzer/scripts/trace.py "$entry" &
done
wait
```

### Composable Pipeline
```bash
# Find entries -> trace each
uv run ${CLAUDE_PLUGIN_ROOT}/skills/codebase-analyzer/scripts/find_entries.py . | \
  jq -r '.entry_points[].file' | \
  xargs -I{} uv run ${CLAUDE_PLUGIN_ROOT}/skills/codebase-analyzer/scripts/trace.py {}
```

## How Claude Knows to Use This

The plugin registration chain:

```
.claude-plugin/plugin.json    # Registers the plugin with Claude Code
    |
    v
skills/codebase-analyzer/SKILL.md    # Defines WHEN to use and HOW to use
    |
    +-- "When to Use" section    # Triggers - Claude reads these to decide relevance
    +-- "Quick Reference"        # Commands - what Claude can actually run
```

Users don't need magic keywords. The "When to Use" section contains intent-based triggers, so when a user says "I don't trust this code - what does it actually do?", Claude recognizes this matches the verification triggers and activates the analyzer.

Claude interprets the results. The scripts output JSON, but Claude reads and explains the dependency graph, identifies architectural patterns, points out potential issues, and suggests next steps. The JSON output is designed for Claude to consume and reason about, not for users to parse manually.

## See Also

- `references/workflows.md` - Detailed workflow guides for common analysis tasks
- `references/llmfiles-reference.md` - Complete llmfiles flag reference
- `references/user-journeys.md` - Conversation-style analysis examples with branching paths
- `references/plan-templates.md` - Copy-paste templates for implementation plans
