# Ghidra InfantryUnit VFunc02 Wave805 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-24
Scope: `infantryunit-vfunc02-wave805`

Wave805 InfantryUnit vfunc02 saved a behavior-bounded rename, signature, comments, and tags for `0x00488f60 CInfantryUnit__VFunc02_ClearParticleLinkAndForward`. The pass replaced the old address-suffixed placeholder `CInfantryUnit__VFunc_02_00488f60`, made no function-boundary changes, and made no executable-byte changes.

Representative anchor:

| Address | Evidence |
| --- | --- |
| `0x00488f60 CInfantryUnit__VFunc02_ClearParticleLinkAndForward` | DATA xref from `0x005e2734`, the `0x005e2730` CInfantryUnit primary vtable slot after `CInfantryUnit__scalar_deleting_dtor`; body uses `ECX` as `this`, calls `ParticleEffectLink__SetHandleStateAndClear(this+0x270, 0)`, then forwards to `CUnit__VFunc02_CleanupWorldLinksAndForward(this)`. |

Read-back evidence:

- `ApplyInfantryUnitVFunc02Wave805.java dry`: `updated=0 skipped=1 renamed=0 would_rename=1 signature_updated=1 comment_only_updated=0 missing=0 bad=0`
- `ApplyInfantryUnitVFunc02Wave805.java apply`: `updated=1 skipped=0 renamed=1 would_rename=0 signature_updated=1 comment_only_updated=0 missing=0 bad=0`
- `ApplyInfantryUnitVFunc02Wave805.java final dry`: `updated=0 skipped=1 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`
- Post exports: 1 metadata row, 1 tag row, 1 xref row, 121 instruction rows, 1 decompile row, 16 vtable-slot rows, 2 helper metadata rows, and 2 helper decompile rows.
- Queue after Wave805: 6098 total, 5577 commented, 521 commentless, 0 exact-undefined signatures, 0 `param_N`, comment-backed proxy `5577/6098 = 91.46%`, strict clean-signature proxy `5577/6098 = 91.46%`.
- Next raw commentless row: `0x0048ddf0 thunk_DXMemBuffer__Close`.
- Verified backup: `G:\GhidraBackups\BEA_20260524-094441_post_wave805_infantryunit_vfunc02_verified`, 19 files, 171314055 bytes, `DiffCount=0`.

What this proves:

- The target function row exists in the saved Ghidra project.
- The saved name is `CInfantryUnit__VFunc02_ClearParticleLinkAndForward`.
- The saved signature is `void __fastcall CInfantryUnit__VFunc02_ClearParticleLinkAndForward(void * this)`.
- The saved comment and tags include `infantryunit-vfunc02-wave805` and `wave805-readback-verified`.
- The observed cleanup body is static retail Ghidra evidence tied to vtable DATA xref, helper metadata, decompile, and instruction exports.

What remains unproven:

- Exact source virtual name.
- Concrete infantry-unit particle/effect link layout beyond the observed `this+0x270` owner-link cell.
- Runtime cleanup order.
- BEA patching behavior.
- Rebuild parity.
