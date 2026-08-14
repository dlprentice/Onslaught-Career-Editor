# Current `.text` body ownership and listing-state accounting

Status: reviewed current structural accounting
Last updated: 2026-08-14
Evidence: MEASURED — exact pristine bytes, current read-only Ghidra body ranges
and listing units, independent interval-union replay, and bounded linear-decode
probes; UNKNOWN — original compiler function denominator, exact missing body
boundaries, loose-code reachability, semantics, runtime behavior, and rebuild
parity.
Verdict: the 8,280 saved Ghidra bodies own exactly 1,794,212 of the pristine
PE's 1,929,117 virtual `.text` bytes (93.006904195%), with zero overlap. The
134,905 unowned bytes are structurally partitioned by current listing state and
bounded discovery evidence; this is body-range ownership, not percent of game
semantics reversed.
Specimen: pristine Steam `BEA.exe`, 2,506,752 bytes, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Machine-local evidence root:
`local-lab/current-text-ownership-post8280-20260814-v1/`.

## Exact body-range result

The current 8,280-function Ghidra snapshot was exported read-only after the
reviewed 79-boundary external-table promotion, from the exact live POST project
(already byte-identical to tracked and the retained POST backup) using the established
`ExportParityLabGraph.java` with `-readOnly -noanalysis`. The export has 8,400
exact body ranges. Every exported range was independently remapped to the
pristine PE and its SHA-256 reproduced.

The PE `.text` virtual extent is `[0x00401000,0x005D7F9D)`, exactly 1,929,117
bytes. The exact current Ghidra body-range union is:

| Measure | Current result |
| --- | ---: |
| Functions | 8,280 |
| Exact body ranges | 8,400 |
| Multi-range functions | 70 |
| Sum / union of body bytes | 1,794,212 |
| `.text` ownership | 93.006904195% |
| Uncovered bytes | 134,905 (6.993095805%) |
| Uncovered runs | 5,980 |
| Overlapping body bytes | 0 |
| Maximum ownership depth | 1 |

This supersedes the prior 8,201-state result of `1,784,978 / 144,139 /
92.528239604%`; that result remains dated evidence for the state before the
79-boundary promotion. It also supersedes the still older
`1,767,100 / 162,017 / 91.6015%` figures from an 8,124-function campaign
generation. It does **not** change either historical generation or Generation
23.

Two offline replays are byte-identical:

- `run-a/result.ready.json`: 14,334 bytes, SHA-256
  `2933328229411a4fe1a1f6a1bbd4df38deda4c1bb362e470c465c7db2e6bf7ac`
- `run-a/uncovered-runs.tsv`: 617,145 bytes, SHA-256
  `da86b8e21d9a8af42a4e95d4aa4108f4b4113fbaf2b53a1add6f81d7c4c62391`
- exact owned range-set SHA-256:
  `295b94e45aae484c1c57339fc2e13f96f57cf520bcb914f3805cf4a835f4fdb8`
- exact uncovered range-set SHA-256:
  `79a5979d98e97b6bd7a3decac3a518a60f915a2c0f0dc8d41cb8658b295863aa`

The aggregate authority and a subsequent project rehash kept live, tracked, and
the retained POST backup exact at 19 files / 186,960,773 bytes / inventory
`ae422079966978ec2f8f5b951b0ef5812b1074bd708ab8d782179f51c90efcf2`.

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

## What the 134,905 bytes contain in current Ghidra listing state

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
| Exact function bodies | 1,794,212 | 8,400 ranges |
| Decoded instructions outside functions | 35,574 | 10,440 instructions |
| Defined data outside functions | 46,918 | 17,596 data units |
| Listing-unclassified gap bytes | 52,413 | — |
| **PE `.text`** | **1,929,117** | exact closure |

The full 134,905-byte gap has 63,567 bytes whose value is `00`, `90`, or `CC`
and 71,338 other byte values. Of those padding-valued bytes, 39,363 form 5,037
entirely padding-valued runs; mixed runs contain the other 24,204. The
listing-unclassified 52,413-byte partition contains 48,916 padding-valued and
only 3,497 non-padding-valued bytes. Across all gap classes, 2,157 Ghidra
references reach 1,804 distinct unowned targets: 1,273 data, 643 conditional
jump, 155 unconditional jump, 56 read, and 30 computed-jump references.

The bounded candidate projection is:

| Mechanical class | Runs | Bytes | Meaning |
| --- | ---: | ---: | --- |
| Padding-only | 5,037 | 39,363 | every byte is `00`/`90`/`CC` |
| Defined-data only/mixed | 200 | 49,891 | current listing contains defined data; classification may still be wrong |
| Loose-instruction only/mixed | 619 | 39,925 | decoded listing instructions, no entry proof by this fact alone |
| Current-function jump fragment candidates | 5 | 1,270 | a current function jumps into a loose-instruction gap; ownership still needs CFG proof |
| External-table target candidates | 5 | 573 | remaining defined-data targets into loose instructions after the reviewed 79-boundary promotion; callback/body ownership remains open |
| Embedded-`.text` table target candidates | 3 | 2,142 | an in-section table points to loose instruction starts; likely switch/body labels until proved otherwise |
| Unclassified-content runs | 111 | 1,741 | no current instruction/data unit; classification remains open |

The classes are a priority partition, not independent predicate counts:
function-fragment evidence wins first. The 79 externally referenced starts
promoted in the latest ceremony are no longer gaps; the five rows above are the
remaining external-table queue, not a continuation of the sealed 79-row cohort.

The five current-function jump-fragment candidates begin at `0x0046282B` (837
bytes; jump-source function `0x00462640`), `0x004BE82D` (272; jump-source
function `0x004BE420`), `0x0055954C` (111; jump-source function `0x00559410`),
`0x00482725` (28; jump-source function `0x00482590`), and `0x004700DA` (22;
jump-source function `0x0046FF10`). Eight of the twelve qualifying refs are
computed jumps. These are candidates, not yet approved body edits or ownership
claims.

The 992-byte `[0x004DA4BE,0x004DA89E)` gap illustrates why embedded `.text`
table targets cannot be called “missing functions.” It is fully decoded to 257
loose instructions; jump-table entries at `0x004DAA04..0x004DAA10`
point to `0x004DA4BE`, `0x004DA502`, and `0x004DA6B9`. Existing round/explosion
evidence already reads these as switch arms associated with the surrounding
`0x004D9F30` body. This is a body/CFG ownership question, not evidence for three
new functions.

The largest remaining gaps still separate data from high-yield code-shaped
queues. The
26,743-byte `[0x005C9C69,0x005D04E0)` gap contains 23,942 bytes of current
defined data and 133 references from the surrounding `HResultToString` region;
the 6,008-byte `[0x00526098,0x00527810)` gap contains 5,996 bytes of defined
localization tables. Neither should be advertised as a missing-function block.
Conversely, the remaining 3,280-byte `[0x005B4EB0,0x005B5B80)` and 2,424-byte
`[0x005AD818,0x005AE190)` gaps contain 3,219 and 2,369 current loose-instruction
bytes respectively. They are strong discovery queues, not established function
boundaries. The two prior fully decoded unclassified regions at
`[0x00563C80,0x00564486)` and `[0x005B87B7,0x005B8CA0)` are no longer gaps:
the reviewed text-gap ceremony split their exact bodies into 31 saved
functions. The later external-table ceremony similarly removed 9,234 exact
body bytes across 79 newly saved functions without changing any PRE row.

Replayed artifact identities:

- `gap-evidence/text-gap-evidence.ready.json`: 1,029 bytes, SHA-256
  `d6d3c0541882ec88aa521c79a625c6e8874ce7817103dd924c6af0c04fb2a927`
- `gap-accounting-a/result.ready.json`: 4,498 bytes, SHA-256
  `bbfb1df8c57fa62de0c76a86dd601e93d6bf4ace1728f4ab60a76abdde001005`
- `gap-accounting-a/gap-classification.tsv`: 834,976 bytes, SHA-256
  `6f32e827bed3094b4a78511c0493460f60d0c6b711e0ee06bc36914898f070b5`

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
