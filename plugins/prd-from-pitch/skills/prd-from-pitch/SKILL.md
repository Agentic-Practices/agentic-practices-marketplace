---
name: prd-from-pitch
description: "Turn a hackathon project pitch overview or feature idea into a scored Product Requirements Document and story-file set for the Agentic Engineering Masterclass. Use when a team has an `overview.md` from the `hackathon-project-pitch` skill, similar pitch notes, or a follow-up feature idea and needs outputs such as `prd.md`, priority user story files, Dave Farley-style acceptance criteria, pass/no-pass example scenarios, data tables for data-driven acceptance tests, technical constraints, risks, and readiness score. For initial product setup, also define and score the base tech stack."
---

# PRD From Pitch

Use this skill to transform a sponsor-pitch artifact or follow-up feature idea into a practical PRD that a cross-functional team can refine during the masterclass.

Base the workflow on the Product Requirements skill pattern: act as a product owner, read project context, ask targeted questions, score requirement quality out of 100, and generate a structured PRD only after taking the team through the full discovery experience.

This is a teaching skill as much as a production skill. Do the full discovery process, but keep the artifact expectation humane: the required output is a strong PRD plus the top priority story files. Remaining stories can stay as a prioritised backlog unless the user asks to generate every story file.

## Inputs

Prefer these inputs, in order:

1. `overview.md` produced by `hackathon-project-pitch`.
2. A follow-up feature brief, issue, support theme, user request, or change proposal.
3. `qanda.md`, `presentation.md`, or sponsor notes if present.
4. Client criteria files such as `project-selection-criteria.md`, `client-criteria.md`, or `hackathon-criteria.md`.
5. Relevant repository context such as `README.md`, architecture notes, package files, or existing standards.

If the user does not provide a path, search the current directory for `overview.md` and likely team-output folders before asking.

## Output

Write outputs beside the source `overview.md`, feature brief, or chosen working directory unless the user gives another destination:

```text
prd.md
user-stories/
  us-001-<slug>.md
  us-002-<slug>.md
  ...
```

For pre-Session-1 work, create at least the top 2-3 user story files. If the scope is small, or the user asks for the complete set, create all story files. Otherwise, capture lower-priority stories in the PRD backlog section.

Use:

- `references/prd-template.md` for the PRD template and scoring rubric.
- `references/user-story-template.md` for per-story files.
- `references/acceptance-criteria-standards.md` before writing acceptance criteria.
- `references/tech-stack-setup.md` only when the run is for initial product setup.

The PRD must include:

- product overview
- problem and opportunity
- users and stakeholders
- goals and non-goals
- scope and demo slice
- technical constraints
- functional requirements
- non-functional requirements
- UX and workflow notes
- user stories
- assumptions
- risks and mitigations
- evidence gaps
- open questions
- readiness score

For initial product setup, the PRD must also include a base tech stack. For a follow-up feature, do not create or score a full base tech stack unless the feature requires a new stack decision; instead document existing technical context and feature-specific constraints.

Each user story file must include:

- user story
- story context and dependencies
- acceptance criteria
- pass example scenarios
- no-pass example scenarios
- data tables when the acceptance test is data-driven
- notes on likely automation level such as domain DSL, API, Playwright, Robot Framework, or manual exploratory support

## Workflow

### 1. Locate and Read Context

Read the pitch overview or feature brief first. Then read adjacent files that can materially improve the PRD, especially `qanda.md`, `presentation.md`, criteria files, issue notes, support evidence, and local project `README.md` files.

Do not invent client strategy, data access, or technical architecture. Mark missing facts as assumptions, evidence gaps, or open questions.

### 2. Classify the Run

Determine whether the run is for:

- **Initial product setup:** a new product, prototype, hackathon product, or first coherent product slice that needs baseline stack decisions.
- **Follow-up feature:** an addition or change to an existing product where the stack already exists.

If the classification is not obvious, ask:

> Is this PRD for the initial product setup or for a follow-up feature in an existing product? Recommended answer: initial product setup if this comes directly from the hackathon pitch overview; follow-up feature if a product and stack already exist.

For initial product setup, read `references/tech-stack-setup.md` before scoring or writing the technical section. For follow-up features, do not read that reference unless a new stack decision is genuinely in scope.

### 3. Extract Pitch or Feature Commitments

Capture the team's committed answers:

- team name
- idea
- pain
- approval path
- hackathon slice
- client or organisation fit
- evidence
- chosen implementation approach
- risks and open questions

For follow-up features, also capture:

- existing product or workflow touched
- current users affected
- current behaviour
- desired behaviour
- compatibility or migration concerns

Preserve the pitch or feature intent. The PRD is a refinement, not a replacement idea.

### 4. Assess Requirement Quality

Score the draft context out of 100:

- business value: 20 points
- user and stakeholder clarity: 15 points
- functional requirements: 20 points
- UX and workflow clarity: 10 points
- technical constraints and fit: 15 points
- testability and acceptance readiness: 15 points
- evidence and risk clarity: 5 points

For initial product setup, score the base tech stack inside the 15-point technical constraints category. For follow-up features, score feature-specific technical fit against the existing stack instead.

Target score: 85+ for a useful pre-Session-1 PRD. A score below 85 can proceed after the full workflow has been completed and the remaining gaps are explicit.

### 5. Ask Targeted Questions

Ask questions that materially improve the PRD score. Ask one question at a time. Continue through the full discovery path rather than stopping at the first acceptable draft.

Prioritise gaps in this order:

1. user or problem ambiguity
2. scope too broad for a demo slice
3. missing technical constraints or fit
4. missing acceptance evidence
5. hidden approval, data, security, compliance, or operational risk

For each question, provide a recommended answer when there is enough context to do so.

Stop asking when either:

- every required PRD section has enough substance to draft responsibly, and
- each user story has testable acceptance criteria with pass/no-pass examples, and
- initial setup stack or follow-up technical fit is clear or explicitly provisional, and
- the remaining gaps are better exposed in the PRD than resolved before Session 1.

### 6. Define Technical Context

For initial product setup, define a base tech stack. Read `references/tech-stack-setup.md`, then document the proposed stack and count it in the technical constraints score.

For follow-up features, document existing technical context and feature-specific constraints. Do not force a complete stack section unless the feature changes the stack.

If an initial setup stack is known, document:

- frontend
- backend
- data store
- authentication or identity
- external integrations
- test tooling
- hosting or deployment target
- observability or logging

If an initial setup stack is not known, propose a conservative baseline from available context and label it as provisional.

### 7. Create User Story Files

Break the product slice into small, independently understandable user stories. Write each story to its own file under `user-stories/`.

For pre-Session-1 work, create the top 2-3 user story files unless the scope is small enough that writing all story files is clearly reasonable. Capture remaining stories in the PRD backlog.

For each story, follow `references/user-story-template.md`.

Acceptance criteria are mandatory. Before writing them, read `references/acceptance-criteria-standards.md` and apply the Dave Farley-style rules:

- Write from the perspective of an external user or stakeholder.
- Describe business-facing behaviour, not implementation detail.
- Use life-like examples.
- Prefer domain language over UI mechanics.
- Keep scenarios atomic and independent.
- Use public system interfaces in the eventual automated test design.
- Make each acceptance criterion refutable.
- Add pass and no-pass scenarios.
- Add data tables for data-driven acceptance tests.

If a scenario would otherwise say "click this button" or "fill this field", rewrite it in domain terms unless the UI action itself is the behaviour under test.

### 8. Generate the PRD

Write `prd.md` using `references/prd-template.md`.

Keep it concise enough for a team to use in Session 1. Prefer clear bullets, tables, links to story files, a visible backlog, and explicit unknowns over long prose.

### 9. Self-Review

Before reporting done, re-read the PRD and every user story file. Check:

- no unresolved template placeholders remain
- pitch commitments are preserved
- initial product setup includes a base tech stack, or follow-up feature documents existing technical context
- technical constraints are distinct from implementation tasks
- every user story connects to goals
- the top 2-3 priority stories live in their own Markdown files, with remaining stories captured in the PRD backlog unless all story files were requested
- acceptance criteria meet the standards in `references/acceptance-criteria-standards.md`
- every story has pass and no-pass example scenarios
- data-driven acceptance tests include data tables
- risks and evidence gaps are visible
- readiness score matches the content

Fix issues inline.

## Done Report

Report:

- path to `prd.md`
- path to `user-stories/`
- readiness score
- top three gaps to resolve in Session 1 or Session 2
- whether the PRD is ready to use as the Session 1 shared training object
