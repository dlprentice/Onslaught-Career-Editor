# Wave1141 CDXCompass/HUD Current-Risk Readiness Note

Status: complete static read-back evidence
Date: 2026-06-05
Scope: `wave1141-cdxcompass-hud-current-risk-review`

Wave1141 re-read thirteen Wave1108 current-risk rows in the CDXCompass/HUD render-state current-risk cluster with fresh Ghidra metadata, tag, xref, instruction, context, and decompile exports. It was a read-only review with no mutation: no rename, no signature edit, no comment/tag edit, no function-boundary change, no executable-byte change, no BEA launch, no installed-game mutation, and no runtime-file mutation.

Probe token anchor: Wave1141; wave1141-cdxcompass-hud-current-risk-review; `251/1179 = 21.29%`; 13 current-risk rows; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 928; current risk candidates: 6166; CDXCompass/HUD render-state current-risk cluster; fresh Ghidra export; read-only review; no mutation; `0 / 0 / 0`; `6411/6411 = 100.00%`; `G:\GhidraBackups\BEA_20260605-145724_post_wave1141_cdxcompass_hud_current_risk_review_verified`; `G:\GhidraBackups\BEA_20260605-142515_post_wave1140_motion_controller_current_risk_review_verified`.

| Address | Evidence |
| --- | --- |
| `0x0053bd60 CDXCompass__InitFields` | `CHud__Init` call xref `0x0048149a`; clears compass field-block resource slots and calls `CDXCompass__Reset`. |
| `0x0053be40 CDXCompass__Init` | `CDXCompass__InitMarkerArrays` call xref `0x00427106`; allocates byte sprite, ring textures, CVBuffers, and compass ring geometry. |
| `0x0053c1d0 CDXCompass__BuildRingGeometry` | `CDXCompass__Init` call xrefs `0x0053c0f3` and `0x0053c18a`; fills the ring vertex strip from texture dimensions and segment/UV parameters. |
| `0x00427110 CDXCompass__LoadTextures` | `CHud__LoadTextures` call xref `0x00481ad3`; loads ThreatFlash, DamageFlash, BarLine, and CompassObjectiveMarker texture references. |
| `0x00427190 CDXCompass__DestroyTextures` | `CHud__ShutDown` call xref `0x00481b1a`; releases and clears compass texture references. |
| `0x00427200 CDXCompass__Reset` | `CDXCompass__InitFields` call xref `0x0053bd63`; clears render/state flag `this+0x3c10`. |
| `0x004821b0 CDXCompass__ApplyRenderStateModulate` | `CDXCompass__Render` call xref `0x0042722c`; applies render-state pair `2/2`. |
| `0x004821e0 CDXCompass__ApplyRenderStateAdditive` | `CDXCompass__Render` call xref `0x00427911`; applies render-state pair `5/6`. |
| `0x00481400 CHud__ctor_base` | `CDXEngine__InitLandscapeTextureTables` call xref `0x00542743`; initializes HUD reader/component/compass state. |
| `0x00481450 CHud__Init` | `CGame__Init` call xref `0x0046c3d8`; allocates compass/BattleLine HUD subobjects. |
| `0x00481650 CHud__LoadTextures` | `CGame__RunLevel` call xref `0x0046e367`; resolves HUD textures and delegates compass/BattleLine texture loading. |
| `0x00481b00 CHud__ShutDown` | `CGame__Shutdown` call xref `0x0046c9ac`; tears down BattleLine, compass, HUD texture refs, and speaker slots. |
| `0x00482090 HudRenderState__ApplyOverlaySpriteState` | `CDXCompass__Render` call xref `0x00427222` plus HUD/message/battleline callers; applies shared overlay sprite state. |

Read-back evidence:

- Primary exports: 13 metadata rows, 13 tag rows, 28 xref rows, 1310 instruction rows, and 13 decompile rows.
- Context exports: 27 metadata rows, 27 tag rows, 45 xref rows, 8549 instruction rows, and 27 decompile rows.
- Queue refresh after the read-only review: `6411/6411 = 100.00%`, static debt `0 / 0 / 0`.
- Current-risk refresh: current risk candidates `6166`, current focused candidates `1178`, focused threshold `15`.
- Wave1108 current focused accounting moved to `251/1179 = 21.29%`; remaining active focused work: `928`.
- Verified backup: `G:\GhidraBackups\BEA_20260605-145724_post_wave1141_cdxcompass_hud_current_risk_review_verified`, 19 files, 175967111 bytes, `DiffCount=0`, `HashDiffCount=0`.
- Previous completed backup: `G:\GhidraBackups\BEA_20260605-142515_post_wave1140_motion_controller_current_risk_review_verified`.

What this proves:

- The thirteen target rows still have clean saved Ghidra names, signatures, comments, tags, xrefs, and decompile rows.
- The CDXCompass/HUD lifecycle, texture lifetime, render-state, ring-geometry, and overlay-state handoff remains coherently bounded in static Ghidra evidence.
- No Ghidra mutation was required for this wave.

What remains unproven:

- Runtime compass behavior.
- Runtime HUD behavior.
- Runtime rendering behavior or visible output.
- Exact concrete `CHud`, `CDXCompass`, BattleEngine, texture, CVBuffer, byte-sprite, and render-resource layouts.
- Exact source-body identity.
- BEA patching behavior, gameplay outcomes, visual QA, and rebuild parity.
