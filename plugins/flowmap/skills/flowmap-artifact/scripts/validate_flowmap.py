#!/usr/bin/env python3
"""Validate Flowmap JSON against the Flowmap grouped Import contract."""

from __future__ import annotations

import json
import re
import sys
from typing import Any

HEX = re.compile(r"^#[0-9A-Fa-f]{6}$")
SIZE = {"S", "M", "L"}
NEED_MODE = {"all", "any", None}


def err(msg: str) -> None:
    print(f"ERROR: {msg}")


def warn(msg: str) -> None:
    print(f"WARN:  {msg}")


def cycle_exists(nodes: dict[str, dict]) -> list[str]:
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {nid: WHITE for nid in nodes}
    parent: dict[str, str | None] = {nid: None for nid in nodes}

    def dfs(u: str) -> list[str] | None:
        color[u] = GRAY
        for v in nodes[u].get("needs") or []:
            if v not in nodes:
                continue
            if color[v] == GRAY:
                path = [v, u]
                cur = u
                while cur != v and parent[cur] is not None:
                    cur = parent[cur]  # type: ignore
                    path.append(cur)
                path.reverse()
                return path
            if color[v] == WHITE:
                parent[v] = u
                found = dfs(v)
                if found:
                    return found
        color[u] = BLACK
        return None

    for nid in nodes:
        if color[nid] == WHITE:
            found = dfs(nid)
            if found:
                return found
    return []


def validate_project(p: dict[str, Any], label: str) -> int:
    errors = 0
    if not isinstance(p, dict):
        err(f"{label}: project must be an object")
        return 1

    pid = p.get("id")
    if not pid:
        err(f"{label}: missing id")
        errors += 1
    if not p.get("name"):
        warn(f"{label}: missing name")

    # Prefer groups; allow tracks only with migration warning
    groups = p.get("groups")
    if groups is None and isinstance(p.get("tracks"), list):
        warn(f"{label}: has tracks (v1); prefer groups for new maps — Import migrates")
        groups = [
            {"id": t.get("id"), "name": t.get("name"), "color": t.get("color")}
            for t in p["tracks"]
            if isinstance(t, dict)
        ]
    if not isinstance(groups, list):
        err(f"{label}: groups must be an array (Import needs groups or migratable tracks)")
        return errors + 1

    group_ids: set[str] = set()
    for i, g in enumerate(groups):
        if not isinstance(g, dict):
            err(f"{label}: groups[{i}] not an object")
            errors += 1
            continue
        gid = g.get("id")
        if not gid:
            err(f"{label}: groups[{i}] missing id")
            errors += 1
            continue
        if gid in group_ids:
            err(f"{label}: duplicate group id {gid!r}")
            errors += 1
        group_ids.add(gid)
        if not g.get("name"):
            warn(f"{label}: group {gid!r} missing name")
        color = g.get("color")
        if not color or not HEX.match(str(color)):
            err(f"{label}: group {gid!r} color must be #RRGGBB")
            errors += 1

    nodes = p.get("nodes")
    if not isinstance(nodes, dict):
        err(f"{label}: nodes must be an object map")
        return errors + 1

    if not nodes:
        warn(f"{label}: no nodes")

    roots = 0
    for key, n in nodes.items():
        if not isinstance(n, dict):
            err(f"{label}: node {key!r} not an object")
            errors += 1
            continue
        nid = n.get("id")
        if nid != key:
            err(f"{label}: node key {key!r} != id {nid!r}")
            errors += 1
        if not n.get("title"):
            err(f"{label}: node {key!r} missing title")
            errors += 1
        size = n.get("size", "S")
        if size not in SIZE:
            err(f"{label}: node {key!r} size must be S|M|L")
            errors += 1
        if "desc" not in n:
            err(f"{label}: node {key!r} missing desc (use \"\")")
            errors += 1
        gref = n.get("groups")
        if gref is None and n.get("track"):
            warn(f"{label}: node {key!r} uses track; prefer groups: [track]")
            gref = [n["track"]]
        if gref is None:
            err(f"{label}: node {key!r} missing groups array (render/import requires it)")
            errors += 1
            gref = []
        if not isinstance(gref, list):
            err(f"{label}: node {key!r} groups must be array")
            errors += 1
            gref = []
        for gid in gref:
            if gid not in group_ids:
                err(f"{label}: node {key!r} references unknown group {gid!r}")
                errors += 1
        needs = n.get("needs")
        if needs is None:
            err(f"{label}: node {key!r} missing needs array")
            errors += 1
            needs = []
        if not isinstance(needs, list):
            err(f"{label}: node {key!r} needs must be array")
            errors += 1
            needs = []
        if not needs:
            roots += 1
        for dep in needs:
            if dep == key:
                err(f"{label}: node {key!r} needs itself")
                errors += 1
            elif dep not in nodes:
                err(f"{label}: node {key!r} needs unknown {dep!r}")
                errors += 1
        nm = n.get("needMode")
        if nm is not None and nm not in ("all", "any"):
            err(f"{label}: node {key!r} needMode must be 'all' or 'any'")
            errors += 1
        todos = n.get("todos")
        if todos is None:
            err(f"{label}: node {key!r} missing todos array — Import/render requires []")
            errors += 1
            todos = []
        if not isinstance(todos, list):
            err(f"{label}: node {key!r} todos must be array")
            errors += 1
            todos = []
        seen_td: set[str] = set()
        for t in todos:
            if not isinstance(t, dict):
                err(f"{label}: node {key!r} todo not object")
                errors += 1
                continue
            tid = t.get("id")
            if not tid:
                err(f"{label}: node {key!r} todo missing id")
                errors += 1
            elif tid in seen_td:
                err(f"{label}: node {key!r} duplicate todo id {tid!r}")
                errors += 1
            else:
                seen_td.add(tid)
            if "text" not in t:
                warn(f"{label}: node {key!r} todo {tid!r} missing text")
            if "done" not in t:
                err(f"{label}: node {key!r} todo {tid!r} missing done boolean")
                errors += 1
        if "manualDone" not in n:
            err(f"{label}: node {key!r} missing manualDone boolean")
            errors += 1
        # Progress consistency (skill rules)
        md = bool(n.get("manualDone"))
        todo_flags = [
            bool(t.get("done"))
            for t in todos
            if isinstance(t, dict)
        ]
        if todo_flags:
            all_td = all(todo_flags)
            if md and not all_td:
                err(
                    f"{label}: node {key!r} is manualDone but has unchecked todos "
                    f"(mark todos done or set manualDone false)"
                )
                errors += 1
            if all_td and not md:
                warn(
                    f"{label}: node {key!r} has all todos done but manualDone is false "
                    f"(prefer manualDone true for finished nodes)"
                )
        for axis in ("x", "y"):
            if axis in n and n[axis] is not None and not isinstance(n[axis], (int, float)):
                err(f"{label}: node {key!r} {axis} must be number or null")
                errors += 1

    if nodes and roots == 0:
        err(f"{label}: no root nodes (every node has needs) — map cannot start")
        errors += 1

    cyc = cycle_exists(nodes) if isinstance(nodes, dict) else []
    if cyc:
        err(f"{label}: dependency cycle: {' -> '.join(cyc)}")
        errors += 1

    ncount = len(nodes) if isinstance(nodes, dict) else 0
    if ncount > 70:
        warn(f"{label}: {ncount} nodes — consider splitting into multiple maps")

    status = "OK" if errors == 0 else "FAIL"
    print(f"{status} {label}: {len(group_ids)} groups, {ncount} nodes, {roots} roots, {errors} errors")
    return errors


def classify_top(data: Any) -> str:
    if isinstance(data, list):
        return "array"
    if isinstance(data, dict):
        if "projects" in data:
            return "store"
        if "nodes" in data:
            return "bare-project"
    return "unknown"


def normalize_projects(data: Any) -> list[tuple[str, dict]]:
    if isinstance(data, list):
        out = []
        for i, item in enumerate(data):
            if isinstance(item, dict) and "nodes" in item:
                out.append((item.get("id") or f"array[{i}]", item))
        return out
    if not isinstance(data, dict):
        return []
    if "projects" in data and isinstance(data["projects"], dict):
        return [(k, v) for k, v in data["projects"].items() if isinstance(v, dict)]
    if "nodes" in data:
        return [(data.get("id") or "project", data)]
    return []


def validate_store_wrapper(data: dict[str, Any]) -> int:
    errors = 0
    projects = data.get("projects")
    if not isinstance(projects, dict):
        err("store: projects must be an object")
        return 1
    if not projects:
        err("store: projects is empty")
        errors += 1
    cid = data.get("currentId")
    if cid is None:
        warn("store: currentId is null — app will pick first project")
    elif cid not in projects:
        err(f"store: currentId {cid!r} not in projects — Import now repairs, still fix this")
        errors += 1
    if "_seededV" not in data:
        warn("store: missing _seededV (emit {{}} for export parity)")
    return errors


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("Usage: validate_flowmap.py <file.json> [more.json ...]", file=sys.stderr)
        return 2
    total = 0
    for path in argv[1:]:
        print(f"\n=== {path} ===")
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            err(f"cannot read JSON: {e}")
            total += 1
            continue

        shape = classify_top(data)
        print(f"shape: {shape}")
        if shape == "unknown":
            err("not a Flowmap store, bare project, or starter array — Import will reject")
            total += 1
            continue
        if shape == "bare-project":
            warn("bare project is importable, but prefer full store {projects, currentId, _seededV}")
        if shape == "store":
            total += validate_store_wrapper(data)  # type: ignore[arg-type]

        projects = normalize_projects(data)
        if not projects:
            err("no projects with nodes found")
            total += 1
            continue
        for label, proj in projects:
            total += validate_project(proj, str(label))
    print(f"\nTotal errors: {total}")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
