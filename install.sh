#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ "${1:-}" = "--help" ] || [ "${1:-}" = "-h" ]; then
  echo "Usage: install.sh [--dry-run]"
  exit 0
fi

dry_run=0
if [ "${1:-}" = "--dry-run" ]; then
  dry_run=1
fi

run() {
  if [ "$dry_run" -eq 1 ]; then
    printf "[dry-run]"
    printf " %q" "$@"
    printf "\n"
  else
    "$@"
  fi
}

installed_any=0
codex_home="${CODEX_HOME:-$HOME/.codex}"

# Claude Code
if [ -d "$HOME/.claude/commands" ]; then
  run cp "$script_dir/midtry.md" "$HOME/.claude/commands/midtry.md"
  echo "Installed for Claude Code"
  installed_any=1
fi

# Codex skill (agent skills standard)
codex_skill_src="$script_dir/.codex/skills/midtry"
if [ -d "$codex_skill_src" ]; then
  codex_skill_dest="$codex_home/skills/midtry"
  run mkdir -p "$codex_skill_dest"
  run cp -R "$codex_skill_src"/. "$codex_skill_dest"/
  echo "Installed Codex skill: $codex_skill_dest"
  installed_any=1
fi

# Codex CLI wrapper (uses the MidTry skill)
if command -v codex >/dev/null 2>&1; then
  bin_dir="$HOME/.local/bin"
  if [ ! -d "$bin_dir" ]; then
    run mkdir -p "$bin_dir"
  fi
  run cp "$script_dir/midtry_codex.sh" "$bin_dir/midtry"
  run chmod +x "$bin_dir/midtry"
  echo "Installed Codex wrapper: $bin_dir/midtry"
  installed_any=1
fi

if [ "$installed_any" -eq 0 ]; then
  echo "No compatible CLI install locations detected."
  echo "- Claude Code: create ~/.claude/commands"
  echo "- Codex CLI: ensure codex is on PATH (wrapper installs to ~/.local/bin)"
  echo "- Codex skills: create ~/.codex/skills"
fi
