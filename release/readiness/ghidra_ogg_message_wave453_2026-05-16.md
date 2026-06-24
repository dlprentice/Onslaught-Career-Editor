# Ghidra Ogg Loader / Message Constructor Wave453 Evidence

Date: 2026-05-16

## Scope

Wave453 saved Ghidra name/signature/comment/tag corrections for `5` adjacent Ogg loader and queued-message targets:

`0x004b6cd0`, `0x004b6d30`, `0x004b6d90`, `0x004b6df0`, and `0x004b6e50`.

## Evidence

- Pre/post artifacts: `subagents/ghidra-static-reaudit/wave453-ogg-message-current/`
- Apply script: `tools/ApplyOggMessageWave453.java`
- Probe: `tools/ghidra_ogg_message_wave453_probe.py`
- Test alias: `npm run test:ghidra-ogg-message-wave453`
- Initial dry summary: `updated=0 skipped=5 created=0 would_create=0 renamed=0 would_rename=5 missing=0 bad=0`
- Initial apply exposed a scalar-deleting destructor signature issue at `0x004b6df0`; the preserved ignored log is `apply_initial_extra_this_signature.log`.
- Correction dry summary: `updated=0 skipped=5 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`
- Final apply summary: `updated=5 skipped=0 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`
- Verify-dry summary: `updated=0 skipped=5 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`
- Post exports verified `5` metadata rows, `5` tag rows, `12` xref rows, `5` decompile exports, and `505` focused instruction rows.
- Corrected four COggLoader names/signatures: `COggLoader__readerSubobject_dtor_body`, `COggLoader__ctor_base`, `COggLoader__ThreadProc_ReadPathIntoBuffer`, and `COggLoader__readerSubobject_scalar_deleting_dtor`.
- Corrected `CMessage__ctor_base`; `ret 0x1c` confirms seven stack arguments after `this`, including `message_text`, optional `active_reader_target`, and `queue_sort_key`, while unknown payload fields remain generic by design.
- Queue after refresh: `6057` functions, `1978` commented, `4079` commentless, `1733` undefined signatures, `1674` `param_N` signatures.
- Current telemetry proxies: comment-backed `1978/6057 = 32.66%`; strict clean-signature `1915/6057 = 31.62%`.
- Verified backup: `G:\GhidraBackups\BEA_20260516-134037_post_wave453_ogg_message_verified` (`19` files, `156633991` bytes, `MissingCount=0`, `ExtraCount=0`, `HashDiffCount=0`).

## Boundary

This is static retail-binary evidence only. Runtime Ogg streaming/audio playback, message display/audio behavior, concrete COggLoader/COggFileRead/CMessage layouts, exact source identities, BEA launch behavior, game patching, and rebuild parity remain unproven.
