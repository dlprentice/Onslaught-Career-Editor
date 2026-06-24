# Ghidra Frontend/Common Video Tranche - 2026-05-13

Status: GREEN public-safe static RE evidence.

## Summary

Serialized headless dry/apply/read-back corrected and hardened `7` frontend/common video-adjacent saved Ghidra targets in the Steam `BEA.exe` project. The pass creates the missing `CFEPCommon__Init` function object, corrects the former Goodies-owned video helpers to `CFEPCommon__StartVideo` and `CFEPCommon__StopVideo`, corrects `0x00452da0` to shared `RET 0x8` no-op behavior, and preserves the video-quad render helper while hardening its signature.

## Saved Targets

| Address | Saved Ghidra state | Evidence summary |
| --- | --- | --- |
| `0x00452b00` | `bool __thiscall CFEPCommon__Init(void * this)` | Created missing CFEPCommon vtable init-slot function object; opens the common `FEBack128.vid` frontend background and returns true. |
| `0x00452b30` | `void __thiscall CFEPCommon__Shutdown(void * this)` | Closes frontend video, frees the owned `this+0x4` object when present, then clears the pointer. |
| `0x00452b60` | `void __thiscall CFrontEndPage__Process_NoOp(void * this, int state)` | Shared frontend-page no-op process slot; instruction body is `RET 0x4`. |
| `0x00452ce0` | `void __stdcall CFrontEnd__RenderVideoQuadScaledToWindow(float scale, int argb, float center_x, float center_y)` | Resolves default center coordinates from platform window dimensions, sets render state, scales the video quad, and calls the frontend video renderer. |
| `0x00452da0` | `void __stdcall SharedVFunc__NoOp_Ret08(int unused0, int unused1)` | Corrects the older slot-specific label; instruction body is `RET 0x8` and broad unrelated vtables reuse it. |
| `0x00452db0` | `void __thiscall CFEPCommon__StartVideo(void * this, int start_flag)` | Corrects former Goodies-owned helper label; Goodies FMV return and another frontend call site use the common video start helper. |
| `0x00452de0` | `void __thiscall CFEPCommon__StopVideo(void * this)` | Corrects former Goodies-owned helper label; Goodies FMV path calls the common video stop helper. |

## Validation

| Check | Result |
| --- | --- |
| Focused probe tests | `py -3 tools\ghidra_frontend_media_common_video_probe_test.py` passed `2/2`. |
| Python compile | `py -3 -m py_compile tools\ghidra_frontend_media_common_video_probe.py tools\ghidra_frontend_media_common_video_probe_test.py` passed. |
| Headless apply | Initial `ApplyFrontendMediaCommonVideoTranche.java` dry reported `updated=0 skipped=7 created=0 would_create=1 renamed=0 would_rename=4 missing=0 bad=0`; apply reported `updated=7 skipped=0 created=1 would_create=0 renamed=4 would_rename=0 missing=0 bad=0` and `REPORT: Save succeeded`. |
| Comment hardening rerun | A follow-up dry/apply after tightening the `CFEPCommon__Shutdown` comment reported dry `updated=0 skipped=7 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0` and apply `updated=7 skipped=0 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`. |
| Read-back exports | Metadata `7`, decompile `7`, xrefs `153`, instruction rows `637`, tags `7`, and vtable-slot rows `84`. |
| Focused package probe | `cmd.exe /c npm run test:ghidra-frontend-media-common-video` passed with targets `7`, xref evidence hits `10`, instruction evidence hits `13`, and vtable evidence hits `4`. |
| Goodies dependent read-back | Refreshed the Goodies decompile proof and `py -3 tools\goodies_ghidra_readback_probe.py --check` passed with functions `6/6`, instruction contexts `8/8`, and unlock/field-map checks passing. |
| Whole-database queue | Refreshed headless `ExportFunctionQualitySnapshot.java` plus `cmd.exe /c npm run test:ghidra-static-reaudit-queue` passed with `6021` total functions, `1339` commented functions, `4682` commentless functions, `1939` undefined signatures, and `1978` `param_N` signatures. |
| Current proxies | Comment-backed `1339/6021 = 22.24%`; strict clean-signature `1274/6021 = 21.16%`. These are telemetry only, not milestones. |
| Ghidra backup | Live `BEA.gpr`/`BEA.rep` backup verified at `G:\GhidraBackups\BEA_20260513_121200_post_wave374_frontend_common_video_verified` with `19` files, `153488263` bytes, and `HashDiffCount=0`. |

## Claim Boundary

This is saved static retail Ghidra boundary/name/signature/comment/tag refinement. It does not prove exact CFEPCommon class layout, concrete local variable types, runtime frontend video playback, packaged app behavior, BEA launch behavior, game patching, or rebuild parity.
