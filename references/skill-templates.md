# Skill Templates by Domain

Ready-to-adapt templates for common skill categories. Each template embeds FAANG-grade patterns.

## Table of Contents

- [API Integration Skill](#api-integration-skill)
- [File Processing Skill](#file-processing-skill)
- [Data Analysis Skill](#data-analysis-skill)
- [UI Automation Skill](#ui-automation-skill)
- [Domain Expert Skill](#domain-expert-skill)
- [Workflow Orchestrator Skill](#workflow-orchestrator-skill)

---

## API Integration Skill

For skills that wrap external APIs (REST, GraphQL, SDK).

### Description Template

```yaml
description: >
  [Service name] integration for [use case]. Use when the user wants to:
  (1) [Action verb] [entity] via [service] (e.g., "send an email via SendGrid"),
  (2) Query or retrieve [entity] from [service],
  (3) Manage [resource] in [service].
  Handles authentication automatically via environment variables.
  Do NOT use for manual [service] web dashboard operations.
```

### SKILL.md Skeleton

```markdown
# [Service] Integration

[One sentence: what this skill does and why it exists.]

## Quick Start

[1 example: simplest possible user request → agent response flow.]

## Prerequisites

- Environment variable: `[SERVICE]_API_KEY` (get from [link])
- [Any account requirements]

## Core Operations

### Operation 1: [Name]

[When to use. Example request.]

```
[Tool call or script invocation pattern]
```

**Error handling**: [Tiered response per faang-patterns.md §1]

### Operation 2: [Name]

...

## API Reference

- **Base URL**: `[url]`
- **Auth**: [method]
- **Rate limit**: [limit] (handled automatically)
- **Pagination**: [method] (handled automatically)

See [references/api-details.md] for full endpoint documentation.

## Output Specification

[Per faang-patterns.md §4]

## Security

[Per faang-patterns.md §7]
```

---

## File Processing Skill

For skills that manipulate files (PDF, DOCX, images, audio, video).

### Description Template

```yaml
description: >
  [Format] file processing: [capabilities]. Use when the user wants to:
  (1) [Action] [format] files (e.g., "merge PDFs", "convert images to WebP"),
  (2) Extract [data type] from [format],
  (3) Batch-process [format] files in a directory.
  Supports input from local paths and URLs.
  Do NOT use for creating [format] files from scratch (use [other skill]).
```

### SKILL.md Skeleton

```markdown
# [Format] Processor

[Purpose statement.]

## Quick Start

[Example: "merge these 3 PDFs" → agent response.]

## Supported Operations

| Operation | Input | Output | Example |
|-----------|-------|--------|---------|
| [op1] | [type] | [type] | "[user phrase]" |
| [op2] | [type] | [type] | "[user phrase]" |

## Core Workflow

1. Validate input files exist and are correct format
2. Execute operation using [tool/script]
3. Verify output integrity (file size > 0, format check)
4. Report result with output path

## Batch Processing

For directory operations:
- List files matching pattern
- Process sequentially with progress: "3/12 done"
- Report summary: succeeded / failed / skipped with reasons

## Error Recovery

- **Corrupt file**: Skip with warning, continue batch
- **Unsupported format**: Suggest conversion or alternative
- **Disk full**: Abort, report remaining space needed
- **Permission denied**: Report path, suggest workaround

## Output Specification

- Output files go to same directory as input (or user-specified)
- Naming: `{original_name}-{operation}.{ext}`
- Never overwrite without confirmation
```

---

## Data Analysis Skill

For skills that analyze, visualize, or transform data.

### Description Template

```yaml
description: >
  Data analysis and visualization for [domain]. Use when the user wants to:
  (1) Analyze [data source] to find [insight type],
  (2) Create charts or visualizations from [data],
  (3) Transform or clean [data format] for [purpose].
  Supports CSV, Excel, JSON, and database connections.
  Do NOT use for real-time streaming data or ML model training.
```

### SKILL.md Skeleton

```markdown
# [Domain] Data Analyzer

[Purpose.]

## Quick Start

[Example request → response with chart/table.]

## Analysis Workflow

1. **Load** — Read data, detect schema, report shape (rows × cols)
2. **Clean** — Handle nulls, outliers, type mismatches
3. **Analyze** — Apply domain-specific logic
4. **Visualize** — Generate charts (save as PNG)
5. **Report** — Produce structured Markdown + charts

## Output Specification

- Report: `[topic]-analysis-[YYYYMMDD].md`
- Charts: `[topic]-[chart-type]-[YYYYMMDD].png`
- All files in output directory

## Edge Cases

- **Empty dataset**: Report "no data" with reason, do not error
- **Single row**: Still produce analysis, note limited sample
- **Encoding issues**: Auto-detect (try UTF-8 → GBK → Latin-1)
- **Large datasets (>100k rows)**: Sample for visualization, full stats on aggregate
```

---

## UI Automation Skill

For skills that automate app/browser interactions.

### Description Template

```yaml
description: >
  [App/Platform] automation for [use case]. Use when the user wants to:
  (1) Automate [workflow] in [app] (e.g., "post to Xiaohongshu"),
  (2) Extract data from [app] UI,
  (3) Perform repetitive [app] operations in bulk.
  Requires [app] to be installed and logged in.
  Do NOT use for [app] settings configuration or account management.
```

### SKILL.md Skeleton

```markdown
# [App] Automator

[Purpose.]

## Prerequisites

- [App] installed (version X.X+)
- User logged in with [account type]
- [Any permissions needed]

## Core Workflow

1. **Launch** — Open app, verify login state
2. **Navigate** — Reach target screen
3. **Execute** — Perform operation
4. **Verify** — Screenshot confirmation
5. **Report** — Success/failure with evidence

## Wait Strategy

- After navigation: wait for [specific element] to appear (max 10s)
- After action: wait for [confirmation element] (max 5s)
- Timeout fallback: screenshot current state and report

## Error Recovery

- **App not installed**: Guide user to install
- **Not logged in**: Prompt user to log in, wait, retry
- **UI changed**: Screenshot, report unexpected state, abort
- **Network error in app**: Wait 5s, retry once, then abort

## Output Specification

- Confirmation: screenshot saved as `[task]-[timestamp].png`
- Data extraction: structured data saved as `[task]-data.[json/csv]`
```

---

## Domain Expert Skill

For skills that provide specialized knowledge (legal, medical, financial).

### Description Template

```yaml
description: >
  [Domain] expert assistant for [tasks]. Use when the user wants to:
  (1) Draft [document type] in [domain] (e.g., "draft an NDA"),
  (2) Review [document type] for [criteria],
  (3) Search [domain] regulations or standards,
  (4) Compare [domain] options or scenarios.
  Knowledge covers [jurisdiction/scope].
  Do NOT use for providing [domain] advice that requires licensed professional judgment.
```

### SKILL.md Skeleton

```markdown
# [Domain] Expert

[Purpose + disclaimer boundary.]

## Quick Start

[Example: "draft a simple NDA" → output.]

## Document Operations

### Drafting

1. Collect requirements (parties, jurisdiction, key terms)
2. Load template from [references/templates/]
3. Fill template with provided details
4. Output as .docx with tracked changes enabled

### Review

1. Load document
2. Check against [checklist] in [references/checklist.md]
3. Flag issues by severity: Critical / Warning / Info
4. Output structured review report

## Knowledge Boundaries

- **In scope**: [list]
- **Out of scope**: [list — be explicit]
- **Escalation**: For [out-of-scope items], advise user to consult [professional type]

## Output Specification

- Drafts: .docx with filename `{doc-type}-{parties}-{date}.docx`
- Reviews: .md with filename `{doc-name}-review-{date}.md`

## Disclaimer

This skill provides document automation and knowledge retrieval, not legal/medical/financial advice. Output should be reviewed by a qualified professional before use.
```

---

## Workflow Orchestrator Skill

For skills that coordinate multiple sub-skills or multi-step processes.

### Description Template

```yaml
description: >
  Multi-step workflow orchestrator for [domain]. Use when the user wants to:
  (1) Execute end-to-end [process name] (e.g., "onboard a new employee"),
  (2) Run [pipeline] across multiple systems,
  (3) Coordinate [N] dependent tasks into a single flow.
  Each step has independent rollback.
  Do NOT use for single-step tasks that a dedicated skill handles better.
```

### SKILL.md Skeleton

```markdown
# [Workflow] Orchestrator

[Purpose: what end-to-end process this automates.]

## Prerequisites

- [System A] access with [permission]
- [System B] access with [permission]
- [Any data needed upfront]

## Workflow Steps

### Step 1: [Name] — [System]
[What happens. Expected output. Rollback action.]

### Step 2: [Name] — [System]
...

### Step N: Verification
[How to confirm all steps succeeded.]

## Checkpoint Strategy

- After each step: save checkpoint to `[workflow]-checkpoint.json`
- On resume: read checkpoint, skip completed steps
- On failure: report completed + failed step, offer retry from failure point

## Rollback

Each step documents its inverse:
- **Step 1 rollback**: [how to undo]
- **Step 2 rollback**: [how to undo]

## Output Specification

- Summary: `[workflow]-summary-[date].md` listing each step and status
- Artifacts: each step's output in `[workflow]-outputs/`
```
