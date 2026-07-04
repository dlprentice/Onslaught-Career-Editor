# Wave1183 Physics Value-List Lifetime Current-Risk Readiness Note

Status: complete static current-risk review; saved comment/tag correction; pending artifact commit
Date: 2026-06-06
Scope: `wave1183-physics-value-list-lifetime-current-risk-review`

Wave1183 reviewed `21 PhysicsScript value-list/registry/lifetime current-risk rows` from the `wave1108-current-risk-rank` current-risk denominator with fresh serialized Ghidra exports. It found and corrected a real static comment mismatch in six shared leaf scalar-deleting destructor wrappers: older comments said the optional free path was `OID__FreeObject`, while instruction evidence and helper metadata show `CDXMemoryManager__Free(&DAT_009c3df0, this)` via call `0x00549220`.

Evidence:

- Apply dry: `updated=0 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=6 tags_added=41 missing=0 bad=0`.
- Apply: `updated=6 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=6 tags_added=41 missing=0 bad=0`, with `REPORT: Save succeeded`.
- Final dry: `updated=0 skipped=6 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=0 missing=0 bad=0`.
- Fresh post-correction exports: `21` metadata rows, `21` tag rows, `120 xref rows`, `404 instruction rows`, `21` decompile rows, and `1` helper metadata row for `CDXMemoryManager__Free`.
- Logs: metadata `targets=21 found=21 missing=0`, tags `rows=21 missing=0`, xrefs `Wrote 120 rows`, instructions `Wrote 404 function-body instruction rows`, decompile `targets=21 dumped=21 missing=0 failed=0`, helper metadata `targets=1 found=1 missing=0`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260606-123452_post_wave1183_physics_value_list_lifetime_current_risk_review_verified`, `19` files, `176098183` bytes, `DiffCount=0`, `HashDiffCount=0`.
- Accounting: `779/1179 = 66.07%`, current focused candidates: 1178, live regenerated current focused candidates: 1178, remaining active focused work: 400, current risk candidates: 6166.

Corrected wrappers:

- `CPhysicsRoundValueLeaf__shared_scalar_deleting_dtor`
- `CPhysicsSpawnerValueLeaf__shared_scalar_deleting_dtor`
- `CPhysicsExplosionValueLeaf__shared_scalar_deleting_dtor`
- `CPhysicsFeatureValueLeaf__shared_scalar_deleting_dtor`
- `CPhysicsHazardValueLeaf__shared_scalar_deleting_dtor`
- `CPhysicsComponentValueLeaf__shared_scalar_deleting_dtor`

Reviewed context also included the four Wave1040 value-list scalar-deleting destructors, three PhysicsScript registry create/register helpers, seven base destructor bodies, and `CDXMemoryManager__Free`. Codex read-only consults were used: one consult recommended a four-row value-list slice, a second recommended the widened 21-row PhysicsScript value-list/registry/lifetime slice, and Codex root made the final mutation judgment after live export checks. No Cursor/Composer was used.

Mutation boundary:

- No rename.
- No signature change.
- No function-boundary change.
- No executable-byte change.
- No BEA launch, installed-game mutation, save mutation, or runtime-file mutation.

Static clean-room target: rebuild-grade static contracts for a future clean-room implementation aiming at no noticeable difference.

Not proven here: runtime PhysicsScript behavior, serialized file-format completeness, exact statement/value-list/concrete record layouts, exact source-body identity, mission/resource-script outcomes, BEA patching behavior, visual QA, gameplay outcomes, rebuild parity, or no-noticeable-difference parity.

Probe token anchor: Wave1183; wave1183-physics-value-list-lifetime-current-risk-review; 779/1179 = 66.07%; 21 PhysicsScript value-list/registry/lifetime current-risk rows; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 400; current risk candidates: 6166; fresh Ghidra export; comment/tag correction; updated=6 skipped=0; comment_only_updated=6; tags_added=41; final dry updated=0 skipped=6; no rename; no signature change; no function-boundary change; no executable-byte change; Codex read-only consults used; one consult recommended four value-list rows; second consult recommended widened 21-row PhysicsScript slice; Codex root final judgment; no Cursor/Composer; PhysicsScript value-list; registry; value-lifetime; CDXMemoryManager__Free; DAT_009c3df0; 0x00549220; not OID__FreeObject; stale OID wording corrected; 0 / 0 / 0; 6411/6411 = 100.00%; 120 xref rows; 404 instruction rows; 21 decompile rows; CPhysicsUnitValueList__scalar_deleting_dtor; CPhysicsRoundValueLeaf__shared_scalar_deleting_dtor; CPhysicsSpawnerValueLeaf__shared_scalar_deleting_dtor; CPhysicsExplosionValueLeaf__shared_scalar_deleting_dtor; CPhysicsFeatureValueLeaf__shared_scalar_deleting_dtor; CPhysicsHazardValueLeaf__shared_scalar_deleting_dtor; CPhysicsComponentValueLeaf__shared_scalar_deleting_dtor; CComponentStatement__CreateAndRegisterByName; CFeatureStatement__CreateAndRegisterByName; CHazardStatement__CreateAndRegisterByName; [maintainer-local-ghidra-backup-root]\BEA_20260606-123452_post_wave1183_physics_value_list_lifetime_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction; rebuild-grade static contracts; no noticeable difference.
