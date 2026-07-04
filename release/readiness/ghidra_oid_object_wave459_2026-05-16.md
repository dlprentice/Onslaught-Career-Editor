# Ghidra OID Object Factory / Lifecycle Wave459 Evidence

Date: 2026-05-16

## Scope

Wave459 saved Ghidra name/signature/comment/tag corrections for `12` OID object factory, render-wrapper, base-init, and scalar-deleting destructor targets:

`0x004bf090`, `0x004bfa60`, `0x004bfab0`, `0x004bfce0`, `0x004bfd00`, `0x004bfd20`, `0x004bfd40`, `0x004bfd60`, `0x004bfd80`, `0x004bfda0`, `0x004bfdc0`, and `0x004bfde0`.

## Evidence

- Pre/post artifacts: `subagents/ghidra-static-reaudit/wave459-oid-object-current/`
- Apply script: `tools/ApplyOidObjectWave459.java`
- Probe: `tools/ghidra_oid_object_wave459_probe.py`
- Test alias: `npm run test:ghidra-oid-object-wave459`
- Dry summary: `updated=0 skipped=12 created=0 would_create=0 renamed=0 would_rename=8 missing=0 bad=0`
- Apply summary: `updated=12 skipped=0 created=0 would_create=0 renamed=8 would_rename=0 missing=0 bad=0`
- Verify-dry summary: `updated=0 skipped=12 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`
- Post exports verified `12` metadata rows, `12` tag rows, `24` xref rows, `12` decompile exports plus `index.tsv`, `5772` focused instruction rows, and `88` vtable-slot rows.
- Hardened `OID__CreateObject`, `OID__InitTargetData`, `OID__RenderWithState1BOverride`, and `OID__InitBaseObject`.
- Corrected eight vtable slot-1 lifecycle labels to `CTree__scalar_deleting_dtor`, `CActorBase__shared_scalar_deleting_dtor_004bfd00`, `CRocket__scalar_deleting_dtor`, `CWaypoint__scalar_deleting_dtor`, `CSpawnerThing__scalar_deleting_dtor`, `CSphereTrigger__scalar_deleting_dtor`, `CWingmanStart__scalar_deleting_dtor`, and `CEscapePod__scalar_deleting_dtor`.
- Queue after refresh: `6057` functions, `2035` commented, `4022` commentless, `1727` undefined signatures, `1636` `param_N` signatures.
- Current telemetry proxies: comment-backed `2035/6057 = 33.60%`; strict comment-plus-clean-signature `1971/6057 = 32.54%`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260516-170043_post_wave459_oid_object_verified` (`19` files, `156863367` bytes, `MissingCount=0`, `ExtraCount=0`, `HashDiffCount=0`).

## Boundary

This is static retail-binary evidence only. Runtime object construction, render-state behavior, cleanup behavior, exact object layouts, exact source identities, BEA launch behavior, game patching, and rebuild parity remain unproven.
