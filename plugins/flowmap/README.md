# flowmap

Turn a plan, architecture, roadmap, migration or learning path into an
**interactive Flowmap** — a graph where nodes unlock only once their
prerequisites are done, coloured groups paint territories over the top, and todos
track progress — published as a live Claude Artifact with the map already on
screen.

**Audience:** anyone laying out work that has dependencies — architects, BAs,
engineers, project leads, or anyone onboarding someone into unfamiliar ground.

## What you get

Ask for a flowmap in plain language ("map out our checkout rebuild", "what
depends on what in this migration") and you get back:

- a **live artifact link** with the map already loaded and editable — drag nodes,
  tick todos, add and rename things, no import step
- a **`.flowmap.json`** file that stays the source of truth and can be re-imported

Edits save to the viewer's browser instantly. A **Save to artifact** button writes
them back to the link, so progress follows it across devices and to anyone the
link is shared with.

## When it triggers

On requests for a plan, system architecture, project phases, prerequisites,
"what depends on what", an onboarding path, migration steps or a rollout laid out
visually — even when the word "flowmap" is never used. It is the right choice over
a static Mermaid or ASCII diagram whenever the result should be explorable and
tickable rather than just looked at.

## Skills

| Skill | Purpose |
|---|---|
| `flowmap-artifact` | Design the graph, lay it out, validate it, build the page, publish it |

## Requirements

**Python 3.9 or newer — that is the whole list.** The scripts use only the
standard library, the Flowmap application ships inside the plugin, and no step
touches the network. It runs offline, from any directory.

Publishing declares two artifact capabilities, both load-bearing:

- `artifact` — powers the page's **Save** button
- `downloads` — makes the app's own **Export** button work, since the artifact
  viewer never grants pages download permission on their own

## First-run check

The skill runs a dependency check before its first build:

```bash
sh skills/flowmap-artifact/scripts/preflight.sh
```

It verifies the interpreter and every bundled file against `manifest.json`
(presence, size, checksum) and confirms the app asset still carries its three
substitution placeholders — an interrupted clone or a stripped asset otherwise
surfaces much later as a confusing build or render failure. It stamps itself on
success, so it is a no-op afterwards.

Exit codes drive the behaviour: `0` ready, `2` repairable, `3` blocked. On `2` the
skill is required to **ask before repairing**, then run `preflight.sh --install`,
which rebuilds the app asset from the bundled source — locally, no network. On `3`
it stops and reports rather than starting a build that would fail later.

## Maintenance

`assets/flowmap-app.html` is generated, not hand-edited. It is the Flowmap
application flattened into a single artifact-safe page — React inlined, fonts
embedded as data URIs, no external requests. Its source bundle ships beside it, so
a rebuild is reproducible and produces a byte-identical file:

```bash
python3 skills/flowmap-artifact/scripts/build_app_asset.py \
        skills/flowmap-artifact/assets/flowmap-source.html
python3 skills/flowmap-artifact/scripts/preflight.py --write-manifest
```

Regenerate `manifest.json` after changing **any** shipped file, or the first-run
check will report a checksum mismatch.

`skills/flowmap-artifact/references/artifact-contract.md` records why the flatten
is shaped the way it is — three of its steps exist to fix specific, non-obvious
breakages and should not be removed casually.

## Third-party content

The bundled page embeds React and React DOM 18.3.1 (MIT, license headers
preserved) and the JetBrains Mono and Space Grotesk webfonts (SIL Open Font
License).
