#!/usr/bin/env python3
"""Check that everything this skill needs is present, and repair what can be.

    python3 preflight.py            # check, report, exit 0 / 2 / 3
    python3 preflight.py --json     # same, machine-readable
    python3 preflight.py --install  # perform the repairs listed by the check
    python3 preflight.py --force    # ignore the "already checked" stamp

Exit codes carry the decision, so a caller never has to parse prose:

    0  ready — nothing to do
    2  repairable — every problem has a fix this script can perform.
       ASK THE USER before running --install; it changes files on disk.
    3  blocked — something is wrong that this script cannot fix
       (report it; do not attempt the build)

Normally the only dependency is Python itself, which is already running by the
time this file executes. The checks that matter are therefore about the plugin's
own payload: an interrupted clone, a partial copy, or a stripped asset would
otherwise surface much later as a confusing build or render failure.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

MIN_PYTHON = (3, 9)
SKILL_DIR = Path(__file__).resolve().parent.parent
MANIFEST = SKILL_DIR / "manifest.json"

APP_ASSET = "assets/flowmap-app.html"
APP_SOURCE = "assets/flowmap-source.html"
PLACEHOLDERS = ("__FLOWMAP_TITLE__", "__FLOWMAP_SEED__", "__SELF_TEMPLATE__")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def stamp_path(manifest: dict) -> Path:
    """Where the 'already checked this exact payload' marker lives.

    Keyed by the manifest digest, so a plugin update invalidates it automatically
    and the next run re-checks. It lives in the user's cache dir rather than the
    plugin directory because an installed plugin may sit on a read-only path.
    """
    base = os.environ.get("XDG_CACHE_HOME") or (Path.home() / ".cache")
    key = hashlib.sha256(
        json.dumps(manifest.get("files", {}), sort_keys=True).encode()
    ).hexdigest()[:16]
    return Path(base) / "flowmap-artifact" / f"preflight-{key}.ok"


# ---------------------------------------------------------------- checks

def check_python(problems: list[dict]) -> None:
    if sys.version_info < MIN_PYTHON:
        problems.append({
            "id": "python-version",
            "severity": "blocked",
            "detail": (f"Python {'.'.join(map(str, MIN_PYTHON))}+ required, "
                       f"running {sys.version.split()[0]}"),
            "fix": "Install a newer Python 3 and re-run. Nothing else is needed — "
                   "this skill uses only the standard library.",
        })


def check_files(manifest: dict, problems: list[dict], deep: bool) -> None:
    files = manifest.get("files", {})
    if not files:
        problems.append({
            "id": "manifest-empty",
            "severity": "blocked",
            "detail": "manifest.json lists no files",
            "fix": "Regenerate it with: python3 scripts/preflight.py --write-manifest",
        })
        return

    have_source = (SKILL_DIR / APP_SOURCE).is_file()

    for rel, meta in sorted(files.items()):
        path = SKILL_DIR / rel
        # The app asset is the one file that can be rebuilt from what ships
        # alongside it, so treat its absence as repairable rather than fatal.
        repairable = rel == APP_ASSET and have_source

        if not path.is_file():
            problems.append({
                "id": f"missing:{rel}",
                "severity": "repairable" if repairable else "blocked",
                "detail": f"missing: {rel}",
                "fix": (f"Rebuild it from the bundled {APP_SOURCE}."
                        if repairable else
                        "Reinstall the plugin — this file ships with it and cannot "
                        "be reconstructed."),
            })
            continue

        size = path.stat().st_size
        if meta.get("bytes") is not None and size != meta["bytes"]:
            problems.append({
                "id": f"size:{rel}",
                "severity": "repairable" if repairable else "blocked",
                "detail": f"{rel} is {size} bytes, expected {meta['bytes']}",
                "fix": (f"Rebuild it from the bundled {APP_SOURCE}."
                        if repairable else "Reinstall the plugin."),
            })
            continue

        if deep and meta.get("sha256") and sha256(path) != meta["sha256"]:
            problems.append({
                "id": f"hash:{rel}",
                "severity": "repairable" if repairable else "blocked",
                "detail": f"{rel} does not match its recorded checksum",
                "fix": (f"Rebuild it from the bundled {APP_SOURCE}."
                        if repairable else "Reinstall the plugin."),
            })


def check_placeholders(problems: list[dict]) -> None:
    """The asset is useless without its three substitution points.

    A file can be the right size and still be the wrong thing — this catches an
    asset that was hand-edited or replaced with an already-built page.
    """
    path = SKILL_DIR / APP_ASSET
    if not path.is_file():
        return
    text = path.read_text(encoding="utf-8", errors="replace")
    missing = [p for p in PLACEHOLDERS if p not in text]
    if missing:
        problems.append({
            "id": "placeholders",
            "severity": "repairable" if (SKILL_DIR / APP_SOURCE).is_file() else "blocked",
            "detail": f"{APP_ASSET} is missing placeholder(s): {', '.join(missing)}",
            "fix": f"Rebuild it from the bundled {APP_SOURCE}.",
        })


def run_checks(deep: bool) -> tuple[list[dict], dict]:
    problems: list[dict] = []
    check_python(problems)
    manifest = {}
    if not MANIFEST.is_file():
        problems.append({
            "id": "manifest-missing",
            "severity": "blocked",
            "detail": "manifest.json not found beside SKILL.md",
            "fix": "Reinstall the plugin.",
        })
    else:
        try:
            manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            problems.append({
                "id": "manifest-invalid",
                "severity": "blocked",
                "detail": f"manifest.json is not valid JSON: {e}",
                "fix": "Reinstall the plugin.",
            })
        else:
            check_files(manifest, problems, deep)
            check_placeholders(problems)
    return problems, manifest


# ---------------------------------------------------------------- repair

def repair(problems: list[dict]) -> int:
    fixable = [p for p in problems if p["severity"] == "repairable"]
    if not fixable:
        print("Nothing to repair.")
        return 0

    # Every repairable problem currently has the same remedy: regenerate the app
    # asset from the source bundle that ships next to it.
    src = SKILL_DIR / APP_SOURCE
    if not src.is_file():
        print(f"error: cannot repair — {APP_SOURCE} is missing too", file=sys.stderr)
        return 3

    builder = SKILL_DIR / "scripts" / "build_app_asset.py"
    print(f"Rebuilding {APP_ASSET} from {APP_SOURCE} ...")
    result = subprocess.run(
        [sys.executable, str(builder), str(src), "-o", str(SKILL_DIR / APP_ASSET)],
        capture_output=True, text=True,
    )
    sys.stdout.write(result.stdout)
    if result.returncode != 0:
        sys.stderr.write(result.stderr)
        print("error: rebuild failed", file=sys.stderr)
        return 3

    problems, _ = run_checks(deep=True)
    if problems:
        print("Repair ran but problems remain:", file=sys.stderr)
        for p in problems:
            print(f"  - {p['detail']}", file=sys.stderr)
        return 3
    print("Repaired. All checks pass.")
    return 0


def write_manifest() -> int:
    """Maintainer helper: record every shipped file's size and checksum."""
    files = {}
    for path in sorted(SKILL_DIR.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(SKILL_DIR).as_posix()
        if rel == "manifest.json" or "__pycache__" in rel or rel.endswith(".pyc"):
            continue
        files[rel] = {"bytes": path.stat().st_size, "sha256": sha256(path)}
    MANIFEST.write_text(json.dumps({
        "skill": "flowmap-artifact",
        "python": {"minimum": ".".join(map(str, MIN_PYTHON))},
        "files": files,
    }, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {MANIFEST} ({len(files)} files)")
    return 0


# ---------------------------------------------------------------- main

def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json", action="store_true", help="machine-readable report")
    ap.add_argument("--install", action="store_true",
                    help="perform the repairs (ask the user first — it writes files)")
    ap.add_argument("--force", action="store_true", help="ignore the first-run stamp")
    ap.add_argument("--quick", action="store_true",
                    help="skip checksums; check presence and size only")
    ap.add_argument("--write-manifest", action="store_true", help=argparse.SUPPRESS)
    args = ap.parse_args(argv[1:])

    if args.write_manifest:
        return write_manifest()

    problems, manifest = run_checks(deep=not args.quick)

    stamp = stamp_path(manifest) if manifest else None
    # The stamp is what makes this a first-run check rather than a tax on every
    # invocation: once this exact payload has passed, later runs exit immediately.
    if not problems and stamp:
        try:
            stamp.parent.mkdir(parents=True, exist_ok=True)
            stamp.write_text("ok\n", encoding="utf-8")
        except OSError:
            pass  # a read-only cache just means we check again next time

    if args.install:
        return repair(problems)

    blocked = [p for p in problems if p["severity"] == "blocked"]
    repairable = [p for p in problems if p["severity"] == "repairable"]
    status = "ready" if not problems else ("blocked" if blocked else "repairable")

    if args.json:
        print(json.dumps({
            "status": status,
            "python": sys.version.split()[0],
            "skill_dir": str(SKILL_DIR),
            "first_run": bool(stamp and not stamp.exists()),
            "problems": problems,
        }, indent=2))
    elif status == "ready":
        print(f"flowmap-artifact: ready (Python {sys.version.split()[0]}, "
              f"{len(manifest.get('files', {}))} files verified)")
    else:
        print(f"flowmap-artifact: {status}\n")
        for p in problems:
            print(f"  [{p['severity']}] {p['detail']}")
            print(f"      fix: {p['fix']}")
        if repairable and not blocked:
            print("\nRepairable without network access. With the user's approval, run:")
            print("  python3 scripts/preflight.py --install")

    return 0 if status == "ready" else (3 if blocked else 2)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
