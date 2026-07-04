# Wave1142 Mixed Score22 Current-Risk Review

Wave1142 (`wave1142-mixed-score22-current-risk-review`) re-read ten Wave1108 current-risk rows from the mixed score22 current-risk residual review set with fresh Ghidra metadata, tag, xref, instruction, callsite-window, static-shadow no-function-window, and decompile exports.

This moves Wave1108 current focused accounting to `261/1179 = 22.14%`. Static closure remains `6411/6411 = 100.00%`; static debt remains `0 / 0 / 0`; expanded post-100 static surface remains `1560/1560 = 100.00%`; Wave911 focused remains `812/1408 = 57.67%`; Wave911 top-500 remains `500/500 = 100.00%`. Current risk candidates: `6166`; current focused candidates: `1178`; live regenerated current focused candidates: `1178`; remaining active focused work: `918`.

Probe token anchor: Wave1142; wave1142-mixed-score22-current-risk-review; `261/1179 = 22.14%`; 10 current-risk rows; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 918; current risk candidates: 6166; mixed score22 current-risk residual review; fresh Ghidra export; xref-site windows; static-shadow no-function boundary candidates; read-only review; no mutation; `0 / 0 / 0`; `6411/6411 = 100.00%`; `[maintainer-local-ghidra-backup-root]\BEA_20260605-153716_post_wave1142_mixed_score22_current_risk_review_verified`; `[maintainer-local-ghidra-backup-root]\BEA_20260605-145724_post_wave1141_cdxcompass_hud_current_risk_review_verified`.

## Primary Evidence

| Address | Name | Static evidence |
| --- | --- | --- |
| `0x004443f0` | `CDestructableSegmentsController__TriggerCoreCascadeIfEligible` | `CUnit__MarkDestroyedAndCleanupLinks` call xref `0x004fd1dc`; checks core child state and cached health/current active-value sum before triggering the root cascade path. |
| `0x0047eb80` | `CStaticShadows__SampleShadowHeightBilinear` | `110` xrefs; saved `__fastcall` signature consumes `world_pos` from EDX, offsets world X/Z by terrain-origin globals, samples/interpolates signed 16-bit height data from `this+0x1028`, scales by `this+0x102c`, and falls back to zero/flat outside range. |
| `0x004b6df0` | `COggLoader__readerSubobject_scalar_deleting_dtor` | DATA vtable xref `0x005dc690`; scalar-deleting wrapper calls `COggLoader__readerSubobject_dtor_body`, conditionally frees the adjusted base pointer, returns it, and ends with `RET 0x4`. |
| `0x004bfd80` | `CSpawnerThng__scalar_deleting_dtor` | DATA vtable xref `0x005dd170`; Wave1022 normalized the stale `CSpawnerThing` spelling to `CSpawnerThng`; wrapper calls `CSpawnerThng__dtor_base`, optionally frees `this`, returns it, and ends with `RET 0x4`. |
| `0x004bfed0` | `CSpawnerThng__dtor_base` | `CSpawnerThng__scalar_deleting_dtor` call xref `0x004bfd83`; removes the observed owner/list link at `this+0x7c` when present and chains to `CComplexThing__dtor_base`. |
| `0x004c4ae0` | `CPDMesh__scalar_deleting_dtor` | DATA vtable xref `0x005ddb3c`; scalar-deleting wrapper calls `CPDMesh__dtor_base`, optionally frees `this`, and returns `this`. |
| `0x004cffd0` | `CVideoDetailLevel__GetCurrentPresetFromItems` | DATA xref `0x005de598`; compares option-item values against active display-profile defaults and texture/multisample globals, returning preset `1`, `2`, `3`, or `0`. |
| `0x005018b0` | `CVertexShader__dtor` | `CVertexShader__scalar_deleting_dtor` call xref `0x00501893`; restores the vertex-shader vtable, unlinks global/base lists, releases the device shader, frees constant/source/blob buffers, and chains to base device-object teardown. |
| `0x00506010` | `ProjectileBurst__SpawnFromPercentBucketFallback` | Ten callers, including `ProjectileBurstCallerBoundary_0044e020`, `ProjectileBurstCallerBoundary_004f4920`, `CGeneralVolume__DispatchMode3BurstProgressAndSpawn`, `CBattleEngineWalkerPart__ChargeWeapon`, and `CBattleEngineWalkerPart__FireWeapon`; tags remain intentionally empty in saved Ghidra. |
| `0x00527c90` | `CReconnectInterface__ctor` | Eight no-function static initializer/destructor-record callsites construct reconnect-interface records from tweak-name/default-index arguments; no new boundary was promoted. |

## Boundary Candidates

Wave1142 exported 805 instruction-window rows around five no-function `CStaticShadows__SampleShadowHeightBilinear` callers: `0x00415310`, `0x0041930c`, `0x004194b7`, `0x004807d8`, and `0x004f61dd`. All five call the saved static-shadow bilinear helper directly, but the window evidence is not enough by itself to create or name new functions. They remain static-shadow no-function boundary candidates.

The callsite-window export also re-read projectile and reconnect-interface xref sites. Projectile xrefs include `0x0044e093` in `ProjectileBurstCallerBoundary_0044e020`, `0x004f4bd6` in `ProjectileBurstCallerBoundary_004f4920`, `0x00411e0f` in `CGeneralVolume__DispatchMode3BurstProgressAndSpawn`, `0x00413d5f` in `CBattleEngineWalkerPart__ChargeWeapon`, and `0x00413ce2` in `CBattleEngineWalkerPart__FireWeapon`. Reconnect-interface xrefs at `0x0053aa1c`, `0x0054556c`, `0x0054d4dc`, `0x0054d50c`, `0x00551ecc`, `0x0055643c`, `0x0055b08c`, and `0x0055b0bc` are static initializer/destructor-record callsites rather than proved standalone function entries.

## Evidence Counts

- Primary exports: `10` metadata rows, `10` tag rows, `135` xref rows, `582` instruction rows, and `10` decompile rows.
- Callsite-window exports: `625` instruction rows around `27` xref sites; the `4` missing targets are DATA table/vtable refs.
- Static-shadow no-function exports: `805` instruction rows around `5` no-function boundary candidates.
- Queue closure: `6411/6411 = 100.00%`; static debt `0 / 0 / 0`.
- Current-risk refresh: current risk candidates `6166`; current focused candidates `1178`; focused threshold `15`; not Wave911 reconstruction.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260605-153716_post_wave1142_mixed_score22_current_risk_review_verified`, `19` files, `175967111` bytes, `DiffCount=0`, `HashDiffCount=0`.
- Previous completed backup: `[maintainer-local-ghidra-backup-root]\BEA_20260605-145724_post_wave1141_cdxcompass_hud_current_risk_review_verified`.

## Boundary

This is static Ghidra evidence only. Runtime shadow/terrain behavior, runtime projectile behavior, `weapon_fire_breaks_stealth`, runtime stealth behavior, runtime reconnect-interface behavior, runtime Ogg streaming, spawner cleanup, shader/device behavior, video-menu behavior, cascade behavior, exact layouts, exact source-body identity, BEA patching, gameplay outcomes, visual QA, and rebuild parity remain separate proof.
