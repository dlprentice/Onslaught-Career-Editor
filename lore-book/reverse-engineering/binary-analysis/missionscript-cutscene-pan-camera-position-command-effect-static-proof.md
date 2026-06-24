# MissionScript Cutscene Pan-Camera / Position Command-Effect Static Proof

Status: static cutscene pan-camera/position command-effect schema proof complete, not runtime proof
Last updated: 2026-06-08
Scope: `missionscript-cutscene-pan-camera-position-command-effect-static`
Artifact: `missionscript-cutscene-pan-camera-position-command-effect-static-proof.md`; schema: `missionscript-cutscene-pan-camera-position-command-effect.v1.json`

This proof converts saved retail Ghidra evidence from Wave580, the completed MissionScript descriptor/datatype schemas, and the public loose-MSL Fenrir cutscene corpus into a machine-checkable pan-camera command-effect map. It is the next narrow MissionScript command-effect child lane after the completed slot, objective/outcome, message/audio, Goodie-state, selected `SpawnThing`, and selected `GetThingRef` static proofs.

Static closeout remains unchanged:

- Static Ghidra function-quality closure: `6411/6411 = 100.00%`.
- Static debt: `0 / 0 / 0` commentless, exact-undefined, and `param_N` rows.
- Expanded post-100 static surface: `1560/1560 = 100.00%`.
- Active current-risk focused accounting: `1179/1179 = 100.00%`.
- Remaining active focused work: `0`.
- Latest verified Ghidra backup remains `G:\GhidraBackups\BEA_20260607-230027_post_wave1219_final_score16_current_risk_review_verified`.

## Schema Result

| Surface | Static result |
| --- | --- |
| Descriptor slots | The descriptor schema records `CreatePosition` index `65` at `0x0064de90` with symbol `s_CreatePosition_0064f6c0`, `Goto3PointPanCamera` index `113` at `0x0064ea90` with symbol `s_Goto3PointPanCamera_0064f3dc`, `Goto4PointPanCamera` index `114` at `0x0064ead0`, and `GotoPlayerCamera` index `115` at `0x0064eb10`. |
| Descriptor raw-shape boundary | `CreatePosition` preserves raw shape values including three type-`2` slots and type-`6` context. `Goto3PointPanCamera` preserves raw values including type-`5`, three type-`6` entries, and type-`2` duration context. These are static descriptor-shape values only; exact descriptor field layout and exact command arity remain bounded, not proven. |
| Position datatype | `CPositionDataType` is type id `6`, vtable `0x005e4da4`, size `20`, payload reads `+0x04`, `+0x08`, and `+0x0c` floats, and observed value getter slot `+0x44`. The `+0x10` field role remains unproven. |
| Pan-camera handlers | Wave580 saved `0x00533b70 IScript__Create3PointPanCamera` and `0x00533eb0 IScript__Create4PointPanCamera` with fixed three-stack-argument command ABI signatures. The 3-point body gets the target thing through datatype slot `+0x40`, transforms three position/vector arguments through getter slot `+0x44` using the thing matrix or `DAT_0083d9c0` fallback, constructs `CBSpline` and `CPanCamera`, reads duration through `+0x34`, and calls `CGame__SetCurrentCamera(&DAT_008a9a98,0,camera,1)`. |
| Loose corpus bridge | The public MSL cutscene example uses `pos1 = CreatePosition(-80.0, 20.0, -30.0)`, `pos2 = CreatePosition(0.0, 40.0, 60.0)`, `pos3 = CreatePosition(100.0, 20.0, 40.0)`, and `Goto3PointPanCamera(GetThingRef("Fenrir"), pos1, pos2, pos3, 15.0)`. The mission thing index records `6 cutscene Fenrir GetThingRef rows` across `level741` and `level742` cutscene files, with `17` total selected-level Fenrir `GetThingRef` rows. |

Evidence rows consumed by the schema:

| Evidence | Count |
| --- | ---: |
| Wave580 metadata/tag/xref/decompile rows | `6` / `6` / `6` / `6` |
| Wave580 instruction rows and vtable rows | `5454` / `36` |

Backups already verified by their original waves:

- Wave580: `G:\GhidraBackups\BEA_20260519-044247_post_wave580_iscript_camera_objective_verified`
- Latest static closeout backup: `G:\GhidraBackups\BEA_20260607-230027_post_wave1219_final_score16_current_risk_review_verified`

## Why This Matters

This gives clean-room MissionScript planning a bounded cutscene-camera bridge: descriptor names, position datatype shape, saved pan-camera handler bodies, and a public Fenrir cutscene corpus example. It connects the already-completed `GetThingRef` object-reference proof to the camera command family without claiming runtime object lookup, live script loading, or visible camera behavior.

The proof intentionally keeps descriptor raw-entry values separate from exact descriptor field layout. It also keeps runtime MissionScript execution, runtime cutscene playback, camera switching, visible output, Godot work, patching, rebuild parity, and no-noticeable-difference parity out of scope until copied/app-owned proof explicitly runs.

## Claim Boundary

This proves static cutscene pan-camera/position command-effect accounting from saved retail Ghidra evidence and public loose-MSL documentation. It does not prove runtime MissionScript execution, runtime command effects, runtime camera switching, runtime cutscene playback, visible camera output, runtime object identity, runtime object lookup by name, live loose-MSL loading, packed-vs-loose script selection, exact command descriptor layout, exact arity, exact argument type schema, exact `CPositionDataType` layout, exact `CPanCamera` layout, exact `CBSpline` layout, BEA patching behavior, visual QA, Godot parity, rebuild parity, or no-noticeable-difference parity.
