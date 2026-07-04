# Ghidra GillM Family Wave389

Status: public-safe static RE evidence

## Scope

Wave389 re-audited the GillM-family cluster around `0x004799c0` through `0x0047a0b0` and saved evidence-backed Ghidra name, signature, comment, and tag corrections for `11` function targets. The pass is static Ghidra evidence only. It does not launch BEA, patch the game, extract private assets, or prove runtime behavior.

The diagnostic `ExportVtableSlots.java` helper was widened from a `32` slot cap to `256` slots so the CGillM RTTI vtable entries at slots `66`, `117`, `118`, and `119` could be exported and checked.

## Saved Ghidra Changes

| Address | Current saved name | Evidence summary |
| --- | --- | --- |
| `0x004799c0` | `CGillM__VFunc09_InitGroundedSpawnState` | CGillM RTTI vtable `0x005e0b30` slot `9`; grounded/timer/spawn-state context. |
| `0x00479a50` | `CGillM__InitLegMotion` | CGillM vtable slot `117`; `LegMotion` lookup, `0xf0` CMCGillM allocation, CMCGillM vtable install, and `this+0x70` store. |
| `0x00479b40` | `SharedCMCMech__ScalarDeletingDestructor` | CMCBattleEngine, CMCGillM, and CMCThunderHead vtable slot `1` all point to the shared CMCMech scalar-deleting destructor body. |
| `0x00479b60` | `CGillM__InitGillMAIComponent` | CGillM vtable slot `118`; `0x60` allocation, CWarspite-style base init, CGillMAI vtable `0x005dbcb4`, and `this+0x13c` store. |
| `0x00479bf0` | `CGillMAI__ScalarDeletingDestructor` | CGillMAI vtable slot `1`; wrapper calls `CGillMAI__Destructor` and honors scalar-delete flags. |
| `0x00479c10` | `CGillMAI__Destructor` | Called by the CGillMAI scalar-deleting destructor; restores base AI-style state, removes tracked sets, and calls monitor shutdown. |
| `0x00479cb0` | `CGillM__InitTerrainGuideComponent` | CGillM vtable slot `119`; `0x20` TerrainGuide-style allocation/init and `this+0x208` store. |
| `0x00479d10` | `CGillM__UpdateGroundedVerticalDrift` | CGillM vtable slot `66`; corrects the older CExplosionInitThing owner label to GillM grounded vertical-drift context. |
| `0x00479db0` | `CGillM__TriggerRandomArmHitAnimationIfReady` | `Gill_M_Left_Arm` / `Gill_M_Right_Arm` strings plus cooldown/child-component hit-animation context; corrects the older CExplosionInitThing owner label. |
| `0x00479f30` | `CGillM__ComputeTerrainClearanceNoiseScale` | Terrain clearance helper from the CMCGillM slot-wrapper region; corrects the older CUnitAI owner label. |
| `0x0047a0b0` | `CGillM__ComputeLateralSlopeAlignment` | Heading/heightfield-normal helper from the GillM movement region; corrects the older CUnitAI owner label. |

## Validation

- Headless `ApplyGillMFamilyWave389.java` dry run: `updated=0 skipped=11 renamed=0 would_rename=10 missing=0 bad=0`, with `REPORT: Save succeeded`.
- Headless `ApplyGillMFamilyWave389.java` apply run: `updated=11 skipped=0 renamed=10 would_rename=0 missing=0 bad=0`, with `REPORT: Save succeeded`.
- Post-apply read-back verified `11` metadata rows, `11` decompile exports, `13` xref rows, `2431` instruction rows, `11` tag rows, `112` related vtable-slot rows, and `128` CGillM vtable-slot rows.
- `py -3 tools\ghidra_gillm_family_wave389_probe_test.py`: PASS, `2/2`.
- `py -3 -m py_compile tools\ghidra_gillm_family_wave389_probe.py tools\ghidra_gillm_family_wave389_probe_test.py`: PASS.
- `cmd.exe /c npm run test:ghidra-gillm-family-wave389`: PASS; focused probe status `PASS`, `11` targets, `11` metadata rows, `11` tag rows, `0` failures.
- Refreshed whole-database queue: `6027` functions, `1455` commented functions, `4572` commentless functions, `1932` undefined signatures, and `1901` `param_N` signatures.
- Current confirmation proxies are telemetry only: comment-backed `1455/6027 = 24.14%`; strict clean-signature `1393/6027 = 23.11%`.
- Actual live Ghidra project backup verified at `[maintainer-local-ghidra-backup-root]\BEA_20260513_204327_post_wave389_gillm_family_verified` with `19` files, `153947015` bytes, and `HashDiffCount=0`.

## Not Proven

- This does not prove exact Stuart-source method identities for every GillM-family body.
- This does not prove concrete GillM, CMCGillM, CGillMAI, TerrainGuide, or CMCMech layouts.
- This does not recover local variable names, structure fields, or full type definitions.
- This does not prove runtime GillM spawning, movement, AI, destruction, animation, or terrain behavior.
- This does not launch BEA, patch BEA, mutate the installed game, or prove rebuild parity.
