# FAANG-Grade Engineering Patterns for AI Skills

Production patterns distilled from Google, Meta, Amazon, Apple, Netflix engineering practices, adapted for AI skill design.

## Table of Contents

1. [Error Handling (Google SRE)](#1-error-handling-google-sre)
2. [Trigger Design (Meta UX)](#2-trigger-design-meta-ux)
3. [API Integration (Amazon)](#3-api-integration-amazon)
4. [Output Consistency (Apple)](#4-output-consistency-apple)
5. [Performance & Caching (Netflix)](#5-performance--caching-netflix)
6. [Progressive Disclosure (Google)](#6-progressive-disclosure-google)
7. [Security by Default (Meta)](#7-security-by-default-meta)

---

## 1. Error Handling (Google SRE)

**Principle**: Every failure mode must be anticipated and documented. The skill must never leave the agent guessing.

### Pattern: Tiered Error Response

```
Level 0 — Transient (automatic retry):
  - Network timeout (<3s) → retry with exponential backoff (1s, 2s, 4s)
  - Rate limit (429) → wait Retry-After header, retry once
  
Level 1 — Recoverable (guided recovery):
  - File not found → list similar filenames, ask user to confirm
  - Invalid input format → show expected format, example, and ask for correction
  
Level 2 — Fatal (clean abort with diagnosis):
  - Authentication failure → instruct user to check credentials
  - Permission denied → explain required permissions, offer alternatives
  - Irrecoverable API error → report error code, suggest escalation path
```

### Required in SKILL.md

Every tool call step must include:

```markdown
If [tool] fails:
- [specific error]: [specific recovery action]
- Otherwise: [graceful degradation path]
```

---

## 2. Trigger Design (Meta UX)

**Principle**: The description is the only UI. It must be tested against real user utterances.

### Pattern: Trigger Matrix

For each skill, document a trigger matrix:

| User says | Should trigger? | Why |
|-----------|----------------|-----|
| "create a contract" | YES | "create" + domain noun |
| "review this PDF" | NO | PDF ≠ contract domain |
| "帮我写合同" | YES | Multi-language trigger |
| "draft NDA" | YES | Domain synonym |

### Anti-Pattern Detection

The description must explicitly reject these false-positive patterns:

- Domain-adjacent but off-topic requests
- Generic terms that overlap with other skills
- Compound requests where only a sub-task matches

---

## 3. API Integration (Amazon)

**Principle**: API surface must be fully encapsulated. The agent should never need to understand raw API details.

### Pattern: Three-Layer API Wrapper

```
Layer 1 — Auth & Session (scripts/auth.py):
  - Token management (refresh, expiry detection)
  - Credential loading from env vars ONLY
  - Session reuse across calls

Layer 2 — Endpoint Methods (scripts/api.py):
  - Typed request/response models
  - Automatic pagination handling
  - Rate limit awareness

Layer 3 — Business Logic (scripts/operations.py):
  - Composed operations (multi-endpoint workflows)
  - Validation and transformation
  - Idempotency keys for mutations
```

### Required in SKILL.md

```markdown
## API Dependencies

- **Base URL**: `https://api.example.com/v2`
- **Auth**: Bearer token from `$EXAMPLE_API_KEY` env var
- **Rate limit**: 100 req/min (handled automatically)
- **Pagination**: Cursor-based, max 50 items/page (handled automatically)
```

---

## 4. Output Consistency (Apple)

**Principle**: Output must be indistinguishable from a human expert's work. Same input → same structure, every time.

### Pattern: Output Contract

Every skill must declare an output contract:

```markdown
## Output Specification

**Format**: Markdown document with these exact sections:
1. `## Summary` — 1-2 sentence gist
2. `## Details` — structured findings in table format
3. `## Recommendations` — actionable numbered list
4. `## Sources` — links with access dates

**Naming**: `{topic}-{YYYYMMDD}.md`

**Idempotency**: Running twice produces identical output file (overwrite, not append).
```

### Quality Gate

- No placeholder text in final output ("TODO", "TBD", "[fill in]")
- All numbers have units
- All URLs are verified reachable (or marked as [unreachable])
- Tables have headers and consistent column counts

---

## 5. Performance & Caching (Netflix)

**Principle**: Assume large scale. Design for it from day one.

### Pattern: Progressive Loading

```
Phase 1 — Instant (<1s): Return cached summary if available
Phase 2 — Fast (<3s): Return primary results
Phase 3 — Complete (<10s): Return full analysis with all enrichments
```

### Caching Guidance

```markdown
## Performance

- Cache API responses in conversation scope (do not re-fetch within same session)
- Batch independent calls: use `asyncio.gather` for Python skills
- For files >10MB: stream-process, never load entirely into memory
- Report progress for operations >3 seconds: "Processing 3/12 files..."
```

---

## 6. Progressive Disclosure (Google)

**Principle**: SKILL.md is the lobby. Details live in rooms you only enter when needed.

### Pattern: Three-Tier Loading

```
Tier 1 — SKILL.md body (<500 lines):
  - Quick start (1 example)
  - Core workflow (numbered steps)
  - Reference index (what to read when)
  
Tier 2 — references/ (<200 lines each):
  - Domain-specific guides
  - API documentation
  - Template libraries
  
Tier 3 — scripts/ (executable without reading):
  - Deterministic operations
  - Tested with real inputs
```

### SKILL.md Reference Pattern

```markdown
## When to load each reference

| User needs | Load |
|------------|------|
| Contract drafting | [references/contracts.md] |
| Legal review | [references/review-guide.md] |
| Clause lookup | [references/clauses.md] |
```

---

## 7. Security by Default (Meta)

**Principle**: The skill must fail closed, not open.

### Pattern: Security Checklist in Every Skill

```markdown
## Security

- [ ] All credentials from environment variables, never hardcoded
- [ ] File writes restricted to output directory only
- [ ] External API calls use HTTPS only
- [ ] User data never logged or stored in temp files
- [ ] Destructive operations require explicit confirmation
- [ ] Input sanitization: reject obviously malicious inputs
```
