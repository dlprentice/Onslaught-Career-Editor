# Ghidra Wave923 HUD/Radar/Pause Render Review (2026-05-27)

Status: read-only static review
Date: 2026-05-27
Branch: `main`
Tag: `hud-radar-pause-render-review-wave923`

## Scope

Wave923 reviewed six still-unreviewed Wave911 focused correction candidates from user-visible HUD, radar warning, pause input, particle sprite, and D3D device-format paths:

| Address | Saved name | Result |
| --- | --- | --- |
| `0x00487d10` | `CHud__RenderBattleline` | Reviewed; no mutation |
| `0x004d66b0` | `CRadarWarningReceiver__Update` | Reviewed; no mutation |
| `0x004d15d0` | `CPauseMenu__VFunc_03_HandleMenuControlInput` | Reviewed; no mutation |
| `0x004c14f0` | `CPDSimpleSprite__VFunc_10_004c14f0` | Reviewed; no mutation |
| `0x004c8040` | `CPDSimpleSprite__VFunc_23_004c8040` | Reviewed; no mutation |
| `0x0052a830` | `CD3DApplication__FindDepthStencilFormat` | Reviewed; no mutation |

Post-closure focused re-audit progress after this slice is `86/1408 = 6.11%` of the Wave911 focused correction-candidate queue. The export-contract function-quality closure remains `6113/6113 = 100.00%`.

## Evidence

Private artifacts:

```text
subagents/ghidra-static-reaudit/wave923-hud-radar-pause-render-review/metadata.tsv
subagents/ghidra-static-reaudit/wave923-hud-radar-pause-render-review/tags.tsv
subagents/ghidra-static-reaudit/wave923-hud-radar-pause-render-review/xrefs.tsv
subagents/ghidra-static-reaudit/wave923-hud-radar-pause-render-review/instructions.tsv
subagents/ghidra-static-reaudit/wave923-hud-radar-pause-render-review/decompile/
subagents/ghidra-static-reaudit/wave923-hud-radar-pause-render-review/wave923-hud-radar-pause-render-review.json
```

Read-back result:

```text
metadata: 6/6 OK
tags: 6/6 OK
xrefs: 6 rows
instructions: 1009 rows
decompile: 6/6 OK
```

## Review Result

The saved names, signatures, comments, and tags remain coherent with the fresh evidence. `CHud__RenderBattleline` is still anchored by `CDXEngine__PostRender`; `CRadarWarningReceiver__Update` is still reached by the event-4000 callback; the pause-menu control handler remains a three-argument vtable slot; the two `CPDSimpleSprite` rows remain descriptor vtable slots; and `CD3DApplication__FindDepthStencilFormat` remains the device-list depth/stencil selector called by `CD3DApplication__BuildDeviceList`.

No Ghidra mutation was performed.

## Backup

Read-only post-wave backup:

```text
[maintainer-local-ghidra-backup-root]\BEA_20260527-210516_post_wave923_hud_radar_pause_render_review_verified
files=19
bytes=173247367
DiffCount=0
```

## Truth Boundary

This review confirms static Ghidra coherence for the selected HUD/radar/pause/sprite/D3D support helpers. It does not prove runtime HUD rendering, radar warning behavior, pause-menu input behavior, particle sprite rendering, Direct3D device selection, concrete layouts, exact source-body identity, BEA patch behavior, or rebuild parity.

## Next

Continue Wave924 with another focused cluster from Wave911. Mutate only when fresh metadata, decompile, xref, instruction, and source/reference evidence justify a bounded correction.
