# The 34 newly admitted MissionScript functions now have bounded static contracts

Status: reviewed static-contract addendum; live metadata promotion remains separate
Last updated: 2026-08-13
Evidence: MEASURED — exact pristine function bodies, instruction listings,
registry records, current Ghidra readback, and instruction-local source plates;
INFERRED — narrow mechanism wording where an indirect call or analyst-labelled
callee remains unresolved; UNKNOWN — original symbols and signatures, complete
callee behavior, runtime reachability, source equivalence, and rebuild parity.
Verdict: all 34 callable entries added to Ghidra on 2026-08-13 now have a
row-specific `C1_CANDIDATE_PARTIAL` / `STATIC_HYPOTHESIS_ONLY` contract and a
cheapest falsifier. Joined with the sealed dated 8,136-row closure, this gives
bounded static-envelope coverage for all 8,170 currently saved internal
functions: 8,163 C1 and seven C2 in this static-accounting projection, with zero
static `OPAQUE`. This does not change immutable Generation 23, which remains the
runtime/campaign authority at 8,126 functions, 217 C1, ten C2, and 7,899
semantic `OPAQUE` functions.
Specimen: pristine PC retail `BEA.exe`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

## Exact result

The mechanical row owner is
[`mission-script-registry-new-function-static-contracts-2026-08-13.tsv`](mission-script-registry-new-function-static-contracts-2026-08-13.tsv).
It joins one-to-one to the separately promoted
[`mission-script-registry-missing-function-boundaries-2026-08-13.tsv`](mission-script-registry-missing-function-boundaries-2026-08-13.tsv)
by registry index, command, and exact entry address.

| Property | Result |
| --- | ---: |
| Functions / unique registry rows | 34 / 34 |
| Exact pristine body bytes | 3,513 |
| Exact instructions | 1,094 |
| Bodies ending in `RET 0x0C` | 34 |
| Registry labels consistent with the visible body | 12 |
| Registry labels broader than the visible body | 22 |
| Registry labels contradicted by the visible body | 0 |
| Handlers returning allocated script-value wrappers | 14 |
| Instruction-local source-coordinate occurrences | 17 across 15 functions |
| Exact PC / Issue-11 Xbox / US-retail Xbox coordinate matches | 3 |
| New runtime claims | 0 |
| Live or tracked Ghidra mutations in this semantic pass | 0 |

The sealed local inputs and receipts are:

- `local-lab/mission-registry-new34-static-admission-20260813-v1/static-inputs.ready.json`
  — 22,660 bytes, SHA-256 `eb61e7820fce92d2560c37680daef191ecf989fd867c4adef28c4e4deadc5708`;
  34 successful read-only decompiles, 1,094 instruction rows, 3,513 exact body
  bytes, 34 default-metadata readbacks, and zero drift in the disposable 19-file
  Ghidra project;
- `local-lab/mission-registry-new34-static-admission-20260813-v1/source-coordinate-extension.ready.json`
  — 8,701 bytes, SHA-256 `8ab50574feedbd1274ce7ed4eba27c5b487f3f3e4208911e07864cd1507e9733`;
  17 instruction-local coordinate plates across 15 functions and three exact
  three-build matches;
- `local-lab/mission-registry-new34-static-admission-20260813-v1/static-contracts.ready.json`
  — 2,176 bytes, SHA-256 `4741463892875a4d2ef98db51069759d96d610295bfef7d10279bfcc5c5dc53b`;
  exact 34-row join, grade, label-disposition, coordinate, body, instruction,
  and terminal-return accounting. Its pinned contract TSV is 21,608 bytes,
  SHA-256 `86c0c4a0e0d5fe0078cb21f271b4985cb1c4fe89aa035b66215076dfbe784a31`.

Each receipt is fail-closed and reproduced byte-for-byte on a second run. The
tracked TSV contains no decompiler body and no retail-derived asset; it records
only bounded facts, explicit unknowns, and falsifiers.

## What the cohort adds

The 34 bodies divide into four useful mechanism groups:

| Group | Rows | Bounded visible envelope |
| --- | ---: | --- |
| UI and control adapters | 6 | one player-view call, paired guarded message-box calls, two indexed HUD-state writes, and a two-vslot visibility dispatch |
| Object actions and direct writes | 11 | receiver/type gates, segment-controller calls, deploy/undeploy calls, one direct health-product store, and weather-global writes |
| Numeric and vector construction | 5 | vector normalization, angle arithmetic, component replacement, safe-position wrapping, and LCG-derived float construction |
| Queries, animation, effects, and spawning | 12 | nine wrapped queries plus animation-wait, particle-create, and escape-pod construction envelopes |

Fourteen handlers allocate a script-value wrapper and write either that pointer
or null to an output slot. This common shape is now recorded, but the absence of
recovered prototypes means the table does not promote calling conventions or
parameter storage. All 34 default Ghidra names and default signatures therefore
remain unchanged pending their own metadata ceremony.

The registry name is treated only as Tier-2 script-facing vocabulary. Twelve
labels agree cleanly with the visible mechanism (`GotoPlayerCamera`, `Deploy`,
`Undeploy`, `Normalise`, `GetAngle`, `SetY`, `GetWeaponAmmo`,
`GetWeaponCharge`, `IsOverWater`, `GetFloatRand`, `PlayAnimationWait`, and
`SpawnParticle`). The other 22 are deliberately marked `BROADER`: for example,
`SwitchMessagesOn` visibly requests a message-box queue action, while
`SpawnersInUse`, `IsFiring`, and `InJetMode` wrap lower-level predicates whose
complete semantics are still open. None is treated as a contradiction merely
because an analyst-labelled callee is narrower than the shipped command.

## Source-coordinate extension

Fifteen functions contain exact instruction-local source plates. Sixteen of the
17 occurrences cite `MissionScript/IScript.cpp`; the other is an inlined
`monitor.h:24` allocation plate inside `GetTarget`. A coordinate proves only
that the compiler emitted that file/line pair at the named instruction; inlining
remains possible.

Three previously uncontained PC functions also have the same coordinate in the
Issue-11 and US-retail Xbox builds:

| PC function | Coordinate | Issue-11 entry | US-retail entry |
| --- | --- | --- | --- |
| `Normalise @ 0x00534500` | `IScript.cpp:636` | `0x0009D7B0` | `0x0009D7A0` |
| `GetNumber @ 0x00535980` | `IScript.cpp:1143` | `0x0009CC20` | `0x0009CC10` |
| `SpawnersInUse @ 0x00535AF0` | `IScript.cpp:1203` | `0x0009CAA0` | `0x0009CA90` |

This is a sparse instruction-coordinate join, not whole-function equivalence or
an Xbox-to-PC semantic transfer.

## Important bounded findings

- `SetWindVector @ 0x00538300` decodes three floats and stores them at
  `0x00660198`, `0x0066019C`, and `0x006601A0`, then copies an otherwise
  unwritten local stack dword to `0x006601A4`. Whether the fourth write is
  ignored padding residue or behavior with a consumer is explicitly open.
- `HighlightHudPart` and `UnHighlightHudPart` perform unchecked indexed writes
  of two and one respectively into the same global dword array. The array bound
  and state meanings require reader analysis or a copied-runtime probe.
- `GetTarget` wraps an object pointer and maintains a lazily allocated pointer
  set at target `+0x04`. Its outer wrapper-allocation failure writes null. If
  the inner allocation fails, the handler stores null at target `+0x04` and
  still calls the add helper with a null receiver; that helper's consequence
  and destruction symmetry remain open.
- `PlayAnimationWait` has a visible prior-item remove/release path, animation
  lookup and dispatch, 0x228-byte template-copy allocation, queue insertion,
  and context/global writes. Allocation failure still passes null to the queue
  helper, sets the global flag, and stores null at context `+0x38`; the helper's
  null handling and completion behavior remain open.
- `SpawnEscapePod` is the largest new body at 556 bytes / 135 instructions. It
  requests `SpawnerF` data, constructs an actor-shaped object and a large
  descriptor, derives orientation, substitutes receiver position for an all-zero
  returned position, and dispatches an actor vslot. Exact descriptor semantics
  and concrete type remain open.

## Authority boundary and next gate

This addendum extends only the static-envelope accounting projection. It does
not rewrite the sealed 8,136-row TSV, Generation 23, the PC demo map, or any
runtime receipt. It also does not authorize a bulk rename: script command names
are not recovered C++ symbols.

The 34 names/comments/signatures remain a separate future Ghidra ceremony from
the reviewed 75-row normalization of pre-existing registry entries and from the
one-row `CreateExplosion` repair. Before any write, the applicable ceremony must
again prove exact live identity, PRE backup/restore, two scratch replicas,
rollback/adverse controls, collision and alias safety, separate apply/readback,
POST backup/restore, and exact live/tracked equality.

The highest-value semantic follow-up is no longer another boundary census. It
is to choose a coherent five-to-ten-function slice, reproduce one consequential
runtime or rebuild mismatch, and use the row-specific falsifiers to deepen only
the branches and values that matter.
