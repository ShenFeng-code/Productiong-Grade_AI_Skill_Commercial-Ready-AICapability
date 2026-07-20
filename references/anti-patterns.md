# Skill Anti-Patterns — What NOT to Do

Common skill design mistakes that cause production failures. Each anti-pattern includes symptoms, root cause, fix, and prevention.

---

## AP-1: Vague Trigger Zone

**Symptom**: Skill fires on every request vaguely related to the domain. Agent is confused about which skill to use.

**Root cause**: Description is too broad. Example: `description: "Contract management. Use when the user mentions contracts."`

**Fix**: Narrow the trigger boundary. Specify exact verbs and contexts:

```yaml
# ❌ Bad
description: "Contract management. Use when the user mentions contracts."

# ✅ Good
description: >
  Contract drafting and review. Use when the user explicitly wants to:
  (1) Draft a new contract (NDA, service agreement, employment contract),
  (2) Review an existing contract for risks or compliance issues,
  (3) Compare two versions of the same contract.
  Do NOT use for general legal questions, contract negotiation advice, or template browsing.
```

**Prevention**: Run `test_trigger.py` with at least 10 positive and 10 negative cases before shipping.

---

## AP-2: Silent Failure Swallowing

**Symptom**: Skill returns "Done!" but nothing happened. User must re-verify manually.

**Root cause**: try/except blocks that catch everything and return generic success. No output verification.

**Fix**: Every operation must verify its own output:

```python
# ❌ Bad
try:
    shutil.copy(src, dst)
    return {"status": "ok"}
except Exception:
    return {"status": "ok"}  # LIES

# ✅ Good
result = subprocess.run(cmd, capture_output=True, text=True)
if result.returncode != 0:
    return {"status": "error", "reason": result.stderr[:200]}
if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
    return {"status": "error", "reason": "Output file empty or missing"}
return {"status": "ok", "path": output_path, "size": os.path.getsize(output_path)}
```

**Prevention**: Validation step in every operation. Scripts must return structured status objects.

---

## AP-3: SKILL.md Bloat

**Symptom**: SKILL.md is 800+ lines. Agent skips sections. Skill behavior is inconsistent.

**Root cause**: Everything crammed into SKILL.md instead of split into references.

**Fix**: Progressive disclosure per faang-patterns.md §6:

| Content | Location | Max lines |
|---------|----------|-----------|
| Core workflow + quick start | SKILL.md | 500 |
| Domain details | references/domain.md | 200 |
| API docs | references/api-details.md | 300 |
| Templates | references/templates/ | N/A |
| Scripts | scripts/ | Executable |

**Prevention**: `validate_business_skill.py` checks body length and warns above 500 lines.

---

## AP-4: Hardcoded Paths and Secrets

**Symptom**: Skill works on developer's machine, fails everywhere else.

**Root cause**: Absolute paths, hardcoded API keys, OS-specific assumptions.

**Fix**: Use relative paths from workspace root. Secrets from environment variables only:

```python
# ❌ Bad — hardcoded credentials and paths
auth = "YOUR_SECRET_KEY_HERE"
output_dir = "/home/dev/projects/output"

# ✅ Good — from environment, workspace-relative
auth = os.environ["MY_SERVICE_API_KEY"]
output_dir = os.environ.get("WORKSPACE_OUTPUT", os.getcwd())
```

**Prevention**: `validate_business_skill.py` scans for common secret patterns.

---

## AP-5: No Idempotency

**Symptom**: Running the skill twice creates duplicate output, double-sends, or corrupts state.

**Root cause**: No uniqueness check before creating resources.

**Fix**: Declare and implement idempotency strategy:

```markdown
## Output Specification
- **Idempotency**: Running twice with same input overwrites previous output (not append, not duplicate).
```

```python
# For API calls: use idempotency keys
headers = {"Idempotency-Key": hashlib.md5(payload.encode()).hexdigest()}

# For files: check before creating
if os.path.exists(output_path):
    log.warning(f"Overwriting existing output: {output_path}")
```

**Prevention**: Output specification must include idempotency behavior.

---

## AP-6: Missing Error Recovery

**Symptom**: One failure cascades to abort the entire workflow. Partial progress is lost.

**Root cause**: No tiered error handling. Every failure treated as fatal.

**Fix**: FAANG §1 tiered response:

| Error level | Action |
|-------------|--------|
| Transient (timeout, rate limit) | Retry with backoff, max 3 attempts |
| Recoverable (bad input, missing file) | Report and ask user |
| Fatal (auth, permission) | Clean abort with diagnosis |

**Prevention**: Every tool call in SKILL.md must have an `If [tool] fails:` recovery block.

---

## AP-7: Ignoring User Context

**Symptom**: Skill always starts from scratch, even when the user just provided relevant data.

**Root cause**: No context-passing mechanism. Skill doesn't read from memory/previous outputs.

**Fix**: Declare context awareness in SKILL.md:

```markdown
## Context Awareness
- If files are attached to the user's message, process them directly
- If the user just created a contract, offer to review it next
- If the same operation was just completed, confirm before re-running
```

**Prevention**: Add context-awareness section to SKILL.md skeleton.

---

## AP-8: Over-Engineering

**Symptom**: Skill has 10 scripts, 8 references, and takes 30 seconds to load—but only one simple operation is ever used.

**Root cause**: Building for hypothetical use cases instead of actual user needs. Gold-plating.

**Fix**: Start with the 20% of features that cover 80% of use cases. Add complexity only when real users hit the boundary:

```markdown
# Phase 1 (ship now):
- Core operation only

# Phase 2 (after 10+ real uses):
- Add batch mode if requested ≥3 times
- Add format conversion if requested ≥3 times

# Phase 3 (never until proven needed):
- Webhook integration
- Multi-language support
- Custom plugin system
```

**Prevention**: Before adding any file to the skill, ask: "Has a real user asked for this?"

---

## Anti-Pattern Severity Classification

| Anti-pattern | Severity | Detected by |
|-------------|----------|-------------|
| AP-1 Vague Triggers | 🔴 Critical | `test_trigger.py` + manual review |
| AP-2 Silent Failure | 🔴 Critical | Code review |
| AP-3 SKILL.md Bloat | 🟡 Warning | `validate_business_skill.py` |
| AP-4 Hardcoded Secrets | 🔴 Critical | `validate_business_skill.py` |
| AP-5 No Idempotency | 🟡 Warning | Output spec check |
| AP-6 Missing Recovery | 🟡 Warning | Manual review |
| AP-7 No Context | 🟡 Warning | Manual review |
| AP-8 Over-Engineering | 🔵 Info | Manual review |
