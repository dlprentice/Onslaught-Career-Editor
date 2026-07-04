# Ghidra Mine / Missile Wave456 Evidence

Date: 2026-05-16

## Scope

Wave456 saved Ghidra name/signature/comment/tag corrections for `8` `CMine`, `CMissile`, and base `CMotionController` targets:

`0x004ba150`, `0x004ba490`, `0x004ba9d0`, `0x004baae0`, `0x004bac10`, `0x004bae10`, `0x004bae30`, and `0x004bae50`.

## Evidence

- Pre/post artifacts: `subagents/ghidra-static-reaudit/wave456-mine-missile-current/`
- Apply script: `tools/ApplyMineMissileWave456.java`
- Probe: `tools/ghidra_mine_missile_wave456_probe.py`
- Test alias: `npm run test:ghidra-mine-missile-wave456`
- Dry summary: `updated=0 skipped=8 created=0 would_create=0 renamed=0 would_rename=6 missing=0 bad=0`
- Apply summary: `updated=8 skipped=0 created=0 would_create=0 renamed=6 would_rename=0 missing=0 bad=0`
- Verify-dry summary: `updated=0 skipped=8 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`
- Post exports verified `8` metadata rows, `8` tag rows, `35` xref rows, `8` decompile exports plus `index.tsv`, `1544` focused instruction rows, and `64` vtable-slot rows.
- Revalidated `CMine__Init` and `CMissile__Init` with two-argument `__thiscall` signatures and bounded comments.
- Corrected stale helper/vfunc labels to `CMine__VFunc02_CleanupLinkedParticleAndForward`, `CMine__TryDestroyedResetAndDispatchVFunc1D4`, `CMissile__DispatchLinkedObjectVFunc68AndPostHook`, `CMotionController__scalar_deleting_dtor`, `CMotionController__ctor_base`, and `CMotionController__dtor_base`.
- Corrected the base motion-controller constructor evidence: `CMotionController__ctor_base` writes vtable `0x005dc778` and clears `+0x04/+0x08` with zeroed `ECX`.
- Queue after refresh: `6057` functions, `2005` commented, `4052` commentless, `1730` undefined signatures, `1662` `param_N` signatures.
- Current telemetry proxies: comment-backed `2005/6057 = 33.10%`; strict comment-plus-clean-signature `1942/6057 = 32.06%`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260516-152041_post_wave456_mine_missile_verified` (`19` files, `156765063` bytes, `MissingCount=0`, `ExtraCount=0`, `HashDiffCount=0`).

## Boundary

This is static retail-binary evidence only. Runtime mine placement/water/destruction behavior, missile payload behavior, exact virtual-slot names/source identities, concrete layouts, BEA launch behavior, game patching, and rebuild parity remain unproven.
