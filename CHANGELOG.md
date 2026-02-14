# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.2]

### Removed

- `agents/codebase-explorer.md` and `agents/` directory (used outdated `llmfiles` CLI invocations, duplicated SKILL.md triggers)
- `pyright` from runtime dependencies (moved to dev dependency group; no script imports it)

### Changed

- CLAUDE.md directory structure updated to reflect agents/ removal
- `pyproject.toml` uses `[dependency-groups]` for dev dependencies instead of `[project.optional-dependencies]`

## [2.0.1]

### Fixed

- **compare.py v2.0 compatibility**: `normalize_graph()` now handles enriched call_graph dict edges (`{to, module, line}`) alongside legacy string lists
- **compare.py key lookup**: Reads from `call_graph` key (v2.0 format) with `graph` fallback (v1.x)
- **compare.py external deps**: Handles both dict format (v2.0: package -> importing files) and list format (v1.x)

### Added

- Pyright LSP usage documentation in README.md and docs/usage.md (installation, available operations, combined workflow examples)
- `test_graph_diff_v2_format` test for v2.0 compare compatibility
- `.gitignore` entry for `scripts/internal/log/` trace artifacts

## [2.0.0]

### Added

- **Direct llmfiles library integration**: trace.py now imports `CallTracer` directly instead of calling llmfiles as a subprocess, providing richer call graph data with per-edge line numbers
- **Hub module detection**: trace.py computes hub scores (in-degree + out-degree) and reports top 5 hub modules in stats
- **`--grep` flag for trace.py**: Find files containing a pattern, then trace their dependencies (uses llmfiles' `grep_files_for_content`)
- **`--since` flag for trace.py**: Filter traced files to those modified in git within a time window (uses llmfiles' `get_git_modified_files`)
- **Class inheritance extraction**: analyze.py now reports base classes for each class
- **Decorator extraction**: analyze.py reports decorators on classes and functions (enables framework detection: `@dataclass`, `@app.route`, etc.)
- **Docstring extraction**: analyze.py extracts summary line of docstrings for classes and functions
- **Type annotation extraction**: analyze.py reports parameter type hints and return type annotations
- **Async function detection**: analyze.py identifies `async def` functions
- **Combined AST + LSP workflow guidance**: SKILL.md documents how to combine codebase-analyzer with pyright LSP for deep analysis
- **LSP-aware workflow examples**: references/workflows.md includes content-based discovery, recent changes analysis, and combined AST+LSP deep analysis workflows
- Unit tests for `compute_hub_scores`, `detect_cycles`, `_is_subpath`, enriched `extract_structure` (inheritance, docstrings, decorators, type hints, async)
- Integration tests for `--grep` and `--since` flags and enriched output format

### Changed

- **trace.py rewritten**: Removed `parse_llmfiles_output()`, `build_dependency_graph()`, `analyze_imports_from_file()` -- all replaced by direct `CallTracer` library usage
- **trace.py output format enriched**: `call_graph` now contains per-edge objects with `to`, `module`, `line` fields instead of flat file lists; `external` maps package name to list of importing files; `stats` includes `hub_modules`, `parse_errors`, `skipped_imports`
- **Subprocess fallback preserved**: llmfiles_wrapper.py kept for environments where library import fails
- **structlog suppressed**: llmfiles' structlog output redirected to WARNING level to keep stdout clean for JSON
- CLAUDE.md updated with strategic architecture context (AST + LSP + Claude layers)
- README.md updated with enriched capability descriptions and AST+LSP synergy explanation
- docs/usage.md updated with advanced workflows section

### Removed

- `parse_llmfiles_output()` -- fragile regex parsing of llmfiles text output (never matched current formats)
- `build_dependency_graph()` -- duplicated llmfiles' own graph building
- `analyze_imports_from_file()` -- redundant AST import analysis
- Tests for removed functions replaced with tests for new architecture

## [1.2.0]

### Added

- Interpreting Results section in SKILL.md -- guides Claude on what to DO with analysis output
- Limitations section in SKILL.md -- clarifies Python-only scope, static analysis boundaries
- Error Recovery section in SKILL.md -- maps error_type codes to user actions
- "How Claude Knows to Use This" section in SKILL.md body -- explains plugin registration chain
- `commands/find-entries.md` -- missing slash command for entry point discovery
- `commands/compare.md` -- missing slash command for trace comparison
- `skills/codebase-analyzer/references/` directory for progressive disclosure:
  - `user-journeys.md` -- conversation-style analysis examples with branching paths
  - `plan-templates.md` -- copy-paste templates for implementation plans
- `scripts/internal/file_utils.py` -- shared `find_python_files()` with canonical exclude set
- 46 unit tests for core functions (`tests/test_core_functions.py`)
- `orjson` dependency for JSON serialization

### Changed

- SKILL.md description rewritten for better natural-language triggering (~525 chars with intent phrases like "what does this code actually do", "I just cloned this repo")
- `trace.py` now uses `internal/llmfiles_wrapper.py` instead of inline subprocess calls
- `trace.py` uses `sys.stdlib_module_names` instead of hardcoded 50+ module set
- `trace.py` cycle detection no longer limited to first 10 files
- `find_entries.py` and `analyze.py` use shared `find_python_files()` from `internal/file_utils.py`
- `internal/output.py` switched from `json` to `orjson` for serialization
- `compare.py` switched from `json` to `orjson` for JSON loading
- `workflows.md` moved to `references/workflows.md`
- `reference.md` moved to `references/llmfiles-reference.md`
- README.md rewritten with verified installation, real examples, accurate capabilities
- `docs/usage.md` rewritten as focused usage guide (~135 lines, down from 759)
- `docs/security.md` rewritten with comprehensive per-script security model
- `docs/what-runs-on-your-machine.md` rewritten with detailed transparency tables
- AGENTS.md updated to reflect new directory structure and conventions
- Existing test for removed `--json` flag updated to test `--log` flag instead

### Removed

- 5 orphaned skill folders: `skills/code-exploration/`, `skills/debugging/`, `skills/documentation/`, `skills/import-tracing/`, `skills/reference-matching/` (never loaded by plugin.json, had invalid frontmatter)
- No-op `--json` flag from all scripts (JSON is always the output format)

## [1.1.0]

### Added

- SKILL.md YAML frontmatter with `name` and `description` fields (required for automatic skill triggering)
- `.claude-plugin/marketplace.json` for GitHub-based plugin distribution
- Installation scope table in docs/usage.md
- Comprehensive "Subagents and Composability" documentation section:
  - Trigger phrases for automatic activation
  - Subagent patterns (parallel analysis, fan-out/fan-in, pipeline composition)
  - Integration with implementation workflows (planning, during, post)
  - Plan templates (feature implementation, refactoring, documentation generation, code audit)
  - Composing with other tools (test runners, doc generators, code review, security scanners)
  - Multi-agent coordination patterns (leader-worker, verification chain, competitive analysis)
  - Full workflow example with multiple subagents
- "Real-World Scenario: Documenting a Complex ML Pipeline" - comprehensive example with coordinator pattern validation, multi-entry-point tracing, and gap analysis workflow

### Changed

- SKILL.md now uses `${CLAUDE_PLUGIN_ROOT}` for portable script paths (works with marketplace installs)
- Added `allowed-tools: Bash(uv:*)` to SKILL.md frontmatter
- README.md installation section now shows marketplace commands for persistent installation
- docs/usage.md fixed incorrect `claude mcp add` to use proper plugin system

## [1.0.3]

### Added

- User Journeys documentation with branching conversation paths
- "How Claude Knows to Use This" section explaining plugin mechanism
- "The Four Modes" summary table (one-and-done, with Claude, with subagents, composable)

### Changed

- Expanded SKILL.md "When to Use" triggers from feature-oriented to intent-oriented
  - Added "deep documentation from entry point" triggers for granular code analysis requests
- README.md now includes "How It Works" section explaining plugin registration
- Restructured usage.md for better discoverability

### Removed

- Direct llmfiles section from usage.md (irrelevant for Claude Code users)

## [1.0.2]

### Added

- `docs/what-runs-on-your-machine.md` - Transparency documentation explaining scripts, data flow, and subprocess calls
- `docs/security.md` - Security properties summary
- `AGENTS.md` - Agent context for codebase navigation

### Changed

- Slimmed down README.md with links to detailed docs

## [1.0.1]

### Changed

- Fixed `plugin.json` paths to use `./` prefix (required by Claude Code schema)
- Simplified README installation instructions to use `--plugin-dir` flag
- Removed incorrect `"plugins": ["path"]` syntax from documentation

## [1.0.0]

### Added

- Initial release
- `trace.py` - Import tracing with structured JSON output
  - Smart filtered tracing via llmfiles --deps
  - Full tracing via --all flag
  - Dependency graph construction
  - Circular dependency detection
  - External package identification
- `find_entries.py` - Entry point discovery
  - main block detection (if __name__ == "__main__")
  - Click command detection
  - FastAPI app detection
  - Flask app detection
  - Typer app detection
  - argparse usage detection
- `analyze.py` - Codebase structure analysis
  - Class extraction with methods
  - Function extraction with parameters
  - Pattern search in names
  - Parallel processing support
- `compare.py` - Trace comparison
  - File list comparison
  - Graph edge differences
  - External dependency differences
  - Statistics and summary
- Internal utilities
  - llmfiles_wrapper.py for CLI invocation
  - output.py for JSON emission and logging
- Test suite with sample project fixture
- Skills documentation (SKILL.md, workflows.md, reference.md)
- Slash commands (trace.md, analyze.md)
