# Ghidra Particle Archive Buffer Cleanup Wave823 Readiness Note

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 semantic revalidation:** Historical record; `0x004cf050` → `CMenuItem__Destructor_Thunk` (was `CMenuItem__Destructor`). The original text below remains provenance rather than current semantic authority. Use the [closeout](../../reverse-engineering/binary-analysis/ghidra-full-reaudit-closeout-2026-07-13.md); exact records are in `reverse-engineering/binary-analysis/ghidra-full-reaudit-corrections-2026-07-13.json` and `reverse-engineering/binary-analysis/ghidra-targeted-revalidation-corrections-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

Status: complete static read-back evidence
Date: 2026-05-24
Scope: `particle-archive-buffer-cleanup-wave823`

Wave823 particle archive buffer cleanup saved Ghidra names, comments, tags, and signatures for two raw-commentless ParticleSet/CDXMemBuffer rows after serialized headless dry/apply/read-back with the `particle-archive-buffer-cleanup-wave823` and `wave823-readback-verified` tags. The pass corrected `0x004cd7a0 CWorldPhysicsManager__FindNodeByNameGE` to `0x004cd7a0 CParticleSet__FindByNameAndTrackLinkSlot`, corrected `0x004cdb90 CDXMemBuffer__dtor_base` to `0x004cdb90 CDXMemBuffer__dtor_base_Thunk`, made no function-boundary changes, and made no executable-byte changes.

Representative anchors:

| Address | Saved state | Evidence |
| --- | --- | --- |
| `0x004cd7a0` | `void * __thiscall CParticleSet__FindByNameAndTrackLinkSlot(void * this, char * set_name)` | `RET 0x4` proves one stack argument after the ECX receiver. Callers pass `&DAT_0082b400`; the body stores the current link slot in `DAT_0082b3f8`, walks nodes via `+0x38`, compares `set_name` against node name `+0x4` with `stricmp`, and returns null early when sorted comparison proves the name is absent. |
| `0x004cdb90` | `void __fastcall CDXMemBuffer__dtor_base_Thunk(void)` | Single-instruction jump thunk to `0x00547d90 CDXMemBuffer__dtor_base`; observed xref is `0x005d4230 Unwind@005d4230` in the ParticleSet.cpp cleanup continuation for the stack-local `CDXMemBuffer` at `EBP-0x140`. |

Read-back evidence:

- `ApplyParticleArchiveBufferCleanupWave823.java dry`: `updated=0 skipped=2 renamed=0 would_rename=2 signature_updated=2 comment_only_updated=0 missing=0 bad=0`
- `ApplyParticleArchiveBufferCleanupWave823.java apply`: saved both rows and reported `updated=2 skipped=0 renamed=2 would_rename=0 signature_updated=2 comment_only_updated=0 missing=0 bad=1` because the first script revision compared the `__thiscall` signature against a short expected-name token after Ghidra rendered the correct explicit `this` receiver. The saved post-apply metadata already contained `void * __thiscall CParticleSet__FindByNameAndTrackLinkSlot(void * this, char * set_name)`.
- `ApplyParticleArchiveBufferCleanupWave823.java final dry`: after correcting the read-back comparator, `updated=0 skipped=2 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`.
- Post exports: 2 metadata rows, 2 tag rows, 46 xref rows, 490 target instruction rows, 14 helper metadata rows, 2030 helper instruction rows, 8 caller decompile rows, 840 caller instruction rows, and 2 target decompile rows.
- Queue after Wave823: 6098 total functions, 5628 commented, 470 commentless, 0 exact-undefined signatures, 0 `param_N` signatures, comment-backed proxy `5628/6098 = 92.29%`, strict comment-plus-clean-signature proxy `5628/6098 = 92.29%`.
- Next raw commentless row: `0x004cf050 CMenuItem__Destructor`; commentless high-signal, signature, and name-confidence queues remain empty.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260524-183746_post_wave823_particle_archive_buffer_cleanup_verified`, 19 files, 171543431 bytes, `DiffCount=0`.

What this proves:

- The two target function rows exist in the saved Ghidra project.
- The saved names, signatures, comments, and tags match the Wave823 read-back artifacts.
- The observed behavior is static retail Ghidra evidence tied to decompile, instruction, xref, helper metadata, caller context, and backup verification artifacts.

What remains unproven:

- Exact particle-set node layout.
- Link-slot ownership beyond the observed static cursor/global evidence.
- Runtime particle/effect lookup behavior.
- Exact unwind parent/source-body identity.
- Runtime stack-local buffer lifetime.
- Runtime particle archive behavior.
- BEA patching behavior.
- Rebuild parity.
