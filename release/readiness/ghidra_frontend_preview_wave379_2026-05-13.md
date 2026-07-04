# Ghidra Frontend Preview/Camera Wave379 Readiness Note

Status: public-safe static RE evidence
Date: 2026-05-13

## Summary

Wave 379 serialized a Ghidra headless dry/apply/read-back pass over ten frontend preview and camera-adjacent functions. The pass corrected four stale saved labels and hardened signatures, comments, and tags for six more targets. This is saved static retail Ghidra evidence only.

## Saved Targets

| Address | Saved state | Evidence boundary |
| --- | --- | --- |
| `0x00466130` | `void __fastcall CGenericCamera__ctor(pointer this)` | Corrects the old constructor-like label to a CGenericCamera constructor body that installs the CGenericCamera vtable. |
| `0x00466140` | `void __thiscall CGenericCamera__GetPos(void * this, pointer out_pos)` | Copies four dwords from the receiver position block into the output pointer and returns with `ret 0x4`. |
| `0x00466170` | `pointer __thiscall CGenericCamera__scalar_deleting_dtor(void * this, uchar free_flag)` | Calls `CGenericCamera__dtor`, conditionally frees on `free_flag`, and returns the receiver. |
| `0x004661b0` | `void __fastcall CGenericCamera__dtor(pointer this)` | Resets the receiver to the base CGenericCamera vtable. |
| `0x0046b950` | `void __thiscall CFEPMultiplayerStart__LoadPreviewMeshFromConfig(void * this, pointer preview_config)` | Loads preview transform/config data, creates the preview object at `+0x58`, and initializes preview animation/timer fields. |
| `0x0046ba90` | `void __fastcall CFrontEndThing__dtor_base(pointer this)` | Corrects the old constructor-like label; destructor-base cleanup resets the CFrontEndThing vtable and releases the preview object pointer at `+0x58`. |
| `0x0046bab0` | `void __thiscall CFEPMultiplayerStart__SetPreviewAnimationByName(void * this, char * animation_name)` | Resolves an animation name through the preview object's animation set and updates preview duration/timer fields. |
| `0x0046bc20` | `void __fastcall CFEPMultiplayerStart__StopPreviewAnimation(pointer this)` | Dispatches the preview object's vcall `+0x08` with zero when the preview object exists. |
| `0x0046c030` | `pointer __thiscall CThingCamera__scalar_deleting_dtor(void * this, uchar free_flag)` | Corrects the old vfunc label to a scalar deleting destructor that calls `CThingCamera__dtor_base`. |
| `0x0046c050` | `void __fastcall CThingCamera__dtor_base(pointer this)` | Corrects the old constructor-like label; destructor-base cleanup removes a linked reader cell and resets to the base CGenericCamera vtable. |

## Validation

- Focused TDD guard was introduced red, then passed with `2/2` tests.
- `py -3 -m py_compile tools\ghidra_frontend_preview_wave379_probe.py tools\ghidra_frontend_preview_wave379_probe_test.py` passed.
- Headless dry/apply passed serially: dry `updated=0 skipped=10 renamed=0 would_rename=4 missing=0 bad=0`; apply `updated=10 skipped=0 renamed=4 would_rename=0 missing=0 bad=0`; apply reported `REPORT: Save succeeded`.
- Read-back verified `10` metadata rows, `10` decompile exports, `41` xref rows, `890` instruction rows, and `10` tag rows.
- `cmd.exe /c npm run test:ghidra-frontend-preview-wave379` passed with focused probe status `PASS`, `10` targets, `14` xref evidence hits, and `23` instruction evidence hits.
- The refreshed whole-database queue reports `6026` functions, `1388` commented functions, `4638` commentless functions, `1939` undefined signatures, and `1939` `param_N` signatures.
- Current static RE confirmation proxies are telemetry only: comment-backed `1388/6026 = 23.03%`; strict clean-signature `1323/6026 = 21.95%`.
- The actual live Ghidra project was backed up to an out-of-repo `[maintainer-local-backup-volume]` backup drive under label `BEA_20260513_150035_post_wave379_frontend_preview_verified`, with `19` files, `153652103` bytes, and `HashDiffCount=0`.

## Not Proven

- This does not prove runtime frontend preview mesh, animation, or camera behavior.
- This does not prove exact Stuart-source method identity for every target.
- This does not recover exact class layouts, concrete local variables, or complete data types.
- This does not launch or patch BEA.exe.
- This does not prove packaged app behavior, public redistribution readiness, or rebuild parity.
