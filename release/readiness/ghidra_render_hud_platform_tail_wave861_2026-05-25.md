# Ghidra Render/HUD/Platform Tail Wave861 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-25
Scope: `render-hud-platform-tail-wave861`

Wave861 render/HUD/platform tail saved comments/tags for ten important connective infrastructure rows from `0x00523a70 CDXEngine__RenderMouseCursorSprite` through `0x005285e0 PCPlatform__UpdateAsyncMusicStreamVolume`. The pass corrected three signatures, made no renames, made no function-boundary changes, and made no executable-byte changes.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x00523a70 CDXEngine__RenderMouseCursorSprite` | Cursor/HUD sprite helper called by game interface, briefing log, message log, pause menu, and frontend cursor render paths; lazily resolves `mouse.tga`, falls back to `meshtex\default.tga`, and calls `CVBufTexture__DrawSpriteEx`. |
| `0x00523b30 CVBufTexture__DestroyGlobalHudHandle89BD98` | CLTShell shutdown helper for global cursor/HUD texture handle `DAT_0089bd98`; decrements texture refcount through `CTexture__DecrementRefCountFromNameField(texture+8)` and clears the global. |
| `0x00527990 CGame__DrawLocalCoopControllerPrompt` | Local co-op/controller prompt renderer reached from frontend, game render, and multiplayer-start render; uses localized text, controller-port comparisons, text wrapping/extent, sprite background, and font draw helpers. |
| `0x00527de0 CWaterRenderSystem__ResetAndMarkSourceFlag` | Corrected to `void __fastcall CWaterRenderSystem__ResetAndMarkSourceFlag(void * validation_record)`; ECX-only render-validation helper clears `DAT_00854dd8` and derives `DAT_00854dd9` from `validation_record+0x10`. |
| `0x00527f50 PCPlatform__AsyncMusicStreamWorkerMain` | CreateThread target installed by async music init; waits on four event handles, validates 44100 Hz stereo Ogg stream properties, fills DirectSound buffer ranges, handles underrun zero-fill, and exits on shutdown wait case 3. |
| `0x005282b0 PCPlatform__InitAsyncMusicStream` | Called before `CMusic__LoadPlaylistFromDir(this,"data\music")`; creates DirectSound buffer/event/thread state, allocates a `0x22f0` COggFileRead-like object, clears path buffer `DAT_0089bed4`, and resets counters. |
| `0x00528460 PCPlatform__ShutdownAsyncMusicStream` | Signals shutdown, polls worker exit, stops/releases the DirectSound buffer object, closes event handles, destroys the Ogg reader object when present, and clears stream path/counter state. |
| `0x00528540 PCPlatform__KickAsyncMusicStreamRead` | Corrected to `void __cdecl PCPlatform__KickAsyncMusicStreamRead(char * track_path)`; compares/copies requested track path into `DAT_0089bed4`, clears `DAT_0089beac`, and signals the worker wake event. |
| `0x005285b0 PCPlatform__ResetAsyncMusicStream` | Invokes the active DirectSound buffer reset slot and resets stream event handles; one event-handle operand is currently symbol-collided with the function name and is kept bounded. |
| `0x005285e0 PCPlatform__UpdateAsyncMusicStreamVolume` | Corrected to `void __cdecl PCPlatform__UpdateAsyncMusicStreamVolume(float normalized_volume)`; clamps volume, applies the observed power curve, converts through the `10000.0` attenuation constant, and forwards to DirectSound vtable slot `0x3c`. |

Read-back evidence:

- `ApplyRenderHudPlatformTailWave861.java dry`: `updated=10 skipped=0 renamed=0 would_rename=0 signature_updated=3 comment_only_updated=7 missing=0 bad=0`
- First `apply` saved the intended state and `REPORT: Save succeeded`, but the checker reported `bad=3` because it expected `__fastcall`/`__cdecl` inside `FunctionSignature.getPrototypeString()` even though Ghidra reports those calling conventions separately. This log is preserved as `apply-prototype-string-mismatch.log`.
- Corrected `ApplyRenderHudPlatformTailWave861.java apply`: `updated=0 skipped=10 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`, with ten `READBACK_OK` rows.
- Corrected `ApplyRenderHudPlatformTailWave861.java final dry`: `updated=0 skipped=10 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`.
- Post exports: 10 metadata rows, 10 tag rows, 23 xref rows, 1010 instruction rows, 10 decompile rows, 18 context metadata rows, 18 context decompile rows, and corrected string dumps for `mouse.tga`, `meshtex\default.tga`, `PCPlatform.cpp`, and `data\music`.
- Queue after Wave861: 6105 total, 5802 commented, 303 commentless, 0 exact-undefined signatures, 0 `param_N`, comment-backed proxy `5802/6105 = 95.04%`, strict clean-signature proxy `5802/6105 = 95.04%`.
- Next raw commentless row: `0x0052a830 CD3DApplication__FindDepthStencilFormat`.
- Commentless high-signal, signature, and name-confidence queues remain empty.
- Verified backup: `G:\GhidraBackups\BEA_20260525-141443_post_wave861_render_hud_platform_tail_verified`, 19 files, 172264327 bytes, `DiffCount=0`.

What this proves:

- The ten target function rows exist in the saved Ghidra project.
- The saved function comments and tags include `render-hud-platform-tail-wave861` and `wave861-readback-verified`.
- The three signature corrections are present in saved Ghidra read-back.
- The observed bodies are static retail Ghidra evidence tied to xrefs, decompile/instruction exports, context helpers, and string dumps.

What remains unproven:

- Exact cursor/HUD/controller-prompt/platform audio object layouts.
- Exact source-body identity for the affected helpers.
- Runtime cursor/HUD/controller prompt behavior.
- Runtime water/D3D validation behavior.
- Runtime async music/audio playback behavior.
- BEA patching behavior.
- Rebuild parity.
