#!/usr/bin/env bash
# SkillKit one-click installer: unzip all dist/*.zip into the target skills dir
# Usage: bash install.sh [target-dir]   (default: ~/.claude/skills)
# Note: if dist/ is empty, run bash build.sh first
set -euo pipefail

HUB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET="${1:-$HOME/.claude/skills}"

if ! command -v unzip >/dev/null 2>&1; then
  echo "error: unzip not found. Install it first (yum install -y unzip / apt install -y unzip)" >&2
  exit 1
fi

mkdir -p "$TARGET"
count=0
for zip in "$HUB_DIR"/dist/*.zip; do
  [ -e "$zip" ] || continue
  name="$(basename "$zip" .zip)"
  echo "installing $name -> $TARGET/$name"
  unzip -oq "$zip" -d "$TARGET"
  count=$((count + 1))
done

echo "done: installed $count skill(s) to $TARGET"
echo "Start a new session to use them."
