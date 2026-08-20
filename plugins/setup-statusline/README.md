# setup-statusline

Gives you a context-window "battery" status line for Claude Code — adapted to your
operating system and wired into your settings — with one command.

## What it does

Run:

```
/setupstatusline
```

Claude will:

1. Detect your OS and shell, and locate your Claude Code config directory.
2. Read the reference statusline bundled with this plugin (`reference/statusline-command.sh`).
3. Check that its dependencies (`jq`, `git`, a Bash environment) are present, and offer
   install hints if not.
4. Adapt the script for your OS.
5. **Show you the plan and ask you to confirm** before changing anything.
6. Write the script into your config directory and make it executable (backing up any
   existing file).
7. Wire it into your `settings.json` `statusLine` key without clobbering your other
   settings.

## What the statusline shows

One line, three segments:

- **Model** — color-coded with a symbol (◆ Opus, ◇ Sonnet, ○ Haiku).
- **Directory + git status** — current folder, plus ✓ clean / ✱ dirty / — not a repo.
- **Context battery** — a bar and percentage showing how full the context window is,
  green → yellow → red as it fills.

## Requirements

- `bash`, `jq`, and `git` on your PATH.
- On Windows, a Bash environment (Git Bash or WSL) — the statusline is a Bash script.

## Reverting

Remove the `statusLine` key from `settings.json`, or restore the backup the command
creates. The command tells you the exact paths when it finishes.
