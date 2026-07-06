---
name: "wuwa-account-cultivation-planner"
description: "Turns an owned Wuthering Waves account into cultivation priorities and team-building plans. Invoke when user wants build advice, upgrade order, or resource planning for an account."
---

# Wuwa Account Cultivation Planner

This skill plans how to turn an owned Wuthering Waves account into practical cultivation advice.

Use this skill when the user wants to:
- turn an owned account into a team plan
- ask what to build first on a purchased account
- ask for character / weapon / echo / resource priorities
- ask for short-term, mid-term, or long-term cultivation routes
- ask whether a roster already supports one or two complete teams

## Scope

The workflow covers:
- ingesting an owned account snapshot
- identifying current playable teams from owned roles and weapons
- ranking cultivation priorities by actual account value
- planning role, weapon, echo, and resource investment order
- producing phased guidance for immediate, short-term, and medium-term goals

## Non-Goals

This skill is not for:
- refreshing market listings from buy/sell platforms
- re-running market ranking for all listings
- generic wiki mirroring without account-specific recommendations

For those tasks, continue to use `wuwa-account-evaluator`.

## Current Default Target

The user's currently owned account is `35112357`, already purchased and unbound.  
When no other account is specified, default to planning for that account.

## Workspace References

Primary project root:
- `game-account-evaluator/`

Relevant data and docs:
- `game-account-evaluator/outputs/wuwa_unified_scored.json`
- `game-account-evaluator/outputs/wuwa_shortlist_compare.html`
- `game-account-evaluator/data/localized/role_cultivation/wuwa_role_cultivation.json`
- `game-account-evaluator/data/localized/role_cultivation/wuwa_role_cultivation_source.md`
- `docs/input-spec.md`
- `docs/knowledge-sources.md`
- `docs/priority-model.md`
- `docs/workflow.md`
- `docs/planning-playbook.md`

## Operating Rules

1. Start from the owned account state, not from market-comparison logic.
2. Reuse existing structured roster / weapon / team data before reaching for external sources.
3. Treat local team and role knowledge already collected in the evaluator stack as the primary source for team inference.
4. Use external wiki knowledge mainly for cultivation mechanics, material routes, and build details.
5. Separate advice into:
   - what is already playable now
   - what should be upgraded first
   - what can wait
6. Prefer recommendations that improve one complete team at a time instead of spreading resources thin.
7. If build advice depends on missing account details, ask for the smallest missing input instead of guessing.
8. Make recommendations with concrete account context:
   - owned roles
   - owned weapons
   - current team coverage
   - likely resource bottlenecks
9. If the user asks for a written handoff, produce a concise action-oriented plan rather than only theory.
10. The task should always be handled in three stages:
   - understand the account input state
   - understand current-version team / role cultivation priority
   - convert both into account-specific upgrade order
11. Distinguish team priority from growth-factor priority:
   - team priority answers who should be built first
   - growth-factor priority answers whether to invest first in level, skill, weapon, or echo
12. Recommendations should include a concrete "current completion estimate" when enough information exists, even if the estimate is only approximate.

## Typical Inputs

The skill may use any of these:
- an owned account already present in `wuwa_unified_scored.json`
- a shortlist / comparison result already generated in project outputs
- pasted screenshots or text summaries from the user
- local cultivation data caches
- approved external knowledge sources such as the Kuro wiki

## Input Levels

Minimum viable input:
- current owned roles
- current owned weapons

Preferred richer input:
- character levels
- weapon levels
- skill / forte levels
- current echo sets or notable echo quality
- current resource stock and bottlenecks

The skill should degrade gracefully:
- if only roles and weapons are known, produce team-first and role-first guidance
- if levels / skills / echoes are also known, produce finer per-character upgrade steps

## Task Breakdown

The skill should complete all of these:

### 1. Understand Current-Version Priority

First determine current-version cultivation priority in this order:
- highest priority: top-tier teams in the current version
- second priority: high-potential key roles, including strong new roles
- third priority: older-version teams and lower-retention fallback options

### 2. Understand Growth-Factor Priority

For each target character, evaluate the relative impact of:
- skill / forte levels
- character level / ascension
- weapon level
- echo setup and echo quality

The goal is to identify which factor gives the largest account-strength gain first.

### 3. Produce Account-Specific Advice

For the target account, convert the above into:
- priority cultivation targets
- team-based build order
- per-character next-step order
- explicit "what to do first, second, third"

## Typical Outputs

- recommended main team and backup team
- prioritized target team list by current-version value
- character upgrade priority
- per-character current-state summary and rough completion estimate
- weapon assignment priority
- echo / set direction
- immediate farming to-do list
- short-term and mid-term progression route
- risk notes about over-investing in low-retention units

## Examples

Example triggers:
- "这个号先养谁"
- "帮我做个培养优先级"
- "我这套号两队怎么组"
- "按这个账号给我做未来两周养成计划"
- "这个已购账号先升角色还是先补武器"
- "按当前版本优先级给我排这个号的培养顺序"
