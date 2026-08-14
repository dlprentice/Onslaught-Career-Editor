# PC-native source-coordinate v3 successor

Status: reviewed integration candidate; predecessor preserved, no Ghidra or
specimen promotion
Date: 2026-08-13
Evidence: MEASURED — pristine PC bytes, the exact 8,170-function projection,
the receipt-pinned 2026-08-12 owner, the reviewed stack-stable intermediate,
two byte-identical v3 scans, focused can-fail controls, and an independent
row-by-row integrity audit. Both coordinate inputs are fail-closed on exact
hash, schema, row count, and function count; UNKNOWN — runtime reachability,
whole-function source ownership, and every semantic or parity claim not
separately proved.
Specimen: pristine PC retail `BEA.exe`, 2,506,752 bytes, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Verdict: the versioned v3 instrument contains the reviewed stack-stable result,
corrects two paths hidden by the old image index, and recovers one additional
CFG-predecessor plate. The final hull-attributed candidate has **1,863
coordinates in 1,002 functions**; its only genuine dataflow addition is
`IScript.cpp:676`. Tested register-carried and ESP-relative forms add zero rows
in this retail projection.

## Immutable predecessor and versioned successor

The 2026-08-12 instrument is historical evidence. This package leaves
[`tools/re_pc_native_source_coordinates.py`](../../tools/re_pc_native_source_coordinates.py)
byte-identical at 5,529 bytes, SHA-256
`98d62226eedcd4c93ebb0aec52d6557007850d9d8b80cfc1210608729b4ba4c6`.
Its frozen [report](pc-native-source-coordinates-2026-08-12.md) and
[1,559-row table](pc-native-source-coordinates-2026-08-12.tsv) also remain
unchanged.

The successor is a separate owner:

- [`tools/re_pc_native_source_coordinates_v3.py`](../../tools/re_pc_native_source_coordinates_v3.py):
  55,188 bytes, SHA-256
  `878403195e6ae48ce68a1e56b1590e9506962e01a18b10dd7df81d6c71a7fa3f`.
- [`tools/re_pc_native_source_coordinates_v3_tests.py`](../../tools/re_pc_native_source_coordinates_v3_tests.py):
  16,621 bytes, SHA-256
  `6cfbcfbe2f194b776e4ba14681475534b232e73d10a1960faecb77418c973757`.
- [Stack-stable intermediate](pc-native-source-coordinates-stack-stable-2026-08-13.tsv):
  1,840 data rows, 293,543 bytes, SHA-256
  `2da8d84135b3b1e4881af62cbf73f202656c091c98bda02e4969ff4efec18a76`.

The integration package was assembled on base `6f1aa3d8` and landed on a
later descendant of that commit. It does
not include another lane's Ghidra store, function-name-table, or inherited
metadata changes.

## Pinned inputs and populations

- Current projection:
  `ghidra-function-name-table-2026-08-13.tsv`, exactly 8,170 functions,
  SHA-256
  `d61f9866d9dbf67bae817a710d50a1a136b7c2156ec6eb7f862d82dea70f26fd`.
- Frozen coordinate owner: 1,559 data rows plus one header (1,560 physical
  lines), 827 distinct functions, SHA-256
  `eb2abec9ca8532e11ed89e4f0f1b39fbbf84501d7e93d297717cfaa996bca90f`;
  exact schema `sourcePath, sourceLine, functionVa, functionName, pushLineAt,
  pushPathAt`.
- Reviewed stack-stable intermediate: 1,576 adjacent rows plus 264 gapped
  rows, 1,840 coordinates in 993 functions, SHA-256
  `2da8d84135b3b1e4881af62cbf73f202656c091c98bda02e4969ff4efec18a76`;
  exact schema `sourcePath, sourceLine, functionVa, functionName, pushLineAt,
  pushPathAt, pairingMode, interveningInstructions, consumerAt, consumerVa,
  consumerName`.
- V3 hull-attributed candidate: 1,863 coordinates at 1,862 accepted call sites
  in 1,002 functions. The shared `IScript` consumer has two valid predecessor
  line values, which is why coordinates exceed accepted call sites by one.

These name counts answer different questions and must not be substituted for
one another:

| Population | Functions | Real-named functions |
| --- | ---: | ---: |
| Frozen rows using names stored on 2026-08-12 | 827 | 323 |
| The same frozen 827 addresses rejoined to the current projection | 827 | 347 |
| Current stack-stable intermediate | 993 | 512 |
| Current v3 hull-attributed candidate | 1,002 | 514 |

The predecessor's image-path index expected 164 paths. The corrected v3 index
finds 166 exact drive-rooted, NUL-terminated source paths; 165 are used by an
accepted candidate. These are image-index populations, distinct from the 149
paths used by frozen rows and the 163 paths used by the stack-stable
intermediate.

## Result and genuine novelty

| Result | Coordinates | Distinct functions |
| --- | ---: | ---: |
| Frozen owner | 1,559 | 827 |
| Stack-stable intermediate | 1,840 | 993 |
| V3 candidate | **1,863** | **1,002** |
| Genuine delta over frozen owner | +304 | +175 net |
| Genuine delta over stack-stable intermediate | +23 | +9 net; 12 functions touched |

The 1,863 rows partition exactly as follows:

- 1,559 rows already in the frozen owner.
- 17 adjacent rows exposed by the current projection.
- 264 reviewed stack-stable gaps.
- 22 path-index corrections.
- 1 CFG-predecessor dataflow recovery.

All 1,863 retail rows ultimately pass path and line as immediate `push`
operands. Register-carried constants, simple derived register constants, and
explicit ESP-relative stores are supported and regression-tested, but produce
zero accepted retail rows. They remain instrument capability, not discovered
retail evidence.

### Corrected path index: 22 rows

The predecessor searched maximal printable runs. A printable float byte directly
before each of these paths caused the complete run to fail path validation:

- `0x0062CE78 C:\dev\ONSLAUGHT2\Hud.cpp`: eight rows at lines 93, 95,
  311, and 315 across normal and unwind functions.
- `0x006316BC C:\dev\ONSLAUGHT2\PolyBucket.cpp`: fourteen rows at lines
  118, 332, 359, 379, 473, 1136, 1164, 1177, 1178, 1226, and 1242.

V3 indexes a drive-rooted path at its actual start and still requires its exact
NUL terminator. These 22 rows are source-path-index recovery, not dataflow
recovery.

### CFG predecessor: one row

The sole coordinate that needs control-flow predecessor evidence is
`C:\dev\ONSLAUGHT2\MissionScript\IScript.cpp:676` in
`IScript__IsNumberBetween` (`0x005347B0`):

- line argument: `0x005347F6`;
- jump to shared path argument: `0x00534842`;
- direct `CDXMemoryManager__Alloc` call: `0x00534850`;
- ordered witness SHA-256:
  `f3e39ed065baebc6370e120f6bebb7ca3546ce509517830c7aa7c3b8891e4b05`.

The same path/call has the already-known fallthrough line 683. Concrete CFG
predecessor paths preserve the two line values as two coordinates without
merging them into a guess.

## Reproduced stack-stable omissions

The predecessor cleared a possible line on every intervening non-`push`.
The stack-stable successor correctly retained a line across instructions that
neither changed ESP nor crossed control flow. The preregistered
BattleEngineData examples reproduce exactly:

| Coordinate | Function | Line argument | Path argument | Consumer call | Ordered witness SHA-256 |
| --- | --- | --- | --- | --- | --- |
| `BattleEngineDataManager.cpp:32` | `CBattleEngineData__Initialise` `0x0040F590` | `0x0040F594` | `0x0040F598` | `0x0040F5A6` | `f5a5f31cf33850d5ae0a38f637ca3306a3313e18c42429e74cb9985a45faf728` |
| `BattleEngineDataManager.cpp:35` | `CBattleEngineData__Initialise` `0x0040F590` | `0x0040F5BD` | `0x0040F5C5` | `0x0040F5E5` | `226ec681c048d4df06b1a33eae9a35617656f3df9bcaaa5eb58160b37fffdaf8` |
| `BattleEngineDataManager.cpp:64` | `CBattleEngineData__Initialise` `0x0040F590` | `0x0040F781` | `0x0040F789` | `0x0040F7A9` | `2eb79a0c67b3770e85b5ae3871aae0ebd59082e599d740e81282bd0ff1364cab` |

The complete 281-row intermediate delta over the frozen owner is 264
stack-stable gaps plus 17 current-projection adjacent rows. V3 requires both
owners as inputs and validates each exact hash, ordered schema, data-row count,
and distinct-function count before scanning. Even a header-plus-one-row
truncation of either input fails rather than publishing a smaller apparent
superset.

## Exact ranges versus projection hulls

The projection TSV supplies each function's `bodyMin`/`bodyMax` hull. V3 scans
those hulls and therefore observes 2,040 direct calls to its three proven
consumers. The exact body-range ledger contains 2,039 of those consumers.
Containment was independently rejoined to the 8,287-range export owned by the
[current text-ownership report](current-text-ownership-2026-08-13.md): its
machine-local `export/body-ranges.tsv` is 1,183,469 bytes, SHA-256
`6703b759ac18528d61c4ad6f646f0fd6933eaf2a8892617f3ecc24b0ef8e0aae`.

The sole distinction is the inherited
`CPhysicsScriptStatements.cpp:212` row attributed to function registry parent
`0x00437490`: its line/path pushes at `0x00437A27` / `0x00437A2C` are inside
the exact body, but its consumer at `0x00437A3A` lies outside that exact range.
The hull manifest retains the historical row so it remains a strict superset
of the frozen and stack-stable owners, but it is not counted as an
exact-range-contained consumer. Thus:

| Consumer population | Direct calls | Accepted call sites | Coordinate rows |
| --- | ---: | ---: | ---: |
| Projection hull | 2,040 | 1,862 | 1,863 |
| Exact-range-contained consumer | 2,039 | 1,861 | 1,862 |

This row is inherited; all 23 additions over the stack-stable intermediate have
exact-range-contained consumers. No Ghidra boundary change is proposed or
inferred from this distinction.

## Conservative rule and false-positive controls

At each direct call to one of the three already-proven consumers, v3 enumerates
at most 1,024 concrete intraprocedural predecessor paths and 128 instructions
per path without crossing another call. It executes each path in a small
stack/register abstract domain and accepts only when all four consumer slots
are assigned, `[ESP+8]` is exactly one of the 166 indexed NUL-terminated paths,
and `[ESP+12]` is a line in `1..99999`.

Eligible consumers are only:

- `OID__FreeObject_Callback` at `0x00449D40`;
- `CMemoryHeap__Alloc` at `0x004A1810`;
- `CDXMemoryManager__Alloc` at `0x005490E0`.

The hull scan rejects 178 call sites: 158 have no predecessor path proving all
four exact arguments, 14 carry a non-path source argument, and six reach the
1,024-path bound. The six bound calls have no exact indexed path reference.
Across the projection, all 1,862 exact path-reference sites are immediate
pushes and every site is accounted for by at least one coordinate.

Focused controls reject an overwritten path slot, a pointer into a source
string, misleading non-path pointer `0x00662B2C`, a call to an unproved
consumer, an ESP-relative plate with one argument-slot hole, and a surplus push
that shifts the apparent argument plate. The can-fail pass detects its three
instruction mutations plus header-and-one-row truncations of both coordinate
inputs, five of five. These controls limit false positives; they do not prove
an unbounded search or a different consumer family would add nothing.

## Determinism and reproduction

Fresh ignored `run-6` and `run-7` directories are byte-identical for every
immutable output:

| Output | Bytes | SHA-256 in both runs |
| --- | ---: | --- |
| `candidate-manifest.json` | 2,805,768 | `0678cbae9353bab0f44f35ba7395a09a5a8a1857b385b49b6d076f4cee363adc` |
| `candidate-manifest.tsv` | 1,157,987 | `7e873dbb2dff2284b73803026418382293d4b6a33d98868ec3ea8f99cce9b036` |
| `rejected-consumer-calls.tsv` | 86,117 | `8dfa47f43c5d3d4ee32d20baa80435e976cd525ff49eba4c1ddac90cc064e011` |
| `scan.ready.json` | 4,294 | `5412b9d9a64672d4d1e777a20d18bccb41dcd2fbd92af13680b1ac89bd4161d7` |

The earlier `run-4` and `run-5` outputs remain preserved as the superseded
pre-input-pinning replay. The writer refuses to overwrite any result. `--check`
recomputes all bytes and compares them without mutation. An independent
read-only pass verified all 1,863 unique coordinate keys, exact path bytes,
line/path pushes, direct call targets, ordered witness hashes, output receipt
hashes, and replay identity.

```powershell
py -3 tools\re_pc_native_source_coordinates_v3_tests.py
py -3 tools\re_pc_native_source_coordinates_v3_tests.py --prove-can-fail
py -3 tools\re_pc_native_source_coordinates_v3.py `
  --specimen <pristine-BEA.exe-path> `
  --projection reverse-engineering\binary-analysis\ghidra-function-name-table-2026-08-13.tsv `
  --baseline-coordinates reverse-engineering\binary-analysis\pc-native-source-coordinates-2026-08-12.tsv `
  --provisional-coordinates reverse-engineering\binary-analysis\pc-native-source-coordinates-stack-stable-2026-08-13.tsv `
  --output-dir <fresh-ignored-output-directory> `
  --expected-projection-functions 8170 `
  --expected-projection-sha256 d61f9866d9dbf67bae817a710d50a1a136b7c2156ec6eb7f862d82dea70f26fd
```

## Integration validation

- V3 focused regressions: 19/19 pass, including the exact frozen/intermediate
  identities and populations, 323/347 name reconciliation, three reviewed
  intermediate anchors, ESP-slot-hole rejection, and surplus-push rejection.
- V3 can-fail mutations: 5/5 detected, including header-plus-one-row
  truncations of both coordinate inputs.
- Full v3 recomputation against the tracked intermediate: `CHECK_PASS`, with
  the exact output hashes above.
- Independent exact-range join: 2,040 hull / 2,039 exact calls, sole outside
  consumer `0x00437A3A`, and all 23 additions exact-range valid.
- Tool-runner registration self-test: pass; the current v3 suites pass directly.
- Python compilation, public-payload safety, documentation headers,
  function-name assertions, evidence-register header, and `git diff --check`:
  pass.
- The repository-wide Markdown link gate still reports 13 pre-existing missing
  `references/` or ignored-local-lab targets. None is in a changed file; a
  focused replay resolves all 167 local links across the three changed
  Markdown files.
- An earlier pre-input-pinning run of the optional complete 56-suite tools
  matrix exceeded the external 599-second command cap after passing the then-v3
  suites and many unrelated suites, so no full-matrix PASS is claimed. Its one
  orphaned test child was stopped by exact PID after the timeout; concurrent
  tasks were left untouched.

## Claim boundary

A row proves only that the named pristine bytes place the recorded source path
and line in the recorded known consumer's argument slots along the recorded
instruction path. Projection-hull attribution and inlining can cross exact
function or source-file boundaries. No row proves whole-function authorship,
an original C++ symbol, signature, runtime reachability, inputs, outputs,
writes, failure behavior, semantics, or reconstruction parity. The generated
instruction-bearing manifests remain ignored local review evidence; this
package promotes only the reusable v3 instrument, its focused tests, the
reviewed stack-stable intermediate, and this bounded report.
