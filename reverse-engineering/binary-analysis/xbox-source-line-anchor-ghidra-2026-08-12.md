# Xbox source-line anchors promoted into isolated Ghidra projects

Status: complete, bounded historical cross-build Ghidra checkpoint
Last updated: 2026-08-31
Evidence: MEASURED — exact XBE and virtual-image identities, 1,166 unique
Issue-11/US-retail source-coordinate pairs, independent Capstone decoding of
all 2,332 build-specific allocation plates, scratch apply/readback, canonical
apply/readback, stable function censuses, and independently reopened PRE/POST
recovery copies; UNKNOWN — whole-function equivalence, XDK/game-code partition,
runtime behavior, original symbols, and reconstruction parity.
Verdict: the January Issue-11 and US-retail Xbox builds produced isolated,
cold-recoverable Ghidra 12.1.2 databases containing 1,166 exact
instruction-local source mappings each. Ninety-five incomplete or misaligned
Ghidra instruction sites were repaired before the mappings were applied. No
function was added, removed, resized, renamed, or semantically promoted by this
operation.

Specimens:

- Issue-11 `default.xbe`, 2,973,696 bytes, SHA-256
  `ac07835e4b8cf38312e672cb7dc17f28a732abbc05a5e4f1760aaa78a5377ed9`;
  PDB key `3D63DBEB4`.
- US-retail `Default.xbe`, 2,973,696 bytes, SHA-256
  `e8adc9d6940ae1a5fa9fac0fe28e398bfffd01758c2740a536b930c37c83985b`;
  PDB key `3D63DBEB3`.
- Pristine PC retail `BEA.exe`, 2,506,752 bytes, SHA-256
  `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`;
  read only and used only for the 425-row cross-platform join.

## What this settles

The Issue-11 XBE is now an operational near-retail oracle rather than only a
promising file. It shares 1,166 unique `(source basename, line)` allocation
coordinates with US retail. All 2,332 corresponding instruction sites were
decoded independently as contiguous source-line/source-path allocation plates,
then admitted into two separate Ghidra source maps. The same extraction also
retains 425 exact PC/Issue-11/US-retail coordinates covering 93 presently known
PC functions. The tables and Ghidra maps prove only those instruction-local
coordinates.

They do **not** prove that an enclosing function is identical, that its source
name or semantics transfer, that the Issue-11 and retail builds behave alike,
or that either current Ghidra function count is a final denominator. Function
correlation and XDK separation are the next instruments, not conclusions
smuggled into this checkpoint.

## Exact promotion

Fresh Ghidra autoanalysis initially recognized 1,118 of 1,166 Issue-11 anchors
at exact instruction starts; 48 were missing. US retail recognized 1,119; 46
were missing and one was inside a misdecoded instruction. None lay outside
loaded or executable memory. Independent decoding and full-range obstacle
inspection produced exact repair tables of 48 Issue-11 and 47 US-retail sites.

The final scratch copies passed 1,166/1,166 exact-start preflight for both
builds. Only then were the same repair tables and source maps applied to the
canonical isolated projects. Separate-process readback produced:

| Build | Ghidra functions before/after | Instructions before → after | Repaired anchor sites | Source mappings | Source files |
| --- | ---: | ---: | ---: | ---: | ---: |
| Issue 11 | 8,941 / 8,941 | 628,640 → 628,738 | 48 | 1,166 | 139 |
| US retail | 8,942 / 8,942 | 628,495 → 628,583 | 47 | 1,166 | 139 |

The instruction increase reflects complete decoding of the proved repair
ranges; one repaired site can contain multiple instructions. The complete
function-inventory hashes remained byte-identical across the operation:

- Issue 11:
  `f977df8a3db7dac228d45e0a4e1b4f55ccfe6916961aa09d6498cc55e62d6b57`;
- US retail:
  `4c52848496fc266cf4919a9e389335faa46898da799d8e9bd75559be0849e381`.

Those 8,941/8,942 values are Ghidra's current discovery results for these two
Xbox builds. They include platform-specific and library code, may still omit
undiscovered functions, and neither replaces nor caps the separately measured
dated 8,136-function PC-retail inventory. The current PC structural census is
8,170 after a separate 2026-08-13 boundary promotion.

## Backup and readback boundary

Each canonical write had a fresh off-volume backup made immediately before it.
Each resulting project then received a fresh POST backup. Every copy compared
with zero missing, extra, size-different, or hash-different project files and
was reopened read-only. The restored POST copies independently reproduced all
95 instruction repairs and all 2,332 source mappings:

| Build | PRE-anchor backup | POST-anchor backup | POST project bytes |
| --- | --- | --- | ---: |
| Issue 11 | `D:\BEA-Ghidra-Backups\2026-08-12-xbox-sparse-symbol-pre-anchors-issue11` | `D:\BEA-Ghidra-Backups\2026-08-12-xbox-sparse-symbol-post-anchors-issue11` | 100,598,877 |
| US retail | `D:\BEA-Ghidra-Backups\2026-08-12-xbox-sparse-symbol-pre-anchors-us-retail` | `D:\BEA-Ghidra-Backups\2026-08-12-xbox-sparse-symbol-post-anchors-us-retail` | 100,303,971 |

Those are historical Windows source paths, not current writable locations. The
five project roots under the former `ghidra-projects/` lane, the recovery trees,
and the scratch/probe database roots are being retired from the exploded
`local-lab` topology after checksum-backed packaging. Their supported recovery
route is a package catalog under
`/srv/archive-a/Onslaught-Ghidra-Recovery/`: restore every required tree to new
empty paths before replay, and never substitute the active mutable PC-retail
project. The non-DB READY receipts, anchor/repair tables, inventories, and logs
remain local evidence and do not require a Ghidra database merely to be read.

The machine-local fail-closed owner is
`local-lab/xbox-sparse-symbol-ghidra-20260812-v1/xbox-sparse-symbol-ghidra.ready.json`,
11,510 bytes, SHA-256
`12aecbba4de0f90bd1c1b8731257a74114d7c1e4683de412724c34e2f65051c6`.
At sealing time it re-hashed the canonical projects, all six PRE/POST recovery
trees, the mutation/readback receipts, the exact repair tables, and the anchor
tables. Its frozen source is retained beside it, and two consecutive full
replays produced those exact same receipt bytes and SHA-256. A new full replay
is topology-bound: it requires catalog-guided restoration of the historical
database trees and the exact frozen owner, rather than the evolving tracked
tool. The same seal also re-hashed the then-current PC live and tracked Ghidra
trees and required their 19 files / 186,485,637 bytes / inventory SHA-256
`b7767b108256c0ff71c033094b25e3f2308ef7d00f007854e0068b9307f3adb4`
to remain exact.

## Repository boundary and successor

The supported repository topology no longer treats the five `.gpr/.rep` roots
formerly under
`local-lab/xbox-sparse-symbol-ghidra-20260812-v1/ghidra-projects/` as live
projects. They are not copied into `reverse-engineering/ghidra/`, whose sole
tracked database remains the synchronized PC-retail project. Xbox database
bytes and their recovery copies are cold retail-derived evidence routed through
the external package catalogs; the raw anchor tables and other non-DB evidence
remain in the lab. This document promotes only the reviewed measurements and
their exact receipt identity.

The read-only containing-function join and complete XBE-section census are now
closed by the
[Xbox source-anchor function correlation checkpoint](xbox-anchor-function-correlation-2026-08-12.md).
It proves 379 one-to-one pairs in the pinned current inventories, with 378
strict translated current-boundary pairs, one bounded anchor-partition-only
pair, zero ambiguous components, and 101 anchors uncontained in both builds.
It also isolates 14 named SDK/middleware sections while retaining `.text` as a
mixed-ownership frontier. A source coordinate can seed Version Tracking; it
still cannot authorize an automatic whole-function rename or semantic transfer.
