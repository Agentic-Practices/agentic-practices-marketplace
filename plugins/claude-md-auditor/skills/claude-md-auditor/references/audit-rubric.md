# CLAUDE.md Audit Rubric

Score seven categories for a total of 100. Award points only for observed evidence in the requested scope. Explain every deduction; do not infer missing facts.

## 1. Essential ground rules — 20 points

Assess whether the automatically loaded project context contains or links to:

- concise project purpose and important domain context — 4
- relevant architecture or system boundaries — 4
- current build, test, lint, type-check, and run commands — 4
- critical local conventions rather than generic advice — 3
- an agreed definition of done and required evidence — 3
- permission to flag contradictions, missing evidence, ambiguity, and unsafe instructions — 2

A link to a current authoritative source can earn credit when a summary is not needed on every task.

## 2. Signal and relevance — 15 points

- automatically loaded instructions are relevant to almost every task in their scope — 5
- no exhaustive directory listings, generic model knowledge, slogans, or impossible demands — 4
- task-specific and temporary details are absent from durable context — 3
- the setup is concise enough that critical rules remain prominent — 3

Do not score by word count alone. A short file can be incomplete; a longer file can be justified.

## 3. Scope and placement — 20 points

- global rules live at root; subsystem rules live in nested context — 5
- file-pattern rules use scoped conditions where supported — 4
- repeatable procedures are Skills rather than long prose checklists — 4
- detailed knowledge lives in focused references loaded on demand — 3
- personal preferences stay out of shared project policy — 2
- temporary requirements live in prompts, stories, or plans — 2

## 4. Currency and empirical truth — 15 points

- commands agree with current manifests or tool configuration — 5
- links and relative paths resolve from the context in which they are used — 3
- instructions do not contradict current code, configuration, or each other — 3
- volatile facts have an owner, source, condition, or review mechanism — 2
- claims of verification distinguish configuration inspection from execution evidence — 2

An incorrect instruction is more serious than an omitted one.

## 5. Hierarchy and composition — 10 points

- inherited instructions are not needlessly duplicated — 3
- root, nested, scoped, Skill, and reference layers form a coherent whole — 3
- precedence and boundaries are understandable — 2
- broken, orphaned, circular, or ambiguous references are absent — 2

## 6. Deterministic enforcement and safety — 10 points

- exact checks use tests, linters, schemas, scripts, or hooks where practical — 4
- destructive or production-sensitive actions use permissions or blocking controls — 3
- secrets, sensitive data, and irreversible actions have explicit boundaries — 2
- prose guidance does not claim to guarantee deterministic compliance — 1

Defense in depth may justify keeping a short reminder alongside an enforced control.

## 7. Maintainability and knowledge lifecycle — 10 points

- durable findings have a defined authoritative home — 3
- obsolete and duplicated guidance is removed rather than accumulated — 2
- the setup supports knowledge checkpoints and handovers where needed — 2
- detailed standards have owners or discoverable sources — 2
- the context can be tested on a fresh representative task — 1

## Rating bands

| Score | Rating | Meaning |
|---|---|---|
| 90–100 | Strong | Focused, current, composed, and evidence-aware |
| 75–89 | Sound | Useful setup with limited material weaknesses |
| 60–74 | Fragile | Helps in places but contains important gaps or noise |
| 40–59 | Weak | Frequently incomplete, misplaced, stale, or unenforced |
| 0–39 | Unsafe | Likely to misdirect work or obscure critical controls |

## Severity

| Severity | Use when |
|---|---|
| Critical | Instruction enables dangerous action, exposes sensitive data, or directs materially incorrect production behaviour |
| High | Stale, contradictory, broken, or mis-scoped guidance is likely to cause incorrect work |
| Medium | Missing or noisy context regularly reduces quality, focus, or maintainability |
| Low | Local improvement with limited immediate consequence |

## Finding quality

Each finding must include:

- stable ID such as `CTX-01`
- severity
- category
- exact location
- observed evidence
- consequence
- one disposition
- concrete recommendation
- verification needed

Do not combine unrelated problems into one finding merely to shorten the report.
