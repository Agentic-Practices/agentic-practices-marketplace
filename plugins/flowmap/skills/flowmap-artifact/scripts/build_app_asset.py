#!/usr/bin/env python3
"""Flatten a bundled Flowmap.html into the artifact-safe asset this skill ships.

Run this only when the Flowmap app itself changes. Normal skill use consumes the
pre-built `assets/flowmap-app.html` and never touches this script.

Flowmap.html is a self-extracting bundle: base64 assets in a `__bundler/manifest`
script, the real page as a JSON string in a `__bundler/template` script, and a
`__bundler/ext_resources` map pointing CDN URLs at bundled copies. At runtime it
rebuilds the page using blob: URLs.

Blob URLs are the problem. A published Artifact runs under a strict CSP, so the
unpacking dance is exactly what we cannot ship. This script does that work ahead
of time and emits plain inline HTML:

  * react + react-dom inlined BEFORE the dc-runtime, so its loadReactUmd() takes
    the `if (w.React && w.ReactDOM) return` early exit and never reaches unpkg
  * dc-runtime inlined in place of its <script src="uuid">
  * fonts rewritten to data: URIs (font-src data: is allowed; blob: is not)
  * body-level content only, since the Artifact host supplies its own
    <!doctype>/<html>/<head>/<body> skeleton

Output carries three placeholders that build_flowmap_artifact.py fills in:
  __FLOWMAP_TITLE__   page + tab title
  __FLOWMAP_SEED__    the starter array, consumed by window.FLOWMAP_STARTERS
  __SELF_TEMPLATE__   base64 of this template, so a saved page can re-save itself
"""

from __future__ import annotations

import argparse
import base64
import gzip
import json
import re
import sys
from pathlib import Path

REACT_URL = "https://unpkg.com/react@18.3.1/umd/react.production.min.js"
REACT_DOM_URL = "https://unpkg.com/react-dom@18.3.1/umd/react-dom.production.min.js"

SAVE_OVERLAY = r"""
(function () {
  'use strict';
  // Save lives outside the app's React tree on purpose: the app is compiled from a
  // text/x-dc template, so patching a button into it would mean editing generated
  // markup that any future rebuild would overwrite. An overlay reads the same
  // localStorage the app already writes and stays valid across rebuilds.
  var KEY = 'flowmap.v2';
  var MARK_SELF = '__SELF' + '_TEMPLATE__';
  var MARK_SEED = '__FLOWMAP' + '_SEED__';

  var btn = document.createElement('button');
  btn.type = 'button';
  btn.hidden = true;
  btn.style.cssText = [
    'position:fixed', 'right:18px', 'bottom:18px', 'z-index:2147483000',
    'font:600 13px/1 -apple-system,BlinkMacSystemFont,Segoe UI,sans-serif',
    'padding:10px 16px', 'border-radius:10px', 'cursor:pointer',
    'background:#1b2431', 'color:#cfe0f3', 'border:1px solid #2f3d4f',
    'box-shadow:0 4px 14px rgba(0,0,0,.4)', 'display:flex', 'gap:8px',
    'align-items:center'
  ].join(';');
  btn.textContent = 'Save to artifact';

  var toast = document.createElement('div');
  toast.style.cssText = [
    'position:fixed', 'right:18px', 'bottom:66px', 'z-index:2147483000',
    'font:500 12px/1.4 -apple-system,BlinkMacSystemFont,Segoe UI,sans-serif',
    'padding:8px 13px', 'border-radius:9px', 'max-width:290px',
    'background:#1b2431', 'color:#9fb0c3', 'border:1px solid #2f3d4f',
    'opacity:0', 'transition:opacity .18s', 'pointer-events:none'
  ].join(';');

  var toastTimer = null;
  function say(msg, tone) {
    toast.textContent = msg;
    toast.style.color = tone === 'bad' ? '#ff9b8a' : (tone === 'good' ? '#8fe0a6' : '#9fb0c3');
    toast.style.opacity = '1';
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () { toast.style.opacity = '0'; }, 4200);
  }

  // #fm-self holds base64(gzip(template)). Storing a second copy of an 850 KB app
  // verbatim would nearly double the page; gzip brings it back to ~150 KB. The
  // blob this page shipped with is re-embedded byte-for-byte on save, so nothing
  // is ever re-compressed in the browser.
  async function decodeSelf(b64) {
    var bin = atob(b64);
    var bytes = new Uint8Array(bin.length);
    for (var i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
    if (typeof DecompressionStream === 'undefined') {
      throw new Error('this browser cannot decompress the page template');
    }
    var stream = new Blob([bytes]).stream().pipeThrough(new DecompressionStream('gzip'));
    var buf = await new Response(stream).arrayBuffer();
    return new TextDecoder().decode(buf);   // the app HTML is not pure ASCII
  }

  // The store keeps projects as a map; FLOWMAP_STARTERS wants an array, each entry
  // carrying the version the app already recorded in _seededV. Reusing that version
  // is what protects the viewer's edits: mergeStarters() skips a project whose
  // recorded version still matches, so a reopened page keeps localStorage rather
  // than being reset to the seed.
  function startersFromStore(store) {
    var seeded = store._seededV || {};
    return Object.keys(store.projects || {}).map(function (id) {
      var p = JSON.parse(JSON.stringify(store.projects[id]));
      delete p._blank;
      p.id = p.id || id;
      p.v = seeded[id] || 1;
      return p;
    });
  }

  async function buildDocument(starters) {
    var enc = document.getElementById('fm-self');
    if (!enc || !enc.textContent.trim()) throw new Error('self-template missing');
    var b64 = enc.textContent.trim();
    var tpl = await decodeSelf(b64);

    var seed = JSON.stringify(starters).replace(/</g, '\\u003c');
    var title = (document.title || 'Flowmap').replace(/[<&]/g, function (c) {
      return c === '<' ? '&lt;' : '&amp;';
    });

    // Self first, then seed: the base64 blob cannot contain the seed marker, but
    // user-authored node text could contain the self marker. Function replacers
    // keep `$&`-style sequences in that text from being treated as substitutions.
    var body = tpl
      .replace(MARK_SELF, function () { return b64; })
      .replace(MARK_SEED, function () { return seed; })
      .replace(/__FLOWMAP_TITLE__/g, function () { return title; });

    // publish() takes a complete document, whereas the first version was published
    // as body content and wrapped by the host. Wrapping here keeps every later
    // version self-contained and identical in shape.
    return '<!doctype html><html lang="en"><head><meta charset="utf-8">' +
      '<meta name="viewport" content="width=device-width, initial-scale=1">' +
      '<title>' + title + '</title></head><body>' + body + '</body></html>';
  }

  var busy = false;
  async function save(artifact) {
    if (busy) return;
    var raw;
    try { raw = localStorage.getItem(KEY); } catch (e) { raw = null; }
    if (!raw) { say('Nothing to save yet.', 'bad'); return; }

    var store;
    try { store = JSON.parse(raw); } catch (e) { say('Saved data is unreadable.', 'bad'); return; }
    if (!store || !store.projects) { say('Saved data is unreadable.', 'bad'); return; }

    busy = true;
    btn.disabled = true;
    btn.textContent = 'Saving…';
    try {
      await artifact.publish(await buildDocument(startersFromStore(store)));
      say('Saved. This link now carries your changes.', 'good');
      btn.textContent = 'Saved ✓';
      setTimeout(function () { btn.textContent = 'Save to artifact'; }, 2500);
    } catch (err) {
      var code = err && (err.code || err.name) || '';
      if (code === 'conflict') {
        // Someone else published first; every view reloads to their version.
        // Retrying would just fight them, so report and stop.
        say('Someone else saved first — reloading to their version.', 'bad');
      } else if (code === 'not_granted' || code === 'not_writer') {
        say('You have view-only access. Use Export to keep a copy.', 'bad');
        btn.hidden = true;
      } else {
        say('Save failed: ' + (err && err.message ? err.message : code || 'unknown'), 'bad');
      }
      btn.textContent = 'Save to artifact';
    } finally {
      busy = false;
      btn.disabled = false;
    }
  }

  // The app's own Export builds a Blob, points a detached <a download> at it and
  // calls .click(). The artifact viewer never grants pages download permission, so
  // that click silently does nothing — and Export is the escape hatch people need
  // to get their map back out. Route it through the downloads capability instead.
  //
  // The anchor is never in the document, so a delegated listener would not see the
  // click; patching the prototype is what catches it. And the blob URL cannot be
  // fetched back under `connect-src 'self'`, so remember the Blob at creation time
  // and read it directly.
  function interceptDownloads(downloads) {
    var blobs = new Map();
    var origCreate = URL.createObjectURL;
    URL.createObjectURL = function (obj) {
      var url = origCreate.call(URL, obj);
      if (obj instanceof Blob) {
        blobs.set(url, obj);
        if (blobs.size > 8) blobs.delete(blobs.keys().next().value);
      }
      return url;
    };

    var origClick = HTMLAnchorElement.prototype.click;
    HTMLAnchorElement.prototype.click = function () {
      var name = this.getAttribute('download');
      if (!name) return origClick.apply(this, arguments);
      var blob = blobs.get((this.href || '').split('#')[0]);
      if (!blob) return origClick.apply(this, arguments);

      blob.text().then(function (data) {
        return downloads.save({ filename: name, data: data });
      }).then(function () {
        say('Exported ' + name + '.', 'good');
      }).catch(function (err) {
        var code = err && err.code;
        if (code === 'declined') return;                    // viewer said no
        if (code === 'rate_limited') say('Too many prompts — try again shortly.', 'bad');
        else say('Export failed: ' + (err && err.message ? err.message : code || 'unknown'), 'bad');
      });
      return undefined;
    };
  }

  function mount() {
    document.body.appendChild(toast);
    document.body.appendChild(btn);
  }
  if (document.body) mount();
  else document.addEventListener('DOMContentLoaded', mount);

  // use() resolves late and never on this script's first run, so the button stays
  // hidden until we know saving is actually available. Opened as a local file or
  // exported elsewhere there is no viewer to answer, and the app's own Export
  // button remains the way out.
  if (window.claude && typeof window.claude.use === 'function') {
    window.claude.use('artifact').then(function (artifact) {
      if (!artifact || typeof artifact.publish !== 'function') return;
      btn.hidden = false;
      btn.addEventListener('click', function () { save(artifact); });
    }).catch(function () { /* stays hidden */ });

    // Only patch once we know saves are actually mediated here. Opened as a plain
    // file the native download works, and hijacking it would break Export.
    window.claude.use('downloads').then(function (downloads) {
      if (downloads && typeof downloads.save === 'function') interceptDownloads(downloads);
    }).catch(function () { /* leave native download alone */ });
  }
})();
"""


SCRIPT_RE = re.compile(r"(<script\b[^>]*>)(.*?)(</script>)", re.S | re.I)


def _js_escape(text: str) -> str:
    out = []
    for ch in text:
        if ord(ch) < 128:
            out.append(ch)
        elif ord(ch) > 0xFFFF:                      # astral, e.g. the padlock glyph
            cp = ord(ch) - 0x10000
            out.append(f"\\u{0xD800 + (cp >> 10):04x}\\u{0xDC00 + (cp & 0x3FF):04x}")
        else:
            out.append(f"\\u{ord(ch):04x}")
    return "".join(out)


def _html_escape(text: str) -> str:
    return "".join(c if ord(c) < 128 else f"&#x{ord(c):X};" for c in text)


def ascii_armor(html: str) -> str:
    """Re-encode every non-ASCII character so the page cannot be mis-decoded.

    The asset is body-level content, so it carries no <meta charset> of its own —
    the surrounding document decides the encoding, and a host that serves
    `text/html` without a charset leaves the browser guessing. Guessing Latin-1
    turns the app's check marks and dashes into mojibake. There are only ~79 such
    characters, so encoding them away makes the page correct under any charset
    instead of relying on the host to declare one.

    The escape has to respect context: the HTML parser resolves entities in text
    and attributes but not inside <script>, where a numeric escape is the JS form.
    """
    parts, pos = [], 0
    for m in SCRIPT_RE.finditer(html):
        parts.append(_html_escape(html[pos:m.start()]))
        parts.append(m.group(1))            # the tag itself is already ASCII
        parts.append(_js_escape(m.group(2)))
        parts.append(m.group(3))
        pos = m.end()
    parts.append(_html_escape(html[pos:]))
    return "".join(parts)


def die(msg: str) -> None:
    print(f"error: {msg}", file=sys.stderr)
    raise SystemExit(1)


def grab_script(src: str, kind: str) -> str:
    m = re.search(rf'<script type="__bundler/{kind}"[^>]*>(.*?)</script>', src, re.S)
    if not m:
        die(f"no __bundler/{kind} script found — is this a bundled Flowmap.html?")
    return m.group(1)


def decode_assets(manifest: dict) -> dict[str, bytes]:
    out = {}
    for uuid, entry in manifest.items():
        data = base64.b64decode(entry["data"])
        if entry.get("compressed"):
            data = gzip.decompress(data)
        out[uuid] = data
    return out


def inline_script(js: str, tag_id: str) -> str:
    # An inline script ends at the first `</script` the parser sees, wherever it
    # sits. None of the bundled sources contain one, so assert rather than paper
    # over it with an escape that is only valid inside a string literal.
    if "</script" in js.lower():
        die(f"{tag_id} contains a literal </script — cannot inline safely")
    return f'<script id="{tag_id}">\n{js}\n</script>'


FACE_RE = re.compile(r"@font-face\s*\{[^}]*\}")


def collapse_font_faces(css_html: str) -> tuple[str, int]:
    """Merge @font-face rules that differ only by font-weight.

    The Google Fonts CSS declares each subset three times, once per weight, and
    all three point at the same woff2. Inlining is per-rule, so left alone every
    font file would be base64'd three times over — around 340 KB of pure
    duplication in an 850 KB page. Since the rules share a src and a
    unicode-range, one rule carrying a `font-weight: min max` range renders
    identically: the same file still answers for every weight in the group.
    """
    groups: dict[tuple[str, ...], list[int]] = {}
    faces = list(FACE_RE.finditer(css_html))
    for i, m in enumerate(faces):
        block = m.group(0)
        fam = re.search(r"font-family:\s*'([^']+)'", block)
        src = re.search(r'url\("([0-9a-f-]{36})"\)', block)
        if not fam or not src:
            continue  # not a bundled font rule; leave it alone
        rng = re.search(r"unicode-range:\s*([^;]+);", block)
        style = re.search(r"font-style:\s*([^;]+);", block)
        key = (fam.group(1), src.group(1),
               rng.group(1).strip() if rng else "",
               style.group(1).strip() if style else "")
        groups.setdefault(key, []).append(i)

    drop: set[int] = set()
    rewrite: dict[int, str] = {}
    for idxs in groups.values():
        if len(idxs) < 2:
            continue
        weights = []
        for i in idxs:
            w = re.search(r"font-weight:\s*([^;]+);", faces[i].group(0))
            if w:
                weights.extend(int(x) for x in re.findall(r"\d+", w.group(1)))
        keep = idxs[0]
        if weights:
            rewrite[keep] = f"font-weight: {min(weights)} {max(weights)};"
        drop.update(idxs[1:])

    out, cursor, removed = [], 0, 0
    for i, m in enumerate(faces):
        out.append(css_html[cursor:m.start()])
        if i in drop:
            removed += 1
        else:
            block = m.group(0)
            if i in rewrite:
                block = re.sub(r"font-weight:\s*[^;]+;", rewrite[i], block, count=1)
            out.append(block)
        cursor = m.end()
    out.append(css_html[cursor:])
    return "".join(out), removed


def build(bundle_path: Path, out_path: Path) -> None:
    src = bundle_path.read_text(encoding="utf-8")

    manifest = json.loads(grab_script(src, "manifest"))
    template = json.loads(grab_script(src, "template"))
    ext_resources = json.loads(grab_script(src, "ext_resources"))

    assets = decode_assets(manifest)
    by_id = {e["id"]: e["uuid"] for e in ext_resources}

    for url in (REACT_URL, REACT_DOM_URL):
        if url not in by_id:
            die(f"bundle does not carry {url}; cannot inline React")

    react_js = assets[by_id[REACT_URL]].decode("utf-8")
    react_dom_js = assets[by_id[REACT_DOM_URL]].decode("utf-8")

    # The dc-runtime is the only <script src="uuid"> in the template's head.
    m = re.search(r'<script src="([0-9a-f-]{36})"></script>', template)
    if not m:
        die("could not locate the dc-runtime script tag in the template")
    runtime_uuid = m.group(1)
    runtime_js = assets[runtime_uuid].decode("utf-8")

    # The runtime resolves its component by re-fetching the page and scanning the
    # source text for the first `<x-dc` and the last `</x-dc>`. That is harmless
    # while the runtime is a separate file, but inlining it drops its own source
    # into the page — including the `/<x-dc.../` matcher and the string
    # "has no <x-dc> block". The scan then locks onto those and renders a slice of
    # the runtime's source instead of the app.
    #
    # All three occurrences sit inside a regex or a string literal, where \x3c is
    # just another way to spell `<`. Escaping them leaves runtime behaviour
    # identical while making the real <x-dc> block the only one findable in text.
    runtime_js = runtime_js.replace("</x-dc>", "\\x3c/x-dc>").replace("<x-dc", "\\x3cx-dc")
    if re.search(r"(?<!\\x3c)<x-dc", runtime_js):
        die("runtime still carries a literal <x-dc after escaping")

    body = re.search(r"<body[^>]*>(.*)</body>", template, re.S)
    if not body:
        die("template has no <body>")
    body_html = body.group(1)

    body_html, dropped_faces = collapse_font_faces(body_html)

    # Fonts are referenced from @font-face inside <helmet>. data: keeps them under
    # the artifact CSP, which permits font-src data: but not blob:.
    for uuid, data in assets.items():
        if uuid == runtime_uuid:
            continue
        mime = manifest[uuid]["mime"]
        if not mime.startswith("font/"):
            continue
        uri = f"data:{mime};base64,{base64.b64encode(data).decode('ascii')}"
        body_html = body_html.replace(uuid, uri)

    leftover = re.findall(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", body_html)
    if leftover:
        die(f"unresolved asset references remain: {sorted(set(leftover))[:3]}")

    parts = [
        "<title>__FLOWMAP_TITLE__</title>",
        inline_script(react_js, "fm-react"),
        inline_script(react_dom_js, "fm-react-dom"),
        # Set before the runtime so the global exists by the time the app mounts
        # and calls applyStarters().
        '<script id="fm-seed">window.FLOWMAP_STARTERS = __FLOWMAP_SEED__;</script>',
        inline_script(runtime_js, "fm-runtime"),
        body_html.strip(),
        '<script type="text/plain" id="fm-self">__SELF_TEMPLATE__</script>',
        inline_script(SAVE_OVERLAY, "fm-save"),
    ]
    out = ascii_armor("\n".join(parts) + "\n")

    non_ascii = [c for c in out if ord(c) > 127]
    if non_ascii:
        die(f"{len(non_ascii)} non-ASCII characters survived the armor pass")

    for marker in ("__FLOWMAP_TITLE__", "__FLOWMAP_SEED__", "__SELF_TEMPLATE__"):
        if out.count(marker) < 1:
            die(f"placeholder {marker} missing from output")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(out, encoding="utf-8")
    kb = len(out.encode("utf-8")) / 1024
    print(f"wrote {out_path} ({kb:.0f} KB)")
    print(f"  react {len(react_js)/1024:.0f} KB · react-dom {len(react_dom_js)/1024:.0f} KB "
          f"· runtime {len(runtime_js)/1024:.0f} KB · app {len(body_html)/1024:.0f} KB")
    print(f"  merged {dropped_faces} duplicate @font-face rules")


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("bundle", type=Path, help="path to the bundled Flowmap.html")
    ap.add_argument("-o", "--output", type=Path,
                    default=Path(__file__).resolve().parent.parent / "assets" / "flowmap-app.html")
    args = ap.parse_args(argv[1:])
    if not args.bundle.is_file():
        die(f"no such file: {args.bundle}")
    build(args.bundle, args.output)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
