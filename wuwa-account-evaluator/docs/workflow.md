# Workflow

## End-to-End Flow

1. Archive the previous working snapshot when the market data is stale.
2. Capture list rows from the user-opened source pages or approved API flow.
3. Compare captured rows against `game-account-evaluator/outputs/wuwa_unified_scored.json`.
4. Send only truly new rows and incomplete rows into detail fetch.
5. Parse detail payloads into normalized role, weapon, resource, and binding data.
6. Score each detail payload into a deliverable row with `strength_score` and `value_score`.
7. Isolate unscorable rows into side outputs instead of shipping them as placeholders.
8. Merge scored rows into the unified dataset and rebuild `wuwa_unified_review.html`.
9. Review the final unified ranking and answer comparison questions from that output.

## Buy-Decision Flow

Use this flow when the user asks which account to buy and does not necessarily need a fresh market refresh.

1. Reuse `game-account-evaluator/outputs/wuwa_unified_scored.json` first.
2. Filter to the user's target price range.
3. Keep only rows that are still active and fully rankable.
4. Compare both `value_score` and `strength_score`.
5. Check team completeness, signature-weapon alignment, and `T0/T0.5` coverage.
6. Check binding / unbind / delivery risk separately from scoring.
7. If the user wants a side-by-side handoff, generate `game-account-evaluator/outputs/wuwa_shortlist_compare.html`.

## Completion Standard

A refresh is complete only when all of the following are true:
- list capture has already been followed by detail fetch
- detail fetch has already been followed by scoring
- scored rows have been merged into `game-account-evaluator/outputs/wuwa_unified_scored.json`
- `game-account-evaluator/outputs/wuwa_unified_review.html` has been rebuilt

These cases do not count as successful delivery:
- list-only rows with `pending` or `missing` detail status
- rows with zeroed `strength_score` and `value_score` caused by missing detail
- incremental placeholders that were never backfilled into real scored rows

## Source Flows

### PZDS

#### List Acquisition

- Use the current page already opened by the user in Trae.
- Do not refresh, reload, or re-open the page after the user has set filters and sorting.
- Extract current `/goodsDetails/<id>/` rows, price, publish time, and listing metadata from the visible page.

#### Detail + Scoring

- Fetch the detail HTML for each target `product_id`.
- Parse description blocks into normalized roles, weapons, resources, and account attributes.
- Score the parsed payload with the current model.

Primary outputs:
- `game-account-evaluator/data/pzds/detail_html/*.html`
- `game-account-evaluator/outputs/pzds_wuwa_top100_scored.json`
- `game-account-evaluator/outputs/pzds_wuwa_top100_scored.csv`

### 7881

#### List Acquisition

- Use the current page already opened by the user in Trae.
- Do not refresh or navigate away from the user-configured page.
- Extract `goods_id`, price, publish time, and listing metadata from the visible rows.

#### Detail + Scoring

- Use the H5 detail API behind the page instead of the desktop page when possible.
- Extract summary fields, roles, weapons, resources, and relevant account metadata from the detail payload.
- Score the parsed payload with the current model.

Primary outputs:
- `game-account-evaluator/data/7881/detail_json/*.json`
- `game-account-evaluator/outputs/7881_wuwa_scored.json`
- `game-account-evaluator/outputs/7881_wuwa_scored.csv`

### Kejinshou

#### List Acquisition

- Prefer the official list API for latest-first collection when valid tokens are available.
- If the user has already opened and filtered a browser page, do not refresh or replace it.
- Extract `product_id`, price, publish time, and listing metadata from API or page results.

#### Detail + Scoring

- Prefer the official detail/API workflow when tokens are valid.
- Otherwise use the current mobile detail page plus listing title to recover role, weapon, and resource information.
- Score the parsed payload with the current model.

Primary outputs:
- `game-account-evaluator/data/raw/kejinshou_top200_pages/*.json`
- `game-account-evaluator/data/detail/kejinshou_top200/*.json`
- `game-account-evaluator/outputs/kejinshou_top200_scored.json`
- `game-account-evaluator/outputs/kejinshou_top200_scored.csv`

## Unified Merge Rules

- `game-account-evaluator/outputs/wuwa_unified_scored.json` is the single source of truth.
- `game-account-evaluator/outputs/wuwa_unified_review.html` is the only required HTML handoff.
- Historical scored rows remain in unified outputs; refreshes append new scored rows and patch market metadata.
- Incremental snapshots are intermediate inputs only; they may patch market fields, but must never replace richer scored payloads with default zeros.
- Unscorable rows stay in side outputs and must not appear in the final unified HTML deliverable.

## Side Outputs

Use side outputs to keep failed or incomplete work visible without polluting final delivery:
- `game-account-evaluator/outputs/wuwa_unified_excluded_incomplete_rows.json`
- `game-account-evaluator/outputs/current_page_backfill_failures.json`

## Re-score Only Flow

When only scoring rules change:
1. Reuse the existing raw and detail cache.
2. Re-run the scoring scripts.
3. Rebuild the unified HTML from `wuwa_unified_scored.json`.
4. Do not perform a fresh browser refresh unless the user asked for new market data.

## Compare-Only Flow

When the user only wants to compare existing candidates:
1. Do not refresh market pages by default.
2. Reuse `game-account-evaluator/outputs/wuwa_unified_scored.json`.
3. Build a shortlist from the requested budget range or explicit `product_id` set.
4. Produce a written recommendation, and generate a dedicated comparison HTML when requested.
