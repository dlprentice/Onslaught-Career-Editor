# Current `.text` body ownership and listing-state accounting

Status: reviewed current structural accounting
Last updated: 2026-08-14
Evidence: MEASURED — exact pristine bytes, current read-only Ghidra body ranges
and listing units, independent interval-union replay, and bounded linear-decode
probes; UNKNOWN — original compiler function denominator, exact missing body
boundaries, loose-code reachability, semantics, runtime behavior, and rebuild
parity.
Verdict: the 8,280 saved Ghidra bodies own exactly 1,795,470 of the pristine
PE's 1,929,117 virtual `.text` bytes (93.072115377%), with zero overlap. The
133,647 unowned bytes are structurally partitioned by current listing state and
bounded discovery evidence; this is body-range ownership, not percent of game
semantics reversed.
Specimen: pristine Steam `BEA.exe`, 2,506,752 bytes, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Machine-local evidence root:
`local-lab/current-text-ownership-post-fragment5-20260814-v1/`.

## Exact body-range result

The current 8,280-function Ghidra snapshot was exported read-only after the
reviewed five-body fragment promotion, from the exact live POST project
(already byte-identical to tracked and the retained POST backup) using the
established `ExportParityLabGraph.java` with `-readOnly -noanalysis`. The export has 8,396
exact body ranges. Every exported range was independently remapped to the
pristine PE and its SHA-256 reproduced.

The PE `.text` virtual extent is `[0x00401000,0x005D7F9D)`, exactly 1,929,117
bytes. The exact current Ghidra body-range union is:

| Measure | Current result |
| --- | ---: |
| Functions | 8,280 |
| Exact body ranges | 8,396 |
| Multi-range functions | 67 |
| Sum / union of body bytes | 1,795,470 |
| `.text` ownership | 93.072115377% |
| Uncovered bytes | 133,647 (6.927884623%) |
| Uncovered runs | 5,976 |
| Overlapping body bytes | 0 |
| Maximum ownership depth | 1 |

This supersedes the immediately prior 8,280-state result of `1,794,212 /
134,905 / 93.006904195%` before the five body repairs. It also supersedes the
8,201-state result of `1,784,978 / 144,139 /
92.528239604%`; that result remains dated evidence for the state before the
79-boundary promotion. It also supersedes the still older
`1,767,100 / 162,017 / 91.6015%` figures from an 8,124-function campaign
generation. It does **not** change either historical generation or Generation
23.

Two offline replays are byte-identical:

- `run-a/result.ready.json`: 14,318 bytes, SHA-256
  `d2e35899eff73cf6ca22304010fbe219320832416c2a79e49b365fd3acfde056`
- `run-a/uncovered-runs.tsv`: 616,714 bytes, SHA-256
  `f1494702aebcbc36a3784ee27d6ed8aa2f624d221c70fdcb54c69f540f0b2e55`
- exact owned range-set SHA-256:
  `bd15a1d64d7afe03b91a833a15c32ec8d463a8ac7d9968229c3e511665a6f28c`
- exact uncovered range-set SHA-256:
  `b92b30d5335d0f6996b786ecd739a2125be7f6e71ab30be2c7f262adcf5e0e8f`

The aggregate authority and a subsequent project rehash kept live, tracked, and
the retained POST backup exact at 19 files / 186,977,157 bytes / inventory
`cda0938c1a266fbe1751a8b0bf175b90c63b296f21fc9631b5bade1ecf93e541`.

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

## What the 133,647 bytes contain in current Ghidra listing state

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
| Exact function bodies | 1,795,470 | 8,396 ranges |
| Decoded instructions outside functions | 34,408 | 10,138 instructions |
| Defined data outside functions | 46,918 | 17,596 data units |
| Listing-unclassified gap bytes | 52,321 | — |
| **PE `.text`** | **1,929,117** | exact closure |

The full 133,647-byte gap has 63,331 bytes whose value is `00`, `90`, or `CC`
and 70,316 other byte values. Of those padding-valued bytes, 39,375 form 5,038
entirely padding-valued runs; mixed runs contain the other 23,956. The
listing-unclassified 52,321-byte partition contains 48,895 padding-valued and
only 3,426 non-padding-valued bytes. Across all gap classes, 2,085 Ghidra
references reach 1,759 distinct unowned targets: 1,252 data, 608 conditional
jump, 147 unconditional jump, 56 read, and 22 computed-jump references.

The bounded candidate projection is:

| Mechanical class | Runs | Bytes | Meaning |
| --- | ---: | ---: | --- |
| Padding-only | 5,038 | 39,375 | every byte is `00`/`90`/`CC` |
| Defined-data only/mixed | 200 | 49,891 | current listing contains defined data; classification may still be wrong |
| Loose-instruction only/mixed | 619 | 39,925 | decoded listing instructions, no entry proof by this fact alone |
| Current-function jump fragment candidates | 0 | 0 | the five reviewed candidates were promoted as body repairs |
| External-table target candidates | 5 | 573 | remaining defined-data targets into loose instructions after the reviewed 79-boundary promotion; callback/body ownership remains open |
| Embedded-`.text` table target candidates | 3 | 2,142 | an in-section table points to loose instruction starts; likely switch/body labels until proved otherwise |
| Unclassified-content runs | 111 | 1,741 | no current instruction/data unit; classification remains open |

The classes are a priority partition, not independent predicate counts:
function-fragment evidence wins first. The 79 externally referenced starts
promoted in the latest ceremony are no longer gaps; the five rows above are the
remaining external-table queue, not a continuation of the sealed 79-row cohort.

The former five current-function jump-fragment candidates are now reviewed body
repairs. Their exact union adds 1,258 owned bytes; the twelve trailing NOP bytes
at `0x00462B64..0x00462B70` remain a separate padding-only gap. The completed
ceremony and its limits are recorded in the
[`function-body fragment live-promotion report`](pc-function-body-fragment-ghidra-live-promotion-2026-08-14.md).

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
  `39c479b9e6a2166827514795eed2fbf3b80e2edc01c3a09d9c97d5e96054c85c`
- `gap-accounting-a/result.ready.json`: 3,401 bytes, SHA-256
  `18084153a1577f08640268109520602669433b2ca2dd69cf56e97b8a6edd0d61`
- `gap-accounting-a/gap-classification.tsv`: 834,132 bytes, SHA-256
  `bc9bdf3973626ab4a22494125a2e94c930ee773e21ffa1a185b57e1c925e7b0f`

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
