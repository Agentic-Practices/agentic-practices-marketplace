# Acceptance Criteria Standards

Use these standards when `prd-from-pitch` writes acceptance criteria and acceptance examples.

The standard is based on Dave Farley's acceptance test-driven development guidance from Continuous Delivery: acceptance tests are business-facing, support programming, are written before code, and act as executable specifications for the work.

## Core Rules

1. Write from the perspective of an external user, stakeholder, or consuming system.
2. Describe what the system does, not how it is implemented.
3. Use the language of the problem domain.
4. Use life-like scenarios and production-like assumptions where possible.
5. Keep each scenario atomic. It should fail for one clear business reason.
6. Keep test data independent between scenarios.
7. Prefer public interfaces for future automation. Do not rely on back-door state changes as the behaviour under test.
8. Write acceptance tests before implementation.
9. Make each criterion refutable. A reviewer should be able to say pass or no-pass.
10. Use technical UI steps only when the UI interaction is itself the requirement.

## Acceptance Criterion Shape

Each acceptance criterion should include:

- **Intent:** the behaviour or rule being specified.
- **Pass examples:** scenarios that should satisfy the criterion.
- **No-pass examples:** scenarios that should fail the criterion.
- **Data table:** required when examples vary by input data, role, status, amount, date, threshold, category, or external condition.
- **Automation note:** likely future automation level, such as domain DSL, API acceptance test, Playwright, Robot Framework, or exploratory support.

## Gherkin Guidance

Use Gherkin when it helps clarity:

```gherkin
Scenario: Short domain-language description
Given a meaningful business context
When a domain action happens
Then an observable business outcome occurs
```

Avoid implementation phrasing:

```gherkin
When the user clicks the blue Submit button
Then the database field is set to true
```

Prefer domain phrasing:

```gherkin
When the customer submits the application
Then the application is marked ready for review
```

## Data-Driven Acceptance Tests

When a criterion depends on data variations, include the data as a Markdown table directly in the story file.

Use this structure:

```markdown
#### Test Data

| Case | Input | Context | Expected outcome | Pass or no-pass |
|---|---|---|---|---|
| 1 | {{INPUT}} | {{CONTEXT}} | {{EXPECTED_OUTCOME}} | Pass |
| 2 | {{INPUT}} | {{CONTEXT}} | {{EXPECTED_OUTCOME}} | No-pass |
```

The table should be understandable to a product owner, tester, and developer without reading implementation code.
