# WinUI Enhanced Profile Catalog Readiness Note

Status: AppCore/WinUI safe-copy profile catalog hardening complete
Date: 2026-06-18
Scope: `winui-enhanced-profile-catalog`

This slice makes safe-copy profile presets catalog-backed instead of only hard-coded in AppCore. The canonical profile catalog is `patches/catalog/safe-copy-profiles.v1.json`.

Implemented evidence:

| Area | Result |
| --- | --- |
| Profile catalog | Added `safe-copy-profiles.v1` with `compatibility-copy`, `recommended-safe-copy`, `enhanced-edition-preview`, and `custom` presets. |
| AppCore loader | `BinaryPatchPlanBuilder` loads the JSON catalog, validates profile patch keys against `patches/catalog/patches.v2.json`, rejects hidden companion rows as direct profile keys, verifies preset shape against the supported fallback profile set, and exposes catalog version/hash/status. |
| Module metadata | Safe-copy profile modules now carry restore strategy, evidence refs, and explicit non-claims in addition to proof status, claim boundary, patch keys, launch args, and copied-options edits. |
| Generated manifests | Playable copied-game manifests write `profileCatalogVersion`, `profileCatalogSha256`, and module metadata under `profilePreset`. |
| UX/product boundary | No new patch bytes, no new runtime proof, no Ghidra mutation, no online mode, and no monolithic mega-patch claim. |

Claim boundary:

- This proves profile/catalog provenance and manifest metadata for safe copied-game profiles.
- This does not prove a new visual/runtime behavior.
- This does not add online networking, matchmaking, in-game toggles, control-feel fixes, or clean-room rebuild parity.
- Future online/resource/runtime modules must remain absent from the Enhanced Profile Preview until they have separate row/module proof, conflict/restore metadata, and accepted validation.

Focused validation:

- `npm run test:winui-enhanced-profile-module-manifest`

Broader validation for the final commit is recorded in the commit closeout/state files.
