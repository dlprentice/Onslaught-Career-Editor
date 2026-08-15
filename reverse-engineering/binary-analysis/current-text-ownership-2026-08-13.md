# Current `.text` body ownership and listing-state accounting

Status: reviewed current structural accounting
Last updated: 2026-08-14
Evidence: MEASURED — exact pristine bytes, current read-only Ghidra body ranges
and listing units, independent interval-union replay, and bounded linear-decode
probes; UNKNOWN — original compiler function denominator, exact missing body
boundaries, loose-code reachability, semantics, runtime behavior, and rebuild
parity.
Verdict: the 8,329 saved Ghidra bodies own exactly 1,811,691 of the pristine
PE's 1,929,117 virtual `.text` bytes (93.912966399%), with zero overlap. The
117,426 unowned bytes are structurally partitioned by current listing state and
bounded discovery evidence; this is body-range ownership, not percent of game
semantics reversed.
Specimen: pristine Steam `BEA.exe`, 2,506,752 bytes, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Machine-local evidence root:
`local-lab/current-text-ownership-post-d3dx-two-20260814-v1/`.

## Exact body-range result

The current 8,329-function Ghidra snapshot was exported read-only after the
reviewed D3DX two-function promotion, from the exact live POST project
(already byte-identical to tracked and the retained POST backup) using the
established `ExportParityLabGraph.java` with `-readOnly -noanalysis`. The export has 8,459
exact body ranges. Every exported range was independently remapped to the
pristine PE and its SHA-256 reproduced.

The PE `.text` virtual extent is `[0x00401000,0x005D7F9D)`, exactly 1,929,117
bytes. The exact current Ghidra body-range union is:

| Measure | Current result |
| --- | ---: |
| Functions | 8,329 |
| Exact body ranges | 8,459 |
| Multi-range functions | 76 |
| Sum / union of body bytes | 1,811,691 |
| `.text` ownership | 93.912966399% |
| Uncovered bytes | 117,426 (6.087033601%) |
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
  `a97d79aa966a0599eca209940085bfd898a2d028148b474de5169d3af7ac8fb8`
- `run-a/uncovered-runs.tsv`: 621,225 bytes, SHA-256
  `08a90257bc0b8b174ad5f2bcafb982a841fc602fce03457528ec5c9a43f28c46`
- exact owned range-set SHA-256:
  `1db37baf83feda63886aafa6ef6a4988faacf910453487234e7fa249758c4681`
- exact uncovered range-set SHA-256:
  `10456460c9176c7ae503d5db84a67af2b7dd379cd12b72f6d97844c10b6784d2`

The aggregate authority and a subsequent project rehash kept live, tracked, and
the retained POST backup exact at 19 files / 187,009,925 bytes / inventory
`c6cb2a228f110a8c7949d8f337a41fc4f060fb33b959bc11868e5cb315e1df7a`.

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

## What the 117,426 bytes contain in current Ghidra listing state

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
| Exact function bodies | 1,811,691 | 8,459 ranges |
| Decoded instructions outside functions | 18,674 | 5,356 instructions |
| Defined data outside functions | 46,918 | 17,596 data units |
| Listing-unclassified gap bytes | 51,834 | — |
| **PE `.text`** | **1,929,117** | exact closure |

The full 117,426-byte gap has 61,288 bytes whose value is `00`, `90`, or `CC`
and 56,138 other byte values. Of those padding-valued bytes, 39,894 form 5,098
entirely padding-valued runs; mixed runs contain the other 21,394. The
listing-unclassified 51,834-byte partition contains 48,809 padding-valued and
only 3,025 non-padding-valued bytes. Across all gap classes, 1,655 Ghidra
references reach 1,441 distinct unowned targets.

The bounded candidate projection is:

| Mechanical class | Runs | Bytes | Meaning |
| --- | ---: | ---: | --- |
| Padding-only | 5,098 | 39,894 | every byte is `00`/`90`/`CC` |
| Defined-data only/mixed | 202 | 49,965 | current listing contains defined data; classification may still be wrong |
| Loose-instruction only/mixed | 597 | 23,446 | decoded listing instructions, no entry proof by this fact alone |
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

The later D3DX promotion removes another 248 fully decoded loose-instruction
bytes as two DEFAULT-source functions at `0x00595FC9` and `0x00596028`. It
preserves every one of the 8,327 PRE function rows and changes neither the
instruction nor reference census. See the
[`D3DX two-function live-promotion report`](d3dx-gap-two-function-ghidra-live-promotion-2026-08-14.md).

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
  `25109242d94b29e40cc7a83c3c039505050fac60023c73f5b8c638cb74e6fc49`
- `gap-accounting-a/result.ready.json`: 3,399 bytes, SHA-256
  `e735c9757bd5278daba491f3bc25ad650dafaad4cca35662041f17123745b864`
- `gap-accounting-a/gap-classification.tsv`: 839,479 bytes, SHA-256
  `8f8d2fb6e92f68cac00e46e892060f1f68ee9d7de3aab2eb6a328663c7d57372`

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
