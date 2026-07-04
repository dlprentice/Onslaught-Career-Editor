# Ghidra GillM Grounded Movement Review Wave1000 Readiness Note

Status: complete read-only static read-back evidence
Date: 2026-05-31
Scope: `gillm-grounded-movement-review-wave1000`

Wave1000 re-reviewed the Wave911 risk-ranked `CGillM` grounded movement, terrain, and state-vector island around the prior Wave389 and Wave409 corrections. Fresh read-only metadata, tag, xref, instruction, decompile, and vtable-slot exports matched the already-saved evidence, so this wave made no Ghidra mutation, no rename, no signature change, no function-boundary change, no executable-byte change, no BEA launch, and no runtime/game-file mutation.

Primary targets:

| Address | Read-back evidence |
| --- | --- |
| `0x004799c0 CGillM__VFunc09_InitGroundedSpawnState` | CGillM vtable `0x005e0b30` slot `9`; clears/stamps grounded spawn fields, calls inherited slot-9 body, samples static-shadow height, marks `+0x274`, and snapshots position context into `+0x278`. |
| `0x00479a50 CGillM__InitLegMotion` | CGillM vtable slot `117`; resolves `LegMotion`, allocates a `0xf0` CMCGillM motion-controller object, installs vtable `0x005dbc74`, stores it at `this+0x70`, and seeds CMCMech motion parameters. |
| `0x00479b60 CGillM__InitGillMAIComponent` | CGillM vtable slot `118`; allocates a `0x60` CGillMAI-style component, initializes it through the Warspite-style base path, installs vtable `0x005dbcb4`, and stores it at `this+0x13c`. |
| `0x00479cb0 CGillM__InitTerrainGuideComponent` | CGillM vtable slot `119`; allocates a `0x20` terrain-guide component, calls `CTerrainGuide__ctor`, and stores it at `this+0x208`. |
| `0x00479d10 CGillM__UpdateGroundedVerticalDrift` | CGillM vtable slot `66`; uses `+0x274`, `+0x244`, static-shadow sampling, and vertical drift fields `+0x84/+0xcc` before dispatching the shared update helper. |
| `0x00479db0 CGillM__TriggerRandomArmHitAnimationIfReady` | Uses `Gill_M_Left_Arm` and `Gill_M_Right_Arm` strings, cooldown field `+0x26c`, and component-list context `+0x19c` before selecting and triggering a matching arm hit animation. |
| `0x00479f30 CGillM__ComputeTerrainClearanceNoiseScale` | CMCGillM-region terrain helper; gates on `+0x274`, `+0x244`, and motion-vector magnitude, samples two static-shadow heights, and returns a scaled terrain-clearance value. |
| `0x0047a0b0 CGillM__ComputeLateralSlopeAlignment` | CMCGillM-region lateral terrain helper; uses heading field `+0x114`, samples a heightfield normal, and returns a lateral slope-alignment scalar. |
| `0x0047a160 CGillM__StartState1WithStoredMotionVector` | CGillM vtable slot `100`; skips state `1/2`, copies the four-dword stored motion vector at `+0x278` into a virtual dispatch at vtable `+0xf4` with a zero flag, then writes `+0x244 = 1`. |

Context target: `0x00479bf0 CGillMAI__ScalarDeletingDestructor`.

Fresh read-back evidence:

- Exports: `10` metadata rows, `10` tag rows, `10` xref rows, `526` body-instruction rows, `10` decompile rows, and `128` CGillM vtable-slot rows.
- Existing GillM probes passed after normalizing the historical Wave409 probe to current queue closure: `test:ghidra-gillm-family-wave389`, `test:ghidra-gillm-start-state-vector-wave409`.
- Queue closure remains `6222/6222 = 100.00%`.
- Wave911 focused re-audit progress remains `467/1408 = 33.17%` because this is a risk-ranked residual island rather than a new focused-candidate anchor.
- Expanded static surface progress is now `606/1478 = 41.00%`.
- Wave911 top-500 risk-ranked coverage for this residual pass advances to `350/500 = 70.00%`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260531-101059_post_wave1000_gillm_grounded_movement_review_verified`, `19` files, `173869959` bytes, `DiffCount=0`, `HashDiffCount=0`.

Probe token anchor: Wave1000; `gillm-grounded-movement-review-wave1000`; `0x004799c0 CGillM__VFunc09_InitGroundedSpawnState`; `0x00479d10 CGillM__UpdateGroundedVerticalDrift`; `0x00479db0 CGillM__TriggerRandomArmHitAnimationIfReady`; `0x00479f30 CGillM__ComputeTerrainClearanceNoiseScale`; `0x0047a0b0 CGillM__ComputeLateralSlopeAlignment`; `0x0047a160 CGillM__StartState1WithStoredMotionVector`; `467/1408 = 33.17%`; `606/1478 = 41.00%`; `350/500 = 70.00%`; `6222/6222 = 100.00%`; `[maintainer-local-ghidra-backup-root]\BEA_20260531-101059_post_wave1000_gillm_grounded_movement_review_verified`; no mutation.

What this proves:

- The reviewed CGillM rows exist in the saved Ghidra project with the expected names, signatures, comments, and tags.
- The saved Wave389 owner/signature corrections and Wave409 state-vector correction still match fresh retail Ghidra xref/decompile/instruction/vtable evidence.
- The grounded movement island is statically coherent around CGillM vtable `0x005e0b30`, terrain guide setup, grounded-state fields, arm-hit animation strings, and stored motion-vector dispatch.

What remains unproven:

- Exact Stuart source-body identity.
- Concrete CGillM, CMCGillM, CGillMAI, TerrainGuide, or state-vector layouts.
- Runtime GillM movement, terrain, or arm-hit animation behavior.
- BEA patching behavior.
- Rebuild parity.
