# The shipped PC executable names its own source files and lines

Status: active, bounded static naming and provenance instrument
Last updated: 2026-08-12
Evidence: MEASURED — 1,559 `push <line>; push <path>` debug-allocator argument
pairs decoded from the pristine specimen, joined to the current tracked Ghidra
name projection and reconciled against the tracked Xbox anchor join; UNKNOWN —
every semantic, boundary and behavioural question, which this instrument does not
address.
Verdict: 827 of the 8,136 known functions carry at least one authored source
file and line number emitted by the compiler into the shipped image. This settles
provenance and naming evidence, not semantics.
Specimen: pristine PC retail `BEA.exe`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

## Result

The retail image passes `__FILE__` and `__LINE__` to its debug allocator, so a
call site looks like `push <line>` then `push <pointer to an authored path>`.
Scanning every known function body for that pair recovers:

| Accounting item | Count |
| --- | ---: |
| Source-path strings present in the image | 164 |
| Coordinates recovered | 1,559 |
| Distinct source paths | 149 |
| Distinct functions covered | 827 |
| Functions carrying coordinates from more than one path | 14 |

The paths are complete and authored, including directory structure — for example
`C:\dev\ONSLAUGHT2\MissionScript\IScript.cpp` and the relative
`C:\dev\ONSLAUGHT2\MissionScript\..\monitor.h` — so they describe the original
project layout rather than bare filenames. The heaviest are
`CPhysicsScriptStatements.cpp` at 269 coordinates, `MissionScript\IScript.cpp`
at 108, `WorldPhysicsManager.cpp` at 90, `PauseMenu.cpp` at 84 and
`MissionScript\AsmInstruction.cpp` at 47.

## Relationship to the Xbox anchor lane

The reconciliation finds 422 of 422 exact file-and-line agreements with
[`xbox-anchor-function-correlation-2026-08-12.md`](xbox-anchor-function-correlation-2026-08-12.md)'s
PC/Xbox join, with zero file conflicts.

**That agreement is method validation, not corroboration, and must not be cited
as two channels confirming each other.** The prior lane's `pcInstruction` column
was measured to be this scan's push-path instruction in all 422 comparable rows,
so both readings come from the same PC instructions.

The contribution is coverage. That lane retained only coordinates having
counterparts in both Xbox builds, because its purpose was cross-platform
correlation: 425 rows over 93 PC functions. Read as a PC instrument in its own
right, the same shipped signal reaches 827 PC functions, so the majority of the
PC image's coordinates had not been surfaced as PC-side evidence.

## Why it matters

It covers subsystems the pinned GPL drop does not contain and which
[`rebuild/PROVENANCE.md`](../../rebuild/PROVENANCE.md) therefore assigns to
byte recovery — the mission-script VM (`IScript.cpp`, `AsmInstruction.cpp`,
`DataType.cpp`), `Unit.cpp`, `mesh.cpp`, `MeshPart.cpp` and `ParticleSet.cpp`
among them. For any covered function the owning source file is a fact about the
shipped build rather than an inference from a chosen name, so it can corroborate
or refute a proposed class attribution the way argument arity checked the
2026-08-12 HUD identities.

It also exposes three functions that remain unnamed in the canonical database
while carrying exact coordinates at `IScript.cpp` lines 1158, 1173 and 1188:
`0x005359D0`, `0x00535A30` and `0x00535A90`. Each tests a flag at `[obj+0x34]`,
calls one health or readiness routine, boxes the result into an allocated script
value with vtable `0x005E4EA4`, and returns `ret 0xc`. Each has zero direct
callers and exactly one pointer reference, which is the shape of a Mission-native
registry entry. No name is proposed here.

## Boundary

A coordinate proves the compiler emitted that file and line at that instruction.
It does **not** prove the enclosing function is wholly defined in that file:
inlining carries coordinates across files, which is why the 14 multi-path
functions are reported rather than smoothed away. The scan covers known function
bodies and the `push <line>; push <path>` ordering only, so 1,559 is a floor and
not a census. Nothing here establishes function boundaries, signatures, runtime
behaviour or reconstruction parity, and no Ghidra mutation was made.

The mechanical owner and its receipts are machine-local under
`local-lab/pc-native-source-coordinates-20260812-v1/`; the derived table is
[`pc-native-source-coordinates-2026-08-12.tsv`](pc-native-source-coordinates-2026-08-12.tsv).
