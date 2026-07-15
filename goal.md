# Active Goal Baton

Status: **ACTIVE** (time-boxed marathon)  
Last updated: 2026-07-14  
**STOP wall clock:** 2026-07-15 10:00 local  
Integration tip: `deafc99e`  
30m durable re-entry: 019f633f58c2 (verify still armed)

## Closed ledger (session)

| Slice | Tip |
|-------|-----|
| Camera look + Core LookX | `83c33e0d` |
| Energy/shield offsets + measure=energy | `0f4af824` |
| M1.6 coast scaffold | `3420588f` |
| Client/Godot LookX | `1f485af1` |
| Fire energy-drop edges | `caca66d8` |
| CommandTape LookX + index | `0f13a6e6` |
| Lore docsync mirrors | `6acb4f43` |
| LookX replay test | `edf70fcc` |
| Energy pair envelope | `3f679a1c` |
| Shield pair envelope + README look | `deafc99e` |

## Current Slice

**ID:** `M2-energy-live-dual-accept-or-projectile-or-WinUI`  
**Objective:** Live jet energy dual-accept when GameProfiles ready; else
projectile speed scaffold pair envelope / WinUI honesty. No reopen closed
motion dual-accepts. Energy BE+0xFC / shields BE+0x100 are hypotheses until
dual-accept.

## Blockers (non-terminal)

- No active `GameProfiles/` copy for live pair right now; live dual-accept needs
  safe-copy preflight + mission control + receipt.

## Resume

Continue while `Get-Date` < 2026-07-15 10:00 local. At STOP: finalize baton;
do **not** `update_goal(completed)` early.
