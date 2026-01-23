# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
