# Ghidra Ogg Message Lifecycle Review Wave1015

Status: PASS read-only static read-back evidence
Date: 2026-05-31
Scope: `ogg-message-lifecycle-review-wave1015`

Wave1015 re-read the adjacent `COggLoader` reader lifecycle and `CMessage` queued-message lifecycle rows with fresh Ghidra headless exports. The pass made no Ghidra mutation, no rename, no signature change, no function-boundary change, no executable-byte change, no BEA launch, and no runtime/game-file mutation.

Primary anchors:

| Address | Evidence |
| --- | --- |
| `0x004b6cd0 COggLoader__readerSubobject_dtor_body` | Called by `COggLoader__readerSubobject_scalar_deleting_dtor`; calls `COggFileRead__dtor_body` on the reader subobject and `CWaitingThread__dtor_body` on the adjusted base. |
| `0x004b6d30 COggLoader__ctor_base` | Calls `CWaitingThread__ctor_base`, constructs `COggFileRead__ctor_base` at `this+0x20`, installs reader-subobject vtable `0x005dc690`, and installs base vtable `0x005dc688`. |
| `0x004b6d90 COggLoader__ThreadProc_ReadPathIntoBuffer` | DATA/vtable ref `0x005dc688`; checks path byte at `this+0x102310`, opens the reader subobject, reads up to `0x100000` bytes into `this+0x2310`, stores byte count/status at `this+0x102414`, and closes on success. |
| `0x004b6df0 COggLoader__readerSubobject_scalar_deleting_dtor` | DATA/vtable ref `0x005dc690`; final signature remains `this, flags`, calls `COggLoader__readerSubobject_dtor_body`, conditionally frees the adjusted base pointer, and `RET 0x4` confirms one stack argument. |
| `0x004b6e50 CMessage__ctor_base` | Called by `CUnit__ApplyDamage`, `CUnit__TriggerEffect`, and `IScript__PlaySound*` helpers; `RET 0x1c` confirms seven stack arguments after `this`; stores `message_text`, optional active-reader target, and queue sort key at `+0x2c`. |
| `0x004b6f10 CMessage__scalar_deleting_dtor` | DATA/vtable ref `0x005dc6b8`; calls `CMessage__dtor_base`, conditionally frees `this`, and `RET 0x4` confirms one stack `flags` argument. |
| `0x004b7160 CMessage__dtor_base` | Called by `CMessage__scalar_deleting_dtor`; resets the vtable, removes active-reader cell `+0x30` from its pointer set when present, and calls `CMonitor__Shutdown`. |

Read-back evidence:

- Target exports verified `7` metadata rows, `7` tag rows, `14` xref rows, `195` body-instruction rows, and `7` decompile rows.
- Context exports verified `17` metadata rows, `549` xref rows, `548` body-instruction rows, and `17` decompile rows.
- Context rows covered `CWaitingThread__ctor_base`, `CWaitingThread__dtor_body`, `COggFileRead` constructor/destructor/open/read/close/state accessors, `CMessageBox__InsertQueuedMessageSortedAndMaybeAdvance`, `CMessageBox__StartVoiceOrFallbackTextReveal`, `CMessageBox__StopVoicePlaybackIfNotInCutscene`, `CGenericActiveReader__SetReader`, `CSPtrSet__Remove`, and `CMonitor__Shutdown`.
- Prior evidence referenced: Wave453 Ogg/message correction, Wave450 MessageBox correction, Wave568 Ogg/Vorbis reader correction, Wave571 waiting-thread hardening, Wave907 frontend/input/game-loop static review, and Wave908 audio/media/cutscene static review.
- Export-contract function-quality closure remains `6238/6238 = 100.00%`.
- Wave911 focused re-audit progress advances to `511/1408 = 36.29%`.
- Expanded static surface progress is `736/1493 = 49.30%`.
- Wave911 top-500 risk-ranked coverage advances to `437/500 = 87.40%`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260531-192131_post_wave1015_ogg_message_lifecycle_review_verified`, `18` files, `173968263` bytes, `DiffCount=0`, `HashDiffCount=0`.

Probe token anchor: Wave1015; ogg-message-lifecycle-review-wave1015; 0x004b6cd0 COggLoader__readerSubobject_dtor_body; 0x004b6d30 COggLoader__ctor_base; 0x004b6d90 COggLoader__ThreadProc_ReadPathIntoBuffer; 0x004b6df0 COggLoader__readerSubobject_scalar_deleting_dtor; 0x004b6e50 CMessage__ctor_base; 0x004b6f10 CMessage__scalar_deleting_dtor; 0x004b7160 CMessage__dtor_base; 511/1408 = 36.29%; 736/1493 = 49.30%; 437/500 = 87.40%; 6238/6238 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260531-192131_post_wave1015_ogg_message_lifecycle_review_verified; no mutation.

Boundary note: this proves static read-back coherence for the selected Ogg loader and queued-message lifecycle rows only. Runtime Ogg streaming/audio playback, runtime message display, runtime voice playback, exact source-body identity, concrete `COggLoader`/`COggFileRead`/`CMessage`/`CMessageBox` layouts, BEA patching, and rebuild parity remain separate proof.
