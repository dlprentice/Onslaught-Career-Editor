# PC `.text` missing-function Ghidra live promotion

Status: **live promoted, separately read back, recoverably backed up, and
refreshed into the tracked Ghidra snapshot**
Date: 2026-08-14
Verdict: **31 exact body sets admitted; structural census 8,170 -> 8,201**
Evidence: MEASURED — sealed scratch replay, two fresh disposable replicas,
live dry/apply/separate readback, full function and program inventories, exact
project-tree comparison, retained PRE/POST/tracked restore probes, and
mechanical name projection; UNKNOWN — original linker names and signatures,
runtime reachability, and reconstruction parity.

Specimen: pristine PC retail `BEA.exe`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.

## Promoted result

The 31 bodies in
[`text-gap-missing-function-boundaries-2026-08-13.tsv`](text-gap-missing-function-boundaries-2026-08-13.tsv)
are now saved as default `FUN_*` functions in live Ghidra and the tracked
canonical snapshot. The exact 14,930-byte manifest has SHA-256
`afc13e4c56a5598c06872326e05e7e61d535a1271e81943c498303a46ee1a586`.
Its admitted bodies contain 14,049 bytes and 3,895 instructions.

| Measurement | PRE | POST | Delta |
| --- | ---: | ---: | ---: |
| Internal functions | 8,170 | 8,201 | +31 |
| Instructions | 549,872 | 550,982 | +1,110 |
| References | 234,357 | 234,537 | +180 |
| Defined-data items | 48,585 | 48,585 | 0 |
| Undefined-data items | 3,912,345 | 3,908,592 | -3,753 |
| User-defined symbols | 6,104 | 6,104 | 0 |
| Analysis symbols | 18,006 | 18,006 | 0 |
| Imported symbols | 907 | 907 | 0 |
| Default other symbols | 61,594 | 61,686 | +92 |
| Comments | 9,199 | 9,199 | 0 |

Every byte of every exported field for all 8,170 PRE function rows is
unchanged. The POST-only address set is exactly the 31 manifest entries, and
all 31 new rows are byte-identical to the independently sealed scratch
readback. The full inventory diff records 31 created functions and zero
destroyed, renamed, re-bounded, retyped, re-signatured, calling-convention,
no-return, instruction-count, or thunk changes. Program bytes, defined data,
stored non-function symbols, comments, and relocations are unchanged.

The live phase artifacts are exact:

| Artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| PRE/dry full functions | 7,089,535 | `ee3090360bd4f4b68d1ac52c59ab397e7ac37d81c76029d492e2a9d046902f1d` |
| PRE/dry program | 1,267 | `2360923e0fa95648a708ee44297006dee222036662d7b34108d10a1fa405dc02` |
| Dry boundaries | 7,095 | `a02922eb296d7388c1101c926ace46ccd862bb6f92739cca7cdb5c40a82642fe` |
| Apply boundaries | 12,286 | `2898bc62b33e94d1478e7848ff051e71c9a576a3c9df7699f5180c8e321b9ecf` |
| Readback boundaries | 12,317 | `15411a14e5cb011d8c6d28948280d8a8a4bf9f144e8a9859c456e6b5841a8597` |
| POST full functions | 7,109,943 | `2cc0b74f9284a3d6d59effa857cb6766bb78b08d50a7896d0dda8631f7c93314` |
| POST program | 1,267 | `be169e6bae9bbd32c822a70c180e43960336fd85ee8ad52f5f494090c0a1e636` |

The three live logs contain exactly one writable project process and exactly
one successful save, both in `live-apply`. PRE/dry and the separate POST
readback opened the project read-only. Two fresh disposable copies ran the
same dry/apply/readback sequence first; both exported byte-identical POST
function and program inventories. Their serialized rolling database bytes are
not claimed equal to one another—the semantic exports are the applicable
replica equality layer.

## Recovery and tracked project identity

The PRE recovery contains 19 files and 186,813,317 bytes. The POST recovery,
live project, and tracked snapshot are raw-file-identical at 19 files and
186,911,621 bytes. Their relative-path-ordered
`sha256<TAB>bytes<TAB>path<LF>` inventory SHA-256 is
`91776fb4a67579950afc4fb3b48ea8a866733628aecfdae7a2cb918c615fe211`.

The only project-tree path transition is removal of
`db.18610.gbf` and addition of `db.18612.gbf`; every common file is
byte-identical. `db.18611.gbf` remains 68,288,512 bytes with SHA-256
`6f45cdac7ae1f10987280f0ec247e6b5d6dcf866eae79e5982efa78dd68455ce`.
The current rolling `db.18612.gbf` is 68,321,280 bytes with SHA-256
`424775377ea0f40d9e429c9219b9310d427760acc40548dbc588ca285f932f7b`.

Fresh PRE, POST, and tracked-snapshot restore copies are retained. Each copy
matches its source recursively, reopens read-only as the exact pristine retail
program, and remains byte-stable after opening. The PRE probe observes 8,394
total Ghidra functions; POST and tracked probes observe 8,425, including the
same 224 external/import functions in both counts.

## Projection and aggregate authority

The tracked
[`ghidra-function-name-table-2026-08-13.tsv`](ghidra-function-name-table-2026-08-13.tsv)
is mechanically rebuilt from the exact POST full inventory. It contains 8,201
internal rows, is 504,598 bytes, and has SHA-256
`c6084999cefebdb900ec752be5c4cb45ed1d7dcbdd086a53cbd207b91db84d20`.

[`ghidra_text_gap_boundary_live_authority.py`](../../tools/ghidra_text_gap_boundary_live_authority.py)
is the bounded read-only aggregate verifier. It re-runs the sealed scratch
authority, re-parses the exact target rows and whole-program delta, proves one
live save from the logs, hashes current live/tracked/backup projects, checks
restore receipts against retained copies and logs, validates chronology, and
regenerates the projection in memory. It never launches Ghidra. Its only write
is create-new publication of the explicitly named ignored JSON receipt.

The retained aggregate receipt is
`local-lab/ghidra-text-gap-boundary-live-authority-20260814-v2/live-promotion.ready.json`,
36,864 bytes, SHA-256
`0ec30cf8c8b3cd2d3faf1f9dfc37a6f05e5b33bfb5c82fd70bbc359ce4886256`.
It contains only repository-relative POSIX roles; absolute machine paths from
the historical local receipts are validated but never copied into it.

Reproduce the receipt with the verifier's `verify` mode, supplying the current
repository, retained live lane and scratch repository, live project, PRE and
POST backup roots, and the existing aggregate receipt. The verifier refuses an
overlapping output, a non-ignored seal destination, or overwrite.

## Evidence boundary

This promotion proves exact function boundaries and persisted structural
ownership. The `FUN_*` labels remain Ghidra defaults, not recovered original
symbols. The separate
[`text-gap-library-function-classification-2026-08-13.md`](text-gap-library-function-classification-2026-08-13.md)
owns provider-qualified classifications for these bodies; this ceremony does
not promote those classifications into original names, signatures, runtime
causality, or reconstruction parity. Generation 23 and simulation behavior are
unchanged by this structural admission.
