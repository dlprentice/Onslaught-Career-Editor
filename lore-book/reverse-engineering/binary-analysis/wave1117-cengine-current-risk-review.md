# Wave1117 CEngine Current-Risk Review

Status: validated static read-only evidence; historical artifact committed
Date: 2026-06-05
Tag: `wave1117-cengine-current-risk-review`

Wave1117 accounts for `10 rows` from the Wave1108 current focused denominator as the score-26 CEngine core head, moving current focused accounting to `87/1179 = 7.38%` of current focused candidates: 1179. The wave used a fresh read-only Ghidra export and no mutation.

Reviewed anchors:

| Address | Static read-back evidence |
| --- | --- |
| `0x00449820 CEngine__ctor` | Constructor seeds near/far clip fields, clears owned pointers, installs the CEngine vtable, and sets render-landscape state. |
| `0x00449890 CEngine__Shutdown` | CDXEngine shutdown xref; releases screen effects, shadow/tree systems, gamut, landscape/camera/water/map texture/HUD resources, and VB/IB pools. |
| `0x004499d0 CEngine__Init` | CDXEngine init xref; registers `cg_renderlandscape` / `cg_drawpolybuckets`, allocates map texture, water, landscape, HUD, light, screen-effect, shadow, and tree resources, and returns success/failure. |
| `0x0044a0d0 CEngine__SelectViewpoint` | CDXEngine render and HUD overlay xrefs; writes current viewpoint at `+0x4ac`, copies viewport state, calls `D3DDevice__SetViewport`, and returns with `RET 0x4`. |
| `0x0044a130 CEngine__InitDamageSystem` | `CGame__RestartLoopRunLevel` xref; resets landscape damage state and applies tree-shadow damage stamps. |
| `0x0044a1f0 CEngine__LoadMixers` | `CHeightField__DeserializeMapAndInitResources` xref; calls `CMapTex__LoadMixerTextureSet` from the engine `+0x49c` map-texture array and returns with `RET 0x4`. |
| `0x0044a2a0 CEngine__SetKempyCube` | Height-field deserialize xref; loads `this+0x498`, pushes the stack `number`, calls the KempyCube resource target, and returns with `RET 0x4`. |
| `0x0044a2c0 CEngine__SetWater` | Height-field deserialize xref; instruction read-back confirms `MOV EAX,[ESP+0x4]`, `PUSH EAX`, call to `CWaterRenderSystem__ReloadTextures`, and `RET 0x4`. |
| `0x0044a6e0 CEngine__Deserialize` | Resource-accumulator xref; reads `ENGN` / map-texture data via `CChunkReader`, deserializes the `+0x49c` map texture array, and dispatches MAP deserialize/init context. |
| `0x0044a830 VFuncSlot_03_0044a830` | Preserved as the Wave365/Wave488 owner-deferred shared slot helper; copies `source_vector3` into `this+0x08..0x10` and is called by `CRadarWarningReceiver__Init`. |

Fresh export evidence:

- Metadata: `10` rows, `targets=10 found=10 missing=0`.
- Tags: `10` rows, `missing=0`.
- Xrefs: `17` rows.
- Instructions: `1370` rows, `targets=10 missing=0`.
- Decompile: `10` rows, `targets=10 dumped=10 missing=0 failed=0`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260605-014214_post_wave1117_cengine_current_risk_review_verified`, `19` files, `175541127` bytes, `DiffCount=0`.
- Previous latest completed Ghidra review backup: `[maintainer-local-ghidra-backup-root]\BEA_20260605-011935_post_wave1116_door_wing_ai_current_risk_review_verified`.

Boundary:

This is static read-only Ghidra/source-reference evidence. It does not prove runtime engine behavior, runtime render behavior, exact concrete layouts, exact source-body identity, BEA patching behavior, gameplay outcomes, visual QA, or rebuild parity.
