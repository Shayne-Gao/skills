# AGENTS.md

This file defines workspace-level execution rules for work under `life_skills/`.

## Delivery Validation Rule

- After any code, page, data, or UI change that the user may need to inspect, the assistant must leave the user with a directly verifiable result before handoff.
- Preferred order:
  1. Start a local preview/dev server and provide the exact accessible URL.
  2. If the project is already publishable, push the latest result and provide the online verification URL.
- It is not enough to only say "done", "build passed", or only paste local commands for the user to run later.
- If a local preview cannot be started and an online publish is not possible, the assistant must explicitly explain the blocker and ask the user before stopping.

## Default Behavior For This Workspace

- For frontend / HTML / demo changes, default to starting local preview if possible, and also share the online URL when already pushed.
- For repository updates that are meant to be user-checked, prefer completing the push workflow instead of stopping after code edits.
