# agentic-practices-marketplace

Public Claude Code skill and plugin marketplace from the **Agentic Practices** training programmes.

## What this is

A public, version-controlled catalogue of Claude Code skills and plugins developed for the Agentic Practices training programmes. Anyone can add this marketplace to their Claude Code configuration and install the skills that fit their work — auditing project context, pressure-testing an idea, or turning a pitch into a PRD.

This repository is public and free to use.

## What's inside

- **Skills** — task-specific instructions and assets Claude Code loads on demand (e.g. PRD writing, design grilling).
- **Plugins** — bundles of skills, commands, hooks, and MCP server configurations distributed as a unit.

### Plugins

| Plugin | What it does |
|---|---|
| `hackathon-project-pitch` | Stress-test a hackathon idea with forcing questions and produce a five-minute, six-slide sponsor-approval pitch — `overview.md`, `presentation.html`/`.pdf`, and `qanda.md`. |
| `prd-from-pitch` | Turn a project pitch or feature idea into a scored PRD and Dave Farley-style user story files with pass/no-pass acceptance criteria. |
| `claude-md-auditor` | Score a complete `CLAUDE.md` setup, identify stale or misplaced context, and offer explicitly approved improvements. |
| `setup-statusline` | Adapt a reference context-window statusline to your operating system and wire it into your Claude Code settings — run `/setupstatusline`. |

## Using the marketplace

Add this marketplace to Claude Code, then browse and install plugins from it.

```bash
claude plugin marketplace add agentic-practices/agentic-practices-marketplace
```

Pin to a branch or tag if you want stability over latest:

```bash
claude plugin marketplace add agentic-practices/agentic-practices-marketplace@main
```

Once added, install plugins interactively from inside Claude Code with the `/plugin` command, or:

```bash
claude plugin install <plugin-name>@agentic-practices-marketplace
```

### Updating

Refreshing pulls the latest `marketplace.json` and plugin sources on demand.

Refresh the catalog (what plugins exist and at what version):

```bash
claude plugin marketplace update agentic-practices-marketplace
```

Or from inside Claude Code:

```
/plugin marketplace update agentic-practices-marketplace
```

Omit the name to refresh every marketplace you've added.

Refreshing the catalog does **not** upgrade plugins you've already installed. Update those separately:

```bash
claude plugin update <plugin-name>@agentic-practices-marketplace
```

## Contributing

Skills and plugins are added via pull request. Each contribution should include a clear description of what it does, who it's for, and when it should trigger. See `CONTRIBUTING.md`.
