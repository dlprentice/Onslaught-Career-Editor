# Ghidra Carrier / Carver Boundary Signature Correction - 2026-05-10

## Summary

This wave saved a focused Carrier/Carver-region Ghidra correction after fresh metadata, decompile, xref, instruction, and callsite-boundary review. It keeps the claim bounded to static saved-Ghidra refinement.

The saved changes cover:

| Address | Saved Ghidra state | Evidence boundary |
| --- | --- | --- |
| `0x00421a80` | `void __thiscall CCarrier__Init(void * this, void * init)` | Carrier init path with base air-unit init, child helper allocation, and vtable setup. |
| `0x00421b80` | `void * __thiscall CCarrierAI__scalar_deleting_dtor(void * this, byte flags)` | Corrects stale `CCarrierAI__VFunc_01_00421b80` to scalar-deleting destructor wrapper. |
| `0x00421ba0` | `void __fastcall CCarrierAI__dtor_base(void * this)` | Corrects stale `CUnitAI__ctor_like_00421ba0` to destructor-base cleanup context. |
| `0x00421c40` | `void __fastcall CUnit__ApplyFlag4DampingAndScaleSpeed(void * this)` | Corrects the old address-suffixed label and saves a bounded movement-helper signature/comment. |
| `0x00422440` | `void __thiscall CCarver__Init(void * this, void * init)` | Recovered missing function boundary and saved Carver init signature/comment. |
| `0x00422560` | `void * __thiscall CCarverAI__scalar_deleting_dtor(void * this, byte flags)` | Corrects stale `CCarverAI__ScalarDeletingDestructor` casing/style to the current destructor-wrapper convention. |
| `0x00422580` | `void __fastcall CCarverAI__dtor_base(void * this)` | Corrects stale `CCarverAI__Destructor` to destructor-base cleanup context. |
| `0x00422620` | `void __fastcall CCarver__UpdateMotionAndWingPose(void * this)` | Recovered missing function boundary and saved bounded motion/wing-pose update label. |
| `0x00422760` | `void __fastcall CCarverAI__OpenWings(void * this)` | Wing-open animation helper signature/comment. |
| `0x004227a0` | `void __fastcall CCarverAI__CloseWings(void * this)` | Wing-close animation helper signature/comment. |
| `0x004227e0` | `void __thiscall CCarverAI__OnHit(void * this, void * otherThing, void * collisionReport)` | Hit override with explicit stack arguments. |
| `0x00422820` | `int __fastcall CCarverAI__Fire(void * this)` | Carver AI fire/animation helper signature/comment. |
| `0x00422930` | `void __fastcall CCarverAI__SetLastAttackTime(void * this)` | Last-attack timestamp setter. |
| `0x00422940` | `int __fastcall CCarverAI__IsRecentlyAttacked(void * this)` | Recent-attack cooldown predicate. |
| `0x00422970` | `int __fastcall CCarverAI__CanStartAttack(void * this)` | Recovered missing boundary and saved attack-start predicate label. |
| `0x004229b0` | `void __cdecl CarverAimGlobals__ResetVector(void)` | Recovered missing boundary for Carver aim/vector global reset. |
| `0x004229d0` | `void __cdecl CarverAimGlobals__InitMatrix(void)` | Recovered missing boundary for Carver aim/orientation matrix init. |
| `0x00422aa0` | `void __thiscall CCarverAI__RefreshTargetReaderAndScheduleMove(void * this, void * event)` | Recovered missing event-handler boundary for target-reader refresh/reschedule. |
| `0x00422b90` | `void __thiscall CCarverAI__UpdateAttackAndReschedule(void * this, void * event)` | Recovered missing event-handler boundary for target/attack update and reschedule. |
| `0x00422db0` | `void __fastcall CCarverAI__CheckNearbyEnemies(void * this)` | Nearby-enemy scan / last-attack update helper. |
| `0x00422f90` | `void * __thiscall CCarverGuide__ctor(void * this, void * guideTarget)` | Guide constructor signature/comment. |
| `0x00422fb0` | `void * __thiscall CCarverGuide__scalar_deleting_dtor(void * this, byte flags)` | Corrects stale `CCarverGuide__ScalarDeletingDestructor` casing/style. |
| `0x00422fd0` | `void __fastcall CCarverGuide__dtor_base(void * this)` | Corrects stale `CCarverGuide__Destructor` to destructor-base cleanup context. |
| `0x00423490` | `void __thiscall CCarverGuide__HandleEvent(void * this, void * event)` | Recovered missing guide event-handler boundary. |

## Validation

- `py -3 tools\ghidra_carrier_carver_boundary_signature_correction_probe_test.py` - PASS; 3/3 tests.
- Headless missing-boundary create dry/apply - PASS; dry found `8` would-create targets; apply created `8` functions, renamed `8`, and reported `REPORT: Save succeeded`.
- Headless `ApplyCarrierCarverBoundarySignatureCorrection.java` dry/apply - PASS; dry `updated=0 skipped=24 renamed=0 missing=0 bad=0`; apply `updated=24 skipped=0 renamed=16 missing=0 bad=0`; `REPORT: Save succeeded`.
- Headless metadata/decompile/xref/instruction read-back - PASS; `24/24` metadata rows, `24/24` decompile rows, `29` xref rows, and `1944` instruction rows.
- `py -3 tools\ghidra_carrier_carver_boundary_signature_correction_probe.py --check` - PASS; `8` created boundaries, `24` signature targets, `16` renamed targets, and `0` failures.
- `cmd.exe /c npm run test:ghidra-carrier-carver-boundary-signature-correction` - PASS.
- `py -3 -m py_compile tools\ghidra_carrier_carver_boundary_signature_correction_probe.py tools\ghidra_carrier_carver_boundary_signature_correction_probe_test.py` - PASS.
- Refreshed queue/baseline - PASS; queue reports `5876` functions, `683` commented functions, `5193` commentless functions, `2032` undefined signatures, `2330` `param_N` signatures, and `0` helper/wrapper/uncertain-owner names.

## Not Proven

`Carrier.cpp` and `Carver.cpp` source bodies are absent from the current `references/Onslaught/` snapshot, so these saved names are retail-binary static evidence rather than source-perfect identities. This wave does not prove concrete Carrier/Carver layouts, tags, local variable names, exact source virtual names, runtime carrier/carver/AI/guide behavior, BEA launch behavior, game patching, or rebuild parity.
