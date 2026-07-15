# Active Goal Baton

Status: **ACTIVE** (full reconstruction campaign — wall-clock marathon stop discarded)  
Last updated: 2026-07-14  
Integration tip: `126f68b3`  
30m re-entry task (if still armed): `019f633f58c2` — may delete if no longer wanted

## Marathon-3 outcome (honest)

**Not finished.** Motion dual-accepts (M1.1–M1.5) are landed. Combat/resource
live dual-accepts, coast live, camera presentation dual-accept, and most M3–M7
milestones remain open. Offline harnesses and LookX Core/Client wiring advanced
M2/M3 prep only.

## Current Slice

**ID:** `M2-energy-live-dual-accept`  
**Objective:** Receipt-bound jet energy dual-accept (`--measure energy --vehicle jet`)
using BE+0xFC hypothesis when mission is controllable. Offline path already green.
Checklist: `reverse-engineering/game-mechanics/energy-live-dual-accept-checklist.md`  
Prep (ignored): `GameProfiles/marathon-energy-jet-01`

## Landed this campaign wave (selected)

| Area | Status |
|------|--------|
| Walker/jet/yaw/strafe/morph dual-accept → Core | **done** |
| Core LookX + Client/Godot ←→ / CommandTape | **done** |
| Energy BE+0xFC / shields BE+0x100 sampler + `measure=energy` | **wired offline** |
| Coast/fire/projectile/shield/camera scaffolds + pair envelopes | **offline** |
| Campaign scalar status / measure-mode catalogs | **done** |
| Live energy dual-accept | **not done** (needs mission + receipt) |
| Core combat constants from retail | **provisional** until dual-accept |

## Resume

No wall-clock stop. Pick Current Slice or next open milestone from `goal.campaign.md`.
