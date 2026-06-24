# Wave1142 Mixed Score22 Current-Risk Readiness Note

Status: complete static read-back evidence
Date: 2026-06-05
Scope: `wave1142-mixed-score22-current-risk-review`

Wave1142 re-read ten Wave1108 current-risk rows from the mixed score22 current-risk residual review set with fresh Ghidra metadata, tag, xref, instruction, callsite-window, static-shadow no-function-window, and decompile exports. It was a read-only review with no mutation: no rename, no signature edit, no comment/tag edit, no function-boundary change, no executable-byte change, no BEA launch, no installed-game mutation, and no runtime-file mutation.

Probe token anchor: Wave1142; wave1142-mixed-score22-current-risk-review; `261/1179 = 22.14%`; 10 current-risk rows; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 918; current risk candidates: 6166; mixed score22 current-risk residual review; fresh Ghidra export; xref-site windows; static-shadow no-function boundary candidates; read-only review; no mutation; `0 / 0 / 0`; `6411/6411 = 100.00%`; `G:\GhidraBackups\BEA_20260605-153716_post_wave1142_mixed_score22_current_risk_review_verified`; `G:\GhidraBackups\BEA_20260605-145724_post_wave1141_cdxcompass_hud_current_risk_review_verified`.

| Address | Evidence |
| --- | --- |
| `0x004443f0 CDestructableSegmentsController__TriggerCoreCascadeIfEligible` | `CUnit__MarkDestroyedAndCleanupLinks` call xref `0x004fd1dc`; older threshold wording remains bounded to static cascade-trigger evidence. |
| `0x0047eb80 CStaticShadows__SampleShadowHeightBilinear` | `110` xrefs; saved `__fastcall` signature consumes `world_pos` from EDX and samples/interpolates packed height data. Five no-function callers remain boundary candidates only. |
| `0x004b6df0 COggLoader__readerSubobject_scalar_deleting_dtor` | DATA vtable xref `0x005dc690`; scalar-deleting wrapper calls the reader-subobject dtor body. |
| `0x004bfd80 CSpawnerThng__scalar_deleting_dtor` | DATA vtable xref `0x005dd170`; Wave1022 normalized the stale `CSpawnerThing` spelling to `CSpawnerThng`. |
| `0x004bfed0 CSpawnerThng__dtor_base` | `CSpawnerThng__scalar_deleting_dtor` call xref `0x004bfd83`; destructor-base removes the observed owner/list link before chaining to `CComplexThing__dtor_base`. |
| `0x004c4ae0 CPDMesh__scalar_deleting_dtor` | DATA vtable xref `0x005ddb3c`; scalar-deleting wrapper calls `CPDMesh__dtor_base`. |
| `0x004cffd0 CVideoDetailLevel__GetCurrentPresetFromItems` | DATA xref `0x005de598`; compares option-item values against display-profile defaults and device/menu globals. |
| `0x005018b0 CVertexShader__dtor` | `CVertexShader__scalar_deleting_dtor` call xref `0x00501893`; releases shader/list/device-object resources. |
| `0x00506010 ProjectileBurst__SpawnFromPercentBucketFallback` | Ten callers, including `ProjectileBurstCallerBoundary_0044e020`, `ProjectileBurstCallerBoundary_004f4920`, `CGeneralVolume__DispatchMode3BurstProgressAndSpawn`, `CBattleEngineWalkerPart__ChargeWeapon`, and `CBattleEngineWalkerPart__FireWeapon`; tags remain intentionally empty in saved Ghidra. |
| `0x00527c90 CReconnectInterface__ctor` | Eight no-function static initializer/destructor-record callsites construct global reconnect-interface records; no new function boundaries were created. |

Read-back evidence:

- Primary exports: 10 metadata rows, 10 tag rows, 135 xref rows, 582 instruction rows, and 10 decompile rows.
- Callsite-window exports: 625 instruction rows around 27 xref sites; the four missing targets are DATA table/vtable refs, not executable call windows.
- Static-shadow no-function window exports: 805 instruction rows around five no-function `CStaticShadows__SampleShadowHeightBilinear` callers at `0x00415310`, `0x0041930c`, `0x004194b7`, `0x004807d8`, and `0x004f61dd`.
- Queue closure after the read-only review remains `6411/6411 = 100.00%`, static debt `0 / 0 / 0`.
- Current-risk accounting moves to `261/1179 = 22.14%`; current risk candidates `6166`; current focused candidates `1178`; remaining active focused work: `918`.
- Verified backup: `G:\GhidraBackups\BEA_20260605-153716_post_wave1142_mixed_score22_current_risk_review_verified`, 19 files, 175967111 bytes, `DiffCount=0`, `HashDiffCount=0`.
- Previous completed backup: `G:\GhidraBackups\BEA_20260605-145724_post_wave1141_cdxcompass_hud_current_risk_review_verified`.

What this proves:

- The ten target rows still have clean saved Ghidra names, signatures, comments, xrefs, and decompile rows.
- The tag-empty projectile helper row is intentional current saved state, not a failed export.
- The stale `CSpawnerThing` spelling was still present in active docs and is normalized in this wave's tracked docs to match saved Ghidra `CSpawnerThng`.
- The static-shadow no-function callsites and reconnect static constructor callsites are bounded follow-up evidence, not mutation proof.

What remains unproven:

- Runtime shadow/terrain behavior.
- Runtime projectile, stealth, reconnect-interface, Ogg streaming, spawner cleanup, shader, menu, and cascade behavior.
- New static-shadow or reconnect-interface function-boundary identity.
- Exact concrete layouts and exact source-body identity.
- BEA patching behavior, gameplay outcomes, visual QA, and rebuild parity.
