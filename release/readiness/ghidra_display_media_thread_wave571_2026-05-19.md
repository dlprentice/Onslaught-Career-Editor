# Ghidra Display/Media Thread Wave571 Readiness Note

Date: 2026-05-19
Status: PASS

## Scope

Wave571 hardened fourteen saved Ghidra rows in the display/cardid, CVar, texture predicate, and Bink/waiting-thread helper area:

| Address | Saved state | Evidence |
| --- | --- | --- |
| `0x005286e0` | `void __cdecl CD3DApplication__LoadCardIdAndApplyVendorTweaks(void * cardid_path)` | Opens the supplied `cardid.txt`-style path, parses Version/Vendor/Device/range/tweak lines, scans the `DAT_0089c018` CVar list, logs `Setting tweak`, and calls the matched CVar vfunc. |
| `0x00528aa0` | `void __thiscall CVar__Init(void * this, void * cvar_name, int initial_value)` | `RET 0x8` confirms two stack arguments after `this`; the helper links into `DAT_0089c018` and stores `initial_value` at `this+0x0c`. |
| `0x00528ad0` | `void __thiscall CVar__SetValueRounded(void * this, float value)` | `RET 0x4` confirms one stack float; the body rounds with `FISTP` and stores the integer value at `this+0x0c`. |
| `0x00528af0` | `bool __thiscall CDXTexture__IsResourceHandleValid(void * this)` | ECX-only predicate returning whether `this+0x0c` differs from `-1`; called by texture load and secondary-blend setup paths. |
| `0x00528b00` | `void __thiscall CEngine__InvokeCallbackIfStateMinusOne(void * this, int callback_value)` | `RET 0x4` removes the old phantom parameter; the helper converts `callback_value` to float and calls the first vfunc only when `this+0x0c == -1`. |
| `0x00528b60` | `int __stdcall CBinkOpenThread__WorkerMain(void * thread_obj)` | Win32 thread proc shape: waits on work event, exits on shutdown flag, runs the object vfunc under the mutex, clears `+0x15`, signals completion, and returns 0. |
| `0x00528bc0` | `void * __thiscall CWaitingThread__ctor_base(void * this)` | Renamed from `CWaitingThread__ctor_like_00528bc0`; initializes handle slots, clears shutdown/running flags, links into `DAT_0089c01c`, and is called by COggLoader, CBinkOpenThread, and mission object-code constructors. |
| `0x00528c70` | `bool __thiscall CBinkOpenThread__Init(void * this)` | Lazily creates mutex/event/thread handles and starts `CBinkOpenThread__WorkerMain`. |
| `0x00528d10` | `void __thiscall CBinkOpenThread__WaitForThread(void * this)` | Ensures init, spins with `Sleep(0)` while `+0x15` is set, then waits on the mutex. |
| `0x00528d50` | `void __thiscall CBinkOpenThread__StartAsync(void * this)` | Sets `+0x15`, releases the mutex, and signals the work event. |
| `0x00528d70` | `void __thiscall CBinkOpenThread__RunSync(void * this)` | Calls the object's first vfunc immediately, then releases the mutex. |
| `0x00528d90` | `bool __thiscall CBinkOpenThread__IsRunning(void * this)` | ECX-only `+0x15` running-flag reader. |
| `0x00528da0` | `void __thiscall CBinkOpenThread__Lock(void * this)` | Ensures init and waits on mutex `+0x08`. |
| `0x00528dc0` | `void __thiscall CBinkOpenThread__Unlock(void * this)` | Releases mutex `+0x08`. |

No `source-parity` tag was applied. This tranche is bounded to saved retail binary evidence; source identity, exact layouts, runtime D3D/media/thread behavior, BEA patching, and rebuild parity remain deferred.

## Verification

- Dry pass: `updated=0 skipped=14 renamed=0 would_rename=1 missing=0 bad=0`
- Apply pass: `updated=14 skipped=0 renamed=1 would_rename=0 missing=0 bad=0`, `REPORT: Save succeeded`
- Final dry: `updated=0 skipped=14 renamed=0 would_rename=0 missing=0 bad=0`, `REPORT: Save succeeded`
- Post exports: `14` metadata rows, `14` tag rows, `129` xref rows, `1134` target instruction rows, and `14` target decompiles
- Focused probe: `py -3 tools\ghidra_display_media_thread_wave571_probe.py --check` PASS
- Npm wrapper: `cmd.exe /c npm run test:ghidra-display-media-thread-wave571` PASS
- Queue refresh: `6093` total functions, `2849` commented, `3244` commentless, `1485` exact-undefined signatures, `1153` `param_N` signatures
- Post-Wave571 comment-backed proxy: `2849 / 6093 = 46.76%`
- Post-Wave571 strict clean-signature proxy: `2797 / 6093 = 45.91%`
- Backup: `[maintainer-local-ghidra-backup-root]\BEA_20260519-001056_post_wave571_display_media_thread_verified`
- Backup verification: `19` files, `160107399` bytes, source/destination manifest hash `710526A0A69117FABF0A1C4E5203B06AF9F1638B4AA7F904D1DC5168E8CA0E4E`

## Limits

This is saved static Ghidra evidence only. No runtime D3D/media/thread behavior was claimed. Exact CVar, CDXTexture, waiting-thread, and Bink/open-thread layouts, exact source identity, BEA launch, game patching, and rebuild parity remain unproven.
