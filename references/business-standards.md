---
AIGC:
    Label: "1"
    ContentProducer: 001191440300708461136T1XGW3
    ProduceID: 9e4ed235a12b2350a4b33c58cd07bc68_630250ec7f2a11f1ae905254006c9bbf
    ReservedCode1: MSuEy9NH1AygBfr2f4BvTaFm6N4Wr7zye8KK1iNTGSWt8MHXrX50tBvs/fg6vCGTIA/xx9rH8XCJGaCTtZURb2xkJ2LaXHHWKl5aYsPZw7NuJOFZXZcp+0U8d9geLW5VGi3tApMrBvHW2V8i0xrDphW7khJkk55TOYnqAXfRowYq+iP61o4WwP2qP94=
    ContentPropagator: 001191440300708461136T1XGW3
    PropagateID: 9e4ed235a12b2350a4b33c58cd07bc68_630250ec7f2a11f1ae905254006c9bbf
    ReservedCode2: MSuEy9NH1AygBfr2f4BvTaFm6N4Wr7zye8KK1iNTGSWt8MHXrX50tBvs/fg6vCGTIA/xx9rH8XCJGaCTtZURb2xkJ2LaXHHWKl5aYsPZw7NuJOFZXZcp+0U8d9geLW5VGi3tApMrBvHW2V8i0xrDphW7khJkk55TOYnqAXfRowYq+iP61o4WwP2qP94=
---

# Business-Grade Standards for AI Skills

This document defines the quality bar for skills intended for production/commercial use.

## 1. Error Handling & Robustness

A business-grade skill must handle failure gracefully:

- **Expected failures**: Every tool call or script execution must anticipate failure modes and provide clear error messages with actionable next steps. Never assume external APIs or file I/O will succeed silently.
- **Retry strategy**: For transient failures (network, rate limits), include retry guidance with exponential backoff.
- **Graceful degradation**: When a non-critical step fails, the skill should continue where possible, reporting what was lost rather than aborting entirely.
- **Input validation**: Validate all user-provided inputs before passing to tools or scripts. Reject or sanitize clearly invalid inputs with helpful messages.

## 2. Security & Safety

- **No hardcoded secrets**: Never include API keys, tokens, passwords, or credentials in skill files. Reference environment variables or prompt the agent to ask the user.
- **Permission boundaries**: Clearly declare what system resources the skill accesses (filesystem, network, specific directories). Never access beyond declared scope.
- **Destructive operation guards**: Any operation that modifies, deletes, or overwrites user data must include confirmation steps and backup recommendations.
- **Data minimization**: Only collect and process the minimum data needed to accomplish the task.

## 3. Documentation Quality

- **Self-contained instructions**: The SKILL.md body must be executable without external knowledge. Any domain-specific term must be defined or referenced.
- **Concrete examples over abstraction**: Every instruction should be accompanied by a short, real-world example showing input → expected output.
- **Decision trees**: For skills with branching logic, provide clear decision trees so the agent never needs to guess which path to take.
- **Version awareness**: If the skill wraps an API or tool with versioned behavior, declare the supported version(s).

## 4. Output Consistency

- **Deterministic output format**: The skill must specify the exact structure of its output (Markdown tables, JSON schemas, file naming conventions, etc.).
- **Idempotency**: Running the same skill twice with the same inputs should not produce side-effect duplication.
- **Progress reporting**: For multi-step operations lasting more than a few seconds, include progress indicators so the user is never left staring at a blank response.

## 5. Performance & Efficiency

- **Minimize tool calls**: Batch independent operations. Avoid sequential single-item processing when batch APIs exist.
- **Context budget awareness**: Keep SKILL.md under 500 lines. Use references/ files for detail that is only occasionally needed.
- **Caching guidance**: If the skill makes repeated lookups of the same data, instruct the agent to cache results within the conversation scope.

## 6. Testing & Validation

- **Edge case coverage**: The skill instructions must explicitly address known edge cases (empty inputs, very large inputs, special characters, Unicode, timezone issues).
- **Rollback capability**: For any state-changing operation, describe how to revert to the previous state if something goes wrong.
*（内容由AI生成，仅供参考）*
