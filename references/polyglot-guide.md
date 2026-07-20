# Polyglot Skill Architecture Guide

Multi-language coordination patterns for FAANG-grade production skills.
Do not force every language into every skill; choose the right tool per sub-problem.

---

## Language Decision Matrix

| Sub-Problem | Python | TypeScript | Go | Rust | Shell |
|-------------|--------|------------|-----|------|-------|
| REST API client | Good (requests) | Good (fetch) | Good (net/http) | Good (reqwest) | Fair (curl) |
| PDF/image processing | Best (PIL/pypdf) | Fair (pdf-lib) | Fair | Fair | Poor |
| Data analysis / ML | Best (pandas/sklearn) | Fair (Danfo) | Poor | Emerging | Poor |
| Real-time / streaming | Fair | Good (streams) | Best (goroutines) | Best (async) | Poor |
| CLI / scripting | Good | Fair | Fair | Fair | Best |
| System-level / driver | Fair | Poor | Good | Best | Good |
| UI automation | Good (Playwright) | Best (Playwright) | Fair (CDP) | Fair (headless) | Fair |
| NLP / text processing | Best (spaCy/jieba) | Fair (compromise) | Fair | Emerging | Poor |
| Concurrent I/O | Fair (asyncio) | Good (Promise) | Best (goroutines) | Best (tokio) | Poor |
| Binary / byte-level | Fair | Poor | Good | Best | Fair |
| Deployment / CI | Good | Good | Good | Good | Best |

## Coordination Patterns

### Pattern 1: Shell Orchestrator → Lang Workers

```
# runbook.sh          # Shell orchestrator (best for env setup + ordering)
# processor.py        # Python NLP worker
# fetcher.go          # Go HTTP fetcher (concurrent)
# validator.rs        # Rust hot-path validator (sub-ms)
```

Shell handles environment, argument parsing, sequencing. Workers handle domain logic.
Output: JSON lines / ndjson over stdout for interop.

### Pattern 2: TypeScript Entry → Native Workers

```
# cli.ts              # TypeScript entry (Zod validation, help text)
# native/analyzer.go  # Go compiled binary for hot path
# native/extract.py   # Python script for PDF parsing
```

TypeScript provides the polished CLI experience. Native workers are spawned as subprocesses.

### Pattern 3: Single Language + Config-Only Polyglot

Most skills don't need 5 languages. Generate the config files for all languages (pyproject.toml, Cargo.toml, go.mod, package.json) but only populate scripts for the language(s) that solve the actual problem. The configs serve as "future-proofing" so contributors can add implementations later without scaffolding.

## Interop Standard

All polyglot scripts MUST communicate via one of:

1. **JSON over stdout** (preferred):
   ```json
   {"status":"ok","path":"/output/file.pdf","elapsed_ms":234}
   {"status":"error","reason":"File not found","recoverable":false}
   ```

2. **Exit codes** (bare minimum):
   - 0: success
   - 1: general error
   - 2: invalid input (retry with correction)
   - 3: auth/permission (user must intervene)

3. **Shared filesystem** (for large payloads):
   - Write to `$SKILL_OUTPUT` env var or `./output/` directory
   - Use atomic writes (write to temp, then rename)

## Anti-Patterns

| Anti-Pattern | Why It Fails | Fix |
|---|---|---|
| Re-implementing the same logic in 5 languages | Maintenance hell, bug divergence | Pick 1 primary, use FFI or subprocess for others |
| Language-for-language's-sake | Adds complexity with no benefit | Only add a language if it solves a specific performance/ecosystem need |
| Mixed-language monolith | Debugging across language boundaries is hard | Keep language boundaries at process level, not module level |
| Encoding assumptions | Windows/Unix newline mismatch, UTF-16 surprises | Always UTF-8, always `\n`, validate at boundaries |

## When to Go Polyglot

**Single-language**: Simple CRUD, single-domain skills, prototyping
**Polyglot (2-3)**: Performance-critical path + scripting + CLI polish
**Polyglot (all 5)**: Infrastructure/tooling skills that need to run anywhere, framework generators (like business-skill-creator itself)
