# Ghidra CRTTree Wave497 Readiness Note

Date: 2026-05-17

## Scope

Wave497 saved static Ghidra name/signature/comment/tag hardening and boundary recovery for twelve CRTTree-adjacent render-object functions:

| Address | Saved state |
| --- | --- |
| `0x004dd7b0` | `void __thiscall CRTTree__Init(void * this, void * init)` |
| `0x004dd850` | `void __fastcall CRTTree__VFuncSlot03_UpdateVisibilityState(void * this)` |
| `0x004dd960` | `void __thiscall CRTTree__VFuncSlot02_BuildRenderOutputs(void * this, void * renderContext)` |
| `0x004ddfd0` | `void __fastcall CRTTree__Destructor(void * this)` |
| `0x004de050` | `float __fastcall CRTTree__VFuncSlot06_GetResourceScalar164(void * this)` |
| `0x004de060` | `void * __fastcall SharedVFunc__ReturnResourceField150_004de060(void * this)` |
| `0x004de080` | `void * __thiscall CRTTree__ScalarDeletingDestructor(void * this, byte flags)` |
| `0x00516580` | `void * __cdecl PCRTID__CreateObject(int typeId)` |
| `0x004dbd40` | `float __thiscall SharedVFunc__ReturnFloat0Ret8_004dbd40(void * this, void * arg0, void * arg1)` |
| `0x004d6a50` | `void __thiscall SharedVFunc__WriteDefaultTransformOutputsRet16_004d6a50(void * this, void * outMatrix, void * outVec3, void * outScalar, void * arg3)` |
| `0x004dbc00` | `byte __thiscall SharedVFunc__ReturnFalseRet4_004dbc00(void * this, void * arg0)` |
| `0x004db880` | `void __thiscall CRenderThing__ForwardSlot26ToChildSlot68(void * this, void * arg0, void * arg1)` |

## Evidence

- Apply script: `tools/ApplyCRTTreeWave497.java`
- Probe: `tools/ghidra_crttree_wave497_probe.py`
- Scratch artifacts: `subagents/ghidra-static-reaudit/wave497-crttree-lifecycle-004ddfd0/`
- Dry/apply/verify:
  - Dry: `updated=0 skipped=3 created=0 would_create=9 renamed=0 would_rename=1 missing=0 bad=0`
  - Apply: `updated=12 skipped=0 created=9 would_create=0 renamed=1 would_rename=0 missing=0 bad=0`
  - Verify dry: `updated=0 skipped=12 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`
- Post-readback verified `12` metadata rows, `12` tag rows, `61` xref rows, `2364` instruction rows, `32` vtable rows, and `12` decompile exports.
- CRTTree vtable `0x005deb9c` slots 0, 1, 2, 3, 4, 6, 14, 17, 20, and 26 resolve to function objects after Wave497; slot 28 remains the deferred non-code pointer `0x00616840`.
- Focused probe: `py -3 tools\ghidra_crttree_wave497_probe.py --check` PASS.
- NPM probe: `cmd.exe /c npm run test:ghidra-crttree-wave497` PASS.
- Queue refresh: `6077` total functions, `2260` commented, `3817` commentless, `1663` undefined signatures, `1514` `param_N`; strict comment-plus-clean-signature proxy `2201/6077 = 36.22%`.
- Verified Ghidra backup: `G:\GhidraBackups\BEA_20260517-112202_post_wave497_crttree_verified` with `19` files, `157748103` bytes, `MissingCount=0`, `ExtraCount=0`, and `HashDiffCount=0`.

## Public Boundary

This note is public-safe static RE accounting. It does not include private game assets, installed-game mutation, runtime launch proof, raw decompile bodies, or private media.

## Not Proven

- Exact source virtual names and full `tree.cpp`, `rtmesh.cpp`, or render-object source-body identity.
- Concrete `CRTTree`, tree-resource, output-record, render-list, or falling-tree layouts.
- Runtime tree rendering, LOD, imposter, lifecycle behavior, BEA launch behavior, game patching, and rebuild parity.
