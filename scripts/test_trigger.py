#!/usr/bin/env python3
"""
Trigger Precision Tester — Validate skill trigger accuracy against a test suite.

Tests both positive cases (should trigger) and negative cases (should NOT trigger)
to catch false positives and false negatives before deployment.

Usage:
    python test_trigger.py <path/to/skill-folder> <test-cases.yaml>

Test cases format (YAML):
    positive:
      - "send an email to john"
      - "email the report to the team"
    negative:
      - "check my email inbox"
      - "delete my gmail account"
"""

import argparse
import os
import re
import sys
import yaml


def load_skill_description(skill_dir: str) -> str:
    """Extract the description field from SKILL.md frontmatter."""
    skill_md = os.path.join(skill_dir, "SKILL.md")
    if not os.path.exists(skill_md):
        print(f"ERROR: SKILL.md not found in {skill_dir}")
        sys.exit(1)

    with open(skill_md, "r", encoding="utf-8") as f:
        content = f.read()

    # Extract frontmatter
    match = re.search(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if not match:
        print("ERROR: No frontmatter found in SKILL.md")
        sys.exit(1)

    fm = match.group(1)
    desc_match = re.search(r"description:\s*>\s*\n((?:\s{2,}.*\n?)*)", fm)
    if not desc_match:
        print("ERROR: No description field in frontmatter")
        sys.exit(1)

    return desc_match.group(1).strip()


def load_test_cases(yaml_path: str) -> tuple:
    """Load positive and negative test cases from YAML."""
    if not os.path.exists(yaml_path):
        print(f"ERROR: Test file not found: {yaml_path}")
        sys.exit(1)

    with open(yaml_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    positives = data.get("positive", [])
    negatives = data.get("negative", [])
    return positives, negatives


def extract_triggers(description: str) -> list:
    """Extract trigger patterns from description."""
    triggers = []
    # Find patterns in "Use when the user wants to:" blocks
    lines = description.split("\n")
    in_triggers = False
    for line in lines:
        stripped = line.strip()
        if "when the user wants" in stripped.lower():
            in_triggers = True
            continue
        if in_triggers:
            if stripped.startswith(("(", "-", "*")):
                # Extract keywords and verbs
                triggers.append(stripped.lower())
            elif stripped.startswith("Do NOT"):
                break
            elif stripped == "":
                continue
            else:
                # Still in trigger zone if no blank line separator
                if stripped:
                    triggers.append(stripped.lower())
    return triggers


def extract_rejection(description: str) -> list:
    """Extract rejection patterns (what should NOT trigger)."""
    rejections = []
    lines = description.split("\n")
    in_rejection = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("Do NOT"):
            in_rejection = True
            rejections.append(stripped.lower())
        elif in_rejection and stripped:
            rejections.append(stripped.lower())
        elif in_rejection and line.strip() == "" and len(rejections) > 0:
            break
    return rejections


def score_match(test_case: str, triggers: list, rejections: list) -> float:
    """Score how well a test case matches trigger patterns."""
    tc_lower = test_case.lower()
    tc_words = set(tc_lower.split())

    # Check rejection first
    for rejection in rejections:
        rej_words = set(rejection.replace("do not", "").strip().split())
        if len(rej_words & tc_words) / max(len(rej_words), 1) > 0.6:
            return -1.0  # Strong rejection

    # Score against triggers
    best_score = 0.0
    for trigger in triggers:
        trigger_words = set(trigger.split())
        if not trigger_words:
            continue
        overlap = len(trigger_words & tc_words)
        score = overlap / max(len(trigger_words), 1)
        best_score = max(best_score, score)

    return best_score


def main():
    parser = argparse.ArgumentParser(description="Test skill trigger precision.")
    parser.add_argument("skill_dir", help="Path to skill folder")
    parser.add_argument("test_cases", help="Path to YAML test cases file")
    parser.add_argument("--threshold", type=float, default=0.3,
                        help="Trigger score threshold (default: 0.3)")
    parser.add_argument("--rejection-threshold", type=float, default=-0.5,
                        help="Rejection score threshold (default: -0.5)")
    args = parser.parse_args()

    description = load_skill_description(args.skill_dir)
    triggers = extract_triggers(description)
    rejections = extract_rejection(description)
    positives, negatives = load_test_cases(args.test_cases)

    if not triggers:
        print("WARNING: No trigger patterns found in description. Check description format.")

    print(f"\n{'='*60}")
    print(f"  Trigger Precision Test — {os.path.basename(args.skill_dir)}")
    print(f"{'='*60}\n")
    print(f"  Trigger patterns found: {len(triggers)}")
    print(f"  Rejection patterns found: {len(rejections)}")
    print(f"  Positive test cases: {len(positives)}")
    print(f"  Negative test cases: {len(negatives)}")
    print(f"  Score threshold: {args.threshold}\n")

    # Test positive cases
    print("--- POSITIVE CASES (should trigger) ---")
    fp_count = 0  # false negatives
    fn_count = 0  # actually false positives in this context
    tp_count = 0
    for tc in positives:
        score = score_match(tc, triggers, rejections)
        status = "✅" if score >= args.threshold else "❌"
        if score >= args.threshold:
            tp_count += 1
        else:
            fp_count += 1
        print(f"  {status} score={score:.2f}  \"{tc}\"")

    # Test negative cases
    print("\n--- NEGATIVE CASES (should NOT trigger) ---")
    fn_count = 0
    tn_count = 0
    for tc in negatives:
        score = score_match(tc, triggers, rejections)
        status = "✅" if score < args.threshold else "❌"
        if score < args.threshold:
            tn_count += 1
        else:
            fn_count += 1
        print(f"  {status} score={score:.2f}  \"{tc}\"")

    # Summary
    total_pos = len(positives)
    total_neg = len(negatives)
    precision = tp_count / max(total_pos, 1) * 100
    specificity = tn_count / max(total_neg, 1) * 100

    print(f"\n{'='*60}")
    print(f"  RESULTS")
    print(f"{'='*60}")
    print(f"  Positive accuracy:  {tp_count}/{total_pos} ({precision:.0f}%)")
    print(f"  Negative accuracy:  {tn_count}/{total_neg} ({specificity:.0f}%)")
    print(f"  Overall score:      {(precision + specificity) / 2:.0f}%")

    if (precision + specificity) / 2 >= 90:
        print(f"\n  ✅ Production ready (≥90%)")
    elif (precision + specificity) / 2 >= 70:
        print(f"\n  ⚠️  Needs improvement (70-89%)")
    else:
        print(f"\n  ❌ Not ready for production (<70%)")

    # Suggestions
    if fp_count > 0:
        missed = [tc for tc in positives if score_match(tc, triggers, rejections) < args.threshold]
        quoted = ", ".join(f'"{tc}"' for tc in missed)
        print(f"\n  💡 Fix false negatives: Add trigger keywords to description for:\n     {quoted}")
    if fn_count > 0:
        misfired = [tc for tc in negatives if score_match(tc, triggers, rejections) >= args.threshold]
        quoted2 = ", ".join(f'"{tc}"' for tc in misfired)
        print(f"\n  💡 Fix false positives: Tighten rejection rules for:\n     {quoted2}")


if __name__ == "__main__":
    main()
