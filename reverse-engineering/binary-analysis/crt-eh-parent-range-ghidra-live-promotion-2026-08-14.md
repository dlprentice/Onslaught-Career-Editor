# CRT EH parent-range Ghidra live promotion

Status: reviewed completed live/tracked structural promotion
Last updated: 2026-08-14
Evidence: MEASURED — pristine bytes, two saved scratch replicas, separate live
PRE/apply/POST processes, full function and program inventories, exact
live/tracked/backup project manifests, retained read-only restore probes, and a
read-only body-range/call-graph export; UNKNOWN — original source naming,
runtime execution, broader EH semantics, semantic grade, and rebuild parity.
Verdict: the 25-byte filter/handler interval at `0x005D0AD6..0x005D0AEF`
is now owned by existing parent `CRT__LongJmpProbe_NoOp` at `0x005D0A9F`.
Function count stays 8,327, exact body ranges fall from 8,458 to 8,457, and
saved `.text` ownership rises from 1,811,418 to 1,811,443 bytes. No function
was created at `0x005D0AD6` or `0x005D0AEA`.
Specimen: pristine Steam `BEA.exe`, 2,506,752 bytes, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Machine-local authority:
`local-lab/ghidra-crt-eh-parent-range-live-authority-20260814-v1/live-promotion.ready.json`,
25,937 bytes, SHA-256
`295b6168601e09a6d97bc1c712b5d33b5fff894c115668c7561ac05f05c6afc9`.

## Exact structural result

The promoted function keeps its entry, name, metadata, and terminal end. Its
two PRE components become one contiguous POST component:

| Measure | PRE | POST | Delta |
| --- | ---: | ---: | ---: |
| Functions | 8,327 | 8,327 | 0 |
| Exact body ranges | 8,458 | 8,457 | -1 |
| Multi-range functions | 77 | 76 | -1 |
| Owned `.text` bytes | 1,811,418 | 1,811,443 | +25 |
| `.text` ownership | 93.898814846% | 93.900110776% | +0.001295930 points |
| Unowned `.text` bytes | 117,699 | 117,674 | -25 |
| Instructions | 551,133 | 551,143 | +10 |
| References | 234,478 | 234,478 | 0 |

The POST body is exactly `[0x005D0A9F,0x005D0B04)`, 101 bytes, SHA-256
`50016632446f1259b35479440c4a14ca82c8ac59a6c4f78a34f146bd119b61c3`.
The inserted interval has ten completely decoded instructions and SHA-256
`e4be71ffc2e3b62db42a6ae7cedc791eaeb8f7c8c05e986bf0ece195613f414a`.
The exact source/handler-table relationship and negative-entry evidence remain
owned by the preceding
[scratch admission](crt-eh-parent-range-ghidra-scratch-admission-2026-08-14.md).

The separate POST function inventory is 7,192,981 bytes, SHA-256
`08886e03b846668681301f0f2ec2ba9ac1af0463faa1835c57abe9e717ebd866`.
All 8,326 non-target rows are byte-identical. Only `0x005D0A9F` changes, and
only its body-byte count, body-range count, body digest, and instruction count
change. The POST program inventory is 1,267 bytes, SHA-256
`e77082ead314ccb44ba070a7b42222e063ec1078d22ab2203fa6ee8968f99909`.
Program bytes, defined data, stored non-function symbols, comments, and
references remain exact; only instruction count/layout and undefined-data
accounting move.

## Recovery and project identity

The ceremony used one writable live apply between read-only PRE and separate
read-only POST processes. PRE and POST were each copied to distinct off-volume
backups and independently reopened read-only. Tracked Ghidra remained exact PRE
until the POST backup and restore proof completed, then was refreshed and
independently copied/reopened again.

Live, tracked, POST backup, and retained POST restore copies are exact 19-file /
187,009,925-byte twins. Their canonical inventory SHA-256 is
`a7916b5642b808f468ef113e731a4cfcf225287c94264009fde1034edd9b91cf`.
The physical transition removes only `db.18615.gbf`, adds only
`db.18617.gbf`, and changes no common file. Stable `db.18616.gbf` remains
68,354,048 bytes / SHA-256
`f0d4988cfa1f36529ed3687816e231bfcc8323240e7d3f9837de48941b8f64fc`;
new `db.18617.gbf` is 68,354,048 bytes / SHA-256
`52cedb3555f418ea8000b0f8bb4c14cddc8c88954b3a5f3104e7600c487b52b0`.

The mechanical 8,327-row name projection is 510,431 bytes / SHA-256
`64c87111651ad37437be96ce3712abe6fafb762f0e545393c8dc65f8ac583669`.
The exact POST body-range export is 1,205,601 bytes / SHA-256
`45e9521e8145c506842767604f10c04fdb0087ad199859207736e5e7d58bdbce`.
The direct-call export remains byte-identical at 1,397,680 bytes / SHA-256
`159f7c89aae54df927186d71263941b5f0857debe09556097820f098da8fa9d8`,
14,598 edges, and 27,244 call sites.

## Current ownership and campaign boundary

Two independent offline ownership replays close the current union at
1,811,443 / 1,929,117 bytes with zero overlap. The 117,674-byte remainder is
6,021 runs: 18,922 decoded-instruction bytes outside functions, 46,918 defined-
data bytes, and 51,834 listing-unclassified bytes. This promotes body ownership
only; it does not turn listing state into semantic or runtime proof.

Generation 27 remains the frozen campaign authority on the immediately prior
8,327-row `db.18616` geometry. Its semantic grades and runtime claims remain
valid, but it is no longer the exact physical-geometry mirror. The next valid
campaign action is a Generation 28 reseed on `db.18617`; no frozen Generation
27 reducer or receipt may be rewritten.

## Reproduction and boundary

The aggregate verifier is read-only and should pass twice from the repository
root with the exact live, lane, PRE-backup, POST-backup, and receipt paths named
by the preparation report. It rehashes the complete scratch package, live and
tracked projects, all recovery copies, three process logs, full inventories,
projection, range/call exports, and chronology before emitting
`CRT_EH_PARENT_RANGE_LIVE_AUTHORITY_VERIFIED`.

This promotion proves one structural parent-body repair. It does not recover an
original linker symbol, establish that the parent name is source-exact, prove
the filter or handler executes in retail play, change an ABI or data type, add
a semantic grade, or establish rebuild parity.
