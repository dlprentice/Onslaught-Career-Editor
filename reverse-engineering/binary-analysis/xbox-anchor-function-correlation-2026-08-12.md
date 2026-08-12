# Xbox source-anchor function correlation and section census

Status: complete, bounded read-only cross-build checkpoint
Last updated: 2026-08-12
Evidence: MEASURED — exact XBE identities, pinned current Ghidra function
inventories, all 1,166 source-coordinate anchors in both Xbox builds, complete
function-to-XBE-section censuses, and byte-identical replay from independently
restored POST-backup projects; UNKNOWN — original source function boundaries,
whole-body equivalence, semantics, runtime behavior, complete ownership within
mixed `.text`, final function denominators, and reconstruction parity.
Verdict: 1,065 anchors are contained by current Ghidra functions in both Xbox
builds and form 379 one-to-one Issue-11/US-retail function pairs with zero
ambiguous components. The other 101 anchors are outside current function bodies
in both builds. This is a countable correlation subset, not a new denominator.

Parent checkpoint:
[Xbox source-line anchors promoted into isolated Ghidra projects](xbox-source-line-anchor-ghidra-2026-08-12.md).

Specimens:

- Issue-11 XBE SHA-256
  `ac07835e4b8cf38312e672cb7dc17f28a732abbc05a5e4f1760aaa78a5377ed9`;
  pinned current inventory: 8,941 functions, SHA-256
  `f977df8a3db7dac228d45e0a4e1b4f55ccfe6916961aa09d6498cc55e62d6b57`.
- US-retail XBE SHA-256
  `e8adc9d6940ae1a5fa9fac0fe28e398bfffd01758c2740a536b930c37c83985b`;
  pinned current inventory: 8,942 functions, SHA-256
  `4c52848496fc266cf4919a9e389335faa46898da799d8e9bd75559be0849e381`.

Those 8,941/8,942 values are current Ghidra discovery counts. They may include
platform and library code and may omit undiscovered functions. They are neither
final ceilings nor substitutes for the separately measured PC-retail inventory.

## Exact anchor-to-function accounting

The read-only exporter validated every Ghidra source-map entry before asking the
current function manager for containment. It retained each function's entry,
name, body ranges, raw-body hash, instruction count, thunk target, calling
convention, parameter count, and return type.

| Measurement | Count |
| --- | ---: |
| Shared instruction-local anchors | 1,166 |
| Contained in current functions in both builds | 1,065 |
| Outside current function bodies in both builds | 101 |
| Asymmetric containment | 0 |
| Distinct Issue-11 containing functions | 379 |
| Distinct US-retail containing functions | 379 |
| Distinct cross-build function-pair edges | 379 |
| One-to-one graph components | 379 |
| Ambiguous split/merge components | 0 |
| Exact translated current-Ghidra-boundary pairs | 378 |
| One-to-one anchor-partition-only pairs | 1 |
| Raw-body byte-identical pairs | 0 |

“Exact translated current-Ghidra-boundary” means the current body ranges,
shape, and anchor/entry translation satisfy the reducer's strict mechanical
test. It does not establish an original source boundary or equivalent behavior.
The zero raw-body-identity count is another reason not to transfer semantics
automatically.

The sole stricter-grade exception is the pair at entry `0x00093130` in both
builds, anchored by `xboxplatform.cpp:1379-1380`. Both current bodies are one
468-byte range with 124 instructions, and their translated ranges and body
shape agree. The two retained anchors move by different deltas, so the pair is
kept at `ONE_TO_ONE_ANCHOR_PARTITION` rather than being promoted to the stricter
boundary grade.

The 101 symmetrically uncontained coordinates remain a separate function-
discovery queue. They prove exact mapped instruction sites, not 101 additional
functions. A control-flow and boundary instrument must decide whether any are
missing functions, fragments, or another kind of compiler artifact.

## Complete XBE-section census

Every current Ghidra function entry and body belongs to exactly one executable
XBE section; zero bodies cross section boundaries, zero entries are in a
non-executable section, and zero functions are external.

| XBE section | Issue 11 | US retail |
| --- | ---: | ---: |
| `.text` | 6,723 | 6,723 |
| `D3DX` | 559 | 559 |
| `XGRPH` | 338 | 338 |
| `DSOUND` | 523 | 524 |
| `WMADECXM` | 36 | 36 |
| `WMADEC` | 122 | 122 |
| `BINK` | 132 | 132 |
| `BINK32` | 4 | 4 |
| `BINK32A` | 8 | 8 |
| `BINK16` | 5 | 5 |
| `BINK4444` | 10 | 10 |
| `BINK5551` | 6 | 6 |
| `BINK16X2` | 1 | 1 |
| `D3D` | 265 | 265 |
| `XPP` | 209 | 209 |
| **Total current Ghidra functions** | **8,941** | **8,942** |

This gives an exact layout partition of 2,218 Issue-11 and 2,219 US-retail
functions into 14 explicitly named SDK/middleware sections. The sole section-
count difference is one additional US-retail `DSOUND` function. It does not
make the remaining 6,723 `.text` functions game-owned: `.text` remains a mixed-
ownership frontier.

All 1,166 retained full paths are case-insensitively identical between the two
builds, cover 139 unique paths, and begin with `C:\dev\XBOnslaught\`. All
anchors and all 379 paired current functions lie in `.text`. No XDK path occurs
among these retained anchors. This proves that the anchored subset came from
the retained XBOnslaught source tree; it does not classify the unanchored
remainder of `.text`.

## PC/Xbox join

The existing 425 PC/Issue-11/US-retail coordinates partition as:

| Current containment state | Anchors |
| --- | ---: |
| Current functions in all three builds | 410 |
| PC current function; both Xbox sites uncontained | 12 |
| PC site uncontained; current functions in both Xbox builds | 3 |

The 410 fully contained coordinates connect 81 current PC functions one-to-one
with 81 of the Xbox function pairs. Across the full 425-row table, 93 currently
known PC functions are touched. The 81-pair subset is suitable for bounded
Version Tracking seeds and independent refutation; it is not source or semantic
equivalence.

## Recovery, replay, and Ghidra boundary

This checkpoint made no Ghidra mutation. The canonical projects already had
fresh POST-anchor backups:

- `D:\BEA-Ghidra-Backups\2026-08-12-xbox-sparse-symbol-post-anchors-issue11`;
- `D:\BEA-Ghidra-Backups\2026-08-12-xbox-sparse-symbol-post-anchors-us-retail`.

The containment and full-section exporters were run read-only against both the
canonical projects and independently restored copies of those POST backups.
All four canonical outputs reproduced byte-for-byte:

- Issue-11 containment SHA-256
  `6ceaf14d4b08832fd22cd0df73a83d415aad8d7823ad4dc960fca37fb3571f39`;
- US-retail containment SHA-256
  `6117bdb87e0877c595c5ebaa6cb57f32ad74872073d3201982be6d4cac3be8a5`;
- Issue-11 section census SHA-256
  `e98f5de6c7d50aecd70b62eaf1813a652a6478092017f8fb26647fadd6f287eb`;
- US-retail section census SHA-256
  `d14636482e2a6fe843e55aa72193cacc4db486ac7ee9d9090f6a469464c7bee1`.

The fail-closed local owner is
`local-lab/xbox-sparse-symbol-ghidra-20260812-v1/function-containment/xbox-anchor-function-correlation.ready.json`,
10,131 bytes, SHA-256
`a9b2a89b2291d9e885396105cf85c97d84c15b1fb60d4c52fef87e46971c01de`.
Two consecutive full seal runs produced identical bytes. It pins the parent
Ghidra checkpoint, both backup-restore receipts, both exporters, the graph
reducer, all canonical and replay exports, and every count above.

Because this phase was read-only, no new backup or tracked Ghidra snapshot was
needed. Any later Version Tracking, function creation, rename, signature, or
comment promotion still requires a fresh recoverable backup and the normal
scratch/apply/readback/refutation gate.

## Next falsifiers

1. Adjudicate the 101 symmetrically uncontained anchors with control-flow and
   boundary evidence before creating any function.
2. Use XDK/library signatures and exact cross-build evidence to partition the
   unanchored mixed `.text` remainder; do not relabel all 6,723 rows as game
   code.
3. Seed a bounded Version Tracking session from the 379 one-to-one pairs and
   the 81 three-platform pairs, retaining ambiguous or raw-different bodies as
   explicit refuters rather than automatic matches.
4. Transfer a name or contract only after the enclosing body, callers/callees,
   state effects, failure behavior, and cheapest falsifier independently pass.
