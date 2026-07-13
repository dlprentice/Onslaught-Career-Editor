# Ghidra CRTBuilding / CRTMesh Wave496 Readiness Note

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 live correction closeout:** Historical record; `0x004dd0c0` comment correction. The original text below remains provenance rather than current semantic authority. It is superseded only where confirmed. Use the [closeout](../../reverse-engineering/binary-analysis/ghidra-full-reaudit-closeout-2026-07-13.md); final per-address decisions and exact before/after metadata are in `reverse-engineering/binary-analysis/ghidra-reviewed-correction-decisions-2026-07-13.jsonl` and `reverse-engineering/binary-analysis/ghidra-reviewed-correction-plan-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

Date: 2026-05-17

## Scope

Wave496 saved static Ghidra name/signature/comment/tag hardening for ten adjacent CRTBuilding/CRTMesh render-object functions:

| Address | Saved state |
| --- | --- |
| `0x004db850` | `void __fastcall CRTBuilding__Destructor(void * this)` |
| `0x004db8d0` | `void * __thiscall CRTBuilding__ScalarDeletingDestructor(void * this, byte flags)` |
| `0x004dba40` | `void * __fastcall CRTBuilding__VFuncSlot10_PickRandomLinkedEntry(void * this)` |
| `0x004dc370` | `void __thiscall CRTMesh__Init(void * this, void * init)` |
| `0x004dc950` | `void __fastcall CRTMesh__Destructor(void * this)` |
| `0x004dcb00` | `void __fastcall CRTMesh__FreePoseData(void * poseData)` |
| `0x004dcb70` | `void * __thiscall CRTMesh__ScalarDeletingDestructor(void * this, byte flags)` |
| `0x004dd0c0` | `void __cdecl CRTMesh__CleanupAllEffects(void)` |
| `0x004dd6b0` | `void __cdecl CRTMesh__SetQualityLevel(int qualityLevel)` |
| `0x004dd770` | `int __cdecl CRTMesh__GetQualityLevel(void)` |

## Evidence

- Apply script: `tools/ApplyRTBuildingRTMeshWave496.java`
- Probe: `tools/ghidra_rtbuilding_rtmesh_wave496_probe.py`
- Scratch artifacts: `subagents/ghidra-static-reaudit/wave496-rtbuilding-rtmesh-004db850/`
- Dry/apply/verify:
  - Dry: `updated=0 skipped=10 created=0 would_create=0 renamed=0 would_rename=2 missing=0 bad=0`
  - Apply: `updated=10 skipped=0 created=0 would_create=0 renamed=2 would_rename=0 missing=0 bad=0`
  - Verify dry: `updated=0 skipped=10 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`
- Post-readback verified `10` metadata rows, `10` tag rows, `14` xref rows, `410` instruction rows, `40` vtable rows, and `10` decompile exports.
- Focused probe: `py -3 tools\ghidra_rtbuilding_rtmesh_wave496_probe.py --check` PASS.
- NPM probe: `cmd.exe /c npm run test:ghidra-rtbuilding-rtmesh-wave496` PASS.
- Queue refresh: `6068` total functions, `2249` commented, `3819` commentless, `1665` undefined signatures, `1514` `param_N`; strict comment-plus-clean-signature proxy `2193/6068 = 36.14%`.
- Verified Ghidra backup: `[maintainer-local-ghidra-backup-root]\BEA_20260517-104658_post_wave496_rtbuilding_rtmesh_verified` with `19` files, `157748103` bytes, `MissingCount=0`, `ExtraCount=0`, and `HashDiffCount=0`.

## Public Boundary

This note is public-safe static RE accounting. It does not include private game assets, installed-game mutation, runtime launch proof, raw decompile bodies, or private media.

## Not Proven

- Exact source virtual names and full `rtmesh.cpp` or render-object source-body identity.
- Concrete `CRTBuilding`, `CRTMesh`, meshpose, imposter, particle/effect, quality-setting, or global list layouts.
- Runtime render, LOD, imposter, effect cleanup, BEA launch behavior, game patching, and rebuild parity.
