# MissionScript Slot Command-Effect Static Proof

Status: static slot command-effect schema proof complete, not runtime proof
Last updated: 2026-06-08
Scope: `missionscript-slot-command-effect-static`
Artifact: `missionscript-slot-command-effect-static-proof.md`; schema: `missionscript-slot-command-effect.v1.json`

This proof converts saved retail Ghidra evidence from Wave579 and Wave803, the completed MissionScript descriptor schema, and the public-safe loose slot corpus into a machine-checkable slot command-effect map at `missionscript-slot-command-effect.v1.json`. It is the first narrow IScript command-effect child lane after the completed descriptor, VM/datatype/opcode, and event/object-code lifecycle maps.

Static closeout remains unchanged:

- Static Ghidra function-quality closure: `6411/6411 = 100.00%`.
- Static debt: `0 / 0 / 0` commentless, exact-undefined, and `param_N` rows.
- Expanded post-100 static surface: `1560/1560 = 100.00%`.
- Active current-risk focused accounting: `1179/1179 = 100.00%`.
- Remaining active focused work: `0`.
- Latest verified Ghidra backup remains `G:\GhidraBackups\BEA_20260607-230027_post_wave1219_final_score16_current_risk_review_verified`.

## Schema Result

| Surface | Static result |
| --- | --- |
| Descriptor names | `SetSlot` is descriptor index `122` at `0x0064ecd0` with symbol `s_SetSlot_0064f340`; `GetSlot` is index `123` at `0x0064ed10` with symbol `s_GetSlot_0064f338`; `SetSlotSave` is index `132` at `0x0064ef50` with symbol `s_SetSlotSave_0064f2c0`. |
| Runtime slot command | `0x005338d0 IScript__SetSlot` reads slot/value arguments and calls `0x0046d3a0 CGame__SetSlot` on the current game state. |
| Persistent slot command | `0x00533900 IScript__SetSlotSave` calls `CGame__SetSlot`, then re-reads slot/value and calls `0x004214e0 CCareer__SetSlot`. |
| Slot query command | `0x005339a0 IScript__GetSlotBitValue` allocates a bool result object, calls `0x0046d410 CGame__GetSlot`, installs result vtable `0x005e4d50`, and writes through `out_result`. |
| Runtime slot storage | `CGame__SetSlot` and `CGame__GetSlot` range-check slot `0..255`, compute `slot>>5` and `1<<(slot&31)`, and access the runtime slot array at `CGame+0x308`. |
| Career slot storage | `CCareer__SetSlot` writes persistent `CCareer.mSlots`; the `.bes` true-view offset for `mSlots[0]` is `0x240A`. |
| Corpus context | `mission-slot-usage.md` records `6 slot-using level rows`, `18 detailed slot call rows`, `6 GetSlot`, `8 SetSlot`, and `4 SetSlotSave` calls across `level100`, `level500`, `level731`, `level732`, `level741`, and `level742`. |

Evidence rows consumed by the schema:

| Evidence | Count |
| --- | ---: |
| Wave579 metadata rows | `6` |
| Wave579 xref rows | `6` |
| Wave579 instruction rows | `1326` |
| Wave579 decompile rows | `6` |
| Wave579 vtable rows | `24` |
| Wave803 metadata rows | `2` |
| Wave803 xref rows | `3` |
| Wave803 instruction rows | `170` |
| Wave803 decompile rows | `2` |

The slot expressions preserved from the loose corpus are `SLOT_TUTORIAL_1`, `SLOT_TUTORIAL_2`, `SLOT_TUTORIAL_3`, `SLOT_TUTORIAL_4`, `61`, `62`, `n`, and `n + 29`. These are corpus vocabulary only until live mission loading and packed-vs-loose script selection are separately proven.

## Why This Matters

This gives clean-room MissionScript planning a bounded command-effect bridge for slots: descriptor name, IScript handler, runtime `CGame` bitset helper, optional immediate `CCareer` persistence through `SetSlotSave`, and the public loose-MSL slot corpus. It deliberately leaves Goodie, AddScore, objective, and level outcome commands for later command-effect families.

## Claim Boundary

This proves static slot command-effect accounting from saved retail Ghidra evidence and public-safe loose-MSL corpus counts. It does not prove runtime MissionScript execution, runtime command effects, runtime save behavior, runtime slot persistence, runtime mission outcome, tutorial progression, Level500 branch behavior, Fenrir state behavior, live loose-MSL loading, packed-vs-loose script selection, exact command descriptor layout, exact arity, exact argument type schema, exact CGame layout, exact CCareer layout, BEA patching behavior, visual QA, Godot parity, rebuild parity, or no-noticeable-difference parity.
