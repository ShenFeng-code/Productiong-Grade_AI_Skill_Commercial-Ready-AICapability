---
name: business-skill-creator
description: >
  Guide for creating production-grade, business-quality AI skills with rigorous standards.
  Use when the user wants to: (1) Create a new AI skill (创建skill / 写一个skill / 帮我做个skill),
  (2) Build a production-ready or commercial-grade skill (商业级skill / 生产级skill),
  (3) Upgrade an existing skill to business quality (升级skill / 优化skill),
  (4) Design a skill with professional toolchains and quality assurance.
  Extends the base skill-creator with business standards for error handling, security,
  trigger design, output consistency, and quality auditing. Do NOT use for simple
  personal scripts or one-off automation that doesn't need production rigor.
---

# Business Skill Creator

Create production-grade AI skills that meet FAANG-level engineering standards. From natural language description to packaged `.skill` file, every phase embeds quality checks and industry patterns.

## Reference Map

| Phase | What you need | Load this |
|-------|---------------|-----------|
| 1-2 | Requirement discovery, architecture | SKILL.md (this file) |
| 2-3 | Domain templates (API/file/data/UI/expert/workflow) | [skill-templates.md](references/skill-templates.md) |
| 2 | Scaffold generator (auto-generate folder structure, --lang all for polyglot) | `scripts/generate_skill.py` |
| 2 | Multi-language coordination guide (when to use which language) | [polyglot-guide.md](references/polyglot-guide.md) |
| 3-4 | Engineering patterns (error, trigger, API, output, security, perf) | [faang-patterns.md](references/faang-patterns.md) |
| 3 | Trigger condition design rules | [trigger-design.md](references/trigger-design.md) |
| 3 | Common mistakes to avoid | [anti-patterns.md](references/anti-patterns.md) |
| 3-4 | Quality standards reference | [business-standards.md](references/business-standards.md) |
| 4 | Manual audit checklist | [quality-checklist.md](references/quality-checklist.md) |
| 4 | Automated validator (10-dimension) | `scripts/validate_business_skill.py` |
| 4 | Trigger precision tester | `scripts/test_trigger.py` |
| 6 | Iteration and self-improvement protocol | [self-improvement.md](references/self-improvement.md) |
| All | Annotated examples | [examples.md](references/examples.md) |

## Workflow

### Phase 1: Natural Language Requirement Extraction

When the user describes a skill in natural language, extract the following before writing anything:

**Step 1.1 — Parse intent.** From the user's description, identify:

| Dimension | Extract | Example |
|-----------|---------|---------|
| **Domain** | What area does this skill operate in? | API integration / file processing / data analysis / UI automation / domain expert / workflow |
| **Core capability** | What is the ONE thing the skill must do? | "Send emails via SendGrid API" |
| **Primary action verbs** | What verbs will users use? | send, dispatch, email, notify |
| **Input/output** | What goes in and comes out? | Input: recipient + content → Output: confirmation |
| **Boundary** | What does it explicitly NOT do? | Does NOT handle email templates or campaign management |

**Step 1.2 — Classify domain.** Map to the closest template in [skill-templates.md](references/skill-templates.md). If none match exactly, pick the closest and note adaptations needed.

**Step 1.3 — Validate with user.** Present the extracted intent in a compact table and ask: "Does this match what you had in mind?" Proceed only after confirmation. This is the ONLY mandatory confirmation point.

### Phase 2: Architecture Planning

Map the confirmed intent to skill structure:

1. **Generate scaffold.** Run `scripts/generate_skill.py <name> "<description>" --lang all` to create the folder skeleton with SKILL.md, scripts/, references/ pre-filled from the matched domain template. Use `--lang python` / `--lang all` etc. to control which languages get stubs. This saves time and ensures consistency.

2. **Select languages.** Load [polyglot-guide.md](references/polyglot-guide.md). Map the skill's sub-problems to the Language Decision Matrix:
   - Simple I/O + NLP → Python primary
   - Real-time/streaming → Go or Rust for hot path
   - CLI polish + schema validation → TypeScript entry
   - Orchestration/deployment → Shell runbook
   Remove languages with no real role. Keep their config files (pyproject.toml etc.) as future-proofing.

3. **Adapt the template.** Fill in domain-specific names, verbs, paths, and constraints. Reference [anti-patterns.md](references/anti-patterns.md) to avoid common mistakes during design.
3. **Identify what goes into `scripts/`, `references/`, `assets/`.** Each script must handle one operation. Each reference must answer one category of questions.
4. **Load [faang-patterns.md](references/faang-patterns.md) and mark which patterns apply.** At minimum: §1 Error Handling, §4 Output Consistency, §7 Security. Rate each as applicable/partially/none and plan implementation.

Result: a completed architecture outline that maps every user need to a concrete file.

### Phase 3: Implementation

Implement in dependency order:

1. **`scripts/`** — Write and test each script. A script that fails at runtime is a blocker. Each script must follow FAANG §1 error handling—tiered response with retry/recover/fatal.
2. **`references/`** — Write reference docs using patterns from [faang-patterns.md](references/faang-patterns.md). Load [trigger-design.md](references/trigger-design.md) when crafting the description.
3. **`assets/`** — Add templates, boilerplate, etc.
4. **`SKILL.md`** — Write the body. Use the template skeleton from [skill-templates.md](references/skill-templates.md). Cross-check against [anti-patterns.md](references/anti-patterns.md):
   - AP-1: Is the trigger boundary precise?
   - AP-3: Is SKILL.md under 500 lines?
   - AP-5: Is idempotency declared?
   - AP-6: Does every operation have error recovery?
   - AP-8: Are all files justified by real use cases?

### Phase 3.5: FAANG Benchmark Check

Before audit, verify each FAANG dimension:

| Dimension | Source | Check |
|-----------|--------|-------|
| **Error handling** | faang-patterns.md §1 | Every tool call has tiered error response documented |
| **Trigger precision** | faang-patterns.md §2 | Description contains trigger matrix logic; anti-patterns excluded |
| **API encapsulation** | faang-patterns.md §3 | If external API: auth/rate-limit/pagination all handled |
| **Output consistency** | faang-patterns.md §4 | Output contract declared with format, naming, idempotency |
| **Performance** | faang-patterns.md §5 | Batch guidance, progress reporting, caching strategy |
| **Progressive disclosure** | faang-patterns.md §6 | SKILL.md <500 lines, references one level deep |
| **Security** | faang-patterns.md §7 | No secrets, HTTPS-only, input sanitization, destructive ops gated |

Any dimension scoring <80% → return to Phase 3 and fix before proceeding.

### Phase 4: Automated Quality Audit

**Step 4.1 — Basic validation:**
```bash
python scripts/validate_business_skill.py <path/to/skill-folder>
```
Checks 10 dimensions: frontmatter, description quality, body length, secrets, references, TOC, edge cases, sections, extraneous files, script syntax. Exit criteria: Zero critical issues. Warnings must have documented justification.

**Step 4.2 — Trigger precision test:**
Create a `test-cases.yaml` with at least 10 positive and 10 negative cases, then:
```bash
python scripts/test_trigger.py <path/to/skill-folder> <test-cases.yaml>
```
Overall score must be ≥90% for production. 70-89% needs improvement. <70% is a blocker. If score <90%, go back to Phase 3 and tighten the description.

**Step 4.3 — Manual audit:**
Load [quality-checklist.md](references/quality-checklist.md) for dimensions the script cannot check (UX coherence, tone consistency, domain accuracy).

### Phase 5: Package & Deliver

```bash
python <skill-creator-path>/scripts/package_skill.py <path/to/skill-folder>
```

Confirm the `.skill` file path to the user.

### Phase 6: Iteration Protocol

Follow [self-improvement.md](references/self-improvement.md) for all post-deployment changes:

1. **Feedback triage** — Classify as bug / trigger miss / feature gap / performance / quality / output mismatch
2. **Root cause** — Drill with 5-Whys, map to [anti-patterns.md](references/anti-patterns.md)
3. **Fix** — Apply improvement, with verifiable test
4. **Validate** — Run Phase 4 on the updated skill
5. **Ship** — Re-package
6. **Monitor** — Watch for regression signals

Brief the user on monitoring signals:
- **False positives**: Skill triggering when it shouldn't → tighten description boundary
- **False negatives**: Skill not triggering when it should → add trigger phrases
- **Edge case misses**: Real-world inputs that break the skill → update references and scripts
- **Performance drift**: Skill getting slower → check caching and batching

## Quick Generation Mode

When the user says "直接生成" / "just generate" / "不需要确认" after describing the skill, skip Phase 1.3 confirmation and proceed directly to Phase 2. All other phases remain intact.

## Design Principles

1. **Natural language in, production skill out.** The user describes what they want; the skill produces it at FAANG quality.
2. **Assume failure, design recovery.** Every step that can fail must have a documented fallback.
3. **Precision in triggers, flexibility in execution.** Description must be surgically precise; body can offer judgment-based guidance.
4. **Templates over blank pages.** Always start from a domain template or `generate_skill.py`, never from scratch.
5. **Audit before you ship.** Never skip the validator, trigger tester, or FAANG benchmark check.
6. **Every fix is a lesson.** Map every bug to an anti-pattern so the same mistake is never repeated.
7. **Right language, right problem.** Default polyglot (generate --lang all for configs), then strip unused languages after Phase 2 analysis. Never force a language that adds no value; never skip a language that solves a genuine need.
