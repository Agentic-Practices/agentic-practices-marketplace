# Flowmap artifact contract (source of truth)

How a Flowmap JSON file becomes a live, editable page. Read this before writing
JSON or touching the build scripts.

## The pipeline

```
your JSON  ──layout_flowmap.py──▶  x/y + progress normalized
           ──validate_flowmap.py─▶  exit 0 required
           ──build_flowmap_artifact.py──▶  <name>.flowmap.html  (~0.75 MB)
           ──Artifact tool──────▶  live URL, map already on screen
```

`build_flowmap_artifact.py` fills three placeholders in `assets/flowmap-app.html`:

| Placeholder | Becomes |
|---|---|
| `__FLOWMAP_TITLE__` | tab + page title |
| `__FLOWMAP_SEED__` | the starter array assigned to `window.FLOWMAP_STARTERS` |
| `__SELF_TEMPLATE__` | base64(gzip(template)), so the page's Save button can rebuild itself |

## How auto-load actually works

The app has a built-in hook — this is not something the skill bolts on. On mount
it calls `loadStarters()`, which reads `window.FLOWMAP_STARTERS` (an array of
project objects, each with a version field `v`) and merges it into the store via
`mergeStarters()`. That call also deletes the empty default project and repoints
`currentId`, so a fresh viewer lands directly on the seeded map.

Persistence is `localStorage['flowmap.v2']`, holding
`{ projects, currentId, _seededV }`.

## Input shapes accepted by build_flowmap_artifact.py

| Shape | Condition |
|---|---|
| **Full store** | `d.projects` is an object — preferred, matches Export |
| **Project array** | `Array.isArray(d)`, each with `.nodes` |
| **Bare project** | `d.nodes` is an object |

All three normalize to the starter array the app wants. Write a full store: it is
what the app's own Export produces, so the file round-trips.

## The `v` field — the rule that decides whether edits survive

`mergeStarters()` reseeds a project only when the incoming `v` is **higher** than
the version recorded in `_seededV`. That single comparison is what protects a
viewer's work:

| Situation | `v` | Result |
|---|---|---|
| Viewer clicks **Save** | unchanged | Recorded version still matches, so the merge is skipped and their localStorage wins. New viewers get the saved state. |
| You revise the map's content | **bump it** | Forces a reseed, deliberately replacing what the viewer had. |

So: republishing the same map with the same `v` is safe and non-destructive.
Bumping `v` is how you say "throw away the old version on purpose". Never bump it
casually — it silently discards someone's ticked todos.

Projects a viewer creates themselves are never listed in `_seededV`, so
`mergeStarters()` leaves them alone.

## Required fields

### Store
- `projects` — object map
- `currentId` — a key of `projects`
- `_seededV` — emit `{}`

### Project
- `id`, `name`
- `groups` — array of `{ id, name, color }`, `color` as `#RRGGBB`
- `nodes` — object map; **keys must equal `node.id`**

Do not emit v1 `tracks` / `track` for new maps.

### Node

| Field | Required | Notes |
|---|---|---|
| `id` | yes | kebab-case; equals its map key |
| `title` | yes | short |
| `groups` | yes | array of group ids; may be empty or multi |
| `size` | yes | `S` \| `M` \| `L` |
| `desc` | yes | string, may be `""` |
| `needs` | yes | array of node ids — the real prerequisites |
| `todos` | yes | array, may be empty |
| `manualDone` | yes | boolean |
| `x`, `y` | recommended | numbers; the layout script fills these |
| `needMode` | optional | `"any"` or `"all"`; omit for `all` |

### Todo
`{ "id": "t1", "text": "…", "done": false }`

## Why the app asset is pre-flattened

`Flowmap.html` is a self-extracting bundle that rebuilds itself at runtime using
`blob:` URLs and CDN fetches. A published Artifact runs under a strict CSP where
neither works, so `build_app_asset.py` does that work ahead of time. Three details
in it are load-bearing, and all three were failures before they were fixes:

1. **React is inlined before the runtime.** The runtime's `loadReactUmd()` starts
   with `if (w.React && w.ReactDOM) return`, so pre-defining them means it never
   reaches unpkg.
2. **`<x-dc>` is escaped inside the inlined runtime.** The runtime locates its
   component by scanning page source for the first `<x-dc` and last `</x-dc>`.
   Inlining the runtime put its own matcher and warning strings into the page, so
   the scan latched onto those and rendered a slice of the runtime's source. The
   occurrences are escaped to `\x3c`, which is identical at runtime but invisible
   to a text scan.
3. **The page is pure ASCII.** It is body-level content with no `<meta charset>`
   of its own, so a host serving `text/html` without a charset leaves the browser
   guessing — and guessing Latin-1 turns the app's check marks into mojibake.

Rebuild the asset only when the Flowmap app itself changes:

```bash
python3 scripts/build_app_asset.py /path/to/Flowmap.html
```

## Known-harmless console noise

Two things appear in the console on every load and neither is a fault:

- `<svg> attribute width: Expected length, "{{ svgW }}"` and similar — the browser
  parsing the app's uncompiled template markup before the runtime compiles it.
  Present in the original app too.
- `flowmap-starters.json 404` — the app's optional starter fetch. It is wrapped in
  a `try`, and `window.FLOWMAP_STARTERS` is already set, so the failure is ignored.

## Smoke check

```bash
python3 scripts/validate_flowmap.py path/to/file.json   # exit 0 required
```
