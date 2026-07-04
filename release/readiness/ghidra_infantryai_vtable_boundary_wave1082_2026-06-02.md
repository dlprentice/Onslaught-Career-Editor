# Ghidra InfantryAI Vtable Boundary Wave1082 Readiness Note

Status: complete static read-back evidence
Date: 2026-06-02
Scope: `infantryai-vtable-boundary-review-wave1082`

Wave1082 recovered and saved eleven previously unresolved AI/vtable function boundaries exposed by the CInfantryAI table at `0x005dbf14` and related CUnitAI-derived tables. The pass created function boundaries, saved conservative names/signatures/comments/tags, and made no executable-byte changes.

Representative anchors:

Probe token anchor: Wave1082; infantryai-vtable-boundary-review-wave1082; 0x004ff330 SharedUnitAI__HandleEventAndMaybeFire_004ff330; 0x0048a030 CInfantryAI__UpdateSupportSelection_0048a030; 0x004f45c0 SharedVFunc__ForwardField64FloatOrZero_004f45c0; 0x005dbf14; 1405/1560 = 90.06%; 812/1408 = 57.67%; 6294/6294 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260602-110925_post_wave1082_infantryai_vtable_boundary_verified.

| Address | Saved name | Evidence |
| --- | --- | --- |
| `0x004ff330` | `SharedUnitAI__HandleEventAndMaybeFire_004ff330` | CInfantryAI slot `0`; broad CUnitAI-derived DATA refs; `RET 0x4` event/control-code shape. |
| `0x004ff4f0` | `SharedUnitAI__UpdateTargetAndAnimationState_004ff4f0` | CInfantryAI slot `4`; linked target/reader and animation-state body before `0x004ff710`. |
| `0x004fea30` | `SharedUnitAI__CheckField24TargetState_004fea30` | CInfantryAI slot `5`; checks `this+0x24`/`this+0x20` target state and returns boolean-style result. |
| `0x004febe0` | `SharedUnitAI__CheckField20TargetMode1_004febe0` | CInfantryAI slot `6`; accepts mode `1` in `this+0x20` and returns boolean-style result. |
| `0x004ffb60` | `SharedUnitAI__TryStartField28TimedEvent_004ffb60` | CInfantryAI slot `7`; writes mode `2`, stores a `DAT_00672fd0` timestamp, and schedules event id `0xbba`. |
| `0x004feac0` | `SharedUnitAI__CheckField24RangeAgainstCandidate_004feac0` | CInfantryAI slot `8`; `RET 0x4` candidate/range gate around `this+0x24`. |
| `0x0048a030` | `CInfantryAI__UpdateSupportSelection_0048a030` | CInfantryAI slot `9`; sole observed DATA xref from `0x005dbf38`; body stops before `CInfantryGuide__ctor`. |
| `0x004ffbb0` | `SharedUnitAI__UpdateField28TargetReaderGate_004ffbb0` | CInfantryAI slot `10`; `RET 0x4` target-reader gate before existing `CSquadNormal__SetReaderAndRefreshSupportSelection`. |
| `0x004ff710` | `SharedUnitAI__CheckField0cCloseTargetGate_004ff710` | CInfantryAI slot `11`; close-target/reader gate before adjacent `0x004ffbb0`. |
| `0x00402d20` | `SharedVFunc__ReturnThis_00402d20` | CInfantryAI slot `17`; two-instruction `return this` shared body. |
| `0x004f45c0` | `SharedVFunc__ForwardField64FloatOrZero_004f45c0` | CInfantryAI slot `55`; returns default zero float if `this+0x64` is null, otherwise tail-jumps to `0x004048c0`. |

Read-back evidence:

- `ApplyInfantryAIVtableBoundaryWave1082.java dry`: `updated=0 skipped=0 created=0 would_create=11 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 bad=0`
- `ApplyInfantryAIVtableBoundaryWave1082.java apply`: `updated=11 skipped=0 created=11 would_create=0 renamed=0 would_rename=0 signature_updated=11 comment_only_updated=0 bad=0`
- `ApplyInfantryAIVtableBoundaryWave1082.java final dry`: `updated=0 skipped=11 created=0 would_create=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 bad=0`
- Pre-state: `11` code pointers had instructions but no function rows; listing-state classified `11` `INSTRUCTION_NO_FUNCTION`, `9` `.rdata` `UNDEFINED`, and `9` `NO_MEMORY_BLOCK` literal/float-like values.
- Post exports: `11` metadata rows, `11` tag rows, `303` xref rows, `1286` body-instruction rows, `11` decompile rows, and `96` CInfantryAI vtable-slot rows.
- Post CInfantryAI vtable-slot export improved from `71` OK / `25` `NO_FUNCTION_AT_POINTER` to `82` OK / `14` `NO_FUNCTION_AT_POINTER`; remaining unresolved slots are `.rdata` cells or no-memory literal/float-like values.
- Queue after Wave1082: `6294` total, `6294` commented, `0` commentless, `0` exact-undefined signatures, `0` `param_N`, strict clean-signature proxy `6294/6294 = 100.00%`.
- Re-audit progress: expanded static surface `1405/1560 = 90.06%`; Wave911 focused remains `812/1408 = 57.67%`; top-500 remains `500/500 = 100.00%`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260602-110925_post_wave1082_infantryai_vtable_boundary_verified`, `19` files, `174787463` bytes, `DiffCount=0`.

What this proves:

- The eleven target addresses are saved function entries in the Ghidra project with conservative names, clean signatures, comments, and `infantryai-vtable-boundary-review-wave1082` / `wave1082-readback-verified` tags.
- The CInfantryAI table at `0x005dbf14` now resolves the eleven code-looking pointers that Wave1081 deliberately left as unresolved boundary candidates.
- The remaining CInfantryAI unresolved entries in this checked range are not proven function pointers by current static evidence.

What remains unproven:

- Exact source virtual names.
- Concrete `CUnitAI`/`CInfantryAI`/reader/vector field layout semantics.
- Runtime AI targeting, firing, support-selection, event scheduling, or animation behavior.
- BEA patching behavior.
- Gameplay outcomes.
- Rebuild parity.
