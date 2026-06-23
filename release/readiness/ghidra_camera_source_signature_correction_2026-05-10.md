# Ghidra Camera Source Signature Correction - 2026-05-10

## Summary

This wave saved a focused Camera-family Ghidra correction after fresh metadata, decompile, xref, instruction, source, and caller-context review. It keeps the claim bounded to static saved-Ghidra refinement.

The saved changes cover:

| Address | Saved Ghidra state | Evidence boundary |
| --- | --- | --- |
| `0x00418ef0` | `void * __thiscall CThing3rdPersonCamera__ctor(void * this, void * forThing)` | Source/decompile parity for active-reader setup and `CBSpline` control points from tracked-thing radius. |
| `0x00419120` | `void * __thiscall CThing3rdPersonCamera__scalar_deleting_dtor(void * this, byte flags)` | Scalar deleting destructor wrapper. |
| `0x00419140` | `void __fastcall CThing3rdPersonCamera__dtor(void * this)` | Source/decompile parity for curve release and active-reader unlink. |
| `0x004198d0` | `void * __thiscall CPanCamera__ctor(void * this, void * forThing, void * curve, float length)` | Source/decompile parity for tracked thing, curve, start time, length, and initial update. |
| `0x00419a40` | `void * __thiscall CPanCamera__scalar_deleting_dtor(void * this, byte flags)` | Scalar deleting destructor wrapper. |
| `0x00419a60` | `void __fastcall CPanCamera__dtor(void * this)` | Source/decompile parity for curve cleanup and active-reader unlink. |
| `0x00419b00` | `void __fastcall CPanCamera__Update(void * this)` | Source/decompile parity for spline-driven pan update and `UPDATE_CAMERA` reschedule. |
| `0x00419e00` | `void * __thiscall CViewPointCamera__ctor(void * this, void * point, float * rotateSpeed, float * startDistance, float * endDistance, float * timeBetweenDistance)` | Corrects the stale `CViewPointCamera__ctor_like_00419e00` label using source/decompile/callsite evidence. |
| `0x0041a740` | `void * __thiscall CControllableCamera__ctor(void * this, float posX, float posY, float posZ, float posW, float orientation00, float orientation01, float orientation02, float orientation03, float orientation10, float orientation11, float orientation12, float orientation13, float orientation20, float orientation21, float orientation22, float orientation23)` | Hardens the previous `undefined CControllableCamera__ctor(void)` state using caller stack-copy evidence for by-value `FVector` and `FMatrix`. |

## Validation

- `py -3 tools\ghidra_camera_source_signature_correction_probe_test.py` - PASS; 3/3 tests.
- Headless `ApplyCameraSourceSignatureCorrection.java` dry/apply - PASS; dry `updated=0 skipped=9 renamed=0 missing=0 bad=0`; apply `updated=9 skipped=0 renamed=1 missing=0 bad=0`; `REPORT: Save succeeded`.
- Headless metadata/decompile/xref/instruction read-back - PASS; `9/9` metadata rows, `9/9` decompile rows, `13` xref rows, and `801` instruction rows.
- `py -3 tools\ghidra_camera_source_signature_correction_probe.py --check` - PASS; `9` targets, `1` renamed target, `0` failures.
- `cmd.exe /c npm run test:ghidra-camera-source-signature-correction` - PASS.
- `py -3 -m py_compile tools\ghidra_camera_source_signature_correction_probe.py tools\ghidra_camera_source_signature_correction_probe_test.py` - PASS.
- Refreshed queue/baseline - PASS; queue reports `5868` functions, `659` commented functions, `5209` commentless functions, `2044` undefined signatures, `2334` `param_N` signatures, and `0` helper/wrapper/uncertain-owner names.

## Not Proven

This does not prove concrete Camera-family structure layouts, tags, local variable names, full type recovery, runtime camera/free-camera/death-camera behavior, BEA launch behavior, game patching, or rebuild parity. It also does not mean all Camera.cpp functions are complete; it only advances the listed saved names/signatures/comments with current read-back evidence.
