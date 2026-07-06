---
name: "wuwa-account-evaluator"
description: "Refreshes Wuthering Waves listings, rebuilds unified ranking, and supports shortlist comparison. Invoke when user wants fresh market data, buy-account comparison, or candidate review."
---

# Wuwa Account Evaluator

This skill maintains the full Wuthering Waves account-evaluation workflow for the `life_skills` workspace.

Use this skill when the user wants to:
- refresh the latest account listings from `PZDS`, `Kejinshou`, and `7881`
- re-run scoring after changing rules, tier lists, or team-synergy rules
- rebuild the unified review HTML
- compare candidate accounts using the current scoring model
- generate a standalone shortlist comparison HTML for specific candidate accounts
- archive stale market snapshots before a new refresh

## Scope

The workflow covers:
- browser-page list capture for `PZDS`
- API-first or page-assisted list capture for `Kejinshou`
- browser-page list capture plus H5 detail API for `7881`
- detail fetch after every new list capture
- role / weapon / pull scoring
- team-synergy bonus scoring
- abnormal-row isolation for unscorable data
- unified-only cross-platform ranking and HTML review
- buy-account comparison and shortlist HTML handoff

## Workspace Layout

Primary project root:
- `game-account-evaluator/`

Core directories:
- `game-account-evaluator/scripts/`
- `game-account-evaluator/configs/`
- `game-account-evaluator/data/`
- `game-account-evaluator/outputs/`
- `game-account-evaluator/archive/`

Additional references:
- `docs/workflow.md`
- `docs/scoring-rules.md`
- `docs/data-layout.md`
- `docs/refresh-playbook.md`
- `docs/buying-playbook.md`

## Source Entry Points

Use these source-specific entry points and collection modes:

- `PZDS`
- listing page should be opened by the user in Trae first
- preferred listing URL: `https://www.pzds.com/goodsList/303/6?goodsCatalogueId=6`
- use browser-session state for exact filter / sort reproduction

- `7881`
- listing page should be opened by the user in Trae first
- preferred listing URL: `https://search.7881.com/A5752-100003-A5752P006-A5752P006008-A5752Y001.html?pageNum=1`
- for latest-round capture on an opened page, click the page's `最新发布` sort button instead of refreshing or reopening
- use the opened page for incremental collection, especially when relying on page-visible relative publish time

- `Kejinshou`
- prefer API-first collection for list refresh
- preferred listing page URL for manual verification only: `https://www.kejinshou.com/goods/7265`
- preferred list endpoint: `https://www.kejinshou.com/kjs_search/product.search`
- current browser behavior shows `最新发布` is backed by the same list endpoint, so API mode can be used for latest-first collection after the sort parameter is aligned in code
- when working from the already opened browser page, click the page's `最新发布` sort button before reading visible rows; do not refresh or re-open the page

## Operating Rules

1. Archive old outputs before a new refresh when the user says listings are stale or many accounts are sold.
2. When the user has already configured filters / sort in the browser, do not refresh, reload, navigate, or reproduce filters manually. Use only the currently opened pages.
3. For latest-round capture from already opened pages, `7881` and `Kejinshou` require clicking the in-page `最新发布` button first; `PZDS` follows the user's already prepared state.
4. If a required page is missing, stop and ask the user to open it. Do not auto-open a replacement page with guessed parameters.
5. List capture alone is never a completed refresh. After capturing list rows, first deduplicate against local unified history, then continue to detail fetch and scoring only for rows that still require it.
6. A row is deliverable only when it has a complete score payload, especially `strength_score` and `value_score`.
7. If a row cannot produce any valid score, do not write it into `wuwa_unified_review.html` and do not let it remain as an empty placeholder in the unified deliverable.
8. Unscorable rows should be isolated as abnormal data in a side output for troubleshooting, rather than treated as successful refresh output.
9. Keep raw captures separate from scored outputs. Do not mutate raw captures after saving them.
10. Prefer local cache reuse for re-scoring tasks when only scoring logic changes.
11. Use the current scoring model unless the user overrides it:
   - three-list role blending
   - `T0/T0.5` preservation emphasis
   - `唤声涡纹` excluded from pull score
   - `铸潮波纹` counted at `0.8`
   - full team-synergy matches add `+100` each
12. `outputs/wuwa_unified_scored.json` is the single source of truth, and `outputs/wuwa_unified_review.html` is the only required HTML handoff.
13. Historical scored rows in unified outputs should be retained. During normal incremental rounds, do not re-fetch detail for rows that already have complete local detail and score data unless the user explicitly requests a full refresh or a special re-update.
14. Only truly new rows, or rows that exist locally but still lack complete detail / score payloads, may enter the detail-fetch stage.
15. If no new information is captured for an already known row, do not modify the row's `round_id`; `round_id` records the first round in which that row appeared.
16. Incremental page snapshots are intermediate inputs only. They may patch market metadata, but they are not final delivery rows.
17. A fetch task is not complete until scored results are merged into `outputs/wuwa_unified_scored.json` and `outputs/wuwa_unified_review.html` is rebuilt.
18. When the user asks which account to buy, prefer reusing the current unified scored dataset first; do not trigger a new market refresh unless the user explicitly wants fresher listings.
19. For buy-account decisions, separate `value_score` from `strength_score`: low-price accounts may win on value while losing on absolute strength.
20. Binding / unbind / delivery risk is a first-class decision factor; if two candidates are close in score, prefer the safer binding profile.
21. Team completeness and signature-weapon alignment matter more than raw five-star count. A smaller but complete two-team account can be a better buy than a scattered higher-count account.
22. When the user wants to compare a shortlist visually, generate a dedicated comparison HTML instead of asking them to inspect the full unified page manually.

## Standard Refresh Flow

### 1. Archive Previous Snapshot

Move old working outputs into:
- `game-account-evaluator/archive/refresh_<timestamp>/`

Archive at least:
- prior raw list pages
- prior detail captures
- prior scored JSON / CSV
- prior unified HTML

### 2. Capture Current List Rows

For each source, capture from the user-opened pages only:

- `PZDS`
  - read the already opened listing page
  - extract current `/goodsDetails/<id>/` rows, price, and publish time
  - do not refresh the page after the user has set filters

- `7881`
  - click the in-page `最新发布` button on the already opened page
  - then read the refreshed visible list from that same page state
  - extract `goods_id`, price, and publish time from the visible list items
  - do not re-open a replacement page if the user did not provide it

- `Kejinshou`
  - prefer API-first if valid tokens are available and the user allows it
  - when working from the browser page, click the in-page `最新发布` button first
  - then read the already opened listing page and extract current `/goods/details/<id>` rows
  - do not refresh the page after the user has set filters

### 3. Deduplicate Against Unified

For captured list rows:
- compare against `outputs/wuwa_unified_scored.json`
- separate rows into:
  - already fully scored rows
  - rows present but missing / incomplete score
  - truly new rows

Decision rules:
- if a row is already present locally and already has complete detail + score data, skip detail fetch by default
- if a row is present locally but detail fetch previously failed, parse failed, or score fields are incomplete, it may enter the detail-fetch stage
- if the user explicitly requests a full refresh or explicitly asks to re-update existing rows, existing scored rows may re-enter the detail-fetch stage

Only the second and third groups should enter the detail-fetch stage during normal incremental rounds.

### 4. Fetch Detail For Target Rows

List rows must be followed by detail fetch:

- `PZDS`
  - fetch the detail HTML page for each target `product_id`
  - parse role / weapon / resource / binding information from detail HTML

- `7881`
  - call the H5 detail API behind the page
  - extract summary fields, roles, weapons, and resource values from the API response

- `Kejinshou`
  - prefer official detail/API workflow when tokens are valid
  - otherwise use the current mobile detail page content and current listing title together to recover role / weapon / resource information

Before any source detail fetch begins:
- look up the row in `outputs/wuwa_unified_scored.json` by stable identity: `platform + product_id`
- if the row already exists with complete detail and score fields, skip detail fetch
- if the row does not exist, or exists but lacks complete detail / score fields, fetch detail and continue scoring

### 5. Score Detail Payloads

For each fetched detail row:
- build normalized role / weapon assets
- compute:
  - `role_score_total`
  - `weapon_score_total`
  - `strength_score`
  - `value_score`
- attach quality fields:
  - `can_rank`
  - `data_quality`
  - `detail_fetch_status`
  - `detail_fetch_label`

### 6. Handle Failures

If a row cannot produce any real score:
- do not write it into the final unified HTML output
- do not leave it as an empty incremental placeholder in unified delivery
- write it into an abnormal / excluded side output for debugging

### 7. Merge And Deliver

After scoring:
- merge scored rows into `outputs/wuwa_unified_scored.json`
- rebuild `outputs/wuwa_unified_review.html`
- optionally keep side outputs for abnormal rows:
  - `outputs/wuwa_unified_excluded_incomplete_rows.json`
  - `outputs/current_page_backfill_failures.json`

Task-complete deliverables:
- `outputs/wuwa_unified_scored.json`
- `outputs/wuwa_unified_scored.csv`
- `outputs/wuwa_unified_review.html`

Optional comparison deliverable:
- `outputs/wuwa_shortlist_compare.html`

## Comparison Workflow

When the user asks which account to buy:
1. open `outputs/wuwa_unified_scored.json`
2. if the market is not obviously stale, reuse current scored data instead of refreshing first
3. filter to the requested budget range and only keep rows that are still active and fully rankable
4. compare both `value_score` and `strength_score`; do not collapse them into a single judgment
5. inspect:
   - price bucket fit
   - role core, with emphasis on `T0/T0.5`
   - signature weapon completeness
   - team count and matched teams
   - pull reserves and unfinished resource space
   - account-binding risks and delivery constraints
6. recommend by:
   - actual playability now
   - roster retention value
   - team completeness
   - binding safety
   - whether the price is being carried by true strength or by discount
7. when the user wants a side-by-side handoff, generate `outputs/wuwa_shortlist_compare.html` from the selected shortlist

## Safety Notes

- Do not store fresh auth tokens inside the skill files.
- Do not overwrite raw snapshots without archiving when the user requests a refresh.
- If the user already set filters / sort in the browser, never refresh or reload that page.
- If `PZDS` direct fetches return WAF pages, keep list acquisition in browser and only continue if detail HTML still parses correctly.
- If a source cannot provide complete detail or complete scoring, stop and ask the user for help instead of silently shipping empty rows.

## Examples

Example triggers:
- "重新抓一下两个平台最新账号并重算"
- "现在很多号卖掉了，刷新统一榜"
- "我改了梯度规则，重算并更新 HTML"
- "比较统一榜前 5 哪个更值得买"
