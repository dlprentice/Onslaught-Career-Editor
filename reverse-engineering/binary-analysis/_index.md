# Binary Analysis

Status: living index for `reverse-engineering/binary-analysis/`
Last updated: 2026-08-11
Summary: front door to the static and byte-level evidence for the Steam
`BEA.exe`. Names the current naming authority, the specimen baseline, and the
per-system contracts. Makes no claim of its own — every claim below belongs to
the document it links.

## Current authority and provenance

- [Executable/Ghidra narrative synthesis](../ghidra-functions.md) — dated
  reviewed synthesis and open queue; the TSV and Ghidra stores below remain the
  mechanical and database owners
- [Ghidra workflow and evidence boundary](GHIDRA-REFERENCE.md)
- [Full re-audit closeout](ghidra-full-reaudit-closeout-2026-07-13.md) — the
  record of the 2026-07-13 audit, **not the current name state**
- [Reviewed correction plan](ghidra-reviewed-correction-plan-2026-07-13.json)
- [Fullpass discovery findings](ghidra-fullpass-findings/) (waves W001–W018)
- [Retail specimen baseline](retail-specimen-baseline.md)
- [Retail capture provenance](retail-capture-provenance-2026-07-25.md) — which
  binary the reference captures came from, and why it matters
- [RE coverage baseline](re-coverage-baseline-2026-07-25.md) — the 6,411 → 6,969
  inventory growth and the byte-level verifier
- [Full 8,136-function static-C1 closure](function-c1-closure-2026-08-11.md) —
  the reviewed per-row crosswalk from 53 sealed static receipts, the ten
  post-Gen19 Mission natives, and the pre-existing bounded C1/C2 set; static
  envelope closure only, not runtime or source parity
- [PC demo/retail virtual-target comparison](../DEMO_VS_RETAIL.md) and its
  [2,127-row address map](pc-demo-retail-virtual-target-map-2026-08-11.tsv) —
  identical strict RTTI/vtable structure pairs every virtual target; 2,123
  instruction streams have zero normalized differences and all four original
  frontend/FMV divergences now have independently bounded semantic explanations
- [PC demo/retail whole-function map](pc-demo-retail-function-map-2026-08-11.tsv)
  — 8,086 independently mapped demo entries; 8,021 normalized-identical body
  streams covering 1,702,495 retail bytes and 512,925 instructions, with 65
  changed/unbounded bodies and 50 address-unmapped functions kept explicit
- [PC demo/retail FMV and startup lineage](pc-demo-retail-fmv-startup-lineage-2026-08-11.md)
  and its [5-function table](pc-demo-retail-fmv-startup-lineage-2026-08-11.tsv)
  — independently bounds five changed bodies and recovers the demo-only
  per-playback skip field, American-English fallback, initialized playable-demo
  state and publisher FMV plus retail's demo-loading adaptation
- [PC demo/retail frontend lineage](pc-demo-retail-frontend-lineage-2026-08-11.md)
  and its [3-function table](pc-demo-retail-frontend-lineage-2026-08-11.tsv) —
  recovers the demo-only publisher-surface draw and dedicated demo-main
  debrief route, retail's playable-demo quit/result path, and the shared
  86-texture loader's one edition-specific substitution
- [PC demo/retail shell and FMV lineage](pc-demo-retail-shell-fmv-lineage-2026-08-11.md)
  and its [3-function table](pc-demo-retail-shell-fmv-lineage-2026-08-11.tsv) —
  bounds demo's separate 500-byte startup-movie helper, publisher insertion on
  all startup/attract paths, and language-selected promotional shutdown request
- [`CUnit` primary virtual-interface semantic crosswalk](cunit-primary-vtable-semantics-2026-08-11.md)
  and its [46-slot table](cunit-primary-vtable-semantics-2026-08-11.tsv) — uses
  the demo twin, pinned source overrides, and typed callsites to replace field
  labels with 21 source/callsite meanings while leaving absent historical names
  explicitly open
- [`CBattleEngine` virtual-interface semantic crosswalk](cbattleengine-vtable-semantics-2026-08-11.md)
  and its [37-target table](cbattleengine-vtable-semantics-2026-08-11.tsv) —
  resolves every uniquely owned Battle Engine target against the pinned source
  and independently linked demo, including render-interface, movement, weapon,
  damage, collision, and terminal-event identities
- [`CThing` base-interface semantic crosswalk](cthing-vtable-semantics-2026-08-11.md)
  and its [31-target table](cthing-vtable-semantics-2026-08-11.tsv) — recovers
  the primary/audible and secondary/render ABI spine inherited by actors,
  units, squads, projectiles, triggers, and level-script objects
- [`CComplexThing` virtual-interface semantic crosswalk](ccomplexthing-vtable-semantics-2026-08-11.md)
  and its [22-target table](ccomplexthing-vtable-semantics-2026-08-11.tsv) —
  adds the source-backed orientation, animation, name, motion-controller, and
  mission-script layer used by higher gameplay classes
- [`CActor` virtual-interface semantic crosswalk](cactor-vtable-semantics-2026-08-11.md)
  and its [18-target table](cactor-vtable-semantics-2026-08-11.tsv) — recovers
  the movement scheduler, pose integration/interpolation, contact timestamps,
  teleport, and velocity-stop layer inherited by moving gameplay objects
- [`CPCController` platform-interface semantic crosswalk](cpccontroller-vtable-semantics-2026-08-11.md)
  and its [15-target table](cpccontroller-vtable-semantics-2026-08-11.tsv) —
  recovers the PC joystick, keyboard, POV, and controller-recording adapter at
  the shared/platform-specific engine boundary described by Lost Toys
- [`CController` shared mapping/dispatch semantic crosswalk](controller-shared-semantics-2026-08-11.md)
  and its [17-function table](controller-shared-semantics-2026-08-11.tsv) —
  recovers the released 47-row two-bank mapper, mouse and wheel extensions,
  repeat/deadzone laws, monitored control stack, inactivity policy, and exact
  divergences from the retained controller source
- [Controller-to-player/game event spine](controller-player-game-event-spine-2026-08-11.md)
  and its [10-target table](controller-player-game-event-spine-2026-08-11.tsv)
  — follows normalized input through shared mapping into player actions and
  game/debug/event dispatch, including the released death-audio fade event
- [`CPCMusic` platform-interface semantic crosswalk](cpcmusic-vtable-semantics-2026-08-11.md)
  and its [8-target table](cpcmusic-vtable-semantics-2026-08-11.tsv) — recovers
  the shared playlist/PC async-stream boundary, directory enumeration, exact
  volume conversion, and corrects `0x004BB450` to `DeviceChangeTrack`
- [`CMusic` shared-policy semantic crosswalk](cmusic-shared-semantics-2026-08-11.md)
  and its [11-function table](cmusic-shared-semantics-2026-08-11.tsv) — recovers
  playlist ordering, selection, fades, finished-track policy, and released
  source divergences: OGG-only discovery, the compiled random-mode assignment,
  linear `volume * 127`, and the corrected `DeviceChangeTrack` identity
- [`CSoundManager` shared audio-policy semantic crosswalk](csoundmanager-shared-semantics-2026-08-11.md)
  and its [34-function table](csoundmanager-shared-semantics-2026-08-11.tsv) —
  recovers the production 256-event pool, sample/effect selection, spatial and
  volume policy, 75% channel arbitration, fades, pitch, pause/stop, language
  XAP reload, and device-loss path against source, demo, and the GDC deck
- [`CPCSoundManager` DirectSound-backend semantic crosswalk](cpcsoundmanager-backend-semantics-2026-08-11.md)
  and its [20-function table](cpcsoundmanager-backend-semantics-2026-08-11.tsv)
  — recovers device enumeration, 64 channel slots, IMA ADPCM decode, three
  output-quality conversions, DirectSound buffer lifecycle, playback, 3D
  listener updates, and the exact shared/platform boundary
- [PC memory-buffer and typed-allocation semantic crosswalk](pc-memory-io-semantics-2026-08-11.md)
  and its [25-function table](pc-memory-io-semantics-2026-08-11.tsv) — recovers
  released 1 MiB-aligned buffering, raw/zlib block I/O and CRC sidecars, 129
  typed allocation routes, four PC heaps, allocation headers, OOM policy, and
  retained-source divergences
- [Frontend save/load and PC persistence semantic crosswalk](frontend-save-load-semantics-2026-08-11.md)
  and its [15-function table](frontend-save-load-semantics-2026-08-11.tsv) —
  recovers the PC file-backed load/save transaction, overwrite and storage
  recovery policy, case-insensitive save identity, and the six-entry released
  XOR-obfuscated cheat-name gate against retained source and the PC demo
- [`CPCMemoryCard` released PC save-backend semantic crosswalk](cpcmemorycard-pc-save-backend-semantics-2026-08-11.md)
  and its [11-function table](cpcmemorycard-pc-save-backend-semantics-2026-08-11.tsv)
  — corrects the owning class and method identities, recovers the one-card
  filename-backed slot model, enumeration/create/read/write/delete laws, and
  two exact CRT stream-lifetime defects shared with the PC demo
- [`CCareer` released PC save-format semantic crosswalk](career-save-format-semantics-2026-08-11.md)
  and its [8-function table](career-save-format-semantics-2026-08-11.tsv) —
  recovers the dynamic size law, the two serializer variants, career versus
  default-options load modes, the 0x56-byte options tail, and the packed D3D
  profile key against retained source and normalized-identical demo bodies
- [`CTokenArchive` particle grammar and reference semantic crosswalk](tokenarchive-semantics-2026-08-11.md)
  and its [12-function table](tokenarchive-semantics-2026-08-11.tsv) — recovers
  the 124-token/six-shape parser, fixed deferred-reference workspace,
  case-insensitive particle-name resolver, thirteen descriptor loaders, one
  shipped-corpus-masked asymmetry, and five compiled formatter-only stubs
- [`PCLTShell` virtual-interface semantic crosswalk](pcltshell-vtable-semantics-2026-08-11.md)
  and its [8-target table](pcltshell-vtable-semantics-2026-08-11.tsv) — resolves
  the released Direct3D device lifecycle, pause, capability filter, and Windows
  message bridge against the retained earlier shell source and PC demo twin
- [`CGame` level/restart lifecycle semantic crosswalk](cgame-level-lifecycle-semantics-2026-08-11.md)
  and its [6-function table](cgame-level-lifecycle-semantics-2026-08-11.tsv) —
  recovers the one-off and per-attempt initialization, run, restart, teardown,
  and exact quit-code propagation boundaries from retail calls, retained source,
  and independently linked demo bodies
- [Event-manager scheduler semantic crosswalk](event-manager-scheduler-semantics-2026-08-11.md)
  and its [14-function table](event-manager-scheduler-semantics-2026-08-11.tsv)
  — recovers the fixed 20 Hz clock, 200-by-3 ring, sorted overflow queue,
  20,000-record pool, strict due-time edge, callback reuse, and cleanup order;
  every released body has a normalized-identical demo twin
- **Current name state — the three grading ledgers, newest last:**
  - [2026-07-25](name-grading-ledger-2026-07-25.md) — first grading; the 332-row
    RTTI re-prefix wave. Two of its figures are superseded; see its banner.
  - [2026-07-26](name-grading-ledger-2026-07-26.md) — grader corrections plus 13
    renames and 1 destructor demotion applied
  - [2026-07-27](name-grading-ledger-2026-07-27-demotion2.md) — second
    destructor demotion, `0x005386d0`

> **Corrected 2026-07-28 — this section previously said only:** "The closeout and
> per-address plan supersede older saved names where they conflict." That is
> still true and is kept below, but it left the 2026-07-13 closeout reading as
> the current naming authority when it is not. **The closeout has itself been
> overtaken.** Since it, and established in tracked evidence: the function
> inventory grew **6,411 → 6,969**
> ([re-coverage-baseline-2026-07-25.md](re-coverage-baseline-2026-07-25.md)),
> **332** RTTI re-prefixes were applied to the live database
> ([07-25 ledger](name-grading-ledger-2026-07-25.md)), then **13** renames and
> **1** destructor demotion ([07-26](name-grading-ledger-2026-07-26.md)), then a
> **second** destructor demotion, `0x005386d0`
> ([07-27](name-grading-ledger-2026-07-27-demotion2.md)). The ledgers, not the
> closeout, are the current record of which names are demoted.
>
> *Deliberately not restated as a single total here.* The tracked
> [`ghidra-function-name-table-2026-07-27.tsv`](ghidra-function-name-table-2026-07-27.tsv)
> is the dated current address-to-name export and the mechanical checker's
> authority. Read that table rather than copying its moving inventory count into
> another document.

The closeout and per-address plan supersede older saved names where they
conflict. Static accounting does not prove runtime behavior, exact layouts,
patch behavior, or rebuild parity. Fullpass findings are discovery notes, not a
claim that every function is semantically correct.

### 2026-07 fullpass correction expedition

| Layer | Location | Role |
| --- | --- | --- |
| Findings | [`ghidra-fullpass-findings/`](ghidra-fullpass-findings/) | Discovery (W001–W018) |
| Lab | `local-lab/ghidra-fullpass-2026-07-23/` (not git) | Ops: queues, dual QC, apply logs; closeout 2026-07-25 |
| Live DB | Maintainer Ghidra Projects (machine-local) | Applied corrections when authorized |
| Tracked snapshot | [`../ghidra/`](../ghidra/README.md) (2026-08-09) | Distributable snapshot; exact to the verified live state at promotion time |

A wave path such as `ghidra-fullpass-findings/W001/primary/A01.md` is not proof
that the live database or the tracked `ghidra/` snapshot was mutated. Mutation
evidence lives under the ignored lab’s apply logs when present.

## Product and format contracts

- [Executable analysis](executable-analysis.md)
- [Windowed mode](windowed-mode-analysis.md)
- [Widescreen patch](widescreen-patch-analysis.md)
- [Career progression bridge](career-progression-static-bridge-contract.md)
- [Mission script contract](missionscript-iscript-static-contract.md)
- [Physics script contract](physics-script-static-contract.md)
- [Texture resource decoding](texture-resource-decode-static-contract.md)
- [Terrain shade plane origin and axis order](terrain-shade-plane-origin-2026-07-26.md)
- [Terrain shade bilinear interpolation decode](terrain-shade-bilinear-decode-2026-07-26.md)
- [Terrain draw texture-stage flags](terrain-draw-stage-flags-2026-07-26.md)
- [Terrain per-node colour light absent from the PC path](terrain-per-node-colour-absent-2026-07-26.md)
- [Retail's implied macro cache inverted from rendered pixels](terrain-implied-macro-inversion-2026-07-26.md)
- [Sun colour route to the terrain draw — all ten references, negative](terrain-sun-colour-route-2026-07-26.md)
- [Terrain material record and the `LANDSCAPE_LIGHTING` gate](terrain-ambient-light-material-2026-07-26.md)
- [Terrain ambient-light term implemented and measured](terrain-ambient-light-applied-2026-07-26.md)
- [Cockpit lighting law — located, decoded, already implemented](cockpit-lighting-law-2026-07-26.md)
- [The default render-state block `0x004EB1E0` — re-derived from bytes](d3d-default-render-state-block-2026-07-27.md)
- [Half-pixel pixel-centre offset corrected in the projection](pixel-centre-projection-offset-applied-2026-07-26.md)
- [CMSH `CPOS`/`CORI` identity](cmsh-cpos-cori-identity-2026-07-25.md)
- [`CRound::Hit`, `CExplosion::Hit`, and their separate damage paths](cround-hit-damage-path-2026-08-10.md)
- [`CWorldPhysicsManager::CreateExplosion` caller family](cexplosion-factory-callers-2026-08-10.md)
- [Local multiplayer evidence boundary](local-multiplayer-static-runtime-contract.md)

Focused patch notes remain beside the binary evidence they depend on. Applied
wave scripts and readiness reports are retained in Git history, not as active
tools or navigation.

## Function notes

[`functions/`](functions/_index.md) contains retained per-function evidence.
These notes are not decompiler source and do not authorize copying proprietary
code into the rebuild.

For controlled debugger work, use the [CDB runbook](windbg-cdb-runbook.md).
Full databases, backups, raw logs, and captures stay outside Git.
