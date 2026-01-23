---
description: Match functionality from reference implementations using tracing
triggers:
  - match reference
  - implement like
  - same functionality
  - port from
  - replicate behavior
  - based on
  - reference implementation
---

# Reference Matching Skill

Use this skill when you need to implement functionality that matches a reference implementation. Tracing helps you understand what the reference actually does vs what you think it does.

## The Reference Matching Workflow

### Step 1: Clone and Trace Reference

```bash
# Clone reference repo (or use llmfiles directly on GitHub)
llmfiles https://github.com/reference/repo --include "**/*.py" --deps

# Or if already cloned
llmfiles reference_repo/main.py --deps
```

### Step 2: Identify the Feature Path

Find the specific feature you're matching:

```bash
# Find the feature entry point
llmfiles reference_repo/ --grep-content "def feature_name\|class FeatureName"

# Trace from that entry point
llmfiles reference_repo/feature.py --deps --chunk-strategy structure
```

### Step 3: Extract Structure

Get the function/class signatures:

```bash
llmfiles reference_repo/feature.py --deps --chunk-strategy structure
```

This gives you:
- Class hierarchy
- Method signatures
- Function parameters
- Module organization

### Step 4: Compare with Your Implementation

```bash
# Trace your implementation
llmfiles your_impl/feature.py --deps --chunk-strategy structure

# Compare structure and dependencies
```

## Matching Patterns

### "Implement the same training loop"

```bash
# Trace reference training code
llmfiles reference/train.py --deps --chunk-strategy structure

# Look for:
# - Data loading pattern
# - Model initialization
# - Optimizer setup
# - Training step structure
# - Logging/checkpointing
```

### "Match the API behavior"

```bash
# Trace reference API handlers
llmfiles reference/api/routes.py --deps

# Compare:
# - Endpoint definitions
# - Request/response handling
# - Middleware chain
# - Error handling
```

### "Port this feature from another language"

When porting from non-Python:
1. Read the reference manually (llmfiles only traces Python)
2. Create your Python structure
3. Use tracing to verify your Python implementation is complete

```bash
# After implementing, verify your trace
llmfiles your_port/feature.py --deps
```

## Comparison Checklist

When matching reference implementations, verify:

1. [ ] **Same dependencies traced** - Are you importing similar modules?
2. [ ] **Same class structure** - Do your classes have matching methods?
3. [ ] **Same function signatures** - Parameters, return types match?
4. [ ] **Same initialization order** - Especially for stateful code
5. [ ] **Same error handling** - Try/except in same places?

## Finding Differences

```bash
# Generate structure from both
llmfiles reference/main.py --deps --chunk-strategy structure > ref_structure.txt
llmfiles your_impl/main.py --deps --chunk-strategy structure > your_structure.txt

# Compare
diff ref_structure.txt your_structure.txt
```

Look for:
- Missing methods
- Extra dependencies (might indicate over-engineering)
- Missing dependencies (might indicate missing features)
- Different class hierarchies

## Avoiding Pitfalls

### Don't copy code
Use tracing to understand structure, then implement yourself. This:
- Avoids license issues
- Ensures you understand the code
- Allows adaptation to your context

### Don't match everything
Reference implementations often have:
- Legacy code
- Over-engineering
- Context-specific features

Trace to understand, then implement what you actually need.

### Verify behavior, not just structure
Matching structure doesn't guarantee matching behavior. Write tests against the reference behavior:

```bash
# Trace reference test to understand expected behavior
llmfiles reference/tests/test_feature.py --deps
```

## Prerequisites

Requires `llmfiles` CLI:
```bash
uv add git+https://github.com/fblissjr/llmfiles
```
