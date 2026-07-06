# Workflow

## End-to-End Flow

1. Identify the target account.
2. Load owned roles, weapons, teams, and market-derived structured fields.
3. Classify the available input tier for the account state.
4. Determine what is already playable now.
5. Rank the highest-value team or role to complete first using the current-version priority model.
6. For each priority target, decide whether the next biggest gain comes from skill, level, weapon, or echo.
7. Build phased cultivation advice:
   - immediate fixes
   - short-term upgrade order
   - medium-term account growth
8. Add resource and farming focus.
9. Output a concise, actionable plan.

## Input Priority

Use sources in this order:

1. account rows already present in `game-account-evaluator/outputs/wuwa_unified_scored.json`
2. local structured cultivation caches
3. user-provided screenshots or corrections
4. approved external references such as the Kuro wiki

## Input Classification

Before planning, classify the input as:
- Tier 1: roster-only
- Tier 2: upgrade-state aware
- Tier 3: full planning input

This determines how specific the final advice can be.

## Account Analysis Flow

### 1. Read Current Assets

For the target account, gather:
- owned five-star roles
- owned weapons and signature alignment
- matched teams
- level / yellow count / pull reserves when available
- any binding-independent account notes relevant to planning

### 2. Identify Playable Core

Before recommending upgrades, answer:
- which team is already closest to completion
- which carry has the strongest support and weapon backing
- whether the account supports one stable team or two usable teams
- which units are high-retention and worth long-term investment
- which current-version top team is realistically reachable first

### 3. Rank Priorities

Sort priorities by impact:

1. complete the main team
2. secure the main carry's weapon and support coverage
3. raise the highest-value sub DPS / support pieces
4. expand into the second team
5. only then spend meaningfully on filler or low-retention units

Within each target role, then rank:
1. highest-impact skill / forte branch
2. level / ascension breakpoint
3. weapon level breakpoint
4. deeper echo finishing

### 4. Translate Into Action

Convert analysis into an actionable route:
- who to level first
- who to ascend first
- whose talents / forte tree to prioritize
- which weapon to assign and upgrade first
- which echo direction to farm first
- which units can stay at temporary investment
- what rough completion percentage the key role is currently at, if enough fields exist

## Default Output Shape

Prefer this structure when answering:

1. overall judgment on the account's current shape
2. main team recommendation
3. backup / second-team recommendation
4. cultivation priority list
5. weapon and echo notes
6. next 1-2 weeks farming focus
7. avoid-investing / wait-and-see notes

## Compare-To-Plan Bridge

If the user first asked which account to buy and then asks how to build it:
- stop using market-selection logic as the main lens
- switch to owned-account optimization
- treat the purchased account as the fixed target
- re-evaluate value in terms of account growth, not market resale
