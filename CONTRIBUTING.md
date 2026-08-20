# Contributing to agentic-practices-marketplace

This marketplace catalogues Claude Code **plugins** from the Agentic Practices training programmes. A plugin is a bundle that can contain skills, slash commands, subagents, hooks, and MCP server configurations.

## Repository layout

```
agentic-practices-marketplace/
├── .claude-plugin/
│   └── marketplace.json        # Catalog of available plugins
├── plugins/
│   └── <plugin-name>/          # One directory per plugin
│       ├── .claude-plugin/
│       │   └── plugin.json     # Plugin manifest (only file in here)
│       ├── skills/             # Skills (each in its own subdir with SKILL.md)
│       ├── commands/           # Slash commands as flat .md files
│       ├── agents/             # Subagent definitions as .md files
│       ├── hooks/              # Hook configuration (hooks.json)
│       ├── scripts/            # Scripts invoked by hooks/commands
│       ├── .mcp.json           # MCP server definitions (optional)
│       └── README.md           # What this plugin does, who it's for
└── README.md
```

Only `plugin.json` belongs in `.claude-plugin/`. Everything else lives at the plugin root.

## Adding a new plugin

1. Create `plugins/<plugin-name>/` (kebab-case).
2. Add `plugins/<plugin-name>/.claude-plugin/plugin.json`:
   ```json
   {
     "name": "<plugin-name>",
     "version": "0.1.0",
     "description": "What this plugin does, in one line.",
     "author": { "name": "Your Name" }
   }
   ```
3. Add the components the plugin provides (skills, commands, agents, hooks).
4. Register it in `.claude-plugin/marketplace.json` by adding an entry to the `plugins` array:
   ```json
   {
     "name": "<plugin-name>",
     "source": "./plugins/<plugin-name>",
     "description": "What this plugin does, in one line."
   }
   ```
5. Open a pull request. Include a short description of who the plugin is for and when it should trigger.

## Adding a skill to a plugin

Skills live under `plugins/<plugin-name>/skills/<skill-name>/`. Each skill needs a `SKILL.md` with YAML frontmatter:

```markdown
---
name: skill-name
description: One-line trigger description. Be specific about WHEN this should fire — Claude uses this to decide whether to load the skill.
---

# Skill body
Instructions, examples, references.
```

Optional supporting files (`reference.md`, `scripts/`, assets) sit alongside `SKILL.md`.

## Naming

- Plugin and skill directory names: kebab-case.
- Plugin names should signal the audience or domain (e.g. `prd-from-pitch`, `claude-md-auditor`).

## Keep skills generic

These skills are public and reusable. Keep client-identifying material and private processes out of skill content — parameterise it instead.
