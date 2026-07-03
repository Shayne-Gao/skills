# Refresh Playbook

## When To Refresh

Run a fresh market refresh when:
- the user reports many listed accounts are already sold
- the top candidates in the unified ranking are stale
- the user explicitly asks for fresh platform data
- the user has already opened filtered source pages and wants the latest current-page capture

Do not refresh when:
- only scoring rules changed
- only ranking logic changed
- only HTML presentation changed
- the user only wants to compare already scored candidates

In those cases, reuse the current local cache and re-score.

## Compare-Only Checklist

Use this when the user wants a buying decision on already scored data:

1. Reuse `game-account-evaluator/outputs/wuwa_unified_scored.json`.
2. Filter by the requested budget range or explicit `product_id` shortlist.
3. Keep only active, fully scored rows.
4. Compare:
   - `value_score`
   - `strength_score`
   - `team_count`
   - `matched_teams`
   - `T0/T0.5` roles
   - signature weapon completeness
   - binding / delivery risk
5. Produce a written recommendation.
6. If the user wants a visual handoff, generate `game-account-evaluator/outputs/wuwa_shortlist_compare.html`.

## Hard Rules

- If the user already configured filters and sort in the browser, do not refresh, reload, navigate, or reproduce filters manually.
- Use only the currently opened source pages for browser-driven capture.
- If a required page is missing, stop and ask the user to open it.
- List capture alone is not a completed task; every refreshed row must continue into detail fetch and scoring.
- A row is deliverable only after it has real scoring output, especially `strength_score` and `value_score`.
- Empty placeholders, `pending` detail rows, and parse-failed rows must not be shipped into `game-account-evaluator/outputs/wuwa_unified_review.html`.

## Fresh Refresh Checklist

1. Archive the current working snapshot when replacing stale market outputs.
2. Confirm which sources will use browser pages and which will use approved APIs.
3. Confirm required pages are already open if the user prepared filters manually.
4. Capture current list rows from `PZDS`, `7881`, and `Kejinshou`.
5. Compare captured rows against `game-account-evaluator/outputs/wuwa_unified_scored.json`.
6. Send only new rows and incomplete rows into detail fetch.
7. Fetch detail payloads by source:
   - `PZDS`: detail HTML
   - `7881`: H5 detail API
   - `Kejinshou`: official detail API when available, otherwise mobile detail page plus listing title
8. Parse and score every target row.
9. Write abnormal or unscorable rows into side outputs instead of the final HTML.
10. Merge successful rows into unified data and rebuild `game-account-evaluator/outputs/wuwa_unified_review.html`.
11. Validate that this round's refreshed rows now have real scores.

Required handoff:
- `game-account-evaluator/outputs/wuwa_unified_scored.json`
- `game-account-evaluator/outputs/wuwa_unified_scored.csv`
- `game-account-evaluator/outputs/wuwa_unified_review.html`

Optional side outputs:
- `game-account-evaluator/outputs/wuwa_unified_excluded_incomplete_rows.json`
- `game-account-evaluator/outputs/current_page_backfill_failures.json`

## Re-score Checklist

1. Confirm raw and detail caches already exist.
2. Update config or scoring logic.
3. Re-run the scoring scripts only.
4. Rebuild unified HTML from the unified scored dataset.
5. Do not perform a fresh browser refresh unless the user requested new market data.

## Validation Checklist

After refresh or re-score, verify:
- `game-account-evaluator/outputs/wuwa_unified_review.html` exists after the task
- refreshed rows have non-zero `strength_score` and `value_score`
- the unified output still preserves historical scored rows
- current-round rows are not left behind as empty placeholders
- platform coverage and market metadata are updated as expected
- team-synergy fields are still present when applicable:
  - `team_count`
  - `team_bonus`
  - `matched_teams`
- rows that failed detail fetch or parsing appear only in side outputs, not in final unified HTML

For compare-only tasks, also verify:
- shortlisted rows are still marked active
- comparison output clearly separates value from strength
- binding uncertainty is surfaced instead of buried in narrative text

## Common Failure Modes

### PZDS WAF

Symptoms:
- returned HTML is a challenge or block page
- parsed values become zero

Response:
- keep list acquisition in browser
- verify direct detail fetching still returns product HTML
- if detail parsing is incomplete, stop and ask the user instead of shipping zero-score rows
- if only scoring changes, reuse local cache instead of re-fetching

### Kejinshou Token Expiry

Symptoms:
- list or detail API returns non-success status

Response:
- obtain a fresh `mw-token`
- obtain a fresh `mw-enc-token`
- obtain a fresh `mw-sid`
- if browser pages were already prepared by the user, prefer using those pages without refreshing them

### 7881 Desktop Detail Risk

Symptoms:
- desktop detail page shows challenge, short page, or incomplete data

Response:
- prefer the H5 detail API behind the page
- keep browser list capture on the current user-opened page
- isolate rows that still cannot be fully scored into side outputs

### Empty New-Round Rows

Symptoms:
- `new` rows appear in unified data but have no real scores
- HTML shows placeholders or missing detail labels for the supposed refreshed rows

Response:
- treat list capture as incomplete
- continue detail fetch and scoring before delivery
- exclude rows that still cannot produce valid scores from the final unified HTML
