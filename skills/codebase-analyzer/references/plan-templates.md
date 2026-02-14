# Plan Templates

Copy these into your implementation plans to include codebase-analyzer validation.

## Template: Feature Implementation with Validation

```markdown
## Implementation Plan: [Feature Name]

### Phase 1: Understand Existing Code
- Trace imports from [related_entry_point] to map current architecture
- Find entry points to identify where new feature integrates
- Document existing patterns to follow

### Phase 2: Implement Feature
- Create [new_files]
- Modify [existing_files]
- Add tests

### Phase 3: Validate Implementation
- Trace imports from [new_entry_point] to verify dependency tree
- Compare against planned architecture - flag unexpected dependencies
- Spawn subagents to document each new module
- Verify code does what documentation says

### Phase 4: Final Verification
- Run full trace comparison (before vs after)
- Confirm no circular dependencies introduced
- Audit implementation matches original spec
```

## Template: Refactoring with Safety Checks

```markdown
## Refactoring Plan: [Component]

### Pre-Refactor Baseline
- Trace imports from all entry points that touch [component]
- Save traces as baseline for comparison
- Document current dependency graph

### Refactoring Steps
- [Your refactoring steps here]

### Post-Refactor Validation
- Trace same entry points after changes
- Compare new traces against baseline
- Flag any broken dependencies or unexpected changes
- Verify all previous functionality still reachable
```

## Template: Documentation Generation

```markdown
## Documentation Plan: [Codebase/Module]

### Discovery
- Find all entry points in [scope]
- Trace each entry point to build complete dependency map

### Parallel Documentation
- Spawn subagents to document each major module:
  - Module purpose and responsibility
  - Public API surface
  - Dependencies (internal and external)
  - Usage patterns

### Synthesis
- Compile module docs into architecture overview
- Generate dependency diagram
- Identify and document shared utilities
```

## Template: Code Audit

```markdown
## Security/Quality Audit: [Codebase]

### Mapping Phase
- Find all entry points (main blocks, CLI, web endpoints)
- Trace each to build complete execution map
- Identify external dependencies

### Analysis Phase (Parallel Subagents)
- Subagent 1: Audit external dependencies for known vulnerabilities
- Subagent 2: Analyze code structure for anti-patterns
- Subagent 3: Verify code does what comments/docs claim
- Subagent 4: Check for dead code or unused imports

### Report
- Compile findings from all subagents
- Prioritize issues by severity
- Generate remediation recommendations
```
