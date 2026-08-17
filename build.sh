#!/usr/bin/env bash
# SkillKit build script: package skills/* source dirs into dist/*.zip
# Usage: bash build.sh [output-dir]   (default: dist/)
# Release flow: tag -> upload dist/*.zip to GitHub Releases
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUT_DIR="${1:-$SCRIPT_DIR/dist}"

# Non-core files excluded from the zips (consistent with repo packaging rules)
EXCLUDES=(
  ".github/*"
  ".gitignore"
  ".git/*"
  "docker-compose.yml"
  "__pycache__/*"
  "*.pyc"
)

mkdir -p "$OUT_DIR"

cd "$SCRIPT_DIR/skills"
count=0
# Walk every directory that contains a SKILL.md at any depth (multi-level taxonomy)
while IFS= read -r skill; do
  skill="${skill#./}"
  # Zip name = skill dir name (flat in dist/), content keeps the skill folder
  name="$(basename "$skill")"
  zip_args=(-r -q "$OUT_DIR/$name.zip" "$skill")
  for ex in "${EXCLUDES[@]}"; do
    zip_args+=(-x "$skill/$ex")
  done
  zip "${zip_args[@]}"
  echo "built: $OUT_DIR/$name.zip  (from $skill)"
  count=$((count + 1))
done < <(find . -name "SKILL.md" -exec dirname {} \; | sort -u)

echo "done: $count pack(s) -> $OUT_DIR"
