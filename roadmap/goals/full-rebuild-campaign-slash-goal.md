# Durable slash goal — Full reconstruction campaign

Status: **canonical `/goal` text**  
Last updated: 2026-07-14  
Campaign map: [`goal.campaign.md`](../../goal.campaign.md)  
Policy: [`goal.policy.md`](../../goal.policy.md)  
Mutable baton: [`goal.md`](../../goal.md)

## How to invoke

In Grok Build (or any agent with `/goal`), set the objective to the **verbatim
block** below (or: “Execute the durable slash goal in
`roadmap/goals/full-rebuild-campaign-slash-goal.md`”).

Re-use the **same** text every session. Do not rewrite a one-off single-slice
goal unless you intentionally pause the campaign.

---

## Verbatim `/goal` objective

```text
Execute the durable Full Reconstruction Campaign for Battle Engine Aquila / Onslaught Toolkit.

Authority files (read in order, then work):
1) goal.policy.md — charter, payload boundary, closeout rules
2) goal.campaign.md — long-horizon milestones across RE, rebuild, WinUI 3, lore, harnesses
3) goal.md — mutable baton: current slice, closed ledger, progress; you MUST mutate this file every cycle
4) AGENTS.md + nearest nested AGENTS.md for path-scoped rules
5) Only the docs/code needed for the active slice (do not load all of RE-INDEX history by default)

Mission: aggressively reverse engineer, rebuild, and productize toward a growing evidence-backed reconstruction — not a single slice. After each ADVANCEMENT or resolved BLOCKED, pick the next slice yourself using goal.campaign.md priority order. Cover RE measurement/contracts, rebuild Core/Client/Godot, WinUI 3 toolkit, lore/knowledge packaging, and durable testing harnesses as the campaign requires. Continue across many slices until campaign exit criteria in goal.campaign.md are met or a well-formed BLOCKED_* record is the honest stop.

Decision rights: you choose slice scope, lane (RE / rebuild / WinUI / lore / harness), tools, and validation gates within policy. Prefer measurement-before-Core for retail-derived behavior. Prefer smallest gate that proves the contract. Build or extend unit/integration/runtime harnesses with each land so regressions stay caught. Keep lab disk bounded: safe-copy while running; strip profile-app-config and runner bin/obj after closeout; compact evidence only.

Hard constraints:
- Never mutate installed Steam / original BEA.exe; copied targets only
- No release, tag, public announcement, or installer/signing from this campaign unless a newer human message explicitly authorizes that family
- Do not claim parity-complete, strict clean-room, or player-ready online; Host/Join stays disabled until accepted distinct-endpoint proofs
- Do not thrash known hard blockers (e.g. AYA MSB4278) without new evidence
- Do not reopen closed walker/jet scalar paths unless new evidence overturns them
- Prefer compact private evidence; do not leave multi-GB proof trees after closeout
- No hosted CI/GitHub Actions scaffolding
- Commit and push green waves when this goal + repo policy allow (green local gates, no hard payloads, honest docs); do not force-push; do not amend published history without explicit extra authority

Each cycle:
1. Read policy + campaign + goal.md; recover baseline git SHA
2. Select or continue exactly one Current Slice; write it into goal.md before large edits
3. Implement + validate (serial .NET builds/tests; npm run test:rebuild after Core changes; focused Python/WinUI gates as needed)
4. Update goal.md (progress, closed ledger) and goal.campaign.md milestone status when a milestone lands
5. Close the cycle with ADVANCEMENT or a well-formed BLOCKED_* record per goal.policy.md
6. If ADVANCEMENT and gates green, commit/push when authorized by this goal, then immediately select the next slice and continue until you must stop (exit criteria, BLOCKED needing human, or context limit — leave goal.md ready for resume)

Resume contract: if the session is new or compacted, trust goal.md + goal.campaign.md over chat memory. Never restart the campaign from zero.
```

---

## Short alias (same campaign)

If the host truncates long goals, use:

```text
Run the durable campaign in roadmap/goals/full-rebuild-campaign-slash-goal.md (verbatim objective). Mutate goal.md every cycle; follow goal.policy.md + goal.campaign.md until exit or BLOCKED.
```

## Operator notes

- **Pause campaign:** `/goal pause` or set `goal.md` Status to `PAUSED` with reason.
- **Single-slice detour:** temporarily replace Current Slice in `goal.md` only;
  do not replace the campaign files unless you mean to end the campaign.
- **Commit authority:** the verbatim block grants green-wave commit/push under
  repo payload rules; revoke by editing this file or sending a newer human rule.
