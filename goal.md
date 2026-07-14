# Active Goal Baton

Status: **ACTIVE** (full reconstruction campaign)  
Last updated: 2026-07-14  
Policy: [`goal.policy.md`](goal.policy.md)  
Campaign map: [`goal.campaign.md`](goal.campaign.md)  
Slash prompt: [`roadmap/goals/full-rebuild-campaign-slash-goal.md`](roadmap/goals/full-rebuild-campaign-slash-goal.md)  
Integration baseline: `890a92c8` (turn/yaw harness + contract regression on main)

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
| Durable multi-slice campaign OS | landed | `goal.campaign.md`; slash-goal text; policy multi-slice mode |
| M1.3 turn/yaw harness scaffold + M8.3 contract regression | landed (partial M1.3) | `battleengine_turn_yaw_measurement.py` + tests; measurement plan; `battleengine_scalar_contract_regression.py` + tests on real walker/jet JSON |

## Current Slice

**ID:** `M1.3-live-turn-yaw-dual-accept`  
**Lane:** RE copied-runtime measurement → public contract (only if dual-accept)  
**Objective:** Wire turn input + yaw/heading sampling into the receipt-bound
live pair runner; obtain exactly two accepted copied-runtime turn/yaw attempts;
publish v1 retail contract + translation policy + Core **only** if both accept.
Use `tools/battleengine_turn_yaw_measurement.py` for analysis. Lab hygiene
strip after closeout. If live path is blocked (no game copy / input bind),
record well-formed `BLOCKED_*` and fall back to M1.5 transform timing harness
or M2.1 fire scaffolding — do not invent dual-accept.

**Constraints (always):**

- Never mutate Steam / original `BEA.exe`
- No release/tag from this baton alone
- No reopen walker/jet scalars without new evidence
- No thrash on AYA MSB4278 without new evidence
- Commit/push green waves when the durable slash goal authorizes and gates pass

## Progress log

### 2026-07-14 — ADVANCEMENT: M1.3 scaffold + M8.3 regression + prior wave push

**Decision:** Campaign priority #1 (land pending green work) then #3 (next
scalar measurement). Pending jet/hygiene/campaign wave was dirty on
`bd3072b7`; validated (64 Python unit tests + prior rebuild green), committed
and pushed as `248a875d`. For the next unit of work, full live turn dual-accept
needs input binding + orientation sampling not yet on the runner path; chose
actionable offline advance of **M1.3 harness** (measurement-before-Core
scaffold, no Core constant) and **M8.3** landed-contract regression driving
real walker v2 + jet v1 JSON entry points.

**Landed this cycle:**

- `tools/battleengine_turn_yaw_measurement.py` + unit tests (heading, rates,
  analyze, pair envelope scaffold with explicit non-claims)
- `reverse-engineering/game-mechanics/walker-turn-yaw-scalar-measurement-plan.md`
- `tools/battleengine_scalar_contract_regression.py` + tests (CLI + real
  contracts)
- Gates: turn/yaw + contract tests OK; no live lab this cycle
  (`{SCRATCH}/no-live-lab.txt`)
- No multi-GB trees created; Steam untouched

**Closeout class:** `ADVANCEMENT` (harness + docs + regression checker).  
**Not claimed:** live dual-accept turn contract; Core turn rate; campaign exit.

### 2026-07-14 — Campaign structure stand-up

- Introduced durable `goal.campaign.md` multi-lane milestone map.
- Canonical slash text under `roadmap/goals/`.

## Lane bias accounting

| Last 3 slices | Lanes |
|---------------|--------|
| jet + campaign OS land | RE + rebuild + docs |
| turn/yaw harness + contract regression | RE harness + M8 harness |
| (next) live turn dual-accept | RE measurement |

## Resume checklist (new session / after compact)

- [x] `git log -1 --oneline` / status (baseline `890a92c8`)
- [x] Read policy + campaign + this file
- [x] Confirm Steam not a write target
- [ ] Execute Current Slice (live turn dual-accept — next session)
- [ ] Mutate this file before ending that cycle
