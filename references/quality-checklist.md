# Business Skill Quality Checklist

Use this checklist before packaging any skill. All items must pass for a "business-grade" label.

## Pre-Packaging Audit

### Metadata Quality
- [ ] `name` uses kebab-case and is descriptive and unique
- [ ] `description` includes capability summary AND concrete trigger phrases/conditions
- [ ] `description` clarifies what the skill does NOT handle (boundary)
- [ ] `description` is under 150 words

### Structural Integrity
- [ ] SKILL.md exists with valid YAML frontmatter
- [ ] No extra documentation files (README, CHANGELOG, etc.)
- [ ] All referenced files in SKILL.md actually exist
- [ ] No broken internal links or paths
- [ ] scripts/ files are tested and executable
- [ ] assets/ files are correctly referenced

### Content Quality
- [ ] SKILL.md body is under 500 lines
- [ ] Every instruction uses imperative/infinitive form
- [ ] Concrete examples present for non-trivial operations
- [ ] Error handling guidance included for each tool/script call
- [ ] Edge cases explicitly addressed (empty input, large input, special chars)
- [ ] No hardcoded credentials or secrets
- [ ] Rollback/recovery instructions for state-changing operations

### Trigger Effectiveness
- [ ] 5+ diverse user queries tested: all that should trigger DO trigger
- [ ] 5+ diverse user queries tested: none that should NOT trigger accidentally trigger
- [ ] Multi-language trigger phrases included if applicable
- [ ] Synonyms and common variations covered

### Output Standards
- [ ] Output format explicitly specified (structure, naming, types)
- [ ] Progress reporting included for operations >3 seconds
- [ ] Idempotency considered: running twice shouldn't double side-effects

### Progressive Disclosure
- [ ] SKILL.md is lean: detailed reference material in references/ files
- [ ] References are one level deep from SKILL.md (no nested references)
- [ ] Files >100 lines have a table of contents at the top
- [ ] Clear in SKILL.md when to load each reference file

## Post-Deployment Validation

After the skill is used in production:

- [ ] Monitor for false-positive triggers: skill firing when it shouldn't
- [ ] Monitor for false-negative triggers: skill NOT firing when it should
- [ ] Collect edge cases discovered in real usage and update skill
- [ ] Time-to-completion: is the skill efficient or does it need optimization?
*（内容由AI生成，仅供参考）*
