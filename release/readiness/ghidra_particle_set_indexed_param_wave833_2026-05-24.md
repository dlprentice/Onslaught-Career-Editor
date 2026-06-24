# Ghidra Particle SetIndexedParam Wave833 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-24
Scope: `particle-set-indexed-param-wave833`

Wave833 particle SetIndexedParam saved a bounded signature/comment/tag correction for `0x004f5b70 CParticleDescriptor__SetIndexedParam`, an important connective particle descriptor indexed-field setter used by the TokenArchive/particle descriptor load path. The pass corrected the stale phantom `unused_flags` parameter and saved the signature as:

`void __thiscall CParticleDescriptor__SetIndexedParam(void * this, int field_index, int field_value)`

The pass made no rename, no function-boundary change, and no executable-byte change.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x004f5b70 CParticleDescriptor__SetIndexedParam` | Body loads `field_index` from `ESP+0x4`, loads `field_value` from `ESP+0x8`, stores `field_value` at `this+0x0c+(field_index*4)`, and returns with `RET 0x8`. |
| `0x004c57d4` / `0x004c57e9` | `CParticleDescriptor__Load` call sites push exactly two stack arguments and load `ECX` with the descriptor/archive receiver before calling the helper. |
| `0x004f5b80 CTokenArchive__RegisterReferenceFixup` | Adjacent helper keeps the same indexed-slot storage shape after recording a reference fixup pointer. |

Read-back evidence:

- `ApplyParticleSetIndexedParamWave833.java dry`: `updated=0 skipped=1 renamed=0 would_rename=0 signature_updated=1 comment_only_updated=0 missing=0 bad=0`
- `ApplyParticleSetIndexedParamWave833.java apply`: `updated=1 skipped=0 renamed=0 would_rename=0 signature_updated=1 comment_only_updated=0 missing=0 bad=0`
- `ApplyParticleSetIndexedParamWave833.java final dry`: `updated=0 skipped=1 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`
- Post exports: 1 metadata row, 1 tag row, 15 xref rows, 49 target instruction rows, 1 target decompile row, 10 context metadata rows, 10 context decompile rows, and 315 xref-site instruction rows.
- Queue after Wave833: 6098 total, 5655 commented, 443 commentless, 0 exact-undefined signatures, 0 `param_N`, comment-backed proxy `5655/6098 = 92.74%`, strict clean-signature proxy `5655/6098 = 92.74%`.
- Commentless high-signal, signature, and name-confidence queues remain empty.
- Next raw commentless row: `0x004f7d30 FromWCHAR`.
- Verified backup: `G:\GhidraBackups\BEA_20260524-233838_post_wave833_particle_set_indexed_param_verified`, 19 files, 171772807 bytes, `DiffCount=0`.

What this proves:

- The target function row exists in the saved Ghidra project.
- The saved signature has the observed two stack arguments plus explicit `this` receiver and no stale `unused_flags` parameter.
- The saved comment and tags include `particle-set-indexed-param-wave833` and `wave833-readback-verified`.
- The observed call sites and body support an indexed descriptor slot write in static retail Ghidra evidence.

What remains unproven:

- Exact source body identity.
- Concrete descriptor subclass or field enum identity.
- Runtime particle parsing behavior.
- BEA patching behavior.
- Rebuild parity.
