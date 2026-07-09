# Initial Product Tech Stack Setup

Use this reference only when `prd-from-pitch` is creating a PRD for initial product setup, or when a follow-up feature genuinely requires a new stack decision.

Do not load this reference for ordinary follow-up feature PRDs where the product stack already exists.

## Purpose

The base tech stack is part of the technical constraints score for initial product setup. It should make the first implementation plan realistic without pretending the team has made final architecture decisions.

## Required Stack Layers

Document each layer with a proposed choice, confidence level, and notes:

| Layer | What to decide |
|---|---|
| Frontend | Web, mobile, desktop, chat interface, admin console, or no UI. |
| Backend | API, serverless functions, workflow automation, integration service, or no backend. |
| Data store | Existing system of record, relational database, document store, files, spreadsheet, vector store, cache, or none. |
| Authentication / identity | Existing SSO, OAuth, role-based access, anonymous demo, service account, or none. |
| External integrations | Internal systems, APIs, MCP servers, third-party tools, email, Slack, GitHub, CRM, ERP, or data feeds. |
| Test tooling | Unit test framework, API acceptance test tool, Playwright, Robot Framework, manual exploratory support. |
| Hosting / deployment | Local-only demo, static hosting, cloud app, serverless, container, internal platform, or existing deployment path. |
| Observability / logging | Application logs, audit events, analytics, error reporting, or demo-only visibility. |

## Scoring Guidance

Award the technical constraints portion of the score based on:

- 5 points: stack layers are named or explicitly marked not applicable.
- 4 points: data, identity, and integration constraints are clear.
- 3 points: test tooling and deployment path are plausible.
- 2 points: confidence levels and assumptions are honest.
- 1 point: the stack supports the demo slice without overbuilding.

## Constraint Prompts

Ask one question at a time when a stack decision materially affects the PRD:

- What system or dataset must this product read from or write to?
- Does the first demo need authentication, or can it run with sample data?
- Is this a UI workflow, API workflow, background automation, or reporting workflow?
- Where must this run for the first demo: local machine, internal environment, cloud, or existing platform?
- Which test tool best matches the acceptance examples: API tests, Playwright, Robot Framework, or domain-level executable specs?
