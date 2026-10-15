# World initializer copy and load boundaries

Status: active — copy effects and seven loaders measured in isolated original code; Spawner loading remains static evidence
Last updated: 2026-09-26
Summary: selective initializer copies, distinct Squad overloads, versioned field reads and source/retail limits for reconstruction.
Evidence: MEASURED — complete pristine instruction bodies, pinned source comparison, original Copy execution and seven original loaders with an intercepted reader; runtime limits are stated below.

Specimen: `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`,
2,506,752 bytes, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source: `references/Onslaught` at
`5352a81cdb838b145a57f7febc5d9fc4b0129ebb`; `InitThing.h` SHA-256
`5a7132f3d0fe5f95a8696675c99ef19fa6ddcc941d9065c7efd3018beab82fef`.
Field names below come from that header and are matched to complete retail
instruction bodies. They do not certify the entire source object layout.

## Selective copying

`CInitThing::Copy` at `0x0040e1b0` receives the destination in ECX and a source
pointer on the stack, then returns with `RET 4`. It copies only these byte ranges,
relative to the two objects; all ranges are half-open:

| Range | Correspondence in `InitThing.h:144–168` |
| --- | --- |
| `[+0x04,+0x50)` | Position including its fourth word, orientation matrix and Euler values |
| `[+0x60,+0x68)` | Orientation mode and mesh number |
| `[+0xa0,+0xa8)` | Allegiance and target |
| `[+0xac,+0x3ac)` | Three complete 256-byte script/name/spawn-script arrays |
| `[+0x3ac,+0x3b4)` | Active and attach-script fields |

The vptr, velocity `[+0x50,+0x60)`, collision settings `[+0x68,+0xa0)`,
force radius `+0xa8`, spawned-by pointer `+0x3b4` and waypoint field `+0x3b8`
remain unchanged. A whole-object clone does not implement this operation.

The derived routines preserve those omissions and add these copies:

| Source method and retail entry | Additional writes |
| --- | --- |
| `CStartInitThing::Copy`, `0x0046d270` | Plane-mode flag `+0x3bc`, player number `+0x3c0` |
| `CTreeInitThing::Copy`, `0x0048cba0` | Completeness field `+0x3bc`, full 256-byte tree-type array `+0x3c0` |
| `CSpawnerInitThing::Copy`, `0x0048ccd0` | Five DWORDs `[+0x3bc,+0x3d0)` and two full arrays `[+0x3d0,+0x5d0)` |
| `CSquadInitThing::Copy(CSquadInitThing*)`, `0x0048d7d0` | Amount `+0x3bc`, full unit-name array `+0x3c0`, mode `+0x4c0` |
| `CWallInitThing::Copy`, `0x0048d910` | Length `+0x3bc`, life `+0x4c0`, wall-type string `+0x3c0` through its first NUL only |
| `CCutsceneInitThing::Copy`, `0x0048da80` | Both full arrays `[+0x3bc,+0x5bc)` |
| Shared body `0x0048dbe0` | One DWORD `+0x3bc`, interpreted as sphere radius or unit stats pointer by the holder |

Squad has two overloads. Its primary table `0x005dc1b0` contains base Copy
`0x0040e1b0`, Squad Load `0x0048d8d0`, then typed Copy `0x0048d7d0`.
The `Copy(CInitThing*)` override at `InitThing.h:645–649` delegates only to
the base. Selecting it does not copy the Squad-specific fields. The second
overload at lines 651–663 occupies slot 2.

`0x0048dbe0` is present in Sphere (`0x005dc15c`), Unit (`0x005dc1c0`) and
BattleEngineInitThing (`0x005dcad4`) slot 0. Sphere and Unit are different
direct children of CInitThing. The shared code does not justify choosing one
exclusive source owner. Its complete 209-byte body has SHA-256
`c459fbac5f3d57e80271bc525ba1feb295b17932222595d1deebd0a209187e5a`.

## Loading and omitted fields

The loaders take a signed 16-bit version in a stack slot and a buffer pointer
in the next slot; their return cleanup is eight bytes. This is distinct from
the saved Ghidra display type of some version arguments, which remains `int`.
Skipped fields are not cleared by these routines. Constructor/default state
must therefore be considered separately when reconstructing world loading.

The base loader `0x0040e280` matches `InitThing.h:170–356`:

| Signed version | Base load path |
| --- | --- |
| `<=16` | XYZ, matrix, Euler values, velocity, one discarded DWORD, orientation mode, two discarded DWORDs, mesh, allegiance, then target. No base strings are read. |
| `17–19` | XYZ, Euler values, mesh, allegiance, target, then script string |
| `20–27` | The preceding modern numeric fields, script, then name string |
| `28–33` | The preceding fields, plus spawn-script string |
| `34–45` | The preceding fields, plus active DWORD |
| `>45` | The preceding fields, plus attach-script DWORD |

No path loads the fourth position word. The modern paths do not load the legacy
matrix or velocity. This is an ordered read contract, not a claim that all
serialized versions are used by shipping levels.

| Derived loader | Reads following the base path |
| --- | --- |
| Start `0x0046d350` | Plane mode above version 14; player number above version 25 |
| Tree `0x0048cc90` | Tree-type string above version 17; does not read the completeness flag |
| Squad `0x0048d8d0` | Amount always; mode above version 28; does not read the unit-name array |
| Wall `0x0048da20` | Length always; life and wall-type string from version 31 |
| Cutscene `0x0048db80` | File string always; link string from version 32 |
| Sphere `0x0048dcc0` | Four-byte radius always |

Spawner `0x0048ce00` **inlines** the base load. Its additional arms use signed
thresholds `16/20/21/22/24/27/33/43`, matching `InitThing.h:454–619`.
The oldest arm reads a fixed 256-byte spawn-unit name; later arms read a
NUL-terminated one. Versions 23–27 also read the **base** spawn script at
`+0x2ac`; only versions above 43 read the derived spawner script at `+0x4d0`.
Those two fields cannot be conflated.

Base, Tree, Cutscene and variable-string Spawner loops increment BL and
sign-extend it for indexing. After index 127, the next destination is string
base minus 128; these are not bounded 256-character readers. Wall increments
a full-width pointer but also has no length guard in this body. These are
malformed-input findings, not a tested file-admission policy. The isolated run
below reproduces the Base/Tree/Cutscene wrap and Wall's different indexing;
Spawner remains static evidence. Valid-data compatibility and safe rejection
of malformed inputs remain separate questions.

## Executed evidence and limits

On September 26, the existing native ELF32 experiment technique executed all
eight unchanged Copy bodies at their original addresses. Each linked body was
compared with pristine bytes before execution. Sixty-four cases cover disjoint
objects and self-copy, with terminators at offsets 0, 3, 127 and 255 within
the array at `+0x3c0` (Wall's string). Other arrays are not independently
length-varied.

Every disjoint source byte differs from the destination before execution.
The complete `0x600`-byte source and destination are compared afterwards,
including the exact expected changed-byte set. Stack cleanup, nonvolatile
registers, stack sentinels and outer memory guards also pass. Counterfactual
output comparisons reject whole-object copying, base-only typed Squad copying,
and fixed-256-byte Wall copying; no mutant retail bodies are executed.

Driver: `local-data/test-runs/re-audit-20260926/initializer-copy/original_copy.py`.
Final receipt and per-case inputs/outputs:
`local-data/test-runs/re-audit-20260926/initializer-copy/run-owwz73wg/`.
That run's frozen `driver.py` has SHA-256
`f3e88de4489eacb20e5a181f444de6174ed9aff63916ec8b947fc65b57171564`;
`results.json` has SHA-256
`4d7eac71c3763bb6a95301de154db77ca64d95476f31e4fda6e1601a782718fc`.
The earlier `run-0ka4qk1m/` is retained: independent review found coincident
source/destination pattern bytes, so the final run uses complementary bytes.
The child allows read, write and exit syscalls; the harness uses stdin/stdout.
The filter does not restrict their file descriptors. No game, Windows services,
original saves, devices or desktop are involved.

Neither self-copy nor separate objects establishes behavior for distinct
overlapping objects.

### Original loaders with intercepted reads

The separate loader experiment executes the unchanged Base, Start, Tree,
Squad, Wall, Cutscene and Sphere bodies at their original addresses. The only
external entry, `0x00548570`, is replaced with an authored full-read service
that copies input bytes and logs destination, length, input position and buffer
receiver. It preserves the callee-saved registers and returns with `RET 8`.
The original `CDXMemBuffer` implementation is **not** executed by this harness.

All **1,288 cases passed**: seven loaders, 23 signed versions, four string
lengths (0, 3, 127 and 128), and two different upper words in the version stack
slot. Versions are `-32768, -1, 0, 14–20, 25–34, 45, 46, 32767`.
These are 1,072 distinct input payloads; some string-length selections repeat
paths that read no strings. The two tested upper words give identical results;
the complete instructions additionally establish use of the signed low word.
All bytes supplied by the read service differ from the
initial object pattern; full `0x700`-byte snapshots, exact final changed-byte
sets, ordered read records, receiver identity, consumed bytes, stack cleanup,
callee-saved registers and outer guards are checked. Logged writes plus final
snapshots do not establish every transient store made inside the loader.

The legacy base path performs 15 reads totaling 116 bytes. Three reads discard
DWORDs into stack scratch: raw instructions establish that the compiler reuses
the incoming buffer and version argument slots. The executed log confirms one
scratch destination followed by two writes four bytes below it. These argument
slots are not immutable canaries. Modern paths start with nine reads totaling
36 bytes, then the strings and optional fields listed above.

A terminator at index 128 is written at string base minus 128 in the signed
loops. Wall instead writes at base plus 128. These are bounded experiments on
allocated memory, not approval to accept malformed world files in the rebuild.
No short reads, EOF behavior, constructor defaults, whole-file validation or
Spawner execution are covered.

Generator: `local-data/test-runs/re-audit-20260926/initializer-load/original_load.py`.
Frozen driver, ELF and per-case inputs/outputs:
`local-data/test-runs/re-audit-20260926/initializer-load/run-5iwdk7m0/`.
The frozen `driver.py` has SHA-256
`5c97d3d277b9dac1cd50499bd6b11aeccdca67fa512683926248243cc8dbcc46`;
`results.json` has SHA-256
`3eb60b5fbfe51f7e76b31acd914564bc9d5bf7b539b491853ab3e5f4414f9477`.
Independent review checked the seven PE/ELF body matches, the emitted harness,
all case identities and coverage, and 126 retained input/output pairs spanning
all bodies and the version/string boundaries. The root run executed all cases.

No complete retail level-load, malformed-file admission, GPU, audio or player
acceptance is claimed. The next falsifiers are original-reader short/zero reads,
the inlined Spawner loader and a controlled full-game construction trace on copies.
For the rebuild, compare constructor defaults, copy overload selection and
untouched bytes before interpreting a downstream spawn mismatch.
