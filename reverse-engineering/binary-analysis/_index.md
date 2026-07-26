# Binary Analysis

## Current authority and provenance

- [Ghidra workflow and evidence boundary](GHIDRA-REFERENCE.md)
- [Full re-audit closeout](ghidra-full-reaudit-closeout-2026-07-13.md)
- [Reviewed correction plan](ghidra-reviewed-correction-plan-2026-07-13.json)
- [Fullpass discovery findings](ghidra-fullpass-findings/) (waves W001–W018)
- [Retail specimen baseline](retail-specimen-baseline.md)
- Host paths and tracked snapshot posture: [Canonical Ghidra project](../ghidra/README.md)

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
| Tracked snapshot | [`../ghidra/`](../ghidra/README.md) (2026-07-18) | Distributable snapshot; live maintainer DB may be ahead |

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
- [CMSH `CPOS`/`CORI` identity](cmsh-cpos-cori-identity-2026-07-25.md)
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
