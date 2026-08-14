# Current `.text` body ownership and listing-state accounting

Status: reviewed current structural accounting
Last updated: 2026-08-14
Evidence: MEASURED — exact pristine bytes, current read-only Ghidra body ranges
and listing units, independent interval-union replay, and bounded linear-decode
probes; UNKNOWN — original compiler function denominator, exact missing body
boundaries, loose-code reachability, semantics, runtime behavior, and rebuild
parity.
Verdict: the 8,304 saved Ghidra bodies own exactly 1,810,287 of the pristine
PE's 1,929,117 virtual `.text` bytes (93.840186987%), with zero overlap. The
118,830 unowned bytes are structurally partitioned by current listing state and
bounded discovery evidence; this is body-range ownership, not percent of game
semantics reversed.
Specimen: pristine Steam `BEA.exe`, 2,506,752 bytes, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Machine-local evidence root:
`local-lab/current-text-ownership-post-jpeg24-20260814-v1/`.

## Exact body-range result

The current 8,304-function Ghidra snapshot was exported read-only after the
reviewed 24-function JPEG/IJG callback promotion, from the exact live POST project
(already byte-identical to tracked and the retained POST backup) using the
established `ExportParityLabGraph.java` with `-readOnly -noanalysis`. The export has 8,434
exact body ranges. Every exported range was independently remapped to the
pristine PE and its SHA-256 reproduced.

The PE `.text` virtual extent is `[0x00401000,0x005D7F9D)`, exactly 1,929,117
bytes. The exact current Ghidra body-range union is:

| Measure | Current result |
| --- | ---: |
| Functions | 8,304 |
| Exact body ranges | 8,434 |
| Multi-range functions | 76 |
| Sum / union of body bytes | 1,810,287 |
| `.text` ownership | 93.840186987% |
| Uncovered bytes | 118,830 (6.159813013%) |
| Uncovered runs | 6,012 |
| Overlapping body bytes | 0 |
| Maximum ownership depth | 1 |

This supersedes the immediately prior 8,280-state result of `1,795,470 /
133,647 / 93.072115377%` after the five body repairs. It also supersedes the
8,201-state result of `1,784,978 / 144,139 /
92.528239604%`; that result remains dated evidence for the state before the
79-boundary promotion. It also supersedes the still older
`1,767,100 / 162,017 / 91.6015%` figures from an 8,124-function campaign
generation. It does **not** change either historical generation or Generation
23.

Two offline replays are byte-identical:

- `run-a/result.ready.json`: 14,303 bytes, SHA-256
  `7196209a58c4902d9a14ddb5c20f3364d4aebbd20421a7714131955d7efe6c39`
- `run-a/uncovered-runs.tsv`: 620,364 bytes, SHA-256
  `2717305dde0b8881a55cac954e2a38ceaba5b150dedcc54f5ca6a95e1424777d`
- exact owned range-set SHA-256:
  `3314a9e1d696ff71b0c608b2be7ea5ebd0dad590090cf36d55ae29f44c261347`
- exact uncovered range-set SHA-256:
  `93392cb6775e0d61f40971da95c7d9476babfc49b1aa9124546cb1a0600a522f`

The aggregate authority and a subsequent project rehash kept live, tracked, and
the retained POST backup exact at 19 files / 186,993,541 bytes / inventory
`3cd459d5461919934199e3346f6a92ce14946f42af400488ccde733173a40627`.

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

## What the 118,830 bytes contain in current Ghidra listing state

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
| Exact function bodies | 1,810,287 | 8,434 ranges |
| Decoded instructions outside functions | 19,711 | 5,682 instructions |
| Defined data outside functions | 46,918 | 17,596 data units |
| Listing-unclassified gap bytes | 52,201 | — |
| **PE `.text`** | **1,929,117** | exact closure |

The full 118,830-byte gap has 61,501 bytes whose value is `00`, `90`, or `CC`
and 57,329 other byte values. Of those padding-valued bytes, 39,636 form 5,066
entirely padding-valued runs; mixed runs contain the other 21,865. The
listing-unclassified 52,201-byte partition contains 48,884 padding-valued and
only 3,317 non-padding-valued bytes. Across all gap classes, 1,697 Ghidra
references reach 1,477 distinct unowned targets: 1,219 data, 317 conditional
jump, 83 unconditional jump, 56 read, and 22 computed-jump references.

The bounded candidate projection is:

| Mechanical class | Runs | Bytes | Meaning |
| --- | ---: | ---: | --- |
| Padding-only | 5,066 | 39,636 | every byte is `00`/`90`/`CC` |
| Defined-data only/mixed | 202 | 49,965 | current listing contains defined data; classification may still be wrong |
| Loose-instruction only/mixed | 611 | 24,698 | decoded listing instructions, no entry proof by this fact alone |
| Current-function jump fragment candidates | 0 | 0 | the five reviewed candidates were promoted as body repairs |
| External-table target candidates | 5 | 573 | remaining defined-data targets into loose instructions after the reviewed 79-boundary promotion; callback/body ownership remains open |
| Embedded-`.text` table target candidates | 3 | 2,142 | an in-section table points to loose instruction starts; likely switch/body labels until proved otherwise |
| Unclassified-content runs | 125 | 1,816 | no current instruction/data unit; classification remains open |

The classes are a priority partition, not independent predicate counts:
function-fragment evidence wins first. The 79 externally referenced starts
promoted in the preceding ceremony are no longer gaps; the five rows above are
the remaining external-table queue, not a continuation of the sealed cohort.

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
  `091557dba8d6fba6fffdf88b370707ffb59f9f1f4f75c49b4796e06ada25c46b`
- `gap-accounting-a/result.ready.json`: 3,399 bytes, SHA-256
  `f88810826489dbce703a0b375bc4f587dbc4fffd5c6eaeaaaf76966d5e4aec10`
- `gap-accounting-a/gap-classification.tsv`: 838,709 bytes, SHA-256
  `3cde2b89d6cef1e45bbb08df914666b633e533c283cf6d3c25d671e17cee6a12`

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
