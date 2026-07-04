# Wave1112 CAnimal Wave1016 Current-Risk Supersession

Status: complete static supersession accounting
Last updated: 2026-06-04
Scope: `wave1112-animal-wave1016-current-risk-supersession`

Wave1112 accounts for `3 rows` from the Wave1108 current focused denominator as already covered by Wave1016 `animal-init-dtor-review-wave1016` static evidence. This is no new Ghidra export, no mutation, no executable-byte change, no BEA launch, and no installed-game/runtime-file mutation.

## Accounting

| Track | Current |
| --- | ---: |
| Static Ghidra function-quality closure | `6410/6410 = 100.00%` |
| Commentless / exact-undefined / `param_N` debt | `0 / 0 / 0` |
| Expanded post-100 static surface | `1560/1560 = 100.00%` |
| Wave1108 current focused candidates | current focused candidates: 1179 |
| Wave1112 current focused supersession accounting | `28/1179 = 2.37%` |

## Superseded Rows

| Address | Saved row | Prior evidence |
| --- | --- | --- |
| `0x00403d30` | `CAnimal__Init` | Wave1016 re-read vtable slot 9, init transform/model/resource setup, `0x00622d48 bird.msh`, `CComplexThing__Init`, animal-list link, and event 3000 scheduling evidence. |
| `0x00404010` | `CAnimal__dtor_base` | Wave1016 re-read the destructor-base body, vtable `0x005d8698`, `DAT_00660130`/`DAT_00660134` animal-list clearing, and `CComplexThing__dtor_base` delegation. |
| `0x004041f0` | `CAnimal__scalar_deleting_dtor` | Wave1016 re-read vtable slot 1, the call to `CAnimal__dtor_base`, optional free when `flags&1`, and return-this behavior. |

Wave1016 verified `3` target metadata rows, `3` tag rows, `3` xref rows, `195` body-instruction rows, and `3` decompile rows. Context exports verified `32` metadata rows, `637` xref rows, `1292` body-instruction rows, and `32` decompile rows. Additional evidence verified `69` CAnimal vtable slots from `0x005d8698`, `14` data-xref rows, `3` scalar-reference rows, and direct strings `0x00622d48 bird.msh`, `0x00622d1c Warning! Unknown animal type %d generated!\x0a`, and `0x00622d70 CAnimal`.

Wave1016 backup: `[maintainer-local-ghidra-backup-root]\BEA_20260531-195306_post_wave1016_animal_init_dtor_review_verified`.

Latest completed Ghidra review backup remains `[maintainer-local-ghidra-backup-root]\BEA_20260604-200748_post_wave1100_cmeshpart_load_geometry_review_verified`.

Probe token anchor: Wave1112; wave1112-animal-wave1016-current-risk-supersession; 28/1179 = 2.37%; 3 rows; current focused candidates: 1179; Wave1016; animal-init-dtor-review-wave1016; 0x00403d30 CAnimal__Init; 0x00404010 CAnimal__dtor_base; 0x004041f0 CAnimal__scalar_deleting_dtor; 0x005d8698; 0x00622d48 bird.msh; 0x00622d1c Warning! Unknown animal type; 0x00622d70 CAnimal; [maintainer-local-ghidra-backup-root]\BEA_20260531-195306_post_wave1016_animal_init_dtor_review_verified; [maintainer-local-ghidra-backup-root]\BEA_20260604-200748_post_wave1100_cmeshpart_load_geometry_review_verified; no new Ghidra export; no mutation.

## Boundary

This wave closes current-risk accounting for these three rows only. It does not prove exact source virtual names, concrete `CAnimal`/`CAnimalInitThing`/resource-descriptor/list layouts, runtime animal behavior, runtime event scheduling, BEA patching behavior, gameplay outcomes, visual QA, or rebuild parity.
