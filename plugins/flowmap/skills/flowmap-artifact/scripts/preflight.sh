#!/bin/sh
# Dependency check for the flowmap-artifact skill.
#
#   sh preflight.sh              check and report
#   sh preflight.sh --json       machine-readable
#   sh preflight.sh --install    perform repairs (ask the user first)
#
# Exit codes:
#   0  ready
#   2  repairable — ASK THE USER, then re-run with --install
#   3  blocked — needs a human (report it; do not start the build)
#
# This wrapper exists for one reason: Python is the skill's only external
# dependency, and preflight.py cannot report its own absence. Everything past the
# interpreter check is delegated there.

set -eu

SKILL_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
MIN_MAJOR=3
MIN_MINOR=9

find_python() {
    for candidate in python3 python3.13 python3.12 python3.11 python3.10 python3.9 python; do
        command -v "$candidate" >/dev/null 2>&1 || continue
        if "$candidate" -c "import sys; sys.exit(0 if sys.version_info >= ($MIN_MAJOR, $MIN_MINOR) else 1)" 2>/dev/null; then
            printf '%s\n' "$candidate"
            return 0
        fi
    done
    return 1
}

install_hint() {
    if command -v brew >/dev/null 2>&1; then
        printf 'brew install python3'
    elif command -v apt-get >/dev/null 2>&1; then
        printf 'sudo apt-get update && sudo apt-get install -y python3'
    elif command -v dnf >/dev/null 2>&1; then
        printf 'sudo dnf install -y python3'
    elif command -v pacman >/dev/null 2>&1; then
        printf 'sudo pacman -S --noconfirm python'
    else
        printf 'install Python %s.%s or newer from https://www.python.org/downloads/' "$MIN_MAJOR" "$MIN_MINOR"
    fi
}

WANT_INSTALL=0
for arg in "$@"; do
    [ "$arg" = "--install" ] && WANT_INSTALL=1
done

if PY=$(find_python); then
    exec "$PY" "$SKILL_DIR/scripts/preflight.py" "$@"
fi

# No usable interpreter. Nothing else this skill needs can be checked without one.
CMD=$(install_hint)

if [ "$WANT_INSTALL" -eq 1 ] && command -v brew >/dev/null 2>&1; then
    # Homebrew is the one path that installs without sudo, so it is the only one
    # safe to run unattended. Everything else would block on a password prompt.
    echo "Installing Python 3 via Homebrew..."
    brew install python3 || exit 3
    if PY=$(find_python); then
        exec "$PY" "$SKILL_DIR/scripts/preflight.py" --force
    fi
    echo "Python 3 still not on PATH after install." >&2
    exit 3
fi

echo "flowmap-artifact: blocked"
echo
echo "  [blocked] Python ${MIN_MAJOR}.${MIN_MINOR}+ not found on PATH"
echo "      fix: $CMD"
echo
echo "Python is this skill's only external dependency — it uses the standard"
echo "library alone, so there is nothing further to install afterwards."
case "$CMD" in
    sudo*) echo; echo "That command needs sudo, so run it yourself rather than through the agent." ;;
esac
exit 3
