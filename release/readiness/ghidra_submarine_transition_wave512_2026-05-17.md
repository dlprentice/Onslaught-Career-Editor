# Ghidra Submarine / Unit Transition Wave512 Readiness

Date: 2026-05-17

## Scope

Wave512 saved static Ghidra name/signature/comment/tag refinements for 8 submarine, unit transition-state, and monitor particle-spawn helpers:

| Address | Saved state | Evidence summary |
| --- | --- | --- |
| `0x004eec80` | `void __thiscall CSubmarine__Init(void * this, void * unit_init)` | `RET 0x4`; clears `this+0x250`, calls `CUnit__Init`, allocates CSubmarineAI-style and CSubmarineGuide components. |
| `0x004eedc0` | `void * __thiscall CSubmarineAI__ScalarDeletingDestructor(void * this, byte flags)` | 2 renames tranche: corrected stale vfunc name; calls destructor body and frees on `flags&1`. |
| `0x004eede0` | `void __fastcall CSubmarineAI__DestructorBody(void * this)` | 2 renames tranche: corrected stale `CUnitAI__ctor_like` owner/purpose; restores CUnitAI base vtable, unregisters SPtrSet links, calls `CMonitor__Shutdown`. |
| `0x004ef000` | `void __fastcall CUnit__SetTransitionState1AndNotifyChildren(void * this)` | Writes state `1` from prior state `2`/`3`, then dispatches child vfunc `+0x5c`. |
| `0x004ef050` | `void __fastcall CUnit__SetTransitionState3_IfState0Or1(void * this)` | Writes state `3` only from prior state `0`/`1`. |
| `0x004ef0f0` | `void __fastcall CUnit__SetTransitionState2(void * this)` | Writes state `2`; a nearby state-machine body calls it after height/position checks. |
| `0x004ef120` | `void __fastcall CMonitor__SpawnParticleEffectFromIndexedListInHeightBand(void * this)` | Uses indexed global effect list `DAT_008553f8`, samples up to 100 positions, and creates an effect within the global height band. |
| `0x004ef570` | `void * __thiscall CSubmarineGuide__CSubmarineGuide(void * this, void * owner_submarine)` | `RET 0x4`; calls `CGuide__ctor_base`, installs vtable `0x005df438`, returns `this`. |

## Verification

- Dry-run mutation log: `SUMMARY updated=0 skipped=8 renamed=0 would_rename=2 missing=0 bad=0`.
- Apply mutation log: `SUMMARY updated=8 skipped=0 renamed=2 would_rename=0 missing=0 bad=0`.
- Verify dry-run log: `SUMMARY updated=0 skipped=8 renamed=0 would_rename=0 missing=0 bad=0`.
- Post read-back exports: 8 metadata rows, 8 tag rows, 8 xref rows, 2888 instruction rows, and 8 decompile exports.
- Focused probe: `py -3 tools\ghidra_submarine_transition_wave512_probe.py --check` returns `PASS`.
- Queue telemetry: 6078 total functions, 2391 commented functions, 3687 commentless functions, 1618 exact-undefined signatures, and 1433 `param_N` signatures.
- Ghidra backup: `[maintainer-local-ghidra-backup-root]\BEA_20260517-190236_post_wave512_submarine_transition_verified`, 19 files, 158370695 bytes, `MissingCount=0`, `ExtraCount=0`, `HashDiffCount=0`.

## Boundaries

This readiness note proves saved static retail Ghidra evidence only. It does not prove exact source-body identity, concrete CSubmarine/CSubmarineAI/CSubmarineGuide/CUnit/CMonitor layouts, runtime submarine behavior, runtime transition behavior, runtime effect behavior, BEA launch behavior, game patching, or rebuild parity.
