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
for skill in */; do
  skill="${skill%/}"
  # A dir is a valid skill if it contains SKILL.md at any depth
  # (e.g. zhihu-skill keeps SKILL.md in a subdirectory)
  if ! find "$skill" -name "SKILL.md" -print -quit | grep -q .; then
    echo "skip $skill (no SKILL.md)"
    continue
  fi

  zip_args=(-r -q "$OUT_DIR/$skill.zip" "$skill")
  for ex in "${EXCLUDES[@]}"; do
    zip_args+=(-x "$skill/$ex")
  done
  zip "${zip_args[@]}"
  echo "built: $OUT_DIR/$skill.zip"
  count=$((count + 1))
done

echo "done: $count pack(s) -> $OUT_DIR"
