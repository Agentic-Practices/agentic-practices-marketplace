# Flowmap JSON schema (v2)

Compatible with Flowmap grouped app (`localStorage` key `flowmap.v2`).

**Data contract:** see `artifact-contract.md` (source of truth for the shapes the app accepts).

## Full store (required agent output)

```ts
type Store = {
  projects: Record<string, Project>;
  currentId: string | null;
  _seededV?: Record<string, number>; // optional; emit {} for new files
};
```

## Project

```ts
type Project = {
  id: string;          // stable slug, unique in store
  name: string;        // display title
  groups: Group[];
  nodes: Record<string, Node>; // keys MUST equal node.id
  // optional / internal:
  v?: number;
  _blank?: boolean;
};
```

## Group

```ts
type Group = {
  id: string;
  name: string;
  color: string; // "#RRGGBB" only
};
```

Groups are territories only — they do **not** gate progress.

Nodes may list **multiple** groups (`groups: ["a", "b"]`). That is intentional: the node
belongs to both hulls and layout may **overlap** those groups. Do not treat groups as
exclusive non-overlapping columns.

## Node

```ts
type Node = {
  id: string;
  title: string;
  groups: string[];     // group ids; may be empty
  size: "S" | "M" | "L";
  desc: string;
  needs: string[];
  needMode?: "all" | "any"; // default all
  todos: Todo[];
  manualDone: boolean;
  x?: number | null;
  y?: number | null;
};

type Todo = {
  id: string;
  text: string;
  done: boolean;
};
```

## Runtime semantics

### Done (raw)

```
rawDone = manualDone OR (todos.length > 0 AND every todo.done)
```

Missing `todos` array crashes render — **always emit `todos: []`**.

### Needs met

- Empty needs → met
- `needMode === "any"` → at least one need complete
- Else → every need complete

### Complete

```
complete[id] = needsMet(id) AND rawDone(id)
```

### Locked

```
locked = !needsMet
```

### Auto-layout (null/missing x)

Depth from needs; place at roughly `x = 90 + depth * 262`, `y = 90 + index * 128`.

## Import formats

1. **Store** `{ projects, currentId, _seededV? }` — replace store (normalized on import).
2. **Array** `Project[]` — merge each project.
3. **Bare project** `{ id, name, groups, nodes, ... }` — merge one project (supported; prefer store).

Invalid → alert. Prefer **store** for agent output (matches Export).

## Legacy v1

`tracks` / `track` migrate on import/normalize. **Emit `groups` for all new maps.**

## Minimal valid store

```json
{
  "projects": {
    "demo": {
      "id": "demo",
      "name": "Demo",
      "groups": [
        { "id": "plan", "name": "Plan", "color": "#f5a623" },
        { "id": "build", "name": "Build", "color": "#2dd4bf" }
      ],
      "nodes": {
        "idea": {
          "id": "idea",
          "title": "Idea",
          "groups": ["plan"],
          "size": "S",
          "desc": "Starting point — no prerequisites.",
          "needs": [],
          "todos": [],
          "manualDone": false,
          "x": 90,
          "y": 90
        },
        "prototype": {
          "id": "prototype",
          "title": "Prototype",
          "groups": ["build"],
          "size": "L",
          "desc": "First working version.",
          "needs": ["idea"],
          "todos": [
            { "id": "t1", "text": "Happy-path demo", "done": false }
          ],
          "manualDone": false,
          "x": 352,
          "y": 90
        }
      }
    }
  },
  "currentId": "demo",
  "_seededV": {}
}
```

## Field constraints

| Field | Rules |
|-------|--------|
| ids | kebab-case preferred; unique within project |
| title | short, scannable |
| desc | 1–2 sentences |
| size | only `S`, `M`, `L` |
| color | `#` + 6 hex digits |
| needs | no self-need; prefer acyclic |
| todos | always an array |
| todos[].id | unique within that node |
| manualDone | `true` only when the node is complete; if todos exist they must all be `done: true` |
| x, y | set by `layout_flowmap.py` after graph edits (preferred) |

## Progress consistency

App: `rawDone = manualDone || (todos.length > 0 && every todo.done)`.

Agent rules:

- **Done node** → `manualDone: true` and every todo `done: true`
- **Incomplete** → `manualDone: false`; unfinished todos `done: false`

`layout_flowmap.py --normalize-progress` enforces the done/todo alignment.
