# Wave1112 CAnimal Wave1016 Current-Risk Supersession Readiness

Status: complete static supersession accounting
Date: 2026-06-04
Scope: `wave1112-animal-wave1016-current-risk-supersession`

Wave1112 accounts for `3 rows` from the Wave1108 current focused denominator:

| Address | Saved row | Evidence |
| --- | --- | --- |
| `0x00403d30` | `CAnimal__Init` | Wave1016 `animal-init-dtor-review-wave1016` re-read the saved row, vtable slot 9, model/resource setup, `0x00622d48 bird.msh`, list linkage, and event 3000 scheduling evidence. |
| `0x00404010` | `CAnimal__dtor_base` | Wave1016 re-read vtable `0x005d8698`, animal-list clearing through `DAT_00660130`/`DAT_00660134`, and `CComplexThing__dtor_base` delegation. |
| `0x004041f0` | `CAnimal__scalar_deleting_dtor` | Wave1016 re-read vtable slot 1, the call to `CAnimal__dtor_base`, optional free when `flags&1`, and return-this behavior. |

Static read-back anchors:

- Current focused accounting after Wave1112: `28/1179 = 2.37%` of current focused candidates: 1179.
- Current static Ghidra function-quality closure remains `6410/6410 = 100.00%` with `0 / 0 / 0` commentless / exact-undefined / `param_N` debt.
- Wave1016 target exports verified `3` metadata rows, `3` tag rows, `3` xref rows, `195` body-instruction rows, and `3` decompile rows.
- Wave1016 context exports verified `32` metadata rows, `637` xref rows, `1292` body-instruction rows, and `32` decompile rows.
- CAnimal vtable export verified `69` slots from `0x005d8698`, including slot 1 to `0x004041f0 CAnimal__scalar_deleting_dtor` and slot 9 to `0x00403d30 CAnimal__Init`.
- Direct string/data evidence includes `0x00622d48 bird.msh`, `0x00622d1c Warning! Unknown animal type %d generated!\x0a`, and `0x00622d70 CAnimal`.
- Wave1016 backup: `G:\GhidraBackups\BEA_20260531-195306_post_wave1016_animal_init_dtor_review_verified`.
- Latest completed Ghidra review backup remains `G:\GhidraBackups\BEA_20260604-200748_post_wave1100_cmeshpart_load_geometry_review_verified`.
- Mutation status: no new Ghidra export, no mutation, no executable-byte change, no BEA launch, and no installed-game/runtime-file mutation.

Probe token anchor: Wave1112; wave1112-animal-wave1016-current-risk-supersession; 28/1179 = 2.37%; 3 rows; current focused candidates: 1179; Wave1016; animal-init-dtor-review-wave1016; 0x00403d30 CAnimal__Init; 0x00404010 CAnimal__dtor_base; 0x004041f0 CAnimal__scalar_deleting_dtor; 0x005d8698; 0x00622d48 bird.msh; 0x00622d1c Warning! Unknown animal type; 0x00622d70 CAnimal; G:\GhidraBackups\BEA_20260531-195306_post_wave1016_animal_init_dtor_review_verified; G:\GhidraBackups\BEA_20260604-200748_post_wave1100_cmeshpart_load_geometry_review_verified; no new Ghidra export; no mutation.

## Boundary

This is static supersession accounting only. Exact source virtual names, concrete `CAnimal`/`CAnimalInitThing`/resource-descriptor/list layouts, runtime animal behavior, runtime event scheduling, BEA patching behavior, gameplay outcomes, visual QA, and rebuild parity remain separate proof.
