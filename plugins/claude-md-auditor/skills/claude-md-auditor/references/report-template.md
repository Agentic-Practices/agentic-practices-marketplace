# Audit Report Template

Use this order. Omit no section; write “Not assessed” with the reason where evidence is unavailable.

## CLAUDE.md setup audit

### Verdict

- **Score:** `[0–100]`
- **Rating:** `[Strong | Sound | Fragile | Weak | Unsafe]`
- **Highest risk:** `[one sentence]`
- **Scope inspected:** `[paths and context surfaces]`
- **Evidence limits:** `[anything unavailable or not executed]`

### Scorecard

| Category | Score | Maximum | Main reason |
|---|---:|---:|---|
| Essential ground rules |  | 20 |  |
| Signal and relevance |  | 15 |  |
| Scope and placement |  | 20 |  |
| Currency and empirical truth |  | 15 |  |
| Hierarchy and composition |  | 10 |  |
| Deterministic enforcement and safety |  | 10 |  |
| Maintainability and knowledge lifecycle |  | 10 |  |
| **Total** |  | **100** |  |

### Context map

| Surface | Path or scope | Purpose | Status |
|---|---|---|---|
| Root context |  |  |  |
| Nested context |  |  |  |
| Scoped rules |  |  |  |
| Skills |  |  |  |
| References |  |  |  |
| Deterministic controls |  |  |  |
| User or memory context |  |  |  |

### Findings

Order findings by severity, then leverage.

#### CTX-01 — `[short title]`

- **Severity:** 
- **Category:** 
- **Location:** `path:line`
- **Evidence:** 
- **Consequence:** 
- **Disposition:** `[Keep | Update and verify | Move or nest | Extract to Skill | Extract to reference | Move to current prompt or task artifact | Enforce deterministically | Delete]`
- **Recommendation:** 
- **Verification needed:** 

Repeat for each finding.

### Recommended target structure

Show the smallest useful context architecture, not a full rewrite:

```text
CLAUDE.md
.claude/rules/
subsystem/CLAUDE.md
skills/
docs/
hooks or deterministic checks
task artifacts
```

Include only surfaces justified by findings.

### What is already working

List concise, evidence-backed strengths worth preserving.

### Prioritised change set

| Order | Finding ID | Change | Why now |
|---:|---|---|---|
| 1 |  |  |  |

### Approval gate

End with one question:

> Would you like me to apply any recommendations? If yes, which finding ID should we address first?

Never apply edits before this answer.
