# MissionScript Cutscene Pan-Camera / Position Command-Effect Static Proof Readiness Note

Status: static cutscene pan-camera/position command-effect schema proof complete, not runtime proof
Date: 2026-06-08
Scope: `missionscript-cutscene-pan-camera-position-command-effect-static`

This slice records a public-safe static proof for the MissionScript cutscene pan-camera / position command-effect bridge. It adds `missionscript-cutscene-pan-camera-position-command-effect-static-proof.md`, `missionscript-cutscene-pan-camera-position-command-effect.v1.json`, and the focused probe `tools/missionscript_cutscene_pan_camera_position_command_effect_static_probe.py`.

Representative anchors:

| Anchor | Evidence |
| --- | --- |
| `CreatePosition` | Descriptor index `65`, record `0x0064de90`, symbol `s_CreatePosition_0064f6c0`; raw descriptor-shape evidence only. |
| `Goto3PointPanCamera` | Descriptor index `113`, record `0x0064ea90`, symbol `s_Goto3PointPanCamera_0064f3dc`; raw shape includes type-`5`, three type-`6` entries, and type-`2` duration context. |
| `Goto4PointPanCamera` | Descriptor index `114`, record `0x0064ead0`, symbol `s_Goto4PointPanCamera_0064f3c8`; static four-position pan-camera descriptor context only. |
| `CPositionDataType` | Type id `6`, vtable `0x005e4da4`, size `20`, payload reads `+0x04`, `+0x08`, `+0x0c` floats, observed value getter slot `+0x44`; `+0x10` remains unproven. |
| `0x00533b70 IScript__Create3PointPanCamera` | Wave580 fixed ABI handler; gets thing through slot `+0x40`, reads three position/vector values through `+0x44`, reads duration through `+0x34`, uses `DAT_0083d9c0` as fallback transform context, builds `CBSpline` and `CPanCamera`, then calls `CGame__SetCurrentCamera(&DAT_008a9a98,0,camera,1)`. |
| `0x00533eb0 IScript__Create4PointPanCamera` | Adjacent Wave580 pan-camera context with four position/vector arguments and the same `CPanCamera` / `CGame__SetCurrentCamera` path. |
| `GetThingRef("Fenrir")` | Public MSL cutscene example plus `6 cutscene Fenrir GetThingRef rows` across `level741` and `level742`, with `17` selected-level Fenrir `GetThingRef` rows in the mission thing index. |

Static closeout remains unchanged:

- Static Ghidra function-quality closure: `6411/6411 = 100.00%`.
- Static debt: `0 / 0 / 0`.
- Expanded post-100 static surface: `1560/1560 = 100.00%`.
- Active current-risk focused accounting: `1179/1179 = 100.00%`.
- Remaining active focused work: `0`.
- Latest verified Ghidra backup remains `[maintainer-local-ghidra-backup-root]\BEA_20260607-230027_post_wave1219_final_score16_current_risk_review_verified`.

Evidence consumed:

- Wave580 exports: `6` metadata rows, `6` tag rows, `6` xref rows, `5454` instruction rows, `6` decompile rows, and `36` vtable rows.
- Wave580 verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260519-044247_post_wave580_iscript_camera_objective_verified`, `19` files, `160500615` bytes, `DiffCount=0`.
- MissionScript descriptor schema: `missionscript-command-descriptor-schema.v1.json`.
- MissionScript datatype schema: `missionscript-vm-datatype-opcode-schema.v1.json`.
- Public loose-MSL docs: `msl-scripting.md`, `mission-thing-usage.md`, and `mission-events-index.md`.

What this proves:

- The static descriptor/datatype/handler/corpus chain for `CreatePosition` feeding `Goto3PointPanCamera(GetThingRef("Fenrir"), pos1, pos2, pos3, duration)` is documented and machine-checkable.
- The `IScript__Create3PointPanCamera` saved body statically bridges thing lookup, position values, duration, `CBSpline`, `CPanCamera`, and `CGame__SetCurrentCamera`.
- The proof is suitable for later copied/app-owned camera or clean-room MissionScript planning.

What remains unproven:

- Runtime MissionScript execution.
- Runtime command effects.
- Runtime camera switching.
- Runtime cutscene playback.
- Visible camera output.
- Runtime object identity or lookup by name.
- Live loose-MSL loading or packed-vs-loose script selection.
- Exact descriptor, datatype, `CPanCamera`, or `CBSpline` layouts.
- BEA patching behavior.
- Visual QA.
- Godot parity.
- Rebuild parity or no-noticeable-difference parity.
