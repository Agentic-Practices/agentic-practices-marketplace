---
description: Adapt the bundled reference statusline to this machine's OS and wire it into Claude Code settings.
argument-hint: "(no arguments)"
allowed-tools: Bash, Read, Edit, Write
---

# /setupstatusline

Set up a context-window "battery" status line for the user, based on the reference
design bundled with this plugin, adapted to **their** operating system, and wired into
their Claude Code settings.

The reference script lives at:

```
${CLAUDE_PLUGIN_ROOT}/reference/statusline-command.sh
```

It is a Bash script that reads Claude Code's status JSON on stdin and prints one line:
a color-coded model badge, the current directory + git status, and a battery bar showing
how full the context window is. It depends on `bash`, `jq`, and `git`.

Work through these steps **in order**. Do not write or change any file until after the
user confirms at step 5.

## 1. Detect the environment

- Determine the OS: run `uname -s` (Darwin = macOS, Linux = Linux). If that fails or you
  are on Windows, treat it as Windows.
- Note the shell and whether a Bash environment is available. On Windows, Bash means Git
  Bash or WSL — plain `cmd`/PowerShell cannot run this script.
- Find the user's Claude Code config directory (normally `~/.claude`).

## 2. Read the reference

Read `${CLAUDE_PLUGIN_ROOT}/reference/statusline-command.sh` in full. This is the design
to reproduce. Preserve its visual identity: the model symbol/colors (◆ Opus, ◇ Sonnet,
○ Haiku), the directory + git-status segment, and the battery bar with its
green/yellow/red thresholds.

## 3. Check dependencies

Check that `jq` and `git` are on PATH (`command -v jq`, `command -v git`).

- If a dependency is missing, tell the user and give the install command for their OS
  (macOS: `brew install jq`; Debian/Ubuntu: `sudo apt install jq`; Fedora: `sudo dnf
  install jq`; Windows: `winget install jqlang.jq` or via Git Bash). Do not silently
  continue with a broken statusline.
- On Windows, confirm the user has Git Bash or WSL, since the reference is a Bash script.

## 4. Adapt for the OS

Produce an adapted copy of the script tailored to the detected OS. Keep the logic and
appearance identical; only change what the OS requires, for example:

- **macOS / Linux** — the reference already runs as-is. Keep it unchanged unless a check
  in step 3 revealed something to adjust.
- **Windows (Git Bash / WSL)** — keep the Bash script, but make sure paths in
  `settings.json` and the `command` use a form that environment can execute
  (e.g. a WSL path or a Git Bash-style path), and note the dependency requirements.

Do not invent new features. If nothing needs to change for the user's OS, say so and use
the reference verbatim.

## 5. Show the plan and confirm

Before touching anything, show the user exactly what you will do:

- The target path for the script (e.g. `~/.claude/statusline-command.sh`).
- The exact `settings.json` change:
  ```json
  "statusLine": { "type": "command", "command": "bash ~/.claude/statusline-command.sh" }
  ```
- Whether an existing statusline or script will be replaced (and that you will back it up).

Ask the user to confirm. Only proceed on an explicit yes.

## 6. Write the script

Write the adapted script to the chosen path (default `~/.claude/statusline-command.sh`)
and make it executable (`chmod +x`). If a file already exists there, back it up first
(e.g. copy to `<path>.bak-<something-stable>`).

## 7. Wire it into settings

Update the user's `settings.json` (normally `~/.claude/settings.json`) to point
`statusLine` at the script. This must be a **read-modify-write**: preserve every existing
key — only add or replace the `statusLine` object. If `settings.json` does not exist,
create a minimal one containing just `statusLine`. If it exists, back it up before editing.

The `statusline-setup` agent may be used to perform the settings edit if that is cleaner —
but the requirement is the same: never clobber unrelated settings.

## 8. Report

Tell the user what changed:

- The script path and that it is executable.
- The `settings.json` change and where the backup (if any) is.
- That the statusline appears on the next prompt render (they may need to submit a message).
- How to revert: restore the backup, or remove the `statusLine` key from `settings.json`.
