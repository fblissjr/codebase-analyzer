# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
