#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_TRAE_SKILLS_DIR="$ROOT_DIR/.trae/skills"
GLOBAL_TRAE_SKILLS_DIR="${HOME}/.trae/skills"

SKILLS=(
  "agent-reach"
  "fetch_smzdm_latest_items"
  "sg-local-activity-deals"
  "shopping-category-buyer-guide"
  "travel-planner"
  "wuwa-account-cultivation-planner"
  "wuwa-account-evaluator"
)

for skill in "${SKILLS[@]}"; do
  repo_path="$ROOT_DIR/$skill"
  repo_compat_path="$REPO_TRAE_SKILLS_DIR/$skill"
  global_path="$GLOBAL_TRAE_SKILLS_DIR/$skill"

  echo "=== $skill ==="
  echo "repo: $repo_path"

  if [[ -L "$repo_compat_path" ]]; then
    echo "repo .trae: symlink -> $(readlink "$repo_compat_path")"
  elif [[ -e "$repo_compat_path" ]]; then
    echo "repo .trae: exists but is not a symlink"
  else
    echo "repo .trae: missing"
  fi

  if [[ -L "$global_path" ]]; then
    echo "global .trae: symlink -> $(readlink "$global_path")"
    if [[ "$repo_path" -ef "$global_path" ]]; then
      echo "same target: yes"
    else
      echo "same target: no"
    fi
  elif [[ -e "$global_path" ]]; then
    echo "global .trae: exists but is not a symlink"
  else
    echo "global .trae: missing"
  fi

  echo
done
