# Active Goal Baton

Status: **ACTIVE** (full reconstruction campaign)  
Last updated: 2026-07-14  
Policy: [`goal.policy.md`](goal.policy.md)  
Campaign map: [`goal.campaign.md`](goal.campaign.md)  
Slash prompt: [`roadmap/goals/full-rebuild-campaign-slash-goal.md`](roadmap/goals/full-rebuild-campaign-slash-goal.md)  
Integration baseline (last closed dual-accept land on main tip may lag): dirty tree post jet-p06 / pending commit

## How this baton works

This file is the **mutable** `/goal` working memory. Every cycle must:

1. Read `goal.policy.md` then `goal.campaign.md` then this file.
2. Execute **Current Slice** only (one bounded unit of work).
3. On closeout: record `ADVANCEMENT` or `BLOCKED_*`, update ledgers, **rewrite
   Current Slice** to the next campaign pick (agent decision — do not wait for
   a human to invent the next slice unless blocked).
4. Update `goal.campaign.md` milestone status when a milestone lands or blocks.

The campaign **does not end** when one slice lands. Continue until
`goal.campaign.md` exit criteria or a well-formed blocker requiring a human.

## North star (one line)

Evidence-backed reverse engineering → accepted contracts → deterministic Core /
rebuild clients → WinUI toolkit + lore usefulness, with harnesses and lab
hygiene, without touching Steam/original `BEA.exe` or claiming false parity.

## Closed ledger (do not re-open without overturning evidence)

| Slice | Result | Artifacts |
|-------|--------|-----------|
| Walker forward scalar | landed | v2 contract; policy; `WalkerSpeedPerTick=100`; p27-compact |
| Jet forward/thrust scalar | landed | v1 contract; policy; `JetSpeedPerTick=381`; jet-p06 compact |
| Runtime proof lab hygiene | landed | `runtime_proof_lab_hygiene.py`; retention doc; runner strip |

## Current Slice

**ID:** `M1.3-turn-yaw-or-next-actionable`  
**Lane:** RE measurement → contract (rebuild-grade), with harness first  
**Objective:** Pick and execute the highest-priority **actionable** open
milestone from `goal.campaign.md` (default target: **M1.3 turn/yaw rate
scalar**). If turn/yaw tooling is not yet feasible, auto-fallback in order:
M1.5 transform timing, M2.1 fire/projectile retail contract scaffolding,
M5.3 Home native-focus only if native authority exists, M8.3 harness for
landed walker/jet contracts, then WinUI/lore polish that unblocks users.

**Required this slice:**

1. Write a one-paragraph decision in Progress log: which milestone and why
   (cite campaign priority order).
2. Prefer measurement-first if retail-derived; dual-accept before Core.
3. Add/extend a durable test harness for whatever lands.
4. Lab hygiene if live BEA is used (strip bulky trees; compact only).
5. Close with `ADVANCEMENT` or well-formed `BLOCKED_*`; then set the **next**
   Current Slice without human rewrite.

**Constraints (always):**

- Never mutate Steam / original `BEA.exe`
- No release/tag from this baton alone
- No reopen walker/jet scalars without new evidence
- No thrash on AYA MSB4278 without new evidence
- Commit/push green waves when the durable slash goal authorizes and gates pass

## Progress log

### 2026-07-14 — Campaign structure stand-up

- Introduced durable `goal.campaign.md` multi-lane milestone map.
- Expanded `goal.policy.md` for multi-slice autonomous campaign loops.
- Canonical slash text:
  `roadmap/goals/full-rebuild-campaign-slash-goal.md`.
- Prior dual-accept lands: walker p27, jet-p06; hygiene tooling.
- **Next agent:** execute Current Slice (turn/yaw or documented fallback).

### 2026-07-14 — Jet + hygiene ADVANCEMENT (pre-campaign file)

- See closed ledger; working tree may still need commit/push of that wave.

## Lane bias accounting

| Last 3 slices | Lanes |
|---------------|--------|
| jet scalar | RE + rebuild |
| lab hygiene | harness |
| campaign stand-up | docs/operating system |

Next picks should prefer **M1.x RE measurement** or **harness for landed
contracts** before another pure docs slice.

## Resume checklist (new session / after compact)

- [ ] `git log -1 --oneline` / status
- [ ] Read policy + campaign + this file
- [ ] Confirm Steam not a write target
- [ ] Execute Current Slice; do not re-litigate closed ledger
- [ ] Mutate this file before ending the cycle
