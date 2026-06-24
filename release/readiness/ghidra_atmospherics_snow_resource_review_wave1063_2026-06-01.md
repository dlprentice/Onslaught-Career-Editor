# Ghidra Atmospherics Snow Resource Review Wave1063 Readiness Note

Status: complete static read-back evidence
Date: 2026-06-01
Scope: `atmospherics-snow-resource-review-wave1063`

Wave1063 re-read the older Atmospherics/CAtmosphericsProfile/DXSnow snow-resource surface after the post-100 re-audit queue closure. Fresh exports showed the six core `Atmospherics__*` lifecycle/list-dispatch rows still had correct saved names, signatures, and comments, but empty function tags. The wave saved tag normalization for those six rows only.

The pass made no rename, no signature change, no comment change, no function-boundary change, no executable-byte change, and did not launch BEA or mutate runtime/game files.

Tag-normalized rows:

| Address | Static evidence |
| --- | --- |
| `0x00404a00 Atmospherics__Init` | Global init loads snow resources, allocates atmospheric profile/cloud objects, and registers `ListAtmospherics` plus `atm_*` variables. |
| `0x00404b90 Atmospherics__ResetAndUpdate` | Clears prevailing-wind globals and dispatches atmospheric list vtable slot `+0x0c`. |
| `0x00404bd0 Atmospherics__UpdateAll` | Walks `DAT_006601a8` and dispatches each atmospheric list entry vtable slot `+0x08`. |
| `0x00404bf0 Atmospherics__RenderAll` | Walks `DAT_006601a8` and dispatches each atmospheric list entry vtable slot `+0x04`. |
| `0x00404c10 Atmospherics__Shutdown` | Releases the cached snow texture handle, dispatches vtable slot `+0x10`, unlinks entries, and frees objects. |
| `0x00404c90 Atmospherics__NotifyAll` | Walks `DAT_006601a8` and dispatches vtable slot `+0x14` with `eventCode`. |

Context anchors:

- `0x00554e80 DXSnow__StaticInitPrimaryTransformGlobals`
- `0x00554f50 DXSnow__StaticInitDisableSnowConfig`
- `0x00554f70 DXSnow__StaticDestroyDisableSnowConfig`
- `0x00554f80 CAtmosphericsProfile__ctor`
- `0x00555010 CAtmosphericsProfile__VFunc00_GetNameString`
- `0x00555020 CAtmosphericsProfile__ResetAndInitSnowResources`
- `0x00555410 CAtmosphericsProfile__ReleaseResources`
- `0x00555460 CAtmosphericsProfile__RenderOverlay`
- `0x00555600 CAtmosphericsProfile__VFunc08_UpdateSnowAndRenderOverlay`
- `0x00555af0 DXSnow__StaticZeroOverlayVectorGlobals`
- `0x00555b10 DXSnow__StaticInitOverlayTransformGlobals`

Read-back evidence:

- Pre primary exports: `6` metadata rows, `6` tag rows, `6` xref rows, `802` function-body instruction rows, and `6` decompile rows.
- Pre context exports: `11` metadata rows, `11` tag rows, `12` xref rows, `272` function-body instruction rows, and `11` decompile rows.
- `ApplyAtmosphericsSnowResourceReviewWave1063.java dry`: `updated=0 skipped=0 tags_added=77 missing=0 bad=0`.
- `ApplyAtmosphericsSnowResourceReviewWave1063.java apply`: `updated=6 skipped=0 tags_added=77 missing=0 bad=0`, with `REPORT: Save succeeded`.
- `ApplyAtmosphericsSnowResourceReviewWave1063.java final dry`: `updated=0 skipped=6 tags_added=0 missing=0 bad=0`.
- Post exports: `17` metadata rows, `17` tag rows, `18` xref rows, `1074` function-body instruction rows, and `17` decompile rows.
- Queue closure remains `6246/6246 = 100.00%`.
- Wave911 focused progress remains `812/1408 = 57.67%` because the normalized rows are outside the materialized focused TSV.
- Expanded static surface progress advances to `1187/1548 = 76.68%`.
- Wave911 top-500 coverage remains `500/500 = 100.00%`.
- Verified backup: `G:\GhidraBackups\BEA_20260601-222739_post_wave1063_atmospherics_snow_resource_review_verified`, `19` files, `174721927` bytes, `DiffCount=0`, `HashDiffCount=0`.

What this proves:

- The seventeen post target rows exist in the saved Ghidra project with expected names and signatures.
- The six `Atmospherics__*` lifecycle/list-dispatch rows now carry Wave1063 static re-audit tags.
- The current Atmospherics snow-resource surface is current against fresh metadata, tags, xrefs, body instructions, and decompile-index evidence.

What remains unproven:

- Runtime weather, snow, render, console/CVar, or list-dispatch behavior.
- Exact `CAtmospheric`, `CAtmosphericsProfile`, `DXSnow`, `CTexture`, or `CVBufTexture` layouts.
- Exact source-body identity.
- BEA patching behavior.
- Gameplay outcomes.
- Rebuild parity.

Next candidate note: continue with the next focused static re-audit cluster; prefer read-only review first and mutate only when fresh evidence proves a correction or normalization need.

Probe token anchor: Wave1063; atmospherics-snow-resource-review-wave1063; 0x00404a00 Atmospherics__Init; 0x00404b90 Atmospherics__ResetAndUpdate; 0x00404bd0 Atmospherics__UpdateAll; 0x00404bf0 Atmospherics__RenderAll; 0x00404c10 Atmospherics__Shutdown; 0x00404c90 Atmospherics__NotifyAll; 0x00555020 CAtmosphericsProfile__ResetAndInitSnowResources; 812/1408 = 57.67%; 1187/1548 = 76.68%; 500/500 = 100.00%; 6246/6246 = 100.00%; G:\GhidraBackups\BEA_20260601-222739_post_wave1063_atmospherics_snow_resource_review_verified; tag normalization.
