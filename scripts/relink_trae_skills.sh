#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TRAE_SKILLS_DIR="$ROOT_DIR/.trae/skills"

SKILLS=(
  "agent-reach"
  "fetch_smzdm_latest_items"
  "sg-local-activity-deals"
  "shopping-category-buyer-guide"
  "travel-planner"
  "wuwa-account-cultivation-planner"
  "wuwa-account-evaluator"
)

mkdir -p "$TRAE_SKILLS_DIR"

for skill in "${SKILLS[@]}"; do
  target="$ROOT_DIR/$skill"
  link_path="$TRAE_SKILLS_DIR/$skill"

  if [[ ! -d "$target" ]]; then
    echo "skip missing skill: $skill" >&2
    continue
  fi

  rm -rf "$link_path"
  ln -s "../../$skill" "$link_path"
  echo "linked $link_path -> ../../$skill"
done
