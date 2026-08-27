#!/usr/bin/env python3
"""Turn a Flowmap JSON file into a publishable, self-contained artifact page.

    python3 build_flowmap_artifact.py map.flowmap.json -o map.flowmap.html

Reads `assets/flowmap-app.html` (the pre-flattened app) and fills its three
placeholders: the title, the starter array the app auto-loads on open, and a
gzipped copy of the template itself so the page's Save button can republish a new
version of the page without help from the agent.

Accepts any shape the Flowmap app itself accepts — a full store
(`{projects, currentId}`), a bare project (`{id, name, groups, nodes}`), or an
array of projects — and always emits the starter-array form the auto-load hook
expects.
"""

from __future__ import annotations

import argparse
import base64
import gzip
import json
import sys
from pathlib import Path

MARK_TITLE = "__FLOWMAP_TITLE__"
MARK_SEED = "__FLOWMAP_SEED__"
MARK_SELF = "__SELF_TEMPLATE__"

MAX_BYTES = 16 * 1024 * 1024


def die(msg: str) -> None:
    print(f"error: {msg}", file=sys.stderr)
    raise SystemExit(1)


def projects_from(doc: object) -> list[dict]:
    """Normalize any accepted input shape into a list of project objects."""
    if isinstance(doc, dict) and isinstance(doc.get("projects"), dict):
        out = []
        for pid, proj in doc["projects"].items():
            if not isinstance(proj, dict):
                continue
            proj.setdefault("id", pid)
            out.append(proj)
        return out
    if isinstance(doc, list):
        return [p for p in doc if isinstance(p, dict) and isinstance(p.get("nodes"), dict)]
    if isinstance(doc, dict) and isinstance(doc.get("nodes"), dict):
        return [doc]
    die("input is not a Flowmap store, project, or project array")
    return []


def to_starters(projects: list[dict], version: int) -> list[dict]:
    starters = []
    for proj in projects:
        p = dict(proj)
        p.pop("_blank", None)
        if not p.get("id"):
            die("a project is missing its `id`")
        if not p.get("name"):
            p["name"] = "Flowmap"
        # `v` drives the app's reseed check. Holding it steady across republishes is
        # what lets a viewer's saved progress survive: mergeStarters() skips any
        # project whose recorded version still matches, leaving localStorage intact.
        # Raising it is the deliberate way to overwrite an older map.
        p["v"] = int(p.get("v", version))
        starters.append(p)
    return starters


def js_json(value: object) -> str:
    # Two hazards, both handled by escaping rather than trusting the input.
    # `ensure_ascii` keeps the page pure ASCII so it renders correctly even if the
    # host serves it without declaring a charset — node text is user-authored and
    # routinely contains dashes, quotes and accents. Escaping `<` stops a literal
    # `</script` inside any node's text from closing the block early.
    return json.dumps(value, ensure_ascii=True).replace("<", "\\u003c")


def build(app_html: str, starters: list[dict], title: str) -> str:
    for marker in (MARK_TITLE, MARK_SEED, MARK_SELF):
        if marker not in app_html:
            die(f"app asset is missing the {marker} placeholder — rebuild it with build_app_asset.py")

    # The page carries a gzipped copy of its own unfilled template. Compressing it
    # keeps the round trip honest without paying twice for a 487 KB app.
    packed = base64.b64encode(gzip.compress(app_html.encode("utf-8"), 9)).decode("ascii")

    safe_title = "".join(
        c if 32 <= ord(c) < 128 and c not in "&<>" else f"&#x{ord(c):X};"
        for c in title
    )

    # Self before seed: base64 cannot contain the seed marker, but a node's own text
    # could contain the self marker. str.replace takes no `$`-substitutions, so
    # user text passes through literally.
    out = app_html.replace(MARK_SELF, packed, 1)
    out = out.replace(MARK_SEED, js_json(starters), 1)
    out = out.replace(MARK_TITLE, safe_title)
    return out


def main(argv: list[str]) -> int:
    here = Path(__file__).resolve().parent
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("json", type=Path, help="the .flowmap.json file")
    ap.add_argument("-o", "--output", type=Path, help="output .html (default: alongside input)")
    ap.add_argument("-t", "--title", help="page + tab title (default: the project name)")
    ap.add_argument("--version", type=int, default=1,
                    help="starter version for projects that lack one; raise it to force a reseed "
                         "that overwrites a viewer's saved edits (default: 1)")
    ap.add_argument("--app", type=Path, default=here.parent / "assets" / "flowmap-app.html",
                    help="the flattened app asset")
    args = ap.parse_args(argv[1:])

    if not args.json.is_file():
        die(f"no such file: {args.json}")
    if not args.app.is_file():
        die(f"app asset not found: {args.app}\n"
            f"       rebuild it: python3 {here / 'build_app_asset.py'} /path/to/Flowmap.html")

    try:
        doc = json.loads(args.json.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        die(f"{args.json} is not valid JSON: {e}")

    projects = projects_from(doc)
    if not projects:
        die("no projects found in the input")
    starters = to_starters(projects, args.version)

    title = args.title or starters[0]["name"]
    out_path = args.output or args.json.with_suffix("").with_suffix(".flowmap.html")

    page = build(args.app.read_text(encoding="utf-8"), starters, title)
    size = len(page.encode("utf-8"))
    if size > MAX_BYTES:
        die(f"page is {size/1024/1024:.1f} MB, over the 16 MB artifact limit")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(page, encoding="utf-8")

    nodes = sum(len(p.get("nodes") or {}) for p in starters)
    groups = sum(len(p.get("groups") or []) for p in starters)
    print(f"wrote {out_path} ({size/1024/1024:.2f} MB)")
    print(f"  {len(starters)} project(s) · {nodes} nodes · {groups} groups "
          f"· seed v{starters[0]['v']}")
    print(f"  title: {title}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
