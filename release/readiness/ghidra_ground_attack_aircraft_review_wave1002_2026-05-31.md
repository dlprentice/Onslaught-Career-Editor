# Ghidra GroundAttackAircraft Review Wave1002 Readiness Note

Status: complete static read-back evidence; no mutation needed
Date: 2026-05-31
Scope: `ground-attack-aircraft-review-wave1002`

Wave1002 re-reviewed the Wave911 risk-ranked `GroundAttackAircraft.cpp` / `CGroundAttackAI` / `CGroundAttackGuide` / `CMCGroundAttack` island around the prior Wave391, Wave432, and Wave557 corrections. Fresh read-only metadata, tag, xref, instruction, decompile, vtable, and pointer-table exports matched the already-saved evidence, so this wave made no Ghidra mutation, no rename, no signature change, no function-boundary change, no executable-byte change, no BEA launch, and no runtime/game-file mutation.

Primary targets:

| Address | Read-back evidence |
| --- | --- |
| `0x0047bab0 CGroundAttackAI__InitState` | Xref from `0x0047bc92` inside `CGroundAttackAircraft__Init`; clears `+0x60`, randomizes `+0x64`, and calls `CGroundAttackAircraft__CloseBay`. |
| `0x0047bbf0 CGroundAttackAircraft__Init` | Function table `0x005e2bf0` slot `0`; delegates to `CAirUnit__Init`, allocates/installs `CMCGroundAttack`, `CGroundAttackAI`, and `CGroundAttackGuide`, and initializes bay/animation state fields. |
| `0x0047bd70 CGroundAttackAI__ScalarDeletingDestructor` | `CGroundAttackAI` vtable `0x005dbd4c` slot `1`; wraps `CGroundAttackAI__Destructor` and optional free-on-flag behavior. |
| `0x0047bd90 CGroundAttackAI__Destructor` | Restores base `CUnitAI` vtable `0x005d8d1c`, removes observed reader/set fields, then calls `CMonitor__Shutdown`. |
| `0x0047be30 CGroundAttackGuide__ScalarDeletingDestructor` | `CGroundAttackGuide` vtable `0x005dbd20` slot `1`; wraps `CGroundAttackGuide__Destructor` and optional free-on-flag behavior. |
| `0x0047be50 CGroundAttackGuide__Destructor` | Removes linked reader/set field `+0x2c` when present, then calls `CMonitor__Shutdown`. |
| `0x0047bfa0 CGroundAttackAircraft__OpenBay` | Referenced by the nearby AI state paths; sets bay state `+0x27c` to opening and plays the open animation token when state allows. |
| `0x0047bff0 CGroundAttackAircraft__CloseBay` | Called by `CGroundAttackAI__InitState` and nearby state paths; sets bay state `+0x27c` to closing and plays the close animation token when state allows. |
| `0x0047c040 CGroundAttackAircraft__AdvanceCloseShootAnimationState` | Function table `0x005e2bf0` slot `50`; advances open/shoot/close/idle animation state and writes bay state `+0x27c`. |
| `0x0050ee10 CGroundAttackAircraft__scalar_deleting_dtor` | `CGroundAttackAircraft` primary vtable `0x005e2bcc` slot `1`; wraps `CGroundAttackAircraft__Destructor_VFunc01` and optional free-on-flag behavior. |
| `0x0050f130 CGroundAttackAircraft__Destructor_VFunc01` | Clears owned pointer sets at `this+0x26c` and `this+0x25c`, removes the `this+0x250` global-list node, then calls `CUnit__dtor_base`. |
| `0x004964d0 CMCGroundAttack__Constructor` | Called from `CGroundAttackAircraft__Init`; installs vtable `0x005dc330`, stores owner aircraft at `+0x08`, and seeds cached state sentinels. |
| `0x00496500 CMCGroundAttack__ScalarDeletingDestructor` | `CMCGroundAttack` vtable `0x005dc330` slot `1`; wraps `CMCGroundAttack__Destructor` and optional free-on-flag behavior. |
| `0x00496520 CMCGroundAttack__Destructor` | Restores vtable `0x005dc330`, clears `+0x08`, and tails into the base motion-controller destructor. |
| `0x00496540 CMCGroundAttack__VFunc_04_UpdateTurretTransform_00496540` | `CMCGroundAttack` vtable `0x005dc330` slot `4`; checks the `turret` token `0x0062dd20`, runs transform math, and refreshes cached owner values. |
| `0x004968a0 CMCGroundAttack__VFunc_08_CheckCachedMotionState_004968a0` | `CMCGroundAttack` vtable `0x005dc330` slot `8`; compares owner fields `+0xe0/+0xe4/+0x284` against cached values at `this+0x0c/+0x10`. |

Fresh read-back evidence:

- Exports: `16` metadata rows, `16` tag rows, `18` xref rows, `691` body-instruction rows, `16` decompile rows, `512` vtable-slot rows, `4` vtable type rows, and `80` pointer-table rows.
- Vtable type read-back resolves `0x005dbd4c` to `CGroundAttackAI`, `0x005dbd20` to `CGroundAttackGuide`, `0x005dc330` to `CMCGroundAttack`, and `0x005e2bcc` to `CGroundAttackAircraft`.
- Pointer table `0x005e2bf0` read-back keeps slot `0` at `0x0047bbf0 CGroundAttackAircraft__Init` and slot `50` at `0x0047c040 CGroundAttackAircraft__AdvanceCloseShootAnimationState`.
- Queue closure remains `6222/6222 = 100.00%`.
- Wave911 focused re-audit progress remains `472/1408 = 33.52%` because this is a risk-ranked residual island rather than a new focused-candidate anchor.
- Expanded static surface progress advances to `629/1478 = 42.56%`.
- Wave911 top-500 risk-ranked coverage advances to `359/500 = 71.80%`.
- Verified backup: `G:\GhidraBackups\BEA_20260531-112128_post_wave1002_ground_attack_aircraft_review_verified`, `19` files, `173869959` bytes, `DiffCount=0`, `HashDiffCount=0`.

Probe token anchor: Wave1002; `ground-attack-aircraft-review-wave1002`; `0x0047bbf0 CGroundAttackAircraft__Init`; `0x0047c040 CGroundAttackAircraft__AdvanceCloseShootAnimationState`; `0x004964d0 CMCGroundAttack__Constructor`; `0x00496540 CMCGroundAttack__VFunc_04_UpdateTurretTransform_00496540`; `0x004968a0 CMCGroundAttack__VFunc_08_CheckCachedMotionState_004968a0`; `472/1408 = 33.52%`; `629/1478 = 42.56%`; `359/500 = 71.80%`; `6222/6222 = 100.00%`; `G:\GhidraBackups\BEA_20260531-112128_post_wave1002_ground_attack_aircraft_review_verified`; no mutation.

What this proves:

- The reviewed GroundAttackAircraft/AI/guide/motion-controller rows exist in the saved Ghidra project with the expected names, signatures, comments, and tags.
- The saved Wave391, Wave432, and Wave557 owner/signature/boundary corrections remain coherent after fresh vtable, pointer-table, xref, decompile, and instruction read-back.
- The already-documented stale GillMHead, constructor, and broad-CUnitAI label corrections remain resolved in the current saved project.

What remains unproven:

- Exact Stuart source-body identity; the available Stuart source corpus in this repo does not include `GroundAttackAircraft.cpp`.
- Concrete `CGroundAttackAircraft`, `CGroundAttackAI`, `CGroundAttackGuide`, `CMCGroundAttack`, bay-state, guide, and motion-controller layouts.
- Runtime ground-attack aircraft AI, bay animation, guide, targeting, destruction, or motion-controller behavior.
- BEA patching behavior.
- Rebuild parity.
