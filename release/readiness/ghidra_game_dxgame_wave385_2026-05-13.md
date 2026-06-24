# Ghidra CGame / CDXGame Owner Correction Tranche - 2026-05-13

Status: public-safe static RE evidence

## Summary

Wave 385 corrected saved Ghidra owner/name/signature/comment/tag metadata for seven game/media-adjacent constructor/destructor targets after metadata, decompile, instruction, RTTI/vtable, source-context, and deferred-boundary review. The pass corrects stale `IController` and `CFrontEndVideo` labels to `CGame`, `CDXGame`, and `CBinkOpenThread` where the current retail evidence supports those owners.

This is static Ghidra evidence only. It does not prove runtime construction/destruction behavior, Bink thread behavior, exact class layouts, concrete local types, BEA launch, game patching, or rebuild parity.

## Saved Targets

| Address | Saved name | Saved signature | Evidence boundary |
| --- | --- | --- | --- |
| `0x0046c210` | `CGame__ctor` | `void * __fastcall CGame__ctor(void * this)` | Constructor body starts from the `IController` vtable, initializes CGame-shaped state, then installs the `CGame` vtable. |
| `0x0046c2b0` | `CGame__scalar_deleting_dtor` | `void * __thiscall CGame__scalar_deleting_dtor(void * this, byte flags)` | Scalar-deleting wrapper calls `CGame__dtor`, checks the delete flag, and optionally frees `this`. |
| `0x0046c2d0` | `CGame__dtor` | `void __fastcall CGame__dtor(void * this)` | Destructor body restores the CGame vtable, unregisters active-reader style links, and calls `CMonitor__Shutdown`. |
| `0x00541f00` | `CDXGame__dtor_thunk` | `void __fastcall CDXGame__dtor_thunk(void * this)` | Unconditional jump to `CGame__dtor`; source and RTTI support `CDXGame : CGame`. |
| `0x00541f10` | `CDXGame__ctor` | `void * __fastcall CDXGame__ctor(void * this)` | Calls `CGame__ctor`, then installs the `CDXGame` secondary vtable at `0x005e509c`. |
| `0x00541f30` | `CDXGame__scalar_deleting_dtor` | `void * __thiscall CDXGame__scalar_deleting_dtor(void * this, byte flags)` | Scalar-deleting wrapper calls `CDXGame__dtor_thunk`, checks the delete flag, and optionally frees `this`. |
| `0x00541120` | `CBinkOpenThread__ctor` | `void * __fastcall CBinkOpenThread__ctor(void * this)` | Calls the waiting-thread constructor, installs vtable `0x005e5078`, and RTTI for that vtable resolves to `CBinkOpenThread`. |

The adjacent `0x00541140` vtable-slot body remains deferred. Wave 385 intentionally does not claim that boundary or behavior is repaired.

## Validation

| Check | Result |
| --- | --- |
| Headless `ApplyGameDxGameWave385.java` final dry run | PASS: `updated=0 skipped=7 renamed=0 would_rename=1 missing=0 bad=0`, `REPORT: Save succeeded`. |
| Headless `ApplyGameDxGameWave385.java` final apply | PASS: `updated=7 skipped=0 renamed=1 would_rename=0 missing=0 bad=0`, `REPORT: Save succeeded`. |
| Post-apply read-back exports | PASS: `7` metadata rows, `7` target decompile exports, `1015` instruction rows, `7` tag rows, `4` RTTI/vtable type hits, `2` vtable slot hits, and the deferred `0x00541140` guard stayed missing. |
| `py -3 tools\ghidra_game_dxgame_wave385_probe_test.py` | PASS: `2/2` tests. |
| `cmd.exe /c npm run test:ghidra-game-dxgame-wave385` | PASS: `targets=7`, `instruction_hits=13`, `vtable_type_hits=4`, `vtable_slot_hits=2`. |
| `py -3 -m py_compile tools\ghidra_game_dxgame_wave385_probe.py tools\ghidra_game_dxgame_wave385_probe_test.py` | PASS. |
| `cmd.exe /c npm run test:ghidra-static-reaudit-queue` | PASS: `6027` functions, `1430` commented functions, `4597` commentless functions, `1935` undefined signatures, and `1913` `param_N` signatures. |
| Actual Ghidra project backup | PASS: copied `BEA.gpr` and `BEA.rep` to `G:\GhidraBackups\BEA_20260513_183156_post_wave385_game_dxgame_verified`; verified `19` files, `153815943` bytes, `HashDiffCount=0`. |

The current broad comment-backed proxy is `1430/6027 = 23.73%`. The stricter comment-plus-no-`undefined`-or-`param_N` proxy is `1368/6027 = 22.70%`. These values are telemetry only, not completion milestones.

## Not Proven

- Runtime construction, destruction, or Bink thread behavior.
- Exact `CGame`, `CDXGame`, or `CBinkOpenThread` layout recovery.
- Concrete local variable names/types for every decompiler temporary.
- The adjacent `0x00541140` vtable-slot body.
- BEA launch, game patching, or runtime proof.
- Rebuild parity or gameplay behavior.
