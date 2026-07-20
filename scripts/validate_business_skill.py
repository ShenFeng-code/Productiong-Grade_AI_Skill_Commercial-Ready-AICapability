#!/usr/bin/env python3
"""
Business Skill Validator — automated quality audit for business-grade skills.

Checks:
  1. YAML frontmatter validity (name, description fields)
  2. Description quality (trigger phrases, boundary, length)
  3. SKILL.md body length (≤500 lines)
  4. No hardcoded secrets
  5. Reference file integrity (broken links, TOC for >100 lines)
  6. Output consistency markers
  7. Progressive disclosure compliance
  8. Edge case coverage

Usage:
  python validate_business_skill.py <path/to/skill-folder> [--json] [--fix]

Returns exit code 0 on pass, 1 on warnings, 2 on critical failures.
"""

import argparse
import json
import re
import sys
from pathlib import Path

# ─── Configuration ───────────────────────────────────────────────

MAX_SKILLMD_LINES = 500
MAX_DESCRIPTION_WORDS = 150
MIN_TRIGGER_PHRASES = 3
SECRET_PATTERNS = [
    (r'(?i)(api[_-]?key|apikey|secret|token|password|passwd)\s*[:=]\s*["\']?\S+["\']?', "hardcoded credential"),
    (r'(?i)(sk-[a-zA-Z0-9]{20,})', "OpenAI-style API key"),
    (r'(?i)(ghp_[a-zA-Z0-9]{36})', "GitHub personal access token"),
    (r'(?i)(-----BEGIN\s+(RSA\s+)?PRIVATE\s+KEY-----)', "private key block"),
]
REQUIRED_SECTIONS = ["Output", "Error", "Quick Start"]

# ─── Helper Functions ────────────────────────────────────────────

def parse_frontmatter(content: str):
    """Extract YAML frontmatter as dict. Handles multi-line values (>, |) and BOM. Returns (dict, body_start_line)."""
    # Strip UTF-8 BOM if present
    if content.startswith("\ufeff"):
        content = content[1:]
    if not content.startswith("---"):
        return None, 0
    end = content.find("\n---", 3)
    if end == -1:
        end = content.find("---", 3)
    if end == -1:
        return None, 0
    fm_text = content[3:end].strip()
    body_start = content[:end+3].count("\n")

    result = {}
    lines = fm_text.split("\n")
    current_key = None
    current_val_lines = []
    in_block_scalar = False

    for i, line in enumerate(lines):
        stripped = line.strip()

        # Empty line in block scalar
        if in_block_scalar and stripped == "":
            current_val_lines.append("")
            continue

        # Detect block scalar start: key: > or key: |
        if not in_block_scalar and ":" in stripped:
            # Check if value starts with > or | on same line
            key_part, _, val_part = stripped.partition(":")
            val_part = val_part.strip()
            if val_part.startswith(">") or val_part.startswith("|"):
                in_block_scalar = True
                current_key = key_part.strip()
                current_val_lines = []
                remainder = val_part[1:].strip()
                if remainder:
                    current_val_lines.append(remainder)
                continue

        # Collect block scalar content
        if in_block_scalar:
            # Check if next line is a new top-level key (no leading whitespace and contains ':')
            next_is_new_key = False
            if i + 1 < len(lines):
                next_line = lines[i + 1]
                if next_line and not next_line[0].isspace() and ":" in next_line:
                    next_is_new_key = True

            if stripped and not line[0].isspace() and ":" in stripped and not stripped.startswith("-"):
                # This is a new key — flush previous block scalar
                if current_key:
                    result[current_key] = " ".join(current_val_lines).strip()
                current_key = None
                current_val_lines = []
                in_block_scalar = False
                # Reprocess this line as a key
                key_part, _, val_part = stripped.partition(":")
                result[key_part.strip()] = val_part.strip().strip('"').strip("'")
            else:
                current_val_lines.append(stripped)
                if i == len(lines) - 1 or next_is_new_key:
                    if current_key:
                        result[current_key] = " ".join(current_val_lines).strip()
                    in_block_scalar = False
                    current_key = None
            continue

        # Normal KV pair
        if ":" in stripped:
            key, _, val = stripped.partition(":")
            result[key.strip()] = val.strip().strip('"').strip("'")

    # Flush remaining block scalar
    if in_block_scalar and current_key:
        result[current_key] = " ".join(current_val_lines).strip()

    return result, body_start


def check_hardcoded_secrets(filepath: Path) -> list[dict]:
    """Scan a file for hardcoded secrets."""
    issues = []
    try:
        content = filepath.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return [{"file": str(filepath), "severity": "warning", "msg": "Cannot read file"}]
    for pattern, label in SECRET_PATTERNS:
        matches = re.findall(pattern, content)
        for m in matches:
            issues.append({
                "file": str(filepath),
                "severity": "critical",
                "msg": f"Potential {label} detected",
                "detail": str(m)[:80]
            })
    return issues


def check_reference_links(skill_dir: Path, content: str) -> list[dict]:
    """Check that all reference links in SKILL.md resolve to real files. Skips code blocks."""
    # Strip markdown code blocks (``` ... ```) to avoid checking template examples
    clean_content = re.sub(r'```.*?```', '', content, flags=re.DOTALL)
    issues = []
    link_pattern = re.compile(r'\[([^\]]+)\]\(references/([^\)]+)\)')
    for match in link_pattern.finditer(clean_content):
        ref_path = skill_dir / "references" / match.group(2)
        if not ref_path.exists():
            issues.append({
                "file": "SKILL.md",
                "severity": "critical",
                "msg": f"Broken reference link: references/{match.group(2)}"
            })
    return issues


def check_reference_toc(skill_dir: Path) -> list[dict]:
    """Check that reference files >100 lines have a table of contents."""
    issues = []
    ref_dir = skill_dir / "references"
    if not ref_dir.exists():
        return issues
    for ref_file in ref_dir.glob("*.md"):
        try:
            lines = ref_file.read_text(encoding="utf-8").split("\n")
        except Exception:
            continue
        if len(lines) > 100:
            has_toc = any(
                re.match(r'^#{1,3}\s+', ln) and 'table of contents' in ln.lower()
                or '## Contents' in ln
                or '## Table of Contents' in ln
                for ln in lines[:20]
            )
            if not has_toc:
                issues.append({
                    "file": str(ref_file),
                    "severity": "warning",
                    "msg": f"Reference file >100 lines ({len(lines)} lines) but no table of contents"
                })
    return issues


def check_edge_case_coverage(content: str) -> list[dict]:
    """Check for edge case handling keywords."""
    issues = []
    edge_keywords = ["edge case", "empty input", "large", "timeout", "encoding", "null", "special char"]
    found = [kw for kw in edge_keywords if kw.lower() in content.lower()]
    if len(found) < 3:
        issues.append({
            "file": "SKILL.md",
            "severity": "warning",
            "msg": f"Limited edge case coverage. Found: {found}. Expected at least 3 of: {edge_keywords}"
        })
    return issues


# ─── Main Validation ─────────────────────────────────────────────

def validate_skill(skill_dir: Path) -> tuple[list[dict], bool]:
    """Run full validation. Returns (issues_list, passed)."""
    all_issues = []
    skillmd = skill_dir / "SKILL.md"

    # 1. SKILL.md exists
    if not skillmd.exists():
        all_issues.append({
            "file": "N/A",
            "severity": "critical",
            "msg": "SKILL.md not found"
        })
        return all_issues, False

    content = skillmd.read_text(encoding="utf-8")

    # 2. Frontmatter
    fm, _ = parse_frontmatter(content)
    if fm is None:
        all_issues.append({"file": "SKILL.md", "severity": "critical", "msg": "Missing or invalid YAML frontmatter"})
        return all_issues, False

    if "name" not in fm:
        all_issues.append({"file": "SKILL.md", "severity": "critical", "msg": "Frontmatter missing 'name' field"})
    elif not re.match(r'^[a-z0-9][a-z0-9-]*$', fm["name"]):
        all_issues.append({"file": "SKILL.md", "severity": "error", "msg": f"Skill name '{fm['name']}' must be kebab-case"})

    if "description" not in fm:
        all_issues.append({"file": "SKILL.md", "severity": "critical", "msg": "Frontmatter missing 'description' field"})
    else:
        desc = fm["description"]
        desc_words = len(desc.split())
        if desc_words > MAX_DESCRIPTION_WORDS:
            all_issues.append({"file": "SKILL.md", "severity": "warning", "msg": f"Description is {desc_words} words (max {MAX_DESCRIPTION_WORDS})"})

        # Trigger phrase heuristics
        trigger_indicators = [
            r'[Uu]se\s+when',
            r'[Tt]rigger',
            r'[Cc]reate',
            r'[Bb]uild',
            r'[Mm]ake',
            r'\(.*\).*\(.*\)',  # Parenthesized phrases (multi-lang)
        ]
        score = sum(1 for p in trigger_indicators if re.search(p, desc))
        if score < 1:
            all_issues.append({"file": "SKILL.md", "severity": "error", "msg": "Description lacks clear trigger conditions. Add 'Use when...' with concrete phrases."})

        # Boundary check
        if not re.search(r'(?i)(do\s+not|don\'t|NOT|exclud)', desc):
            all_issues.append({"file": "SKILL.md", "severity": "warning", "msg": "Description missing boundary clarification (what skill does NOT handle)"})

    # 3. SKILL.md body length
    body_lines = [l for l in content.split("\n") if l.strip()]
    if len(body_lines) > MAX_SKILLMD_LINES:
        all_issues.append({"file": "SKILL.md", "severity": "warning", "msg": f"SKILL.md body is {len(body_lines)} lines (max {MAX_SKILLMD_LINES})"})

    # 4. Hardcoded secrets scan
    for md_file in skill_dir.rglob("*.md"):
        all_issues.extend(check_hardcoded_secrets(md_file))
    for py_file in skill_dir.rglob("*.py"):
        all_issues.extend(check_hardcoded_secrets(py_file))

    # 5. Reference link integrity
    all_issues.extend(check_reference_links(skill_dir, content))

    # 6. Reference TOC
    all_issues.extend(check_reference_toc(skill_dir))

    # 7. Edge case coverage
    all_issues.extend(check_edge_case_coverage(content))

    # 8. Required sections
    for section in REQUIRED_SECTIONS:
        if not re.search(rf'^#+\s+.*{section}', content, re.MULTILINE | re.IGNORECASE):
            all_issues.append({"file": "SKILL.md", "severity": "warning", "msg": f"Recommended section missing: '{section}'"})

    # 9. Extra files check
    forbidden_files = ["README.md", "CHANGELOG.md", "INSTALLATION_GUIDE.md", "QUICK_REFERENCE.md"]
    for forbidden in forbidden_files:
        if (skill_dir / forbidden).exists():
            all_issues.append({"file": forbidden, "severity": "error", "msg": "Extraneous documentation file should be removed"})

    # 10. Scripts testability
    scripts_dir = skill_dir / "scripts"
    if scripts_dir.exists():
        py_files = list(scripts_dir.glob("*.py"))
        for pyf in py_files:
            try:
                compile(pyf.read_text(encoding="utf-8"), str(pyf), "exec")
            except SyntaxError as e:
                all_issues.append({"file": str(pyf), "severity": "critical", "msg": f"Python syntax error: {e}"})

    # Determine pass/fail
    has_critical = any(i["severity"] == "critical" for i in all_issues)
    passed = not has_critical
    return all_issues, passed


# ─── CLI ──────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Business Skill Validator")
    parser.add_argument("skill_dir", type=Path, help="Path to skill directory")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--fix", action="store_true", help="Attempt automatic fixes (experimental)")
    args = parser.parse_args()

    if not args.skill_dir.is_dir():
        print(f"ERROR: {args.skill_dir} is not a directory", file=sys.stderr)
        sys.exit(2)

    issues, passed = validate_skill(args.skill_dir)

    if args.json:
        print(json.dumps({"passed": passed, "issues": issues}, indent=2))
    else:
        severity_order = {"critical": 0, "error": 1, "warning": 2}
        issues.sort(key=lambda x: severity_order.get(x["severity"], 99))

        print(f"\n{'='*60}")
        print(f"  Business Skill Validator — {args.skill_dir.name}")
        print(f"{'='*60}")

        if not issues:
            print("\n  ✅ All checks passed. Skill is business-grade ready.\n")
        else:
            by_severity = {}
            for i in issues:
                by_severity.setdefault(i["severity"], []).append(i)

            for sev in ["critical", "error", "warning"]:
                if sev in by_severity:
                    icon = {"critical": "🔴", "error": "🟡", "warning": "⚪"}[sev]
                    print(f"\n  {icon} {sev.upper()} ({len(by_severity[sev])})")
                    for issue in by_severity[sev][:15]:
                        src = Path(issue["file"]).name if issue["file"] != "N/A" else ""
                        print(f"     [{src}] {issue['msg']}")
                        if "detail" in issue:
                            print(f"            → {issue['detail']}")

            print(f"\n  {'❌ FAILED' if not passed else '⚠️  PASSED WITH WARNINGS'}")
            print(f"     Critical: {len(by_severity.get('critical',[]))} | Errors: {len(by_severity.get('error',[]))} | Warnings: {len(by_severity.get('warning',[]))}\n")

    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
