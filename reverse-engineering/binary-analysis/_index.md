# Binary Analysis

Status: living index for `reverse-engineering/binary-analysis/`
Last updated: 2026-10-15 (Ghidra-era authority records moved to the private RE archive; the decompilation is the naming authority)
Summary: front door to the static and byte-level findings about the Steam `BEA.exe`: specimen baseline, dated
analyses, per-system contracts and per-function notes. Makes no claim of its own — every claim below belongs to the
document it links.

The byte-matching decompilation (private `bea-decomp`) is the naming and behaviour authority. The Ghidra-era
records that used to head this index (the Ghidra workflow reference, full re-audit, correction plans, full-pass
wave findings, coverage baseline, C1 closure and the promotion and boundary records) are in the private
`dlprentice/onslaught-re-archive`. Function counts, generations and database versions quoted in the documents below
are dated snapshots.

## Dated analyses and provenance

- [Retail Specimen Baseline](retail-specimen-baseline.md)
- [Retail capture provenance — what the reference screenshots actually show](retail-capture-provenance-2026-07-25.md)
- [The 34 newly admitted MissionScript functions now have bounded static contracts](mission-script-registry-new-function-static-contracts-2026-08-13.md)
- [MissionScript 34-handler semantic refinement](mission-script-registry-new-function-semantic-refinement-2026-08-13.md)
- [D3DX9 section-contribution provenance](d3dx9-section-contribution-provenance-2026-08-13.md)
- [Collision-component implementation-identity correction](collision-component-identity-correction-2026-08-12.md)
- [PC demo versus PC retail](../DEMO_VS_RETAIL.md)
- [pc-demo-retail-virtual-target-map-2026-08-11.tsv](pc-demo-retail-virtual-target-map-2026-08-11.tsv)
- [`CUnit` primary virtual interface: demo/retail semantic crosswalk](cunit-primary-vtable-semantics-2026-08-11.md)
- [cunit-primary-vtable-semantics-2026-08-11.tsv](cunit-primary-vtable-semantics-2026-08-11.tsv)
- [`CBattleEngine` virtual-interface semantic crosswalk](cbattleengine-vtable-semantics-2026-08-11.md)
- [cbattleengine-vtable-semantics-2026-08-11.tsv](cbattleengine-vtable-semantics-2026-08-11.tsv)
- [`CThing` base-interface semantic crosswalk](cthing-vtable-semantics-2026-08-11.md)
- [cthing-vtable-semantics-2026-08-11.tsv](cthing-vtable-semantics-2026-08-11.tsv)
- [`CComplexThing` virtual-interface semantic crosswalk](ccomplexthing-vtable-semantics-2026-08-11.md)
- [ccomplexthing-vtable-semantics-2026-08-11.tsv](ccomplexthing-vtable-semantics-2026-08-11.tsv)
- [`CThing` / `CComplexThing` retail object layout](cthing-ccomplexthing-layout-2026-08-13.md)
- [`CActor` virtual-interface semantic crosswalk](cactor-vtable-semantics-2026-08-11.md)
- [cactor-vtable-semantics-2026-08-11.tsv](cactor-vtable-semantics-2026-08-11.tsv)
- [`CPCController` platform-interface semantic crosswalk](cpccontroller-vtable-semantics-2026-08-11.md)
- [cpccontroller-vtable-semantics-2026-08-11.tsv](cpccontroller-vtable-semantics-2026-08-11.tsv)
- [`CController` shared mapping and dispatch semantic recovery](controller-shared-semantics-2026-08-11.md)
- [controller-shared-semantics-2026-08-11.tsv](controller-shared-semantics-2026-08-11.tsv)
- [Controller-to-player/game event spine](controller-player-game-event-spine-2026-08-11.md)
- [controller-player-game-event-spine-2026-08-11.tsv](controller-player-game-event-spine-2026-08-11.tsv)
- [`CPCMusic` platform-interface semantic crosswalk](cpcmusic-vtable-semantics-2026-08-11.md)
- [cpcmusic-vtable-semantics-2026-08-11.tsv](cpcmusic-vtable-semantics-2026-08-11.tsv)
- [`CMusic` shared music-policy semantic recovery](cmusic-shared-semantics-2026-08-11.md)
- [cmusic-shared-semantics-2026-08-11.tsv](cmusic-shared-semantics-2026-08-11.tsv)
- [`CSoundManager` shared audio-policy semantic recovery](csoundmanager-shared-semantics-2026-08-11.md)
- [csoundmanager-shared-semantics-2026-08-11.tsv](csoundmanager-shared-semantics-2026-08-11.tsv)
- [`CPCSoundManager` DirectSound backend semantic recovery](cpcsoundmanager-backend-semantics-2026-08-11.md)
- [cpcsoundmanager-backend-semantics-2026-08-11.tsv](cpcsoundmanager-backend-semantics-2026-08-11.tsv)
- [PC memory-buffer and allocation-service semantic recovery](pc-memory-io-semantics-2026-08-11.md)
- [pc-memory-io-semantics-2026-08-11.tsv](pc-memory-io-semantics-2026-08-11.tsv)
- [Frontend save/load and PC persistence semantics](frontend-save-load-semantics-2026-08-11.md)
- [frontend-save-load-semantics-2026-08-11.tsv](frontend-save-load-semantics-2026-08-11.tsv)
- [`CPCMemoryCard` released PC save-backend semantics](cpcmemorycard-pc-save-backend-semantics-2026-08-11.md)
- [cpcmemorycard-pc-save-backend-semantics-2026-08-11.tsv](cpcmemorycard-pc-save-backend-semantics-2026-08-11.tsv)
- [`CCareer` released PC save-format semantics](career-save-format-semantics-2026-08-11.md)
- [career-save-format-semantics-2026-08-11.tsv](career-save-format-semantics-2026-08-11.tsv)
- [`CTokenArchive` particle grammar and reference semantics](tokenarchive-semantics-2026-08-11.md)
- [tokenarchive-semantics-2026-08-11.tsv](tokenarchive-semantics-2026-08-11.tsv)
- [`PCLTShell` virtual-interface semantic crosswalk](pcltshell-vtable-semantics-2026-08-11.md)
- [pcltshell-vtable-semantics-2026-08-11.tsv](pcltshell-vtable-semantics-2026-08-11.tsv)
- [`CGame` level-lifecycle semantic recovery](cgame-level-lifecycle-semantics-2026-08-11.md)
- [cgame-level-lifecycle-semantics-2026-08-11.tsv](cgame-level-lifecycle-semantics-2026-08-11.tsv)
- [Event-manager scheduler semantic recovery](event-manager-scheduler-semantics-2026-08-11.md)
- [event-manager-scheduler-semantics-2026-08-11.tsv](event-manager-scheduler-semantics-2026-08-11.tsv)
- [CTentacle factory-name chain — evidence and rehearsal](tentacle-factory-name-chain-2026-08-17.md)
- [Reverse-Engineering Index](../RE-INDEX.md)
- [Runtime-witness corpus merge — DeepSeek Extended findings relocated and queued](runtime-witness-corpus-merge-2026-08-17.md)

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
- [`CRound` event-2000 two-position runtime addendum](cround-event2000-two-position-runtime-addendum-2026-08-13.md)
  — bounds two exact receiver-matched `CALL_ENTRY` paths, explicitly retaining
  the 167/10/2 selection limit and leaving allocator return/effects open
- [`CWorldPhysicsManager::CreateExplosion` caller family](cexplosion-factory-callers-2026-08-10.md)
- [Local multiplayer evidence boundary](local-multiplayer-static-runtime-contract.md)

Focused patch notes remain beside the binary evidence they depend on. Applied
wave scripts and readiness reports are retained in Git history, not as active
tools or navigation.

## Function notes

[`functions/`](functions/_index.md) contains retained per-function evidence.
These notes are not decompiler source and do not authorize copying proprietary
code into the rebuild.

For controlled debugger work, use the CDB runbook (private RE archive: `reverse-engineering/binary-analysis/windbg-cdb-runbook.md`).
Full databases, backups, raw logs, and captures stay outside Git.
