# Scoring Rules

## Current Role Model

Role strength uses three-list blending:
- overall list weight: `0.4`
- tower list weight: `0.3`
- requiem list weight: `0.3`

Tier score mapping:
- `T0 = 120`
- `T0.5 = 90`
- `T1 = 40`
- `T2 = 10`
- `T3/T4/T5 = 0`

Mode grade mapping:
- `EX = 120`
- `SS = 90`
- `S = 40`
- `A = 10`
- `B/C = 0`

Four-star factor:
- `0.5`

Resonance multiplier:
- `0 = 1.0`
- `1 = 1.4`
- `2 = 1.7`
- `3 = 1.95`
- `4 = 2.15`
- `5 = 2.3`
- `6 = 2.4`

Manual role adjustments come from:
- `game-account-evaluator/configs/wuwa_role_adjustments_33.json`

Role tier source comes from:
- `game-account-evaluator/configs/wuwa_role_tiers_corrected.json`

## Weapon Model

Signature weapon base score:
- owner `T0 = 60`
- owner `T0.5 = 50`
- owner `T1 = 30`
- owner `T2 = 10`

Standard 5-star weapon:
- `20`

Weapon refine uses the same diminishing multiplier model as role resonance.

Weapon catalog source:
- `game-account-evaluator/configs/wuwa_weapon_catalog.json`

## Pull Model

Current pull rules:
- `160 星声 = 1 抽`
- `浮金波纹 = 1.0`
- `铸潮波纹 = 0.8`
- `唤声涡纹 = 0`

This reflects the current preference that standard-pool pulls should not contribute to valuation, while weapon-banner pulls are discounted relative to character-banner pulls.

## Team Synergy Model

Team-synergy source:
- `game-account-evaluator/configs/wuwa_team_synergy_33.json`

Rules:
- a full team only counts when all three positions are satisfied
- each position can contain one or more acceptable role options
- each matched full team adds:
  - `team_count + 1`
  - `strength_score + 100`

Unified report should expose:
- `team_count`
- `team_bonus`
- `matched_teams`

## Final Strength Formula

For each account:

```text
strength_score =
  pulls_total
  + role_score_total
  + weapon_score_total
  + team_bonus
```

```text
value_score = strength_score / price
```

## Review Priorities

When recommending purchases, prioritize:
1. high-retention `T0/T0.5` role concentration
2. team completeness
3. signature-weapon completeness
4. clean binding state
5. remaining pull reserve
