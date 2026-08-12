# Canonical Ghidra project

`BEA.gpr` and `BEA.rep/` are the reviewed distributable snapshot of the current
Battle Engine Aquila analysis database. This is the single tracked database
owner; local working copies and historical backups remain untracked.

- Snapshot date: 2026-08-12
- Ghidra lineage used for the latest review: 12.1.2
- Imported Steam specimen SHA-256:
  `74154BFAE14DDC8ECB87A0766F5BC381C7B7F1AB334ED7A753040EDA1E1E7750`
- Imported specimen MD5: `3b456964020070efe696d2cc09464a55`
- Project payload: 19 files, 186,485,637 bytes
- Canonical `sha256<TAB>bytes<TAB>path` inventory SHA-256:
  `b7767b108256c0ff71c033094b25e3f2308ef7d00f007854e0068b9307f3adb4`

**Promotion note:** this snapshot was refreshed from the source-stable live
maintainer project after the Generation 23 CRound arm-effects comment package
passed exact PRE validation, two independent persistent scratch replicas, two
rollback probes, an evidence-path adverse control, separate-process live
readback, and full 8,136-function inventory comparison. Exactly twelve function
comments changed; function boundaries, names, signatures, instructions, data,
symbols, and references did not. These comments preserve the proof's bounded
scope: five selected invocations in two sealed sessions, with only default/3000
and event 4003 gap-free. External effects, event 2000, event 4002, CMissile
placement, field meanings, source spelling, and direct rebuild parity remain
open.

The 19-file tree is byte-identical to the independently restored/read-only-
opened D: disaster-recovery copy made on 2026-08-12. Future live work can make
the snapshot lag again; each refresh remains a separately authorized promotion.
The ignored live-promotion and tracked-restore receipts are respectively
`local-lab/ghidra-cround-handle-event-arm-effects-live-promotion-20260812-v1/live-promotion-v2.ready.json`
(5,323 bytes, SHA-256 `6009a379eeb5c7506a9c1a30f6312e695b74a0a0779161e86f76c76637fc4811`)
and `local-lab/ghidra-cround-handle-event-arm-effects-live-promotion-20260812-v1/tracked-snapshot-restore.ready.json`
(5,971 bytes, SHA-256 `d687fc821b0f674e46337c436f67c02a2adc344c5cd5a85b1e83519b21475e5f`).

Related (not this folder):

| Role | Path |
| --- | --- |
| Expedition ops (ignored lab) | `local-lab/ghidra-fullpass-2026-07-23/` (runbook, state, corrections) |
| Wave discovery notes (tracked) | `reverse-engineering/binary-analysis/ghidra-fullpass-findings/` |

The database retains program bytes needed by Ghidra together with functions,
symbols, types, comments, references, and reviewed analysis state. It does not
contain a standalone retail executable, save, debugger transcript, or runtime
capture. This canonical database is the repository's explicitly retained
analysis artifact; its inclusion is not a claim of affiliation, endorsement,
or broader permission for retail game assets. Original game-derived material
remains copyright of its respective rights holders, and the repository's source
licenses do not independently relicense that material.

Open `BEA.gpr` from a disposable clone or local working copy. Ghidra may update
project metadata when opening or upgrading it. Static database contents remain
evidence, not a claim that every inferred signature or semantic label is
correct; controlled copied-runtime observation continues to own behavioral
claims.

## Local host layout (maintainer workstation)

Machine-local paths (not tracked). Agents on this host should use these unless
the user overrides them:

| Role | Path |
| --- | --- |
| Active Ghidra install | `D:\ghidra_12.1.2_PUBLIC_20260605\ghidra_12.1.2_PUBLIC` |
| Headless entry | `...\support\analyzeHeadless.bat` |
| Prior install archive | `D:\GhidraArchives\` (12.0.3 retained there; do not delete) |
| Working/maintainer project | `C:\Users\david\Ghidra\Projects` (`BEA.gpr` / `BEA.rep`) |
| Verified off-volume recovery | `D:\BEA-Ghidra-Backups\2026-08-12-cround-handle-event-gen23-post-live\` (exact current POST snapshot; independently copied and read-only reopened) |
| User settings | `%APPDATA%\ghidra\ghidra_12.1.2_PUBLIC` |

Expedition overlays (RO clones, wave exports, ops state, correction ledgers)
live under ignored `local-lab/` — do not commit them. Prefer **headless CLI**
exports and scripts under `tools/` for automation. Do not assume a Ghidra MCP
extension is installed or required. Mutating the maintainer project is a
separately authorized action; default posture is read-only on a disposable
copy. Promoting live maintainer DB bytes into this tracked snapshot is likewise
separately authorized.
