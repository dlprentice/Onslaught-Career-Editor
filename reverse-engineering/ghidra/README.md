# Canonical Ghidra project

`BEA.gpr` and `BEA.rep/` are the reviewed distributable snapshot of the current
Battle Engine Aquila analysis database. This is the single tracked database
owner; local working copies and historical backups remain untracked.

- Snapshot date: 2026-08-14 (second refresh: HUD route name demotion)
- Ghidra lineage used for the latest review: 12.1.2
- Imported Steam specimen SHA-256:
  `74154BFAE14DDC8ECB87A0766F5BC381C7B7F1AB334ED7A753040EDA1E1E7750`
- Imported specimen MD5: `3b456964020070efe696d2cc09464a55`
- Project payload: 19 files, 187,059,077 bytes
- Canonical project inventory (sha256<TAB>bytes<TAB>relative-posix-path<LF>,
  sorted by rendered line) SHA-256:
  `08a7ffdaca6864a03431997f95730600abbbda0f25f39f7b0c12ae1348307377`
- Current rolling database `db.18621.gbf`: 68,386,816 bytes, SHA-256
  `ac5fcf400da340954bfe2913f3169bd5000a078f7b0a7a2bc606c9006809f263`
  (stable prior `db.18620.gbf` retained)

**Promotion note:** this snapshot was refreshed from the source-stable live
maintainer project after the four HUD route descriptive-name demotions
(`0x00483530`, `0x004858d0`, `0x00485d50`, `0x00486940` → neutral
`CHud__RoutePanel_T*_<address>` Tier-3 labels) passed sealed scratch and
current-geometry replicas, rollback and containment controls, one live apply,
separate-process full-inventory readback, tracked-still-PRE proof, and
PRE/POST/tracked restore probes. Internal functions remain 8,329; only the
four rows' names, displayed signatures, comments, and tags changed, and at
program scope only `commentsSha256`. No boundary, instruction, program byte,
data unit, reference, or non-target function row moved. See the
[`HUD route name demotion report`](../binary-analysis/hud-route-name-demotion-live-promotion-2026-08-14.md)
and the preceding
[`D3DX two-function live-promotion report`](../binary-analysis/d3dx-gap-two-function-ghidra-live-promotion-2026-08-14.md),
the preceding
[`CRT EH parent-range live-promotion report`](../binary-analysis/crt-eh-parent-range-ghidra-live-promotion-2026-08-14.md),
the preceding
[`CRT P0 live-promotion report`](../binary-analysis/crt-runtime-p0-ghidra-live-promotion-2026-08-14.md),
the preceding
[`JPEG/IJG callback live-promotion report`](../binary-analysis/jpeg-ijg-callback-ghidra-live-promotion-2026-08-14.md),
the preceding
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
opened D: POST recovery made on 2026-08-14 (HUD route demotion POST backup).
Future live work can make
the snapshot lag again; each refresh remains a separately authorized promotion.
The current ignored live readback and tracked-restore receipts are respectively
`local-lab/ghidra-hud-route-demotion-20260814-v1/runs/live-readback/targets.ready.json`
(1,878 bytes, SHA-256 `c5da3f2136c430bb932c1f35b4c1c1e07d01fc12ab928cf6c370b8f2f509f163`)
and
`local-lab/ghidra-hud-route-demotion-20260814-v1/tracked-snapshot-restore.ready.json`
(5,897 bytes, SHA-256
`72d427018989894fbfca07136c919751481f17c9aecc704f0c690655e918b3a8`).
The read-only aggregate authority is
`local-lab/ghidra-hud-route-demotion-live-authority-20260814-v1/live-promotion.ready.json`
(4,738 bytes, SHA-256
`42c8383f807bc2d645fe592dc88fd0f4c4b2386653a390ff973986189703b17b`).
Its portable verifier is
[`tools/ghidra_hud_route_demotion_live_authority.py`](../../tools/ghidra_hud_route_demotion_live_authority.py).

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
| Verified off-volume recovery | `D:\BEA-Ghidra-Backups\2026-08-14-hud-route-demotion-post-live` (exact current POST snapshot; independently copied and read-only reopened) |
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
