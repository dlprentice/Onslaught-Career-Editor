# Ghidra Infantry Lifecycle Wave416

Status: public-safe static RE evidence
Date: 2026-05-14

This note records a serialized headless Ghidra dry/apply/read-back pass for an infantry, collision-seeking helper, high-level collision detector constructor, and UnitAI death-animation tranche. It is public-safe: it contains addresses, saved names/signatures, command summaries, counts, and claim boundaries, but not raw decompile excerpts, private paths, screenshots, frames, copied executables, saves, or private runtime proof.

## Saved Ghidra Corrections

| Address | Saved name | Saved signature | Result |
| --- | --- | --- | --- |
| `0x00488bb0` | `CInfantry__Init` | `void __thiscall CInfantry__Init(void * this, void * infantryInit)` | Hardened the infantry init signature/comment around the init pointer, `CGroundUnit__Init`, allocation context, scale setup, and velocity/heading state. |
| `0x00488dc0` | `CInfantryAI__scalar_deleting_dtor` | `void * __thiscall CInfantryAI__scalar_deleting_dtor(void * this, byte flags)` | Corrected the vfunc-style label to a scalar-deleting destructor wrapper. |
| `0x00488de0` | `CInfantryAI__dtor_body_00488de0` | `void __fastcall CInfantryAI__dtor_body_00488de0(void * this)` | Corrected constructor-like wording to the destructor body that restores the CUnitAI base vtable, removes pointer-set links, and shuts down monitor state. |
| `0x00488e80` | `CCollisionSeekingInfantryBloke__scalar_deleting_dtor` | `void * __thiscall CCollisionSeekingInfantryBloke__scalar_deleting_dtor(void * this, byte flags)` | Corrected the vfunc-style label to a scalar-deleting destructor wrapper. |
| `0x00488ea0` | `CCollisionSeekingInfantryBloke__dtor_body_00488ea0` | `void __fastcall CCollisionSeekingInfantryBloke__dtor_body_00488ea0(void * this)` | Corrected shutdown/destroy wording to a bounded destructor body that shuts down monitor state before chaining to the collision-seeking round destructor. |
| `0x00488ef0` | `CCollisionSeekingThing__ctor_base` | `void __fastcall CCollisionSeekingThing__ctor_base(void * this)` | Hardened the base constructor signature/comment around field clear and shared vtable install. |
| `0x00488f00` | `CHLCollisionDetector__ctor_base` | `void __fastcall CHLCollisionDetector__ctor_base(void * this)` | Hardened the high-level collision detector constructor signature/comment around field clear and vtable install. |
| `0x00489040` | `CUnitAI__TryPlayActivateAnimation` | `int __fastcall CUnitAI__TryPlayActivateAnimation(void * this)` | Hardened the UnitAI activation-animation helper signature/comment. |
| `0x00489de0` | `CUnitAI__PromoteDieAnimationToDeadVariant` | `int __fastcall CUnitAI__PromoteDieAnimationToDeadVariant(void * this)` | Hardened the death-animation token mapping helper signature/comment. |
| `0x00489ef0` | `CUnitAI__ForceDeadForwardAndResetDeathState` | `void __fastcall CUnitAI__ForceDeadForwardAndResetDeathState(void * this)` | Hardened the forced dead-forward/death-state reset helper signature/comment. |

## Evidence Summary

- The available Stuart source snapshot does not include matching Infantry, UnitAI, or collision helper source bodies for this tranche, so these corrections are retail-static evidence rather than exact source-body confirmation.
- The destructor wrappers are bounded by scalar-deleting wrapper shape: destructor-body calls, delete-flag tests, optional object free, returned receiver, and `RET 0x4`.
- `0x00488de0` is now bounded as InfantryAI destructor-body context, not a constructor-like helper.
- `0x00488ef0` and `0x00488f00` are constructor-base helpers with observed vtable constants for collision-seeking and high-level collision detector contexts.
- `0x00489de0` maps current `die_*` animation tokens toward `dead_*` variants or `dead_forward`; this is static token/control-flow evidence, not runtime animation proof.
- Refreshed whole-project queue telemetry reports `6037` total functions, `1617` commented functions, `4420` commentless functions, `1891` undefined signatures, and `1827` `param_N` signatures. Current confirmation proxies are comment-backed `1617/6037 = 26.78%` and strict clean-signature `1541/6037 = 25.53%`; both are telemetry only, not milestones.

## Validation

- Expected red focused test before implementation: `py -3 tools\ghidra_infantry_lifecycle_wave416_probe_test.py` failed with `ModuleNotFoundError`.
- Focused tests: `py -3 tools\ghidra_infantry_lifecycle_wave416_probe_test.py` passed `3/3`.
- Python compile: `py -3 -m py_compile tools\ghidra_infantry_lifecycle_wave416_probe.py tools\ghidra_infantry_lifecycle_wave416_probe_test.py` passed.
- Headless dry run: `ApplyInfantryLifecycleWave416.java dry` reported `updated=0 skipped=10 created=0 would_create=0 renamed=0 would_rename=6 missing=0 bad=0` with `REPORT: Save succeeded`.
- Headless apply run: `ApplyInfantryLifecycleWave416.java apply` reported `updated=10 skipped=0 created=0 would_create=0 renamed=6 would_rename=0 missing=0 bad=0` with `REPORT: Save succeeded`.
- Read-back exports verified `10` metadata rows, `10` tag rows, `12` xref rows, `890` instruction rows, and `10` decompile exports.
- Package wrapper: `cmd.exe /c npm run test:ghidra-infantry-lifecycle-wave416` passed with focused probe status `PASS`.
- Queue refresh: headless `ExportFunctionQualitySnapshot.java` and `cmd.exe /c npm run test:ghidra-static-reaudit-queue` passed with the `6037`-function telemetry above.
- Actual Ghidra project backup: copied `BEA.gpr` and `BEA.rep` to `G:\GhidraBackups\BEA_20260514_124157_post_wave416_infantry_lifecycle_verified` and verified `19` files, `154962823` bytes, and `HashDiffCount=0`.

## Not Proven

This tranche does not prove runtime infantry behavior, runtime collision-seeking behavior, runtime collision-detector behavior, runtime death-animation behavior, exact source-body identity, concrete class layouts, local-variable/type recovery, BEA launch behavior, game patching, packaged app behavior, or rebuild parity.
