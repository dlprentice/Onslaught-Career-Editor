# Ghidra Frontend Save/Multiplayer Wave802 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-24
Scope: `frontend-save-multiplayer-wave802`

Wave802 frontend save/multiplayer saved comments/tags/signatures for eight raw commentless or helper-body rows. The pass corrected two stale frontend labels, corrected four destructor/cleanup helper labels, hardened seven signatures, left one constructor name in place, made no function-boundary changes, and made no executable-byte changes.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x0044d390 FEMessBox__Create` | Corrected stale `CFEPSaveGame__InitDialogAndLayoutState`; `RET 0x2c` proves eleven explicit stack arguments after `ECX=this`; source callsites in FEPSaveGame.cpp, FEPLoadGame.cpp, and FrontEnd.cpp call `FEMESSBOX.Create(...)`. |
| `0x00465640 CFMV__PlayFullscreenWithLoadingGate` | Corrected stale `CLTShell__InvokeWithLoadingTransitionGate`; `RET 0x1c` proves seven explicit stack arguments after `ECX=this`; the body toggles the non-interactive/loading gate, conditionally forwards `g_LanguageIndex`, dispatches vtable slot `+0x2c`, then clears the gate. |
| `0x00465f10 CFEPMultiplayerStart__ctor` | Constructor called by `CDXFrontEnd__Constructor`; installs the CFEPMultiplayerStart vtable, constructs monitor/camera/video/member helpers, calls `CMissionScriptObjectCode__CMissionScriptObjectCode`, and initializes the `SubObj8848` helper. |
| `0x004661c0 DeviceObject__dtor_thunk` | Corrected ctor-like placeholder; one-instruction jump to `0x00512d50 DeviceObject__dtor_body`. |
| `0x004661f0 CFEPMultiplayerStart__CleanupMissionScriptWaitingThread` | Corrected init-like placeholder; adds `0x0c` to `ECX` and jumps to `0x00528bf0 CWaitingThread__dtor_body` for the CMissionScriptObjectCode waiting-thread subobject. |
| `0x00466290 CWaitingThread__dtor_thunk` | Corrected ctor-like placeholder; one-instruction jump to `0x00528bf0 CWaitingThread__dtor_body`. |
| `0x00512d50 DeviceObject__dtor_body` | Installs the DeviceObject scalar-deleting destructor vtable and unlinks `this` from the two global DeviceObject lists rooted at `DAT_00889074` and `DAT_00889078`. |
| `0x00528bf0 CWaitingThread__dtor_body` | Signals shutdown, waits/closes thread/event handles at `this+0x04/+0x08/+0x0c/+0x10`, resets them to `-1`, and unlinks from `DAT_0089c01c`. |

Read-back evidence:

- `ApplyFrontendSaveMultiplayerWave802.java dry`: `updated=0 skipped=8 renamed=0 would_rename=7 signature_updated=7 comment_only_updated=1 missing=0 bad=0`
- First apply intentionally remains in evidence: seven rows saved, while `0x004661f0` exposed a read-back signature mismatch because the first script spec supplied both implicit `this` and explicit `mission_script_minus_c`; log summary `updated=7 skipped=0 renamed=7 would_rename=0 signature_updated=5 comment_only_updated=3 missing=0 bad=1`, with `REPORT: Save succeeded`.
- Corrective dry/apply after fixing the ABI spec: `updated=0 skipped=8 renamed=0 would_rename=0 signature_updated=1 comment_only_updated=0 missing=0 bad=0`, then `updated=1 skipped=7 renamed=0 would_rename=0 signature_updated=1 comment_only_updated=0 missing=0 bad=0`, with `REPORT: Save succeeded`.
- Final dry: `updated=0 skipped=8 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`
- Post exports: 8 metadata rows, 8 tag rows, 91 xref rows, 2088 instruction rows, and 8 decompile rows.
- Queue after Wave802: 6098 total, 5572 commented, 526 commentless, 0 exact-undefined signatures, 0 `param_N` signatures (`0 param_N`), strict clean-signature proxy `5572/6098 = 91.37%`.
- Next raw commentless row: `0x0046d3a0 CGame__SetSlot`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260524-081932_post_wave802_frontend_save_multiplayer_verified`, 19 files, 171314055 bytes, `DiffCount=0`.

What remains unproven:

- Exact source-body identity for these helpers.
- Exact FEMessBox, CFMV, CFEPMultiplayerStart, DeviceObject, and CWaitingThread layouts beyond the stated offsets/globals.
- Runtime save/load dialog, FMV playback/localization, multiplayer frontend, device-object lifetime, or waiting-thread behavior.
- BEA patching behavior.
- Rebuild parity.
