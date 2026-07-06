#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
GLOBAL_TRAE_SKILLS_DIR="${HOME}/.trae/skills"
BACKUP_ROOT="${HOME}/.trae/skills_backups/life_skills_unify_$(date +%Y%m%d_%H%M%S)"

SKILLS=(
  "agent-reach"
  "fetch_smzdm_latest_items"
  "sg-local-activity-deals"
  "shopping-category-buyer-guide"
  "travel-planner"
  "wuwa-account-cultivation-planner"
  "wuwa-account-evaluator"
)

mkdir -p "$GLOBAL_TRAE_SKILLS_DIR"
mkdir -p "$BACKUP_ROOT"

for skill in "${SKILLS[@]}"; do
  repo_path="$ROOT_DIR/$skill"
  global_path="$GLOBAL_TRAE_SKILLS_DIR/$skill"

  if [[ ! -d "$repo_path" ]]; then
    echo "skip missing repo skill: $skill" >&2
    continue
  fi

  if [[ -e "$global_path" && ! -L "$global_path" ]]; then
    echo "backup existing global skill: $skill"
    cp -R "$global_path" "$BACKUP_ROOT/"
  fi

  rm -rf "$global_path"
  ln -s "$repo_path" "$global_path"
  echo "linked $global_path -> $repo_path"
done

echo
echo "backup saved at: $BACKUP_ROOT"
