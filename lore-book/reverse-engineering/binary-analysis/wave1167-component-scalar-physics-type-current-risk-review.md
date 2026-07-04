# Wave1167 Component Scalar / Physics Type Current-Risk Review

Status: complete static read-only evidence pending validation
Date: 2026-06-06
Tag: `wave1167-component-scalar-physics-type-current-risk-review`

Wave1167 re-read twelve active Wave1108 focused rows from the PhysicsScript component scalar and type destructor tail. The saved comments, signatures, and tags remain coherent with Wave343 component value recovery, Wave344 type destructor recovery, and Wave1039 component scalar/flag apply review.

| Address | Name | Static role |
| --- | --- | --- |
| `0x0043ca70` | `CComponentScalarD8__ApplyToComponentByName` | Component scalar apply helper; writes matched component record `+0xd8`. |
| `0x0043cb40` | `CComponentScalarDC__ApplyToComponentByName` | Component scalar apply helper; writes matched component record `+0xdc`. |
| `0x0043cbe0` | `CComponentScalarC0__ApplyToComponentByName` | Component scalar apply helper; writes matched component record `+0xc0`. |
| `0x0043cc80` | `CComponentScalar158__ApplyToComponentByName` | Component scalar apply helper; writes matched component record `+0x158`. |
| `0x0043cd20` | `CComponentScalarB8__ApplyToComponentByName` | Component scalar apply helper; writes matched component record `+0xb8`. |
| `0x0043cdc0` | `CComponentScalarBC__ApplyToComponentByName` | Component scalar apply helper; writes matched component record `+0xbc`. |
| `0x0043d460` | `CComponentScalar160__ApplyToComponentByName` | Component scalar apply helper; writes matched component record `+0x160`. |
| `0x0043ddb0` | `CPhysicsSeekType__dtor_base` | Type-11 seek destructor-base body; restores vtable `0x005dab20`. |
| `0x0043e300` | `CPhysicsBehaviourType__dtor_base` | Type-12 behaviour destructor-base body; restores vtable `0x005dac58`. |
| `0x0043e3c0` | `CPhysicsAlligenceType__dtor_base` | Type-13 alligence destructor-base body; restores vtable `0x005dac88`. |
| `0x0043e530` | `CPhysicsNavMapType__dtor_base` | Type-14 navmap destructor-base body; restores vtable `0x005dacc4`. |
| `0x0043e620` | `CPhysicsStateType__dtor_base` | Type-15 state destructor-base body; restores vtable `0x005dacf4`. |

Evidence counts: `12` metadata rows, `12` tag rows, `12` xref rows, `472` instruction rows, and `12` decompile rows. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260606-050232_post_wave1167_component_scalar_physics_type_current_risk_review_verified` (`19` files, `176065415` bytes, `DiffCount=0`, `HashDiffCount=0`).

Wave1167 is a read-only review with no mutation, no rename, no signature change, no comment/tag change, no function-boundary change, and no executable-byte change. The component scalar rows are DATA-backed by `0x005daac4`, `0x005daab0`, `0x005daa9c`, `0x005daa88`, `0x005daa38`, `0x005daa10`, and `0x005da998`; the destructor rows are called by `CPhysicsSeekTypeLeaf__shared_scalar_deleting_dtor`, `CPhysicsBehaviourTypeLeaf__shared_scalar_deleting_dtor`, `CPhysicsAlligenceTypeLeaf__shared_scalar_deleting_dtor`, `CPhysicsNavMapTypeLeaf__shared_scalar_deleting_dtor`, and `CPhysicsStateTypeLeaf__shared_scalar_deleting_dtor`.

System-map note: this closes a current-risk tail in the static PhysicsScript component scalar/type surface, tying component record scalar offsets (`+0xd8`, `+0xdc`, `+0xc0`, `+0x158`, `+0xb8`, `+0xbc`, `+0x160`) to the existing `DAT_00855400` component registry map and tying type-11 through type-15 destructor-base rows to their scalar-deleting wrapper callers and base vtables.

Current accounting: `636/1179 = 53.94%` Wave1108 current focused reviewed, remaining active focused work: 543, current risk candidates: 6166, current focused candidates: 1178, live regenerated current focused candidates: 1178, focused threshold `15`, not Wave911 reconstruction. Static quality remains `6411/6411 = 100.00%` with `0 / 0 / 0` commentless/exact-undefined/`param_N` debt.

Boundary: static Ghidra coherence only. Runtime PhysicsScript behavior, runtime component scalar behavior, serialized file-format completeness, mission-script outcomes, exact component/type concrete layouts, exact source-body identity, BEA patching behavior, visual QA, gameplay outcomes, and rebuild parity remain separate proof.

Probe token anchor: Wave1167; wave1167-component-scalar-physics-type-current-risk-review; 636/1179 = 53.94%; 12 component scalar / physics type current-risk rows; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 543; current risk candidates: 6166; fresh Ghidra export; read-only review; no mutation; no Wave1167-specific Codex consult; 0 / 0 / 0; 6411/6411 = 100.00%; 12 xref rows; 472 instruction rows; CComponentScalarD8__ApplyToComponentByName; CComponentScalar160__ApplyToComponentByName; CPhysicsSeekType__dtor_base; CPhysicsStateType__dtor_base; DAT_00855400; 0x005daac4; 0x005dacf4; [maintainer-local-ghidra-backup-root]\BEA_20260606-050232_post_wave1167_component_scalar_physics_type_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction.
