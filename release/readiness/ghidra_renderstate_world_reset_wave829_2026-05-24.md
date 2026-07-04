# Ghidra Render-State World Reset Wave829 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-24
Scope: `renderstate-world-reset-wave829`

Wave829 render-state world reset corrected the raw commentless head at `0x004eb1e0` from the stale `CGame__ResetRenderStateForWorldRender` label to `D3DStateCache__UseDefaultRenderState`. The same pass saved bounded comments/tags for eight adjacent render-state/cache helpers. It made no function-boundary changes and no executable-byte changes.

Static evidence:

| Address | Evidence |
| --- | --- |
| `0x004eb1e0 D3DStateCache__UseDefaultRenderState` | Source-aligns to `STATE.UseDefault()` callsites in `CDXEngine::PreRender`, `CDXEngine::Render`, `CDXFrontEnd::RenderStart`, loading-screen render, and debug render. The retail body resets sentinel tables, forces baseline raw render states, clamps fog/range constants, resets projection depth bias / shader path state, and initializes texture-stage defaults for stages 0-3. |
| `0x00513600 D3DStateCache__ResetSentinelTable` | Writes `INVALID_STATE` (`0xfedcba98`) into render-state and texture-stage cache tables and resets shader/auxiliary sentinels. |
| `0x00513a50 CEngine__SetRenderStateCached` | Updates compact render-state cache `0x008554d0[state_id]` and dispatches through the engine device pointer only when the cached value changes. |
| `0x00513c20 RenderState_SetRaw` | Forces cache and device render state writes, with the same cull-mode 2<->3 winding-flip adjustment as the cached helper. |
| `0x00513d90` / `0x00513dd0` | Cached/raw alpha-reference helpers for render state `0x18`, including the observed optional `alpha_ref | alpha_ref<<8` packing. |
| `0x00514030 RenderState_Set_23_8C_Compat` | Enables/disables paired render states `0x23` and `0x8c` depending on the observed capability/global bit `0x100`. |
| `0x00550d50 CDXEngine__ApplyPendingRenderState` | Flushes dirty CDXEngine render state, transforms, lights, fog/color states, and vertex-shader object/render-info shader state. |
| `0x00558fb0 CVBufTexture__SetupRenderStates` | Configures texture transform and stage 0/1 state for CVBufTexture mode field `this+0x88`, including alpha-ref mode 4 and overlay handling. |

Read-back evidence:

- `ApplyRenderStateWorldResetWave829.java dry`: `updated=0 skipped=9 renamed=0 would_rename=1 signature_updated=0 comment_only_updated=9 missing=0 bad=0`
- `ApplyRenderStateWorldResetWave829.java apply`: nine `READBACK_OK` rows, then `updated=9 skipped=0 renamed=1 would_rename=0 signature_updated=0 comment_only_updated=9 missing=0 bad=0`.
- The first apply log also records a redundant explicit-save `Unable to lock due to active transaction` script error after read-back; the script was corrected to rely on the headless save path, and final dry/post exports verify the saved state.
- `ApplyRenderStateWorldResetWave829.java final dry`: `updated=0 skipped=9 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`
- Post exports: 9 metadata rows, 9 tag rows, 237 xref rows, 333 instruction rows, 9 decompile rows, and 5 caller decompile rows.
- Queue after Wave829: `6098` total functions, `5650` commented, `448` commentless, `0` exact-undefined signatures, `0` `param_N` signatures, comment-backed proxy `5650/6098 = 92.65%`, strict clean-signature proxy `5650/6098 = 92.65%`.
- Next raw commentless row: `0x004ef100 CUnit__RunTransitionStepThreeTimes`; commentless high-signal, signature, and name-confidence queues remain empty.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260524-213733_post_wave829_renderstate_world_reset_verified`, 19 files, 171641735 bytes, `DiffCount=0`.

What this proves:

- The saved Ghidra row at `0x004eb1e0` now has the corrected `D3DStateCache__UseDefaultRenderState` name, bounded comment, and `renderstate-world-reset-wave829` / `wave829-readback-verified` tags.
- The eight adjacent render-state/cache helpers now have bounded comments/tags tied to static retail decompile/instruction evidence.
- The observed callers now decompile against `D3DStateCache__UseDefaultRenderState`.
- The queue snapshot has nine fewer raw commentless functions than Wave828.

What remains unproven:

- Exact state-table, CDXEngine, CEngine, CVBufTexture, shader-object, and device field layouts.
- Exact Direct3D enum names for every numeric state.
- Runtime render behavior.
- BEA patching behavior.
- Rebuild parity.
