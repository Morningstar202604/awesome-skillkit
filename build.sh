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

# Zip a skill dir flat (top-level entry = skill folder name). `zip` is not
# shipped with stock Git Bash, so fall back to python's zipfile module.
zip_dir() {
  local archive="$1" parent="$2" name="$3"
  (
    cd "$parent" || exit 1
    if command -v zip >/dev/null 2>&1; then
      zip -r -q "$archive" "$name" -x "*.local.json"
    else
      python3 - "$archive" "$name" <<'PY'
import os, sys, zipfile
archive, name = sys.argv[1], sys.argv[2]
with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as z:
    for root, _dirs, files in os.walk(name):
        for f in sorted(files):
            if f.endswith(".local.json"):
                continue
            p = os.path.join(root, f)
            z.write(p, p)
PY
    fi
  )
}

count=0
all_count=0
declare -A ALL_SKILLS
for pack_json in "$SCRIPT_DIR"/packs/*/pack.json; do
  pack_id="$(basename "$(dirname "$pack_json")")"
  # Collect skill names from pack.json (jq if available, else python3).
  # The path is passed as argv (not interpolated into the script) so that
  # MSYS/Git Bash translates it for native Windows Python.
  # Native Windows Python writes CRLF; tr strips \r so names match dir names.
  mapfile -t skills < <(python3 -c "
import json,sys
p=json.load(open(sys.argv[1],encoding='utf-8'))
for s in p['skills']: print(s['name'])
" "$pack_json" | tr -d '\r')
  missing=0
  for skill in "${skills[@]}"; do
    dir="$(find_skill_dir "$skill")"
    if [ -z "$dir" ]; then
      echo "WARN: skill dir not found: $skill (pack $pack_id)" >&2
      missing=1
      continue
    fi
    ALL_SKILLS["$skill"]=1
    all_count=$((all_count + 1))
    # zip content keeps the skill folder name flat (top-level = skill name),
    # so users unzip and drag the skill folders straight into skills/.
    parent="$(dirname "$dir")"
    name="$(basename "$dir")"
    zip_dir "$OUT_DIR/$pack_id.zip" "$parent" "$name"
  done
  echo "built: $OUT_DIR/$pack_id.zip  (${#skills[@]} skills)"
  count=$((count + 1))
done

# Convenience bundle: every skill from every pack in one zip
if [ "$all_count" -gt 0 ]; then
  for skill in "${!ALL_SKILLS[@]}"; do
    dir="$(find_skill_dir "$skill")"
    parent="$(dirname "$dir")"
    name="$(basename "$dir")"
    zip_dir "$OUT_DIR/_all.zip" "$parent" "$name"
  done
  echo "built: $OUT_DIR/_all.zip  (_all bundle, $all_count skills)"
  count=$((count + 1))
fi

echo "done: $count archive(s) -> $OUT_DIR"
