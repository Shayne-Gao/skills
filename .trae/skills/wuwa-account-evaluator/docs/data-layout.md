# Data Layout

## Configs

- `game-account-evaluator/configs/wuwa_role_tiers_corrected.json`
  - corrected role tier source with overall / tower / requiem fields
- `game-account-evaluator/configs/wuwa_role_adjustments_33.json`
  - manual role adjustments and dependency penalties
- `game-account-evaluator/configs/wuwa_weapon_catalog.json`
  - weapon-to-owner mapping
- `game-account-evaluator/configs/wuwa_team_synergy_33.json`
  - full team definitions for synergy bonus
- `game-account-evaluator/configs/pzds_wuwa_top100_ids.txt`
  - fresh `PZDS` top-100 product IDs in listing order

## Raw Data

- `game-account-evaluator/data/raw/kejinshou_top200_pages/`
  - raw list API pages for `Kejinshou`
- `game-account-evaluator/data/detail/kejinshou_top200/`
  - raw `Kejinshou` detail JSON files
- `game-account-evaluator/data/pzds/detail_html/`
  - raw `PZDS` detail HTML files
- `game-account-evaluator/data/raw/pzds_top100_from_browser_<timestamp>.json`
  - browser-derived `PZDS` ID snapshots
- `game-account-evaluator/data/raw/kejinshou_incremental_page1_<date>.json`
- `game-account-evaluator/data/raw/7881_incremental_page1_<date>.json`
- `game-account-evaluator/data/raw/pzds_incremental_page1_<date>.json`
- `game-account-evaluator/data/raw/*_incremental_seen_ids.json`
  - latest page-1 incremental snapshots and local dedupe caches

## Outputs

- `game-account-evaluator/outputs/kejinshou_top200_scored.json`
- `game-account-evaluator/outputs/kejinshou_top200_scored.csv`
- `game-account-evaluator/outputs/wuwa_top200_normalized_assets.json`
- `game-account-evaluator/outputs/wuwa_top200_role_tier_scored.json`
- `game-account-evaluator/outputs/wuwa_top200_role_tier_scored.csv`
- `game-account-evaluator/outputs/pzds_wuwa_top100_scored.json`
- `game-account-evaluator/outputs/pzds_wuwa_top100_scored.csv`
- `game-account-evaluator/outputs/wuwa_unified_scored.json`
- `game-account-evaluator/outputs/wuwa_unified_scored.csv`
- `game-account-evaluator/outputs/wuwa_top200_review.html`
- `game-account-evaluator/outputs/pzds_wuwa_top100_review.html`
- `game-account-evaluator/outputs/wuwa_unified_review.html`

## Archive

- `game-account-evaluator/archive/refresh_<timestamp>/`

Archive before a new refresh when:
- the user says many accounts are sold
- the market view is stale
- fresh crawling will overwrite the active working snapshot

Archive should include:
- old raw captures
- old output files
- prior `PZDS` ID list

## Comparison Source Of Truth

The primary comparison source should be:
- `game-account-evaluator/outputs/wuwa_unified_scored.json`

The primary review page should be:
- `game-account-evaluator/outputs/wuwa_unified_review.html`

The required fetch-completion handoff page should be:
- `game-account-evaluator/outputs/wuwa_unified_review.html`

Unified outputs should behave as an append-only market history:
- keep previous rows in `wuwa_unified_scored.json`
- append newly seen incremental rows into the same store
