#!/usr/bin/env python3
"""
Skill Scaffold Generator - Multi-language production-grade skill skeleton.

Generates complete skill folder with SKILL.md, scripts/, references/,
pre-filled with FAANG-grade patterns across Python, Node.js, Go, Rust, and Shell.

Features:
  - Domain auto-classification (API / file / data / UI / expert / workflow)
  - Multi-language script stubs (Python, TypeScript, Go, Rust, Shell)
  - Each file annotated with functional comment (as shown in VS Code tree)
  - Language-appropriate error handling, type hints, and project configs

Usage:
    python generate_skill.py "my-skill" "Natural language description" [--lang LANG]

Languages:
    python  - Python 3.11+ with type hints + pytest
    node    - TypeScript 5.x with Zod + vitest
    go      - Go 1.22+ with standard library
    rust    - Rust 1.75+ with anyhow + thiserror
    shell   - POSIX sh + PowerShell 5.1
    all     - All of the above (recommended for production skills)

Example:
    python generate_skill.py "sensitive-word-checker" \
      "Detect and filter sensitive words in Chinese text. Handles homophones,
       similar characters, pinyin mappings, and abbreviations." \
      --lang all
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


# --- Domain Classification --------------------------------------------------

def classify_domain(description: str) -> str:
    desc_lower = description.lower()
    keyword_map = {
        "api-integration":  ["api", "rest", "http", "endpoint", "sdk", "webhook", "oauth"],
        "file-processing":  ["pdf", "docx", "image", "convert", "merge", "split", "compress"],
        "data-analysis":    ["analyze", "chart", "visualize", "statistics", "dashboard"],
        "ui-automation":    ["click", "screenshot", "navigate", "launch", "app", "browser"],
        "domain-expert":    ["legal", "contract", "medical", "financial", "compliance"],
        "workflow":         ["pipeline", "multi-step", "end-to-end", "onboard", "orchestrate"],
    }
    scores = {domain: sum(1 for kw in kws if kw in desc_lower) for domain, kws in keyword_map.items()}
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "api-integration"


def extract_verbs(description: str) -> list:
    common = ["send", "create", "get", "fetch", "update", "delete", "search", "list", "query",
              "download", "upload", "convert", "merge", "split", "analyze", "generate",
              "draft", "review", "compare", "automate", "launch", "navigate", "post",
              "read", "write", "extract", "transform", "clean", "validate",
              "detect", "filter", "scan", "check", "match", "replace", "map"]
    desc_lower = description.lower()
    return [v for v in common if v in desc_lower]


def slugify(name: str) -> str:
    return re.sub(r"[^a-z0-9-]", "-", name.lower().strip()).strip("-")


# --- Domain Templates -------------------------------------------------------

DOMAIN_TEMPLATES = {
    "api-integration": {
        "scripts": {
            "python":  [("client.py",     "# API client with retry + rate limit")],
            "node":    [("client.ts",     "// TypeScript API client with Zod schemas")],
            "go":      [("client.go",     "// Go HTTP client with context support")],
            "rust":    [("client.rs",     "// Rust reqwest client with error handling")],
            "shell":   [("test.sh",       "# Shell integration test script")],
        },
        "references": [
            ("api-details.md",   "# API endpoint reference"),
            ("auth-guide.md",    "# Authentication flow documentation"),
        ],
        "section_order": ["Quick Start", "Prerequisites", "Core Operations", "API Reference",
                          "Error Recovery", "Output Specification", "Security"],
    },
    "file-processing": {
        "scripts": {
            "python":  [("processor.py",  "# Core file processor")],
            "node":    [("processor.ts",  "// Streaming file processor")],
            "go":      [("processor.go",  "// Concurrent file processor")],
            "rust":    [("processor.rs",  "// Zero-copy file processor")],
            "shell":   [("batch.sh",      "# Batch processing script")],
        },
        "references": [
            ("format-specs.md","# Supported format specifications"),
            ("edge-cases.md",  "# Known edge cases and workarounds"),
        ],
        "section_order": ["Quick Start", "Supported Operations", "Core Workflow",
                          "Batch Processing", "Error Recovery", "Output Specification"],
    },
    "data-analysis": {
        "scripts": {
            "python":  [("analyzer.py",   "# Statistical analysis engine")],
            "node":    [("analyzer.ts",   "// Data pipeline with streaming")],
            "go":      [("analyzer.go",   "// High-performance aggregator")],
            "rust":    [("analyzer.rs",   "// SIMD-accelerated computation")],
            "shell":   [("pipeline.sh",   "# Data pipeline orchestrator")],
        },
        "references": [
            ("metrics.md",     "# Metric definitions and formulas"),
            ("viz-guide.md",   "# Visualization best practices"),
        ],
        "section_order": ["Quick Start", "Analysis Workflow", "Output Specification", "Edge Cases"],
    },
    "ui-automation": {
        "scripts": {
            "python":  [("automator.py",  "# UI automation driver")],
            "node":    [("automator.ts",  "// Playwright-based automator")],
            "go":      [("automator.go",  "// CDP protocol automator")],
            "rust":    [("automator.rs",  "// Headless browser controller")],
            "shell":   [("launcher.sh",   "# App launcher and health check")],
        },
        "references": [
            ("app-ui-map.md",  "# UI element selectors and navigation map"),
            ("wait-strategy.md","# Wait condition reference"),
        ],
        "section_order": ["Quick Start", "Prerequisites", "Core Workflow",
                          "Wait Strategy", "Error Recovery", "Output Specification"],
    },
    "domain-expert": {
        "scripts": {
            "python":  [("validator.py",  "# Domain rule validator")],
            "node":    [("validator.ts",  "// Schema-based validator")],
            "go":      [("validator.go",  "// Rule engine with DAG evaluation")],
            "rust":    [("validator.rs",  "// Compile-time rule checker")],
            "shell":   [("lint.sh",       "# Document lint runner")],
        },
        "references": [
            ("templates/",     "# Document templates directory"),
            ("checklist.md",   "# Review checklist"),
            ("regulations.md", "# Regulatory reference"),
        ],
        "section_order": ["Quick Start", "Document Operations", "Knowledge Boundaries",
                          "Output Specification", "Disclaimer"],
    },
    "workflow": {
        "scripts": {
            "python":  [("orchestrator.py","# Workflow orchestrator")],
            "node":    [("orchestrator.ts","// State machine orchestrator")],
            "go":      [("orchestrator.go","// Saga pattern executor")],
            "rust":    [("orchestrator.rs","// Actor-based orchestrator")],
            "shell":   [("runbook.sh",     "# Operational runbook")],
        },
        "references": [
            ("systems.md",     "# External system integration docs"),
            ("checkpoints.md", "# Checkpoint and rollback strategy"),
        ],
        "section_order": ["Quick Start", "Prerequisites", "Workflow Steps",
                          "Checkpoint Strategy", "Rollback", "Output Specification"],
    },
}

# --- Language-specific stubs ------------------------------------------------

def py_stub(module_name: str, annotation: str, skill_name: str) -> str:
    return f'''"""{annotation} - {skill_name}"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def main(*, input_path: Path | None = None, **kwargs: Any) -> dict[str, Any]:
    """Execute {module_name} operation.

    Returns:
        dict with keys: status ("ok"|"error"), path (output path if any),
        reason (error description if failed)
    """
    raise NotImplementedError("Implement {module_name} logic here")


if __name__ == "__main__":
    result = main()
    print(result)
'''


def ts_stub(module_name: str, annotation: str, skill_name: str) -> str:
    return f"""{annotation} - {skill_name}

import {{ z }} from "https://deno.land/x/zod@v3.22.0/mod.ts";

// --- Types ------------------------------------------------------------

const ResultSchema = z.object({{
  status: z.enum(["ok", "error"]),
  path: z.string().optional(),
  reason: z.string().optional(),
}});

type Result = z.infer<typeof ResultSchema>;

// --- Core -------------------------------------------------------------

export async function main(
  inputPath?: string,
  options?: Record<string, unknown>,
): Promise<Result> {{
  // TODO: Implement {module_name} logic
  throw new Error("Not implemented: {module_name}");
}}

// --- Entry ------------------------------------------------------------

if (import.meta.main) {{
  const result = await main();
  console.log(JSON.stringify(result, null, 2));
}}
"""


def go_stub(module_name: str, annotation: str, skill_name: str) -> str:
    return f"""{annotation} - {skill_name}

package main

import (
\t"context"
\t"encoding/json"
\t"errors"
\t"fmt"
\t"log"
\t"time"
)

// Result represents the outcome of a {module_name} operation.
type Result struct {{
\tStatus string `json:"status"` // "ok" | "error"
\tPath   string `json:"path,omitempty"`
\tReason string `json:"reason,omitempty"`
}}

// main executes the {module_name} operation.
func main() {{
\tctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
\tdefer cancel()

\tresult, err := run(ctx, nil)
\tif err != nil {{
\t\tlog.Fatalf("fatal: %v", err)
\t}}

\toutput, _ := json.MarshalIndent(result, "", "  ")
\tfmt.Println(string(output))
}}

func run(ctx context.Context, inputPath *string) (Result, error) {{
\treturn Result{{}}, errors.New("not implemented: {module_name}")
}}
"""


def rust_stub(module_name: str, annotation: str, skill_name: str) -> str:
    return f"""{annotation} - {skill_name}

use anyhow::{{Context, Result}};
use serde::{{Deserialize, Serialize}};
use std::path::Path;

/// Outcome of a {module_name} operation.
#[derive(Debug, Serialize, Deserialize)]
struct OpResult {{
    status: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    path: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    reason: Option<String>,
}}

fn main() -> Result<()> {{
    let result = run(None).context("operation failed")?;
    println!("{{}}", serde_json::to_string_pretty(&result)?);
    Ok(())
}}

fn run(input_path: Option<&Path>) -> Result<OpResult> {{
    Err(anyhow::anyhow!("not implemented: {module_name}"))
}}
"""


def sh_stub(module_name: str, annotation: str, skill_name: str) -> str:
    return f"""#!/usr/bin/env bash
# {annotation} - {skill_name}
set -euo pipefail

main() {{
    echo '{{"status":"error","reason":"not implemented: {module_name}"}}'
    exit 1
}}

main "$@"
"""


LANG_STUBS = {
    "python":  (".py",    py_stub),
    "node":    (".ts",    ts_stub),
    "go":      (".go",    go_stub),
    "rust":    (".rs",    rust_stub),
    "shell":   (".sh",    sh_stub),
}


# --- SKILL.md generation ----------------------------------------------------

def generate_frontmatter(name: str, description: str, domain: str, languages: list) -> str:
    verbs = extract_verbs(description)
    primary = verbs[0].capitalize() if verbs else "Process"

    lines = ["---", f"name: {slugify(name)}", "description: >"]
    lines.append(f"  {primary} using {', '.join(languages)}. Use when the user wants to:")
    for i, verb in enumerate(verbs[:4]):
        lines.append(f"    ({i+1}) {verb.capitalize()} [entity] (e.g., \"{verb} [example]\"),")
    far = verbs[0] if verbs else "process"
    lines.append(f"  Do NOT use for unrelated operations outside the {far} domain.")
    lines.append("---")
    return "\n".join(lines) + "\n"


def generate_skill_md(name: str, description: str, domain: str, languages: list) -> str:
    template = DOMAIN_TEMPLATES[domain]
    sections = template["section_order"]
    verbs = extract_verbs(description)
    primary = verbs[0] if verbs else "process"

    lines = [generate_frontmatter(name, description, domain, languages)]
    lines.append(f"# {name}\n")
    lines.append(f"{description}\n")

    # Language Matrix
    lines.append("## Language Support\n")
    lines.append("| Language | Script | Purpose |")
    lines.append("|----------|--------|---------|")
    for lang in languages:
        scripts = template["scripts"].get(lang, [])
        for fname, annot in scripts:
            clean_annot = annot.lstrip("#/ ")
            lines.append(f"| {lang.capitalize()} | `scripts/{fname}` | {clean_annot} |")
    lines.append("")

    for sec in sections:
        lines.append(f"## {sec}\n")
        if sec == "Quick Start":
            lines.append("```bash")
            for lang in languages[:3]:
                scripts = template["scripts"].get(lang, [])
                if scripts:
                    fname = scripts[0][0]
                    lines.append(f"# {lang.capitalize()}")
                    lines.append(f"# See scripts/{fname} for implementation")
            lines.append("```\n")
        elif sec == "Prerequisites":
            for lang in languages:
                if lang == "python":  lines.append("- Python 3.11+")
                elif lang == "node":  lines.append("- Node.js 20+ / Deno 2+")
                elif lang == "go":    lines.append("- Go 1.22+")
                elif lang == "rust":  lines.append("- Rust 1.75+")
                elif lang == "shell": lines.append("- Bash 4+ / PowerShell 5.1+")
            lines.append("")
        elif sec == "Core Operations":
            lines.append("| Operation | Input | Output | Description |")
            lines.append("|-----------|-------|--------|-------------|")
            for v in verbs[:5]:
                lines.append(f"| {v.capitalize()} | [type] | [type] | [what it does] |")
            lines.append("")
        elif sec == "Error Recovery":
            lines.append("| Error | Recovery | Retry |")
            lines.append("|-------|----------|-------|")
            lines.append("| Timeout / network | Exponential backoff (1s,2s,4s) | Yes |")
            lines.append("| Invalid input | Report format expected, ask user | No |")
            lines.append("| Auth / permission | Clean abort, instruct user | No |")
            lines.append("")
            lines.append("If recovery fails: report error with diagnostic, do not silently succeed.\n")
        elif sec == "Output Specification":
            lines.append("- **Format**: [Markdown / JSON / DOCX / PNG]")
            lines.append("- **Naming**: `{topic}-{YYYYMMDD}.{ext}`")
            lines.append("- **Location**: output directory")
            lines.append("- **Idempotency**: Overwrite on re-run (not append, not duplicate)\n")
        elif sec == "Security":
            lines.append("- [ ] Credentials from environment variables only (never committed)")
            lines.append("- [ ] HTTPS enforced for all external calls")
            lines.append("- [ ] User data never logged to disk (temp files cleaned)")
            lines.append("- [ ] Destructive operations gated with explicit confirmation\n")
        elif sec == "Batch Processing":
            lines.append("- List files matching pattern")
            lines.append('- Process sequentially with progress: "3/12 done"')
            lines.append("- Aggregate: succeeded / failed (with reasons) / skipped\n")
        elif sec == "Disclaimer":
            lines.append("> This skill provides automation, not professional advice. Review output before use.\n")
        else:
            lines.append("[Adapt to your specific use case]\n")

    return "\n".join(lines)


# --- Project config generation ----------------------------------------------

def generate_pyproject(skill_name: str) -> str:
    return f"""[build-system]
requires = ["setuptools>=68.0"]
build-backend = "setuptools.backends._legacy:_Backend"

[project]
name = "{slugify(skill_name)}"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = []

[project.optional-dependencies]
dev = ["pytest>=8.0", "ruff>=0.4", "mypy>=1.8"]

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
"""


def generate_package_json(skill_name: str) -> str:
    return json.dumps({
        "name": slugify(skill_name),
        "version": "0.1.0",
        "type": "module",
        "scripts": {
            "test": "vitest run",
            "lint": "deno lint scripts/",
            "fmt": "deno fmt scripts/"
        },
        "devDependencies": {
            "vitest": "^1.6.0",
            "zod": "^3.22.0"
        }
    }, indent=2) + "\n"


def generate_go_mod(skill_name: str) -> str:
    return f"module github.com/skills/{slugify(skill_name)}\n\ngo 1.22\n"


def generate_cargo_toml(skill_name: str) -> str:
    safe_name = slugify(skill_name).replace("-", "_")
    return f"""[package]
name = "{safe_name}"
version = "0.1.0"
edition = "2021"

[dependencies]
anyhow = "1"
serde = {{ version = "1", features = ["derive"] }}
serde_json = "1"

[dev-dependencies]
"""


# --- Tree printer (VS Code-style with inline annotations) --------------------

def print_tree(skill_dir: str) -> str:
    """Generate VS Code-style tree view with inline annotations."""
    lines = []
    root = Path(skill_dir)
    name = root.name
    lines.append(f"{name}/")

    def walk(directory: Path, prefix: str):
        entries = sorted(directory.iterdir(), key=lambda p: (p.is_file(), p.name))
        count = len(entries)
        for i, entry in enumerate(entries):
            is_last = i == count - 1
            connector = "`-- " if is_last else "|-- "
            child_prefix = prefix + ("    " if is_last else "|   ")

            if entry.is_dir():
                lines.append(f"{prefix}{connector}{entry.name}/")
                walk(entry, child_prefix)
            else:
                annotation = ""
                try:
                    with open(entry, "r", encoding="utf-8") as f:
                        first = f.readline().strip()
                    if first.startswith(('"""', '//', '#', '/*', '---', '/*')):
                        clean = first.replace('"""', '').replace('//', '').replace('#', '').replace('---', '').strip()
                        if clean and len(clean) < 60:
                            annotation = f"  {clean}"
                except Exception:
                    pass
                lines.append(f"{prefix}{connector}{entry.name}{annotation}")

    walk(root, "")
    return "\n".join(lines)


# --- Main generator ---------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Generate a multi-language FAANG-grade skill scaffold.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("name", help="Skill name (e.g., 'sensitive-word-checker')")
    parser.add_argument("description", help="Natural language description")
    parser.add_argument("--lang", "-l", default="all",
                        choices=["python","node","go","rust","shell","all"],
                        help="Target language(s). 'all' generates every supported language.")
    parser.add_argument("--output", "-o", default=".",
                        help="Output directory (default: current dir)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print tree only, don't create files")
    args = parser.parse_args()

    skill_name = slugify(args.name)
    domain = classify_domain(args.description)
    verbs = extract_verbs(args.description)

    if args.lang == "all":
        languages = ["python", "node", "go", "rust", "shell"]
    else:
        languages = [args.lang]

    skill_dir = Path(args.output) / skill_name

    if args.dry_run:
        print(f"Would generate {skill_dir}/ with languages: {languages}")
        print(f"Domain: {domain} | Verbs: {verbs}")
        return

    # Create directories
    (skill_dir / "scripts").mkdir(parents=True, exist_ok=True)
    (skill_dir / "references").mkdir(parents=True, exist_ok=True)
    (skill_dir / "tests").mkdir(exist_ok=True)

    template = DOMAIN_TEMPLATES[domain]

    # --- Generate SKILL.md ---
    skill_md = generate_skill_md(args.name, args.description, domain, languages)
    with open(skill_dir / "SKILL.md", "w", encoding="utf-8") as f:
        f.write(skill_md)

    # --- Generate language-specific scripts ---
    for lang in languages:
        ext, stub_fn = LANG_STUBS[lang]
        scripts = template["scripts"].get(lang, [])
        for fname, annotation in scripts:
            if not fname.endswith(ext):
                base = fname.rsplit(".", 1)[0]
                fname = f"{base}{ext}"
            content = stub_fn(fname, annotation, args.name)
            with open(skill_dir / "scripts" / fname, "w", encoding="utf-8") as f:
                f.write(content)

    # --- Generate references ---
    for ref_name, ref_annotation in template["references"]:
        if ref_name.endswith("/"):
            (skill_dir / "references" / ref_name).mkdir(exist_ok=True)
        else:
            clean_annot = ref_annotation.lstrip("# ")
            header = clean_annot if clean_annot else ref_name.replace(".md", "").replace("-", " ").title()
            content = f"# {header}\n\nReference for `{args.name}` - fill in from domain knowledge.\n"
            with open(skill_dir / "references" / ref_name, "w", encoding="utf-8") as f:
                f.write(content)

    # --- Generate project configs ---
    if "python" in languages:
        with open(skill_dir / "pyproject.toml", "w", encoding="utf-8") as f:
            f.write(generate_pyproject(args.name))
    if "node" in languages:
        with open(skill_dir / "package.json", "w", encoding="utf-8") as f:
            f.write(generate_package_json(args.name))
    if "go" in languages:
        with open(skill_dir / "go.mod", "w", encoding="utf-8") as f:
            f.write(generate_go_mod(args.name))
    if "rust" in languages:
        with open(skill_dir / "Cargo.toml", "w", encoding="utf-8") as f:
            f.write(generate_cargo_toml(args.name))

    # --- Generate .gitignore ---
    gitignore = """__pycache__/
*.pyc
*.pyo
node_modules/
target/
*.exe
*.dll
*.so
*.dylib
.env
*.log
"""
    with open(skill_dir / ".gitignore", "w", encoding="utf-8") as f:
        f.write(gitignore)

    # --- Print tree ---
    print(print_tree(str(skill_dir)))
    print(f"\nGenerated {skill_name}/")
    print(f"   Domain: {domain}")
    print(f"   Languages: {', '.join(languages)}")
    if verbs:
        print(f"   Verbs: {', '.join(verbs[:6])}")
    script_count = sum(len(template["scripts"].get(l, [])) for l in languages)
    ref_count = len(template["references"])
    print(f"   Files: SKILL.md + {script_count} scripts + {ref_count} references + configs")
    print(f"   Next: Fill [placeholder] sections, then validate & package.")


if __name__ == "__main__":
    main()
