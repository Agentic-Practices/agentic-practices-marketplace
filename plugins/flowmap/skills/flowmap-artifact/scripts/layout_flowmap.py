#!/usr/bin/env python3
"""
Tight Flowmap layout — compact group hulls (simple).

Measured problem: multi-group nodes placed far away blew out convex hulls
(e.g. GTM "Customer & Problem" was ~900×1000 empty space).

Approach:
  1. Exclusive (single-group) nodes define each group's compact pack — a dense
     square-ish grid (depth only sorts order). Grid pitch (COL/ROW) is wider
     than the rendered 196px card so cards never overlap.
  2. Pack centres use springs so bridge-linked groups sit adjacent (touching),
     and pack AABBs never interpenetrate.
  3. Multi-group "bridge" nodes are NOT buried inside their primary pack —
     that forces the *other* group's hull to stretch across the map. Instead
     each bridge sits in the shared lens (centroid of its groups' pack
     centres); with adjacent packs that lands on the boundary, so every hull
     only reaches its own edge.

Result: hulls hug their members (no giant empty interiors, no cross-map
stretch to a stray secondary node), and cards keep breathing room.

Usage:
  python3 layout_flowmap.py map.flowmap.json --in-place [--normalize-progress]
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from collections import defaultdict
from typing import Any

X0 = 100.0
Y0 = 100.0
# Rendered card is 196px wide; COL/ROW are the grid pitch inside a pack.
# COL must exceed the card width (plus a gap) or cards visibly overlap.
CARD_W = 196.0
CARD_H = 96.0
COL = 244.0  # 196 card + ~48 horizontal breathing room
ROW = 150.0  # card height + vertical breathing room
PACK_AIR = 130.0
UNGROUPED = "_ungrouped"


def node_depth(nodes: dict[str, dict]) -> dict[str, int]:
    memo: dict[str, int] = {}

    def depth(nid: str, stack: set[str]) -> int:
        if nid in memo:
            return memo[nid]
        if nid in stack:
            return 0
        stack.add(nid)
        needs = [p for p in (nodes[nid].get("needs") or []) if p in nodes]
        d = 0 if not needs else 1 + max(depth(p, stack) for p in needs)
        stack.discard(nid)
        memo[nid] = d
        return d

    for nid in nodes:
        depth(nid, set())
    return memo


def membership(nodes: dict[str, dict], gid_set: set[str]) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for nid, n in nodes.items():
        gs = [g for g in (n.get("groups") or []) if g in gid_set]
        out[nid] = gs if gs else [UNGROUPED]
    return out


def compact_grid(
    ids: list[str], depths: dict[str, int], nodes: dict[str, dict]
) -> dict[str, tuple[float, float]]:
    if not ids:
        return {}
    ordered = sorted(
        ids, key=lambda i: (depths.get(i, 0), nodes[i].get("title") or i, i)
    )
    n = len(ordered)
    cols = n if n <= 3 else min(3, max(2, int(math.ceil(math.sqrt(n)))))
    local: dict[str, tuple[float, float]] = {}
    for i, nid in enumerate(ordered):
        local[nid] = ((i % cols) * COL, (i // cols) * ROW)
    return local


def pack_wh(local: dict[str, tuple[float, float]]) -> tuple[float, float]:
    if not local:
        return (COL, ROW)
    xs = [p[0] for p in local.values()]
    ys = [p[1] for p in local.values()]
    return (max(xs) - min(xs) + COL, max(ys) - min(ys) + ROW)


def layout_pack_centers(
    gids: list[str],
    sizes: dict[str, tuple[float, float]],
    multi_pairs: list[tuple[str, str]],
) -> dict[str, tuple[float, float]]:
    """Pack top-left origins. Multi-linked packs sit as neighbours; no AABB overlap."""
    if not gids:
        return {}
    half = {g: (sizes[g][0] / 2, sizes[g][1] / 2) for g in gids}
    n = len(gids)
    cols = max(1, int(math.ceil(math.sqrt(n))))
    centers: dict[str, list[float]] = {}
    for i, g in enumerate(gids):
        r, c = divmod(i, cols)
        centers[g] = [c * 500.0 + half[g][0], r * 380.0 + half[g][1]]

    springs = []
    seen = set()
    for a, b in multi_pairs:
        if a not in centers or b not in centers or a == b:
            continue
        k = (a, b) if a < b else (b, a)
        if k not in seen:
            seen.add(k)
            springs.append(k)

    def clear_overlap() -> bool:
        moved = False
        for i, a in enumerate(gids):
            ax, ay = centers[a]
            ahx, ahy = half[a]
            for b in gids[i + 1 :]:
                bx, by = centers[b]
                bhx, bhy = half[b]
                dx, dy = bx - ax, by - ay
                need_x = ahx + bhx + PACK_AIR
                need_y = ahy + bhy + PACK_AIR
                ox, oy = need_x - abs(dx), need_y - abs(dy)
                if ox <= 0 or oy <= 0:
                    continue
                if ox < oy:
                    p = ox / 2 + 1
                    sx = 1.0 if dx >= 0 else -1.0
                    if abs(dx) < 1e-6:
                        sx = 1.0 if a < b else -1.0
                    centers[a][0] -= p * sx
                    centers[b][0] += p * sx
                else:
                    p = oy / 2 + 1
                    sy = 1.0 if dy >= 0 else -1.0
                    if abs(dy) < 1e-6:
                        sy = 1.0 if a < b else -1.0
                    centers[a][1] -= p * sy
                    centers[b][1] += p * sy
                moved = True
        return moved

    for _ in range(80):
        # soft springs first: pull bridge-linked packs to touching distance so
        # the bridge node's shared lens lands right on the boundary (compact
        # hulls). Weak enough that clear_overlap still wins on conflicts.
        for a, b in springs:
            ax, ay = centers[a]
            bx, by = centers[b]
            dx, dy = bx - ax, by - ay
            dist = math.hypot(dx, dy) or 1.0
            rest = max(half[a][0] + half[b][0], half[a][1] + half[b][1]) + PACK_AIR
            if dist > rest * 1.05:
                f = 0.5 * (dist - rest)
                centers[a][0] += f * dx / dist
                centers[a][1] += f * dy / dist
                centers[b][0] -= f * dx / dist
                centers[b][1] -= f * dy / dist
        # then hard clear
        for _ in range(5):
            if not clear_overlap():
                break

    for _ in range(50):
        if not clear_overlap():
            break

    return {
        g: (centers[g][0] - half[g][0], centers[g][1] - half[g][1]) for g in gids
    }


def layout_project(project: dict[str, Any]) -> None:
    nodes: dict[str, dict] = project.get("nodes") or {}
    if not nodes:
        return

    declared = [
        g["id"]
        for g in (project.get("groups") or [])
        if isinstance(g, dict) and g.get("id")
    ]
    gid_set = set(declared)
    depths = node_depth(nodes)
    mem = membership(nodes, gid_set)

    used: list[str] = []
    seen: set[str] = set()
    for g in declared:
        if any(g in mem[n] for n in nodes) and g not in seen:
            used.append(g)
            seen.add(g)
    if any(UNGROUPED in mem[n] for n in nodes) and UNGROUPED not in seen:
        used.append(UNGROUPED)

    # Split nodes into single-group (exclusive) vs multi-group (bridge).
    # Exclusive nodes define each group's compact pack. Bridge nodes are NOT
    # buried inside their primary pack — burying them forces the *other*
    # group's hull to stretch across the map to reach them. Instead bridges
    # are placed afterwards in the shared lens *between* their groups' packs,
    # so every hull that owns a bridge only has to reach its own edge.
    exclusive_by_group: dict[str, list[str]] = {g: [] for g in used}
    bridges: list[tuple[str, list[str]]] = []
    for nid, gs in mem.items():
        if len(gs) == 1:
            exclusive_by_group.setdefault(gs[0], []).append(nid)
        else:
            bridges.append((nid, gs))

    # Groups with no exclusive members would otherwise have no footprint; seed
    # their pack with the bridge nodes whose primary group they are, so the
    # spring/overlap solver still gives them a place to live.
    pack_members: dict[str, list[str]] = {
        g: list(exclusive_by_group.get(g, [])) for g in used
    }
    for nid, gs in bridges:
        if not pack_members.get(gs[0]):
            pack_members.setdefault(gs[0], []).append(nid)

    local: dict[str, dict[str, tuple[float, float]]] = {}
    sizes: dict[str, tuple[float, float]] = {}
    lmin: dict[str, tuple[float, float]] = {}
    for g in used:
        loc = compact_grid(pack_members.get(g, []), depths, nodes)
        local[g] = loc
        if loc:
            xs = [p[0] for p in loc.values()]
            ys = [p[1] for p in loc.values()]
            lmin[g] = (min(xs), min(ys))
            sizes[g] = pack_wh(loc)
        else:
            lmin[g] = (0.0, 0.0)
            sizes[g] = (COL, ROW)

    multi_pairs = [
        (gs[0], gs[1])
        for _, gs in bridges
    ]
    origins = layout_pack_centers(used, sizes, multi_pairs)

    # Pack centres (used to place bridges in the shared lens between groups).
    centers: dict[str, tuple[float, float]] = {}
    for g in used:
        ox, oy = origins[g]
        w, h = sizes[g]
        centers[g] = (ox + w * 0.5, oy + h * 0.5)

    pos: dict[str, list[float]] = {}
    placed_in_pack: set[str] = set()
    for g in used:
        ox, oy = origins[g]
        loc = local[g]
        if not loc:
            continue
        mx0, my0 = lmin[g]
        for nid, (lx, ly) in loc.items():
            pos[nid] = [
                ox + (lx - mx0) + COL * 0.5,
                oy + (ly - my0) + ROW * 0.5,
            ]
            placed_in_pack.add(nid)

    # Bridge nodes: sit at the centroid of their groups' pack centres — i.e.
    # the shared edge where those hulls overlap by design. Adjacent packs put
    # this right on the boundary; both hulls stay compact.
    for nid, gs in bridges:
        if nid in placed_in_pack:
            continue
        valid = [g for g in gs if g in centers]
        if not valid:
            pos[nid] = [X0, Y0]
            continue
        cx = sum(centers[g][0] for g in valid) / len(valid)
        cy = sum(centers[g][1] for g in valid) / len(valid)
        pos[nid] = [cx, cy]

    for nid in nodes:
        if nid not in pos:
            pos[nid] = [X0, Y0]

    # Grid is already non-overlapping within packs; packs don't overlap.
    # Only residual: numerical ties — push any card pair apart (both can move a little).
    GAP_X, GAP_Y = COL, ROW
    ids = list(pos.keys())
    for _ in range(40):
        moved = False
        for i, a in enumerate(ids):
            for b in ids[i + 1 :]:
                dx = pos[b][0] - pos[a][0]
                dy = pos[b][1] - pos[a][1]
                if abs(dx) >= GAP_X or abs(dy) >= GAP_Y:
                    continue
                if GAP_X - abs(dx) <= GAP_Y - abs(dy):
                    p = (GAP_X - abs(dx) + 1) / 2
                    sx = 1.0 if dx >= 0 else -1.0
                    pos[a][0] -= p * sx
                    pos[b][0] += p * sx
                else:
                    p = (GAP_Y - abs(dy) + 1) / 2
                    sy = 1.0 if dy >= 0 else -1.0
                    pos[a][1] -= p * sy
                    pos[b][1] += p * sy
                moved = True
        if not moved:
            break

    min_x = min(p[0] for p in pos.values())
    min_y = min(p[1] for p in pos.values())
    sx, sy = X0 - min_x, Y0 - min_y
    for nid, (x, y) in pos.items():
        nodes[nid]["x"] = int(round(x + sx))
        nodes[nid]["y"] = int(round(y + sy))


def normalize_progress(project: dict[str, Any]) -> int:
    adjusted = 0
    for n in (project.get("nodes") or {}).values():
        if not isinstance(n, dict):
            continue
        todos = n.get("todos")
        if todos is None:
            n["todos"] = []
            todos = n["todos"]
            adjusted += 1
        if not isinstance(todos, list):
            continue
        md = bool(n.get("manualDone"))
        if todos:
            all_done = all(bool(t.get("done")) for t in todos if isinstance(t, dict))
            if md or all_done:
                if not md:
                    n["manualDone"] = True
                    adjusted += 1
                for t in todos:
                    if isinstance(t, dict) and not t.get("done"):
                        t["done"] = True
                        adjusted += 1
            elif md:
                n["manualDone"] = False
                adjusted += 1
        elif "manualDone" not in n:
            n["manualDone"] = False
            adjusted += 1
    return adjusted


def iter_projects(data: Any) -> list[tuple[str, dict]]:
    if isinstance(data, list):
        return [
            (p.get("id") or f"[{i}]", p)
            for i, p in enumerate(data)
            if isinstance(p, dict) and "nodes" in p
        ]
    if isinstance(data, dict):
        if isinstance(data.get("projects"), dict):
            return [(k, v) for k, v in data["projects"].items() if isinstance(v, dict)]
        if "nodes" in data:
            return [(data.get("id") or "project", data)]
    return []


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Tight Flowmap layout")
    ap.add_argument("path")
    ap.add_argument("-o", "--output")
    ap.add_argument("--in-place", action="store_true")
    ap.add_argument("--project")
    ap.add_argument("--normalize-progress", action="store_true")
    ap.add_argument("--no-layout", action="store_true")
    args = ap.parse_args(argv[1:])

    with open(args.path, encoding="utf-8") as f:
        data = json.load(f)

    projects = iter_projects(data)
    if not projects:
        print("ERROR: no projects found", file=sys.stderr)
        return 1

    for pid, proj in projects:
        if args.project and pid != args.project and proj.get("id") != args.project:
            continue
        if args.normalize_progress:
            print(
                f"{pid}: progress normalized ({normalize_progress(proj)})",
                file=sys.stderr,
            )
        if not args.no_layout:
            layout_project(proj)
            print(f"{pid}: laid out {len(proj.get('nodes') or {})} nodes", file=sys.stderr)

    out = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    if args.in_place:
        with open(args.path, "w", encoding="utf-8") as f:
            f.write(out)
        print(f"wrote {args.path}", file=sys.stderr)
    elif args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(out)
    else:
        sys.stdout.write(out)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
