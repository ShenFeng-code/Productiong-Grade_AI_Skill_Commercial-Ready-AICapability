---
AIGC:
    Label: "1"
    ContentProducer: 001191440300708461136T1XGW3
    ProduceID: 9e4ed235a12b2350a4b33c58cd07bc68_6391ceae7f2a11f1ae905254006c9bbf
    ReservedCode1: p2qY0BS8L5MST414iDgpzgn7T2VnUtbMqp93mYVZYu6LNiRoKb5+vJsG6TraTC9FXuTA7fM+HiUOCRDhE3GPTZT/cHJKNRxzZ7qw+TpUfitwL3gaoCjR6DCq9JOehjqU51qWMlAwyq1BOSBlanR+HaIPVIPAXjCx2JhFzZjAnlLKlCjpy8TTQ54aw80=
    ContentPropagator: 001191440300708461136T1XGW3
    PropagateID: 9e4ed235a12b2350a4b33c58cd07bc68_6391ceae7f2a11f1ae905254006c9bbf
    ReservedCode2: p2qY0BS8L5MST414iDgpzgn7T2VnUtbMqp93mYVZYu6LNiRoKb5+vJsG6TraTC9FXuTA7fM+HiUOCRDhE3GPTZT/cHJKNRxzZ7qw+TpUfitwL3gaoCjR6DCq9JOehjqU51qWMlAwyq1BOSBlanR+HaIPVIPAXjCx2JhFzZjAnlLKlCjpy8TTQ54aw80=
---

# Trigger Design for Business Skills

The `description` field in SKILL.md frontmatter is the **only** mechanism Claude uses to decide when to trigger your skill. A poorly written description means the skill never fires when needed—or fires when it shouldn't.

## The Anatomy of a Trigger Description

A trigger description must answer three questions:

1. **What does this skill do?** (capability summary)
2. **When should it activate?** (trigger conditions with concrete keywords)
3. **When should it NOT activate?** (boundary clarification, optional but recommended)

## Pattern 1: Keyword-driven triggers

For skills that handle specific, well-defined tasks:

```yaml
description: >
  PDF document manipulation including rotation, merging, splitting, and text extraction.
  Use when the user mentions PDF operations: (1) Rotating or reordering pages,
  (2) Merging multiple PDFs, (3) Splitting a PDF into parts, (4) Extracting text from PDFs,
  (5) Any other PDF file modifications. Do NOT use for creating PDFs from scratch.
```

## Pattern 2: Intent-driven triggers

For skills that solve a class of problems where exact keywords vary:

```yaml
description: >
  Financial data analysis and modeling for investment decisions. Use when the user asks to
  analyze stock performance, evaluate investment opportunities, calculate financial metrics,
  compare market data, or build financial models. Covers equities, bonds, ETFs, and mutual funds.
  Do NOT use for personal budgeting or accounting.
```

## Pattern 3: Multi-language triggers

For skills serving users across languages, list trigger phrases in all supported languages:

```yaml
description: >
  Legal contract drafting and review assistant. Use when the user asks to draft a contract
  (起草合同 / 写合同 / 生成合同), review a contract for risks (审查合同 / 检查风险),
  compare contract versions (对比合同 / 版本比较), or search legal provisions
  (查法条 / 法律检索). Supports Chinese contract law primarily.
```

## Trigger Design Rules

### DO

- List **5-10 concrete user phrases** that should trigger the skill
- Include synonyms and common variations (e.g., "create", "make", "build", "generate")
- Clarify boundaries: what the skill explicitly does NOT handle
- Keep the description under 150 words for efficient context usage
- Test by imagining 20 diverse user queries and checking if they correctly trigger or not-trigger

### DON'T

- Rely on vague descriptions like "helps with documents"
- Use only one trigger phrase when users express the same intent many ways
- Omit the negative boundary—Claude needs to know when to route elsewhere
- Include procedural instructions in the description (those belong in the body)

## Quality Self-Test

After writing your description, verify against this checklist:

- [ ] A user saying the simplest trigger phrase (e.g., "rotate this PDF") will activate the skill
- [ ] A user asking about an adjacent but unrelated topic (e.g., "create a PDF report") will NOT activate the skill
- [ ] Both technical users ("merge PDFs") and non-technical users ("combine these files") trigger correctly
- [ ] The description contains no implementation details, only capabilities and triggers
*（内容由AI生成，仅供参考）*
