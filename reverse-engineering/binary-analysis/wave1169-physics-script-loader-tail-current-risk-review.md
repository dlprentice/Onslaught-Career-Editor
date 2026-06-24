# Wave1169 PhysicsScript Loader Tail Current-Risk Review

Status: complete static read-only evidence validated
Date: 2026-06-06
Tag: `wave1169-physics-script-loader-tail-current-risk-review`

Wave1169 accounts for `12 PhysicsScript loader tail current-risk rows` from the `wave1108-current-risk-rank` current-risk denominator with fresh Ghidra export evidence. It is a read-only review with no mutation, no rename, no signature change, no comment/tag change, no function-boundary change, no executable-byte change, no BEA launch, no installed-game mutation, no save mutation, and no runtime-file mutation. Codex read-only consult used; no Cursor/Composer used.

This is current-risk accounting with fresh read-back, not new discovery. Wave1043 already consolidated the broader eighteen-row statement/value-list load contract; Wave1169 revalidates the round, spawner, explosion, component, feature, and hazard tail pairs against the current Wave1108 denominator.

| Address | Static read-back evidence |
| --- | --- |
| `0x00430210 CRoundStatement__LoadFromMemBuffer` | DATA vtable ref `0x005d9848`; reads statement name, creates `CPhysicsRoundValueList`, dispatches type-5 children or skips unknown payload bytes. |
| `0x00430330 CPhysicsRoundValueList__LoadFromMemBuffer` | Recursive value-list loader with four call xrefs from round statement/list recursion. |
| `0x004306e0 CSpawnerStatement__LoadFromMemBuffer` | DATA vtable ref `0x005d9834`; creates `CPhysicsSpawnerValueList` and dispatches type-6 children. |
| `0x00430800 CPhysicsSpawnerValueList__LoadFromMemBuffer` | Recursive value-list loader with four call xrefs from spawner statement/list recursion. |
| `0x00430b60 CExplosionStatement__LoadFromMemBuffer` | DATA vtable ref `0x005d9820`; creates `CPhysicsExplosionValueList` and dispatches type-7 children. |
| `0x00430c80 CPhysicsExplosionValueList__LoadFromMemBuffer` | Recursive value-list loader with four call xrefs from explosion statement/list recursion. |
| `0x00431050 CComponentStatement__LoadFromMemBuffer` | DATA vtable ref `0x005d980c`; creates `CPhysicsComponentValueList` and dispatches type-10 children. |
| `0x00431170 CPhysicsComponentValueList__LoadFromMemBuffer` | Recursive value-list loader with four call xrefs from component statement/list recursion. |
| `0x004314a0 CFeatureStatement__LoadFromMemBuffer` | DATA vtable ref `0x005d97f8`; creates `CPhysicsFeatureValueList` and dispatches type-8 children. |
| `0x004315c0 CPhysicsFeatureValueList__LoadFromMemBuffer` | Recursive value-list loader with four call xrefs from feature statement/list recursion. |
| `0x004318f0 CHazardStatement__LoadFromMemBuffer` | DATA vtable ref `0x005d97e4`; creates `CPhysicsHazardValueList` and dispatches type-9 children. |
| `0x00431a10 CPhysicsHazardValueList__LoadFromMemBuffer` | Recursive value-list loader with four call xrefs from hazard statement/list recursion. |

Evidence counts:

- `12` metadata rows.
- `12` tag rows.
- `30` xref rows.
- `1134` instruction rows.
- `12` decompile rows.
- Verified backup: `G:\GhidraBackups\BEA_20260606-055200_post_wave1169_physics_script_loader_tail_current_risk_review_verified`, `19` files, `176065415` bytes, `DiffCount=0`, `HashDiffCount=0`.

Accounting:

- Static closure remains `6411/6411 = 100.00%` with static debt `0 / 0 / 0`.
- Expanded post-100 static surface remains `1560/1560 = 100.00%`.
- Wave911 focused is historical-retired/non-reconstructable at `812/1408 = 57.67%`.
- Wave911 top-500 remains `500/500 = 100.00%`.
- Wave1108 current focused accounting is now `660/1179 = 55.98%`.
- Current risk candidates: 6166.
- Current focused candidates: 1178.
- Live regenerated current focused candidates: 1178.
- Remaining active focused work: 519.
- Focused threshold `15`.
- Not Wave911 reconstruction.

Boundary:

- This wave revalidates the current-risk accounting for a Wave1043-covered load-contract tail. It does not claim new source identity or new parser semantics.
- Runtime PhysicsScript behavior, serialized file-format completeness, runtime round/spawner/explosion/component/feature/hazard behavior, exact statement/value-list concrete layouts, exact source-body identity, BEA patching behavior, visual QA, gameplay outcomes, and rebuild parity remain separate proof.

Probe token anchor: Wave1169; wave1169-physics-script-loader-tail-current-risk-review; 660/1179 = 55.98%; 12 PhysicsScript loader tail current-risk rows; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 519; current risk candidates: 6166; fresh Ghidra export; read-only review; no mutation; Codex read-only consult used; 0 / 0 / 0; 6411/6411 = 100.00%; 30 xref rows; 1134 instruction rows; CRoundStatement__LoadFromMemBuffer; CPhysicsRoundValueList__LoadFromMemBuffer; CSpawnerStatement__LoadFromMemBuffer; CPhysicsSpawnerValueList__LoadFromMemBuffer; CExplosionStatement__LoadFromMemBuffer; CPhysicsExplosionValueList__LoadFromMemBuffer; CComponentStatement__LoadFromMemBuffer; CPhysicsComponentValueList__LoadFromMemBuffer; CFeatureStatement__LoadFromMemBuffer; CPhysicsFeatureValueList__LoadFromMemBuffer; CHazardStatement__LoadFromMemBuffer; CPhysicsHazardValueList__LoadFromMemBuffer; Wave1043; physics-script-static-contract.md; G:\GhidraBackups\BEA_20260606-055200_post_wave1169_physics_script_loader_tail_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction.
