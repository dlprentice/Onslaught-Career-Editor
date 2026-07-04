# Ghidra Vector Tail Wave469 Evidence

Date: 2026-05-16

## Scope

Wave469 saved Ghidra name/signature/comment/tag corrections for `2` owner-neutral Vec3 helpers:

`0x004c7900` and `0x004c7d90`.

## Evidence

- Pre/post artifacts: `subagents/ghidra-static-reaudit/wave469-vector-tail-current/`
- Apply script: `tools/ApplyVectorTailWave469.java`
- Probe: `tools/ghidra_vector_tail_wave469_probe.py`
- Test alias: `npm run test:ghidra-vector-tail-wave469`
- Dry summary: `updated=0 skipped=2 created=0 would_create=0 renamed=0 would_rename=1 missing=0 bad=0`
- Apply summary: `updated=2 skipped=0 created=0 would_create=0 renamed=1 would_rename=0 missing=0 bad=0`
- Verify-dry summary: `updated=0 skipped=2 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`
- Post exports verified `2` metadata rows, `2` tag rows, `10` xref rows, `2` decompile exports plus `index.tsv`, and `130` focused instruction rows.
- Corrected stale `CRocket__NormalizeVec3InPlace` ownership to `Vec3__NormalizeInPlace`.
- Hardened `Vec3__CopyXYZ` to `void * __thiscall Vec3__CopyXYZ(void * this, void * src_vec3)` from `RET 0x4` / `EAX = ECX` evidence.
- Queue after refresh: `6057` functions, `2136` commented, `3921` commentless, `1705` undefined signatures, `1578` `param_N` signatures.
- Current telemetry proxies: comment-backed `2136/6057 = 35.26%`; strict comment-plus-clean-signature `2069/6057 = 34.16%`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260516-212835_post_wave469_vector_tail_verified` (`19` files, `157125511` bytes, `MissingCount=0`, `ExtraCount=0`, `HashDiffCount=0`).

## Boundary

This is static retail-binary evidence only. Runtime vector/particle/render behavior, exact vector/source identity, BEA launch behavior, game patching, and rebuild parity remain unproven.
