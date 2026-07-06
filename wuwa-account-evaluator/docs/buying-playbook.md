# Buying Playbook

## Goal

This playbook covers the reusable "find account -> compare account -> decide whether to buy" workflow for the current Wuwa evaluator stack.

Use it when the user asks:
- which account is more worth buying
- whether a specific listing is worth the money
- which shortlist in a target price band is better
- to generate a dedicated comparison page for several candidate accounts

## Decision Principle

Do not judge a candidate by raw five-star count alone.

Always split the decision into four layers:
1. price and budget fit
2. actual playable strength
3. roster / weapon completeness
4. delivery and binding risk

## Core Heuristics

### 1. Separate Value From Strength

- `value_score` answers whether the account is cheap for what it offers.
- `strength_score` answers how strong the account actually is.
- A low-price account can rank very high on value while still not being the strongest roster in the bucket.
- When the user wants a purchase recommendation, always mention both.

### 2. Prefer T0 / T0.5 Retention

- Give more weight to `T0` and `T0.5` roles than to total five-star count.
- In current practice, accounts with multiple preserved `T0/T0.5` roles stay valuable longer than accounts full of `T1/T2` filler.
- Treat `T2` as optional upside, not core justification for price.

### 3. Team Completeness Beats Scattered Assets

- Prefer accounts that already form at least one complete, coherent team.
- Two real teams with matching supports are often more valuable than a larger but fragmented roster.
- `team_count`, `team_bonus`, and `matched_teams` should be read as strong buy signals, not just decoration.

### 4. Signature-Weapon Alignment Matters

- Do not only count weapons; check whether the important carry roles have their matching signature or near-signature coverage.
- A role with its signature weapon often converts into better real playability than adding another side-grade five-star role.
- Mention signature alignment explicitly in the recommendation.

### 5. Binding Risk Can Override Small Score Differences

- Binding / unbind /实名 /换绑 constraints are first-class risk factors.
- If two accounts are close in value and strength, prefer the one with cleaner delivery conditions.
- When a listing has unclear binding fields, do not assume it is safe. Call that out as unresolved risk.

### 6. Resource And Future Growth Still Matter

- Pull reserves, unfinished exploration, anniversary event backlog, and coral/wave inventory are real future value.
- Treat them as secondary upside, not primary justification.
- If the seller's text mentions future resources, ask the user to verify them before purchase.

## Recommended Comparison Flow

1. Reuse `outputs/wuwa_unified_scored.json` unless the user explicitly asks for fresher market data.
2. Filter to:
   - target price range
   - `market_status = active`
   - `can_rank = true`
3. Build a shortlist by `value_score`, then cross-check with `strength_score`.
4. For each candidate, inspect:
   - `price`
   - `unified_rank`
   - `value_score`
   - `strength_score`
   - `team_count`
   - `matched_teams`
   - `roles`
   - `weapons`
   - binding / security fields
5. Explain the decision in plain language:
   - who is strongest
   - who is most cost-effective
   - who is safest to receive
   - who is best for immediate play
6. If the user wants visual comparison, generate `outputs/wuwa_shortlist_compare.html`.

## What To Say In Recommendations

A good recommendation should answer:
- Is this account worth buying at this price?
- Is it winning because it is cheap, or because it is truly strong?
- What is the biggest risk?
- What should the buyer verify before paying?

## Pre-Purchase Checklist

Before telling the user to buy, remind them to verify:
- current sale status is still active
- account binding / unbind condition
- delivery method and whether any cooldown remains
- whether the key roles and weapons in the parsed detail really match the listing
- whether seller-claimed future resources are actually present
- whether package protection / compensation applies

## HTML Handoff

When generating a dedicated comparison page:
- keep the selected shortlist order stable
- show price, rank, value, strength, teams, core roles, signature weapons, and safety summary
- keep the page standalone and readable without opening the full unified review
- save to `outputs/wuwa_shortlist_compare.html` unless the user asks for a different path

## Common Mistakes To Avoid

- Do not recommend based only on `unified_rank`.
- Do not hide binding uncertainty behind a high score.
- Do not overvalue filler five-stars.
- Do not treat seller text as verified fact.
- Do not refresh the market when the user only wants comparison on existing data.
