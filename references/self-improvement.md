# Self-Improvement Protocol

How a deployed business skill should evolve in production. This protocol applies to both the skill-creator itself and any skill it generates.

---

## The Improvement Loop

```
User Feedback → Triage → Root Cause → Fix → Validate → Ship → Monitor
     ↑                                                              |
     └──────────────────────────────────────────────────────────────┘
```

---

## Phase 1: Feedback Triage

Classify every piece of user feedback into one of:

| Feedback | Signal | Priority | Response |
|----------|--------|----------|----------|
| "It didn't work" | Bug | 🔴 P0 | Fix immediately |
| "That's not what I meant" | Trigger miss | 🔴 P0 | Tighten description |
| "Can it also do X?" | Feature gap | 🟡 P1 | Evaluate effort/impact |
| "It's slow" | Performance | 🟡 P1 | Profile and optimize |
| "The output is wrong" | Quality | 🔴 P0 | Fix logic or add validation |
| "I expected Y format" | Output mismatch | 🟡 P1 | Update output contract |
| Silence after success | Signal of good quality | 🔵 P3 | No action needed |

---

## Phase 2: Root Cause Analysis

For each feedback, drill to root cause using 5-Whys:

```
"It didn't send the email"
  Why? → "API returned 401"
    Why? → "Token was expired"
      Why? → "No token refresh logic"
        Why? → "Token refresh wasn't in the requirements"
          Why? → "Requirements didn't consider token lifecycle"
```

Then map the root cause to the closest anti-pattern in [anti-patterns.md](anti-patterns.md).

---

## Phase 3: Fix Application

| Root cause | Fix location | Fix type |
|------------|-------------|----------|
| Token/session expiry | scripts/auth.py | Add refresh logic |
| Wrong trigger firing | SKILL.md description | Narrow boundary words |
| Missing feature | SKILL.md + new script | Add operation + reference |
| Bad output format | SKILL.md output spec | Update contract |
| Repeated same error | SKILL.md error section | Add recovery pattern |
| Too slow | scripts/ + SKILL.md | Add caching / batching |

**Constraint**: Every fix must be verifiable. No fix is complete without a test that proves it works.

---

## Phase 4: Validation

Run before shipping any fix:

```bash
# 1. Automated quality audit
python scripts/validate_business_skill.py <skill-dir>

# 2. Trigger precision test (if description changed)
python scripts/test_trigger.py <skill-dir> <tests.yaml>

# 3. Manual regression test
# Re-run the exact user request that triggered the feedback
# Verify the fix resolves the issue
# Re-run 2-3 other common scenarios to ensure no regression
```

---

## Phase 5: Shipping

```bash
python <skill-creator>/scripts/package_skill.py <skill-dir>
```

Update the version note in SKILL.md frontmatter:

```yaml
---
name: my-skill
# version tracked via modification history
# Last updated: 2026-07-14 — Fixed token refresh (AP-2, AP-6)
---
```

---

## Phase 6: Monitoring Signals

After deployment, watch for these signals that indicate the fix worked or needs more work:

### Positive Signals
- User stops reporting the same issue
- User spontaneously uses new features
- Throughput increases without errors

### Negative Signals
- Same issue reported again within 24h → fix didn't work, escalate
- New error appears in a different operation → regression, rollback
- User stops using the skill entirely → UX degradation, investigate

---

## Iteration Examples

### Example 1: Trigger Fix

```
User: "I said 'send the report' and it tried to draft a contract"

Root cause: AP-1 Vague Trigger Zone
  → 'send' overlaps with contract skill trigger words

Fix: Add to negative triggers in description:
  "Do NOT use for sending documents via email or messaging."

Validation: test_trigger.py with "send the report" in negative cases → score < 0.3
Ship: Re-package and deploy.
```

### Example 2: Silent Failure Fix

```
User: "It said 'Done' but no file was created"

Root cause: AP-2 Silent Failure Swallowing
  → Script caught all exceptions and returned success

Fix: Replace generic try/except with structured error handling (per faang-patterns.md §1)

Validation: Run the exact failing input, verify error is reported clearly.
Ship: Re-package and deploy.
```

### Example 3: Missing Recovery

```
User: "Network was slow and the whole thing crashed"

Root cause: AP-6 Missing Error Recovery
  → Timeout treated as fatal instead of retryable

Fix: Add retry with exponential backoff for network operations.
     Document in SKILL.md error recovery section.

Validation: Mock a slow network, verify retries happen and eventually succeed.
Ship: Re-package and deploy.
```

---

## Self-Improvement for the Skill Creator Itself

The business-skill-creator uses this same protocol on itself:

1. User reports a problem with a skill it generated → triage → root cause in the creator's patterns/templates
2. Fix the template or SKILL.md instructions in the creator
3. Re-package the creator with the fix
4. Future generated skills automatically get the improvement

This is **meta-self-improvement**: the skill that creates skills learns to create better skills.
