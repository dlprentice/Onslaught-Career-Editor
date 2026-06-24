# Wave1167 Component Scalar / Physics Type Current-Risk Review

Status: complete static read-only evidence pending validation
Date: 2026-06-06
Tag: `wave1167-component-scalar-physics-type-current-risk-review`

Wave1167 re-read twelve active Wave1108 focused rows in the PhysicsScript component scalar and type destructor surface. The saved comments, signatures, and tags still match the prior Wave343/Wave344/1039 evidence.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x0043ca70 CComponentScalarD8__ApplyToComponentByName` | DATA xref `0x005daac4`; walks `DAT_00855400` by `componentName` and writes `this+0x8` to component record `+0xd8`. |
| `0x0043cb40 CComponentScalarDC__ApplyToComponentByName` | DATA xref `0x005daab0`; writes component record `+0xdc`. |
| `0x0043cbe0 CComponentScalarC0__ApplyToComponentByName` | DATA xref `0x005daa9c`; writes component record `+0xc0`. |
| `0x0043cc80 CComponentScalar158__ApplyToComponentByName` | DATA xref `0x005daa88`; writes component record `+0x158`. |
| `0x0043cd20 CComponentScalarB8__ApplyToComponentByName` | DATA xref `0x005daa38`; writes component record `+0xb8`. |
| `0x0043cdc0 CComponentScalarBC__ApplyToComponentByName` | DATA xref `0x005daa10`; writes component record `+0xbc`. |
| `0x0043d460 CComponentScalar160__ApplyToComponentByName` | DATA xref `0x005da998`; writes component record `+0x160`. |
| `0x0043ddb0 CPhysicsSeekType__dtor_base` | Called by `CPhysicsSeekTypeLeaf__shared_scalar_deleting_dtor`; restores vtable `0x005dab20`. |
| `0x0043e300 CPhysicsBehaviourType__dtor_base` | Called by `CPhysicsBehaviourTypeLeaf__shared_scalar_deleting_dtor`; restores vtable `0x005dac58`. |
| `0x0043e3c0 CPhysicsAlligenceType__dtor_base` | Called by `CPhysicsAlligenceTypeLeaf__shared_scalar_deleting_dtor`; restores vtable `0x005dac88`. |
| `0x0043e530 CPhysicsNavMapType__dtor_base` | Called by `CPhysicsNavMapTypeLeaf__shared_scalar_deleting_dtor`; restores vtable `0x005dacc4`. |
| `0x0043e620 CPhysicsStateType__dtor_base` | Called by `CPhysicsStateTypeLeaf__shared_scalar_deleting_dtor`; restores vtable `0x005dacf4`. |

Read-back evidence:

- Fresh exports: `12` metadata rows, `12` tag rows, `12` xref rows, `472` instruction rows, and `12` decompile rows.
- Logs report `targets=12 found=12 missing=0`, `rows=12 missing=0`, `Wrote 12 rows`, `targets=12 missing=0`, and `targets=12 dumped=12 missing=0 failed=0`.
- Verified backup: `G:\GhidraBackups\BEA_20260606-050232_post_wave1167_component_scalar_physics_type_current_risk_review_verified`, `19` files, `176065415` bytes, `DiffCount=0`, `HashDiffCount=0`.
- Accounting after Wave1167: `636/1179 = 53.94%`, remaining active focused work: 543, current risk candidates: 6166, current focused candidates: 1178, live regenerated current focused candidates: 1178, focused threshold `15`, not Wave911 reconstruction.
- Static quality remains `6411/6411 = 100.00%` with `0 / 0 / 0` commentless/exact-undefined/`param_N` debt.
- Probe token anchor: Wave1167; wave1167-component-scalar-physics-type-current-risk-review; 636/1179 = 53.94%; 12 component scalar / physics type current-risk rows; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 543; current risk candidates: 6166; fresh Ghidra export; read-only review; no mutation; no Wave1167-specific Codex consult; 0 / 0 / 0; 6411/6411 = 100.00%; 12 xref rows; 472 instruction rows; CComponentScalarD8__ApplyToComponentByName; CComponentScalar160__ApplyToComponentByName; CPhysicsSeekType__dtor_base; CPhysicsStateType__dtor_base; DAT_00855400; 0x005daac4; 0x005dacf4; G:\GhidraBackups\BEA_20260606-050232_post_wave1167_component_scalar_physics_type_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction.

What this proves:

- The twelve target function rows exist in the saved Ghidra project.
- The saved comments/signatures/tags remain coherent with the prior PhysicsScript component scalar and type destructor evidence.
- The scalar apply rows are DATA-backed by component-value vtable references and write offset-backed fields on records reached through `DAT_00855400`.
- The type destructor rows are reached by scalar-deleting wrapper callers and restore the observed base vtables.

What remains unproven:

- Runtime PhysicsScript behavior.
- Runtime component scalar behavior.
- Serialized file-format completeness.
- Mission-script outcomes.
- Exact component/type concrete layouts.
- Exact source-body identity.
- BEA patching behavior.
- Visual QA, gameplay outcomes, and rebuild parity.
