# Current `.text` body ownership and listing-state accounting

Status: reviewed current structural accounting
Last updated: 2026-08-14
Evidence: MEASURED — exact pristine bytes, current read-only Ghidra body ranges
and listing units, independent interval-union replay, and bounded linear-decode
probes; UNKNOWN — original compiler function denominator, exact missing body
boundaries, loose-code reachability, semantics, runtime behavior, and rebuild
parity.
Verdict: the 8,327 saved Ghidra bodies own exactly 1,811,418 of the pristine
PE's 1,929,117 virtual `.text` bytes (93.898814846%), with zero overlap. The
117,699 unowned bytes are structurally partitioned by current listing state and
bounded discovery evidence; this is body-range ownership, not percent of game
semantics reversed.
Specimen: pristine Steam `BEA.exe`, 2,506,752 bytes, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Machine-local evidence root:
`local-lab/current-text-ownership-post-crt23-20260814-v1/`.

## Exact body-range result

The current 8,327-function Ghidra snapshot was exported read-only after the
reviewed 23-function CRT P0 promotion, from the exact live POST project
(already byte-identical to tracked and the retained POST backup) using the
established `ExportParityLabGraph.java` with `-readOnly -noanalysis`. The export has 8,458
exact body ranges. Every exported range was independently remapped to the
pristine PE and its SHA-256 reproduced.

The PE `.text` virtual extent is `[0x00401000,0x005D7F9D)`, exactly 1,929,117
bytes. The exact current Ghidra body-range union is:

| Measure | Current result |
| --- | ---: |
| Functions | 8,327 |
| Exact body ranges | 8,458 |
| Multi-range functions | 77 |
| Sum / union of body bytes | 1,811,418 |
| `.text` ownership | 93.898814846% |
| Uncovered bytes | 117,699 (6.101185154%) |
| Uncovered runs | 6,022 |
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
  `e27e2f5852a000156a582658ca82f4ee3c979b2175de9c5adb23b0487460c05d`
- `run-a/uncovered-runs.tsv`: 621,331 bytes, SHA-256
  `26a3a335fa63a51df721314b842152ea0b09629b3efc89262e28a60bf3f7c0a5`
- exact owned range-set SHA-256:
  `fcf60b4a14c4cd39b8716e176ec84208b3b56872dc9217cffe47451e9549ea38`
- exact uncovered range-set SHA-256:
  `1d1f21ea13f8d4dbae7f8c2cfa4f48eeffdab7ef8c68f738de2226124fa2a1c9`

The aggregate authority and a subsequent project rehash kept live, tracked, and
the retained POST backup exact at 19 files / 187,009,925 bytes / inventory
`61f77b70fdf807c960a9441ea8e5c4a5b5bd6281675864089a52d61481432f1f`.

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

## What the 117,699 bytes contain in current Ghidra listing state

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
| Exact function bodies | 1,811,418 | 8,458 ranges |
| Decoded instructions outside functions | 18,922 | 5,448 instructions |
| Defined data outside functions | 46,918 | 17,596 data units |
| Listing-unclassified gap bytes | 51,859 | — |
| **PE `.text`** | **1,929,117** | exact closure |

The full 117,699-byte gap has 61,292 bytes whose value is `00`, `90`, or `CC`
and 56,407 other byte values. Of those padding-valued bytes, 39,894 form 5,098
entirely padding-valued runs; mixed runs contain the other 21,398. The
listing-unclassified 51,859-byte partition contains 48,813 padding-valued and
only 3,046 non-padding-valued bytes. Across all gap classes, 1,659 Ghidra
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
| Unclassified-content runs | 117 | 1,431 | no current instruction/data unit; classification remains open |

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
  `61d58f40096d438bbb03375b4b386ab561fadf27ea03e680055eba6bd7fde4d9`
- `gap-accounting-a/gap-classification.tsv`: 839,650 bytes, SHA-256
  `bffa60038cf05fe99679ae645d8fd83bf77ab09c35e94b2a0634e90e4ceeca81`

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
