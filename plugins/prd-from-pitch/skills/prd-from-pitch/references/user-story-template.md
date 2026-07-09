# User Story File Template

Use this template for each file under `user-stories/`.

```markdown
# US-{{N}}: {{STORY_TITLE}}

**Status:** Draft for Agentic Engineering Masterclass  
**Source PRD:** ../prd.md  
**Story ID:** US-{{N}}  
**Priority:** {{MUST_SHOULD_COULD}}  
**Depends on:** {{DEPENDENCIES_OR_NONE}}

## User Story

**As a** {{USER_OR_ROLE}}  
**I want** {{CAPABILITY}}  
**So that** {{BUSINESS_OR_USER_OUTCOME}}

## Context

{{SHORT_CONTEXT_FROM_PRD}}

## Acceptance Criteria

### AC-{{N}}.1: {{CRITERION_NAME}}

**Intent:** {{BUSINESS_BEHAVIOUR_OR_RULE}}

#### Pass Examples

```gherkin
Scenario: {{PASS_SCENARIO_NAME}}
Given {{BUSINESS_CONTEXT}}
When {{DOMAIN_ACTION}}
Then {{OBSERVABLE_OUTCOME}}
```

#### No-Pass Examples

```gherkin
Scenario: {{NO_PASS_SCENARIO_NAME}}
Given {{BUSINESS_CONTEXT}}
When {{DOMAIN_ACTION}}
Then {{EXPECTED_REJECTION_OR_NON_OUTCOME}}
```

#### Test Data

Include this section only when the acceptance test is data-driven.

| Case | Input | Context | Expected outcome | Pass or no-pass |
|---|---|---|---|---|
| 1 | {{INPUT}} | {{CONTEXT}} | {{EXPECTED_OUTCOME}} | Pass |
| 2 | {{INPUT}} | {{CONTEXT}} | {{EXPECTED_OUTCOME}} | No-pass |

#### Automation Note

{{DOMAIN_DSL_API_PLAYWRIGHT_ROBOT_FRAMEWORK_OR_EXPLORATORY_NOTE}}

## Open Questions

- {{QUESTION_OR_NONE}}
```

## File Naming

Use lowercase kebab case:

```text
user-stories/us-001-short-story-title.md
```
