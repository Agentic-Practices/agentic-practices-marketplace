# CLAUDE.md

Guidance for Claude when working on this marketplace. Keep edits surgical; this is a distribution point, not a development workspace.

## What this repo is

A public Claude Code plugin marketplace from the Agentic Practices training programmes. Plugins bundle one or more skills (and optionally commands, agents, hooks, MCP configs). The catalog lives in `.claude-plugin/marketplace.json`; each plugin's manifest lives in `plugins/<name>/.claude-plugin/plugin.json`. See `CONTRIBUTING.md` for the directory contract.

## Marketplace copies and contributor upstreams

The marketplace is the canonical, distributable source for every skill it ships. What lives here is what installed users get.

Contributors often maintain their own working copy of a skill outside this repo (commonly `~/.claude/skills/<name>/`). That's fine, but the marketplace copy is not a passive mirror of any contributor's local tree:

- **Edits to the marketplace copy are valid on their own.** You do not need an upstream change to justify a marketplace edit. Scrubbing personal content, removing contributor-specific defaults, or fixing a sample reference is normal marketplace maintenance.
- **Drift between a contributor's local copy and the marketplace is expected**, especially where the marketplace version has been generalised (e.g. removing personal templates, parameterising examples). Don't blanket-overwrite the marketplace from a local tree without diffing first.
- **When syncing from a local copy**, review the diff before committing. Look for re-introduction of personal artifacts, hardcoded paths into a contributor's home directory, or client-identifying content.

Watch for symlinks when copying directories — use `cp -RL` to dereference. Don't commit symlinks.

## Plugin grouping convention

Group skills by domain, not by author or by date added. Current groupings:

| Plugin | Skills | Purpose |
|---|---|---|
| `prd-from-pitch` | prd-from-pitch | Turn a pitch or feature idea into a scored PRD and story files |
| `claude-md-auditor` | claude-md-auditor | Audit project context placement, currency, hierarchy, and enforcement |
| `setup-statusline` | — (ships `/setupstatusline` command) | Adapt a reference statusline to the user's OS and wire it into their settings |

When adding a new skill, place it in an existing plugin if the domain fits. Spin up a new plugin only when the domain is genuinely distinct.

## Dependencies and interlinks

Skills that orchestrate other skills must declare it. There are two layers:

**1. Plugin-level dependencies** (in `plugin.json`): add a `dependencies` array whenever a skill in this plugin calls a skill in another plugin. Forgetting this means users install the orchestrator and hit runtime failures when the dependency isn't loaded.

**2. Skill-level invocation discipline** (in `SKILL.md`): always invoke sibling skills **by skill name**, never by hardcoded path to their scripts. When skills are installed via this marketplace, they live in a plugin cache directory, not in any contributor's `~/.claude/skills/`. Paths like `~/.claude/skills/<name>/scripts/...` will break for installed users. Let Claude resolve and run the dependent skill by name.

If you spot a SKILL.md with hardcoded sibling-skill paths, fix it in the marketplace copy.

## What not to do

- Don't bump plugin versions for content edits unless the contract or interface changes — version bumps trigger re-installs for every user.
- Don't add a skill to multiple plugins. One skill, one home. Cross-plugin reuse happens through dependencies, not duplication.
- Don't commit symlinks. Always dereference before copying.
- Don't include client-identifying material in skill content. These skills are public — parameterise instead.
