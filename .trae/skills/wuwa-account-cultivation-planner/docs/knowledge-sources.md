# Knowledge Sources

## Primary Local Sources

Use local project knowledge first.

### Account State

- `game-account-evaluator/outputs/wuwa_unified_scored.json`
- shortlist comparison outputs when available

These already contain:
- owned roles
- owned weapons
- matched teams
- score-derived structure
- many seller-side account notes

### Cultivation Cache

- `game-account-evaluator/data/localized/role_cultivation/wuwa_role_cultivation.json`
- `game-account-evaluator/data/localized/role_cultivation/wuwa_role_cultivation_source.md`

Use these for:
- character build direction
- role positioning
- likely upgrade focus
- reusable build notes already localized into project data

## External Sources

### Kuro Wiki

Reference:
- `https://wiki.kurobbs.com/mc/home`

Useful sections visible from the home index include:
- character catalogue
- weapon catalogue
- echo catalogue
- guide collections
- task collections

Use the wiki mainly for:
- official or semi-official role / weapon reference lookup
- cultivation-material routing
- build mechanics confirmation
- echo and weapon details not yet normalized locally

Do not use the wiki as a replacement for local account-state parsing.

## Source Priority Rules

1. Use local structured account data for what the user owns.
2. Use local team and role knowledge already collected in the evaluator stack for roster inference.
3. Use external wiki sources for missing cultivation mechanics and lookup detail.
4. If local structured data and external references conflict, prefer the account-specific local state for ownership and prefer the external reference for generic mechanics.

## Missing-Data Policy

If planning depends on details not present in current sources, request only the smallest missing piece, for example:
- current weapon assignment
- current resonance / talent levels
- current echo sets
- current resource stock

Do not fabricate account-state details just because the wiki contains general build advice.
