# PM Superpower Recovery Plan

Status: active
Audience: PM, engineering, design, leadership
Owner: ProductOS PM
Updated At: 2026-04-09

## Assessment

This review excluded `workspaces/` and focused on the ProductOS core repo plus the reference workspace.

Current repo reality is strong on contracts, schemas, workflows, tests, and bounded release posture.

Current repo reality is weaker on the PM-first entry surface:

1. there was no canonical mission intake artifact capturing the few high-signal PM questions
2. the CLI started from phase commands instead of one PM-first mission surface
3. the repo lacked the `AGENTS.md` map that the vendor-neutral harness standard says every agent-capable ProductOS repo should define
4. the reference plan already described superpowers, but the mission framing was still implicit across docs and artifacts

## Ralph Loop x11

1. Inspect: confirmed the repo is broad and mostly healthy, but the execution surface is still expert-facing.
2. Inspect: verified `README.md`, `scripts/productos.py`, and `core/docs/next-version-superpower-model.md` all point to `CLI + repo first`.
3. Inspect: confirmed there was no PM-first mission artifact or `init-mission` command.
4. Inspect: confirmed the reference workspace carries real phase outputs but no single canonical “few questions” brief.
5. Refine: narrowed the recovery scope to one bounded slice that improves onboarding without over-claiming autonomy.
6. Refine: rejected a broad autonomous-PM implementation because it would widen claims faster than proof.
7. Refine: rejected UI-first work because the repo standard remains CLI-first.
8. Refine: selected a repo-native mission intake contract plus command as the highest-leverage next step.
9. Implement plan: add `mission_brief` schema, example, template, reference artifact, and markdown surface.
10. Implement plan: add `./productos init-mission`, mission visibility in CLI status surfaces, and mission-aware next-version context.
11. Validate plan: keep the change bounded with tests, docs, and agent guidance rather than broadening release claims.

## Final Plan

1. make the PM-first mission explicit in-repo
2. give the CLI a mission-initialization command that captures the few high-signal questions
3. wire that mission into status and context generation so downstream phases inherit the same intent
4. document the repo map for Codex, Claude, Windsurf, and Antigravity style agents
5. keep the broader autonomous PM claim set deferred until repeated outcome proof exists

## Implemented Slice

- added `mission_brief` as a first-class artifact contract
- added `./productos init-mission` as the new PM-first entrypoint after workspace creation
- updated the reference workspace to carry the mission explicitly
- updated next-version context generation so the mission brief influences the bounded baseline
- added `AGENTS.md` so approved agent tools have one short repo map instead of relying on prompt lore

## Next Follow-On Work

1. drive `run discover` directly from `mission_brief` when the workspace has no richer artifact set yet
2. extend adoption so `adopt-workspace` can infer a first-pass mission brief from legacy notes-first folders
3. add score-bearing checks for mission freshness and mission-to-output traceability
