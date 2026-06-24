# Ghidra Shader Capability Init Wave840 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-25
Scope: `shader-capability-init-wave840`

Wave840 Shader Capability Init saved a bounded signature/comment/tag hardening for `0x005016b0 InitShaderCapabilityFlagsAndCVar` after serialized headless dry/apply/read-back. The pass made no rename, no function-boundary change, and no executable-byte change.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x005016b0 InitShaderCapabilityFlagsAndCVar` | Saved signature `void __cdecl InitShaderCapabilityFlagsAndCVar(void)`; no explicit stack arguments, no ECX receiver, and a plain `RET` at `0x00501720`. |
| `0x005155b1 PCPlatform__Init` | Sole caller xref; follows the `"Initting shaders"` log in the PC platform startup path. |
| `DAT_00854e6c` | Updated from a Direct3D device-capability stack field compared against `0xfffe0101`. |
| `cg_forcevertexshaders` | Registered through `CConsole__RegisterVariable` with description string `s_Should_vertex_shaders_be_used_wh_0063ce00` and backing byte `DAT_00854e6d` when `DAT_0063c108` enables vertex shaders. |

Read-back evidence:

- `ApplyShaderCapabilityInitWave840.java dry`: `updated=0 skipped=1 renamed=0 would_rename=0 signature_updated=1 comment_only_updated=0 missing=0 bad=0`
- `ApplyShaderCapabilityInitWave840.java apply`: `updated=1 skipped=0 renamed=0 would_rename=0 signature_updated=1 comment_only_updated=0 missing=0 bad=0`
- `ApplyShaderCapabilityInitWave840.java final dry`: `updated=0 skipped=1 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`
- Post exports: 1 metadata row, 1 tag row, 1 xref row, 205 instruction-window rows, 501 target-deep instruction rows, 97 xref-site instruction rows, 1 decompile row, 6 context metadata rows, 6 context tag rows, and 6 context decompile rows.
- Queue after Wave840: 6098 total functions, 5664 commented, 434 commentless, 0 exact-undefined signatures, 0 `param_N` signatures, comment-backed proxy `5664/6098 = 92.89%`, strict clean-signature proxy `5664/6098 = 92.89%`.
- Next raw commentless row: `0x005019c0 VFuncSlot_09_005019c0`.
- The commentless high-signal, signature, and name-confidence queues remain empty.
- Verified backup: `G:\GhidraBackups\BEA_20260525-030308_post_wave840_shader_capability_init_verified`, 19 files, 171838343 bytes, `DiffCount=0`.

What this proves:

- The saved Ghidra function row exists with the `void __cdecl InitShaderCapabilityFlagsAndCVar(void)` signature.
- The saved comment and tags include `shader-capability-init-wave840` and `wave840-readback-verified`.
- The observed body is important PC/Direct3D shader startup infrastructure tying `PCPlatform__Init`, Direct3D capability probing, `DAT_00854e6c`, `DAT_0063c108`, and the `cg_forcevertexshaders` CVar registration together.

What remains unproven:

- Exact Direct3D caps field identity.
- Exact console/CVar schema.
- Runtime hardware or driver behavior.
- Runtime shader enablement behavior.
- BEA patching behavior.
- Rebuild parity.
