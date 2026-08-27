---
name: flowmap-artifact
description: >
  Build a Flowmap — an interactive, editable dependency map of a plan,
  architecture, roadmap, learning path, or decision — and publish it as a live
  Claude Artifact with the map already loaded and ready to edit. Use whenever
  someone wants a plan, system architecture, project phases, prerequisites,
  "what depends on what", onboarding path, migration steps, or a rollout laid out
  visually as nodes with dependencies, coloured groups and checkable todos — even
  if they never say the word "flowmap". Prefer this over a static Mermaid or ASCII
  diagram whenever the result should be explorable, tickable, or editable rather
  than just looked at. Also use for "/flowmap", "make me a flowmap", "map this
  out", or a request to update an existing Flowmap.
metadata:
  short-description: "Publish an editable Flowmap as a live artifact"
---

# Flowmap → live editable artifact

Turn a plan, architecture or decision into a **Flowmap**: a directed graph where
nodes unlock only when their prerequisites are done, groups paint coloured
territories over the top, and todos track progress. The deliverable is a published
artifact with the map already on screen — no file to open, no Import step.

## Pipeline

```
design the graph  →  write <slug>.flowmap.json
                  →  layout_flowmap.py       (x/y + progress flags)
                  →  validate_flowmap.py     (exit 0 required)
                  →  build_flowmap_artifact.py  → <slug>.flowmap.html
                  →  Artifact tool           → live URL
```

Everything needed ships inside this skill — the app is bundled as
`assets/flowmap-app.html`, so this works in any directory on any machine with
Python 3, offline. Resolve scripts relative to **this skill's own directory**,
never a hardcoded skills root; a same-named script elsewhere may be a different
version. Installed as a plugin that directory is
`${CLAUDE_PLUGIN_ROOT}/skills/flowmap-artifact`; if that variable is unset, use
the directory containing this `SKILL.md`. Below it is written `$SKILL_DIR`.

Load `references/artifact-contract.md` before writing JSON the first time in a
session. Load `references/schema.md` for field-level types and
`references/authoring.md` for large, ambiguous, or high-stakes maps.

## 0. Check dependencies — first run only

Before the first build in a session:

```bash
sh "$SKILL_DIR/scripts/preflight.sh"
```

A fast presence-and-integrity check that stamps itself, so later runs are a no-op.
Act on the **exit code** rather than the prose:

| Exit | Meaning | What to do |
|---|---|---|
| `0` | ready | Continue, and say nothing about it. |
| `2` | repairable | **Ask the user first.** Show them what is missing and that the fix rebuilds the bundled app asset locally — it writes files inside the plugin. Only with their approval: `sh "$SKILL_DIR/scripts/preflight.sh" --install` |
| `3` | blocked | Stop and report what it printed. Do not start the build; it would fail later and less clearly. |

Never run `--install` unprompted. It modifies files, and someone who installed
this plugin has not thereby agreed to let it rewrite itself.

Python 3.9+ is the only external dependency. Everything else is bundled, and no
step needs network access.

## 1. Clarify — briefly

Ask only what you cannot reasonably infer. A vague request is usually still
enough to draft something concrete, and a draft the user corrects beats an
interview.

| Input | Default when unstated |
|---|---|
| Topic / goal | required |
| Mode | infer: `explore` (concepts) · `execute` (work + todos) · `decide` (`needMode: "any"`) |
| Depth | medium, ~25–40 nodes |
| Audience | the person asking |

If the user is mapping work that already exists (a repo, a document, a plan in the
conversation), read it first. A map built from the real thing is worth far more
than one built from the topic word.

## 2. Design the graph

**Groups are territories, not logic.** A group colours a region of the canvas. It
says "these belong together". It does **not** gate anything. Only `needs` gates.
Confusing the two produces maps that look organised and teach nothing.

**`needs` are real prerequisites.** Ask "is this genuinely impossible before that
finishes?" If the honest answer is "no, just tidier", it is not a `need`. Aim for
a few roots and shallow-to-medium depth; a map where everything chains off one
node is a list wearing a graph costume.

**Multi-group nodes are first-class.** `"groups": ["frontend", "auth"]` puts a
node in both territories, and the layouter places it on the shared edge so the
hulls overlap there. That overlap is the *only* intended reason hulls should
touch, and it is how you show a genuine shared surface between two domains. Use it
honestly rather than hoping unrelated groups drift together.

Practical shape:

- 5–10 groups, 20–50 nodes (hard cap ~70 — past that, split into several maps).
- `size`: `L` for the few nodes that carry the most weight, `M` for substance,
  `S` for everything else. Uniform sizing wastes a signal.
- `desc`: one or two sentences. Not an essay — the node is a handle, not the doc.
- `todos`: 0–4 on execute nodes; skip them on pure concept nodes.
- Include risk and kill-criteria nodes when the map is a plan. "What would make us
  stop" is usually the most valuable node on the canvas.
- Legal, tax and medical content: awareness plus "talk to a professional". Never
  binding conclusions.

### Progress flags

Completion is `manualDone OR (todos exist AND all todos done)`.

| State | Encode as |
|---|---|
| Done | `manualDone: true`, and every todo `done: true` |
| Partial | `manualDone: false`, some todos `done: true` |
| Not started | `manualDone: false`, todos `done: false` |
| No checklist | `todos: []`, use `manualDone` alone |

Never mark a node done while it still has unchecked todos — the app computes
unlocks from this, so an inconsistent node silently unlocks work that is not
actually ready.

## 3. Write the JSON

Always a **full store** — it matches what the app's own Export produces, so the
file round-trips:

```json
{
  "projects": {
    "topic-slug": {
      "id": "topic-slug",
      "name": "Human Title",
      "groups": [{ "id": "plan", "name": "Plan", "color": "#f5a623" }],
      "nodes": {
        "idea": {
          "id": "idea", "title": "Idea", "groups": ["plan"], "size": "S",
          "desc": "Starting point.",
          "needs": [], "todos": [], "manualDone": false
        }
      }
    }
  },
  "currentId": "topic-slug",
  "_seededV": {}
}
```

Node map keys must equal `node.id`. Omit `x`/`y` — the layouter fills them.

Palette: `#60a5fa #4ade80 #a78bfa #f5a623 #f472b6 #2dd4bf #fb7185 #38bdf8 #fbbf24`

## 4. Lay out, validate, build

```bash
# installed as a plugin: "${CLAUDE_PLUGIN_ROOT}/skills/flowmap-artifact"
# local checkout:        the directory containing this SKILL.md
python3 "$SKILL_DIR/scripts/layout_flowmap.py"      map.flowmap.json --in-place --normalize-progress
python3 "$SKILL_DIR/scripts/validate_flowmap.py"    map.flowmap.json
python3 "$SKILL_DIR/scripts/build_flowmap_artifact.py" map.flowmap.json -o map.flowmap.html
```

Let the layouter place nodes. It packs each group's exclusive members tightly,
shelf-packs the groups apart, and puts multi-group nodes on the short shared edge
— which is what keeps hulls compact and their overlaps meaningful. Hand-place
coordinates only when the user asks for pixel-perfect control.

Do not tell the user the map is ready unless the validator exited 0.

## 5. Publish

Call the **Artifact** tool with the built `.html`:

```
file_path:    map.flowmap.html
title:        the map's name
description:  one sentence on what the map covers
favicon:      a relevant emoji, kept stable across redeploys
capabilities: {"artifact": {}, "downloads": true}
```

Both capabilities are load-bearing, so pass them every time:

- `artifact` powers the **Save** button. Without it the button hides itself and
  edits never leave the viewer's browser.
- `downloads` makes the app's own **Export** button work. The artifact viewer
  never grants pages download permission, so Export's blob link silently does
  nothing unless the page routes it through this capability — and Export is how a
  viewer gets their map back out.

The declaration is fixed and documented in `references/artifact-contract.md`;
consult the `artifact-capabilities` skill only if a publish fails with a
capability error or you are rebuilding the app asset.

You do **not** need the `artifact-design` skill here. That pass calibrates design
investment for pages you author; this page is a pre-built application whose design
is fixed, and there is no markup of yours to design.

To update a map published earlier, pass that artifact's `url` so it redeploys to
the same link instead of creating a second one.

## 6. Hand it over

Tell the user:

- the **artifact link**, and that the map is already loaded
- group and node counts, and a 5–8 node first path through the graph
- that edits save to their browser instantly, and **Save to artifact** (bottom
  right) writes them back to the link so progress follows it to other devices and
  anyone they share it with
- the `.json` path, which stays the source of truth and can be re-imported

Then offer to deepen a thin area, split an overgrown map, or add todos.

## Editing an existing map

1. Start from the existing JSON when there is one; otherwise ask the user to
   **Export** from the artifact so their progress comes with it.
2. Keep node ids stable when renaming titles, and update every `needs` entry if an
   id really must change.
3. Preserve `manualDone` and todo state unless the user asked you to reset it.
4. Re-run layout and validation, rebuild, and republish to the **same URL**.
5. **Leave `v` alone.** Republishing with an unchanged `v` is non-destructive: the
   viewer's saved edits win, and new viewers see your update. Raise `v`
   (`--version N`) only when the user has asked you to overwrite what is there —
   it silently discards their ticked todos.

## Do not

- Use groups as fake prerequisites, or `needs` as mere sequencing preference
- Mark a node done while its todos are unchecked
- Dump essays into `desc`
- Exceed ~70 nodes instead of splitting
- Bump `v` on a routine update
- Claim the map is ready when the validator failed
- Return a Mermaid diagram or a markdown table when a flowmap was asked for
