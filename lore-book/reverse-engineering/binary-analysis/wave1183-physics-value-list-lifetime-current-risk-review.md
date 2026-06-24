# Wave1183 Physics Value-List Lifetime Current-Risk Review

Status: complete static current-risk review; saved comment/tag correction; pending artifact commit
Date: 2026-06-06
Scope tag: `wave1183-physics-value-list-lifetime-current-risk-review`

Wave1183 accounts for `21 PhysicsScript value-list/registry/lifetime current-risk rows` from the `wave1108-current-risk-rank` current-risk denominator with fresh serialized Ghidra evidence. The pass corrected six saved comments that still described optional scalar-delete freeing through `OID__FreeObject`. Live instruction read-back and helper metadata prove those six wrappers free through `CDXMemoryManager__Free(&DAT_009c3df0, this)` via call `0x00549220` when the scalar-delete flag bit is set.

Codex read-only consults were used before the final judgment: one consult recommended a four-row value-list slice, a second recommended the widened 21-row PhysicsScript value-list/registry/lifetime slice, and Codex root accepted the widened slice after duplicate/accounting checks and live Ghidra export review. No Cursor/Composer was used.

Static closure remains `6411/6411 = 100.00%` with static debt `0 / 0 / 0`; expanded post-100 static surface remains `1560/1560 = 100.00%`; Wave911 focused is historical-retired/non-reconstructable at `812/1408 = 57.67%`; Wave911 top-500 remains `500/500 = 100.00%`; Wave1108 current focused accounting is now `779/1179 = 66.07%`; current risk candidates: 6166; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 400; focused threshold `15`; not Wave911 reconstruction.

Fresh exports verified `21` metadata rows, `21` tag rows, `120 xref rows`, `404 instruction rows`, `21` decompile rows, and `1` helper metadata row. Verified backup: `G:\GhidraBackups\BEA_20260606-123452_post_wave1183_physics_value_list_lifetime_current_risk_review_verified`.

## Corrected Lifetime Anchors

| Address | Anchor | Correction |
| --- | --- | --- |
| `0x00438400` | `CPhysicsRoundValueLeaf__shared_scalar_deleting_dtor` | Calls `CPhysicsRoundValue__dtor_base`, then conditionally frees `this` through `CDXMemoryManager__Free(&DAT_009c3df0, this)` via `0x00549220`, not `OID__FreeObject`. |
| `0x0043a840` | `CPhysicsSpawnerValueLeaf__shared_scalar_deleting_dtor` | Calls `CPhysicsSpawnerValue__dtor_base`, then uses the same `CDXMemoryManager__Free` optional-free path. |
| `0x0043b970` | `CPhysicsExplosionValueLeaf__shared_scalar_deleting_dtor` | Calls `CPhysicsExplosionValue__dtor_base`, then uses the same `CDXMemoryManager__Free` optional-free path. |
| `0x0043bff0` | `CPhysicsFeatureValueLeaf__shared_scalar_deleting_dtor` | Calls `CPhysicsFeatureValue__dtor_base`, then uses the same `CDXMemoryManager__Free` optional-free path. |
| `0x0043c230` | `CPhysicsHazardValueLeaf__shared_scalar_deleting_dtor` | Calls `CPhysicsHazardValue__dtor_base`, then uses the same `CDXMemoryManager__Free` optional-free path. |
| `0x0043d5a0` | `CPhysicsComponentValueLeaf__shared_scalar_deleting_dtor` | Calls `CPhysicsComponentValue__dtor_base`, then uses the same `CDXMemoryManager__Free` optional-free path. |

## Reviewed Context

| Group | Static evidence |
| --- | --- |
| Value-list wrappers | `CPhysicsUnitValueList__scalar_deleting_dtor`, `CPhysicsWeaponValueList__scalar_deleting_dtor`, `CPhysicsWeaponModeValueList__scalar_deleting_dtor`, and `CPhysicsRoundValueList__scalar_deleting_dtor` already had Wave1040 `CDXMemoryManager__Free` wording and remain coherent. |
| Registry helpers | `CComponentStatement__CreateAndRegisterByName`, `CFeatureStatement__CreateAndRegisterByName`, and `CHazardStatement__CreateAndRegisterByName` remain bounded default-record constructors/registrars for `DAT_00855400`, `DAT_00855404`, and `DAT_00855408`. |
| Base destructors | `CPhysicsUnitValue__dtor_base`, `CPhysicsWeaponValue__dtor_base`, `CPhysicsRoundValue__dtor_base`, `CPhysicsSpawnerValue__dtor_base`, `CPhysicsExplosionValue__dtor_base`, `CPhysicsFeatureValue__dtor_base`, `CPhysicsHazardValue__dtor_base`, and `CPhysicsComponentValue__dtor_base` remain base-vtable restore bodies. |
| Helper metadata | `0x00549220 CDXMemoryManager__Free` has signature `void __thiscall CDXMemoryManager__Free(void * this, void * mem)` and is the observed free helper, not object-id freeing. |

## Mutation Summary

Dry/apply/final-dry sequence:

- Dry: `updated=0 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=6 tags_added=41 missing=0 bad=0`.
- Apply: `updated=6 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=6 tags_added=41 missing=0 bad=0`, with `REPORT: Save succeeded`.
- Final dry: `updated=0 skipped=6 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=0 missing=0 bad=0`.

No rename, signature change, function-boundary change, executable-byte change, BEA launch, installed-game mutation, save mutation, or runtime-file mutation occurred.

## Boundary

This wave strengthens the PhysicsScript lifetime static contract needed for rebuild-grade static contracts and a future clean-room implementation aiming at no noticeable difference from the original game. It does not prove runtime PhysicsScript behavior, serialized file-format completeness, exact statement/value-list/concrete record layouts, exact source-body identity, mission/resource-script outcomes, BEA patching behavior, visual QA, gameplay outcomes, rebuild parity, or no-noticeable-difference parity.

Probe token anchor: Wave1183; wave1183-physics-value-list-lifetime-current-risk-review; 779/1179 = 66.07%; 21 PhysicsScript value-list/registry/lifetime current-risk rows; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 400; current risk candidates: 6166; fresh Ghidra export; comment/tag correction; updated=6 skipped=0; comment_only_updated=6; tags_added=41; final dry updated=0 skipped=6; no rename; no signature change; no function-boundary change; no executable-byte change; Codex read-only consults used; one consult recommended four value-list rows; second consult recommended widened 21-row PhysicsScript slice; Codex root final judgment; no Cursor/Composer; PhysicsScript value-list; registry; value-lifetime; CDXMemoryManager__Free; DAT_009c3df0; 0x00549220; not OID__FreeObject; stale OID wording corrected; 0 / 0 / 0; 6411/6411 = 100.00%; 120 xref rows; 404 instruction rows; 21 decompile rows; CPhysicsUnitValueList__scalar_deleting_dtor; CPhysicsRoundValueLeaf__shared_scalar_deleting_dtor; CPhysicsSpawnerValueLeaf__shared_scalar_deleting_dtor; CPhysicsExplosionValueLeaf__shared_scalar_deleting_dtor; CPhysicsFeatureValueLeaf__shared_scalar_deleting_dtor; CPhysicsHazardValueLeaf__shared_scalar_deleting_dtor; CPhysicsComponentValueLeaf__shared_scalar_deleting_dtor; CComponentStatement__CreateAndRegisterByName; CFeatureStatement__CreateAndRegisterByName; CHazardStatement__CreateAndRegisterByName; G:\GhidraBackups\BEA_20260606-123452_post_wave1183_physics_value_list_lifetime_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction; rebuild-grade static contracts; no noticeable difference.
