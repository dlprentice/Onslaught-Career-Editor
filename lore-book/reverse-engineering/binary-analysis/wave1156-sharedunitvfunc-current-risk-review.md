# Wave1156 SharedUnitVFunc Current-Risk Review

Wave1156 (`wave1156-sharedunitvfunc-current-risk-review`) accounts for `29 SharedUnitVFunc current-risk rows` from the Wave1108 current focused denominator. It is a fresh Ghidra read-only review with no mutation.

Probe token anchor: Wave1156; wave1156-sharedunitvfunc-current-risk-review; 453/1179 = 38.42%; 29 SharedUnitVFunc current-risk rows; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 726; current risk candidates: 6166; fresh Ghidra export; read-only review; no mutation; Codex read-only consults used; 0 / 0 / 0; 6411/6411 = 100.00%; 951 DATA xrefs; 442 instruction rows; wave1083-readback-verified=6; wave1085-readback-verified=23; SharedUnitVFunc__WriteVector1cMinus8cToOut_00401550; SharedUnitVFunc__TestField17c19cReadiness_004fd440; SharedUnitVFunc__CopySourceVectors114120AndRefresh_004fe4a0; SharedUnitVFunc__ForwardField208Slot10_004fce00; SharedUnitVFunc__TestField17cEntryNameMatch_004fe310; [maintainer-local-ghidra-backup-root]\BEA_20260605-231547_post_wave1156_sharedunitvfunc_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction.

## Evidence

Fresh primary exports verified `29` metadata rows, `29` tag rows, `951 DATA xrefs`, `442 instruction rows`, and `29` decompile rows. The provenance tag split is `wave1083-readback-verified=6` and `wave1085-readback-verified=23`. The verified Ghidra project backup is `[maintainer-local-ghidra-backup-root]\BEA_20260605-231547_post_wave1156_sharedunitvfunc_current_risk_review_verified` from the local Ghidra project root, with `19` files, `175967111` bytes, `DiffCount=0`, and `HashDiffCount=0`.

| Address | Current name | Static evidence |
| --- | --- | --- |
| `0x00401550` | `SharedUnitVFunc__WriteVector1cMinus8cToOut_00401550` | Wave1085 row; writes a three-float delta from `this+0x1c/0x20/0x24` minus `this+0x8c/0x90/0x94` into the caller output vector. |
| `0x00401900` | `SharedUnitVFunc__ForwardArgToThingBridge_00401900` | Wave1085 row; forwards one stack argument to the shared thing bridge helper. |
| `0x00401910` | `SharedUnitVFunc__CopyTransformAndNotify_00401910` | Wave1085 row; copies a caller block into `this+0x8c`, refreshes, and optionally dispatches through a nested virtual slot. |
| `0x00405d90` | `SharedUnitVFunc__ReturnField130ColorMask_00405d90` | Wave1083 row; returns one of two packed color/mask constants based on `this+0x130`. |
| `0x00405de0` through `0x00405e70` | `SharedUnitVFunc__TestField168Or214OrFlag2c_00405de0` and adjacent field helpers | Wave1083/Wave1085 rows; boolean/field setters and accessors for `0x168`, `0x214`, `0x2c`, `0x1f0`, `0x15c`, and `0x210` contexts. |
| `0x004175c0` through `0x00417630` | `SharedUnitVFunc__ReturnField164FloatF4_004175c0` through `SharedUnitVFunc__ReturnObject114OrOne_00417630` | Wave1083/Wave1085 rows; field `0x164` float/int accessors plus `field13c` and object `0x114` bounded return helpers. |
| `0x004f9220` | `SharedUnitVFunc__CountNestedThingListAndDispatch_004f9220` | Wave1085 row; counts nested list entries from an argument-side field and dispatches through a shared helper. |
| `0x004f9a10` | `SharedUnitVFunc__ReturnField178Or164C0Float_004f9a10` | Wave1085 row; field `0x178` tail-call path or `0x164+0xc0` float fallback. |
| `0x004fb270` | `SharedUnitVFunc__ReturnField114Float_004fb270` | Wave1085 row; bounded float return from `this+0x114`. |
| `0x004fce00` | `SharedUnitVFunc__ForwardField208Slot10_004fce00` | Wave1085 row; forwards five stack arguments through `this+0x208` slot `+0x10` when present. |
| `0x004fd440` | `SharedUnitVFunc__TestField17c19cReadiness_004fd440` | Wave1085 row; walks `this+0x17c`/`this+0x19c` style member lists and returns a boolean-style readiness result. |
| `0x004fda90`, `0x004fdc90`, `0x004fdd60`, `0x004fe310` | field/list/name predicates and propagators | Wave1083/Wave1085 rows; active-member search, field13c mode test, name propagation to `0x18c`/`0x19c`, and entry-name match predicate. |
| `0x004fe4a0`, `0x004fe5c0` | source-vector refresh and scaled float helper | Wave1083/Wave1085 rows; source-vector sampling/copy/refresh and mode-scaled `0x164+0xb4` float access. |

## Boundary

This wave proves fresh static Ghidra read-back coherence for the selected shared unit-family vfunc rows only. Runtime shared-unit vfunc behavior, exact source virtual names, exact concrete layouts, runtime targeting/movement/render/name-propagation behavior, BEA patching behavior, gameplay outcomes, visual QA, and rebuild parity remain separate proof.
