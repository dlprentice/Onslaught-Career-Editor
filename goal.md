# Active Goal Baton

Status: **ACTIVE** (full reconstruction campaign)  
Last updated: 2026-07-14  
Policy: [`goal.policy.md`](goal.policy.md)  
Campaign map: [`goal.campaign.md`](goal.campaign.md)  
Slash prompt: [`roadmap/goals/full-rebuild-campaign-slash-goal.md`](roadmap/goals/full-rebuild-campaign-slash-goal.md)  
Integration baseline: pending push of turn-p02 dual-accept wave (builds on `71c85101`)

## How this baton works

This file is the **mutable** `/goal` working memory. Every cycle must:

1. Read `goal.policy.md` then `goal.campaign.md` then this file.
2. Execute **Current Slice** only (one bounded unit of work).
3. On closeout: record `ADVANCEMENT` or `BLOCKED_*`, update ledgers, **rewrite
   Current Slice** to the next campaign pick.
4. Update `goal.campaign.md` milestone status when a milestone lands or blocks.

## North star (one line)

Evidence-backed reverse engineering → accepted contracts → deterministic Core /
rebuild clients → WinUI toolkit + lore usefulness, with harnesses and lab
hygiene, without touching Steam/original `BEA.exe` or claiming false parity.

## Closed ledger (do not re-open without overturning evidence)

| Slice | Result | Artifacts |
|-------|--------|-----------|
| Walker forward scalar | landed | v2; `WalkerSpeedPerTick=100`; p27 |
| Jet forward/thrust scalar | landed | v1; `JetSpeedPerTick=381`; jet-p06 |
| Runtime proof lab hygiene | landed | strip helpers + retention |
| Durable multi-slice campaign OS | landed | `goal.campaign.md` + slash text |
| M1.3 turn/yaw harness scaffold + M8.3 regression | landed | offline harness + contract CLI |
| **M1.3 live Look/Left yaw dual-accept** | **landed** | turn-p02; v1 contract; policy; `WalkerLookYawRateMilliRadPerTick=3` |

## Current Slice

**ID:** `M1.4-strafe-lateral-or-M1.5-transform`  
**Lane:** RE measurement-first (preferred) or harness  
**Objective:** Next motion scalar after closed walker forward, jet thrust, and
Look/Left yaw. Prefer **M1.4 strafe/lateral** dual-accept using Movement/Left
bound path + position lateral speed, reusing pair runner measure mode. If
strafe tooling is blocked after one real attempt, fall back to **M1.5 transform
timing** harness (morph state 1→3 latency already partially instrumented).

**Constraints:** Steam untouched; no Core without dual-accept; no walker/jet
forward reopen; lab hygiene strip; commit/push when green.

## Progress log

### 2026-07-14 — ADVANCEMENT: M1.3 live turn-p02 dual-accept → Core

**Decision:** Campaign priority next scalar after offline harness. Wired
`--measure turn` (Look/Left=Q, BE+0x278 sample, yaw_axis_store rates, no Up
poke). Live pair **turn-p02** `pairEligible=true`; both attempts steady
**0.090657 rad/s**. Published v1 contract + accepted translation policy;
Core `WalkerLookYawRateMilliRadPerTick=3` (milli-rad @ 30 Hz). Facing still
snaps (constant reserved for later continuous yaw). Hygiene: profile trees
stripped; turn-p02 ~0.5 MB. Steam untouched. Gates: 72 Python unit tests OK;
39 Core tests OK.

**Not claimed:** body vs camera yaw identity; source mGroundTurnRate=1.5; full
facing integration; campaign exit.

### 2026-07-14 — Decision log (start of live wire)

See prior progress for offline scaffold and jet land.

## Lane bias accounting

| Last 3 | Lanes |
|--------|--------|
| jet/campaign | RE+rebuild |
| turn harness | RE harness |
| turn live dual-accept | RE+rebuild |

## Resume checklist

- [x] tip / baton for this cycle
- [ ] Execute Current Slice M1.4/M1.5 after push
- [ ] Mutate baton on closeout
