# Stuart's 50,266-line Onslaught source is deeply mapped, but it is a partial internal lineage—not the Steam game

Status: active canonical synthesis of the pinned Stuart Gillam source corpus and
its current reverse-engineering/rebuild use; the source files remain the
line-level primary evidence
Last updated: 2026-07-29
Verdict: **The pinned `references/Onslaught` drop is an exceptionally valuable
but incomplete architecture corpus: 106 C/C++ files (52 `.cpp`, 54 headers),
50,266 physical source lines, 1,354,693 source bytes, 254 distinct quoted
include targets, and 202 targets absent even after case-insensitive basename
recovery (204 do not resolve by their written relative paths). It exposes the real object model,
20 Hz event/game architecture, Battle Engine simulation, Career graph,
frontend, input, audio, resource, memory, and platform algorithms. It does not
contain a build system, tests, or enough dependencies to compile; it is not the
exact Steam source tree; mutually exclusive PC/Xbox/PS2/editor/debug bodies
coexist in the text; and released behavior still belongs to controlled Steam
runtime and pristine-binary evidence. This file is the integrated source master
and work queue, not a claim that every textual body is a released Steam
function or that the absent source has been recovered.**
Evidence: SOURCE + MEASURED — complete read-only scan of every tracked file at
Onslaught commit `5352a81cdb838b145a57f7febc5d9fc4b0129ebb`, its Git tree and
history, all quoted/system includes and conditional directives, source-derived
function/type/table inventories, current Ghidra readback and source-path/RTTI
ledgers, current rebuild source, focused byte crosswalks, and controlled-runtime
findings. Source-only, retail-static, runtime, rebuild, inferred, and unknown
claims are separated below.
Specimen: retail addresses and byte claims use
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, 2,506,752 bytes,
MD5 `3b456964020070efe696d2cc09464a55`, SHA-256
`74154BFAE14DDC8ECB87A0766F5BC381C7B7F1AB334ED7A753040EDA1E1E7750`,
read-only. The installed `BEA.exe` is intentionally patched and is not the
static specimen. No game executable, Ghidra project, retail data, or installed
game file was mutated for this document.

“Baseline” here means the repository-designated unpatched retail specimen. It
is pristine only relative to the project's patch catalog; this research does
not establish its Steam depot identity.

---

## Purpose and reading contract

This is the single narrative master for Stuart's partial Onslaught source and
its use in the Battle Engine Aquila reverse-engineering/rebuild project. It
answers five different questions without pretending they are one:

1. What exactly is present in the pinned source drop?
2. What architecture, algorithms, data formats, names, and constants does that
   text establish?
3. Which parts correspond to the shipped Steam executable, and with what
   strength?
4. Which source-shaped behaviors are present, absent, superseded, or still
   provisional in `rebuild/`?
5. Which source facts should drive the next Ghidra, runtime, data, and rebuild
   investigations?

The companion [`../ghidra-functions.md`](../ghidra-functions.md) is the executable-side
master. [`../installed-corpus-census.md`](../installed-corpus-census.md) is the installed-data master. Their
relationship is:

```text
../source-code/stuart-source-synthesis.md        architecture, names, algorithms, intent
          │
          ├── static crosswalk ──> ../ghidra-functions.md
          │                         shipped code, addresses, ABI, bytes
          │
          ├── data contract ─────> ../installed-corpus-census.md
          │                         authored files and finite registries
          │
          └── implementation ────> rebuild/
                                    original reconstruction and tests
```

The source text is already the atom-level store for every statement and body.
This document therefore does not paste 50,266 lines of GPL source into a stale
second copy. It records every global denominator, every source unit, the
dependency and target graph, the finite tables, the subsystem/function atlas,
the known retail agreements and deltas, the rebuild crosswalk, and exact source
locations needed to inspect an individual claim.

### Evidence vocabulary

| Grade | Meaning in this file |
| --- | --- |
| **SOURCE** | Directly present in the pinned source. Establishes text, naming, ownership, algorithm, and developer intent for that lineage. |
| **CORPUS-MEASURED** | Counted mechanically from the exact pinned tree: files, bytes, lines, includes, definitions, tables, markers, or Git objects. |
| **RETAIL-STATIC** | Independently read from the repo-designated unpatched baseline executable, current Ghidra readback, RTTI, shipped strings/tables, or disassembly. |
| **RUNTIME** | Observed in a controlled copied-retail execution and bounded to that captured path. |
| **REBUILD** | Describes current original reconstruction code or tests. It cannot prove what retail did. |
| **INFERRED** | Best current explanation joining stronger evidence. A falsifier is required for material claims. |
| **UNKNOWN** | Not established; the missing build input, byte read, capture, or focused test is named where consequential. |
| **HISTORICAL** | A prior source map, upload record, or audit result retained for provenance but not current authority. |

### Authority rule

For released Steam behavior, use:

```text
controlled retail runtime
        > unpatched-baseline retail static evidence
        > pinned Stuart source
        > provisional reconstruction design
```

For implementation, the efficient default is still “port Stuart's shape first,
cite the file and line, and override only when retail measurement proves a
delta.” That is an engineering strategy, not an assertion that source and Steam
are interchangeable.

### Master map

- [Executive state](#executive-state)
- [Provenance, history, and license boundary](#provenance-history-and-license-boundary)
- [Exact corpus census](#exact-corpus-census)
- [Buildability and dependency graph](#buildability-and-dependency-graph)
- [Targets and conditional compilation](#targets-and-conditional-compilation)
- [Source architecture spine](#source-architecture-spine)
- [Core object and lifetime systems](#core-object-and-lifetime-systems)
- [Game loop and event scheduler](#game-loop-and-event-scheduler)
- [Battle Engine simulation](#battle-engine-simulation)
- [Career, save shape, and progression](#career-save-shape-and-progression)
- [Frontend, Goodies, input, and camera](#frontend-goodies-input-and-camera)
- [Rendering and DirectX](#rendering-and-directx)
- [Audio and music](#audio-and-music)
- [Resources, I/O, memory, and containers](#resources-io-memory-and-containers)
- [Source-to-Steam crosswalk](#source-to-steam-crosswalk)
- [Source-to-rebuild crosswalk](#source-to-rebuild-crosswalk)
- [Canonical progress queue](#canonical-progress-queue)
- [Per-unit census](#appendix-a-complete-source-unit-census)
- [Finite source registries](#appendix-b-finite-source-registries)
- [Missing quoted includes](#appendix-c-complete-missing-quoted-include-registry)
- [Shipped source-path lower bound](#appendix-d-shipped-source-path-lower-bound)
- [Reproduction and evidence map](#appendix-e-reproduction-and-evidence-map)

## Executive state

| Question | Current exact answer |
| --- | --- |
| Pinned commit | `5352a81cdb838b145a57f7febc5d9fc4b0129ebb` |
| Pinned tree | `7a8d0a83257ff7a2e9831455eca576ade11decbd` |
| Working state | Clean submodule at the pin during this pass |
| Git entries | 108: 106 source files, `README.md`, `LICENSE` |
| C++ units | 52 `.cpp` |
| Headers | 54: 53 `.h` plus uppercase `DX.H` |
| Source bytes | 1,354,693 |
| Source lines | 50,266 physical lines |
| Whole tree bytes | 1,390,527 |
| Encoding/newlines | All 106 source files are 7-bit ASCII, no BOM, CRLF-only |
| Layout | Flat directory; 52 implementation units, usually paired with headers, plus `DX.H` and `membuffer.h` |
| Build files | None: no solution, project, makefile, CMake, or other build owner |
| Tests | None in the source project |
| Quoted include occurrences | 827 |
| Distinct quoted targets | 254 after case-insensitive slash normalization |
| Basename-availability result | 52 present targets / 202 absent targets |
| Literal relative-path result | 50 present targets / 204 absent targets |
| Files with quoted includes | 98 of 106 |
| Files touching an absent target | 82 of 106 |
| Basename-availability occurrences | 292 resolved / 535 unresolved |
| Literal relative-path occurrences | 290 resolved / 537 unresolved |
| Distinct resolved file-to-file edges | 290 under basename availability |
| Angle-bracket includes | 46 occurrences, 14 distinct names |
| Conditional directives | 498 `#if/#ifdef/#ifndef/#elif` directives, 111 exact normalized expressions |
| Function implementation census | 1,855 physical textual body blocks / 1,857 target-conditional definition heads; neither is a one-target linker count |
| Callable declarations without bodies | 1,013 |
| Types | 110 class bodies, 13 struct-body occurrences, 45 enum bodies / 312 enumerators |
| Steam source-path evidence | 166 case-preserving `C:\dev\ONSLAUGHT2\...` strings; 163 case-insensitive full paths; 162 case-insensitive basenames |
| Drop/Steam-path basename overlap | 28 |
| Steam-path basenames absent from drop | 134, a lower bound because only assert-bearing paths survive |
| Drop basenames without a shipped path literal | 78; absence of an assert path is not evidence that the code was absent |
| Known exact retail use | Hundreds of current symbols carry source-corresponding names; consequential functions still require byte/body review |
| Strongest new crosswalk in this pass | high-confidence `CBattleEngine::Damage` correspondence at retail `0x0040A890`, including the missing fourth stack argument and one narrow out-of-invariant body delta |

### What the source settles

- The engine is a strongly object-oriented C++ game built around global
  subsystem singletons, virtual interfaces, monitored pointers, scheduled
  events, resource archives, platform-selected backends, and an authored
  script/data layer.
- The source model uses `GAME_FR = 20.0f` and `CLOCK_TICK = 0.05f`
  (`thing.h:28-29`), with model updates separated from interpolated rendering.
- The supplied Battle Engine, controller, Career, frontend, camera, sound,
  resource, archive, memory, and platform implementations expose real developer
  names and algorithms.
- The supplied source is multi-target text, not a coherent single build. PC,
  Xbox, PS2, editor, resource-builder, development, profiling, and debug
  branches coexist.
- The source drop is partial. High-value shipped owners such as `World`, `Unit`,
  `UnitAI`, `Weapon`, `Hud`, `Cockpit`, `BattleLine`, `MessageBox`, Map/MapWho,
  Landscape, PhysicsScript, the MissionScript VM, and core math implementations
  are absent.

### What the source does not settle

- It does not prove released Steam timing, rendering, input mapping, save
  bytes, audio output, or gameplay outcomes where the retail binary/runtime has
  not been checked.
- It does not prove a total original source-file count. The often-repeated
  “117 of 169 missing” has no surviving primary inventory.
- The 202 absent quoted includes are dependency names, not 202 missing original
  files and not a count of missing `.cpp` implementations.
- A textual function body behind mutually exclusive preprocessor conditions is
  not proof that the Steam compilation contained that body.
- A current Ghidra name matching a source name is not proof of byte identity,
  correct prototype, active branch, or runtime parity.
- A source-only constant is not automatically active. The canonical example is
  `engine.h`'s dead `DEFAULT_Z_FAR = 256`; active source paths use 700, and
  retail agrees with the active path.

## Provenance, history, and license boundary

### Pin and upload history

The repository has six commits. Their timestamps describe public upload
history, not original production revision dates:

| Commit | Timestamp | Material change |
| --- | --- | --- |
| `0fa6b194d6a7` | 2025-04-10 14:03:37 +01:00 | `LICENSE` and one-line `README.md` |
| `f4ca46def6f5` | 2025-04-10 14:52:22 +01:00 | 30 source files, 15,531 inserted lines |
| `24939a605ee7` | 2025-12-12 19:59:40 Z | 72 source files, 32,192 inserted lines |
| `ac5eff7a2528` | 2025-12-12 20:01:40 Z | `EditorD3DApp.cpp/.h`, 2,064 lines |
| `a073df730148` | 2025-12-12 20:06:43 Z | `CLIParams.cpp/.h`, 479 lines |
| `5352a81cdb83` | 2025-12-12 20:16:26 Z | Empty final “Add files via upload” commit; current pin |

The root `README.md` contains only `# Onslaught`. There is no changelog,
original depot metadata, compiler configuration, project file, or claim that
the uploaded files came from one production revision. Mixed lineage must
therefore be decided from the text and retail evidence, not Git dates.

### License and provenance boundary

- The source root carries GPLv3. The `rebuild/` lane is GPL-3.0-or-later,
  source- and RE-informed, and explicitly not clean-room.
- The repository's root MIT license does not relicense either the pinned source
  or `rebuild/`.
- Four Direct3D framework files preserve Microsoft sample copyright notices:
  `d3dapp.cpp:6-10`, `d3dapp.h:1-6`, `EditorD3DApp.cpp:3-8`, and
  `EditorD3DApp.h:1-6`. Their redistribution posture requires review; this
  document makes no legal conclusion.
- Retail executables, retail assets or conversions, decompiler output, user
  saves, and raw runtime captures stay outside `rebuild/`. Source-derived
  original implementation must retain appropriate attribution and license
  boundaries.

### Source lineage versus Steam lineage

Several independent facts prevent calling this “the Steam source”:

- Source rendering headers and shell types are Direct3D 8-era; the pristine
  Steam binary imports and uses Direct3D 9.
- Source `CCareer` selects a developer
  `c:\dev\onslaught2\career.dat` path under `TARGET == PC`; Steam uses the
  released `.bes` wrapper/layout.
- Source contains substantial Xbox, PS2, editor, resource-builder, devkit,
  playable-demo, and development-tool code.
- Steam assert strings prove at least 134 case-insensitive source basenames that
  are absent from this drop.
- The drop contains 78 basenames that have no assert-derived source-path literal
  in the unpatched baseline binary. That means only “no surviving assert path,” not “not
  compiled.”

## Exact corpus census

### Physical shape

The source tree is flat. There are no subdirectories beneath
`references/Onslaught` in the pinned tree. It contains:

- 52 implementation units;
- 52 conventionally corresponding implementation/header stems except for
  casing and platform alternatives;
- two additional headers (`DX.H`, `membuffer.h`);
- one GPL license;
- one one-line README.

Largest source files:

| File | Lines | Principal content |
| --- | ---: | --- |
| `game.cpp` | 4,166 | initialization, level lifecycle, fixed update/render loop, game state, frontend/game bridge, debug/resource paths |
| `BattleEngine.cpp` | 3,672 | Aquila initialization, movement, locks, targeting, weapons, morph, damage, cloak, augment, effects |
| `FEPGoodies.cpp` | 2,534 | 232 Goodie descriptors, asset lookup, unlocking, async resource load, display/control |
| `d3dapp.cpp` | 1,929 | Direct3D 8 application framework, device/window/fullscreen setup |
| `MemoryManager.cpp` | 1,912 | custom heaps, free lists, allocation, split/coalesce, diagnostics |
| `EditorD3DApp.cpp` | 1,847 | editor/tool D3D framework |
| `ltshell.cpp` | 1,821 | WinMain, DirectInput/D3D shell, main dispatch, capture/debug/editor hooks |
| `SoundManager.cpp` | 1,742 | sample/effect ownership, tracking, priority, attenuation, pause, multiplayer listener selection |
| `FrontEnd.cpp` | 1,633 | page graph, transitions, input, processing, rendering, frontend loop |
| `DXEngine.cpp` | 1,598 | shared `_DIRECTX` renderer with PC and Xbox branches |
| `Career.cpp` | 1,522 | 43-node campaign graph, persistence model, Goodie unlocks, ranks, kill/slot progression |
| `XBoxMemoryCard.cpp` | 1,408 | full Xbox card/save implementation |
| `BattleEngineWalkerPart.cpp` | 1,103 | walker gait, dash, recharge, collision/slide/friction |
| `BattleEngineJetPart.cpp` | 1,090 | flight, energy, stall, ground effect, skim, aerial moves |
| `ResourceAccumulator.cpp` | 1,056 | resource discovery, chunk/archive naming and emission |
| `PCEngine.cpp` | 1,044 | alternate PC engine/render lane, not the `_DIRECTX` selection owner |
| `BattleEngineDataManager.cpp` | 1,003 | Battle Engine configuration defaults, versioned read/write, resource accumulation |
| `InitThing.h` | 969 | versioned authored object-init record hierarchy |

The complete per-unit lines/bytes/body census is Appendix A.

### Text integrity

All 106 source files:

- decode as 7-bit ASCII;
- have no UTF-8 BOM;
- use CRLF line endings only;
- are ordinary text rather than generated/minified payloads.

That makes byte fingerprints and line citations stable at this pin. It does not
make old documentation line numbers stable across future source updates; cite
the commit with consequential claims.

### Developer archaeology markers

Whole-word, case-insensitive lexical counts:

| Marker | Occurrences | Files | Concentration |
| --- | ---: | ---: | --- |
| `FIXME` | 4 | 4 | one each in `BattleEngine.cpp`, `Controller.cpp`, `Controller.h`, `game.cpp` |
| `HACK` | 24 | 11 | `BattleEngine.cpp` 7, `game.cpp` 6, `ltshell.cpp` 3 |
| `SRG` | 25 | 13 | `BattleEngine.cpp` 6, `actor.cpp` 4 |
| `JCL` | 36 | 19 | `game.cpp` 9, `PCPlatform.cpp` 3, `ltshell.cpp` 3 |
| `XXX` | 1 | 1 | `FEPSaveGame.h` |
| `TODO` | 0 | 0 | absence is lexical only, not a quality claim |

These initials/comments are provenance clues and hypothesis generators, not
released behavior evidence. The source also preserves spelling mistakes that
are part of the real vocabulary—`TK_INFANTY`, `BUTTON_LOOSE_LEVEL`,
`FORAWRD`, `ControllerMaping`, and `Infinate`, among others. Do not silently
“correct” identifiers when crosswalking symbols or serialized/script tokens.

## Buildability and dependency graph

### Exact include result

The quoted-include scan:

1. enumerates all 106 tracked `.cpp`/header files;
2. matches `^\s*#\s*include\s*"..."`, including the spaced directive in
   `DX.H`;
3. normalizes slash direction and case;
4. reports both literal relative-path resolution and a separate
   case-insensitive basename-availability crosswalk;
5. preserves raw spellings for diagnostics.

Result:

| Measure | Count |
| --- | ---: |
| Quoted include occurrences | 827 |
| Distinct normalized targets | 254 |
| Literal-path-resolvable target names | 50 |
| Literal-path-absent target names | 204 |
| Literal-path-resolved/unresolved occurrences | 290 / 537 |
| Basename-available target names | 52 |
| Absent even by basename | 202 |
| Basename-resolved/unresolved occurrences | 292 / 535 |
| Distinct resolved file-to-file edges | 290 |
| Files with any quoted include | 98 |
| Files with at least one absent quoted target | 82 |

Angle-bracket includes add 46 occurrences across 14 distinct names:

| Target | Occurrences | Files |
| --- | ---: | ---: |
| `stdio.h` | 14 | 14 |
| `string.h` | 11 | 11 |
| `basetsd.h` | 4 | 4 |
| `windows.h` | 3 | 3 |
| `d3d8.h` | 2 | 2 |
| `mmsystem.h` | 2 | 2 |
| `tchar.h` | 2 | 2 |
| `windowsx.h` | 2 | 2 |
| `commdlg.h`, `dsound.h`, `libdev.h`, `malloc.h`, `stdarg.h`, `stdlib.h` | 1 each | 1 each |

### Highest fan-in supplied headers

| Supplied target | Distinct supplied files including it |
| --- | ---: |
| `game.h` | 21 |
| `CLIParams.h` | 17 |
| `eventmanager.h` | 15 |
| `engine.h` | 14 |
| `Platform.h` | 14 |
| `membuffer.h` | 13 |
| `Player.h` | 13 |
| `Frontend.h` | 12 |
| `ResourceAccumulator.h` | 11 |
| `Camera.h` | 10 |
| `MemoryCard.h` | 10 |
| `SoundManager.h` | 10 |
| `activereader.h` | 9 |
| `BattleEngineDataManager.h` | 8 |
| `Career.h` | 8 |
| `DX.H` | 8 |
| `thing.h` | 8 |

### Highest fan-out supplied files

| File | Distinct supplied targets |
| --- | ---: |
| `FrontEnd.cpp` | 12 |
| `game.cpp` | 12 |
| `BattleEngine.cpp` | 11 |
| `Career.cpp` | 9 |
| `DXEngine.cpp` | 9 |
| `DXGame.cpp` | 9 |
| `PCEngine.cpp` | 8 |
| `PCGame.cpp` | 8 |
| `engine.cpp` | 7 |
| `FEPGoodies.cpp` | 7 |
| `Frontend.h` | 7 |
| `Player.cpp` | 7 |
| `ResourceAccumulator.cpp` | 7 |

The 288-edge literal-relative supplied-file graph has exactly six non-trivial
strongly connected components:

```text
MemoryCard.h <-> PCMemoryCard.h <-> XBoxMemoryCard.h
MemoryManager.h <-> DXMemoryManager.h
Controller.h <-> PCController.h
game.h <-> DXGame.h
SoundManager.h <-> pcsoundmanager.h
engine.h <-> DXEngine.h
```

These cycles mostly arise because a base/selector header includes its selected
concrete owner while that concrete header includes the base. Include guards and
target macros are therefore part of the source's type-selection architecture,
not incidental preprocessing noise.

### Most frequent absent dependencies

| Target | Occurrences | Files |
| --- | ---: | ---: |
| `common.h` | 52 | 52 |
| `debuglog.h` | 28 | 25 |
| `console.h` | 21 | 21 |
| `renderinfo.h` | 14 | 14 |
| `map.h` | 13 | 13 |
| `world.h` | 12 | 12 |
| `profile.h` | 11 | 11 |
| `spriterenderer.h` | 11 | 11 |
| `text.h` | 10 | 10 |
| `state.h` | 8 | 7 |
| `stdafx.h` | 8 | 8 |
| `meshrenderer.h` | 7 | 7 |
| `particlemanager.h` | 7 | 7 |
| `debugtext.h` | 6 | 6 |
| `landscape.h` | 6 | 6 |
| `mesh.h` | 6 | 6 |

`common.h` alone is absent from all 52 implementation units that reference it,
and many central types/macros (`SINT`, `BOOL`, `FVector`, `FMatrix`, target
constants, assertion/logging/profiling machinery) arrive through absent owners.
There is no honest compile command for the supplied tree. Reconstructing enough
headers to parse selected units can support a lab AST, but it would be a
project-authored compatibility environment—not recovery of the original build.

The two-count difference is exact and instructive. `d3dapp.cpp:27-28` includes
`..\cliparams.h` and `..\DX.h`; those written parent-relative paths do not
exist in the flat pin, but root files `CLIParams.h` and `DX.H` are available by
basename. `..\resource.h` and `..\capture.h` on the preceding two lines remain
absent. Therefore 204/537 is literal preprocessor-path truth, while 202/535 is
the repository's established source-recovery availability metric. Neither
makes the tree buildable.

The complete 202-target registry is Appendix C.

## Targets and conditional compilation

The text contains 498 conditional directives with 111 exact normalized
expressions. The dominant active-choice vocabulary is:

| Exact source spelling | Occurrences | Files |
| --- | ---: | ---: |
| `#if TARGET == XBOX` | 68 | 20 |
| `#if TARGET==PS2` | 40 | 10 |
| `#if TARGET == PC` | 32 | 25 |
| `#ifdef RESBUILDER` | 27 | 17 |
| `#if TARGET == PS2` | 24 | 11 |
| `#ifdef _DIRECTX` | 21 | 14 |
| `#ifdef DEBUG_TIMERECORDS` | 19 | 4 |
| `#if TARGET==PC` | 16 | 10 |
| `#ifdef EDITORBUILD` | 15 | 4 |
| `#if TARGET==XBOX` | 13 | 8 |
| `#elif TARGET == PS2` | 12 | 11 |
| `#ifdef _DEBUG` | 11 | 7 |
| `#elif TARGET == XBOX` | 10 | 9 |
| `#ifdef E3BUILD` | 10 | 3 |
| `#ifdef MEMMANAGER_DEBUG` | 10 | 2 |
| `#ifdef DEV_VERSION` | 9 | 5 |

Spelling variants are kept separate in that table because they are exact text;
semantically grouped totals are larger. Other important selectors include
`VANILLA_MEMORYMANAGER`, `USE_THING_HEAP`, `MEMORY_TAGGING`,
`OPTIMISED_DEBUG`, `SIMPLE_MESHES`, `PROFILE`, `MATH_TEST`,
`GENERATE_DEBUG_REPORT`, `STRESS_TEST_GOODIES`, `OLD_LIGHTING`,
`VIS_GAMUT`, and playable-demo/attract paths.

### DirectX partition correction

The `DX*` layer is not Xbox-only:

- `DX.H:5-13` routes PC to `ltshell.h` and Xbox to `XBOXDX.h`.
- `engine.h:229-233` selects `CDXEngine` whenever `_DIRECTX` is defined.
- `DXEngine.cpp:7` owns the `_DIRECTX` body and contains explicit PC branches
  beginning at line 99.
- `Frontend.h:298-302` selects `CDXFrontEnd` under `_DIRECTX`;
  `DXFrontend.cpp:3` owns that body.
- `membuffer.h:23-26` selects `CDXMemBuffer`;
  `DXMemBuffer.cpp:9,22,84,146` contains shared and PC-specific branches.
- `MemoryManager.h:429-433` selects `CDXMemoryManager`;
  `DXMemoryManager.cpp:7,62,93` contains shared and PC-specific branches.

`PCEngine` and `PCFrontend` are alternate/older PC-specific lanes, not the
normal `_DIRECTX` selection. In unpatched baseline bytes the `CDXFrontEnd` clear
color `0x001F1F3F` occurs once at the operand used by
`PUSH 0x001F1F3F` at `0x00540F87`; the `CPCFrontEnd` color `0x000F0F2F`
does not occur. `Front End Move/Select/Back` strings occur at
`0x00629E24/34/48`; the lowercase `frontend\move/select/back` literals of the
`CPCFrontEnd` lane do not. That is retail-static evidence that the CPC lane is
dead in the checked Steam image.

### Why bodies and functions need two counts

The reconciled whole-tree parser census is:

| Construct | Exact corpus count |
| --- | ---: |
| Physical textual function-body blocks | 1,855 |
| Target-conditional definition-head occurrences | 1,857 |
| Bodyless callable declarations | 1,013 |
| Class definition bodies | 110 |
| Struct definition bodies | 13 occurrences / 10 unique names |
| Enum definition bodies / enumerators | 45 / 312 |
| File-scope global/static data definitions | 112 occurrences / 105 unique names |
| Extern variable declarations | 32 |
| Macro definitions | 452 occurrences / 415 unique names |

The 1,857 definition heads classify as 85 constructors, 33 destructors, 15
operators, 1,645 other methods, and 79 free functions. The 1,013 bodyless
callable declarations classify as 36 constructors, 21 destructors, three
operators, 951 other methods, and two free functions.

The 1,855/1,857 distinction is deliberate. A raw tree-sitter pass produced
1,817 `function_definition` nodes. Ten were control/macro false positives:
nine `FOR_ALL_ITEMS_IN` sites and one `FAILED(hr)` site. Forty-six real inline
or macro-prefixed bodies were recovered from declaration-shaped parse nodes.
Two physical bodies have two mutually exclusive definition heads:
`CDXMemoryManager::Init` (`DXMemoryManager.cpp:63/65` → body at `:67`) and
`CMemoryHeap::Init` (`MemoryManager.cpp:302/304` → body at `:306`). Therefore:

```text
physical bodies     = 1,817 - 10 + 46 + 2 = 1,855
conditional heads   = 1,817 - 10 + 46 + 4 = 1,857
```

Appendix A gives both values per source unit and lists the recovered/parser
trap sites. A whole-tree text scan necessarily also sees:

- functions in mutually exclusive PC/Xbox/PS2 arms;
- debug/editor/resource-builder bodies absent from release builds;
- alternate class definitions selected by macros;
- inline/template bodies instantiated zero, one, or many times;
- commented-out/dead preprocessor regions;
- macros that inject declarations or class structure.

Accordingly, this master uses:

- **physical body** for one balanced implementation block present in the
  source text;
- **definition head** for each source-level signature that selects that body;
- **unique normalized signature** for lexical deduplication;
- **retail function** only when the unpatched baseline image/current Ghidra inventory
  establishes an address;
- **runtime path** only when controlled execution observes it.

No source-text count is presented as a linker symbol or released-Steam
function denominator.

## Source architecture spine

### Process-to-frame control flow

The strongest source-defined runtime spine is:

```text
WinMain / CLTShell
  ├─ CCLIParams::GetParams
  ├─ MEM_MANAGER initialization
  ├─ Direct3D/Input/shell initialization
  └─ CLTShell::MainLoop
       └─ SYSTEM.Init / SYSTEM.Run / SYSTEM.Shutdown
            └─ CGame
                 ├─ Init
                 ├─ RestartLoopRunLevel
                 ├─ RunLevel
                 ├─ PreRun
                 └─ MainLoop
                      ├─ PLATFORM.Process / controller dispatch
                      ├─ EVENT_MANAGER.AdvanceTime + Flush
                      ├─ model update
                      ├─ SOUND.UpdateStatus / MUSIC.UpdateStatus
                      ├─ camera/viewpoint update
                      └─ ENGINE.PreRender / Render / PostRender
```

`SYSTEM` is referenced but its implementation is absent. Source locations:

- `ltshell.cpp:489-575`: exception setup, default 96 MiB heap selection,
  command-line parse, memory manager, shell creation, and delegation to
  `SYSTEM`;
- `game.cpp:246-409`: game initialization, event/script/particle/fear-grid
  setup, initial state, and three-second pre-run event;
- `game.cpp:624-760`: resource/archive/world/player/controller load order;
- `game.cpp:1260-1825`: restart, level run, viewports, and render coordinator;
- `game.cpp:1836-2293`: model update, pause/audio behavior, interpolated render
  loop, timing/catch-up, and base-time repair.

Representative retail-static anchors:

| Source identity | Current Steam address | Boundary |
| --- | --- | --- |
| `CLTShell::WinMain` | `0x00512130` | current static identity |
| shell/runtime initialization | `0x004EFB10` | current name `CLTShell__InitializeRuntimeAndLoadCoreResources` |
| frontend/game shell loop | `0x004F0330` | current name `CLTShell__RunFrontEndAndGameLoop` |
| `CGame::Init` | `0x0046C360` | source-shaped static match |
| `CGame::RestartLoopRunLevel` | `0x0046DC30` | source-shaped static match |
| `CGame::RunLevel` | `0x0046E240` | source-shaped static match |
| `CGame::Update` | `0x0046E910` | source-shaped static match |
| `CGame::MainLoop` | `0x0046EEE0` | source-shaped static match |
| `CDXEngine::PreRender` | `0x0053E220` | D3D9 retail implementation |
| `CDXEngine::Render` | `0x0053E2E0` | D3D9 retail implementation |
| `CDXEngine::PostRender` | `0x0053ECC0` | D3D9 retail implementation |

### Global subsystem owners

The source favors one process-wide owner per major service, selected by target:

| Global | Source type/selection | Role |
| --- | --- | --- |
| `GAME` | `CDXGame` under `_DIRECTX`, `CPS2Game` otherwise (`game.h:417-426`) | lifecycle, level, players, state, fixed update/render |
| `ENGINE` | `CDXEngine` under `_DIRECTX`, `CPS2Engine` otherwise (`engine.h:229-239`) | viewports, scene/render coordination |
| `PLATFORM` | `CPCPlatform`, `CPS2Platform`, or `CXBOXPlatform` (`Platform.h:40-54`) | system timer, input, fonts, process/flip/quit |
| `FRONTEND` | `CDXFrontEnd` under `_DIRECTX`, PS2 alternative (`Frontend.h:298-304`) | frontend state machine and page ownership |
| `SOUND` | PC/PS2/Xbox sound-manager implementation (`SoundManager.h:279-294`) | effects, samples, listener and device state |
| `MUSIC` | PC/PS2/Xbox music implementation (`Music.h:108-122`) | song/playlist/fade state |
| `EVENT_MANAGER` | `CEventManager` (`eventmanager.h:90`) | fixed-time scheduling |
| `CAREER` | `CCareer` (`Career.h:211`) | campaign graph and persistent state |
| `MEM_MANAGER` | DirectX or PS2 memory manager (`MemoryManager.h:429-439`) | custom heap routing |
| `MEMORYCARD` | target-defined `CMEMORYCARD` alias (`MemoryCard.h:105`) | save device abstraction |
| `LT` | `PCLTShell` (`ltshell.h:38`) | Win32/D3D/input shell |
| `END_LEVEL_DATA` | `CEndLevelData` (`EndLevelData.h:36`) | runtime mission result bridge, not persistent Career storage |

The architecture is coupled by design. Globals such as `GAME`, `ENGINE`,
`WORLD`, `HUD`, `SOUND`, `CAREER`, `EVENT_MANAGER`, and `PLATFORM` make source
algorithms readable but also mean a narrow file rarely represents an isolated
component.

### Platform and backend selection

The important source distinction is interface/base owner versus selected
backend:

```text
CPlatform     -> CPCPlatform / CPS2Platform / CXBOXPlatform
CEngine       -> CDXEngine under _DIRECTX / CPS2Engine
CGame         -> CDXGame under _DIRECTX / CPS2Game
CFrontEnd     -> CDXFrontEnd under _DIRECTX / PS2 frontend
IMemBuffer    -> CDXMemBuffer under _DIRECTX / PSX/PS2 buffer
CMemoryManager-> CDXMemoryManager under _DIRECTX / PS2 manager
CSoundManager -> CPCSoundManager / PS2 / Xbox sound manager
CMusic        -> CPCMusic / PS2 / Xbox music
```

`PCEngine`, `PCGame`, and `PCFrontend` should not be assumed to be the selected
Steam classes merely because their names contain `PC`. `_DIRECTX` chooses the
`DX*` owners. The source itself calls this out indirectly through its selection
headers; the pristine literal scan independently rejects `CPCFrontEnd` for the
checked Steam executable.

## Core object and lifetime systems

### Gameplay inheritance spine

The source-visible spine is:

```text
CMonitor                         [definition absent]
  ├─ active-reader/deletion observation
  └─ CThing                      [also IAudibleThing + IRenderableThing]
       └─ CComplexThing
            └─ CActor
                 └─ CUnit       [definition absent]
                      └─ CBattleEngine
```

The `DECLARE_MULTI_INTERFACE_CLASS` and `DECLARE_THING_CLASS` macros are
defined in absent headers. Their invocations and `SUPERTYPE` use still establish
the intended hierarchy:

- `thing.h:65`: `CThing` with audible and renderable interfaces;
- `thing.h:257`: `CComplexThing` derives from `CThing`;
- `actor.h:13`: `CActor` derives from `CComplexThing`;
- `BattleEngine.h:72`: `CBattleEngine` derives from absent `CUnit`.

`CPlayer` is not the vehicle base. It derives from `IController` and owns or
observes the player's `CBattleEngine`, camera/view state, statistics, lives, and
input behavior.

### `CThing`

Source-defined base contracts:

- fixed simulation constants `GAME_FR = 20.0f`, `CLOCK_TICK = 0.05f`;
- scheduled events `SHUTDOWN = 2000`, `INIT_SCRIPT`, `START_DIE_PROCESS`,
  `READY_SCRIPT`;
- flags for shutdown, MapWho membership, dying, render suppression,
  invisibility/collision suppression, objective marking, big-thing gamut,
  sliding, and removed-unit type;
- render/collision position, old position, object number, type mask, MapWho
  entry, render owner, audio material, monitoring, and virtual `Hit`/`Damage`
  surface.

`thing.cpp:28-130` allocates sequential object numbers, initializes render and
collision state, clamps against water/ground, and registers in world/MapWho
collections. Shutdown unregisters world/big-thing state, clears monitoring, and
self-deletes. `thing.cpp:133-179` implements render/objective-highlight gates
and event-driven death/shutdown.

`CComplexThing` adds orientation, authored name, and script ownership.
`thing.cpp:563-723` registers names in the noticeboard, clones an authored
script object, schedules `INIT_SCRIPT`, and forwards ready/death/shutdown
events.

Retail-static join points:

| Address | Current identity | Useful source contract |
| --- | --- | --- |
| `0x00401000` | `CGenericActiveReader__SetReader` | monitored reader assignment |
| `0x00401040` | `CMonitor__AddDeletionEvent` | deletion notification linkage |
| `0x004E5A80` | `CSPtrSet__AddToHead` | global/set insertion |
| `0x004F34A0` | `CThing__Init` | base object initialization |
| `0x004F3FD0` | `CComplexThing__Init` | orientation and base-init paths |
| `0x004F4120` | `CComplexThing__SetName` | named-object registration |
| `0x004F4230` | `CComplexThing__SetScript` | authored script attachment |
| `0x004F86D0` | `CUnit__Init` | large absent-source Unit initialization |

### Active readers and scheduled deletion safety

`CGenericActiveReader` (`activereader.h/.cpp`) observes a `CThing` through the
absent `CMonitor` contract. On reassignment it removes the previous deletion
event and adds one to the new object; `ToReadDied()` declares the intended
pointer-nulling response. However,
`CGenericActiveReader::HandleEvent(CEvent*)` is declared and never defined in
the drop, and `Monitor.h` is absent. The registration and invalidation design
explains many reader wrappers and “set reader” calls in Ghidra, but the source
drop does not contain the event-delivery implementation.

`CScheduledEvent` similarly monitors both the destination and optional data.
The event pool reuses objects only after their readers are cleared. A raw
pointer-looking field in decompiler output may therefore participate in a
lifetime-notification protocol; replacing it with an owning or ordinary pointer
in rebuild code without understanding the event relationship changes behavior.

### `CActor`: two-fidelity movement and interpolation

`actor.h/.cpp` supplies the movement layer immediately above complex things:

- full- and low-fidelity move events;
- linear and angular velocity;
- old position/orientation and update timestamps;
- a randomized full-move phase so expensive work is spread across actors;
- low-fidelity integration and ground clamp between full moves;
- water/terrain interaction, slope projection/bounce, MapWho sector update, and
  collision on full moves;
- render position and orientation interpolation from model states.

Key source ranges:

| Range | Contract |
| --- | --- |
| `actor.cpp:15-70` | initialization, randomized phase, low-fidelity integration |
| `actor.cpp:74-173` | full integration, terrain/water and collision |
| `actor.cpp:213-321` | reusable events, fidelity cadence, render interpolation |

Interpolation is not automatically orthonormal: the source's
`GetRenderOrientation` is a component-wise matrix interpolation and has the
renormalization commented out. A rebuild renderer that normalizes or uses one
shared interpolation fraction for both position and orientation is making an
observable choice.

### Authored initialization records

`InitThing.cpp/.h` is a versioned serialization/factory description for objects
placed in levels. The source-visible factory supports:

```text
Unit, Building, Squad, Spawner, Cutscene, Start, SpawnPoint,
Tree, Wall, Feature, Hazard, SphereTrigger
```

`CInitThing` carries position/orientation, collision level/response/type,
allegiance, render mesh/name/script, water/ground handling, and versioned
optional state. Version gates occur through at least 16, 19, 27, 33, and 45.
Derived records add type-specific payloads:

- `CTreeInitThing`
- `CSpawnerInitThing`
- `CSquadInitThing`
- `CWallInitThing`
- `CCutsceneInitThing`
- `CStartInitThing`
- `CSphereTriggerInitThing`
- `CUnitInitThing`
- `CRoundInitThing`
- `CBattleEngineInitThing`
- `CExplosionInitThing`
- `CAnimalInitThing`
- `CFeatureInitThing`
- `CHazardInitThing`

Do not classify all of `InitThing.cpp` as editor-only. Lines 10-87 contain
runtime factory/constructor work; editor `Save/Load` begins under a later
`EDITORBUILD` guard. Guard scope must be analyzed region by region.

`World`, `Map`, `MapWho`, `Landscape`, `Unit`, `Weapon`, and the generic
physics-definition factory implementation are absent. The source initialization
records describe authored inputs but cannot replace retail recovery of those
owners.

## Game loop and event scheduler

### Fixed model time and interpolated rendering

The source model is explicitly 20 Hz:

```c
GAME_FR   = 20.0f
CLOCK_TICK = 0.05f
```

`CEventManager::AdvanceTime` increments an integer frame count and assigns
`mTime = mFrameCount * CLOCK_TICK`; model time is not accumulated from
variable wall-clock deltas. `CGame::MainLoop` performs one model update, then
may render repeatedly until the current `mFrameLength` interval ends. Render
fractions are recomputed from wall time and the fixed model frame.

The main update order at `game.cpp:1836-2060` is materially:

1. increment update-frame number and controllable-camera frame count;
2. play pending message-box samples;
3. process reconnect interfaces when beyond pre-run;
4. set `CUnit::mGuideUpdateCounter = updateFrame % 8`;
5. when unpaused, advance event time;
6. flush player controllers so control events occur at frame start;
7. flush scheduled events;
8. process atmospherics;
9. synchronize pause/unpause state for all game sounds;
10. process resource-builder and terminal-level countdown paths.

`CGame::MainLoop` then updates sound/music status, refreshes each viewpoint, and
renders. Slow-frame handling advances `mBaseTime` by measured elapsed time and
hard-resets it when the overrun exceeds 1.3 times the frame length.

The current deterministic rebuild declares a 30 Hz Core. Retail runtime already
establishes a 20 Hz released update, agreeing with the source event clock; the
rate decision is therefore settled in principle, while migration remains
pending because it touches hashes, message quantization, and many per-tick
coefficients. Thirty hertz is a current implementation divergence, not an open
retail-rate question.

### Event manager geometry

Source constants:

| Constant | Value | Meaning |
| --- | ---: | --- |
| `MAX_NUM_EVENTS` | 20,000 | fixed scheduled-event pool |
| `NUM_PRIORITY` | 3 | start/middle/end-of-frame buckets |
| `NUM_EVENT_LIST_BUFFERS` | 200 | ten seconds at 20 Hz |
| `NEXT_FRAME` | `-1.0` | special scheduling route |
| priorities | `0`, `1`, `2` | start, middle, end |

The scheduler uses a 200-frame circular array of `SPtrSet<CScheduledEvent>`
buckets plus a sorted overflow list:

- pool/free-list initialization: `eventmanager.cpp:41-68`;
- insertion: `eventmanager.cpp:170-279`;
- time step: `eventmanager.cpp:293-304`;
- flush/overflow execution: `eventmanager.cpp:311-397`.

For future times the bucket offset is:

```text
floor((event_time - current_time - 0.001) * 20)
```

Offsets at or beyond `NUM_EVENT_LIST_BUFFERS - 2` go into the time-sorted
overflow list. Overflow events lose normal priority ordering and effectively
run after normal-buffer events, a limitation documented in the source header.
Events with absurd times over 1,000,000 are ignored. Negative/next-frame
scheduling uses a small `+0.0001` time.

Retail-static anchors:

| Address | Identity |
| --- | --- |
| `0x0044B060` | `CEventManager__Init` |
| `0x0044B2D0` | one `AddEvent` form |
| `0x0044B310` | one `AddEvent` form |
| `0x0044B370` | one `AddEvent` form |
| `0x0044B5C0` | `CEventManager__Update` |
| `0x0044B600` | `CEventManager__AdvanceTime` |
| `0x0044B640` | `CEventManager__Flush` |

The rebuild has bounded mission/session scheduling but no demonstrated generic
parity with the complete pool, ring, three priorities, reuse protocol, and
sorted overflow law.

### Game states and terminal flow

Source `EGameState` order:

```text
NOT_RUNNING, PRE_RUNNING, PANNING, PLAYING,
LEVEL_LOST, LEVEL_WON, PLAYER_1_WON, PLAYER_2_WON,
GAME_DRAWN, QUIT
```

`PRE_RUNNING` allows model work before visuals. `game.cpp:371-373` schedules
`FINISHED_PRE_RUN` after the configured three-second pre-run. Panning follows
its own camera/event flow. Terminal states use explicit countdowns because the
game is paused and cannot rely on normal event-time advancement.

Important source-only behavior still absent or partial in rebuild includes the
full pre-run window, player death/viewpoint camera, pause-on-loss semantics,
end-level overlays, debrief transition, result aggregation, and the eight-phase
unit guide-update cadence. Each must be ported or explicitly superseded by
retail evidence; omission is not neutral.

## Battle Engine simulation

### Composition and state

`CBattleEngine` is the player vehicle owner, not merely a movement class. Its
source surface combines:

- `CUnit` life, collision, damage, weapons, equipment, and world behavior;
- a `CPlayer` reader;
- one `CBattleEngineWalkerPart` and one `CBattleEngineJetPart`;
- walker/jet/morph state;
- life, energy, shields, vulnerability, cloak, augment, engine mode, vibration,
  camera shake, safe positions, locks, auto-aim, target tracking, current
  configuration, and render/effect state;
- current weapon, primary/augment weapon support, six energy-store selections,
  radar-warning receiver, and sound/effect handles.

Source state values:

| Enum | Values |
| --- | --- |
| `EBattleEngineState` | `0 MORPHING_INTO_WALKER`, `1 MORPHING_INTO_JET`, `2 WALKER`, `3 JET` |
| `EEngineState` | `0 Afterburner`, `1 Normal`, `2 Off` |
| events | `BECOME_JET=6000`, then walker, crosshair calculation, auto-aim handling |
| transform time | `0.5f` |
| slow-movement factor | `4.0f` |
| augment cap/decrease | `10.0f` / `0.01f` per source update |
| zoom range | charge `0.2`, normal in `0.4`, out `1.0`; step `0.1` |

High-value source regions:

| Range | System |
| --- | --- |
| `BattleEngine.cpp:63-352` | construction/init, configuration, weapons/equipment, part state |
| `:586-752` | target-lock validation/acquisition and stealth gates |
| `:1014-1061` | collision `Hit`, safe-position recovery |
| `:1094-1114` | shock/cockpit shake |
| `:1270-1750` | main movement/update pipeline |
| `:2038-2124` | morph gating, energy, events, animations, cockpit/sound |
| `:2127-2240` | damage, repair, shield/augment, shock/vibration, god-mode restoration |
| `:2278-2616` | crosshair, predictive target and auto-aim cluster |
| `:3000-3072` | launch position |
| `:3096-3139` | cloak |
| `:3199-3216` | interpolated auto-aim position |
| `:3302-3343` | augmentation activation/reset |

### Damage law and high-confidence retail correspondence

The source virtual order is:

```text
CThing::Hit
CThing::Damage(float, CThing*, BOOL, int mesh_part_no)
```

at `thing.h:175-176`, and `CBattleEngine` overrides `Hit` and `Damage` in the
same order (`BattleEngine.h:105,133`). The pristine CBattleEngine RTTI vtable
at `0x005D89C4` contains:

| Slot | Target | Source-order identity |
| ---: | --- | --- |
| 39 | `0x00407350` | `Hit` |
| 40 | `0x0040A890` | `Damage` |

The body at `0x0040A890..0x0040AC24` independently matches
`BattleEngine.cpp:2127-2240`:

- `this+0xF8` life;
- `this+0xFC` energy;
- `this+0x100` shields;
- `this+0x260` Battle Engine state;
- `this+0x2F8` augment value;
- `this+0x2FC` augment active;
- `this+0x4B0` configuration;
- `configuration+0x24` shield efficiency, scaled by `0.01`;
- augment cap 10.0;
- state `2` copies shields to energy at `0x0040AAB4`;
- shock caps 0.25 and 0.05, followed by vibration scaling by 50;
- vulnerability-off restoration of original life/shield/energy at
  `0x0040AC00..0x0040AC18`.

The function ends `RET 0x10` at `0x0040AC22`. It consumes four stack
arguments even though the current Ghidra prototype exposes only three; the
fourth `mesh_part_no` is simply unused in the visible body. The reviewed
prototype and rename target are:

```c
void __thiscall CBattleEngine__Damage(
    CBattleEngine *this,
    float amount,
    CThing *source,
    BOOL damageShields,
    int meshPartNo);
```

This is a high-confidence SOURCE + RETAIL-STATIC correspondence for the vtable
slot, address, ABI, fields, and normal-state control-flow law. It is not a claim
of instruction-for-instruction identity: the narrow repair-path difference
below remains real. Nor is it a runtime measurement of shield drain, augment
charge, repair, death, or god-mode outcomes.

One narrow non-identity remains. Source lines 2208-2210 compute a remaining
energy-repair adjustment with `configuration.life - life`; retail's
`0x0040AB5A` path sets maximum energy without that add. They are equivalent
under the normal invariant that remaining repair reaches energy only after life
is at maximum, but not for impossible/corrupted states such as life above max
or NaN. Preserve the source oddity in historical analysis; implement the
released path when retail parity is the contract.

### Source damage algorithm

For positive damage:

1. increase the player's damage-taken statistic by `amount * 256`;
2. if life is nonnegative, absorb against shields using
   `amount * shieldEfficiency / 100`;
3. suppress shield damage when `damageShields` is false;
4. charge the walker augment from absorbed shields when the augment is inactive
   and the walker has an augment weapon;
5. if remaining damage exceeds remaining shields, drain shields to zero and
   pass overflow to life;
6. start death only when life becomes negative and vulnerability is true;
7. stamp last-damage time and add a directional damage flash.

Then:

- clamp augment value to 10;
- in walker state mirror shields into energy;
- negative damage repairs life then energy;
- derive shock and controller vibration from life loss;
- when `mVulnerable == FALSE`, restore the original life, shields, and energy.

“God mode restores values” does not mean the rest of `Damage` is skipped:
statistics, timestamps, flashes, shock, vibration, and intermediate augment
work can still occur before restoration.

### Target locking and auto-aim

`BattleEngine.cpp:586-752` manages existing locks, removes dead/invalid or
out-of-deflection targets, honors stealth distance, and supports direct,
proximity, and sequence-based acquisition.

The predictive auto-aim source computes a projectile lead using:

```text
lead_time = distance / projectile_speed * 20
```

and smooths toward the predicted point with a 0.5 factor
(`BattleEngine.cpp:2366-2443`). Because the source simulation is 20 Hz, a port
must distinguish “ticks” from seconds before reusing that expression.

Priority retail crosswalk:

| Address | Current identity | Source range |
| --- | --- | --- |
| `0x0040ACC0` | `CBattleEngine__CalcUnitOverCrossHair` | crosshair cluster |
| `0x0040B120` | `CBattleEngine__UpdateAutoAim` | predictive aim |
| `0x0040B6D0` | `CBattleEngine__HandleAutoAim` | aim state |
| `0x0040C990` | `CBattleEngine__GetLaunchPosition` | `:3000-3072` |
| `0x0040D7C0` | `CBattleEngine__GetInterpolatedAutoAimPos` | `:3199-3216` |
| `0x0040DE40` | `CBattleEngine__AugmentWeapon` | `:3302-3328` |

These names are strong current static candidates. The Damage discovery makes
the augment chain especially valuable: trace writes at `+0x2F8/+0x2FC` through
activation, consumption, reset, weapon behavior, and controlled runtime.

### Jet part

`CBattleEngineJetPart` is a composed helper, not the base vehicle class. It
owns input accumulation, simple/advanced flight model state, engine mode,
energy/stall timers, maneuver state, skim/ground-effect behavior, and the main
part pointer.

Source algorithm map:

| Range | Behavior |
| --- | --- |
| `BattleEngineJetPart.cpp:64-220` | gesture/input sequencing and aerial maneuvers |
| `:305-504` | main move, energy cost, stall, ground effect, target-speed correction, orientation/friction, auto-morph, loops/rolls, shields, skim |
| `:516-543` | water skim |
| `:546-606` | ground effect |
| `:609-635` | friction |

Notable source laws:

- a low-speed stall persists for 2.5 seconds below a speed threshold of 0.15;
- target-speed correction divides by 25;
- skim activates below altitude 0.5 with horizontal speed over 0.3, multiplies
  velocity by 0.8, and applies damage `(0.5 - altitude) * 20`;
- ground effect predicts half a second with `velocity * GAME_FR * 0.5`;
- below five units it adds `(5 - altitude) / 400` forward acceleration;
- friction selects altitude/speed-dependent factors around 0.99 and 0.98.

Retail-static matches:

| Source identity | Address |
| --- | --- |
| `CBattleEngineJetPart::Move` | `0x00410C50` |
| `HandleGroundEffect` | `0x00411630` |
| `GetFriction` | `0x00411AA0` |
| `GetIsDoingSpecialAirMove` | `0x00411B70` |
| `AutoLevel` | `0x00412900` |

The bodies are strongly source-shaped statically. Handling feel, exact
per-tick conversion, ground-effect roll sign, stalls, energy, and automatic
morph still need focused tests or runtime captures.

### Walker part

`CBattleEngineWalkerPart` owns gait, dash, landing jets, water state, recharge,
slide/friction, and movement input. Source constants include:

```text
DASH_BOOST_VELOCITY = 25.0
DASH_BOOST_ROLL     = 0.08
ENGINE_VOLUME       = 1.0
```

Source ranges:

| Range | Behavior |
| --- | --- |
| `BattleEngineWalkerPart.cpp:30-58` | gait constants/setup |
| `:119-160`, `:265-316` | dash gates and progression |
| `:361-474` | movement, recharge, water, sliding, friction, velocity cap |

The strict source/Ghidra name mapping is
`CBattleEngineWalkerPart::Move` →
`CBattleEngineWalkerPart__Move @ 0x00413760`. Update-walk-cycle maps to
`0x00412AD0`.

Known retail delta: the source ground-recency check at
`BattleEngineWalkerPart.cpp:375` uses 0.3 seconds; retail predicate
`0x00408120` uses the pristine float at `0x005D85EC`, 0.5 seconds. The
MissionScript `InJetMode` native negates that predicate. The released meaning
is consequently closer to “not a walker with recent ground contact” than a
simple enum check for jet state.

### Configuration data and versioning

`CBattleEngineData` (`BattleEngineDataManager.h/.cpp`) owns configuration
parameters, not `BattleEngineConfigurations`:

- format version 12;
- six energy stores;
- life, energy, shield efficiency;
- movement/turn/friction/flight/roll/loop parameters;
- walker and jet weapons;
- primary and augment data;
- explosion, cockpit, stealth, language, and display name.

Defaults are initialized at `BattleEngineDataManager.cpp:30-99`. The exact
binary read order and version gates occupy `:148-446`; corresponding archive
serialization/resource accumulation follows later. Older gates begin with
legacy weapon strings, then add counted weapons/stores, minimum air velocity,
walker velocity/friction, energy/roll/loop fields, augment, primary, cockpit,
and language.

`UBattleEngineConfigurations` (`BattleEngineConfigurations.cpp/.h`) is the
separate up-to-20 configuration-name/manager table. It stores a count and
byte-length-prefixed names; invalid numeric ids clamp to zero, and failed named
lookup falls back to the first configuration. Calling these versions “save
versions” is wrong: they version Battle Engine configuration resources, not
Career saves.

## Career, save shape, and progression

### Persistent model

The source `CCareer` model fixes these capacities:

| Constant | Value | Meaning |
| --- | ---: | --- |
| `BASE_THINGS_EXISTS_SIZE` | 288 bits | per-node base-object persistence |
| storage for those bits | 9 dwords | `288 >> 5` |
| `MAX_NODES` | 100 | allocated Career nodes |
| `MAX_LINKS` | 200 | two child links per node |
| `NUM_LEVELS` | 43 | authored campaign entries |
| `MAX_NUM_GOODIES` | 300 | persistent Goodie state slots |
| `MAX_CAREER_SLOTS` | 32 dwords | tech/script slot storage |
| reachable slot ids | 0..255 | source bounds against `32 * 8`, so only first eight dwords are addressed |
| languages | 5 | Career/frontend language capacity |
| `CAREER_VERSION` | 9 | source lineage's handcrafted version component |

`CCareer` owns:

- `CCareerNode[100]`;
- `CCareerNodeLink[200]`;
- `CGoodie[300]`;
- killed-type totals;
- 32 slot dwords;
- career-in-progress;
- sound/music volume;
- two-player god, invert-Y, vibration, and controller-configuration arrays;
- pending extra Goodies.

Each node stores:

- unused-but-retained island-start flag;
- completion;
- lower/higher link indices;
- world number;
- nine base-object bitset dwords;
- attempt count;
- best ranking.

Link states are `CN_NOT_COMPLETE`, `CN_COMPLETE`, and
`CN_COMPLETE_BROKEN`. The broken state preserves a previously traversable
alternative when another parent path becomes authoritative.

### Defaults and blanking

`CCareer::CCareer` (`Career.cpp:168-178`) sets:

| Field | Source default |
| --- | --- |
| in progress | false |
| sound volume | `0.8f` |
| music volume | `0.9f` |
| controller configurations | all `1` |
| invert Y | false |
| vibration | true |

`CCareer::Blank` builds the 43-node graph from `level_structure`, assigns two
links per node, resets Goodies/kills/slots, clears god mode and pending
Goodies, and recomputes initial Goodie states. `CCareerNode::Blank` starts base
thing bits as present and ranking as `-1`.

Steam static initialization corroborates the important `0.8/0.9` volume
defaults and the fixed Career-shaped arrays. Retail byte offsets, not the C++
compiler's source layout, own save editing.

### Exact 43-node campaign graph

Each source row is:

```text
world, lower-child node index, higher-child node index,
base world updated on primary completion,
base world additionally updated when all secondaries complete
```

| Node | World | Lower | Higher | Primary base update | Secondary base update |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 0 | 100 | 1 | -1 | 110 | -1 |
| 1 | 110 | 2 | -1 | -1 | -1 |
| 2 | 200 | 3 | 4 | 211 | 212 |
| 3 | 211 | 5 | 6 | 231 | 232 |
| 4 | 212 | 5 | 6 | 231 | 232 |
| 5 | 221 | 7 | 8 | -1 | -1 |
| 6 | 222 | 7 | 8 | -1 | -1 |
| 7 | 231 | 9 | -1 | -1 | -1 |
| 8 | 232 | 9 | -1 | -1 | -1 |
| 9 | 300 | 10 | 11 | 311 | 312 |
| 10 | 311 | 12 | 13 | 321 | 322 |
| 11 | 312 | 12 | 13 | 321 | 322 |
| 12 | 321 | 14 | 15 | -1 | -1 |
| 13 | 322 | 14 | 15 | -1 | -1 |
| 14 | 331 | 16 | -1 | -1 | -1 |
| 15 | 332 | 16 | -1 | -1 | -1 |
| 16 | 400 | 17 | 18 | 411 | 412 |
| 17 | 411 | 19 | 20 | 431 | 432 |
| 18 | 412 | 19 | 20 | 431 | 432 |
| 19 | 421 | 21 | 22 | -1 | -1 |
| 20 | 422 | 21 | 22 | -1 | -1 |
| 21 | 431 | 23 | -1 | -1 | -1 |
| 22 | 432 | 23 | -1 | -1 | -1 |
| 23 | 500 | 24 | 25 | -1 | -1 |
| 24 | 511 | 26 | 27 | -1 | -1 |
| 25 | 512 | 28 | 29 | -1 | -1 |
| 26 | 521 | 30 | -1 | -1 | -1 |
| 27 | 522 | 30 | -1 | -1 | -1 |
| 28 | 523 | 30 | -1 | -1 | -1 |
| 29 | 524 | 30 | -1 | -1 | -1 |
| 30 | 600 | 31 | 32 | -1 | -1 |
| 31 | 611 | 33 | 34 | 621 | 622 |
| 32 | 612 | 33 | 34 | 621 | 622 |
| 33 | 621 | 35 | -1 | -1 | -1 |
| 34 | 622 | 35 | -1 | -1 | -1 |
| 35 | 700 | 36 | -1 | -1 | -1 |
| 36 | 710 | 37 | -1 | 720 | -1 |
| 37 | 720 | 38 | 39 | 731 | 732 |
| 38 | 731 | 40 | -1 | -1 | -1 |
| 39 | 732 | 41 | -1 | -1 | -1 |
| 40 | 741 | -1 | -1 | -1 | -1 |
| 41 | 742 | 42 | -1 | -1 | -1 |
| 42 | 800 | -1 | -1 | -1 | -1 |

This table has been byte/static-crosschecked sufficiently for index/world/link
mapping in the editor. Payload fields still require preservation: knowing the
graph does not license rewriting unknown per-node data.

World 500 is special. Its two paths are gated by slot ids associated with the
rocket and submarine choices; the source checks the higher link for one slot
and lower link for the other. On Steam saves those are bits 29 and 30 of
`mSlots[1]`, corresponding to source slot ids 61 and 62.

### Progression update

`CCareer::Update` only commits campaign progression on
`GAME_STATE_LEVEL_WON`:

1. overwrite persistent slots from `END_LEVEL_DATA.mSlots`;
2. accumulate this mission's killed-type counts;
3. resolve the completed node by world number;
4. keep the better ranking;
5. mark complete and set Career in progress;
6. recalculate links/base-world state;
7. update Goodies.

When the level was not won, it updates Goodie state only. `ReCalcLinks`
propagates base-world “thing exists” bits, checks all secondary objectives for
the alternate update, handles the world-500 slot branch, and marks competing
complete parent links `CN_COMPLETE_BROKEN`.

`CEndLevelData` is a runtime bridge from game to frontend/Career, deliberately
without virtuals or pointers. It carries:

- 288 base-things-left flags;
- ten primary and ten secondary objectives;
- finished world and final game state;
- ranking, score, time, loss reason;
- killed-type counts;
- 32 slot dwords.

It is not embedded as a hidden persistent block. Confusing it with reserved
save bytes would corrupt the format.

### Rankings and grades

`CCareer::GetGradeFromRanking` maps:

| Ranking | Grade |
| --- | --- |
| exactly `1.0` | `S` |
| `<= 0.0` | `E` |
| otherwise | `'D' - floor(ranking * 4)` |

That yields D/C/B/A bands for positive values below 1. `CGrade::operator>=`
treats `S` as best and otherwise relies on ascending character order. Goodie
logic counts A-or-better, C-or-better, and exact S using these rules.

### Slot law

Both get and set:

```text
index = slot >> 5
bit   = slot & 31
mask  = 1 << bit
```

The source range check is `slot < MAX_CAREER_SLOTS * 8`, i.e. 256, despite the
array having 32 dwords/1,024 physical bits. Retail static evidence agrees that
only the bounded logical range is used. In the Steam `.bes` true view,
`mSlots[0]` starts at file offset `0x240A`, not the historically misaligned
`0x2408`; the two-byte Career wrapper prefix is load-bearing.

### Source persistence branches versus Steam

The source contains two different persistence bodies:

**Internal PC-development branch** (`Career.cpp:1039-1080`)

- reads/writes `c:\dev\onslaught2\career.dat`;
- stores a four-byte `CAREER_VERSION`;
- raw-copies `sizeof(CCareer)`;
- points level selection at the highest available level.

**Console-style external-buffer branch** (`Career.cpp:1084-1163`)

- computes a 16-bit stamp:
  `CAREER_VERSION + (sizeof(CCareer) << 4)`;
- writes the stamp, then raw-copies the Career object;
- adjusts target-specific buffer sizing.

Steam uses the console-shaped bulk Career copy but wraps it in released PC
save/options data. The measured file is 10,004 bytes:

```text
2-byte version/stamp
+ 0x24BC-byte Career payload
+ 16 * 0x20-byte option blocks
+ 0x56-byte tail
= 10,004 bytes
```

Retail `CCareer__Load @ 0x00421200` and `CCareer__Save @ 0x00421350`
therefore have useful source names and broad serializer shape, but the source
PC branch is not the Steam implementation. AppCore and retail byte evidence own
actual `.bes` offsets and mutation safety.

`PCFEPLoadGame.cpp` and `PCFEPSaveGame.cpp` are seven-line implementation
stubs; their headers declare page shells. The substantial FE save/load
orchestration lives in `FEPLoadGame.cpp` and `FEPSaveGame.cpp`, with memory-card
validation and buffer transfer. Steam's released PC wrappers must be recovered
from bytes, not inferred from the stub subclasses.

### Goodie persistence versus presentation

Career allocates 300 four-byte Goodie states:

```text
GS_UNKNOWN, GS_INSTRUCTIONS, GS_NEW, GS_OLD
```

The wall's source descriptor table contains 232 visible Goodie entries.
MissionScript uses 1-based Goodie ids while the Career array is zero-based;
retail static work maps script `N` to Career index `N-1`. Preserve all 300
storage entries even though the source wall has fewer content descriptors.

## Frontend, Goodies, input, and camera

### Frontend owner and page graph

`CFrontEnd` is an `IController` and owns the page objects directly. Its source
page-pointer table maps:

```text
Main, Development, Common, BE Configuration, Wingmen,
Briefing, Debriefing, Level Select, Goodies, Dev Select,
Load Game, Save Game, Intro, Multiplayer, Multiplayer Start,
Options, Credits, Controller, Virtual Keyboard, Directory,
E3 Level Select, Language Test, Demo Main, Unknown
```

Initialization (`FrontEnd.cpp:49-155`) creates/initializes frontend data, text,
video, Career, controller/card/message-box state, fills unknown slots with the
unknown-page fallback, and then installs the concrete page owners.

The main source flow:

| Range | Contract |
| --- | --- |
| `FrontEnd.cpp:177-285` | entry selection: normal, attract, loaded system, dev/select, demo and debrief routes |
| `:477-561` | controller ownership and action dispatch |
| `:563-596` | immediate or timed page transition |
| `:650-699` | transition completion and every-page process state |
| `:777-1225` | shared curved borders, title, video background, transition composition |
| `:1259-1340` | pre-common/common/page/post-common render order |
| `:1438+` | frontend run loop and timing |

`SetPage(page, time)` either switches immediately or stores from/to pages,
enters `FEP_TRANSITION`, and gives both pages notifications. During transition,
all pages receive an appropriate process state; render order is deliberately
sorted by page enum value for layering.

Source frontend constants include:

| Constant | Value |
| --- | --- |
| reflection offset/color | `512`, `0xFF7F7F7F` |
| transition ring | `(285,225)`, scale `0.1` → `1.6` |
| level-select magic offset | `(168,-118)` |
| Goodies magic offset | `(-212,204)` |
| main time | `70` |
| controller ports | 2 on PS2, 4 elsewhere |
| sounds | Move, Select, Back |
| autosave | explicit/not, normal, pretend-no-write |

Retail anchors:

| Address | Identity |
| --- | --- |
| `0x004662A0` | `CFrontEnd__Init` |
| `0x00466BA0` | `CFrontEnd__Process` |
| `0x00468200` | `CFrontEnd__Render` |
| `0x00468770` | `CFrontEnd__PlaySound` |

The present rebuild frontend is a bounded released-looking Level 100 route, not
the full source page graph. Missing pages and transitions should be recorded
individually rather than hidden by a generic “frontend implemented” label.

### Goodies wall: exact topology

`FEPGoodies.cpp` contains exactly 232 `CGoodieData(...)` initializers, so valid
descriptor/transition indices are `0..231`. The visual grid maps four category
rows:

| Grid row | X domain | Career Goodie ids | Content |
| ---: | --- | --- | --- |
| 0 | `0..7` | `0..7` | character bios |
| 0 | `8..12` | `66..70` | race levels |
| 0 | `13..16` | `74..77` | developer/team/special material |
| 1 | `0..57` | `8..65` | units |
| 2 | `0..31` | `201..232` | 32 FMV cells; returned id 232 is one past the arrays |
| 3 | `0..122` | `78..200` | 123 concept-art cells; id 200 is the first default/movie descriptor |

That is 8 + 5 + 4 + 58 + 32 + 123 = 230 grid cells, but only 229 map to valid
descriptor indices. The array layout is exact: indices `0..77` are
`GOODIES_1..GOODIES_78`, `78..199` are 122 `GOODIES_79` rows, and `200..231`
are 32 default/movie rows. The grid never exposes valid indices `71..73`, uses
index 200 as the last concept cell, and emits invalid id 232 for its last FMV
cell. Rendering indexes `goodietransition[goodienum]` at
`FEPGoodies.cpp:1906-1949`, so the last cell can access one element past that
232-entry array. This is a concrete source defect, not demonstrated Steam
behavior.

Goodie content types:

```text
GT_IMAGE, GT_MESH, GT_FMV, GT_LEVEL, GT_CHEAT
```

The type hack resolves:

- selected bios/unit ids as images;
- most ids 8..57 as meshes;
- 58..65 as images;
- 66..70 as levels;
- 71..75 as images except 75 FMV;
- 76 mesh;
- 77 FMV;
- every id above 200 as FMV;
- remaining concept art as images.

Text shape:

| Goodie id | Text class | Slots |
| --- | --- | ---: |
| `0..7` | person | 12 |
| `8..65` | unit | 9 |
| `66..77` | generic | 9 by the explicit `>65` branch |
| `>77` | no text | 0 |

The code comments call 201–233 “in-game FMVs,” while the actual type predicate
and grid emit `201..232`. The final value is nevertheless outside the
descriptor/transition arrays; “code wins over comment” does not make that
index valid.

### Goodie resources and interaction

The Goodies implementation is more than an unlock table:

- exact concept-art texture names for ids through 200;
- mesh/background lookup hacks for 3D entries;
- FMV id/path/localization rules;
- race-level mapping;
- per-Goodie archive ids `-1000 - goodie_number`;
- `GDIE`/`GDAT` resource chunks;
- large images split into strips no taller than 512 with overlap;
- asynchronous cache loading and explicit release;
- `GS_NEW → GS_OLD` transitions;
- image pan/zoom;
- manual or automatic mesh yaw/pitch/roll and distance;
- FMV and level launch after zoom-in.

Core ranges:

| Range | Contract |
| --- | --- |
| `FEPGoodies.cpp:150-388` | 232 unlock-description records |
| `:393-454` | grid id/state mapping |
| `:512-999` | texture, mesh, background, type, text, FMV and level maps |
| `:1004-1336` | resource build/serialize/load/free |
| `:1339-1679` | navigation, state transitions, open/close, FMV/level action |
| `:1775+` | full grid render and selected-content render |

The descriptor table stores up to two localized requirement text ids, two
numeric thresholds, and two killed/grade categories. Special pseudo-kill
categories count total A and exact S grades. Career's `UpdateGoodieStates`
contains the actual source unlock decision tree, including script-owned
exceptions and episode gates.

### Controller abstraction

`IController` derives from absent `CMonitor`; a controller keeps active readers
to the current controllable owner. Control types cover frontend, mech, camera,
game interface, game, message log, briefing log, and game menu.

Source analog constants:

| Constant | Value |
| --- | ---: |
| X/Y deadzone | `0.36` |
| analog button deadzone | `0.3` |
| analog-as-digital threshold | `0.9` |
| axes | `-1..-4` = X1, Y1, X2, Y2 |

Source push modes:

```text
BUTTON_ON, BUTTON_ONCE, BUTTON_RELEASE, BUTTON_REPEAT,
ANALOGUE_PLUS, ANALOGUE_MINUS,
ANALOGUE_PLUS_ACT_AS_BUTTON_REPEAT,
ANALOGUE_MINUS_ACT_AS_BUTTON_REPEAT,
KEY_ONCE, KEY_ON
```

`CController::Flush` moves current virtual-bit blocks to old state, clears
three current blocks, and calls the platform mapping owner. `DoMappings`:

1. lazily counts mapping rows up to sentinel 999;
2. reads four axes and hard-zeros values inside 0.36;
3. optionally replaces state from playback;
4. advances a one-button-at-a-time repeat timer;
5. filters by controller configuration;
6. evaluates digital/analog/key push semantics;
7. suppresses duplicate virtual actions in one flush;
8. detects the two-shoulder frontend cheat chord;
9. records state if capture is active.

Debug virtual ids below 16 normally route to `GAME`; ordinary actions route to
the top controlled owner when pause/reconnect policy allows. The mapping stack
uses monitored readers, so pausing, frontend menus, free camera, logs, and
reconnect UI can temporarily take ownership.

The complete source virtual action range is `0..66`, with
`TOTAL_BUTTONS = 67`; id 15 is unused, as are 23 and 24. Exact spellings include
`BUTTON_LOOSE_LEVEL` and `BUTTON_CAMERA_MOVE_FORAWRD`. Appendix B retains the
full map.

### Source controller versus Steam

Retail is not source-identical:

- source hard-clips inside 0.36 without rescaling;
- retail `CController__GetMappedInputValue @ 0x0042E3D0` uses a continuous
  ±0.15 deadzone and rescales the remainder by `1/0.85`;
- retail has six analog codes and additional push modes `0xB..0x11`;
- `PCController.cpp` is a developer mapping table, while shipped mappings come
  from `defaultoptions.bea`;
- a normal retail mapping does not establish the supposed direct-mouse walker
  route; a virgin install with no options file remains a separate unknown.

The source and retail agree on the player's nonlinear look curve:

```text
tan(1.2 * x) / tan(1.2)
```

The retail body at `CPlayer__ReceiveButtonAction @ 0x004D3110` even preserves
the function-local cached divisor shape. That is a strong static algorithm
crosswalk, not an input-output latency or sensitivity capture.

### Camera hierarchy

The visible camera classes are:

```text
CCamera
  ├─ CThingCamera
  ├─ CThing3rdPersonCamera
  ├─ CViewPointCamera
  ├─ CPanCamera              [+ CMonitor]
  ├─ CMovieCamera
  ├─ CControllableCamera     [+ IController]
  ├─ CGenericCamera
  └─ CInterpolatedCamera
```

They cover attached first/third person, death/viewpoint, spline pan, movie,
free-control, generic transform, and interpolation use cases. `CPanCamera`
continuously schedules its update at end-of-frame
(`Camera.cpp:344-393`). `CControllableCamera` is an input owner and participates
in the global update-frame counter used to improve free-camera interpolation.

`CPlayer::GotoPanView @ 0x004D2C10` statically matches
`Player.cpp:152-196`: same eight special level ids, spline point setup, camera
construction, and an event at `for_time - 0.05`. The supplied duration differs:
source `game.cpp:303` initializes `mPanTime = 3.0f`; two controlled Steam runs
measured 6.0 seconds and the expected 8.95/9.0 handoff boundary. Port the
algorithmic shape; use the measured released duration.

The source `CViewPointCamera` death path remains high-value rebuild work. It is
not equivalent to leaving the normal follow camera active after player death.

## Rendering and DirectX

### Renderer ownership and the two PC-looking engines

`CEngine` is the platform-neutral owner of cameras, viewports, landscape,
water, lights, sky cube, global meshes, hit/cloak textures, render toggles, and
resource serialization (`engine.h:55-225`). It is not a complete renderer by
itself. The active `_DIRECTX` branch includes `DXEngine.h` and declares the
global `CDXEngine ENGINE` (`engine.h:228-233`).

Two sibling implementations exist in the drop:

```text
CEngine
  ├─ CDXEngine   selected by _DIRECTX; contains TARGET==PC and TARGET==XBOX arms
  └─ CPCEngine   parallel older/alternate PC renderer; not selected by engine.h
```

That distinction is load-bearing. `CPCEngine` does **not** extend
`CDXEngine`; both directly extend `CEngine` (`DXEngine.h:22`,
`PCEngine.h:19`). The `DX*` family is also not “Xbox-only.” Its PC arms create
the screen-capture texture, release the editor arrow, use the PC buffer size,
and make other Windows-specific choices (`DXEngine.cpp:99-101,169-177`,
`DXMemBuffer.cpp:22-26`). A file prefix is not a target proof.

The lifecycle exposed by the selected renderer is:

```text
CEngine::Init
  create gamut, map-mip array, water, landscape, Kempy cube, lights,
  screen FX, shadows, and trees
        ↓
CDXEngine::Init
  create PC capture texture, retain default gamma, register reflection
  controls, initialise patch manager
        ↓
CEngine/CDXEngine::InitResources
  resolve named textures, mesh, sun particle, landscape/shadow/FX resources
        ↓
PreRender → Render(viewpoint...) → PostRender
        ↓
CDXEngine::ShutDown → CEngine::Shutdown
```

The base initializer is at `engine.cpp:104-191`; the DirectX extension is at
`DXEngine.cpp:150-202`; resource resolution is at `engine.cpp:194-224` and
`DXEngine.cpp:207-221`; teardown is at `engine.cpp:69-100` and
`DXEngine.cpp:90-110`.

### Selected source render pipeline

The active DirectX body is large but its phase boundaries are explicit:

1. `PreRender` stores viewport state, clears the depth buffer (and Xbox
   stencil), and advances ripple phase (`DXEngine.cpp:375-427`).
2. `Render` selects the camera/viewpoint, builds the `C3DGamut`, and calculates
   landscape LODs (`:637-711`).
3. It resets render state/queue, renders shadow textures, begins a scene,
   prepares lights, billboard angle, fog colour, and fog density (`:712-770`).
4. It draws the Kempy sky cube with its own projection (`:772-783`).
5. It restores the world projection with a hard active far distance of
   `700.0f`, draws landscape and landscape shadows, and on PC optionally
   captures the backbuffer for cloak/blur use (`:786-819`).
6. It draws world objects, trees, water/reflection paths, debug markers,
   particles, and queued geometry (`:821-1084`).
7. It stores matrices needed by the HUD, conditionally renders the internal
   cockpit, flushes its queue, and renders screen effects
   (`:573-614`, called from the main body).
8. `PostRender` draws HUD, message/briefing/pause, overlay, debug, console, and
   game-interface layers plus blur, then finishes the scene
   (`:1279-1527`). It does not directly call `FRONTEND.Render` in this body.

`DEFAULT_Z_FAR` is `256.0f` in `engine.h:14`, and the base constructor stores
it in `mFarZ` (`engine.cpp:44`). That member is not the active
landscape/world projection in this body. `CDXEngine::Render` supplies common/PC
`700` at `DXEngine.cpp:788-789`; the other `700` at `:649-650` is inside an
Xbox-only every-other-frame arm. Unpatched-baseline retail static evidence independently
agrees. The old “source 256 versus retail 700” claim is therefore false: 256 is
a dead/default member value on this path.

Other finite render facts:

- `VIEWPOINTS = 2`, `N_MAPMIPS = 7`, and `MAX_GLOBAL_MESHES = 256`
  (`engine.h:16,33-34`);
- map mixers are loaded as 256, 128, 64, 32, 16, 8, and 4-sized levels
  (`engine.cpp:396-413`);
- the PC light setup uses map ambient plus sun and opposite anti-sun
  directional lights; color channels are converted with `1/256`
  (`engine.cpp:431-560`);
- normal alpha is `SRCALPHA/INVSRCALPHA`, additive alpha is `ONE/ONE`, and both
  disable Z writes until `DisableAlpha` restores them
  (`engine.cpp:580-603`);
- PC capture allocates a 1024×512 `X8R8G8B8` texture
  (`DXEngine.cpp:169-176`);
- blur alpha falls by 15 per post-render pass (`DXEngine.cpp:1424-1430`);
- `PATCHMANAGER.Init(800,300,90)` is the selected source call
  (`DXEngine.cpp:199`);
- the seven debug bits are map-who, profiler, cuboids, cockpit, accurate
  skeletal rendering, outer radius, and memory manager
  (`engine.h:48-54`);
- `CEngine::GetDefaultMesh` and `GetGlobalMesh` increment the returned mesh's
  reference count (`engine.h:116-117`), so callers inherit a release
  obligation;
- `CDXEngine::SetDefaultMaterial` is an inline no-op; the actual reset owner is
  `ReallySetDefaultMaterial` (`DXEngine.h:80-83`).

### D3D8 source versus D3D9 release

The supplied Windows shell is unambiguously Direct3D 8:

- `Direct3DCreate8(D3D_SDK_VERSION)` in `d3dapp.cpp:96`;
- `D3DCAPS8`, `D3DPRESENT_PARAMETERS`, `IDirect3DTexture8`,
  `IDirect3DVertexBuffer8`, and `IDirect3DIndexBuffer8` throughout
  `d3dapp.h` and `ltshell.h`;
- a D3D8 application framework handling adapter enumeration, device choice,
  resize/reset, fullscreen, pause, and error display
  (`d3dapp.cpp:91-1846`);
- `PCLTShell` wrapping device calls and shadowing 172 render states plus 30
  states for each of eight texture stages (`ltshell.h:48-66`).

The unpatched baseline imports D3D9, and the recovered retail state block uses D3D9
device slots including `SetSamplerState`. Source architecture and state intent
remain valuable, but D3D enum values, COM vtable offsets, reset behavior, and
sampler/texture-stage separation cannot be copied mechanically. This is an
exact API-generation delta, not a reason to discard the source render order.

`d3dapp.*` and `EditorD3DApp.*` are near-parallel framework copies and retain
Microsoft Direct3D sample notices. They need a file-level redistribution review
before any adaptation; this document makes no legal conclusion.

### Rendering evidence still open

Source code alone does not prove Steam's final pixels. Current stronger retail
evidence establishes, among other things, the D3D9 default state block,
terrain-light enable/colour captures, frontend draw-call census, and HUD
composition described in `../ghidra-functions.md`. Open source-guided render work
includes:

- map every selected `CDXEngine::Render/PostRender` phase to retail address
  ranges and exact draw/state transitions;
- separate source D3D8 intent from D3D9 port corrections;
- crosswalk the absent `DXLandscape`, `DXTexture`, `DXTrees`, `DXShadows`,
  `DXPatchManager`, `Hud`, `Cockpit`, and render-queue bodies;
- capture the water/reflection and cloak/screen-capture paths;
- validate camera, cockpit, and death-view output by discrete draw/state or
  pixel-region evidence rather than source inspection.

## Audio and music

### Sound object model

The source sound layer separates description, logical event, and device
implementation:

```text
CEffect              parsed named recipe; may chain another effect
   ↓ resolves
CSample              cached platform sample identity
   ↓ used by
CSoundEvent          live owner/tracking/fade/pitch/pan/time state
   ↓ managed by
CSoundManager        platform-neutral allocation, ordering, updates and policy
   ↓ selected on PC
CPCSoundManager      DirectSound buffer/device operations
```

`CEffect` stores 64-byte effect/sample names, a low-pass sample name, integer
volume/falloff/pitch variance, language/loop flags, and an optional chained
effect (`SoundManager.h:43-83`). `CSoundEvent` stores an active-reader owner,
channel, sample, four-way tracking mode, menu/game sound class, loop/fade/time,
pan, pitch interpolation, position/velocity, current and attenuated volume,
end point, completion notification, and pause state (`:124-158`).

The four tracking modes are no tracking, capture initial position,
follow-and-die, and follow-but-survive-owner (`SoundManager.h:26-32`).
`CActiveReader<IAudibleThing>` declares/registers an intended deletion-event
invalidation path for a followed owner. Because the generic reader's
`HandleEvent` body and `Monitor.h` are absent, this drop does not by itself
prove the delivery path is complete or safe.

The manager has a pool ceiling of 256 logical sound events
(`SoundManager.cpp:21`) while the PC device has 32 simultaneous sound buffers
(`pcsoundmanager.h:20`). Logical events are created, inserted, sorted,
spatially updated, faded, paused, killed by owner/sample, or retired when the
device reports completion (`SoundManager.cpp:451-1038,1224-1414`).

### Supplied PC device path

`CPCSoundManager::DeviceInit` creates DirectSound8, requests priority
cooperation, and configures a stereo 44,100 Hz, 16-bit primary buffer
(`pcsoundmanager.cpp:36-113`). `LoadNewSample`:

- maps ordinary names to `data\<name>.wav`;
- maps `sounds\...` through `data\sounds\<language>\...` when the
  language-dependent flag is active;
- reads PCM through the absent `CWaveSoundRead`;
- creates mono, 44,100 Hz, 16-bit secondary buffers
  (`pcsoundmanager.cpp:151-223`).

The source carries commented-out DirectSound3D listener/buffer updates.
Its live PC path sets pan, caps pitch multiplication at 1.0, sets frequency
against 44,000, transforms the already attenuated volume below -4000, and
passes that to `IDirectSoundBuffer::SetVolume`
(`pcsoundmanager.cpp:324-431`). The platform-neutral manager's source distance
law uses `FAR_SOUND = 50` and a manual linear percentage falloff
(`SoundManager.h:21`, `SoundManager.cpp:437-442`). `NEAR_SOUND = 3` is defined
at `SoundManager.h:22` but has no other reference in the supplied drop; it does
not participate in this source attenuation function.

The supplied device path is internally inconsistent: secondary buffers omit
`DSBCAPS_CTRL3D` (`pcsoundmanager.cpp:207-214`), yet `PlaySound` performs an
unchecked `IID_IDirectSound3DBuffer` query (`:251-255`) and `StopSound` does not
release that per-channel 3D interface. The actual 3D parameter writes are
commented out (`:366-395`). This strengthens the source-lineage
transitional/incomplete verdict; it is not a license to project those defects
onto Steam.

Retail does not preserve that exact live device law. Static retail work shows:

- frontend `CFrontEnd__PlaySound @ 0x00468770` explicitly uses volume `1.0`
  and `ST_GAME_SOUND`, not the source default argument `0.7`;
- retail's device update passes current volume while the manual distance term
  affects priority rather than final device attenuation;
- retail configures DirectSound3D with min distance 3, max distance 50,
  rolloff 0.7, doppler 1.0, and hard mute at 50.

Those are byte-derived retail claims; a DirectSound loopback capture is still
needed for audible-output parity.

### Music state machine

`CMusic` is another platform-neutral owner with a missing PC device subclass.
The drop defines:

- four play types: single, linear, random, and selection;
- five semantic selections: frontend, credits, tutorial, stealth, and in-game;
- a sorted, duplicate-suppressing linked playlist;
- queued fade-to-zero track changes;
- per-frame target-volume motion in steps of five;
- automatic next/random/selection behavior when a device track finishes
  (`Music.h:8-106`, `Music.cpp:111-303,306-455`).

The selection table is finite:

| Selection | Source track policy |
| --- | --- |
| Frontend | track 8; track 1 in playable demo |
| Credits | track 7 |
| Tutorial | track 3 |
| Stealth / in-game | demo track 0; otherwise `(rand() >> 8) % 8`, with 7 remapped to 9 |

See `Music.cpp:460-548`. Non-Xbox directory loading requests both `mp3` and
`wav`; Xbox requests `wma` (`:366-382`). The saved normalized music volume is
converted to the device's 0..127 domain using
`1 - tan((1-vol)*1.38)/tan(1.38)` on non-PS2 targets
(`:557-570`).

Two source-level hazards must not silently become reconstruction behavior:

- `PlayFromList` uses assignment in
  `if ((mPlayType=MPT_RANDOM) && (mFirstSong))`
  (`Music.cpp:448`), so the null-selection branch forces random mode;
- `GetMenuSoundsMasterVolume` returns `mGameSoundsMasterVolume`, not
  `mMenuSoundsMasterVolume` (`SoundManager.h:243`).

They are direct source facts. Whether Steam inherited, fixed, or bypassed them
requires independent retail control flow.

`PCMusic.h`/implementation and `wavread.*` are absent, so the drop cannot build
or settle PC music-device behavior by itself.

## Resources, I/O, memory, and containers

### Chunk writer and reader

`CChunker` is a buffered tagged writer; `CChunkReader` is its sequential
reader (`chunker.h`, `chunker.cpp`). A physical chunk is:

```text
+0x00  uint32 tag       MKID("ABCD"), host-endian; little-endian on PC/Xbox x86
+0x04  uint32 size      payload bytes only
+0x08  byte[size] payload
```

`Start` writes tag plus a placeholder and records the size-field position.
`End` patches `DataUsed - start - 4`; when the outermost chunk ends, it flushes
the accumulated bytes (`chunker.cpp:56-81`). The initial/growth quantum is
256 KiB and maximum nesting is 255 active levels because `Start` rejects
`Chunk >= LENGTHSMAX-1` with `LENGTHSMAX = 256`
(`chunker.h:8-9`, `chunker.cpp:46-66`). The reader tracks bytes consumed inside
the current payload, asserts against overread, and can skip the unknown
remainder (`chunker.cpp:151-200`).

This chunk system is the resource serializer. It is **not** the Steam `.bes`
save layout, which is a version word followed by raw/bulk career/options/tail
data.

### AYA resource contract

`CResourceAccumulator` declares fixed arrays for 100 meshes and 1,000 textures
and assigns resource ids from zero, or from 10,000 for intended goodie files
(`ResourceAccumulator.h:11-12`, `ResourceAccumulator.cpp:231-244`). `AddMesh`
and `AddTexture` increment those arrays without a capacity guard
(`ResourceAccumulator.cpp:82-154`), so the numbers are storage capacities, not
enforced caps. It merges duplicate resources by source identity and reconciles
flags, then writes or loads platform-specific `.aya` files.

The exact source filename mapping is:

| Logical level | Source output/input |
| ---: | --- |
| `-1` | `data\Resources\base_res_<TARGET>.aya` |
| `-2` | `data\Resources\Frontend_res_<TARGET>.aya` |
| `-3` | `data\Resources\Loading_res_<TARGET>.aya`, sometimes language-suffixed |
| `>= 0` | `data\Resources\<level:03>_res_<TARGET>.aya` |
| every other negative value | `data\Resources\goodie_<-level-1000:02>_res_<TARGET>.aya` |

That filename mapping is implemented at `ResourceAccumulator.cpp:162-205`.
Values `<= -1000` are the intended Goodie/resource-id convention and select
resource ids starting at 10,000 (`:238-240`), but `GetFileName` does not enforce
that bound: `-4..-999` also take the Goodie filename branch and produce
negative formatted numbers.

The `LVLR` version written and required is 103. `AYAD` records the compile-time
sizes of `CTEXTURE`, `CMesh`, `CMeshPart`, `CHeightField`, and (non-PS2)
`CVertexShader`, plus the source static-shadow switch
(`ResourceAccumulator.cpp:43-55,322-353,870-943`). A same-version file can
still be ABI-incompatible if those source object sizes differ.

The top-level tag vocabulary emitted or recognized by the supplied code is:

| Tag | Supplied source-side status |
| --- | --- |
| `LVLR` | directly written and read: resource version |
| `TARG` | directly written and read: target platform |
| `AYAD` | directly written and read: compile-time object-size/feature contract |
| `TEXT` | directly written and read: texture |
| `MESH` | directly written and read: mesh; Goodies also nest mesh chunks |
| `ERES` | directly written/read wrapper around engine-owned resources |
| `WRES` | directly written/read wrapper around world-owned resources |
| `IMPS` | directly written and read: imposters |
| `LNDS` | directly written on PC; read only on PS2 and explicitly skipped elsewhere |
| `SURF` | directly written and read: surface data |
| `SSHD` | directly written/read wrapper around static shadows |
| `VSDS` | read-dispatch branch; producer body belongs to an absent owner |
| `PLAT` | emitted/read by supplied `CPCPlatform` font serialization |
| `PMIB` | read-dispatch branch; producer body belongs to absent patch-manager code |
| `DMKR` | read-dispatch branch; producer body belongs to absent landscape-damage code |
| `GDIE` | written by `CFEPGoodies::Serialise`, then read-dispatched here |
| `PAGE` | writer-only wrapper for a separate PS2 page file; never dispatched by `ReadResources` |

Direct accumulator writes span `ResourceAccumulator.cpp:311-703`;
`FEPGoodies.cpp:1010` emits `GDIE`; read dispatch is at
`ResourceAccumulator.cpp:868-1029`. Unknown tags are traced and skipped,
giving forward-compatible chunk traversal but not semantic compatibility.
The PC writer emits `LNDS` (`:631-650`), while the non-PS2 reader explicitly
skips it (`:970-976`); this source reader does not reconstruct PC landscape
data from that chunk.

Thirteen independent resource bits control paging, target exclusion, base and
loading sets, sky cropping, compression, alpha fixing, optionality,
downsampling, shadow palette, swizzling, and paging inhibition
(`ResourceAccumulator.h:18-31`). On Xbox level builds, the accumulator
repeatedly drops a mip from the largest eligible texture until its computed
texture budget fits, with `meshtex\be_texb.tga` deliberately selected first
when applicable (`ResourceAccumulator.cpp:388-493`).

### Buffered file I/O

`CStorage` itself is an empty target selector whose actual `PCStorage`,
`PS2Storage`, and `XBOXStorage` implementations are all absent
(`storage.h:4-24`). The concrete I/O present in the DirectX branch is
`CDXMemBuffer`:

- default read block: 64 KiB;
- PC write buffer: 2 MiB;
- non-PC DirectX write buffer: 10 KiB;
- optional next-read size must be a multiple of `0x8000`;
- Windows `CreateFile`/`ReadFile`/`WriteFile` backing;
- position-aware block crossing, string reads, skip, EOF, and conversion of an
  in-memory writer to a reader
  (`DXMemBuffer.cpp:21-42,65-628`).

The sidecar “CRC” is only a signed-byte sum per read block
(`DXMemBuffer.cpp:261-279`). Its read path is disabled by
`FILE *crc = NULL` (`:172`), even though the write path may emit `.crc`.
Comments in the source explicitly dismiss it as non-CRC. Do not infer retail
integrity enforcement from the class or filename.

### Memory-card abstraction

`CMemoryCard` defines nine result codes and a platform-neutral card/save
interface (`MemoryCard.h:8-101`). The PC subclass is intentionally inert:
zero cards, no HDD, empty names, successful no-op format/create/read/write,
and a zero save size (`PCMemoryCard.h:8-98`). Therefore it cannot be used as
the model for Steam `.bes` I/O.

The supplied Xbox implementation is substantial:

- 9 card locations and a fixed 4,096-entry save array; enumeration lacks a
  capacity guard and can overflow it;
- 16 KiB allocation blocks;
- `SAVE.DAT` inside the save directory;
- a header with `MKID("NEKO")`, version 100, and Xbox signature;
- create/delete/read/write, image, size, mount, hotplug, and reboot-state
  paths (`XBoxMemoryCard.h`, `XBoxMemoryCard.cpp:16-1408`).

That establishes console architecture and intent, not the Steam file wrapper.
Retail static evidence establishes the Steam 10,004-byte layout described in
the Career section.

### Custom heap and the memory-type trap

The memory layer is a segregated, tagged heap rather than ordinary untracked
`new`:

- `CMemoryBlock` carries a magic `0x4F69EA21`, used/base-set bits, type, links,
  and debug source metadata;
- `CMemoryHeap` supports 16-byte tiny blocks, size-class free lists,
  split/merge, realloc, cleanup, validation, per-type stats, base-set marking,
  and dumps;
- `CDXMemoryManager` routes selected types to general, sound, thing,
  texture-data, vertex-buffer-data, and temporary heaps
  (`MemoryManager.h:200-375`, `MemoryManager.cpp:249-1612`,
  `DXMemoryManager.cpp:27-392`).

`USE_THING_HEAP` gives 10,000 KiB in debug and 3,500 KiB otherwise, with 200
KiB “nearly full” and 10 KiB “full” thresholds
(`MemoryManager.h:11-29`). The DirectX manager routes weapons, AI,
active-readers, navigation, explosions, guides, collisions, deletion callback
lists, general volumes, render things, motion controllers, and map-who entries
to that heap (`DXMemoryManager.cpp:104-132`).

There are exactly 130 `EMemoryType` enumerators including `MEMTYPE_LIMIT`, and
130 rows in `gMemTypeData` including its sentinel. They are **not** positional
mirrors:

- 67 positions differ;
- enum position 42 is `MEMTYPE_MESSAGELOG`, but the table repeats
  `MEMTYPE_MESSAGEBOX` for the `"MessageLog"` row;
- `MEMTYPE_IBUFFER` moves from enum position 47 to table position 81;
- `MEMTYPE_FMV` is absent at enum position 96 and appears at table position
  127;
- index-buffer and tiny-heap ordering diverges in the tail.

The set difference is one missing `MESSAGELOG` and one duplicated
`MESSAGEBOX`, but the positional drift is far broader. Any tool that zips enum
ordinal to table row will silently mislabel memory. Use the explicit
`MemoryTypeData.mType` field (`MemoryManager.cpp:99-240`), not row position.

### Local containers and monitored pointers

The supplied low-level containers explain many source idioms:

- `CArray<T>` owns a resizable heap array;
- `CSArray<T,N>` is inline fixed storage;
- `COSet<T>` layers entry count and iterator state over `CArray`
  (`Array.h:11-92`);
- `GenericSPtrSet` is a linked pointer set with an optional fixed node pool,
  dynamic overflow nodes, add/append/remove/contains/index, and iterator
  wrappers (`SPtrSet.h`, `SPtrSet.cpp`);
- `CActiveReader<T>` registers with a `CMonitor`, removes its old deletion
  event when retargeted, and declares `ToReadDied()` as the nulling endpoint;
  the generic `HandleEvent` delivery body and `Monitor.h` are absent
  (`activereader.h`, `activereader.cpp`).

These are not interchangeable with ordinary `List<T>`/raw pointers in a
rebuild. Iteration order, fixed-pool overflow, ownership, invalidation timing,
and source copy behavior can affect event and gameplay results.

### PC shell, platform, CLI, and editor lanes

`WinMain` parses startup state, creates the global `PCLTShell LT`, then enters
`PCLTShell::MainLoop` (`ltshell.cpp:489-575`). The shell owns the D3D8 window
and device, DirectInput keyboard/joysticks, up to four joypads, force feedback,
render-state mirrors, screenshots, and system-message dispatch
(`ltshell.h:10-286`, `ltshell.cpp:579-1820`).

`CPCPlatform` adapts game-facing process/flip, timing, input, rumble, viewport,
font-resource, prompt, and registry operations (`PCPlatform.cpp:22-506`). Its
registry owner is:

```text
HKEY_CURRENT_USER\Software\Lost Toys\Battle Engine Aquila
```

and the source uses a volatile key (`PCPlatform.cpp:464-501`). Registry
behavior is source-lineage evidence only until matched against Steam.

`CCLIParams` has 40 ordinary data members before target/dev/demo conditional
members (`CLIParams.h:9-64`). Its raw-string parser has nominal storage for 30
space-separated 256-byte parameter rows, but its guards permit writes to
`parms[30]` and `parms[*][256]`; these are dimensions, not safe accepted
limits. It has no quote/escape grammar and walks one large case-insensitive
independent-`if` chain (`CLIParams.cpp:15-392`). Appendix B records its exact
flags and defaults.
Several source flags are absent from the Steam parser; accepted source syntax
is not a supported retail launch contract.

`d3dapp.*` and `EditorD3DApp.*` provide mutually guarded parallel D3D8
framework bases; `PCLTShell` chooses between them under `EDITORBUILD2`
(`ltshell.h:52-57`, `ltshell.cpp:48-53`). `InitThing.cpp` similarly contains
both normal factory/initialization work and editor-only Save/Load work. A
single guarded region must never be used to label an entire unit
“editor-only.” Conversely, `CEditorD3DApp::Run` begins inside a block comment
at `EditorD3DApp.cpp:1538`; this drop establishes substantial editor framework
and schema vocabulary, not a complete standalone editor loop.

### Source-only defect and portability ledger

These are direct properties of the pinned text. They are reasons to port
intent selectively, not evidence that Steam executes the same defect.

| Source site | Exact source fact | Reconstruction consequence |
| --- | --- | --- |
| `engine.cpp:606-619` | `SetTreeAlphaMode` contains only commented state changes | do not infer an active tree-alpha policy from the method name |
| `engine.cpp:635-637` | `SetSky` is empty | sky selection lives elsewhere or is incomplete in this lineage |
| `engine.cpp:648-695` | engine resources nest an `ENGN` chunk, count 7, seven map textures, then `MAP` | preserve nested framing when reading this source format |
| `DXEngine.cpp:869-878` | selected DX body draws ordinary water only when `mRenderReflections` is false and contains no replacement reflection render call there | selected source reflection toggle can suppress water; old `PCEngine` reflection code is not the active lane |
| `DXEngine.cpp:1315,1336` | viewport copies use `sizeof(mCurrentViewpoint)` rather than `sizeof(mCurrentViewport)` | only four bytes are copied in the source text; do not silently call that retail behavior |
| `FEPGoodies.cpp:393-435,1906-1949` | the grid omits valid indices 71..73 and emits 232 for a 232-entry transition array | last-FMV selection can access one past the source array; recover retail behavior before copying the topology |
| `SoundManager.cpp:669-756` | one bubble-sort pass orders events, then PC admits three quarters of device channels—24 of 32 | priority/channel behavior needs its own parity test |
| `SoundManager.cpp:1495-1535` | empty SFX lines can underflow `line[strlen(line)-1]`; names are copied into fixed fields with `strcpy` | use bounded, validated parsing |
| `pcsoundmanager.cpp:25-30` | `mWavData` allocated with `new[]` is released through scalar `delete` macro | source memory-management defect; never reproduce it |
| `pcsoundmanager.cpp:366-395` | live 3D parameter updates are block-commented, although a 3D interface is queried | the source PC device path is internally transitional/incomplete |
| `pcsoundmanager.cpp:207-255` | buffers omit `DSBCAPS_CTRL3D`, then `PlaySound` performs an unchecked 3D-interface query whose per-channel result is not released by `StopSound` | do not copy this inconsistent COM/device ownership |
| `pcsoundmanager.cpp:420-425` | status mask uses logical OR inside bitwise `&` | test actual desired status bits explicitly |
| `Music.cpp:448` | `mPlayType=MPT_RANDOM` is assignment inside a condition | do not port as intended random-mode comparison without adjudication |
| `chunker.cpp:16-19` | array `Data` is destroyed with scalar `delete` | replace with safe owned storage |
| `chunker.cpp:56-92` | tag/size words are host-endian unaligned casts with no arithmetic overflow guard | source format is 32-bit little-endian in practice; implement explicit checked reads/writes |
| `ResourceAccumulator.cpp:569-575` | mesh filtering reads `mTextureFlags[i]` for `RES_LOADINGSET` | likely wrong table and potentially wrong bound; do not normalize silently into a retail claim |
| `ResourceAccumulator.cpp:82-154` | fixed mesh/texture arrays are appended without capacity checks | reject or grow safely rather than treating 100/1,000 as enforced limits |
| `ResourceAccumulator.cpp:353-354,544-545` | `writetexture` and `droppedmipmaps` are allocated with `new[]` then passed to scalar `SAFE_DELETE` | preserve the data-flow intent, not the mismatched deletion |
| `DXMemBuffer.cpp:318-327` | `mCRCDataUpTo` increments even when the disabled CRC path leaves it null | undefined source pointer arithmetic; no semantic behavior to preserve |
| `DXMemBuffer.cpp:599-605` | write close calls `fclose(mCRCFile)` without a null guard | handle optional sidecars safely |
| `MemoryManager.cpp:371-391,568-603` | heap initialization shifts the `malloc` pointer to align it, later frees the shifted pointer, and records pre-alignment `aSize` as free size | replace the allocator; its ownership pointer and statistics are unsound |
| `MemoryManager.cpp:1147-1151` | `CMemoryHeap::FreeAll` is a false-returning stub | it supplies no reclamation contract |
| `MemoryManager.cpp:1573-1610` | `FindLargestFree` dereferences the initial free node; `FindSmallestFree` returns null with its algorithm commented | diagnostic/query names overstate implementation |
| `DXMemoryManager.cpp:93` | PC sound heap size is `30*1024*1025 + 512*1024` | exact source value is 32,012,288 bytes ≈ 30.53 MiB and strongly resembles a 1025 typo |
| `DXMemoryManager.cpp:151-159` | shutdown closes the default heap and only Xbox texture heap, not dump/thing/sound heaps | source teardown is incomplete |
| `DXMemoryManager.cpp:221-243` | `DoesExist` returns true for an invalid header and deliberately null-dereferences a freed valid block | never port this predicate; current safe identity must own validity |
| `SPtrSet.cpp:70-147` | one process-global node pool is shut down independently of live sets; size zero writes `mBlock[-1]` | replace with independently owned managed collections |
| `SPtrSet.cpp:335-345` | `GenericSPtrSet::At` dereferences `current` after traversal without an out-of-range check | use a checked lookup contract |
| `Array.h:11-49` | dynamic array resizing is raw byte reallocation; release indexing is unchecked | safe only for very narrow types; managed containers intentionally supersede it |
| `Array.h:21` | assignment copies exactly the destination's current size without resizing or checking the source | do not preserve this asymmetric out-of-range copy contract |
| `CLIParams.cpp:85-135,390-404` | fixed token arrays, no quoting, unchecked value increments, unbounded argv concatenation | current launch parsing must be bounded and explicit |
| `ltshell.cpp:1089-1105,1259-1260` | joystick callback writes `pJoystick[mJoypads]` before later clamping count to four | more than four devices can overwrite the source array |
| `ltshell.cpp:1213-1310` | ordinary startup rejects zero joypads outside selected dev/resource modes | source internal-PC input assumptions are not a Steam/rebuild UX contract |

Other source facts in the same category include x86 pointer-to-`UINT`
arithmetic, inline-assembly spin locks, raw `sizeof` serialization, fixed
tables without complete capacity guards, and several selected backend owners
missing entirely. Managed safety is an intentional reconstruction correction,
not a parity loss.

## Source-to-Steam crosswalk

### Lexical name overlap: useful denominator, not identity proof

A comment/string-stripped scan found 980 explicitly scoped out-of-class member
definition occurrences and 970 distinct `(owner, member)` keys in the Stuart
corpus. It balanced parameter parentheses, accepted only signatures leading to
a body (including constructor initializer lists), included scoped inline
definitions, and collapsed overload/name duplicates for the denominator.

Against the current Ghidra function-name table:

| Normalization | Overlap | Meaning |
| --- | ---: | --- |
| Strict `Owner::Member` → `Owner__Member` | 400 / 970 (41.2%) | Lexically identical owner/member spelling |
| Plus `Owner::Owner` → `Owner__ctor` and `Owner::~Owner` → `Owner__dtor_base` | 429 / 970 (44.2%) | Convention-aware lexical overlap |

The strict 400 is the canonical exact-name count. An earlier hybrid count of
409 silently added nine destructor rewrites but no constructor rewrites and
was invalid. The corrected convention-aware result adds 20 constructor and
nine destructor keys.

This overlap proves useful naming/ownership correspondence only. It does not
prove that an address is the same revision, has the same prototype, or behaves
the same. Overloads are collapsed; inline class-body methods and free
functions are outside this particular denominator.

Examples with independent source/body support include:

| Source key | Source | Retail address |
| --- | --- | ---: |
| `CBattleEngineJetPart::Move` | `BattleEngineJetPart.cpp:305` | `0x00410C50` |
| `CBattleEngineWalkerPart::Move` | `BattleEngineWalkerPart.cpp:361` | `0x00413760` |
| `CPlayer::GotoPanView` | `Player.cpp:152` | `0x004D2C10` |
| `CBattleEngine::Damage` | `BattleEngine.cpp:2127` | `0x0040A890` |

The JetPart owner has 39 explicit source definitions, 24 strict name matches,
and 26 convention-aware matches. WalkerPart has 41, 25, and 27 respectively.
There are no source owners named `CJet` or `CWalker`; those were invalid
shorthand labels in an earlier intermediate report.

### Shipped source-path lower bound

The unpatched baseline executable retains MSVC `__FILE__` strings under
`C:\dev\ONSLAUGHT2\`. A fresh scan, normalized explicitly, gives:

| Measure | Exact count |
| --- | ---: |
| Case-preserving path-string occurrences/values before case folding | 166 |
| Case-insensitive distinct full paths | 163 |
| Case-insensitive distinct basenames | 162 |
| Basenames present in the Stuart drop | 28 |
| Basenames proven by retail paths but absent from the drop | 134 |
| Stuart basenames with no surviving retail path string | 78 |

The full-path/basename drop is caused by path/case variants such as
`Monitor.h`; the case-preserving count also distinguishes `Array.h`/`array.h`.
The prior 161/133 ledger missed `Hud.cpp` and `PolyBucket.cpp`; Appendix D is
the corrected 162/134 registry.

This is a **lower bound** on the shipped source tree. Only paths embedded by
assert/debug macros survive, so a Stuart file with no path literal is not
proven absent from retail. Conversely, a surviving basename establishes that
some compiled lineage referenced that file; it does not say the entire file
linked or that the current address map is known.

The 134 absent basenames expose the drop's most important blind spots:
mission/physics script VM, world/unit/weapon families, HUD/cockpit/frontend
pages, terrain/landscape/texture/mesh/render backends, particles, shadows,
trees, water-adjacent systems, and numerous vehicle/unit subclasses.

### Confirmed agreement ledger

| System | Strongest current verdict |
| --- | --- |
| Battle Engine damage | **High-confidence RETAIL-STATIC correspondence.** RTTI/vtable order and the pristine body at `0x0040A890` reproduce the source ABI, field accesses, and normal-state branch law, while `ret 0x10` repairs the missing fourth stack argument. One out-of-invariant repair-path delta and all runtime outcomes remain open. |
| Battle Engine movement | **RETAIL-STATIC crosswalk.** `Move`, jet movement/ground effect/friction/special-air/autolevel, and walker-cycle bodies have source-corresponding address identities. Runtime vehicle parity remains open. |
| Pan camera body | **RETAIL-STATIC algorithm agreement.** Same eight special level ids, spline construction, and event at duration minus 0.05. |
| Player look curve | **RETAIL-STATIC agreement.** Both use `tan(1.2*x)/tan(1.2)` including the cached divisor shape. |
| World far plane | **SOURCE + RETAIL-STATIC agreement.** Active selected source and retail use 700; the 256 base member is not the active projection. |
| Career serializer shape | **RETAIL-STATIC partial agreement.** Retail preserves the console-like bulk structure but adds the PC wrapper, options entries, and fixed tail. |
| Cheat check mechanism | **RETAIL-STATIC mechanism agreement.** XOR/substring shape corresponds, but table contents differ. |

### Proven or bounded deltas

| Area | Stuart source | Steam evidence |
| --- | --- | --- |
| Ground-recency flight predicate | `0.3f` in `BattleEngineWalkerPart.cpp:375` | pristine constant is `0.5f`; `InJetMode` negates the recent-ground predicate |
| Intro pan duration | game default `3.0f` | two controlled runs measured `6.0f` and the expected 8.95/9.0 handoff |
| Graphics API | D3D8 | D3D9 |
| Controller deadzone | hard clip inside `0.36`, no rescale | continuous ±0.15 with `1/0.85` rescale, six analog codes, more push types |
| Mapping source | `PCController.cpp` developer table | shipped `defaultoptions.bea` |
| Frontend sound call | default argument `0.7` | retail body explicitly supplies `1.0` and `ST_GAME_SOUND` |
| Positional audio | source PC live path uses manual attenuated volume | retail uses DirectSound3D law and sends current volume |
| PC Career path | `Career.dat`/PC subclass stubs in this lineage | fixed observed 10,004-byte `.bes` wrapper/layout |
| Cheat index 3 | `B4K42` | `Maladim` |
| Selected frontend subclass | `DXFrontend`; `PCFrontend` also exists as alternate text | pristine bytes select/contain CDX behavior; CPC clear literal and lowercase paths are absent |
| CLI | broad internal/resource/debug switches | retail lacks at least `-configuration`, `-norumble`, `-nostaticshadows`, `-hidetail`, `-textureramlimit` |

An executable/source comparison is not automatically runtime evidence. The
pan duration is runtime-measured; the API, constants, prototypes, and most
audio/controller claims above are static until a stated capture exists.

### Corrections that must not regress

- The supplied `DXEngine`, `DXFrontend`, `DXMemBuffer`, `DXMemoryManager`, and
  `DX.H` are shared `_DIRECTX` files with explicit PC arms, not Xbox-only.
- “84 source files have zero citations” was a documentation grep result, not
  evidence that 84 files were unported or unused.
- Do not classify an entire file from one target/editor guard.
- The refuted K1–K3 claims—RNG consumer phase, Level 100 trigger/allegiance
  loss, and missing water clamp—remain dead.
- The D7 reconstruction divisor `/900` is correct; `/600` introduces a 1.5×
  error.
- Per-node terrain colour is a closed false path: its sole writer is
  unreachable, no loader exists, and all 67 shipped `CHFD` records have null
  arrays.
- A vague “weapon resource path differs” statement in older provenance notes
  is not yet evidence. Located source HUD-icon paths occur under
  `RESBUILDER`; either recover an exact runtime source/byte pair or remove the
  exception.
- Source `BattleEngine.cpp:2208-2210` adds energy-repair bookkeeping that is
  absent or optimized from the retail Damage body, but it only changes state
  outside the normal `life <= maximum` invariant. Do not inflate that narrow
  static observation into a demonstrated gameplay delta.

## Source-to-rebuild crosswalk

### Current reconstruction boundary

No complete Stuart class-family can honestly be called full released-game
parity. The current reconstruction is a substantial, bounded Level 100 and
Aquila implementation with:

- deterministic Core physics, morph, weapons, mission, actor, contact, terrain,
  and destruction work;
- a Client/Godot frontend, startup, input, camera, render, HUD, pause, audio,
  and retail-asset adapter;
- managed replacements for D3D, Win32, custom heaps, raw pointer monitors,
  buffers, and target-specific storage;
- 411 xUnit `[Fact]`/`[Theory]` declarations at the survey base: 139 in
  Core.Tests and 272 in Client.Tests.

The working tree mattered to this dated census. At the 2026-07-29 survey base,
169 rebuild files were tracked, 164 still existed, one additional Python
materializer test was untracked, and five tracked C# files were deleted. Those
frozen survey facts are not current repository architecture.
Ignored locally materialized retail assets are also excluded from source-file
counts.

Core currently advances at 30 Hz (`SimulationConstants.cs:7`) while explicitly
carrying the released/source 20 Hz rate (`:15`) and time-converting selected
laws. That is a current reconstruction divergence, not a source-exact
scheduler port; the move to the established released 20 Hz cadence is decided
in principle but pending implementation sequencing. Tests establish
reconstruction behavior only.

### Complete Stuart-unit classification

| Stuart unit | Current rebuild verdict | Current owner or boundary |
| --- | --- | --- |
| `activereader` | Superseded, partial semantics | stable ids, owned/nullable references; no raw monitored-pointer clone |
| `actor` | Partial | Level 100 registry/mechanics, chiefly retail-data/static-derived |
| `Array` | Superseded | managed arrays/lists |
| `BattleEngine` | Substantial partial | `Simulation.cs`; damage funnel, locks/autoaim, augment, cloak, rearm, death and broad lifecycle/sound are incomplete |
| `BattleEngineConfigurations` | Absent | no up-to-20 configuration-name/lookup table; selected `SimulationConstants` belong to `CBattleEngineData`, not this manager |
| `BattleEngineDataManager` | Partial/data-specific | materialized manifests and bounded loaders |
| `BattleEngineJetPart` | Substantial partial | thrust, turn, pitch, ground effect, water skim, friction, auto-land, energy |
| `BattleEngineWalkerPart` | Substantial partial | walking, yaw/pitch, slope/water/contact, landing jets |
| `Camera` | Partial | opening pan, controlled/chase/render camera; death/movie/free/broader third-person paths absent |
| `Career` | Substantial bounded partial | 43-node graph, grade law, bounded Goodie update/latches, and in-memory progression; save/write persistence remains open |
| `chunker` | Superseded | managed readers and materializer tooling |
| `CLIParams` | Partial | bounded startup/skip-FMV behavior |
| `Controller` | Partial | client input/session mapping, not full source ownership stack |
| `d3dapp` | Deliberately superseded | Godot window/render loop |
| `DX.H` | Deliberately superseded | .NET/Godot project boundaries |
| `DXEngine` | Algorithms partially adapted; backend superseded | terrain/render/camera conventions; no D3D8 port |
| `DXFrontend` | Partial | `RetailFrontendSession` / `RetailFrontendFlow` |
| `DXGame` | Excluded | selected source unit is mainly diagnostics/timing glue |
| `DXMemBuffer` | Superseded | `Stream`/`BinaryReader` and Python tools |
| `DXMemoryManager` | Superseded | managed allocation/GC |
| `EditorD3DApp` | Excluded | internal editor framework |
| `EndLevelData` | Partial with bounded bridge | snapshot carries world/state, objective tables, ranking, time/score, kills/base flags, and the bounded Career/debrief handoff; live first-play score/time join and a general bridge remain open |
| `engine` | Partial algorithms; backend superseded | selected timing/render concepts only |
| `event` | Partial | typed deterministic events, not generic `CMonitor` events |
| `eventmanager` | Partial | typed 30 Hz queues, not the source 20 Hz generic scheduler |
| `FEPGoodies` | Absent as a page/system | only shared helper corroboration and menu-facing identity remain; topology, unlocks, viewer, resources, and lifecycle are absent |
| `FEPLoadGame` | Absent | no load-page/system |
| `FEPSaveGame` | Absent | no save-page/system |
| `FrontEnd` | Partial | main/options/dev/level/briefing/config/loading/pause/debriefing slices |
| `game` | Partial | startup, media, frontend→Level 100, pause/quit; broad lifecycle/result/career absent |
| `InitThing` | Partial Level 100 substitute | actor manifest subset; no general factory/versioned serializer |
| `ltshell` | Superseded with partial input semantics | Godot/.NET host |
| `membuffer` | Superseded | managed byte readers |
| `MemoryCard` | Excluded/inert on source PC | no useful PC device contract |
| `MemoryManager` | Superseded | managed allocation/GC |
| `Music` | Partial | menu/tutorial selection, play/stop/repeat/volume; general playlist/credits incomplete |
| `PCController` | Source abstraction partial; source table superseded | current input/bindings are primarily shipped-`defaultoptions.bea` and retail-static derived, not a port of the refuted developer mapping table |
| `PCEngine` | Excluded from the selected source lane | not selected by `engine.h` and stale against supplied interfaces (`mLandscape` used as a scalar and absent `mDetailTexture`); exact historical compilation exclusion is unproven without a project file |
| `PCFEPLoadGame` | Excluded | empty implementation |
| `PCFEPSaveGame` | Excluded | empty implementation |
| `PCFrontend` | Excluded | dead alternate; selected class is `DXFrontend` |
| `PCGame` | Excluded from selected source lane | `game.h` selects `DXGame` under `_DIRECTX`; exact historical compilation exclusion is unproven without a project file |
| `PCMemoryCard` | Excluded | zero-device success-returning stubs |
| `PCPlatform` | Superseded with partial semantics | Godot/.NET process/input/window host |
| `pcsoundmanager` | Partial; source-ported but retail-refuted | current positional attenuation is wrong for Steam |
| `Platform` | Superseded | Godot/.NET platform ownership |
| `Player` | Substantial partial | input, camera, mode, weapons; stats/career/control breadth incomplete |
| `ResourceAccumulator` | Superseded | exact-hash materializer/manifests |
| `scheduledevent` | Partial | typed queues, not generic source objects |
| `SoundManager` | Partial; source-ported but retail-refuted | current positional attenuation is wrong for Steam |
| `SPtrSet` | Superseded | managed sets/dictionaries/lists |
| `storage` | Superseded | managed filesystem/streams |
| `thing` | Partial | registry/pose/health/contact/destruction subset, not complete generic lifecycle |
| `XBoxMemoryCard` | Excluded | wrong platform |

“Superseded” is not “forgotten.” It means the behavioral contract, if any,
should be represented with safe deterministic .NET/Godot owners rather than
copying old platform mechanisms and source defects.

### Aquila implementation crosswalk

Current Core's major Aquila regions are:

```text
Simulation.cs:141-3030
  main step                         :141
  opening camera                   :309
  mode transitions                :844-913
  walker/landing-jet movement      :925-1058
  jet movement                     :1070-1208
  jet energy                       :1209+
  ground effect                    :1235+
  water skim                       :1299+
  jet orientation/autoland/friction:1383-1533
  walker yaw/pitch/terrain         :1550-1662
  walker movement/contact/water    :1663-2110
  flight/contact resolution        :2143-2219
  water failure/map limits         :2220-2289
  feet                             :2290-2449
  mission/resources/fire/projectiles:2453-2830
```

The current largest source-visible gaps are exact:

1. **Damage/shields.** Stuart's canonical stage is
   `BattleEngine.cpp:2127-2240`, and retail `0x0040A890` now independently
   identifies it. Current player damage sites around `Simulation.cs:523-540`
   and `:741-748` subtract hull directly. The constants file itself notes that
   no shield-drain path exists (`SimulationConstants.cs:301-345`).
2. **Ground-impact damage.** Source `BattleEngine.cpp:2980-2990` squares the
   surface cosine, calls
   `Damage(sqrt(velocitySq) * 16 * cosSurface, NULL, FALSE)`, and scales
   velocity by `1-cosSurface`. Current `Simulation.cs:2163-2180` emits only a
   threshold event and calls the translation unknown; that comment is stale.
   The Stuart law is exact SOURCE evidence but not yet retail-adjudicated, and
   its per-tick velocity also depends on resolving the current 30→20 Hz
   migration.
3. **Lock/autoaim/launch position.** Source families around
   `BattleEngine.cpp:586-1013` and `:2278-2610` are not implemented as a
   complete chain.
4. **Zoom.** Current input declares but rejects Zoom In/Out
   (`SimulationTypes.cs:261-274,352-376`) on the premise that zoom is only
   presentation. Source `mZoom` is mutable gameplay/camera state bounded near
   0.4..1.0; there is no current propagation path.
5. Landing-jet burn damage, grounded walker map-edge handling, augment, cloak,
   rearm, selected-weapon breadth, death camera, and broad sound/lifecycle
   behavior remain incomplete.

### Mission, actor, terrain, and destruction boundary

The current Level 100 chain is large and deterministic, but most of it is not
a Stuart port because mission VM, unit AI, weapon, HUD, and many actor families
are absent from the drop:

- `Level100MissionProgram.cs` accepts exactly 25 hash-pinned Steam script
  payloads and owns the bounded identity/event tables;
- `Level100Mission.cs` executes the supported opcode/native set and terminal
  flow;
- `Level100ActorScriptRuntime`, `Level100ActorRegistry`,
  `Level100ActorMechanics`, and `Level100ActorWeaponRuntime` own bounded actor,
  AI, weapon, round, guidance, and impact behavior;
- `Level100Terrain`, `Level100ContactMap`, and `Level100Destruction` own
  hash-pinned terrain/contact/destruction reconstruction.

`Level100FullChainTests` encodes assertions for all 11 current progression
events and a direct-Core path to `Won`; this documentation pass counted test
declarations but did not record an executed result, so “proves” would be too
strong. `Level100ColdStartTests` encodes a different acceptance result: an
omniscient, pointer-quantized test autopilot clears objective four but changes
to walker mode over open water and expects `Lost/WaterLoss`, while its
direct-Core control expects `Won`. The driver reads exact health, full actor
poses, and ray tests, and the mode-switch policy lives in
`Level100ChainAutopilot.NavigateToZone`. That is a test-driver acceptance
limitation, not an isolated production-code defect or evidence of human
playability.

### Frontend, Career, render, and audio boundary

The current frontend supports substantial bounded navigation and in-memory
Career progression, but persistence and broad campaign ownership remain open:

- `RetailFrontendSession` exposes the current main rows and page state;
- Load, Multiplayer, and Goodies can be selected but are inert;
- the language state exists without an assignment path;
- Stuart's outgoing dual-page transition is deliberately not ported on the
  measured cold-main edge: controlled retail frames refute the visible
  outgoing click-page draw there. Other edges require individual crosswalks;
- options have real sound/music/mouse/VSync consumers, while other rows are
  display/state only and none have a general Career persistence owner;
- the 43-node Career graph, grade law, bounded Goodie update/latches, world-110
  unlock, and settled debriefing projection exist; save/load writes, loaded-model
  Won merge, broad later-campaign construction, dynamic debriefing phases, and
  Goodies-page persistence remain open.

Rendering correctly lives in the Godot presentation adapter. Source algorithms
are selectively useful, but the D3D8/D3D9 backend, Win32 shell, render-state
cache, custom resource builder, and heap should remain superseded. Current
render interpolation uses quaternion/nlerp logic rather than Stuart's actor
matrix-linear interpolation; deterministic tests do not establish retail
render parity. HUD work is primarily Steam-static/runtime reconstruction
because HUD source is absent.

The audio classification is more severe:

```text
current Level100Audio:
  disables engine/DS3D attenuation
  manually applies Stuart GetVolumeForPos

unpatched baseline bytes:
  device update at 0x00517B79 sends mCurrentVolume (+0x64),
  not source-attenuated mCurrentAttenuatedVolume (+0x68)
  configures min=3, max=50, rolloff=0.7, doppler=1 plus hard mute
```

Therefore current `SoundManager`/`pcsoundmanager` behavior is
**PARTIAL — SOURCE-PORTED, BUT RELEASED STEAM-REFUTED**. The source/retail
pitch clamp remains aligned. Stuart's `BE On 02` idle-hum call is also
contradicted by the shipped `sounds.sfx` identity and must not be added from
source alone.

### Source mechanisms that should remain superseded

Do not put these in the gameplay parity queue:

- D3D8 device/window/adapter and state-cache implementation;
- the custom allocator, memory-type routing bugs, and pointer arithmetic;
- raw `CActiveReader`/monitor deletion coupling;
- global static `SPtrSet` node pool;
- Xbox memory-card/signature implementation;
- unselected/stale alternate `PC*` engine/frontend/game classes;
- internal MFC/D3D editor application shells;
- ABI-sized raw resource-building machinery where exact-hash retail readers
  already own the released data.

Their useful semantics—ordering, invalidation, ids, resource roles, and
serialization vocabulary—should be expressed in current safe owners.

## Canonical progress queue

This separates bounded near-term corrections from broader discovery families.
P0/P1 items name the current falsifier or evidence dependency. P2 is a thematic
backlog, not a finite completion gate; each family must be split into a counted
function, table, event, or draw/state set before implementation claims close.
Order may change only when new evidence changes impact or dependency.

### P0: current correctness

1. **Migrate deterministic Core from 30 Hz to the established retail 20 Hz
   cadence.** The retail-rate decision is settled; implementation sequencing is
   not. Inventory and convert every per-tick coefficient, message/event
   quantization, hash, and timing assertion before adding further tick-coupled
   source behavior. Acceptance includes an explicit intentional state-hash
   update and focused wall-time equivalence checks.
2. **Create one canonical player-damage funnel.**
   Route every ingress through the retail-corresponding shield, overflow,
   hull, repair, walker-energy, invulnerability, shock, and vibration stages.
   Acceptance: focused table tests for shield-sufficient, overflow,
   `inDamageShields=false`, walker mirror, repair ordering, and invulnerability.
   Augment may remain separately explicit—not silently claimed.
3. **Replace source-port attenuation with released Steam behavior.**
   Stop applying source `GetVolumeForPos` as final device gain. Implement or
   explicitly emulate the Steam 3/50/0.7/doppler/hard-mute contract.
   Acceptance: mechanical state assertions plus copied-runtime distance sweep
   before parity wording.
4. **Correct current source/rebuild documentation.**
   Remove unselected/stale `PCEngine`/`PCGame` as normal candidates, stale unknown
   ground-impact wording, projection-only zoom claim, outdated mission/AI
   breadth, the vague weapon-resource exception unless its exact pair is
   recovered, and the false `Level100Audio.cs` comments that call the manual
   Stuart attenuation path released behavior and deny retail DS3D.

### P1: source-guided bounded behavior

5. **Locate and adjudicate the retail ground-impact body, then implement the
   result.** Stuart `BattleEngine.cpp:2980-2990` supplies an exact provisional
   law, but no cited retail body/runtime evidence yet makes it released parity.
   Acceptance covers normal/slope/velocity cases and
   `inDamageShields=false`; tick conversion depends on item 1.
6. **Implement mutable zoom state and projection propagation**, proving 0.4
   and 1.0 bounds and both input directions after the cadence migration.
7. **Crosswalk and implement the bounded lock/autoaim family:**
   `0x0040ACC0 CalcUnitOverCrossHair`,
   `0x0040B120 UpdateAutoAim`,
   `0x0040B6D0 HandleAutoAim`,
   `0x0040C990 GetLaunchPosition`,
   `0x0040D7C0 GetInterpolatedAutoAimPos`.
   Acceptance covers candidate selection, loss, angular/range rejection, and
   launch direction.
8. **Trace `0x0040DE40 CBattleEngine__AugmentWeapon`** from Damage's
   `+0x2F8/+0x2FC` writes through consume/reset and runtime effect.
9. **Join and persist the result/Career handoff:** replace the canned first-play
   score/time input with the live `EndLevelData` stores, then add safe
   persistence/reload without widening the settled debriefing projection.
10. **Close bounded frontend holes:** language selection and explicit
    unavailable handling for inert rows. Preserve the runtime-adjudicated
    single-page cold-main transition; crosswalk every other transition edge
    individually rather than importing the source dual-page rule globally.

The final-ferry `WaterLoss` assertion remains outside product P0: first isolate
a production-code failure independent of the omniscient test autopilot's
`NavigateToZone` mode-switch policy.

### P2: thematic parity families

11. Landing-jet burn damage and grounded walker map-edge behavior.
12. Cloak, rearm, remaining selected-weapon and Aquila lifecycle state.
13. Death camera, dynamic debrief effects/transitions, and outro handoff.
14. Plane roll, pitch bias, friction, gravity, and the controlled jet
    ground-effect roll-sign capture.
15. General actors, collision, debris, and destruction beyond the bounded
    Level 100 catalog.
16. Audio channel priority/cap, DirectSound loopback, and general music
    sequencing.
17. Options persistence and consumers for display-only rows.
18. Byte-first recovery for high-value absent owners: HUD/DXHud/PCHud,
    Unit/UnitAI/Weapon, BattleLine, MessageBox, Cockpit, world physics, and the
    mission/physics script VMs.
19. Complete D3D8-source→D3D9-retail phase crosswalk using discrete draw/state
    evidence; never infer API parity from source structure.

## Appendix A: complete source-unit census

### Stem-pair semantic census

This table covers every one of the 106 C/C++ files. A “unit” is the
case-preserving `.cpp`/header stem pair, except the two standalone headers.
`Bodies` is physical implementation blocks; `Heads` is target-conditional
definition heads; `Decl` is bodyless callable declarations; `G/E` is
file-scope global/static data definitions and extern variable declarations.
`Inc R/U/A` is literal-relative quoted includes resolved, quoted includes
unresolved, and angle-bracket occurrences.

| Unit | Bytes | Lines | Bodies | Heads | Decl | Class | Struct | Enum | G/E | Macros | Inc R/U/A |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Array | 3,639 | 147 | 25 | 25 | 2 | 3 | 0 | 0 | 0/0 | 1 | 1/3/0 |
| BattleEngine | 107,065 | 4,159 | 163 | 163 | 113 | 3 | 0 | 3 | 2/0 | 14 | 12/29/1 |
| BattleEngineConfigurations | 2,775 | 121 | 6 | 6 | 5 | 1 | 0 | 0 | 3/0 | 1 | 3/2/0 |
| BattleEngineDataManager | 27,396 | 1,435 | 34 | 34 | 8 | 2 | 0 | 0 | 3/0 | 1 | 5/3/2 |
| BattleEngineJetPart | 29,412 | 1,202 | 44 | 44 | 39 | 1 | 0 | 1 | 0/0 | 2 | 7/8/1 |
| BattleEngineWalkerPart | 31,088 | 1,226 | 46 | 46 | 44 | 1 | 0 | 0 | 6/0 | 4 | 9/12/1 |
| CLIParams | 10,504 | 479 | 4 | 4 | 3 | 1 | 0 | 0 | 1/1 | 3 | 2/3/2 |
| Camera | 26,797 | 1,098 | 80 | 80 | 47 | 9 | 0 | 1 | 1/0 | 1 | 7/7/1 |
| Career | 51,102 | 1,738 | 69 | 69 | 35 | 5 | 1 | 2 | 6/3 | 29 | 13/3/0 |
| Controller | 23,104 | 895 | 42 | 42 | 18 | 2 | 1 | 2 | 3/0 | 81 | 7/6/0 |
| DXEngine | 47,651 | 1,715 | 31 | 31 | 19 | 1 | 1 | 0 | 18/0 | 1 | 11/49/0 |
| DXFrontend | 4,868 | 187 | 4 | 4 | 4 | 1 | 0 | 0 | 1/1 | 1 | 4/7/0 |
| DXGame | 4,191 | 170 | 4 | 4 | 2 | 1 | 0 | 0 | 1/0 | 1 | 11/11/0 |
| DXMemBuffer | 16,157 | 715 | 22 | 22 | 15 | 1 | 0 | 1 | 1/0 | 5 | 3/5/0 |
| DXMemoryManager | 15,134 | 585 | 32 | 33 | 19 | 1 | 0 | 0 | 5/1 | 1 | 2/3/0 |
| EditorD3DApp | 76,996 | 2,064 | 29 | 29 | 16 | 1 | 3 | 1 | 1/0 | 15 | 1/7/8 |
| EndLevelData | 2,045 | 89 | 2 | 2 | 2 | 1 | 0 | 0 | 1/1 | 1 | 3/3/0 |
| FEPGoodies | 87,823 | 2,656 | 41 | 41 | 18 | 2 | 0 | 3 | 5/1 | 19 | 8/12/0 |
| FEPLoadGame | 7,401 | 287 | 8 | 8 | 8 | 1 | 0 | 0 | 0/0 | 1 | 4/4/0 |
| FEPSaveGame | 17,413 | 614 | 12 | 12 | 11 | 1 | 0 | 0 | 1/0 | 1 | 5/6/0 |
| FrontEnd | 52,404 | 1,939 | 59 | 59 | 34 | 1 | 0 | 5 | 0/1 | 42 | 19/37/0 |
| InitThing | 34,354 | 1,668 | 52 | 52 | 17 | 16 | 0 | 5 | 0/0 | 1 | 2/9/0 |
| MemoryCard | 2,717 | 118 | 3 | 3 | 21 | 1 | 0 | 0 | 1/1 | 16 | 3/2/0 |
| MemoryManager | 60,057 | 2,355 | 64 | 65 | 37 | 5 | 1 | 1 | 3/2 | 22 | 5/6/5 |
| Music | 14,868 | 784 | 42 | 42 | 21 | 3 | 0 | 2 | 0/3 | 1 | 2/7/3 |
| PCController | 11,237 | 263 | 13 | 13 | 7 | 1 | 0 | 0 | 1/0 | 1 | 4/2/0 |
| PCEngine | 29,433 | 1,147 | 29 | 29 | 18 | 1 | 0 | 0 | 1/0 | 2 | 10/47/0 |
| PCFEPLoadGame | 552 | 31 | 0 | 0 | 0 | 1 | 0 | 0 | 0/0 | 1 | 1/1/0 |
| PCFEPSaveGame | 552 | 31 | 0 | 0 | 0 | 1 | 0 | 0 | 0/0 | 1 | 1/1/0 |
| PCFrontend | 3,763 | 153 | 6 | 6 | 6 | 1 | 0 | 0 | 1/1 | 1 | 5/7/0 |
| PCGame | 9,255 | 324 | 5 | 5 | 3 | 1 | 0 | 0 | 1/0 | 1 | 10/11/0 |
| PCMemoryCard | 2,708 | 121 | 21 | 21 | 1 | 1 | 0 | 0 | 0/0 | 1 | 3/1/0 |
| PCPlatform | 16,125 | 659 | 41 | 41 | 32 | 1 | 0 | 0 | 1/0 | 48 | 6/7/0 |
| Platform | 1,365 | 80 | 1 | 1 | 1 | 1 | 0 | 2 | 0/3 | 1 | 3/6/1 |
| Player | 15,337 | 623 | 32 | 32 | 18 | 1 | 0 | 4 | 0/0 | 1 | 9/5/0 |
| ResourceAccumulator | 29,262 | 1,168 | 17 | 17 | 7 | 2 | 0 | 0 | 16/0 | 18 | 7/14/1 |
| SPtrSet | 10,793 | 459 | 37 | 37 | 13 | 5 | 0 | 0 | 3/0 | 2 | 1/4/0 |
| SoundManager | 46,028 | 2,039 | 67 | 67 | 47 | 5 | 0 | 3 | 4/3 | 6 | 5/11/2 |
| XBoxMemoryCard | 37,151 | 1,509 | 37 | 37 | 35 | 2 | 0 | 1 | 1/0 | 8 | 4/6/0 |
| activereader | 1,651 | 66 | 12 | 12 | 2 | 2 | 0 | 0 | 0/0 | 1 | 2/3/0 |
| actor | 11,125 | 436 | 30 | 30 | 18 | 1 | 0 | 1 | 0/0 | 1 | 5/7/0 |
| chunker | 5,951 | 252 | 20 | 20 | 17 | 2 | 0 | 0 | 0/0 | 3 | 2/2/1 |
| d3dapp | 79,511 | 2,145 | 28 | 28 | 15 | 1 | 3 | 1 | 1/0 | 17 | 1/8/8 |
| engine | 25,075 | 960 | 73 | 73 | 34 | 2 | 0 | 0 | 0/2 | 18 | 10/29/2 |
| event | 1,166 | 46 | 6 | 6 | 1 | 1 | 0 | 0 | 0/0 | 1 | 2/1/0 |
| eventmanager | 18,014 | 641 | 20 | 20 | 14 | 1 | 0 | 0 | 2/1 | 8 | 7/8/1 |
| game | 116,961 | 4,596 | 137 | 137 | 62 | 3 | 3 | 3 | 2/3 | 8 | 17/53/2 |
| ltshell | 73,418 | 2,156 | 118 | 118 | 39 | 1 | 0 | 0 | 11/1 | 20 | 5/17/0 |
| pcsoundmanager | 16,183 | 597 | 24 | 24 | 17 | 2 | 0 | 0 | 1/0 | 5 | 6/9/3 |
| scheduledevent | 2,403 | 85 | 12 | 12 | 2 | 1 | 0 | 0 | 1/0 | 1 | 3/1/0 |
| storage | 373 | 30 | 0 | 0 | 0 | 1 | 0 | 0 | 0/3 | 1 | 1/4/0 |
| thing | 31,337 | 1,148 | 148 | 148 | 46 | 2 | 0 | 3 | 2/0 | 4 | 9/25/1 |
| DX.H (standalone) | 179 | 15 | 0 | 0 | 0 | 0 | 0 | 0 | 0/0 | 1 | 1/1/0 |
| membuffer.h (standalone) | 824 | 40 | 3 | 3 | 0 | 1 | 0 | 0 | 0/0 | 6 | 1/2/0 |
| **Total** | **1,354,693** | **50,266** | **1,855** | **1,857** | **1,013** | **110** | **13** | **45** | **112/32** | **452** | **290/537/46** |

The include total here uses written relative paths. Two additional occurrences
become available only by root-basename recovery, yielding 292/535 and 290
distinct file edges. The literal graph has 288 distinct edges because
`engine.h → membuffer.h` and `eventmanager.cpp → thing.h` each occur twice
under case variants.

### Physical-file byte and line manifest

Physical lines count an unterminated final line. All source bytes and lines sum
exactly to the semantic table above.

| File | Bytes | Lines | File | Bytes | Lines |
| --- | ---: | ---: | --- | ---: | ---: |
| `activereader.cpp` | 477 | 22 | `activereader.h` | 1,174 | 44 |
| `actor.cpp` | 9,271 | 367 | `actor.h` | 1,854 | 69 |
| `Array.cpp` | 197 | 10 | `Array.h` | 3,442 | 137 |
| `BattleEngine.cpp` | 93,772 | 3,672 | `BattleEngine.h` | 13,293 | 487 |
| `BattleEngineConfigurations.cpp` | 2,098 | 92 | `BattleEngineConfigurations.h` | 677 | 29 |
| `BattleEngineDataManager.cpp` | 17,278 | 1,003 | `BattleEngineDataManager.h` | 10,118 | 432 |
| `BattleEngineJetPart.cpp` | 26,801 | 1,090 | `BattleEngineJetPart.h` | 2,611 | 112 |
| `BattleEngineWalkerPart.cpp` | 28,047 | 1,103 | `BattleEngineWalkerPart.h` | 3,041 | 123 |
| `Camera.cpp` | 20,984 | 858 | `Camera.h` | 5,813 | 240 |
| `Career.cpp` | 45,444 | 1,522 | `Career.h` | 5,658 | 216 |
| `chunker.cpp` | 4,605 | 200 | `chunker.h` | 1,346 | 52 |
| `CLIParams.cpp` | 8,851 | 405 | `CLIParams.h` | 1,653 | 74 |
| `Controller.cpp` | 13,847 | 552 | `Controller.h` | 9,257 | 343 |
| `d3dapp.cpp` | 70,526 | 1,929 | `d3dapp.h` | 8,985 | 216 |
| `DX.H` | 179 | 15 | `DXEngine.cpp` | 44,268 | 1,598 |
| `DXEngine.h` | 3,383 | 117 | `DXFrontend.cpp` | 4,197 | 163 |
| `DXFrontend.h` | 671 | 24 | `DXGame.cpp` | 3,817 | 149 |
| `DXGame.h` | 374 | 21 | `DXMemBuffer.cpp` | 14,555 | 635 |
| `DXMemBuffer.h` | 1,602 | 80 | `DXMemoryManager.cpp` | 12,307 | 478 |
| `DXMemoryManager.h` | 2,827 | 107 | `EditorD3DApp.cpp` | 67,866 | 1,847 |
| `EditorD3DApp.h` | 9,130 | 217 | `EndLevelData.cpp` | 1,044 | 51 |
| `EndLevelData.h` | 1,001 | 38 | `engine.cpp` | 17,897 | 719 |
| `engine.h` | 7,178 | 241 | `event.cpp` | 468 | 18 |
| `event.h` | 698 | 28 | `eventmanager.cpp` | 14,523 | 548 |
| `eventmanager.h` | 3,491 | 93 | `FEPGoodies.cpp` | 85,129 | 2,534 |
| `FEPGoodies.h` | 2,694 | 122 | `FEPLoadGame.cpp` | 6,698 | 249 |
| `FEPLoadGame.h` | 703 | 38 | `FEPSaveGame.cpp` | 16,122 | 565 |
| `FEPSaveGame.h` | 1,291 | 49 | `FrontEnd.cpp` | 43,757 | 1,633 |
| `Frontend.h` | 8,647 | 306 | `game.cpp` | 103,727 | 4,166 |
| `game.h` | 13,234 | 430 | `InitThing.cpp` | 9,988 | 699 |
| `InitThing.h` | 24,366 | 969 | `ltshell.cpp` | 56,174 | 1,821 |
| `ltshell.h` | 17,244 | 335 | `membuffer.h` | 824 | 40 |
| `MemoryCard.cpp` | 196 | 11 | `MemoryCard.h` | 2,521 | 107 |
| `MemoryManager.cpp` | 49,520 | 1,912 | `MemoryManager.h` | 10,537 | 443 |
| `Music.cpp` | 12,042 | 658 | `Music.h` | 2,826 | 126 |
| `PCController.cpp` | 9,917 | 225 | `PCController.h` | 1,320 | 38 |
| `PCEngine.cpp` | 26,325 | 1,044 | `PCEngine.h` | 3,108 | 103 |
| `PCFEPLoadGame.cpp` | 79 | 7 | `PCFEPLoadGame.h` | 473 | 24 |
| `PCFEPSaveGame.cpp` | 79 | 7 | `PCFEPSaveGame.h` | 473 | 24 |
| `PCFrontend.cpp` | 2,954 | 120 | `PCFrontend.h` | 809 | 33 |
| `PCGame.cpp` | 8,854 | 301 | `PCGame.h` | 401 | 23 |
| `PCMemoryCard.cpp` | 669 | 21 | `PCMemoryCard.h` | 2,039 | 100 |
| `PCPlatform.cpp` | 12,133 | 506 | `PCPlatform.h` | 3,992 | 153 |
| `pcsoundmanager.cpp` | 13,986 | 508 | `pcsoundmanager.h` | 2,197 | 89 |
| `Platform.cpp` | 393 | 23 | `Platform.h` | 972 | 57 |
| `Player.cpp` | 12,519 | 511 | `Player.h` | 2,818 | 112 |
| `ResourceAccumulator.cpp` | 26,207 | 1,056 | `ResourceAccumulator.h` | 3,055 | 112 |
| `scheduledevent.cpp` | 907 | 35 | `scheduledevent.h` | 1,496 | 50 |
| `SoundManager.cpp` | 37,556 | 1,742 | `SoundManager.h` | 8,472 | 297 |
| `SPtrSet.cpp` | 7,548 | 348 | `SPtrSet.h` | 3,245 | 111 |
| `storage.cpp` | 45 | 3 | `storage.h` | 328 | 27 |
| `thing.cpp` | 19,657 | 830 | `thing.h` | 11,680 | 318 |
| `XBoxMemoryCard.cpp` | 33,744 | 1,408 | `XBoxMemoryCard.h` | 3,407 | 101 |

Support files are `LICENSE` (35,823 bytes, 674 lines) and `README.md` (11
bytes, one line). All 108 tracked content files therefore total 1,390,527 bytes
and 50,941 physical lines. The source total is 50,215 CRLF terminators plus 51
unterminated final lines; exactly 51 of 106 source files lack a terminal
newline.

### Parser audit and collision registry

The ten rejected raw `function_definition` nodes are:

```text
Career.cpp:292,430,504,1337
eventmanager.cpp:334,369,522
game.cpp:1417
SPtrSet.cpp:299              FOR_ALL_ITEMS_IN
ltshell.cpp:1199             FAILED(hr)
```

The first nine are `FOR_ALL_ITEMS_IN` macro/control uses. The 46 recovered real
bodies are at:

```text
Camera.h:32
Career.h:130
EditorD3DApp.h:203
ltshell.h:225,227-233,237,244-245,247,249,251-256,260,267-268,
          270,272-276,279,281,284-286
PCMemoryCard.h:11-13
pcsoundmanager.h:55,67-68
SoundManager.h:168
thing.h:143-144,295
XBoxMemoryCard.h:53
```

All 54 headers have guards, but there are only 53 unique guards:
`d3dapp.h` and `EditorD3DApp.h` both use `D3DAPP_H`. Their duplicate D3D
framework types are therefore mutually exclusive by include order.

There are 13 duplicate definition-signature groups / 28 occurrences, all
target/config alternatives:

```text
CArray::ReSize                 Array.h:27/29/32/35
CArray constructor             Array.h:15/18
CArray destructor              Array.h:16/19
CCareer::Load                  Career.cpp:1095 / Career.h:129
CCareer::SizeOfSaveGame        Career.cpp:1151 / Career.h:133
con_setgammabias               DXEngine.cpp:113 / PCEngine.cpp:110
WndProc                        EditorD3DApp.cpp:73 / d3dapp.cpp:79
SortModesCallback              EditorD3DApp.cpp:177 / d3dapp.cpp:188
goodies_prepare_projection     FEPGoodies.cpp:1790/1808
goodies_restore_projection     FEPGoodies.cpp:1800/1818
CPCEngine::GetSky              PCEngine.h:48/50
PCLTShell::ForceRS             ltshell.h:201/204
PCLTShell::ForceTS             ltshell.h:202/205
```

The 112 global/static definitions reduce to 105 unique names. The seven
duplicate-name groups are target/config alternatives: `g_pD3DApp`, `ENGINE`,
`FRONTEND`, `GAME`, `goodies_matProjSave`, `resfile_vshadersize`, and
`allowed_to_load_sample`. Extern names with no definition in the pin are
`MUSIC`, `STORAGE`, and `performing_stress_test`; their owning implementations
are absent.

## Appendix B: finite source registries

### Complete class/struct definition registry

This is the exact definition-body registry, not a forward-declaration list.
`@N` means the definition starts at line N.

```text
activereader.h:
  CGenericActiveReader@11, CActiveReader@29
Array.h:
  CArray@11, CSArray@54, COSet@75
actor.h:
  CActor@13 [macro-declared; base CComplexThing]
BattleEngine.h:
  CLockInfo@48, CDamageFlash@66,
  CBattleEngine@72 [macro-declared; base CUnit]
BattleEngineConfigurations.h:
  UBattleEngineConfigurations@9
BattleEngineDataManager.h:
  CBattleEngineData@13, UBattleEngineDataManager@243
BattleEngineJetPart.h:
  CBattleEngineJetPart@23
BattleEngineWalkerPart.h:
  CBattleEngineWalkerPart@16
Camera.h:
  CCamera@19, CThingCamera@40, CThing3rdPersonCamera@59,
  CViewPointCamera@81, CPanCamera@119, CMovieCamera@144,
  CControllableCamera@172, CGenericCamera@207,
  CInterpolatedCamera@222
Career.h:
  CGrade@28, CGoodie@49, CCareerNodeLink@66, CCareerNode@76,
  struct CLevelStructure@104, CCareer@112
chunker.h:
  CChunker@11, CChunkReader@33
CLIParams.h:
  CCLIParams@4
Controller.h:
  IController@37, struct ControllerMaping@72, CController@174
d3dapp.h:
  struct D3DModeInfo@41, struct D3DDeviceInfo@58,
  struct D3DAdapterInfo@84, CD3DApplication@115
DXEngine.cpp:
  local struct Vert@1161
DXEngine.h:
  CDXEngine@22
DXFrontend.h:
  CDXFrontEnd@9
DXGame.h:
  CDXGame@9
DXMemBuffer.h:
  CDXMemBuffer@20
DXMemoryManager.h:
  CDXMemoryManager@10
EditorD3DApp.h:
  struct D3DModeInfo@41, struct D3DDeviceInfo@58,
  struct D3DAdapterInfo@84, CEditorD3DApp@115
EndLevelData.h:
  CEndLevelData@12
engine.h:
  CViewport@58, CEngine@66
event.h:
  CEvent@13
eventmanager.h:
  CEventManager@43
FEPGoodies.h:
  CGoodieData@20, CFEPGoodies@50
FEPLoadGame.h:
  CFEPLoadGame@6
FEPSaveGame.h:
  CFEPSaveGame@7
Frontend.h:
  CFrontEnd@100
game.cpp:
  local CWaitForStart@1238, local CGameCreditControlHandler@4086
game.h:
  struct SFrontEndSettings@63, struct TimeRecord@76,
  struct RenderRecord@88, CGame@108
InitThing.h:
  CInitCSThing@72, CInitThing@112, CTreeInitThing@360,
  CSpawnerInitThing@410, CSquadInitThing@623, CWallInitThing@678,
  CCutsceneInitThing@733, CStartInitThing@791,
  CSphereTriggerInitThing@833, CUnitInitThing@868,
  CRoundInitThing@887, CBattleEngineInitThing@905,
  CExplosionInitThing@918, CAnimalInitThing@939,
  CFeatureInitThing@947, CHazardInitThing@958
ltshell.h:
  PCLTShell@55
membuffer.h:
  IMemBuffer@11
MemoryCard.h:
  CMemoryCard@27
MemoryManager.cpp:
  local CMutexGrabber@67
MemoryManager.h:
  struct MemoryTypeData@193, CMemoryBlock@218, CMemoryHeap@256,
  CMemoryTag@377, CMemoryManager@392
Music.h:
  CSong@16, CMusicMenu@30, CMusic@48
PCController.h:
  CPCController@14
PCEngine.h:
  CPCEngine@19
PCFEPLoadGame.h:
  CPCFEPLoadGame@6
PCFEPSaveGame.h:
  CPCFEPSaveGame@6
PCFrontend.h:
  CPCFrontEnd@11
PCGame.h:
  CPCGame@9
PCMemoryCard.h:
  CPCMemoryCard@8
PCPlatform.h:
  CPCPlatform@57
pcsoundmanager.h:
  CPCSample@24, CPCSoundManager@42
Platform.h:
  CPlatform@28
Player.h:
  CPlayer@58
ResourceAccumulator.h:
  CResFileHeader@33, CResourceAccumulator@62
scheduledevent.h:
  CScheduledEvent@13
SoundManager.h:
  CEffect@43, CSample@103, CSoundEvent@124,
  CSoundManagerDebugMenu@162, CSoundManager@173
SPtrSet.h:
  SPtrSetNode@13, GenericSPtrSet@25, SPtrSet@67,
  GenericListIterator@90, ListIterator@103
storage.h:
  CStorage@4
thing.h:
  CThing@65 [macro-declared; bases IAudibleThing, IRenderableThing],
  CComplexThing@257 [macro-declared; base CThing]
XBoxMemoryCard.cpp:
  local CXBoxSaveHeader@23
XBoxMemoryCard.h:
  CXBoxMemoryCard@15
```

The generic AST recognizes 106 class bodies; the four macro-declared bodies
raise the exact class total to 110. The 13 struct occurrences represent ten
unique names because `D3DModeInfo`, `D3DDeviceInfo`, and `D3DAdapterInfo` are
duplicated in the mutually guarded D3D application headers.

### Complete enum registry

There are 45 enum definitions and 312 enumerators. `FEPSaveGame.h:24` is only
a parameter use of `enum EFETextHack`, not a definition.

| Source | Enum | n | Enumerators in source order |
| --- | --- | ---: | --- |
| `actor.h:7` | `ActorEvent` | 2 | `MOVE=3000`, `LF_MOVE` |
| `BattleEngine.h:20` | `EBattleEngineEvent` | 4 | `BECOME_JET=6000`, `BECOME_WALKER`, `CALC_UNIT_OVER_CROSSHAIR`, `HANDLE_AUTO_AIM` |
| `BattleEngine.h:28` | `EBattleEngineState` | 4 | `MORPHING_INTO_WALKER`, `MORPHING_INTO_JET`, `WALKER`, `JET` (all `BATTLE_ENGINE_STATE_` prefixed) |
| `BattleEngine.h:36` | `EEngineState` | 3 | `kAfterburnerEngines=0`, `kNormalEngines`, `kEnginesOff` |
| `BattleEngineJetPart.h:14` | `EJetFlightModel` | 2 | `SIMPLE_JET_FLIGHTMODEL`, `ADVANCED_JET_FLIGHTMODEL` |
| `Camera.h:114` | `ECameraEvent` | 1 | `UPDATE_CAMERA=2000` |
| `Career.h:40` | `EGoodieState` | 4 | `GS_UNKNOWN`, `GS_INSTRUCTIONS`, `GS_NEW`, `GS_OLD` |
| `Career.h:58` | `ECNLinkType` | 3 | `CN_NOT_COMPLETE`, `CN_COMPLETE`, `CN_COMPLETE_BROKEN` |
| `Controller.h:18` | `EControlType` | 8 | frontend, mech, camera, game-interface, game, message-log, briefing-log, game-menu controls |
| `Controller.h:57` | `EJoyButtonPushType` | 10 | `BUTTON_ON`, `BUTTON_ONCE`, `BUTTON_RELEASE`, `BUTTON_REPEAT`, analog ±, analog ± as repeat, `KEY_ONCE`, `KEY_ON` |
| `d3dapp.h:19` | `APPMSGTYPE` | 3 | `MSG_NONE`, `MSGERR_APPMUSTEXIT`, `MSGWARN_SWITCHEDTOREF` |
| `DXMemBuffer.h:9` | `EMemoryType` | 1 | `MEMTYPE_MEMBUFFER` (`SIMPLE_MESHES` fallback) |
| `EditorD3DApp.h:19` | `APPMSGTYPE` | 3 | same three values as `d3dapp.h` |
| `FEPGoodies.cpp:841` | `EGoodieTextType` | 3 | `GTT_GENERIC`, `GTT_UNIT`, `GTT_PERSON` |
| `FEPGoodies.h:11` | `EGoodieType` | 5 | `GT_IMAGE=0`, `GT_MESH`, `GT_FMV`, `GT_LEVEL`, `GT_CHEAT` |
| `FEPGoodies.h:112` | `EGoodyState` | 3 | `NO_GOODY`, `GOODY_LOADING`, `GOODY_LOADED` |
| `Frontend.h:52` | `EFrontEndEntry` | 3 | `FEE_START=0`, `FEE_FROM_ATTRACT`, `FEE_TITLE_SCREEN` |
| `Frontend.h:60` | `EFrontEndSound` | 4 | `FES_MOVE=0`, `FES_SELECT`, `FES_BACK`, `FES_NUM_SOUNDS` |
| `Frontend.h:104` | anonymous | 1 | `NUM_CONTROLLER_PORTS=2` |
| `Frontend.h:106` | anonymous | 1 | `NUM_CONTROLLER_PORTS=4` |
| `Frontend.h:155` | `AutoSaveMode` | 3 | `AUTO_SAVE_NOT`, `AUTO_SAVE_NORMAL`, `AUTO_SAVE_PRETEND` |
| `game.h:31` | `EGameEvent` | 7 | `DEMO_RESTART_LEVEL=2000`, `FINISHED_PRE_RUN`, `FINISHED_PANNING`, respawn player 1/2, pause, continue sound fade |
| `game.h:42` | `EGameState` | 10 | not-running, pre-running, panning, playing, level lost/won, player 1/2 won, drawn, quit |
| `game.h:56` | `EWingmanType` | 3 | `kTaraWingman=0`, `kBillyWingman`, `kJasonWingman` |
| `InitThing.h:31` | `EOrientationType` | 2 | `EULER_ANGLES`, `DIRECTION_COSINE_MATRIX` |
| `InitThing.h:37` | `EAllegiance` | 7 | Forseti, Muspell, neutral, undefined, invalid, toggle, independent |
| `InitThing.h:49` | `ECollisionLevel` | 3 | outer sphere, approximate geometry shapes, mesh |
| `InitThing.h:57` | `ECollisionResponse` | 3 | passive, static, slide |
| `InitThing.h:64` | `ECollisionType` | 4 | nothing, ground, water, thing |
| `MemoryManager.h:50` | `EMemoryType` | 130 | exact sequence below |
| `Music.h:8` | `EMusicPlayType` | 4 | single, linear, random, selection |
| `Music.h:39` | `EMusicSelection` | 5 | frontend, credits, tutorial, stealth, in-game |
| `Platform.h:6` | `EQuitType` | 8 | none, frontend, system, load error, restart, timeout, user frontend, user title |
| `Platform.h:18` | `EFontType` | 4 | normal, small, debug, title |
| `Player.h:12` | `EPlayerStats` | 8 | units destroyed, rounds fired/hit, cheated, jet/walker time, damage taken, count |
| `Player.h:27` | `EKilledType` | 8 | aircraft, vehicles, emplacements, infantry (`INFANTY` spelling), mechs, total, A/S-grade hacks |
| `Player.h:42` | `EPlayerEvent` | 1 | `GOTO_CONTROL_VIEW=4000` |
| `Player.h:48` | `EPlayerCameraView` | 3 | pan, first-person, third-person |
| `SoundManager.h:26` | `ESoundTrackingType` | 4 | no tracking, initial position, follow-and-die, follow-don't-die |
| `SoundManager.h:35` | `ESoundType` | 2 | menu, game |
| `SoundManager.h:96` | `ESampleType` | 3 | mono, left, right |
| `thing.h:33` | `EThingEvent` | 4 | `SHUTDOWN=2000`, `INIT_SCRIPT`, `START_DIE_PROCESS`, `READY_SCRIPT` |
| `thing.h:41` | `THING_FLAGS` | 9 | declared shutdown, map-who, dying, don't-render, invisible, objective, big, slide, removed-unit-type bits |
| `thing.h:54` | `EAIState` | 5 | `AI_ON=0`, `AI_OFF`, `AI_NORMAL`, `AI_DEFENSIVE`, `AI_ONF` |
| `XBoxMemoryCard.h:80` | `UpdateReason` | 4 | no, unplugged, plugged, module-init |

Duplicate identities are conditional: `APPMSGTYPE` is duplicated under the
shared `D3DAPP_H` guard; `EMemoryType` has the full memory-manager definition
and the one-entry `SIMPLE_MESHES` fallback; `NUM_CONTROLLER_PORTS` has two
conditional anonymous definitions.

### Exact 130-entry memory-type order

```text
MEMTYPE_GENERIC=0, MEMTYPE_MESH, MEMTYPE_TEXTURE, MEMTYPE_TEXTURE_DATA,
MT_PHYSICS, MT_THING, MT_UNIT_THING, MT_TREE_THING, MT_SQUAD,
MT_INIT_THING, MT_BUBBLE, MT_CST, MT_DUNNO_THING, MT_ROUND,
MT_ROUND_DATA, MT_UNIT_DATA, MEMTYPE_PARTICLE, MEMTYPE_MEMBUFFER,
MEMTYPE_FLEXARRAY, MEMTYPE_CAPTURE, MEMTYPE_MUSIC, MEMTYPE_BATTLEENGINE,
MEMTYPE_AI, MEMTYPE_GUIDE, MT_SCRIPT, MT_VM_SCRIPT, MT_INST_SCRIPT,
MEMTYPE_MOTIONCONTROLLER, MEMTYPE_CHUNKER, MEMTYPE_CUTSCENE,
MEMTYPE_EQUIPMENT, MEMTYPE_VBUFTEXTURE, MEMTYPE_INFLUENCEMAP, MEMTYPE_MAP,
MEMTYPE_HEIGHTFIELD, MEMTYPE_JCLTEXTURE, MEMTYPE_MESHTEXTURE,
MEMTYPE_NAVIGATION, MEMTYPE_CAMERA, MEMTYPE_CONTROLLER, MEMTYPE_PLAYER,
MEMTYPE_MESSAGEBOX, MEMTYPE_MESSAGELOG, MEMTYPE_FEARGRID, MEMTYPE_VBUFFER,
MEMTYPE_VBUFFER_DATA, MEMTYPE_DYNAMIC_VBUFFER_DATA, MEMTYPE_IBUFFER,
MEMTYPE_MAPTEX, MEMTYPE_KEMPYCUBE, MEMTYPE_SKY, MEMTYPE_WATER,
MEMTYPE_LIGHT, MEMTYPE_LANDSCAPE, MEMTYPE_GAMUT, MEMTYPE_FRONTEND,
MEMTYPE_HUD, MEMTYPE_IMPOSTER, MEMTYPE_MESHVB, MEMTYPE_RENDERTHING,
MEMTYPE_WEAPONMODE, MEMTYPE_WEAPON, MEMTYPE_SPAWNER, MEMTYPE_EXPLOSION,
MEMTYPE_COMPONENT, MEMTYPE_FEATURE, MEMTYPE_DETAILLEVEL,
MEMTYPE_EVENTMANAGER, MEMTYPE_SHADOW, MEMTYPE_MAPWHO, MEMTYPE_POLYBUCKET,
MEMTYPE_POLYBUCKET_ENTRY, MEMTYPE_PTRSET, MEMTYPE_RADAR, MEMTYPE_SOUND,
MEMTYPE_SOUND_SAMPLE, MEMTYPE_SPTRSET, MEMTYPE_BYTESPRITE, MEMTYPE_CONSOLE,
MEMTYPE_WORLDMESHLIST, MEMTYPE_VERTEXSHADER, MEMTYPE_WALL, MEMTYPE_TREE,
MEMTYPE_FONT, MEMTYPE_ARRAY, MT_DESTROYABLESEGMENT, MT_DISPLAYLIST,
MT_PS2PROFILER, MT_PRIMITIVECOMPILER, MEMTYPE_ACTIVE_READER,
MT_LANDSCAPEDATA, MEMTYPE_SPHERETRIGGER, MEMTYPE_GENERAL_VOLUME,
MEMTYPE_SCRIPT_THING_PTR, MEMTYPE_DELETION_CALLBACK_LIST, MT_PALETTIZER,
MEMTYPE_FMV, MEMTYPE_SCRATCHPAD, MEMTYPE_TEMP, MEMTYPE_MEMTAG,
MEMTYPE_DUMPTEMP, MEMTYPE_ATMOSPHERICS, MEMTYPE_AREA, MEMTYPE_DIRECTOR,
MEMTYPE_GROUPMANAGER, MEMTYPE_PATH, MEMTYPE_WORLD, MEMTYPE_CONFIGURATIONS,
MEMTYPE_COLLISION, MEMTYPE_MODELVIEWER, MEMTYPE_NODE, MEMTYPE_GAMEDISC,
MEMTYPE_STATICSHADOW, MEMTYPE_DEBUGMARKER, MEMTYPE_TEXT,
MEMTYPE_SCENENODE, MEMTYPE_MESHCACHE, MEMTYPE_SCENE, MEMTYPE_SCRIPT,
MEMTYPE_MIXERMAP, MEMTYPE_HELP_TEXT_DISPLAY, MEMTYPE_STORAGE,
MEMTYPE_BINK_VIDEO, MEMTYPE_MAPWHO_ENTRY, MEMTYPE_MEMORYCARD,
MEMTYPE_POSE, MEMTYPE_TINY_HEAP, MEMTYPE_INDEX_BUFFER, MEMTYPE_UNKNOWN,
MEMTYPE_LIMIT
```

The exact `gMemTypeData` permutation relative to that order is:

```text
table 0..41   = enum 0..41
table 42      = MEMTYPE_MESSAGEBOX/"MessageLog", not enum 42 MESSAGELOG
table 43..46  = enum 43..46
table 47..80  = enum 48..81
table 81      = enum 47 MEMTYPE_IBUFFER
table 82..95  = enum 82..95
table 96..124 = enum 97..125
table 125     = enum 127 MEMTYPE_INDEX_BUFFER
table 126     = enum 126 MEMTYPE_TINY_HEAP
table 127     = enum 96 MEMTYPE_FMV
table 128..129= enum 128..129
```

Every table limit is `0xFFFFFFFF`.

### Initialized fixed-array registry

| Source | Array | Capacity / explicit initializers | Audit meaning |
| --- | --- | ---: | --- |
| `Career.cpp:24-75` | `level_structure[NUM_LEVELS][5]` | 43×5 / 43 rows | complete campaign graph |
| `Career.cpp:1221` | `temp[50]` | 50 / empty string | local scratch |
| `d3dapp.cpp:218` | `DeviceTypes[]` | inferred 2 / 2 | HAL, REF |
| `DXEngine.cpp:441` | `test_number_available[8]` | 8 / 4 | remaining four zero-initialized |
| `DXEngine.cpp:826` | `rsx[]` | 2 / 2 | alpha-test exception + sentinel |
| `DXEngine.cpp:1211-1214` | `verts[4]` | 4 / 4 | first local vertex quad |
| `DXEngine.cpp:1242-1245` | `verts[4]` | 4 / 4 | second local vertex quad |
| `DXMemoryManager.cpp:269` | `buf[20]` | 20 / empty string | diagnostics |
| `EditorD3DApp.cpp:202` | `strDeviceDescs[]` | 2 / 2 | HAL, REF descriptions |
| `EditorD3DApp.cpp:203` | `DeviceTypes[]` | 2 / 2 | HAL, REF |
| `FEPGoodies.cpp:150-386` | `goodies[]` | 232 / 232 | indices 0..231: 78 unique ids, 122 id-79, 32 defaults; grid separately emits invalid 232 |
| `ltshell.cpp:1166` | `dwAxes[2]` | 2 / 2 | DirectInput X/Y axes |
| `ltshell.cpp:1167` | `lDirection[2]` | 2 / 2 | zeros |
| `ltshell.cpp:1518-1543` | `mNotRI[172]` | 172 / 172 | render-state exclusion bitmap |
| `ltshell.cpp:1544-1638` | `g_rsnames[172]` | 172 / 172 | D3D8 render-state index labels |
| `ltshell.cpp:1639-1669` | `g_tsnames[30]` | 30 / 29 | slot 29 implicitly null |
| `MemoryManager.cpp:99-241` | `gMemTypeData[]` | 130 / 130 | 67 ordinal mismatches |
| `MemoryManager.cpp:1318` | `num_small_blocks[2]` | 2 / 2 | zeros |
| `MemoryManager.cpp:1319` | `small_blocks_mem_used[2]` | 2 / 2 | zeros |
| `PCController.cpp:15-139` | `mMappings[]` | 109 / 109 | 108 mappings + sentinel |
| `PCEngine.cpp:612` | `rsx[]` | 2 / 2 | alpha-test exception + sentinel |
| `ResourceAccumulator.cpp:43` | `resdata_tag[8]` | 8 / `"AYADATA"` | seven bytes + NUL |
| `ResourceAccumulator.cpp:54` | `resdata_end[4]` | 4 / `"END"` | three bytes + NUL |
| `XBoxMemoryCard.cpp:887` | `root_path[4]` | 4 / `"x:\\"` | local root |
| `XBoxMemoryCard.cpp:1018` | `root_path[4]` | 4 / `"x:\\"` | local root |
| `XBoxMemoryCard.cpp:1335` | `root_path[4]` | 4 / `"x:\\"` | local root |

The ten zero entries in `mNotRI` are render states 28 `FOGENABLE`, 34
`FOGCOLOR`, 35 `FOGTABLEMODE`, 36 `FOGSTART`, 37 `FOGEND`, 38 `FOGDENSITY`,
48 `RANGEFOGENABLE`, 137 `LIGHTING`, 139 `AMBIENT`, and 140
`FOGVERTEXMODE`. `g_tsnames[12]` is literally `"12"`; slots 0..11 and 13..28
name their D3D8 states, and slot 29 is null.

### Goodies and source controller table arithmetic

`FEPGoodies.cpp:150-386` has exactly 232 rows:

```text
GOODIES_1 .. GOODIES_78     78 rows, once each
GOODIES_79                 122 rows
default CGoodieData()       32 rows, used as movie slots
TOTAL_GOODIES              232
```

`PCController.cpp:15-139` has exactly 109 rows:

```text
configuration -1 common     68
configuration 1             10
configuration 2             10
configuration 3             10
configuration 4             10
END_CONTROL_MAPPINGS         1
```

It references 60 distinct action names. Including the sentinel, push-type
frequencies are `BUTTON_ONCE=26`, `BUTTON_REPEAT=4`,
`ANALOGUE_MINUS=20`, `ANALOGUE_PLUS=20`, `KEY_ONCE=21`,
analog-plus/minus-as-repeat `=2` each, `BUTTON_ON=12`, and
`BUTTON_RELEASE=2`. This is the developer source table, not the Steam
`defaultoptions.bea` contract.

### Complete active source CLI registry

There are 44 unique active switch spellings and 46 active checks.
`-forcewindowed` and `-resbuildermode` are each checked twice. Comparisons are
case-insensitive.

| Switch | Argument | Exact source effect |
| --- | --- | --- |
| `-artists` | — | `mArtistTest=TRUE` |
| `-nostaticshadows` | — | `mNoStaticShadows=TRUE` |
| `-hidetail` | — | `mHiDetailMode=TRUE` |
| `-decimatemeshes` | — | `mDecimateMeshes=TRUE` |
| `-nomeshpartreduction` | — | `mNoMeshPartReduction=TRUE` |
| `-textureramlimit` | decimal integer | `mTextureRAMLimit` |
| `-forcewindowed` | — | `mForceWindowed=TRUE`; duplicated check |
| `-emulatedvd` | — | `mEmulateDVD=TRUE` |
| `-showdebugtrace` | — | `mShowDebugTrace=TRUE` |
| `-buildgoodies` | — | `mBuildGoodies=true` |
| `-resbuildermode` | — | `mResBuilderMode=TRUE`; duplicated check |
| `-nocodeoffcd` | — | `mNoCodeOffCD=TRUE` |
| `-geforce2` | — | Geforce3 false, forced card true |
| `-geforce3` | — | Geforce3 true, forced card true |
| `-vshaders` | — | shaders true, forced-shaders true |
| `-novshaders` | — | shaders false, **forced-shaders false**; returns to autodetect, not forced-off |
| `-nomusic` | — | `mMusic=FALSE` |
| `-nosound` | — | `mSound=FALSE` |
| `-pure` | — | `mPureDevice=TRUE` |
| `-impure` | — | `mPureDevice=FALSE` |
| `-devkit` | — | `mDevKit=TRUE` |
| `-quickcompression` | — | `mNiceCompression=false` |
| `-largeram` | — | `mLargeRAM=TRUE` |
| `-pal` | — | `mPal=TRUE` |
| `-ntsc` | — | `mPal=FALSE` |
| `-buildresources` | following non-hyphen tokens | recognizes PC/PS2/XBOX, enables requested builds, sets build mode and heap to 256 MiB |
| `-nobaseresources` | — | `mNoBaseResources=TRUE` |
| `-devmode` | — | `mDeveloperMode=TRUE` |
| `-skipfmv` | — | `mSkipFMV=TRUE` |
| `-attractmode` | — | `mAttractMode=TRUE` |
| `-traceconsole` | — | immediate `CONSOLE.SetTrace(TRUE)` |
| `-modelviewer` | — | dev-only; enable and set heap to 64 MiB |
| `-buildmodelinfo` | — | dev-only |
| `-cutsceneeditor` | — | dev-only |
| `-killhud` | — | dev-only |
| `-level` | decimal integer | `mLevelNo` |
| `-clearutility` | — | Xbox-only |
| `-reboot` | decimal integer | Xbox-only reboot-cycle count |
| `-stresstest` | decimal integer | `mStressTest` |
| `-norumble` | — | immediate platform rumble disable |
| `-record` | one token | filename + record boolean |
| `-play` | one token | same filename buffer + playback boolean |
| `-configuration` | decimal integer | `mConfigurationNo` |
| `-mem` | positive integer MiB | immediate platform heap size |

`PC`, `PS2`, and `XBOX` are operands to `-buildresources`, not switches.
Commented `-controller`, `-joymode`, and `-character` comparisons are inactive.

Constructor defaults are:

```text
mArtistTest=false; mNoStaticShadows=false; mConfigurationNo=0; mLevelNo=-1;
mMusic=true; mDeveloperMode=false;
mBuildResources=false; mBuildPCResources=false; mBuildPS2Resources=false;
mBuildXBOXResources=false; mNoBaseResources=false; mBuildModelInfo=false;
mBuildGoodies=false; mGeforce3=false; mVShaders=false; mForcedCard=false;
mForcedShaders=false; mForceWindowed=false; mPureDevice=true;
mEmulateDVD=false; mDevKit=false; mHiDetailMode=false;
mDecimateMeshes=false; mTextureRAMLimit=0x7fffffff; mLargeRAM=false;
mPal=true; mNoCodeOffCD=false; mResBuilderMode=false; mRecordDemo=false;
mPlaybackDemo=false; mNiceCompression=true; mSound=true;
mNoMeshPartReduction=false; mGoStraightToDeviceSelectScreen=-1;
mSkipFMV=false; mKillHUD=false; mStressTest=0; mLanguage=LANG_ENGLISH;
mShowDebugTrace=false; mAttractMode=false; mInactiveTimeout=-1;
mGameplayTimeout=-1;
DEV_VERSION: mModelViewer=false; mCutsceneEditor=false;
TARGET==XBOX: mBasePath="d:"; mClearUtility=false; mCyclesBeforeReboot=1.
```

`mDemoFilename[256]` is not initialized; only `-record`/`-play` writes it. No
active switch changes the device-select field, language, timeouts, or Xbox base
path. The parser splits only literal spaces, has no quotes or tab grammar,
ignores unknown tokens, increments past value switches without an end guard,
and concatenates `argv` through unbounded `strcat` into a 4,096-byte buffer.
Both `-record` and `-play` may remain true; the last filename wins. These are
source defects, not automatically Steam defects.

## Appendix C: complete missing quoted-include registry

This is the exact 202-target basename-absent registry, totaling 535 include
occurrences. Each entry is `normalized target=occurrences/files`. Normalization
lowercases, converts backslashes to `/`, and collapses repeated slashes.
Availability is a case-insensitive basename comparison against all 106 supplied
C/C++ files. This intentionally retains quoted SDK/CRT names because the source
author chose quoted-include syntax; the registry is a text/dependency result,
not a claim that every target should have been project-authored.

```text
../capture.h=1/1
../resource.h=1/1
action.h=1/1
animaltype.h=1/1
assert.h=1/1
asynccache.h=1/1
atmospherics.h=5/5
audiblething.h=3/3
battleline.h=2/2
bspline.h=2/2
capture.h=3/3
cframetimer.h=1/1
cockpit.h=4/4
collisionseekinground.h=1/1
collisionseekingthing.h=4/4
common.h=52/52
console.h=21/21
credits.h=2/2
cutscene.h=3/3
cutsceneeditor.h=3/3
cylinder.h=2/2
d3d8.h=1/1
d3dres.h=1/1
d3dutil.h=1/1
d3dutils.h=4/4
data/missionscripts/onsldef.msl=2/2
data/missionscripts/text/text.stf=2/2
debris.h=4/4
debuglog.h=28/25
debugmarker.h=4/4
debugtext.h=6/6
deviceobject.h=2/2
dxhud.h=1/1
dxpatchmanager.h=1/1
dxutil.h=1/1
explosion.h=1/1
fcoords.h=2/2
feargrid.h=2/2
feature.h=1/1
femessbox.h=3/3
fepbeconfig.h=1/1
fepbriefing.h=1/1
fepcommon.h=1/1
fepcontroller.h=1/1
fepcredits.h=1/1
fepdebriefing.h=1/1
fepdemomain.h=1/1
fepdevelopment.h=1/1
fepdevselect.h=1/1
fepdirectory.h=1/1
fepe3levelselect.h=1/1
fepintro.h=1/1
feplanguagetest.h=1/1
feplevelselect.h=1/1
fepmain.h=1/1
fepmultiplayer.h=1/1
fepmultiplayerstart.h=1/1
fepoptions.h=1/1
fepvirtualkeyboard.h=1/1
fepwingmen.h=1/1
float.h=1/1
fmv.h=2/2
fog.h=2/2
font.h=1/1
frontenddata.h=1/1
frontendpage.h=4/4
frontendtext.h=2/2
frontendvideo.h=1/1
gamedisc.h=1/1
gameinterface.h=5/5
gcgamut.h=3/3
generalvolume.h=1/1
heightfield.h=1/1
helptext.h=1/1
hlcollisiondetector.h=1/1
hud.h=1/1
hudpositions.h=1/1
ibuffer.h=1/1
imagehlp.h=1/1
imposter.h=5/5
kempycube.h=4/4
keyeventtype.h=1/1
landscape.h=6/6
levelbriefinglog.h=1/1
lights.h=5/5
line.h=5/5
map.h=13/13
maptex.h=3/3
mapwho.h=2/2
mapwhoentry.h=2/2
math.h=1/1
mathtest.h=1/1
mcbattleengine.h=1/1
mcbuggy.h=1/1
mesh.h=6/6
meshpart.h=1/1
meshpose.h=1/1
meshrenderer.h=7/7
messagebox.h=3/2
messagelog.h=1/1
missionobjective.h=2/2
missionscript/iscript.h=1/1
missionscript/scripteventnb.h=1/1
missionscript/vm.h=1/1
mmsystem.h=1/1
modelviewer.h=1/1
monitor.h=3/3
motioncontroller.h=1/1
ms/d3dres.h=1/1
ms/d3dutil.h=1/1
ms/dxutil.h=1/1
navigationmap.h=1/1
oids.h=3/3
optrset.h=1/1
particlemanager.h=7/7
particleset.h=4/4
particletexture.h=1/1
pausemenu.h=2/2
pchud.h=1/1
pcmusic.h=1/1
pcpatchmanager.h=1/1
pcrenderdata.h=1/1
pcsimd.h=1/1
pcstorage.h=1/1
process.h=1/1
profile.h=11/11
ps2clutdata.h=1/1
ps2controller.h=1/1
ps2display.h=2/2
ps2dmalist.h=1/1
ps2engine.h=1/1
ps2frontend.h=1/1
ps2game.h=1/1
ps2membuffer.h=1/1
ps2memorycard.h=1/1
ps2memorymanager.h=1/1
ps2mipmapdata.h=1/1
ps2music.h=1/1
ps2pinmapper.h=1/1
ps2platform.h=1/1
ps2profiler.h=1/1
ps2scene.h=1/1
ps2soundmanager.h=1/1
ps2storage.h=1/1
psxmembuffer.h=1/1
ptrset.h=2/2
radarwarningreceiver.h=1/1
rain.h=2/2
reconnectinterface.h=3/3
renderablething.h=1/1
renderinfo.h=14/14
renderqueue.h=3/3
rendertarget.h=2/2
renderthing.h=2/2
resource.h=3/3
rtmesh.h=3/3
samplelist.h=1/1
screenfx.h=3/3
shadows.h=4/3
sky.h=1/1
smoke.h=2/2
soundmaterial.h=1/1
spawnpoint.h=1/1
sphere.h=1/1
spriterenderer.h=11/11
squad.h=1/1
start.h=1/1
state.h=8/7
staticshadows.h=2/2
stdafx.h=8/8
surf.h=1/1
system.h=2/2
text.h=10/10
texture.h=5/5
tgaloader.h=1/1
thingtype.h=3/3
transitionhelpers.h=1/1
tree.h=2/2
trees.h=3/3
umtexture.h=2/2
unit.h=2/2
unitai.h=1/1
vbuftexture.h=2/2
vertexshader.h=3/3
vfw.h=1/1
visibilitytester.h=2/2
waitingthread.h=1/1
wall.h=1/1
water.h=4/4
waterreflection.h=2/2
wavread.h=1/1
weapon.h=5/5
world.h=12/12
worldphysicsmanager.h=5/5
xbox.h=1/1
xboxcontroller.h=1/1
xboxdx.h=2/2
xboxmusic.h=1/1
xboxplatform.h=1/1
xboxsoundmanager.h=1/1
xboxstorage.h=1/1
xgraphics.h=1/1
```

The two further targets that fail by their written relative path but are
available by root basename are exactly:

```text
d3dapp.cpp:27  ../cliparams.h  → CLIParams.h
d3dapp.cpp:28  ../dx.h         → DX.H
```

Thus the literal result is 204 missing targets / 537 occurrences, while
basename availability is 202 / 535. Neither number means “202 missing
implementation files.”

## Appendix D: shipped source-path lower bound

### 28 retail-path basenames present in the drop

```text
Array.h
BattleEngine.cpp
BattleEngineConfigurations.cpp
BattleEngineDataManager.cpp
BattleEngineDataManager.h
Camera.cpp
chunker.cpp
Controller.cpp
DXMemBuffer.cpp
engine.cpp
eventmanager.cpp
FEPGoodies.cpp
FEPLoadGame.cpp
FEPSaveGame.cpp
FrontEnd.cpp
game.cpp
InitThing.cpp
ltshell.cpp
MemoryManager.cpp
Music.cpp
PCPlatform.cpp
pcsoundmanager.cpp
Platform.cpp
Player.cpp
ResourceAccumulator.cpp
SoundManager.cpp
SPtrSet.cpp
thing.cpp
```

### 134 retail-path basenames absent from the drop

```text
AirUnit.cpp
AsmInstruction.cpp
asminstruction.h
Atmospherics.cpp
Boat.cpp
Bomber.cpp
BSpline.cpp
Building.cpp
bytesprite.cpp
Cannon.cpp
Carrier.cpp
Carver.cpp
CollisionSeekingRound.cpp
collisionseekingthing.cpp
Component.cpp
console.cpp
CPhysicsScript.cpp
CPhysicsScriptStatements.cpp
CPhysicsScriptStatements.h
Cutscene.cpp
damage.cpp
DataType.cpp
DataType.h
DestructableSegmentsController.cpp
DiveBomber.cpp
Dropship.cpp
DXBattleLine.cpp
DXClouds.cpp
DXCompass.cpp
DXFMV.CPP
DXFont.cpp
DXFrontEndVideo.cpp
DXImposter.cpp
DXKempyCube.cpp
DXLandscape.cpp
DXLandscape.h
DXMeshVB.cpp
DXPalletizer.cpp
DXParticleTexture.cpp
DXPatchManager.cpp
DXShadows.cpp
DXSnow.cpp
DXSurf.cpp
DXTexture.cpp
DXTrees.cpp
EventFunction.cpp
FastVB.cpp
FEPBEConfig.cpp
FEPDebriefing.cpp
FEPDevelopment.cpp
FEPDirectory.cpp
FEPMain.cpp
FEPMultiplayerStart.cpp
FEPOptions.cpp
FEPWingmen.cpp
flexarray.cpp
gcgamut.cpp
GillM.cpp
GillMHead.cpp
GroundAttackAircraft.cpp
GroundUnit.cpp
GroundVehicle.cpp
HeightField.cpp
HiveBoss.cpp
Hud.cpp
ibuffer.cpp
imageloader.cpp
imposter.cpp
Infantry.cpp
InfluenceMap.cpp
InfluenceMap.h
IScript.cpp
landscapeib.cpp
LandscapeTexture.cpp
maptex.cpp
mapwho.cpp
MCBuggy.cpp
MCMech.cpp
MCTentacle.cpp
Mech.cpp
MenuItem.cpp
mesh.cpp
MeshCollisionVolume.cpp
MeshPart.cpp
meshpose.h
MeshRenderer.cpp
Mine.cpp
Missile.cpp
mixermap.cpp
Monitor.h
oids.cpp
ParticleDescriptor.cpp
ParticleManager.cpp
ParticleSet.cpp
PauseMenu.cpp
PCRTID.cpp
Plane.cpp
PolyBucket.cpp
RadarWarningReceiver.cpp
Round.cpp
RTCutscene.cpp
rtmesh.cpp
ScriptEventNB.cpp
ScriptObjectCode.cpp
Sentinel.cpp
SpawnerThng.cpp
SphereTrigger.cpp
SquadNormal.cpp
SquadRelaxed.cpp
StaticShadows.cpp
Submarine.cpp
Symtab.cpp
Tentacle.cpp
text.cpp
texture.cpp
tgaloader.cpp
ThunderHead.cpp
TokenArchive.cpp
tree.cpp
triangulate.cpp
Unit.cpp
vbuffer.cpp
vbuftexture.cpp
VertexShader.cpp
Warspite.cpp
WarspiteDome.cpp
wavread.cpp
WaypointManager.cpp
world.cpp
WorldMeshList.cpp
WorldMeshList.h
WorldPhysicsManager.cpp
WorldPhysicsManager.h
XBOXAsyncCache.cpp
```

### 78 drop basenames without a retail path literal

```text
activereader.cpp
activereader.h
actor.cpp
actor.h
Array.cpp
BattleEngine.h
BattleEngineConfigurations.h
BattleEngineJetPart.cpp
BattleEngineJetPart.h
BattleEngineWalkerPart.cpp
BattleEngineWalkerPart.h
Camera.h
Career.cpp
Career.h
chunker.h
CLIParams.cpp
CLIParams.h
Controller.h
d3dapp.cpp
d3dapp.h
DX.H
DXEngine.cpp
DXEngine.h
DXFrontend.cpp
DXFrontend.h
DXGame.cpp
DXGame.h
DXMemBuffer.h
DXMemoryManager.cpp
DXMemoryManager.h
EditorD3DApp.cpp
EditorD3DApp.h
EndLevelData.cpp
EndLevelData.h
engine.h
event.cpp
event.h
eventmanager.h
FEPGoodies.h
FEPLoadGame.h
FEPSaveGame.h
Frontend.h
game.h
InitThing.h
ltshell.h
membuffer.h
MemoryCard.cpp
MemoryCard.h
MemoryManager.h
Music.h
PCController.cpp
PCController.h
PCEngine.cpp
PCEngine.h
PCFEPLoadGame.cpp
PCFEPLoadGame.h
PCFEPSaveGame.cpp
PCFEPSaveGame.h
PCFrontend.cpp
PCFrontend.h
PCGame.cpp
PCGame.h
PCMemoryCard.cpp
PCMemoryCard.h
PCPlatform.h
pcsoundmanager.h
Platform.h
Player.h
ResourceAccumulator.h
scheduledevent.cpp
scheduledevent.h
SoundManager.h
SPtrSet.h
storage.cpp
storage.h
thing.h
XBoxMemoryCard.cpp
XBoxMemoryCard.h
```

The final list is non-evidence of absence: a file without an emitted assert
path is invisible to this instrument. All three lists are case-insensitive
basename projections of the 163 distinct full paths / 162 basenames, not a
claim that source directories were flat in the shipped tree.

## Appendix E: reproduction and evidence map

### Corpus reproduction contract

The census is reproducible from the pin as follows:

1. Verify identity and cleanliness with
   `git -C references/Onslaught rev-parse HEAD`,
   `git -C references/Onslaught status --short`, and
   `git -C references/Onslaught show -s --format=fuller HEAD`.
2. Enumerate tracked `.cpp`/`.h` entries case-insensitively. Read raw bytes.
   Count physical lines as LF count plus one only for a nonempty file without
   terminal LF. Enumerate `LICENSE`/`README.md` separately.
3. Verify high bytes, BOM, NUL, and that every LF is immediately preceded by
   CR. The audited source has no high bytes/BOM/NUL and every newline is CRLF.
4. Extract includes with
   `^\s*#\s*include\s*(["<])([^">]+)[">]`. Normalize case, slash direction,
   and repeated slashes. Report relative-path resolution and flat-basename
   availability as separate predicates.
5. Parse all 106 syntax trees with Node `tree-sitter@0.21.1` and
   `tree-sitter-cpp@0.22.3`, streaming large files in 16,384-byte callback
   chunks. Count class/struct/enum specifiers only when they have bodies;
   count declarations and definitions separately.
6. Apply the published body correction ledger: 1,817 raw
   `function_definition` nodes, minus ten false positives, plus 46 recovered
   real bodies, plus two shared physical bodies = 1,855. Count four conditional
   heads for those two shared blocks to reach 1,857.
7. Cross-check line-anchored guards, macros, externs, globals, and target
   directives; group duplicates case-insensitively; hand-read every
   load-bearing parser-error-adjacent site and finite-table mismatch.

The unpreprocessed trees contain 276 `ERROR` nodes and eight missing nodes
across 51 files because original macro/type owners are absent. All 52
translation units fail first-principles standalone preprocessing at the absent
`common.h`. The parser census includes mutually exclusive, dead, debug,
editor, and template text; it is not a template-instantiation, linker-symbol,
or retail-function count.

### Durable tracked evidence

| Topic | Primary tracked owner |
| --- | --- |
| RE front door and evidence policy | [`reverse-engineering/RE-INDEX.md`](../RE-INDEX.md) |
| Source pin/buildability audit | [`reference-submodule-audit-2026-07-12.md`](reference-submodule-audit-2026-07-12.md) |
| Source corpus itself | [`references/Onslaught`](../../references/Onslaught) |
| Ghidra/executable master | [`../ghidra-functions.md`](../ghidra-functions.md) |
| Installed-data master | [`../installed-corpus-census.md`](../installed-corpus-census.md) |
| Rebuild evidence/authority boundary | [`rebuild/PROVENANCE.md`](../../rebuild/PROVENANCE.md) |
| Rebuild architecture and commands | [`rebuild/README.md`](../../rebuild/README.md) |
| Battle Engine movement crosswalk | [`battleengine-movement-static-crosswalk-2026-07-12.md`](../binary-analysis/battleengine-movement-static-crosswalk-2026-07-12.md) |
| Retail source paths/RTTI | [`rtti-and-source-path-evidence-2026-07-25.md`](../binary-analysis/rtti-and-source-path-evidence-2026-07-25.md) |
| Controller static crosswalk | [`controller-system.md`](frontend/controller-system.md) and current Ghidra notes |
| Career/save structures | [`save-format.md`](../save-file/save-format.md), [`struct-layouts.md`](../save-file/struct-layouts.md) |
| Source subsystem indexes | [`source-code/_index.md`](_index.md) |

### Machine-local measured evidence

The following ignored/local evidence informed current static/runtime verdicts
but is not durable repository truth by itself:

| Topic | Local evidence |
| --- | --- |
| Unpatched baseline executable | `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup` |
| Corrected source-tree basename extraction | fresh read-only scan of that baseline image in this pass |
| Audio static law | `local-lab/agent-notes-2026-07-27/recon-sound.md` |
| Current parity/delta adjudications | `local-lab/PARITY-WORKLIST-2026-07-27.md` |
| Terrain light runtime state | `local-lab/TERRAIN-LIGHT-STATE-RUNTIME-2026-07-26.md` |
| Source divergence history/adversarial corrections | `local-lab/SOURCE-DIVERGENCE-AUDIT-2026-07-27.md` and gauntlet assessments |

When a local finding becomes load-bearing implementation truth, promote the
smallest reviewed capture, byte table, or focused test—not the raw lab
directory.

### Closing state

This file closes the first complete Stuart-source research pass at four levels:

- every source/support file is physically accounted for;
- definitions, declarations, types, enums, globals, macros, includes, finite
  arrays, CLI switches, and source-path gaps have explicit denominators;
- each major supplied subsystem has an architectural/function atlas;
- source-to-retail and source-to-rebuild claims are separated by evidence
  grade and converted into a discrete next-work queue.

It does **not** close reconstruction of the game. The source pin is partial,
multi-target, unbuildable in isolation, and not the exact Steam tree. Its value
is that it turns anonymous behavior into named hypotheses and often into exact
algorithms. The Steam specimen and controlled runtime decide which hypotheses
survived release; `rebuild/` then implements that adjudicated result.
