#!/usr/bin/env bash
# SkillKit build script: package scene packs (packs/*/pack.json) into dist/*.zip
# Each scene pack zip contains multiple skill dirs (flat), so users unzip and
# drag the skill folders into their AI tool's skills directory.
# Usage: bash build.sh [output-dir]   (default: dist/)
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
  "*.local.json"
)

mkdir -p "$OUT_DIR"

# Locate a skill dir under skills/ by its directory name
find_skill_dir() {
  local name="$1"
  find "$SCRIPT_DIR/skills" -type d -name "$name" -not -path "*/.git/*" | head -n1
}

count=0
declare -A ALL_SKILLS
for pack_json in "$SCRIPT_DIR"/packs/*/pack.json; do
  pack_id="$(basename "$(dirname "$pack_json")")"
  # Collect skill names from pack.json (jq if available, else python3)
  mapfile -t skills < <(python3 -c "
import json,sys
p=json.load(open('$pack_json',encoding='utf-8'))
for s in p['skills']: print(s['name'])
")
  zip_args=(-r -q "$OUT_DIR/$pack_id.zip")
  missing=0
  for skill in "${skills[@]}"; do
    dir="$(find_skill_dir "$skill")"
    if [ -z "$dir" ]; then
      echo "WARN: skill dir not found: $skill (pack $pack_id)" >&2
      missing=1
      continue
    fi
    ALL_SKILLS["$skill"]=1
    # zip content keeps the skill folder name flat (top-level = skill name),
    # so users unzip and drag the skill folders straight into skills/.
    parent="$(dirname "$dir")"
    name="$(basename "$dir")"
    (cd "$parent" && zip -r -q "$OUT_DIR/$pack_id.zip" "$name" -x "*.local.json")
  done
  echo "built: $OUT_DIR/$pack_id.zip  (${#skills[@]} skills)"
  count=$((count + 1))
done

# Convenience bundle: every skill from every pack in one zip
if [ "${#ALL_SKILLS[@]}" -gt 0 ]; then
  for skill in "${!ALL_SKILLS[@]}"; do
    dir="$(find_skill_dir "$skill")"
    parent="$(dirname "$dir")"
    name="$(basename "$dir")"
    (cd "$parent" && zip -r -q "$OUT_DIR/_all.zip" "$name" -x "*.local.json")
  done
  echo "built: $OUT_DIR/_all.zip  (_all bundle, ${#ALL_SKILLS[@]} skills)"
  count=$((count + 1))
fi

echo "done: $count archive(s) -> $OUT_DIR"
