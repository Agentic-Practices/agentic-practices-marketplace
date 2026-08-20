#!/bin/bash
# Claude Code status line - shows context window usage as a "battery" bar.
# Reference template distributed by the setup-statusline plugin.
# Requires: bash, jq, git. Reads Claude Code's status JSON from stdin.

input=$(cat)

MODEL=$(echo "$input" | jq -r '.model.display_name')
MODEL_ID=$(echo "$input" | jq -r '.model.id')
CONTEXT_SIZE=$(echo "$input" | jq -r '.context_window.context_window_size')
USAGE=$(echo "$input" | jq '.context_window.current_usage')

# Max output tokens for effective window calculation.
# Claude Code internally caps this when computing the autocompact threshold;
# the actual model max doesn't matter here — only the capped value does.
MAX_OUTPUT_CAP=20000
case "$MODEL_ID" in
    *opus-4-6*)    MODEL_MAX=128000 ;;
    *opus-4-5*|*sonnet-4*|*haiku-4*) MODEL_MAX=64000 ;;
    *opus-4*)      MODEL_MAX=32000 ;;
    *3-5*)         MODEL_MAX=8192 ;;
    *claude-3-opus*) MODEL_MAX=4096 ;;
    *claude-3-sonnet*) MODEL_MAX=8192 ;;
    *claude-3-haiku*) MODEL_MAX=4096 ;;
    *)             MODEL_MAX=32000 ;;
esac
# min(modelMax, cap)
[ "$MODEL_MAX" -lt "$MAX_OUTPUT_CAP" ] && MAX_OUTPUT=$MODEL_MAX || MAX_OUTPUT=$MAX_OUTPUT_CAP

# Calculate autocompact buffer
# EHA = contextSize - maxOutputTokens (available context)
EHA=$((CONTEXT_SIZE - MAX_OUTPUT))

if [ -n "$CLAUDE_AUTOCOMPACT_PCT_OVERRIDE" ]; then
    # threshold = min(EHA * pct/100, EHA - 13000)
    PCT_THRESHOLD=$((EHA * CLAUDE_AUTOCOMPACT_PCT_OVERRIDE / 100))
    DEFAULT_THRESHOLD=$((EHA - 13000))
    if [ "$PCT_THRESHOLD" -lt "$DEFAULT_THRESHOLD" ]; then
        THRESHOLD=$PCT_THRESHOLD
    else
        THRESHOLD=$DEFAULT_THRESHOLD
    fi
else
    THRESHOLD=$((EHA - 13000))
fi

# Buffer = contextSize - threshold (only if autocompact enabled)
# Check env vars and config file
AUTOCOMPACT_ENABLED=1
# Check DISABLE_COMPACT env var
if [ -n "$DISABLE_COMPACT" ] && [ "$DISABLE_COMPACT" != "0" ] && [ "$DISABLE_COMPACT" != "false" ]; then
    AUTOCOMPACT_ENABLED=0
fi
# Check DISABLE_AUTO_COMPACT env var
if [ -n "$DISABLE_AUTO_COMPACT" ] && [ "$DISABLE_AUTO_COMPACT" != "0" ] && [ "$DISABLE_AUTO_COMPACT" != "false" ]; then
    AUTOCOMPACT_ENABLED=0
fi
# Check config file (defaults to true if not set)
CONFIG_FILE="$HOME/.claude.json"
if [ -f "$CONFIG_FILE" ]; then
    CONFIG_VAL=$(jq -r 'if has("autoCompactEnabled") then .autoCompactEnabled else true end' "$CONFIG_FILE" 2>/dev/null)
    if [ "$CONFIG_VAL" = "false" ]; then
        AUTOCOMPACT_ENABLED=0
    fi
fi

# Calculate buffer based on compact settings
# - Full autocompact enabled: use full threshold buffer
# - Autocompact disabled but compact enabled: use 3k blocking buffer
# - All compact disabled: no buffer
COMPACT_DISABLED=0
if [ -n "$DISABLE_COMPACT" ] && [ "$DISABLE_COMPACT" != "0" ] && [ "$DISABLE_COMPACT" != "false" ]; then
    COMPACT_DISABLED=1
fi

if [ "$AUTOCOMPACT_ENABLED" = "1" ]; then
    BUFFER=$((CONTEXT_SIZE - THRESHOLD))
elif [ "$COMPACT_DISABLED" = "0" ]; then
    BUFFER=3000
else
    BUFFER=0
fi

if [ "$USAGE" != "null" ]; then
    # Calculate current context from current_usage fields
    CURRENT_TOKENS=$(echo "$USAGE" | jq '.input_tokens + .cache_creation_input_tokens + .cache_read_input_tokens')
    # Show usage as % of effective space
    # With autocompact: denominator = threshold (hits 100% when compact triggers)
    # Without autocompact: denominator = effective window (EHA)
    if [ "$AUTOCOMPACT_ENABLED" = "1" ]; then
        EFFECTIVE=$THRESHOLD
    else
        EFFECTIVE=$EHA
    fi
    PERCENT_USED=$((CURRENT_TOKENS * 100 / EFFECTIVE))
    [ "$PERCENT_USED" -gt 100 ] && PERCENT_USED=100

    PERCENT=$PERCENT_USED
else
    PERCENT=""
fi

# --- Colors ---
RED=$'\033[31m'
GREEN=$'\033[32m'
YELLOW=$'\033[33m'
BLUE=$'\033[34m'
MAGENTA=$'\033[35m'
GRAY=$'\033[90m'
RESET=$'\033[0m'

# --- Model (color-coded) ---
case "$MODEL" in
    *Opus*)   MODEL_COLOR="$MAGENTA"; MODEL_SYMBOL="◆" ;;
    *Sonnet*) MODEL_COLOR="$BLUE";    MODEL_SYMBOL="◇" ;;
    *Haiku*)  MODEL_COLOR="$GREEN";   MODEL_SYMBOL="○" ;;
    *)        MODEL_COLOR="$GRAY";    MODEL_SYMBOL="●" ;;
esac
MODEL_PART="${MODEL_COLOR}${MODEL_SYMBOL} ${MODEL}${RESET}"

# --- Current directory ---
CWD=$(echo "$input" | jq -r '.workspace.current_dir // empty')
DIR_NAME=$(basename "${CWD:-.}")
DIR_PART="${BLUE}${DIR_NAME}${RESET}"

# --- Git status ---
GIT_PART=""
if [ -n "$CWD" ] && [ -d "$CWD" ]; then
    if git -C "$CWD" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
        if [ -z "$(git -C "$CWD" status --porcelain 2>/dev/null)" ]; then
            GIT_PART="${GREEN}✓${RESET}"
        else
            GIT_PART="${YELLOW}✱${RESET}"
        fi
    else
        GIT_PART="${GRAY}—${RESET}"
    fi
fi

# --- Battery indicator ---
if [ -n "$PERCENT" ]; then
    BAR_WIDTH=5
    FILLED=$((PERCENT * BAR_WIDTH / 100))
    [ "$FILLED" -gt "$BAR_WIDTH" ] && FILLED=$BAR_WIDTH
    [ "$FILLED" -lt 1 ] && [ "$PERCENT" -gt 0 ] && FILLED=1
    EMPTY=$((BAR_WIDTH - FILLED))

    if [ "$PERCENT" -ge 76 ]; then
        BAR_COLOR="$RED"
    elif [ "$PERCENT" -ge 51 ]; then
        BAR_COLOR="$YELLOW"
    else
        BAR_COLOR="$GREEN"
    fi

    BAR="${BAR_COLOR}"
    for ((i=0; i<FILLED; i++)); do BAR+="▓"; done
    BAR+="${GRAY}"
    for ((i=0; i<EMPTY; i++)); do BAR+="░"; done
    BAR+="${RESET}"

    BATTERY_PART="${BAR} ${GRAY}${PERCENT}%${RESET}"
else
    BATTERY_PART="${GRAY}n/a${RESET}"
fi

# --- Output ---
SEP="${GRAY}|${RESET}"
printf "%s" "${MODEL_PART} ${SEP} ${DIR_PART} ${GIT_PART} ${SEP} ${BATTERY_PART}"
