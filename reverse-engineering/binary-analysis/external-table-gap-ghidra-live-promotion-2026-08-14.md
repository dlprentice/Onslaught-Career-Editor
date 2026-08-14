# External-table gap Ghidra live promotion

Status: **live promoted, separately read back, recoverably backed up, and
refreshed into the tracked Ghidra snapshot**
Date: 2026-08-14
Verdict: **79 exact body sets admitted; structural census 8,201 -> 8,280**
Evidence: MEASURED — sealed scratch replay, two fresh disposable replicas,
live dry/apply/separate readback, full function and program inventories, exact
project-tree comparison, retained PRE/POST/tracked restore probes, a durable
tracked-still-PRE inspection, and mechanical name projection; UNKNOWN —
original linker names and signatures, runtime reachability, and reconstruction
parity.

Specimen: pristine PC retail `BEA.exe`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.

## Promoted result

The 79 bodies in
[`external-table-gap-function-boundaries-2026-08-13.tsv`](external-table-gap-function-boundaries-2026-08-13.tsv)
are now saved as default `FUN_*` functions in live Ghidra and the tracked
canonical snapshot. The 30,020-byte manifest has SHA-256
`4293ebb936639299301985f128728b127ca60014693871a981d2324d47f2044f`.
Its admitted bodies are pairwise disjoint and contain 9,234 bytes.

| Measurement | PRE | POST | Delta |
| --- | ---: | ---: | ---: |
| Internal functions | 8,201 | 8,280 | +79 |
| Listing instructions | 550,982 | 550,991 | +9 |
| References | 234,537 | 234,495 | -42 |
| Defined-data items | 48,585 | 48,585 | 0 |
| Undefined-data items | 3,908,592 | 3,908,482 | -110 |
| User-defined symbols | 6,104 | 6,104 | 0 |
| Analysis symbols | 18,006 | 18,006 | 0 |
| Imported symbols | 907 | 907 | 0 |
| Other/default symbols | 61,686 | 61,684 | -2 |
| Comments | 9,199 | 9,199 | 0 |

Every byte of every exported field for all 8,201 PRE function rows is
unchanged. The POST-only address set is exactly the 79 manifest entries, and
all 79 new rows are byte-identical to the independently sealed scratch
readback. The full inventory diff records 79 created functions and zero
destroyed, renamed, re-bounded, retyped, re-signatured, calling-convention,
no-return, instruction-count, or thunk changes. Program bytes, defined data,
stored non-function symbols, comments, and relocations are unchanged. The
instruction, reference, undefined-data, and default-symbol deltas above are the
exact sealed consequence of turning already listed/table-referenced regions
into functions; they must not be restated as simple positive growth.

| Artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| PRE/dry full functions | 7,109,943 | `2cc0b74f9284a3d6d59effa857cb6766bb78b08d50a7896d0dda8631f7c93314` |
| PRE/dry program | 1,267 | `be169e6bae9bbd32c822a70c180e43960336fd85ee8ad52f5f494090c0a1e636` |
| Dry boundaries | 21,022 | `a09a264de05e7394384eac466ad8ab1357252e1bd2c663a8ee7858db39462594` |
| Apply boundaries | 29,018 | `97db9f391eb4a42a6a5f192ed37dfe3f29bdf6229c3437f17b1bd787a6007592` |
| Readback boundaries | 29,097 | `2f4b23ac985f55562a1897dc3d4163bd546b8b752c1c302e7d35f1d6ae365eb9` |
| POST full functions | 7,161,942 | `c3942b9e340cef71b731290b845843697af5c53204449c51949b779e896272d6` |
| POST program | 1,267 | `3e51ce1d5e926c632869b2058c9d89e91f48345a329a724ea9520570bd91212d` |
| Inventory diff | 14,160 | `02da186a4efa0824344e10aa603a52a0deec7623ba8f4fde263498596d7ddd9c` |

The nine run directories contain exactly one writable live process and one
successful live save, both in `live-apply`. Every other live phase is
read-only. Two fresh disposable copies completed dry/apply/separate readback
first and exported byte-identical full POST function and program inventories.
Their rolling database serialization is not claimed byte-identical; the
semantic exports and exact non-rolling project files are the replica equality
layer.

## Recovery and tracked identity

The PRE recovery contains 19 files and 186,911,621 bytes. The POST recovery,
live project, and tracked snapshot are raw-file-identical at 19 files and
186,960,773 bytes. Their relative-path-ordered
`sha256<TAB>bytes<TAB>path<LF>` inventory SHA-256 is
`ae422079966978ec2f8f5b951b0ef5812b1074bd708ab8d782179f51c90efcf2`.

The only project-tree transition is removal of `db.18611.gbf` and addition of
`db.18613.gbf`; every common file is byte-identical. The stable
`db.18612.gbf` remains 68,321,280 bytes with SHA-256
`424775377ea0f40d9e429c9219b9310d427760acc40548dbc588ca285f932f7b`.
The new rolling `db.18613.gbf` is 68,337,664 bytes with SHA-256
`615497847b0c732077ee7164b0973b9012092523e9ad99b91c21781952420ebe`.

Fresh PRE, POST, and tracked-snapshot restore copies are retained. Each copy
matches its source recursively, reopens read-only as the exact pristine retail
program, and remains byte-stable after opening. PRE observes 8,425 aggregate
Ghidra functions; POST and tracked restore probes observe 8,504, including the
same 224 external/import functions. A separate exact-root inspection proves
tracked remained PRE after POST recovery and before the tracked refresh.

## Projection and aggregate authority

The tracked
[`ghidra-function-name-table-2026-08-13.tsv`](ghidra-function-name-table-2026-08-13.tsv)
is mechanically rebuilt from the exact POST full inventory. It contains 8,280
internal rows, is 508,242 bytes, and has SHA-256
`6e22a93a4792a2b5a9a6109a65e3b6460dc1ef6dc0606cc195a9a50e30ebdd68`.

[`ghidra_external_table_gap_boundary_live_authority.py`](../../tools/ghidra_external_table_gap_boundary_live_authority.py)
is the bounded read-only aggregate verifier. It re-runs the scratch authority,
re-parses every target and all PRE rows, proves the exact nine-run topology and
one save, hashes live/tracked/backup projects, checks exact execution roots and
restore commands, validates retained restores and chronology, and regenerates
the projection in memory. It never launches Ghidra. Its only write is
create-new publication of the named ignored JSON receipt.

The aggregate receipt is
`local-lab/ghidra-external-table-gap-boundary-live-authority-20260814-v1/live-promotion.ready.json`,
38,280 bytes, SHA-256
`48ca86cf8d86e0541a202cda0154504aa7cd59ab6bbd653364f0cbf762b63a00`.
The authority tool is 68,053 bytes, SHA-256
`70967434fa6138cfc29fc5cb469b47ac62475d28c3075078b2e7919d19ba9396`.
Use its `verify` mode to reproduce the existing receipt; `seal` is historical
and refuses overwrite.

## Evidence boundary

This promotion proves exact function boundaries and persisted structural
ownership. The `FUN_*` labels remain Ghidra defaults, not recovered original
symbols. The ranked provider evidence in the boundary owner remains separate:
this ceremony does not promote compatibility labels into original names,
signatures, runtime causality, or reconstruction parity. Generation 23 and
simulation behavior are unchanged by this structural admission.
