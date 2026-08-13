# Current `.text` body ownership and listing-state accounting

Status: reviewed current structural accounting
Last updated: 2026-08-13
Evidence: MEASURED — exact pristine bytes, current read-only Ghidra body ranges
and listing units, independent interval-union replay, and bounded linear-decode
probes; UNKNOWN — original compiler function denominator, exact missing body
boundaries, loose-code reachability, semantics, runtime behavior, and rebuild
parity.
Verdict: the 8,170 saved Ghidra bodies own exactly 1,770,929 of the pristine
PE's 1,929,117 virtual `.text` bytes (91.799978954%), with zero overlap. The
158,188 unowned bytes are structurally partitioned by current listing state and
bounded discovery evidence; this is body-range ownership, not percent of game
semantics reversed.
Specimen: pristine Steam `BEA.exe`, 2,506,752 bytes, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Machine-local evidence root:
`local-lab/current-text-ownership-20260813-v1/`.

## Exact body-range result

The current 8,170-function Ghidra snapshot was exported read-only from a
19-file byte-identical disposable copy using the established
`ExportParityLabGraph.java` with `-readOnly -noanalysis`. The export has 8,287
exact body ranges. Every exported range was independently remapped to the
pristine PE and its SHA-256 reproduced.

The PE `.text` virtual extent is `[0x00401000,0x005D7F9D)`, exactly 1,929,117
bytes. The exact current Ghidra body-range union is:

| Measure | Current result |
| --- | ---: |
| Functions | 8,170 |
| Exact body ranges | 8,287 |
| Multi-range functions | 67 |
| Sum / union of body bytes | 1,770,929 |
| `.text` ownership | 91.799978954% |
| Uncovered bytes | 158,188 (8.200021046%) |
| Uncovered runs | 5,984 |
| Overlapping body bytes | 0 |
| Maximum ownership depth | 1 |

This supersedes the current-use `1,767,100 / 162,017 / 91.6015%` figures. Those
values belong to an older 8,124-function campaign generation. It also closes
the present-tense `UNKNOWN` interval-union claim. It does **not** change that
historical generation or Generation 23.

Two offline replays are byte-identical:

- `run-c/result.ready.json`: 14,341 bytes, SHA-256
  `e6dbd602894e710a306c745b3e1404d13b0dff0e2dfbffef9b599a22f2f7b4df`
- `run-c/uncovered-runs.tsv`: 617,749 bytes, SHA-256
  `533ceecbbf6238ffef488dad92e5812e11db953c0a627328cf77d52ef1720adb`
- exact owned range-set SHA-256:
  `c9b0622c335f6a7c4bd7395ace338ff7ce3e78db7a3db70f09357480ee90fa7f`
- exact uncovered range-set SHA-256:
  `f271917a02efcad45f66663411998d7df112ac5eb27fb45c4ebd13b9549cc7a8`

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

## What the 158,188 bytes contain in current Ghidra listing state

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
| Exact function bodies | 1,770,929 | 8,287 ranges |
| Decoded instructions outside functions | 54,994 | 16,534 instructions |
| Defined data outside functions | 46,918 | 17,596 data units |
| Listing-unclassified gap bytes | 56,276 | — |
| **PE `.text`** | **1,929,117** | exact closure |

The full 158,188-byte gap has 65,407 bytes whose value is `00`, `90`, or `CC`
and 92,781 other byte values. Of those padding-valued bytes, 39,207 form 5,014
entirely padding-valued runs; mixed runs contain the other 26,200. The
listing-unclassified 56,276-byte partition contains 49,158 padding-valued and
only 7,118 non-padding-valued bytes. Across all gap classes, 2,498 Ghidra
references reach 2,048 distinct unowned targets: 1,373 data, 825 conditional
jump, 194 unconditional jump, 56 read, and 50 computed-jump references.

The bounded candidate projection is:

| Mechanical class | Runs | Bytes | Meaning |
| --- | ---: | ---: | --- |
| Padding-only | 5,014 | 39,207 | every byte is `00`/`90`/`CC` |
| Defined-data only/mixed | 199 | 49,803 | current listing contains defined data; classification may still be wrong |
| Loose-instruction only/mixed | 619 | 51,174 | decoded listing instructions, no entry proof by this fact alone |
| Current-function jump fragment candidates | 5 | 1,270 | a current function jumps into a loose-instruction gap; ownership still needs CFG proof |
| External-table target candidates | 51 | 9,834 | defined data in `.data`/`.rdata` points to a loose instruction start; callback/vtable/function provenance remains open |
| Embedded-`.text` table target candidates | 3 | 2,142 | an in-section table points to loose instruction starts; likely switch/body labels until proved otherwise |
| Unclassified-content runs | 93 | 4,758 | no current instruction/data unit; 3,977 bytes are non-padding-valued |

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

The largest gaps also separate data from high-yield code-shaped queues. The
26,743-byte `[0x005C9C69,0x005D04E0)` gap contains 23,942 bytes of current
defined data and 133 references from the surrounding `HResultToString` region;
the 6,008-byte `[0x00526098,0x00527810)` gap contains 5,996 bytes of defined
localization tables. Neither should be advertised as a missing-function block.
Conversely, `[0x005B8E9E,0x005BB9B0)` contains 10,296 current loose-instruction
bytes, while two current unclassified gaps have complete bounded linear-decode
evidence: after six `CC` bytes, `[0x00563C80,0x00564486)` decodes through all
2,054 bytes (695 instructions, 78 returns), and `[0x005B87B7,0x005B8CA0)`
decodes through all 1,257 bytes (290 instructions, 14 returns). These are strong
code-shaped discovery queues, not established function boundaries. Two
byte-identical probe receipts are 2,626 bytes each with SHA-256
`b224f0a5aa4ab70fdd9c2316ff107eb0b722839a0e0f5a0e9494b596d18a58af`.

Replayed artifact identities:

- `gap-evidence-c/text-gap-evidence.ready.json`: 1,029 bytes, SHA-256
  `54111731abebc4e47181bd54e84a9290d253d042b790cab13c95d69a59d32af6`
- `gap-accounting-c/result.ready.json`: 4,535 bytes, SHA-256
  `1d0c8c4d326f433f34f5500789f1185fd1e655fa316ec3f6ea22c192ff9ac2c0`
- `gap-accounting-c/gap-classification.tsv`: 837,395 bytes, SHA-256
  `2e3e6a1826bd36180f97b12a57a030240ac5df43dd3b984e64361296e6f9b0c4`

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
