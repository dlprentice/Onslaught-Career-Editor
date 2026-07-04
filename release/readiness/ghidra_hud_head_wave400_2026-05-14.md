# Ghidra HUD Head Correction Tranche - 2026-05-14

Status: public-safe static evidence note

This note records a serialized static Ghidra correction wave for twelve HUD-head and early HUD render-state targets. It documents saved Ghidra metadata only. It does not include private decompile excerpts, private screenshots, copied executables, copied saves, raw runtime evidence, or private asset payloads.

## What Changed

| Address | Saved state | Public-safe evidence summary |
| --- | --- | --- |
| `0x00481400` | `void * __thiscall CHud__ctor_base(void * this)` | Corrected the older `CDXEngine__InitLandscapeTextureReaderState` owner label to bounded `CHud` constructor/base-init wording. Static read-back shows active-reader cell construction at `+0x9c`, component/compass slot clearing, and six HUD state flag seeds. |
| `0x00481450` | `void __thiscall CHud__Init(void * this)` | Corrected the saved undefined/no-argument form to an ECX-this `CHud` init signature. Static read-back shows allocation of compass/BattleLine HUD subobjects, initialized-flag setup, and text string id loads from the `CGame__Init` HUD-singleton caller path. |
| `0x004815c0` | `void __thiscall CHud__Reset(void * this)` | Corrected the generic fastcall-style signature to ECX-this `CHud` reset shape. Static read-back shows six HUD flags, screen marker arrays, and objective/indicator state resets from the restart-loop caller path. |
| `0x00481650` | `void __thiscall CHud__LoadTextures(void * this)` | Corrected the saved undefined/no-argument form to ECX-this texture-load shape. Static read-back shows crosshair, radar, weapon, objective, and speaker HUD texture resolution plus compass and battleline texture-load delegation. |
| `0x00481af0` | `int __thiscall CHud__PostLoadProcess(void * this)` | Corrected the saved void/no-argument form to ECX-this with the return value observed by `CGame__PostLoadProcess`. Static read-back shows a tail jump through the BattleLine object at `+0x30` to `CDXBattleLine__Setup`. |
| `0x00481b00` | `void __thiscall CHud__ShutDown(void * this)` | Corrected the generic fastcall-style signature to ECX-this shutdown shape. Static read-back shows BattleLine/compass cleanup, compass/BattleLine allocation frees, HUD texture reference releases, and speaker-array cleanup. |
| `0x00481f40` | `void __thiscall CHud__SetHudComponent(void * this, char * component_name, byte slot_flag)` | Hardened the cutscene caller-driven HUD component swap signature. Static read-back shows pending/current slot cleanup at `+0x200` / `+0x1fc`, `CHudComponent` allocation from `component_name`, and slot selection by `slot_flag`. |
| `0x00482050` | `void __thiscall CHud__PromotePendingHudComponent(void * this)` | Corrected the older `CDXEngine__SwapPendingHudRenderComponent` owner label to bounded `CHud` component-promotion wording. Static read-back shows `CDXEngine__PostRender` passing the HUD singleton, vfunc cleanup of the current component, and pending-to-active slot promotion. |
| `0x00482090` | `void __cdecl HudRenderState__ApplyOverlaySpriteState(void)` | Corrected the overly narrow `CExplosionInitThing__SetupOverlayMarkerRenderState` owner label to shared HUD/message/compass/battleline overlay render-state setup. Static read-back shows blend, texture-stage, mip, z, fog, and pending-render-state setup, with xrefs spanning HUD overlay, message log, battleline, and compass render paths. |
| `0x004821b0` | `void __cdecl CDXCompass__ApplyRenderStateModulate(void)` | Hardened the plain cdecl compass render-state helper signature/comment. Static read-back shows render states `0x13` / `0x14` set to `2` / `2` before applying pending render state. |
| `0x004821e0` | `void __cdecl CDXCompass__ApplyRenderStateAdditive(void)` | Hardened the plain cdecl compass render-state helper signature/comment. Static read-back shows render states `0x13` / `0x14` set to `5` / `6` before applying pending render state. |
| `0x00482210` | `void __thiscall CHud__RenderSegmentedMeterBar(void * this, float x, float y, float width, float scale, float fill_fraction)` | Corrected the older `CDXEngine__RenderSegmentedMeterBar` owner label to bounded `CHud` meter rendering. Static read-back shows segmented objective/message meter drawing using CHud texture refs `+0x154`, `+0x158`, `+0x160`, and `+0x164`; callers ignore the old return residue. |

## Validation

- `ApplyHudHeadWave400.java` dry run: `updated=0 skipped=12 created=0 would_create=0 renamed=0 would_rename=4 missing=0 bad=0`.
- `ApplyHudHeadWave400.java` apply run: `updated=12 skipped=0 created=0 would_create=0 renamed=4 would_rename=0 missing=0 bad=0`, with `REPORT: Save succeeded`.
- Metadata/decompile/xref/tag/instruction read-back is stored under ignored `subagents/`.
- Focused probe: `tools/ghidra_hud_head_wave400_probe.py --check`.
- Self-test: `tools/ghidra_hud_head_wave400_probe_test.py`.
- Read-back verified `12` metadata rows, `12` decompile exports, `30` xref rows, `12` tag rows, and `1452` instruction rows.
- Refreshed static queue: `6028` functions, `1541` commented functions, `4487` commentless functions, `1910` undefined signatures, and `1860` `param_N` signatures.
- Current confirmation proxies remain telemetry only: comment-backed `1541/6028 = 25.56%`, strict clean-signature `1476/6028 = 24.49%`.
- Live Ghidra backup verified at `[maintainer-local-ghidra-backup-root]\BEA_20260514_034222_post_wave400_hud_head_verified` with `19` files, `154798983` bytes, and `HashDiffCount=0`.

## Claim Boundary

This tranche improves saved static Ghidra names, comments, tags, and signatures for the HUD-head and early HUD render-state cluster. It does not prove runtime HUD behavior, does not prove concrete CHud layout, does not recover concrete structure types/locals, does not launch or patch `BEA.exe`, and does not prove rebuild parity.
