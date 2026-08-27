# Flowmap authoring guide

Always emit a **full store** (`projects` + `currentId` + `_seededV`) that passes
`scripts/validate_flowmap.py`. See `artifact-contract.md` for how the JSON reaches the published page.

## Progress (done vs unchecked)

| State | `manualDone` | Todos |
|-------|--------------|--------|
| Done | `true` | all `done: true` (or `todos: []`) |
| Incomplete | `false` | open items `done: false`; partial OK |
| Never | `true` while any todo is still `false` | — |

After status maps: `layout_flowmap.py file.json --in-place --normalize-progress`.

## Groups (overlap + multi-membership)

- A node may list **multiple** `groups` — it belongs to every listed territory.
- Group hulls **may overlap**; shared nodes and strong cross-group links *should* create overlap.
- Groups are not exclusive columns or non-overlapping swimlanes.

## Layout (let code place nodes)

Do **not** hand-grid large maps. Run:

```bash
python3 scripts/layout_flowmap.py file.json --in-place --normalize-progress
```

Algorithm (cheap):

1. Depth → seed x (left→right unlock order).
2. Build group affinity (multi-group nodes + cross-group needs).
3. Hub group centre; linked groups adjacent on a ring; short force relax.
4. Place nodes near mean of all their groups; spring-refine along needs.

## Choose a shape for the domain

| Domain | Typical groups | Edge style |
|--------|----------------|------------|
| Start a company | Idea, Customer, Product, Legal & Finance, Team, Go-to-Market, Ops, Growth | Mostly sequential with parallel lanes |
| Learn a stack | Core, Data, Auth, Frontend, Security, Ship, Grow | Strict technical prereqs |
| How X works (e.g. AI) | Foundations, Models, Data, Training, Systems, Product, Safety, Ops | Explore roots + branching depth |
| Marketing decisions | Research, Positioning, Channels, Content, Paid, Measure, Optimize | `needMode: any` between channels |
| Legal/tax awareness | Entity, Contracts, IP, Tax, Employment, Privacy, Fundraising | Awareness + "escalate to pro" nodes |
| Physical systems | Site, Water, Energy, Food, … | Resource dependencies |

## Node quality

**Good**

- "Customer Interviews" — *Talk to 30+ potential users before building.*
- "Migrations" — *Numbered SQL files, embedded, applied at startup.*
- "Willingness to Pay" — *Get price signals before you build.*

**Weak**

- "Strategy" with empty desc
- "Do marketing" with no unlock logic
- Ten near-duplicate nodes ("SEO 1", "SEO 2")

## Edge quality

Ask: "Can someone honestly complete B without A?"

- Yes they can skip A → do not add the need (or use `needMode: any` with alternatives)
- B is unsafe/useless without A → add the need

Prefer **fan-out from few roots** over forcing everything through one bottleneck unless the bottleneck is real (e.g. Incorporate before Bank Account).

## Size rubric

| Size | Meaning |
|------|---------|
| S | Quick read, small task, or thin concept |
| M | Real work session or core concept |
| L | Multi-day effort or capstone (MVP, PMF, Solar Array) |

## Todos

Use when the node is **executable**:

```json
"todos": [
  { "id": "c1", "text": "Write interview script", "done": false },
  { "id": "c2", "text": "Book 10 calls", "done": false }
]
```

Skip todos on pure orientation nodes ("Market Research" can stay todo-free if desc is enough).

## Decide mode (`needMode: "any"`)

Example: ship if you did a design polish **or** a bug-fix pass:

```json
"needs": ["design-pass", "bugfix-pass"],
"needMode": "any"
```

Use sparingly so the graph stays meaningful.

## High-stakes domains

Frame nodes as:

- Decisions to make
- Documents / data to gather
- Questions for a lawyer / accountant / doctor
- Common landmines (awareness)

Example desc:

> Choose entity type and registration path for your jurisdiction. Confirm with a local attorney before filing — rules differ by country and state.

## Splitting large topics

If you exceed ~50–60 nodes:

1. Overview map with L-sized "portal" nodes
2. Child maps per domain (`company-legal.flowmap.json`, …)
3. Cross-link in `desc`: "Deep dive: import company-legal map"

## Recommended first-path (tell the user)

After generating, name 5–8 node ids in order for a first walk-through so the map is usable immediately, e.g.:

`problem-discovery → customer-interviews → value-proposition → mvp-spec → build-mvp → first-customers`

## Anti-sycophancy

Include at least a few of:

- Kill-criteria / "when to stop"
- Common failure modes
- Cost / time reality checks
- Alternatives the user might not like but should see
