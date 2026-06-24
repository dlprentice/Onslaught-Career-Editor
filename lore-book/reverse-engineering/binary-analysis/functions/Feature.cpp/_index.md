# Feature.cpp Functions

> Source family: feature/pickup-spawn helpers | Binary: `BEA.exe` (Steam build)

> **Queue status (2026-05-26):** Ghidra export-contract closure **6113/6113** (Wave900: every function commented; clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

## Overview

This folder tracks saved Ghidra evidence for feature lifecycle and pickup-spawn helpers. Wave 368 corrected stale generic feature vfunc labels and stale `CExplosionInitThing` constructor-like labels after fresh metadata, decompile, xref, instruction, tag, and vtable read-back.

Wave1133 (`wave1133-feature-pickup-current-risk-review`) re-read the four Feature/pickup-spawn anchors `0x0044ca30 CFeature__Init`, `0x0044cbe0 CFeature__ShutdownAndRemoveFromWorld`, `0x0044cee0 CFeature__MaybeSpawnRandomPickupFromData`, and `0x0044e300 PickupSpawn__MaybeSpawnAttachedPickupFromFrame_0044e300` with fresh Ghidra export evidence and no mutation. The review keeps `CFeature__Init` tied to init field `+0x3bc`, `CActor__Init`, and optional random sample startup; keeps shutdown tied to sample kill, occupancy removal, visibility update, and base cleanup dispatch; keeps the feature-owned pickup helper tied to `DAT_008553f8`, `CWorldPhysicsManager__CreatePickup`, and feature data field `+0xe4`; and keeps the owner-neutral attached pickup helper tied to `+0x164`, attached-frame context, `DAT_008553f8`, and profile field `+0xec`. Wave1133 covers `6 rows`; current focused accounting is `184/1179 = 15.61%`; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 995; static debt remains `0 / 0 / 0`; the wave is a read-only review with no mutation. Verified backup: `G:\GhidraBackups\BEA_20260605-100620_post_wave1133_feature_pickup_current_risk_review_verified`. Runtime feature/pickup/drop behavior, exact feature/pickup layouts, source-body identity, BEA patching, gameplay outcomes, visual QA, and rebuild parity remain separate proof.

Wave993 (`feargrid-feature-pickup-review-wave993`) re-read the Feature/pickup-spawn rows as context for the FearGrid spatial API review and saved one comment/tag normalization on `0x0044c440 CFearGrid__RebuildOccupancyAndScheduleTick`, replacing stale `CFearGrid__LookupFearWeightByArchetype` wording with `FearGridTrackedObject__LookupFearWeightByArchetype`. Feature context anchors include `0x0044ca30 CFeature__Init`, `0x0044cbe0 CFeature__ShutdownAndRemoveFromWorld`, `0x0044cee0 CFeature__MaybeSpawnRandomPickupFromData`, and `0x0044e300 PickupSpawn__MaybeSpawnAttachedPickupFromFrame_0044e300`. Wave911 focused re-audit progress is `447/1408 = 31.75%`; expanded static surface progress is `549/1478 = 37.14%`; export-contract closure remains `6222/6222 = 100.00%`. Verified backup: `G:\GhidraBackups\BEA_20260531-061908_post_wave993_feargrid_feature_pickup_review_verified`. Runtime AI/fear behavior, runtime pickup behavior, exact feature/pickup layouts, source-body identity, BEA patching, and rebuild parity remain separate proof.

Probe token anchor: Wave993; feargrid-feature-pickup-review-wave993; 0x0044c440 CFearGrid__RebuildOccupancyAndScheduleTick; FearGridTrackedObject__LookupFearWeightByArchetype; 0x0044cee0 CFeature__MaybeSpawnRandomPickupFromData; 0x0044e300 PickupSpawn__MaybeSpawnAttachedPickupFromFrame_0044e300; 447/1408 = 31.75%; 549/1478 = 37.14%; 6222/6222 = 100.00%; G:\GhidraBackups\BEA_20260531-061908_post_wave993_feargrid_feature_pickup_review_verified.

## Functions

| Address | Saved name | Purpose | Evidence |
| --- | --- | --- | --- |
| `0x0044ca30` | `CFeature__Init` | Copies feature data from the init object, creates the owned resource object, calls `CActor__Init`, links into occupancy/grid context, updates shadow context, and optionally plays a random sample | `ghidra_feature_unitai_frontend_signature_tranche_2026-05-13.md` |
| `0x0044cbe0` | `CFeature__ShutdownAndRemoveFromWorld` | Removes feature-world side effects through sample kill, occupancy removal, visibility update, and base cleanup dispatch | `ghidra_feature_unitai_frontend_signature_tranche_2026-05-13.md` |
| `0x0044cee0` | `CFeature__MaybeSpawnRandomPickupFromData` | Feature-adjacent randomized pickup helper that gates on feature data and calls the pickup creation/init path; owner is inferred and remains less certain than the observed behavior | `ghidra_feature_unitai_frontend_signature_tranche_2026-05-13.md` |
| `0x0044e300` | `PickupSpawn__MaybeSpawnAttachedPickupFromFrame_0044e300` | Owner-neutral attached pickup-spawn helper with frame/transform context and pickup creation/init dispatch | `ghidra_feature_unitai_frontend_signature_tranche_2026-05-13.md` |
| `0x00511c10` | `CFeatureTexture__SetTagListIndexOrMinusOne` | Wave560 queue-tail reference resolver correction: `CFeatureTexture__ApplyToFeatureByName` calls this on the matched `DAT_00855404` feature record, and the body resolves the caller's tag name through `DAT_008553f8` into `this+0x8` or `-1` | `ghidra_queue_tail_refs_wave560_2026-05-18.md` |

## Boundaries

- These are saved static Ghidra names, signatures, comments, and tags only.
- `0x0044cee0` has a feature owner inferred from caller/field context; exact source identity remains open.
- `0x0044e300` is intentionally owner-neutral until a stronger class/source identity is proven.
- Wave560 also saved `CWorldPhysicsManager__ResolveThingOrComponentDefinitionRefs`; the feature-texture correction is static queue-tail reference resolver evidence only.
- Concrete feature/pickup layouts, local variables, exact source identities, runtime pickup behavior, BEA launch behavior, game patching, and rebuild parity remain unproven.
