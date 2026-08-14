# Current `.text` body ownership and listing-state accounting

Status: reviewed current structural accounting
Last updated: 2026-08-14
Evidence: MEASURED — exact pristine bytes, current read-only Ghidra body ranges
and listing units, independent interval-union replay, and bounded linear-decode
probes; UNKNOWN — original compiler function denominator, exact missing body
boundaries, loose-code reachability, semantics, runtime behavior, and rebuild
parity.
Verdict: the 8,201 saved Ghidra bodies own exactly 1,784,978 of the pristine
PE's 1,929,117 virtual `.text` bytes (92.528239604%), with zero overlap. The
144,139 unowned bytes are structurally partitioned by current listing state and
bounded discovery evidence; this is body-range ownership, not percent of game
semantics reversed.
Specimen: pristine Steam `BEA.exe`, 2,506,752 bytes, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Machine-local evidence root:
`local-lab/ghidra-text-gap-boundary-live-promotion-20260814-v1/text-ownership-post/`.

## Exact body-range result

The current 8,201-function Ghidra snapshot was exported read-only after the
reviewed 31-boundary text-gap promotion, from a
19-file byte-identical disposable copy using the established
`ExportParityLabGraph.java` with `-readOnly -noanalysis`. The export has 8,321
exact body ranges. Every exported range was independently remapped to the
pristine PE and its SHA-256 reproduced.

The PE `.text` virtual extent is `[0x00401000,0x005D7F9D)`, exactly 1,929,117
bytes. The exact current Ghidra body-range union is:

| Measure | Current result |
| --- | ---: |
| Functions | 8,201 |
| Exact body ranges | 8,321 |
| Multi-range functions | 70 |
| Sum / union of body bytes | 1,784,978 |
| `.text` ownership | 92.528239604% |
| Uncovered bytes | 144,139 (7.471760396%) |
| Uncovered runs | 6,004 |
| Overlapping body bytes | 0 |
| Maximum ownership depth | 1 |

This supersedes the prior current-use 8,170-state result of `1,770,929 /
158,188 / 91.799978954%`; that result remains dated evidence for the state
before the 31-boundary promotion. It also supersedes the still older
`1,767,100 / 162,017 / 91.6015%` figures from an 8,124-function campaign
generation. It does **not** change either historical generation or Generation
23.

Two offline replays are byte-identical:

- `run-a/result.ready.json`: 14,334 bytes, SHA-256
  `b13b26e547e784c2e4086c10fc7ceac043769166293bcf97d7def83b43598db1`
- `run-a/uncovered-runs.tsv`: 619,802 bytes, SHA-256
  `9b96a1a369b6bbd84400c7ac76a1fa0626a6fcd688e0f43683ab9fd94feca705`
- exact owned range-set SHA-256:
  `79f4d6545e175193129a8d1e797462356aadc518eafe0c8bf5ca6625bac09dce`
- exact uncovered range-set SHA-256:
  `3ab81ca35173c8267ce005801bfd04f91e901b4911baca9c35f32e8f501217af`

The disposable project remained byte-identical to the tracked 19-file snapshot
after the final read-only open.

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

## What the 144,139 bytes contain in current Ghidra listing state

A second read-only exporter joined the same exact gaps to current listing
instructions, defined data, and inbound references. Two exports and two offline
joins are byte-identical.

An initial join treated every code-origin `DATA` reference as possible entry
evidence. Inspection falsified that rule: ordinary instructions use Ghidra
`DATA` references for strings and globals. The final exporter records source
block and listing kind, confines itself to the PE virtual `.text` end rather
than Ghidra's 99-byte aligned tail, and separates external table targets from
embedded `.text` tables. All earlier `gap-evidence-a/b` and
`gap-accounting-a/b` outputs are preserved as superseded pre-hardening evidence.

| Partition | Bytes | Rows |
| --- | ---: | ---: |
| Exact function bodies | 1,784,978 | 8,321 ranges |
| Decoded instructions outside functions | 44,698 | 13,749 instructions |
| Defined data outside functions | 46,918 | 17,596 data units |
| Listing-unclassified gap bytes | 52,523 | — |
| **PE `.text`** | **1,929,117** | exact closure |

The full 144,139-byte gap has 64,167 bytes whose value is `00`, `90`, or `CC`
and 79,972 other byte values. Of those padding-valued bytes, 39,234 form 5,019
entirely padding-valued runs; mixed runs contain the other 24,933. The
listing-unclassified 52,523-byte partition contains 48,942 padding-valued and
only 3,581 non-padding-valued bytes. Across all gap classes, 2,428 Ghidra
references reach 2,018 distinct unowned targets: 1,367 data, 773 conditional
jump, 182 unconditional jump, 56 read, and 50 computed-jump references.

The bounded candidate projection is:

| Mechanical class | Runs | Bytes | Meaning |
| --- | ---: | ---: | --- |
| Padding-only | 5,019 | 39,234 | every byte is `00`/`90`/`CC` |
| Defined-data only/mixed | 199 | 49,803 | current listing contains defined data; classification may still be wrong |
| Loose-instruction only/mixed | 618 | 40,148 | decoded listing instructions, no entry proof by this fact alone |
| Current-function jump fragment candidates | 5 | 1,270 | a current function jumps into a loose-instruction gap; ownership still needs CFG proof |
| External-table target candidates | 51 | 9,834 | defined data in `.data`/`.rdata` points to a loose instruction start; callback/vtable/function provenance remains open |
| Embedded-`.text` table target candidates | 3 | 2,142 | an in-section table points to loose instruction starts; likely switch/body labels until proved otherwise |
| Unclassified-content runs | 109 | 1,708 | no current instruction/data unit; 1,093 bytes are non-padding-valued |

The classes are a priority partition, not independent predicate counts:
function-fragment evidence wins first. Before that priority rule, 52 gaps have
external-table targets and six have embedded-`.text` table targets; one and
three respectively also qualify as function-fragment candidates, yielding the
published 51/3 table-target partition without discarding their underlying refs.

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
the reviewed text-gap ceremony split their exact bodies into the 31 newly saved
functions measured above.

Replayed artifact identities:

- `gap-evidence/text-gap-evidence.ready.json`: 1,029 bytes, SHA-256
  `53dbdca09ea2558c7562ac168d5c964ad9d8a1d2633b5d20abd0dafd2abe7fbc`
- `gap-accounting-a/result.ready.json`: 4,535 bytes, SHA-256
  `d4bb971a9d29835f57ae4790b93d57a2017262f0ed3f961e6c89c4fa053eb36d`
- `gap-accounting-a/gap-classification.tsv`: 840,190 bytes, SHA-256
  `d3b0b94a3d6cf3d726130e16412c40e7ccddd85985e07503c78f8f2f9b7ce91b`

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
