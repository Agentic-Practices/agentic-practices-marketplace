---
name: claude-md-auditor
description: Use when auditing, reviewing, cleaning up, restructuring, or scoring CLAUDE.md files, Claude Code project instructions, hierarchical context, scoped rules, linked references, Skills, hooks, or project memory.
---

# CLAUDE.md Auditor

## Overview

Audit the whole context setup, not one file in isolation. Treat context as a limited resource: keep automatically loaded instructions small, current, broadly relevant, and placed at the narrowest useful scope.

Remain read-only through the audit. Offer changes only after reporting, and apply only the finding IDs the user explicitly approves.

## Audit workflow

1. Establish the project root and requested scope.
2. Discover root and nested `CLAUDE.md` files, `.claude/rules/`, linked references, relevant Skills, hooks, and documented memory or user-level context. Do not inspect personal files outside the requested scope without permission.
3. Read the discovered files and relevant project manifests. Resolve inheritance, duplication, contradictions, broken links, and ambiguous relative paths.
4. Check whether recorded commands match the repository's current configuration. Distinguish configuration-confirmed commands from commands actually executed; never claim execution without evidence.
5. Apply every category in [references/audit-rubric.md](references/audit-rubric.md).
6. Assign each finding one disposition:
   - **Keep**
   - **Update and verify**
   - **Move or nest**
   - **Extract to Skill**
   - **Extract to reference**
   - **Move to current prompt or task artifact**
   - **Enforce deterministically**
   - **Delete**
7. Produce the report using [references/report-template.md](references/report-template.md). Cite the exact file and line when available.
8. Ask whether the user wants to apply recommendations. If yes, ask which finding ID to address first. Apply that approved change, show the result, then ask about the next finding.

## Placement test

For each instruction ask, in order:

1. **Broadly:** Is it relevant to almost every task in this scope?
2. **Repeatedly:** Is it a reusable procedure rather than knowledge?
3. **Durably:** Will it remain true and useful?
4. **Narrowly:** Can it load closer to the directory, file pattern, or task that needs it?
5. **Deterministically:** Must compliance be guaranteed rather than requested?

Use the answers to choose the destination:

| Need | Destination |
|---|---|
| Always-relevant project ground rule | Root `CLAUDE.md` |
| Directory-specific convention | Nested `CLAUDE.md` |
| File-pattern-specific instruction | Scoped rule |
| Repeatable procedure | Skill |
| Detailed reusable knowledge | Reference document |
| Temporary outcome, evidence, or story detail | Current prompt or task artifact |
| Personal preference | User-level context or memory |
| Exact safety or quality control | Hook, test, linter, script, or permission boundary |
| Obvious, duplicated, expired, or useless content | Nowhere; delete it |

## Audit discipline

- Score only observed evidence. Mark an area **not assessed** rather than inventing context.
- Do not reward length, exhaustive directory listings, generic advice, or duplicated references.
- Do not invent architecture, commands, conventions, or a definition of done. Recommend that the team supply or approve missing facts.
- Treat stale or incorrect instructions as higher risk than missing instructions because they actively misdirect work.
- Treat “never do this” as insufficient when a deterministic guard can prevent the action.
- Preserve concise summaries that give a useful global rule while linking deeper material on demand.
- Challenge rules that demand agreement, suppress questions, or encourage unsupported completion claims.
- Separate findings from proposed rewrites. The audit must remain useful even if the user applies nothing.

## Common mistakes

| Mistake | Correction |
|---|---|
| Reviewing only the root file | Resolve the complete inherited context stack |
| Rewriting before reporting | Finish the read-only audit first |
| Treating every detail as permanent context | Apply the placement test |
| Calling a command “verified” because it appears in prose | Check project configuration or execute it |
| Keeping safety rules only as reminders | Recommend deterministic enforcement |
| Copying entire reference documents into `CLAUDE.md` | Keep a concise rule and link the source |
| Giving vague advice without locations | Cite file, line, evidence, and disposition |
| Applying all recommendations after general approval | Request explicit finding IDs, one decision at a time |
