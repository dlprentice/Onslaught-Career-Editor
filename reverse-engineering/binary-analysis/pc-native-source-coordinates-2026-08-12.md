# The shipped PC executable names its own source files and lines

Status: active, bounded static naming and provenance instrument
Last updated: 2026-08-12
Evidence: MEASURED — 1,559 `push <line>; push <path>` debug-allocator argument
pairs decoded from the pristine specimen, joined to the dated 2026-08-12 Ghidra
name projection and reconciled against the tracked Xbox anchor join; UNKNOWN —
every semantic, boundary and behavioural question, which this instrument does not
address.
Verdict: 827 of the then-current 8,136 functions carry at least one authored source
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

> **WITHDRAWN 2026-08-12 — the section below is measured wrong, by about sixty
> times.** Its audit read a single `Address:` field from the first 2,000
> characters of each document. Function documents list many addresses in tables —
> `functions/IScript.cpp.md` alone carries 45 rows — so almost every documented
> function was counted as undocumented.
>
> Recounting every address in all 1,056 documents under `reverse-engineering/`:
> of the **323** real-named coordinate-covered functions, **318 are mentioned in
> some tracked document and 5 are not**. The claimed frontier of 307 is not
> 307; the floor is 5.
>
> Neither number is the useful one. "Mentioned somewhere" is a weaker bar than
> "has a written contract", and the original measurement never defined which it
> was testing — which is the actual defect. A real coverage figure needs that
> definition first, and lies somewhere between 5 and 307.
>
> The ranking by source file below inherits the same error. Do not quote it —
> the corrected ranking is different in both counts and order.
>
> **Replacement measurement, with the definition stated first.** A function is
> **documented** when a tracked document either (a) is a dedicated per-function
> note whose header pairs its address with it, or (b) contains a table row
> pairing its address with a purpose cell — someone wrote what it does. An
> address appearing only in a wave/probe token list or running prose is
> **mentioned**, which is evidence it was read, not that it was described.
>
> | Tier | Count |
> | --- | ---: |
> | Real-named coordinate-covered functions | 323 |
> | — contracted (dedicated function doc) | 26 |
> | — tabled (row with a purpose cell) | 127 |
> | **= documented** | **153** |
> | — mentioned only | 165 |
> | — absent entirely | 5 |
> | **undocumented** | **170** |
>
> **170**, between the 5 and 307 bounds and near neither. The corrected ranking is
> `MeshPart.cpp` 32, `BattleEngineDataManager.cpp` 31, `WorldPhysicsManager.cpp`
> 21, `oids.cpp` 20, `mesh.cpp` 19, `ParticleSet.cpp` 16 — mesh, particle and
> data-manager territory. The broken measurement pointed at the mission-script VM
> instead, so it would have sent the work to the wrong subsystem entirely.

## Documentation debt — corrected authority

The withdrawn 307-function census formerly repeated here was the broken
single-`Address:` measurement described above. It is not an active frontier.
Under the stated contract-or-purpose-row definition, the corrected gap was
**170 unique real-named coordinate-covered functions**. That documentation gap
is now closed: the five detailed documents cover 29 unique functions and
`functions/coordinate-long-tail.md` has 148 function/file rows covering 141
unique functions; their union is the same 170, not 177. This closes purpose-row
coverage only, not behavioral contracts. The corrected ranking was
`MeshPart.cpp` 32, `BattleEngineDataManager.cpp` 31,
`WorldPhysicsManager.cpp` 21, `oids.cpp` 20, `mesh.cpp` 19 and
`ParticleSet.cpp` 16.

## The instrument is factory-biased, and that explains its shape

Working the ranked gap files exposed a pattern that characterises the instrument
itself. The first five detailed files yielded 18 then-undocumented real-named
functions, now covered by their purpose rows, and almost every one is an
**object factory**:

| Source file | Undocumented | Functions |
| --- | ---: | --- |
| `WorldPhysicsManager.cpp` | 9 | `CreateSquad`, `CreateWeaponByIndex`, `CreateProjectile`, `CreateSpawner`, `CreateCharacter`, `CreateExplosion`, `CreateEffect`, `CreateTrigger`, `InitializeLists` |
| `mesh.cpp` | 4 | `InitStatic`, `Load`, `FindOrCreate`, `OptimizeParts` |
| `ParticleSet.cpp` | 3 | `CreateByType`, `LoadFromArchive`, `LoadParticleSetFile` |
| `oids.cpp` | 1 | `OID__CreateObject` |
| `InitThing.cpp` | 1 | `InitThing__CreateThingByType` |

The reason is structural, not coincidental: coordinates are emitted at
**debug-allocator call sites**, so a function only appears if it allocates. That
selects for constructors, factories and loaders and against pure logic,
rendering and math. `CWorldPhysicsManager` contributes eight consecutive
`Create*` entry points at source lines 145–292, which is the game's central
object factory laid out in order.

Two consequences worth carrying:

- **The instrument is a factory map, not a general function map.** Its 827
  functions are not a random sample of that dated 8,136, and coverage figures derived
  from it must not be read as coverage of the binary.
- **It is unusually well suited to object-lifecycle work.** Every `Create*` above
  arrives with its source line and its constructor callee already attached —
  `CreateProjectile` → `CRound__ctor` ×2, `CreateCharacter` → `CUnit__ctor_base`
  ×3, `CreateExplosion`/`CreateEffect`/`CreateTrigger` →
  `CComplexThing__ctor_base`. The explosion identity has separate vtable and
  caller proof; the coordinate alone did not establish it.
  That is a spawn-path census for free.

`CMesh__Load` is the outlier worth flagging separately: 18,546 bytes spanning
source lines 565–1534 with 82 buffer reads, by far the largest body the
instrument touches.

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
