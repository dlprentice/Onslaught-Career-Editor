# Ghidra Wave982 Resource Descriptor Cleanup Correction (2026-05-30)

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 semantic revalidation:** Historical record; `0x005d4bd0` comment correction. The original text below remains provenance rather than current semantic authority. Use the [closeout](../../reverse-engineering/binary-analysis/ghidra-full-reaudit-closeout-2026-07-13.md); exact records are in `reverse-engineering/binary-analysis/ghidra-full-reaudit-corrections-2026-07-13.json` and `reverse-engineering/binary-analysis/ghidra-targeted-revalidation-corrections-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

Status: saved Ghidra rename/comment/tag/signature correction
Date: 2026-05-30
Branch: `main`
Tag: `resource-descriptor-cleanup-wave982`

## Scope

Wave982 re-reviewed the resource-descriptor cleanup thunk previously saved as `0x00403ff0 CDXLandscape__DestroyResourceDescriptorArray_Thunk` plus adjacent descriptor and particle cleanup context.

The saved correction is intentionally narrow:

| Address | Previous saved name | Wave982 saved name | Result |
| --- | --- | --- | --- |
| `0x00403ff0` | `CDXLandscape__DestroyResourceDescriptorArray_Thunk` | `CResourceDescriptorTable__DestroyEmbeddedDescriptor_Thunk` | Owner-neutralizing rename, signature/comment/tag correction |

Read-only context rows:

- `0x00403f40 CResourceDescriptor__ctor`
- `0x00403f80 CResourceDescriptor__dtor`
- `0x00515f60 CResourceDescriptorTable__ctor`
- `0x00516450 CResourceDescriptorTable__FreeAllEntries`
- `0x005164b0 CResourceDescriptorTable__InstantiateChain`
- `0x00405d80 CParticleManager__RemoveFromGlobalList_Thunk`
- `0x004cb050 CParticleManager__RemoveFromGlobalList`

## Evidence

Fresh read-back artifacts under ignored private evidence root:

```text
subagents/ghidra-static-reaudit/wave982-resource-descriptor-cleanup-review/
```

Dry/apply/final-dry:

```text
dry before saved mutation: updated=0 skipped=1 renamed=0 would_rename=1 signature_updated=1 comment_only_updated=1 missing=0 bad=0
idempotent apply after script fix/read-back: updated=0 skipped=1 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0
final dry: updated=0 skipped=1 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0
```

The first apply landed before the script's explicit manual-save call was removed; headless still reported `REPORT: Save succeeded`. The committed script now relies on headless save, and the clean idempotent apply plus final dry confirm the saved row.

Read-back result:

```text
metadata: 8/8 OK
tags: 8/8 OK
xrefs: 151 rows
instructions: 193 rows
decompile: 8/8 OK
queue: 6222/6222, 0 commentless, 0 undefined signatures, 0 param_N
```

Normalized progress tokens:

```text
static closure: 6222/6222 = 100.00%
Wave911 focused re-audit progress: 376/1408 = 26.70%
expanded static surface progress: 435/1478 = 29.43%
```

The corrected body is a 7-instruction thunk:

```text
PUSH CResourceDescriptor__dtor
PUSH 1
ADD ECX, 8
PUSH 0x41c
PUSH ECX
CALL CRT__EhVectorDestructorIterator_WithUnwind
RET
```

Representative xrefs to `0x00403ff0` include unwind cleanup callers `0x005d0fb0`, `0x005d1062`, `0x005d196b`, `0x005d2070`, `0x005d2470`, `0x005d2580`, `0x005d2760`, `0x005d4900`, `0x005d4bd0`, and `0x005d52e0`, plus DATA refs `0x00515f30` and `0x00515f90`.

## Review Result

The old `CDXLandscape` owner prefix was too strong for a helper reached by broad resource-descriptor unwind cleanup contexts. Wave982 replaces it with a neutral descriptor-table cleanup name tied to the observed constructor/destructor iterator evidence:

```text
void __thiscall CResourceDescriptorTable__DestroyEmbeddedDescriptor_Thunk(void * this)
```

The pass made no executable-byte change and did not launch BEA.

## Backup

Verified post-wave backup:

```text
[maintainer-local-ghidra-backup-root]\BEA_20260530-232843_post_wave982_resource_descriptor_cleanup_verified
files=19
bytes=173837191
MissingCount=0
ExtraCount=0
DiffCount=0
HashDiffCount=0
```

## Wave900+ Gate

Wave982 was started only after the Wave900-Wave981 probe/evidence audit gate was committed and pushed. That gate is documented in:

- `release/readiness/ghidra_wave900_plus_reaudit_probe_audit_2026-05-30.md`
- `release/readiness/ghidra_wave900_plus_evidence_audit_2026-05-30.md`

## Truth Boundary

This review improves saved static Ghidra name/signature/comment/tag evidence for one resource-descriptor cleanup thunk. It does not prove exact source identity, concrete descriptor-table layout, runtime unwind/cleanup behavior, BEA patch behavior, or rebuild parity.

## Next

Continue the Wave911 risk-ranked static re-audit from the next focused resource/render/frontend candidate while preserving read-only-first review, mutation only with fresh evidence, backup, validation, commit, and push gates.
