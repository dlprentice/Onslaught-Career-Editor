# Canonical Ghidra project

`BEA.gpr` and `BEA.rep/` are the reviewed distributable snapshot of the current
Battle Engine Aquila analysis database. This is the single tracked database
owner; local working copies and historical backups remain untracked.

- Snapshot date: 2026-08-09
- Ghidra lineage used for the latest review: 12.1.2
- Imported Steam specimen SHA-256:
  `74154BFAE14DDC8ECB87A0766F5BC381C7B7F1AB334ED7A753040EDA1E1E7750`
- Imported specimen MD5: `3b456964020070efe696d2cc09464a55`
- Project payload: 19 files, 186,485,637 bytes
- Canonical `sha256<TAB>bytes<TAB>path` inventory SHA-256:
  `9aacd7d0dad41879229aab2cf73918d28208a0ad29df9748c4412264ef475c74`

**Promotion note:** this snapshot was refreshed from a source-stable copy of the
live maintainer project after the backed-up, scratch-reproduced, separately
read-back TokenArchive metadata, Mission-native `IScript__SetPos`, and the
eleven-function Mission-native boundary/name cohort ending in
`IScript__SetLightningDensity`. The current snapshot contains 8,136 functions;
the cohort added only exact boundaries, shipped registry names, and fact-only
comments, with no signature or behavior-contract promotion.
The 19-file tree is byte-identical to the independently verified D: disaster-
recovery copy made on 2026-08-09. Future live work can make the snapshot lag
again; each refresh remains a separately authorized promotion.
The ignored read-only restore receipt is
`local-lab/ghidra-tracked-snapshot-cohort11-promotion-20260809-v1/tracked-snapshot-restore.ready.json`
(5,931 bytes, SHA-256 `44035be354c93c2e81cbedd049885e946309c20f8c9682d9874eb97caaaf2518`).

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
| Verified off-volume recovery | `D:\BEA-Ghidra-Backups\2026-08-09-post-recovery\` (including the exact current eleven-function POST snapshot plus retained read-only restore drill) |
| User settings | `%APPDATA%\ghidra\ghidra_12.1.2_PUBLIC` |

Expedition overlays (RO clones, wave exports, ops state, correction ledgers)
live under ignored `local-lab/` — do not commit them. Prefer **headless CLI**
exports and scripts under `tools/` for automation. Do not assume a Ghidra MCP
extension is installed or required. Mutating the maintainer project is a
separately authorized action; default posture is read-only on a disposable
copy. Promoting live maintainer DB bytes into this tracked snapshot is likewise
separately authorized.
