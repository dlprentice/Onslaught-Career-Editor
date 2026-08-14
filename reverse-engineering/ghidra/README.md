# Canonical Ghidra project

`BEA.gpr` and `BEA.rep/` are the reviewed distributable snapshot of the current
Battle Engine Aquila analysis database. This is the single tracked database
owner; local working copies and historical backups remain untracked.

- Snapshot date: 2026-08-14
- Ghidra lineage used for the latest review: 12.1.2
- Imported Steam specimen SHA-256:
  `74154BFAE14DDC8ECB87A0766F5BC381C7B7F1AB334ED7A753040EDA1E1E7750`
- Imported specimen MD5: `3b456964020070efe696d2cc09464a55`
- Project payload: 19 files, 186,977,157 bytes
- Canonical `sha256<TAB>bytes<TAB>path` inventory SHA-256:
  `cda0938c1a266fbe1751a8b0bf175b90c63b296f21fc9631b5bade1ecf93e541`
- Current rolling database `db.18614.gbf`: 68,337,664 bytes, SHA-256
  `d7f0011ea337f58b710415d5664e73d91ca9f1f61e20a836278d3e71b71b2865`

**Promotion note:** this snapshot was refreshed from the source-stable live
maintainer project after five existing-function body fragments passed exact PRE
validation, two saved scratch replicas, rollback and containment controls, one
live apply, separate-process full-inventory readback, tracked-still-PRE proof,
and PRE/POST/tracked restore probes. Internal functions remain 8,280; exact body
ranges become 8,396 and owned `.text` grows by 1,258 bytes to 1,795,470. All
8,275 non-target rows remain byte-identical and only the five reviewed body
rows change. No name, signature, parameter, ABI/storage field, comment, tag,
defined-data unit, stored non-function symbol, program byte, or relocation
changed. See the
[`function-body fragment live-promotion report`](../binary-analysis/pc-function-body-fragment-ghidra-live-promotion-2026-08-14.md),
the preceding
[`external-table boundary live-promotion report`](../binary-analysis/external-table-gap-ghidra-live-promotion-2026-08-14.md),
the preceding
[`text-gap boundary live-promotion report`](../binary-analysis/text-gap-missing-function-ghidra-live-promotion-2026-08-14.md),
the preceding
[`new-function vocabulary live-promotion report`](../binary-analysis/mission-script-registry-new-function-vocabulary-live-promotion-2026-08-13.md),
the preceding
[`explosion-factory live-promotion report`](../binary-analysis/cexplosion-factory-identity-live-promotion-2026-08-13.md),
its [`scratch owner`](../binary-analysis/cexplosion-factory-identity-promotion-2026-08-13.md),
the preceding
[`vocabulary live-promotion report`](../binary-analysis/mission-script-registry-vocabulary-live-promotion-2026-08-13.md),
and the structural
[`boundary live-promotion report`](../binary-analysis/mission-script-registry-boundary-live-promotion-2026-08-13.md).

The 19-file tree is byte-identical to the independently restored/read-only-
opened D: POST recovery made on 2026-08-14. Future live work can make
the snapshot lag again; each refresh remains a separately authorized promotion.
The current ignored live readback and tracked-restore receipts are respectively
`local-lab/ghidra-function-fragment5-range-live-promotion-20260814-v1/runs/live-readback/result.ready.json`
(1,267 bytes, SHA-256 `cbf6c4cb93a3aaba265cde7027ca33f0204c009c16fc8b1c17588ef7932c983a`)
and
`local-lab/ghidra-function-fragment5-range-live-promotion-20260814-v1/tracked-post-restore.ready.json`
(5,945 bytes, SHA-256 `facf9a67d54a67139f8d7b6b0205055cafb0c616e2d4ee03a8fca5c26ea6f4bc`).
The read-only aggregate authority is
`local-lab/ghidra-function-fragment5-range-live-authority-20260814-v1/live-promotion.ready.json`
(26,073 bytes, SHA-256
`18b8a7e75bf44108d72c7589dc2fa6a1ac0e2634fbb8ac387562b41ac2fdd451`).
Its portable verifier is
[`tools/ghidra_function_fragment_range_live_authority.py`](../../tools/ghidra_function_fragment_range_live_authority.py)
(68,331 bytes, SHA-256
`bc6c7fdc9ee9a19ccff0c437166dbde2b08b98a7bcd78b4d3ca7a46de0cab30c`).

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
| Verified off-volume recovery | `D:\BEA-Ghidra-Backups\2026-08-14-function-fragment5-ranges-post-live\` (exact current POST snapshot; independently copied and read-only reopened) |
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

This does not block a new promotion. Every current mutation needs a fresh,
immutable target manifest plus fresh PRE/scratch/apply/readback/POST evidence.
Reuse a supported versioned promotion runner and authority when they already
express the mutation shape and all current gates; add target-specific code only
when the existing runner cannot fail closed on the required metadata or
collateral. Never repin or reinterpret a completed one-shot owner. The Mission-
registry boundary owner named above is a boundary-only reference shape; its
receipt-pinned files remain immutable.

The dated `ghidra-function-name-table-2026-07-27.tsv` also is not a current
name oracle. Nine later historical edits changed 54 rows after its original
seal, and Generations 20–23 now pin that exact dated artifact. Do not restore or
edit it in place and break frozen replay. The 2026-08-12 projection is likewise
frozen for Generations 20–23 and two receipt-pinned instruments. Use the current
2026-08-13 projection plus a fresh live readback for current names; preserve any
correction as a new dated authority.
