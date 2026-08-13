# Canonical Ghidra project

`BEA.gpr` and `BEA.rep/` are the reviewed distributable snapshot of the current
Battle Engine Aquila analysis database. This is the single tracked database
owner; local working copies and historical backups remain untracked.

- Snapshot date: 2026-08-13
- Ghidra lineage used for the latest review: 12.1.2
- Imported Steam specimen SHA-256:
  `74154BFAE14DDC8ECB87A0766F5BC381C7B7F1AB334ED7A753040EDA1E1E7750`
- Imported specimen MD5: `3b456964020070efe696d2cc09464a55`
- Project payload: 19 files, 186,747,781 bytes
- Canonical `sha256<TAB>bytes<TAB>path` inventory SHA-256:
  `8eb664062a8ba67005e9f8ad8f61aa2222585622c41022a69080c5e408cd3cf6`
- Current rolling database `db.18610.gbf`: 68,222,976 bytes, SHA-256
  `210a0461a6b1746f7bbc53e883b616c4a02694a055f1bd23ccadaf44472c1356`

**Promotion note:** this snapshot was refreshed from the source-stable live
maintainer project after the separate `0x0050FF10` explosion-factory repair
passed exact PRE validation, two independent persistent scratch replicas,
rollback/compensation and external-path controls, one live apply,
separate-process full-inventory readback, and POST restore. The operation
replaced the disproved pickup identity/signature/comment with the bounded
`CWorldPhysicsManager__CreateExplosion` contract. Internal functions remain
8,170; all bodies, instructions, program bytes, data units, references, and
8,169 non-target function rows remained unchanged. The preceding 75-row
MissionScript vocabulary ceremony and 34-boundary structural ceremony remain
distinct. See the
[`explosion-factory live-promotion report`](../binary-analysis/cexplosion-factory-identity-live-promotion-2026-08-13.md),
its [`scratch owner`](../binary-analysis/cexplosion-factory-identity-promotion-2026-08-13.md),
the preceding
[`vocabulary live-promotion report`](../binary-analysis/mission-script-registry-vocabulary-live-promotion-2026-08-13.md),
and the structural
[`boundary live-promotion report`](../binary-analysis/mission-script-registry-boundary-live-promotion-2026-08-13.md).

The 19-file tree is byte-identical to the independently restored/read-only-
opened D: disaster-recovery copy made on 2026-08-13. Future live work can make
the snapshot lag again; each refresh remains a separately authorized promotion.
The current ignored live readback and tracked-restore receipts are respectively
`local-lab/ghidra-cexplosion-live-promotion-20260813-v1/runs/live-readback/cexplosion.ready.json`
(2,159 bytes, SHA-256 `1616fea1eb6276b052e99260a3f79084a76831544ae350a549783b5115ee3175`)
and
`local-lab/ghidra-cexplosion-live-promotion-20260813-v1/tracked-snapshot-restore.ready.json`
(5,911 bytes, SHA-256 `72fc473678d86a43dfd3dbb4f0df692e0c507342b5e29042c6ab30ba68ec3126`).
The aggregate read-only authority is
`local-lab/ghidra-cexplosion-live-authority-20260813-v1/live-promotion.ready.json`
(31,486 bytes, SHA-256 `3336fa46c8c9d894f1d81fc5561fba91ff76c89ca728792069c0746d64b55337`).

Related (not this folder):

| Role | Path |
| --- | --- |
| Expedition ops (ignored lab) | `local-lab/ghidra-fullpass-2026-07-23/` (runbook, state, corrections) |
| Wave discovery notes (tracked) | `reverse-engineering/binary-analysis/ghidra-fullpass-findings/` |
| Isolated Xbox oracle projects | `local-lab/xbox-sparse-symbol-ghidra-20260812-v1/ghidra-projects/` (Issue-11 and US-retail; ignored retail-derived evidence, not this tracked PC snapshot) |
| Xbox promotion evidence | `reverse-engineering/binary-analysis/xbox-source-line-anchor-ghidra-2026-08-12.md` (1,166 instruction-local source maps per build; no whole-function transfer) |

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
| Verified off-volume recovery | `D:\BEA-Ghidra-Backups\2026-08-13-cexplosion-factory-post-live\` (exact current POST snapshot; independently copied and read-only reopened) |
| Xbox Issue-11 POST recovery | `D:\BEA-Ghidra-Backups\2026-08-12-xbox-sparse-symbol-post-anchors-issue11\` (exact isolated project; restored semantic readback passed) |
| Xbox US-retail POST recovery | `D:\BEA-Ghidra-Backups\2026-08-12-xbox-sparse-symbol-post-anchors-us-retail\` (exact isolated project; restored semantic readback passed) |
| User settings | `%APPDATA%\ghidra\ghidra_12.1.2_PUBLIC` |

Expedition overlays (RO clones, wave exports, ops state, correction ledgers)
live under ignored `local-lab/` — do not commit them. Prefer **headless CLI**
exports and scripts under `tools/` for automation. Do not assume a Ghidra MCP
extension is installed or required. Mutating the maintainer project is a
separately authorized action; default posture is read-only on a disposable
copy. Promoting live maintainer DB bytes into this tracked snapshot is likewise
separately authorized.

## Promotion-tool status

The early bulk/global-initializer and target-lock promotion programs are
historical one-shot owners, not reusable current launchers. In particular,
`ghidra_target_lock_semantic_live_launcher.py`,
`ghidra_global_init515_live_promotion.py`, and their envelope, batch, scratch,
full-520, and target-lock proof helpers retain fail-closed dependency hashes
from their completed 2026-08-03–07 ceremonies. Later reviewed fixes changed the
shared backup/envelope helpers, so reviving those old programs now stops on an
integrity mismatch. Do not repair that by mechanically replacing hashes: their
receipts describe the old dependency graph and the live project is no longer in
their PRE state.

This does not block a new promotion. A current mutation needs a new bounded
target-specific owner with fresh hashes and fresh PRE/scratch/apply/readback/
POST evidence. The Mission-registry boundary owner named above is the most
recent boundary-only shape to study; its receipt-pinned files remain immutable.

The dated `ghidra-function-name-table-2026-07-27.tsv` also is not a current
name oracle. Nine later historical edits changed 54 rows after its original
seal, and Generations 20–23 now pin that exact dated artifact. Do not restore or
edit it in place and break frozen replay. The 2026-08-12 projection is likewise
frozen for Generations 20–23 and two receipt-pinned instruments. Use the current
2026-08-13 projection plus a fresh live readback for current names; preserve any
correction as a new dated authority.
