# Wave1158 HUD Render Component Current-Risk Review

Status: complete static read-only evidence
Date: 2026-06-06
Tag: `wave1158-hud-render-component-current-risk-review`

Wave1158 accounts for `20 HUD render/component current-risk rows` from the active `wave1108-current-risk-rank` denominator. It uses fresh read-only Ghidra export evidence and makes no mutation.

Probe token anchor: Wave1158; wave1158-hud-render-component-current-risk-review; 485/1179 = 41.14%; 20 HUD render/component current-risk rows; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 694; current risk candidates: 6166; fresh Ghidra export; read-only review; no mutation; Codex read-only consults used; 0 / 0 / 0; 6411/6411 = 100.00%; 24 xref rows; 7335 instruction rows; CHud__RenderOverlayForViewpoint; CHud__RenderBattleline; CHud__RenderActiveHudComponentPass; CHud__RenderTacticalRadarContacts; CHud__RenderObjectiveStatusPanel; CHud__SetHudComponent; [maintainer-local-ghidra-backup-root]\BEA_20260606-002152_post_wave1158_hud_render_component_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction.

## Evidence

Fresh exports under `subagents/ghidra-static-reaudit/wave1158-hud-render-component-current-risk-review/`:

| Artifact | Rows |
| --- | ---: |
| `pre-metadata.tsv` | 20 |
| `pre-tags.tsv` | 20 |
| `pre-xrefs.tsv` | 24 |
| `pre-instructions.tsv` | 7335 |
| `pre-decompile/index.tsv` | 20 |

All Ghidra export logs report zero missing/failed targets and no `LockException`.

The xref evidence keeps the HUD graph bounded:

- `CGame__Init`, `CGame__InitRestartLoop`, `CGame__RunLevel`, `CGame__PostLoadProcess`, and `CGame__Shutdown` call the lifecycle rows.
- `CCutscene__Start`, `CCutscene__Stop`, and `CCutscene__Update` call `CHud__SetHudComponent`.
- `CDXEngine__PostRender` calls `CHud__PromotePendingHudComponent`, `CHud__RenderBattleline`, and `CHud__RenderActiveHudComponentPass`.
- `CHud__RenderOverlay` calls `CHud__RenderOverlayForViewpoint`.
- `CHud__RenderOverlayForViewpoint` calls the target-indicator, controller-status, target-marker, tactical-radar, objective, slot-fill, and world-target helper rows.

Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260606-002152_post_wave1158_hud_render_component_current_risk_review_verified`; `19` files, `175967111` bytes, `DiffCount=0`, `HashDiffCount=0`.

## Accounting

| Track | Current |
| --- | ---: |
| Static Ghidra function-quality closure | `6411/6411 = 100.00%` |
| Commentless / exact-undefined / `param_N` debt | `0 / 0 / 0` |
| Expanded post-100 static surface | `1560/1560 = 100.00%` |
| Wave911 focused historical residual | `596` rows, historical-retired/non-reconstructable, `300` materialized focused rows |
| Wave911 top-500 risk-ranked subset | `500/500 = 100.00%` |
| Wave1108 current focused accounting | `485/1179 = 41.14%` |
| Current risk candidates | `6166` |
| Current focused candidates | `1178` |
| Live regenerated current focused candidates | `1178` |
| Remaining active focused work | `694` |

This is the active current-risk denominator, not Wave911 reconstruction.

## Boundary

This review proves static retail Ghidra metadata/decompile/xref/instruction evidence for the selected HUD rows. It does not prove runtime HUD behavior, visible render output, exact concrete layouts, exact source-body identity, BEA patching behavior, visual QA, or rebuild parity.
