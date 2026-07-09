# PRD From Pitch Template and Scoring Rubric

Use this template when `prd-from-pitch` writes `prd.md`.

## PRD Template

```markdown
# {{PROJECT_NAME}} PRD

**Status:** Draft for Agentic Engineering Masterclass  
**Source pitch:** {{SOURCE_OVERVIEW_PATH}}  
**Team:** {{TEAM_NAME}}  
**Run type:** {{INITIAL_PRODUCT_SETUP_OR_FOLLOW_UP_FEATURE}}  
**Created:** {{DATE}}  
**Readiness score:** {{SCORE}} / 100

## Generated Files

- PRD: `prd.md`
- User stories: `user-stories/`

## 1. Product Overview

{{ONE_PARAGRAPH_OVERVIEW}}

## 2. Problem and Opportunity

**Pain:** {{PAIN}}

**Affected users or teams:** {{AFFECTED_USERS}}

**Cost or consequence today:** {{CURRENT_COST}}

**Opportunity:** {{OPPORTUNITY}}

## 3. Users and Stakeholders

| Role | Need | Decision or support required |
|---|---|---|
| {{ROLE}} | {{NEED}} | {{DECISION_OR_SUPPORT}} |

## 4. Goals and Non-Goals

### Goals

- {{GOAL_1}}
- {{GOAL_2}}
- {{GOAL_3}}

### Non-Goals

- {{NON_GOAL_1}}
- {{NON_GOAL_2}}

## 5. Scope and Demo Slice

**Hackathon or first demo slice:** {{DEMO_SLICE}}

**In scope:**

- {{IN_SCOPE_1}}
- {{IN_SCOPE_2}}

**Out of scope:**

- {{OUT_OF_SCOPE_1}}
- {{OUT_OF_SCOPE_2}}

## 6. Base Tech Stack

Include this section only for initial product setup, or when a follow-up feature requires a new stack decision.

| Layer | Proposed choice | Confidence | Notes |
|---|---|---|---|
| Frontend | {{FRONTEND}} | {{CONFIDENCE}} | {{NOTES}} |
| Backend | {{BACKEND}} | {{CONFIDENCE}} | {{NOTES}} |
| Data store | {{DATA_STORE}} | {{CONFIDENCE}} | {{NOTES}} |
| Authentication / identity | {{AUTH}} | {{CONFIDENCE}} | {{NOTES}} |
| External integrations | {{INTEGRATIONS}} | {{CONFIDENCE}} | {{NOTES}} |
| Test tooling | {{TEST_TOOLING}} | {{CONFIDENCE}} | {{NOTES}} |
| Hosting / deployment | {{HOSTING}} | {{CONFIDENCE}} | {{NOTES}} |
| Observability / logging | {{OBSERVABILITY}} | {{CONFIDENCE}} | {{NOTES}} |

## 7. Existing Technical Context

Include this section for follow-up features.

- Existing product or service: {{EXISTING_PRODUCT_OR_SERVICE}}
- Existing stack or platform: {{EXISTING_STACK_OR_PLATFORM}}
- Integration points touched: {{INTEGRATION_POINTS}}
- Compatibility or migration concerns: {{COMPATIBILITY_OR_MIGRATION_CONCERNS}}

## 8. Technical Constraints

- {{CONSTRAINT_1}}
- {{CONSTRAINT_2}}
- {{CONSTRAINT_3}}

## 9. Functional Requirements

| ID | Requirement | Priority | Source |
|---|---|---|---|
| FR-001 | {{REQUIREMENT}} | Must | {{SOURCE}} |

## 10. Non-Functional Requirements

| ID | Requirement | Priority | Notes |
|---|---|---|---|
| NFR-001 | {{REQUIREMENT}} | Must | {{NOTES}} |

## 11. UX and Workflow Notes

- {{UX_NOTE_1}}
- {{UX_NOTE_2}}

## 12. Priority User Story Files

| Story | File | User outcome | Acceptance readiness |
|---|---|---|---|
| US-001: {{STORY_TITLE}} | `user-stories/us-001-{{SLUG}}.md` | {{USER_OUTCOME}} | {{READY_PARTIAL_BLOCKED}} |

## 13. Remaining Story Backlog

Use this section when only the top 2-3 story files were generated.

| Candidate story | Why it matters | Generate file now? |
|---|---|---|
| {{STORY_TITLE}} | {{RATIONALE}} | Later |

## 14. Assumptions

- {{ASSUMPTION_1}}
- {{ASSUMPTION_2}}

## 15. Risks and Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| {{RISK}} | {{IMPACT}} | {{MITIGATION}} |

## 16. Evidence Gaps

- {{EVIDENCE_GAP_1}}
- {{EVIDENCE_GAP_2}}

## 17. Open Questions

- {{QUESTION_1}}
- {{QUESTION_2}}

## 18. Session 1 Readiness

**Use as Session 1 shared training object:** {{YES_NO}}

**Top gaps to resolve during training:**

1. {{GAP_1}}
2. {{GAP_2}}
3. {{GAP_3}}
```

## Scoring Rubric

| Category | Points | Strong evidence |
|---|---:|---|
| Business value | 20 | Clear pain, named affected users, concrete consequence, plausible value. |
| User and stakeholder clarity | 15 | Primary users, sponsors, approvers, and support roles are named or strongly inferred. |
| Functional requirements | 20 | Requirements are observable, scoped, prioritised, and tied to pitch commitments. |
| UX and workflow clarity | 10 | Main workflow, user touchpoints, and obvious error or empty states are visible. |
| Technical constraints and fit | 15 | For initial setup, stack layers and constraints are named or explicitly provisional. For follow-up features, existing technical context, integration needs, compatibility, data, security, deployment, and test tooling are clear. |
| Testability and acceptance readiness | 15 | Top priority stories have their own files with Dave Farley-style acceptance criteria, pass/no-pass examples, and data tables for data-driven tests. |
| Evidence and risk clarity | 5 | Evidence, assumptions, risks, and open questions are separated. |

## Score Interpretation

- **90-100:** Strong PRD. Ready for Session 1 and likely ready for Session 2 refinement.
- **80-89:** Useful PRD. Ready for Session 1 with visible gaps.
- **65-79:** Coaching PRD. Usable as a training object, but Session 1 should resolve major gaps.
- **Below 65:** Weak PRD. Use only if the learning goal is to repair an under-specified idea.
