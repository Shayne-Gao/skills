# Input Spec

## Goal

Define what the cultivation-planning skill expects as account input, from minimum viable account state to richer planning-grade account state.

## Minimum Input

The minimum viable input for planning is:
- owned roles
- owned weapons

With only these two, the skill should still be able to:
- identify likely main-team candidates
- identify likely second-team direction
- rank high-value roles for cultivation first
- produce rough role-first recommendations

## Preferred Input

For better planning quality, also capture:
- character levels
- character ascension state
- skill / forte levels
- weapon levels
- current echo sets
- current echo quality or graduation estimate
- current resource stock
- known bottlenecks such as credits, EXP, talent mats, or echo exp

## Input Tiers

### Tier 1: Roster-Only

Contains:
- roles
- weapons

Can produce:
- team-first priority
- role-first priority
- rough weapon assignment

Cannot produce with high confidence:
- exact per-character upgrade step order
- current completion percentage
- precise echo optimization advice

### Tier 2: Upgrade-State Aware

Contains:
- Tier 1
- levels
- skill / forte state
- weapon levels

Can produce:
- per-character next-step order
- whether the next gain comes more from skill, level, or weapon
- rough current completion estimate

### Tier 3: Full Planning Input

Contains:
- Tier 2
- echo sets / echo quality
- resource stock

Can produce:
- detailed short-term cultivation route
- per-character finishing sequence
- farming focus and opportunity cost advice

## Missing-Data Strategy

If the input is incomplete:
- do not guess hidden account details
- give the best recommendation allowed by the current input tier
- explicitly state what extra fields would improve precision

## Example Input Framing

Good compact input:
- account owns A/B/C/D roles
- account owns X/Y/Z weapons

Good richer input:
- A level 80, weapon 90, skills 6/8/8/8/6
- B level 70, weapon 70, key skill still low
- main team echo set incomplete

## Output Mapping

The planning output should adapt to the input tier:
- Tier 1 -> team and role order
- Tier 2 -> team order + per-character growth factor order
- Tier 3 -> full cultivation roadmap with farming focus
