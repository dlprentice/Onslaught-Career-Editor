# MissionScript Slot Command-Effect Static Readiness Note

Status: static slot command-effect schema proof complete, not runtime proof
Date: 2026-06-08
Scope: `missionscript-slot-command-effect-static`

This readiness note records the public-safe static proof result for [MissionScript Slot Command-Effect Static Proof](../../reverse-engineering/binary-analysis/missionscript-slot-command-effect-static-proof.md), backed by `missionscript-slot-command-effect.v1.json`.

Static closeout remains unchanged: `6411/6411 = 100.00%`, `0 / 0 / 0`, `1560/1560 = 100.00%`, `1179/1179 = 100.00%`, and remaining active focused work `0`. Latest verified Ghidra backup remains `G:\GhidraBackups\BEA_20260607-230027_post_wave1219_final_score16_current_risk_review_verified`.

Evidence anchors:

| Surface | Anchor |
| --- | --- |
| Descriptor slots | `SetSlot` at `0x0064ecd0`, `GetSlot` at `0x0064ed10`, `SetSlotSave` at `0x0064ef50`. |
| IScript handlers | `0x005338d0 IScript__SetSlot`, `0x00533900 IScript__SetSlotSave`, `0x005339a0 IScript__GetSlotBitValue`. |
| Runtime helpers | `0x0046d3a0 CGame__SetSlot`, `0x0046d410 CGame__GetSlot`, runtime slot array at `CGame+0x308`. |
| Persistence helper | `0x004214e0 CCareer__SetSlot`, `.bes` true-view `mSlots[0]` offset `0x240A`. |
| Loose corpus | `6 slot-using level rows`, `18 detailed slot call rows`, `6 GetSlot`, `8 SetSlot`, and `4 SetSlotSave`. |

Evidence counts: Wave579 `6` metadata rows, `6` xref rows, `1326` instruction rows, `6` decompile rows, and `24` vtable rows; Wave803 `2` metadata rows, `3` xref rows, `170` instruction rows, and `2` decompile rows. This slice used saved static exports and did not mutate Ghidra.

What this proves:

- The static slot command bridge is mapped from descriptor names through IScript handlers to CGame runtime slot helpers.
- `SetSlotSave` is statically separated from `SetSlot` because it also calls `CCareer__SetSlot`.
- The loose slot corpus count is reproducible and bounded.

What remains unproven:

- Runtime MissionScript execution or runtime command effects.
- Runtime save behavior or runtime slot persistence.
- Tutorial progression, Level500 branch behavior, Fenrir state behavior, or mission outcomes.
- Live loose-MSL loading or packed-vs-loose script selection.
- Exact descriptor, CGame, CCareer, VM, datatype, arity, or argument layouts.
- BEA patching behavior, visual QA, Godot parity, rebuild parity, or no-noticeable-difference parity.
