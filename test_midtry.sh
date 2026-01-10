#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
output_path="$script_dir/examples/sheep-test.md"

task="A farmer has 17 sheep. All but 9 run away. How many sheep does the farmer have left?"

if ! command -v codex >/dev/null 2>&1; then
  echo "codex CLI not found in PATH." >&2
  exit 1
fi

prompt="\$midtry $task"
codex exec --color never --output-last-message "$output_path" "$prompt"

python3 - "$output_path" <<'PY'
import pathlib
import sys

path = pathlib.Path(sys.argv[1])
text = path.read_text(encoding="utf-8")
replacements = {
    "\u201c": "\"",
    "\u201d": "\"",
    "\u2018": "'",
    "\u2019": "'",
    "\u2013": "-",
    "\u2014": "-",
    "\u2212": "-",
    "\u2026": "...",
}
for src, dst in replacements.items():
    text = text.replace(src, dst)
path.write_text(text, encoding="utf-8")
PY

echo "Saved output to $output_path"
