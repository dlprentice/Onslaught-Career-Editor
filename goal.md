# Active Goal Baton

Status: **ACTIVE** (time-boxed marathon)  
Last updated: 2026-07-14  
**STOP wall clock:** 2026-07-15 10:00 local  
Integration tip: (pending this push)  
30m durable re-entry: 019f633f58c2

## Closed ledger (this session, selected)

| Slice | Tip |
|-------|-----|
| Camera look harness + Core LookX | `83c33e0d` |
| Energy/shield offsets + measure=energy | `0f4af824` |
| M1.6 coast/friction scaffold | `3420588f` |
| Client/Godot LookX | `1f485af1` |
| Fire energy-drop edges | `caca66d8` |
| CommandTape LookX + mechanics index | `0f13a6e6` |
| Lore mirrors docsync | `6acb4f43` |
| CommandTape LookX replay test | (this) |

## Current Slice

**ID:** `M2-energy-live-dual-accept-or-fire-live-or-WinUI`  
**Objective:** Prefer live jet energy dual-accept when GameProfiles/receipt ready
(`--measure energy --vehicle jet`); else fire-hold live path; else WinUI
honesty/polish. Offsets BE+0xFC / +0x100 remain hypotheses until dual-accept.
No reopen closed motion dual-accepts.

## Resume

Continue while `Get-Date` < STOP. At STOP: leave resume-ready baton; do not
`update_goal(completed)` early.
