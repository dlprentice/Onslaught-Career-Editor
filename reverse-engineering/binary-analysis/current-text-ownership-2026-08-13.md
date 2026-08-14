# Current `.text` body ownership and listing-state accounting

Status: reviewed current structural accounting
Last updated: 2026-08-14
Evidence: MEASURED — exact pristine bytes, current read-only Ghidra body ranges
and listing units, independent interval-union replay, and bounded linear-decode
probes; UNKNOWN — original compiler function denominator, exact missing body
boundaries, loose-code reachability, semantics, runtime behavior, and rebuild
parity.
Verdict: the 8,327 saved Ghidra bodies own exactly 1,811,443 of the pristine
PE's 1,929,117 virtual `.text` bytes (93.900110776%), with zero overlap. The
117,674 unowned bytes are structurally partitioned by current listing state and
bounded discovery evidence; this is body-range ownership, not percent of game
semantics reversed.
Specimen: pristine Steam `BEA.exe`, 2,506,752 bytes, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Machine-local evidence root:
`local-lab/current-text-ownership-post-crt-eh-parent-20260814-v1/`.

## Exact body-range result

The current 8,327-function Ghidra snapshot was exported read-only after the
reviewed CRT EH parent-range repair, from the exact live POST project
(already byte-identical to tracked and the retained POST backup) using the
established `ExportParityLabGraph.java` with `-readOnly -noanalysis`. The export has 8,457
exact body ranges. Every exported range was independently remapped to the
pristine PE and its SHA-256 reproduced.

The PE `.text` virtual extent is `[0x00401000,0x005D7F9D)`, exactly 1,929,117
bytes. The exact current Ghidra body-range union is:

| Measure | Current result |
| --- | ---: |
| Functions | 8,327 |
| Exact body ranges | 8,457 |
| Multi-range functions | 76 |
| Sum / union of body bytes | 1,811,443 |
| `.text` ownership | 93.900110776% |
| Uncovered bytes | 117,674 (6.099889224%) |
| Uncovered runs | 6,021 |
| Overlapping body bytes | 0 |
| Maximum ownership depth | 1 |

This supersedes the immediately prior 8,304-state result of `1,810,287 /
118,830 / 93.840186987%` after the JPEG/IJG callback promotion. It also
supersedes the 8,280-state result of `1,795,470 / 133,647 / 93.072115377%`
after the five body repairs. It also supersedes the
8,201-state result of `1,784,978 / 144,139 /
92.528239604%`; that result remains dated evidence for the state before the
79-boundary promotion. It also supersedes the still older
`1,767,100 / 162,017 / 91.6015%` figures from an 8,124-function campaign
generation. It does **not** change either historical generation or Generation
23.

Two offline replays are byte-identical:

- `run-a/result.ready.json`: 14,303 bytes, SHA-256
  `397391d1e5382f4434182dd2869343d406677b7e4ea757ddc61df49893f31bfa`
- `run-a/uncovered-runs.tsv`: 621,226 bytes, SHA-256
  `32620ad6d9cedf0f7a301bca82c4718a5d2d763ad742b1a448ed051eaf775f85`
- exact owned range-set SHA-256:
  `8203961a7664cbfc86cb6fc569563b67948b1c5605040d77b7336c9233a99427`
- exact uncovered range-set SHA-256:
  `ca094810804d100dea7d001d072afc0562301926b50ea52af79aafbb2f1178ce`

The aggregate authority and a subsequent project rehash kept live, tracked, and
the retained POST backup exact at 19 files / 187,009,925 bytes / inventory
`a7916b5642b808f468ef113e731a4cfcf225287c94264009fde1034edd9b91cf`.

An independent minimal PE parser and per-byte coverage bitmap reproduced every
headline, every range hash, both range-set hashes, and the uncovered TSV
byte-for-byte without importing the analyzer. The checker was then hardened to
require contiguous range ordinals, one stable name per entry, and every entry
inside one of its own body ranges; the result now records filenames rather than
host-absolute paths. Earlier `run-a/run-b` receipts are preserved as superseded
pre-hardening output and are not authority.

Negative controls also passed: both offline analyzers refused existing outputs;
interactive controls observed the ownership analyzer reject the deliberately
patched installed executable and the gap join reject the wrong receipt schema,
each before publishing anything; and the preserved exporter no-clobber log
records a forced rerun refusing all four existing outputs with their hashes
unchanged.

## What the 117,674 bytes contain in current Ghidra listing state

A second read-only exporter joined the same exact gaps to current listing
instructions, defined data, and inbound references. Two offline joins over that
export are byte-identical.

An initial join treated every code-origin `DATA` reference as possible entry
evidence. Inspection falsified that rule: ordinary instructions use Ghidra
`DATA` references for strings and globals. The final exporter records source
block and listing kind, confines itself to the PE virtual `.text` end rather
than Ghidra's 99-byte aligned tail, and separates external table targets from
embedded `.text` tables. All earlier `gap-evidence-a/b` and
`gap-accounting-a/b` outputs are preserved as superseded pre-hardening evidence.

| Partition | Bytes | Rows |
| --- | ---: | ---: |
| Exact function bodies | 1,811,443 | 8,457 ranges |
| Decoded instructions outside functions | 18,922 | 5,448 instructions |
| Defined data outside functions | 46,918 | 17,596 data units |
| Listing-unclassified gap bytes | 51,834 | — |
| **PE `.text`** | **1,929,117** | exact closure |

The full 117,674-byte gap has 61,288 bytes whose value is `00`, `90`, or `CC`
and 56,386 other byte values. Of those padding-valued bytes, 39,894 form 5,098
entirely padding-valued runs; mixed runs contain the other 21,394. The
listing-unclassified 51,834-byte partition contains 48,809 padding-valued and
only 3,025 non-padding-valued bytes. Across all gap classes, 1,659 Ghidra
references reach 1,443 distinct unowned targets: 1,204 data, 295 conditional
jump, 82 unconditional jump, 56 read, and 22 computed-jump references.

The bounded candidate projection is:

| Mechanical class | Runs | Bytes | Meaning |
| --- | ---: | ---: | --- |
| Padding-only | 5,098 | 39,894 | every byte is `00`/`90`/`CC` |
| Defined-data only/mixed | 202 | 49,965 | current listing contains defined data; classification may still be wrong |
| Loose-instruction only/mixed | 597 | 23,694 | decoded listing instructions, no entry proof by this fact alone |
| Current-function jump fragment candidates | 0 | 0 | the five reviewed candidates were promoted as body repairs |
| External-table target candidates | 5 | 573 | remaining defined-data targets into loose instructions after the reviewed 79-boundary promotion; callback/body ownership remains open |
| Embedded-`.text` table target candidates | 3 | 2,142 | an in-section table points to loose instruction starts; likely switch/body labels until proved otherwise |
| Unclassified-content runs | 116 | 1,406 | no current instruction/data unit; classification remains open |

The classes are a priority partition, not independent predicate counts:
function-fragment evidence wins first. The 79 externally referenced starts
promoted in the preceding ceremony are no longer gaps; the five rows above are
the remaining external-table queue, not a continuation of the sealed cohort.

The former five current-function jump-fragment candidates are now reviewed body
repairs. Their exact union adds 1,258 owned bytes; the twelve trailing NOP bytes
at `0x00462B64..0x00462B70` remain a separate padding-only gap. The completed
ceremony and its limits are recorded in the
[`function-body fragment live-promotion report`](pc-function-body-fragment-ghidra-live-promotion-2026-08-14.md).

The later CRT P0 promotion removes another 1,131 bytes from the gaps as 23
default-metadata functions. Its two-range `0x00542710` owner absorbs the local
tail at `0x00542720` without creating a second entry; the two EH labels and the
separate `0x005B8500` canary remain excluded. See the
[`CRT live-promotion report`](crt-runtime-p0-ghidra-live-promotion-2026-08-14.md).

The latest CRT EH parent-range repair removes a further 25 bytes from the gap
without adding a function. It joins the two existing body components of
`CRT__LongJmpProbe_NoOp` across its scope-table-owned filter and handler, while
keeping `0x005D0AD6` and `0x005D0AEA` as interior labels rather than entries.
See the
[`CRT EH live-promotion report`](crt-eh-parent-range-ghidra-live-promotion-2026-08-14.md).

The 992-byte `[0x004DA4BE,0x004DA89E)` gap illustrates why embedded `.text`
table targets cannot be called “missing functions.” It is fully decoded to 257
loose instructions; jump-table entries at `0x004DAA04..0x004DAA10`
point to `0x004DA4BE`, `0x004DA502`, and `0x004DA6B9`. Existing round/explosion
evidence already reads these as switch arms associated with the surrounding
`0x004D9F30` body. This is a body/CFG ownership question, not evidence for three
new functions.

The largest remaining gaps still separate data from code-shaped queues. The
26,743-byte `[0x005C9C69,0x005D04E0)` gap contains 23,942 bytes of current
defined data and 133 references from the surrounding `HResultToString` region;
the 6,008-byte `[0x00526098,0x00527810)` gap contains 5,996 bytes of defined
localization tables. Neither should be advertised as a missing-function block.
The former 3,280-byte `[0x005B4EB0,0x005B5B80)` and 2,424-byte
`[0x005AD818,0x005AE190)` gaps are no longer large loose-code queues: the
reviewed JPEG/IJG ceremony promoted their proved callback bodies while leaving
the `0x005B4EB0` table and other excluded bytes unowned. The two prior fully
decoded unclassified regions at
`[0x00563C80,0x00564486)` and `[0x005B87B7,0x005B8CA0)` are no longer gaps:
the reviewed text-gap ceremony split their exact bodies into 31 saved
functions. The later external-table ceremony similarly removed 9,234 exact
body bytes across 79 newly saved functions without changing any PRE row.

Replayed current artifact identities:

- `gap-evidence/text-gap-evidence.ready.json`: 1,027 bytes, SHA-256
  `574274b4f1b364865cfbb9b9702f61c5eef4f0b3cec18a0f8d3b98366e830f5c`
- `gap-accounting-a/result.ready.json`: 3,399 bytes, SHA-256
  `b7667aeae138410dd00a1e99f30386183546524e6165b7fc8615cfba5ab80e28`
- `gap-accounting-a/gap-classification.tsv`: 839,502 bytes, SHA-256
  `d8d93e11b00593a7129377bf441f4f3622a9aaa0402adb76cfbbf5f0b89a1309`

## Boundary

This pass measures exact current Ghidra ownership and current listing state. It
does not claim that loose instructions are executable, that data classifications
are correct, that table-referenced labels are function starts, or that padding
values cannot occur in reachable code. Code-origin data references are not entry
evidence and are deliberately excluded from the boundary-candidate cohorts. It
grades no name, signature, semantic
contract, runtime reachability, or rebuild parity. Any body expansion or new
function still requires a target-specific boundary proof and the full backed-up
Ghidra promotion gate.
