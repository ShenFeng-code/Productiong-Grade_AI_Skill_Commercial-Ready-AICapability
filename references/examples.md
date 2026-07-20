# Business Skill Examples

Real-world examples of business-grade skills with annotated design decisions.

## Example 1: tencent-esign-contract (Legal Domain)

**What makes it business-grade:**

- **Clear trigger boundary**: Activates on contract drafting, review, comparison, and legal search. Explicitly calls out Chinese contract law scope.
- **Multi-language triggers**: Includes both Chinese and English trigger phrases.
- **Progressive disclosure**: Likely has references/ for specific contract types and legal clauses.
- **Safety-conscious**: Legal domain inherently requires accuracy—skill instructions emphasize verification and disclaimer boundaries.
- **Self-contained**: Usable by an agent with zero legal background knowledge.

**Key takeaway**: Domain-specific skills must encode enough domain knowledge to be useful, but clearly declare their jurisdictional and capability boundaries.

## Example 2: Hypothetical "api-integration-builder"

A skill that helps developers integrate third-party APIs:

**SKILL.md structure:**

```yaml
name: api-integration-builder
description: >
  Build production-ready API integration code. Use when the user asks to integrate an external API,
  connect to a REST/GraphQL service, handle authentication flows, or generate API client code.
  Supports Python (requests/httpx) and JavaScript (fetch/axios).
```

**What makes it business-grade:**

- **Error handling templates**: References file with boilerplate for retry logic, timeout handling, rate limiting
- **Security**: Instructions explicitly warn against hardcoding secrets; prompts agent to use env vars
- **Output standards**: Generated code must include type hints (Python) or JSDoc (JS), error classes, and inline comments
- **Testing**: Instructions require generating test fixtures alongside integration code
- **Versioning**: Declares target Python 3.10+ and Node 18+

## Example 3: Hypothetical "data-pipeline-validator"

A skill for validating data pipeline configurations:

**What makes it business-grade:**

- **Idempotency**: Validation operations are read-only by design—running twice produces identical results
- **Progress reporting**: For large datasets, reports "Validating table 3/12 (users)..." 
- **Edge cases**: Explicitly handles empty tables, NULL values, encoding issues, and schema mismatches
- **Output format**: Always produces a structured Markdown report with sections: Critical / Warning / Info / Passed
- **Rollback**: Since it's read-only, no rollback needed—but the skill states this explicitly

## Anti-Patterns to Avoid

These examples would FAIL business-grade review:

```yaml
# BAD: Too vague, no trigger phrases
description: "Helps with data stuff."

# BAD: No boundary clarification  
description: "Handles all file operations."

# BAD: Missing negation boundary—will fire on unrelated tasks
description: "Processes text and documents."

# BAD: Implementation detail in description
description: "Uses pandas and matplotlib to analyze data and create charts."
```
*（内容由AI生成，仅供参考）*
