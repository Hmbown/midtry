#!/usr/bin/env bash
set -euo pipefail

if [ "${1:-}" = "--help" ] || [ "${1:-}" = "-h" ]; then
  echo "Usage: midtry <task>"
  echo "Runs the MidTry Codex skill through Codex CLI."
  exit 0
fi

if ! command -v codex >/dev/null 2>&1; then
  echo "codex CLI not found in PATH." >&2
  exit 1
fi

if [ "$#" -eq 0 ]; then
  echo "Missing task. Example: midtry \"Explain big-O tradeoffs\"" >&2
  exit 1
fi

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
codex_home="${CODEX_HOME:-$HOME/.codex}"
user_skill="$codex_home/skills/midtry/SKILL.md"
repo_skill="$script_dir/.codex/skills/midtry/SKILL.md"

if [ ! -f "$user_skill" ] && [ ! -f "$repo_skill" ]; then
  echo "MidTry skill not found. Run ./install.sh or use this repo as CWD." >&2
fi

task="$*"
prompt="\$midtry $task"

codex exec --color never "$prompt"
