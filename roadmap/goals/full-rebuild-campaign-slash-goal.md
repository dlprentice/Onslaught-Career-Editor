# Durable slash goal — Full reconstruction campaign (multi-slice marathon)

Status: **canonical `/goal` text**  
Last updated: 2026-07-15  
Campaign map: [`goal.campaign.md`](../../goal.campaign.md)  
Policy: [`goal.policy.md`](../../goal.policy.md)  
Mutable baton: [`goal.md`](../../goal.md)

## How to invoke

Paste the **verbatim** block into `/goal` every session. Same text forever.
Do **not** invent a single-slice goal (“do M1.4 only”) unless you want a short detour.

---

## Verbatim `/goal` objective

```text
MARATHON MODE — Full Reconstruction Campaign (Battle Engine Aquila / Onslaught Toolkit).

This is NOT a one-slice goal. A single ADVANCEMENT, one commit, or one dual-accept is routine progress, NOT completion. Do NOT call the goal complete, update_goal(completed), or stop after one slice. Keep working slice after slice in the same session.

Authority (read every cycle, in order):
1) goal.policy.md
2) goal.campaign.md
3) goal.md  ← MUST mutate every cycle (progress, closed ledger, next Current Slice)
4) AGENTS.md + nearest nested AGENTS.md
5) Only slice-local docs/code (do not bulk-load historical RE-INDEX)

Resume: trust goal.md + goal.campaign.md over chat. Start from Current Slice (now M1.4-strafe / M1.5-transform fallback). Never restart the campaign from zero. Do not reopen closed walker-forward, jet-thrust, or Look/Left yaw dual-accepts without overturning evidence.

Mission: run a continuous loop of bounded slices that advances RE, rebuild Core/Client/Godot, WinUI 3, lore, and harnesses per goal.campaign.md priority. After EVERY slice closeout:
  → commit/push if green and authorized
  → immediately pick the NEXT actionable slice
  → rewrite goal.md Current Slice
  → execute it
  → repeat

MINIMUM SESSION QUOTA (hard):
- Complete at least FIVE (5) distinct slice closeouts this session (each ADVANCEMENT or well-formed BLOCKED_* counts as one), OR keep going until a real stop condition below.
- Prefer more than five when context allows. One dual-accept + stop is a FAIL against this goal.
- After each closeout, do not “hand back” for human permission to continue; continue automatically.

Stop ONLY when one of these is true (and then leave goal.md resume-ready):
1) Campaign exit criteria in goal.campaign.md are actually met AND you document that honestly (still rare; do not fake exit), OR
2) A well-formed BLOCKED_* needs human authority (Steam/risk lease, release, paid spend, exhausted retries with new evidence), OR
3) Hard context/session limit — baton rewritten for resume, next slice named, no “campaign done” claim, OR
4) Human says pause.

FORBIDDEN “fake done” patterns:
- Treating one milestone land as goal complete
- update_goal(completed) after a single slice without meeting MINIMUM SESSION QUOTA or a real stop condition
- Stopping because “next slice is ready for another agent”
- Re-litigating closed scalars for busywork
- Inventing dual-accept or Core from source defaults alone

Decision rights: choose slice scope within campaign priority; measurement-before-Core for retail-derived behavior; dual-accept → public contract → translation policy → Core; co-land harnesses; lab hygiene (safe-copy live; strip profile-app-config + runner bin/obj after closeout; compact only).

Hard constraints:
- Never mutate Steam / original BEA.exe; copied targets only
- No release/tag/public announcement/installer/signing unless newer human text explicitly authorizes that family
- No parity-complete, strict clean-room, or player-ready online claims; Host/Join stays disabled
- No thrash on AYA MSB4278 without new evidence
- No hosted CI/GitHub Actions scaffolding
- Commit and push green waves when this goal + repo policy allow (no force-push; no amend of published history)

Slice loop (repeat):
1. Read policy + campaign + baton; note git tip
2. Confirm or write Current Slice in goal.md
3. Implement + smallest proving gates (serial .NET; npm run test:rebuild after Core; focused Python/WinUI)
4. ADVANCEMENT or well-formed BLOCKED_*; update goal.md + milestone status
5. Commit/push if green
6. Immediately start the next slice — do not wait for the human

When you finally stop under a real stop condition, report: slices closed this session, tip SHA, baton Current Slice, and that the campaign remains ACTIVE unless exit criteria truly hold.
```

---

## Short alias

```text
/goal Marathon: roadmap/goals/full-rebuild-campaign-slash-goal.md. Multi-slice only — min 5 slice closeouts this session; do NOT mark complete after one ADVANCEMENT. Mutate goal.md every cycle; continue until real stop (exit criteria / human BLOCKED / context). Start at goal.md Current Slice.
```

## Operator notes

- **Why sessions used to die early:** harness “goal done” after one planned unit. This text forbids that and sets a **minimum of 5 slice closeouts**.
- **Pause:** `/goal pause` or set `goal.md` Status to `PAUSED`.
- **Commit authority:** green-wave commit/push granted under payload rules; no force-push.
