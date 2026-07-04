# Ghidra Carver Init/Combat/Wing Review Wave965

Status: read-only static review
Date: 2026-05-28
Scope: `carver-init-combat-wing-review-wave965`

Wave965 re-reviewed the Carver init/combat/wing helper band that Wave945 left as context after its narrower CCarver vtable-boundary recovery. The pass made no Ghidra mutation: no rename, no signature change, no comment/tag change, no function-boundary change, and no executable-byte change.

Primary reviewed rows:

| Address | Saved name | Static read-back evidence |
| --- | --- | --- |
| `0x00422440` | `CCarver__Init` | Calls `CAirUnit__Init`, allocates/installs helper objects at `+0x208` and `+0x13c`, and seeds wing/attack fields including `+0x27c`, `+0x280`, `+0x284`, and `+0x288`. |
| `0x00422580` | `CCarverAI__dtor_base` | Resets vtable `0x005d8d1c`, unlinks monitored reader slots at `+0x28`, `+0x24`, and `+0x0c` through `CSPtrSet__Remove`, then calls `CMonitor__Shutdown`. |
| `0x00422620` | `CCarver__UpdateMotionAndWingPose` | Calls `CUnit__UpdateMotionAndTrailEffects` at `0x00422667`, moves wing blend toward target fields `+0x280/+0x284`, and dispatches through vtable byte offset `+0x70`. |
| `0x00422760` | `CCarverAI__OpenWings` | Reads animation through owner/helper pointers, calls animation resolver `0x004aa630`, dispatches vfunc `+0xf0`, and writes wing state `+0x27c = 1`. |
| `0x004227a0` | `CCarverAI__CloseWings` | Same animation-dispatch shape as open-wings and writes wing state `+0x27c = 2`. |
| `0x004227e0` | `CCarverAI__OnHit` | Vtable slot 38 row with `RET 0x8`; conditionally dispatches vfunc byte offset `+0x38`, then forwards to `0x00403ba0`. |
| `0x00422820` | `CCarverAI__Fire` | Calls owner readiness vfunc byte offset `+0x58`, animation resolver `0x004aa630`, and animation vfunc `+0xf0`; updates wing state `+0x27c` and returns `0`. |
| `0x00422930` | `CCarverAI__SetLastAttackTime` | Copies global time `0x00672fd0` into `this+0x288`. |
| `0x00422940` | `CCarverAI__IsRecentlyAttacked` | Compares `this+0x288 + 0x005d8568` against global time `0x00672fd0` and returns a boolean. |
| `0x004229b0` | `CarverAimGlobals__ResetVector` | Writes zero to `0x00662c60`, `0x00662c64`, and `0x00662c68`; xrefs include init table/data row `0x006220e0`. |
| `0x004229d0` | `CarverAimGlobals__InitMatrix` | Writes an identity-style matrix block at `0x00662c30` through `0x00662c5c`; xrefs include init table/data row `0x006220e4`. |

Context continuity:

- CCarver vtable `0x005e0d90` still resolves the reviewed rows at slots `8`, `35`, `38`, `58`, `63`, `65`, `67`, `103`, and `104`.
- Wave945 boundary rows `0x00422750 CCarver__Thunk_CallGuideVFunc08`, `0x004228b0 CCarver__VFunc35_RenderWithFadeGlobal`, and `0x00422910 CCarver__VFunc104_IsWingBlendAboveThreshold` remain present with saved function objects.
- Wave915 targeting/event rows `0x00422970`, `0x00422aa0`, `0x00422b90`, `0x00422db0`, `0x00423490`, and `0x00423510` remain context only for this wave.

Read-back evidence:

- Fresh exports: `28` metadata rows, `28` tag rows, `46` xref rows, `4060` around-address instruction rows, `1522` function-body instruction rows, `28` decompile rows, `128` CCarver vtable rows, and `4` Carver aim-global xref rows.
- Queue remains `6152` total functions, `6152` commented, `0` commentless, `0` exact-undefined signatures, and `0` `param_N`; export-contract function-quality closure remains `6152/6152 = 100.00%`.
- Wave911 focused re-audit progress after Wave965: `334/1408 = 23.72%`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260528-144929_post_wave965_carver_init_combat_wing_review_verified`, `19` files, `173542279` bytes, `DiffCount=0`.

What this proves:

- The reviewed Carver rows still exist in the saved Ghidra database with coherent saved names/signatures/comments.
- The CCarver vtable and xref/decompile/body-instruction evidence still support the existing bounded Carver init, wing, attack timestamp, hit/fire, and aim-global summaries.

What remains unproven:

- Runtime wing timing, damage, fire, aim, guide, render, or attack behavior.
- Exact `CCarver`, `CCarverAI`, or `CCarverGuide` layouts and field names.
- Exact source method or virtual names, because `Carver.cpp` source is absent from the current source snapshot.
- BEA patching behavior and rebuild parity.

Probe token anchor: Wave965; carver-init-combat-wing-review-wave965; 0x00422440 CCarver__Init; 0x00422580 CCarverAI__dtor_base; 0x00422620 CCarver__UpdateMotionAndWingPose; 0x00422760 CCarverAI__OpenWings; 0x004227a0 CCarverAI__CloseWings; 0x004227e0 CCarverAI__OnHit; 0x00422820 CCarverAI__Fire; 0x00422930 CCarverAI__SetLastAttackTime; 0x00422940 CCarverAI__IsRecentlyAttacked; 0x004229b0 CarverAimGlobals__ResetVector; 0x004229d0 CarverAimGlobals__InitMatrix; 0x005e0d90; 334/1408 = 23.72%; 6152/6152 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260528-144929_post_wave965_carver_init_combat_wing_review_verified; no mutation.
