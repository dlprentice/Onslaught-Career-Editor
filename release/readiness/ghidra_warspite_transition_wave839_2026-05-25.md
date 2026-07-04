# Ghidra Warspite Transition Wave839 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-25
Scope: `warspite-transition-wave839`

Wave839 Warspite Transition saved a bounded comment/tag hardening for `0x004fde70 CWarspite__TransitionToUndeploying` after serialized headless dry/apply/read-back. The pass made no rename, no signature change, no function-boundary change, and no executable-byte change.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x004fde70 CWarspite__TransitionToUndeploying` | Existing clean signature `void __thiscall CWarspite__TransitionToUndeploying(void * this)`; body checks whether `this+0x244 equals 4`, writes state 5 to `this+0x244`, asks the owner/unit pointer at `this+0x30` through vfunc `+0x24` for `s_undeploying_006239d8`, resolves the animation index through `CMesh__FindAnimationIndexByName`, then dispatches receiver vfunc `+0xf0` with that index. |
| `0x004ff2ae CWarspite__Update` | Named caller xref from the Warspite update body. |
| Raw xrefs | Additional raw controller/AI callsites at `0x00416870`, `0x0044655f`, `0x00446671`, `0x0044671a`, and `0x00534f99`. |

Read-back evidence:

- `ApplyWarspiteTransitionWave839.java dry`: `updated=0 skipped=1 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=1 missing=0 bad=0`
- `ApplyWarspiteTransitionWave839.java apply`: `updated=1 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=1 missing=0 bad=0`
- `ApplyWarspiteTransitionWave839.java final dry`: `updated=0 skipped=1 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`
- Post exports: 1 metadata row, 1 tag row, 6 xref rows, 121 instruction-window rows, 221 target-deep instruction rows, 438 xref-site instruction rows, 1 decompile row, 10 context metadata rows, and 10 context decompile rows.
- Queue after Wave839: 6098 total functions, 5663 commented, 435 commentless, 0 exact-undefined signatures, 0 `param_N` signatures, comment-backed proxy `5663/6098 = 92.87%`, strict clean-signature proxy `5663/6098 = 92.87%`.
- Next raw commentless row: `0x005016b0 InitShaderCapabilityFlagsAndCVar`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260525-023901_post_wave839_warspite_transition_verified`, 19 files, 171838343 bytes, `DiffCount=0`.

What this proves:

- The saved Ghidra function row exists with the existing clean signature.
- The saved comment and tags include `warspite-transition-wave839` and `wave839-readback-verified`.
- The observed body is an important Warspite state/animation transition helper, with static evidence for the state gate, state write, undeploying animation lookup, and vfunc dispatch path.

What remains unproven:

- Exact Warspite state enum names.
- Concrete owner/unit animation-resource type.
- Runtime AI/animation behavior.
- BEA patching behavior.
- Rebuild parity.
