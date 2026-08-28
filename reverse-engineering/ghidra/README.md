# Canonical Ghidra project

`BEA.gpr` and `BEA.rep/` are the reviewed distributable snapshot of the current
Battle Engine Aquila analysis database. This is the single tracked database
owner; local working copies and historical backups remain untracked.

- Snapshot date: 2026-08-28 (seventeenth refresh: the one-row
  `name-cohort-battleengine-set-collision-shape` SET_NAME)
- Ghidra lineage used for the latest review: 12.1.2
- Imported Steam specimen SHA-256:
  `74154BFAE14DDC8ECB87A0766F5BC381C7B7F1AB334ED7A753040EDA1E1E7750`
- Imported specimen MD5: `3b456964020070efe696d2cc09464a55`
- Project payload: 19 files, 187,517,829 bytes
- Canonical project inventory SHA-256:
  `745c00ad15a0fc1c3098533143caded4b1b825583322669df22699b5e99585a5`
- Current rolling database `db.18634.gbf`: 68,616,192 bytes, SHA-256
  `40d5100ca9ede5317c2052c9ea0d936ab9f07a0daf39fd96765a839ccf9e4ba2`
  (stable prior `db.18633.gbf`, 68,599,808 bytes, SHA-256
  `73bf683b0050d3b5c4c6d159de7d997ebb436833733c44abbeb0b6945faba57a`, retained)

**Reproducing the inventory digest.** The convention was previously stated as
`sha256<TAB>bytes<TAB>relative-posix-path<LF>`, which reads as line-terminated.
It is not: the digest is over the rows **joined** by `LF` with **no trailing
newline**, one row per payload file as
`sha256<TAB>bytes<TAB>relative-posix-path`, sorted by the rendered line, over the
19 payload files with this `README.md` excluded. Measured 2026-08-28 after the
Battle Engine collision-shape name refresh against the tracked tree, live
maintainer project, and verified POST backup: all reproduce `745c00ad…` at 19
files and 187,517,829 bytes. Re-measure rather than quote — a concurrent
ceremony can move this at any time.

**Promotion note (superseded in place 2026-08-17).** This header previously still
described the 2026-08-14 HUD route demotion while its `db` and payload pins had
already been advanced by three later promotions — the stale-prose-with-current-
pins failure mode. The pins above are current; the promotion history is:
`db.18618` → 41 boundary corrections → `db.18619`/`db.18620` → 160 name
corrections (158 functions, 2 labels) → `db.18621` → 294 ABI signature
corrections → `db.18622` → **CTentacle factory-name ceremony A** → `db.18623` →
**CTentacle factory-name ceremony B** → `db.18624` → the 36-row
`abi-two-witness-arity36` SET_PROTOTYPE cohort → `db.18625` → the five-row
runtime-witnessed `name-cohort5` → `db.18626` → the 65-slot RTTI vftable
`vftable-cohort65` SET_DATA_POINTER cohort → `db.18627` → the two-row
`varargs-cohort2` SET_PROTOTYPE (`sprintf` / `CConsole__AddString` varargs
axis only) → `db.18628` → the 12-row `name-cohort-unique-owner` SET_NAME
→ `db.18629` → the 8-row `name-cohort-fun-unique-owner` SET_NAME
→ `db.18630` → the 7-row `name-cohort-placeholder-unique-owner` SET_NAME
→ `db.18631` → the 3-row `name-cohort-cockpit-dual-owner` SET_NAME
→ `db.18632` → the 6-row `name-cohort-round-dual-owner` SET_NAME
→ `db.18633` → the one-row
`name-cohort-battleengine-set-collision-shape` SET_NAME → `db.18634` on
2026-08-28, each a separately authorized promotion. Internal functions remain
**8,329** across all fifteen: no function was created or destroyed. All fifteen ceremonies are owned
by the shared cohort framework's replayable specs under `tools/cohort-specs/`;
prefer replaying a spec over reading this paragraph. The 34 `.data` rows of the
original 99-slot pointer cohort were correctly excluded and have a terminal
disposition: none is a vtable (CRT init/hook tables, a `CFastVB` CPU-feature
dispatch table, and a `CTexture` interpolation dispatch table) — see
[`../binary-analysis/data34-slot-disposition-2026-08-17.md`](../binary-analysis/data34-slot-disposition-2026-08-17.md).

**The CTentacle factory-name chain (`db.18622` → `db.18624`).** Two one-row
`SET_NAME` cohorts, run as two sequential ceremonies through
`GhidraApplyCohortManifestLive.java`:
`0x004f07e0` `CTentacle__CreateTentacleAI` → `CTentacle__CreateTentacleGuide`
(ceremony A, `db.18623`), then `0x004f0860` `CTentacle__CreateWarspiteAI` →
`CTentacle__CreateTentacleAI` (ceremony B, `db.18624`). They are **two cohorts on
purpose**: each row wants the name the other holds, so a single cohort is refused
by the framework's own `noCycle` and collision gates, and with no in-process
rollback available every non-mutating gate must pass before the first write.
Ceremony A was closed in full — separate-process readback, verified POST backup,
tracked refresh on proven byte equality — before ceremony B's gates were
evaluated. Each ceremony measured `functionsExamined=8329 functionsChanged=1
functionsUntouched=8328 columnsMoved={name=1}`, with an independent external
diff of the full 8,329-row inventory confirming one changed row, zero non-target
movement, zero frozen-column drift, and zero movement in all 29 program-scope
metrics. Evidence and byte anchors:
[`CTentacle factory-name chain`](../binary-analysis/tentacle-factory-name-chain-2026-08-17.md).

The 2026-08-14 HUD route demotion, retained for its own record: four descriptive
names (`0x00483530`, `0x004858d0`, `0x00485d50`, `0x00486940`) were demoted to
neutral `CHud__RoutePanel_T*_<address>` Tier-3 labels after sealed scratch and
current-geometry replicas, containment controls, one live apply,
separate-process full-inventory readback, tracked-still-PRE proof, and
PRE/POST/tracked restore probes. Only those
four rows' names, displayed signatures, comments, and tags changed, and at
program scope only `commentsSha256`. No boundary, instruction, program byte,
data unit, reference, or non-target function row moved. Its "rollback control"
is superseded: in-process rollback is measured **unavailable** in this build, so
reversibility is ceremony-level restore from a verified off-volume PRE backup
only. See the
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

The 19-file tree was measured byte-identical to the live maintainer project on
2026-08-28 after the `name-cohort-battleengine-set-collision-shape` refresh —
19 files, 187,517,829 bytes, inventory `745c00ad…` from live, tracked, and POST,
with zero per-file mismatches. The independently copied and read-only-reopened
POST recovery is retained at
`H:\BEA-Ghidra-Backups\2026-08-28-name-cohort-battleengine-set-collision-shape-post-live`;
it reopened as `BEA.exe`, MD5 `3b456964020070efe696d2cc09464a55`, specimen
SHA-256 `74154bfa…7750`. Future live work can make the snapshot lag again; each
refresh remains a separately authorized promotion. The current ignored live
readback is
`local-lab/name-cohort-battleengine-set-collision-shape-ceremony-2026-08-28/readback.json`
(2,264 bytes, SHA-256
`839a43c189e4dbeb9cec36ff84e8b33fd43ff9d8efc40f4aeab4a9e17beb9572`),
and the tracked-snapshot reopen receipt beside it is 5,795 bytes, SHA-256
`300f30085b8ffdae99d8b82850821d0671305002bb1fec97298d14809621e3f5`.

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

## Live-ceremony contract (normative order)

Every mutation of the maintainer's live project follows this exact sequence.
Steps are ordered; each gate must pass before the next begins, and a failed or
skipped gate aborts the ceremony — there is no in-process rollback in this
Ghidra build, so reversibility is restore-from-verified-backup only.

1. **Verified PRE backup** to `H:\BEA-Ghidra-Backups` (restore-proven before
   any write).
2. **Exact identity**: measure the live database version and payload by
   inspection — never quote a version recorded elsewhere.
3. **Isolated rehearsal** on a disposable replica (census/dry/apply/readback),
   never against live.
4. **Family-specific reviewer GO** for exactly the rows in this cohort's
   manifest; no earlier or other-family GO is a blank check.
5. **Live apply** through the shared cohort framework
   (`tools/GhidraApplyCohortManifestLive.java`).
6. **Separate-process readback** proving only the declared rows moved and all
   frozen columns and program-scope metrics held.
7. **Verified H: POST backup**, independently copied, restore-proven
   byte-identical, and reopened read-only.
8. **Tracked snapshot refresh only on byte equality** between the tracked tree
   and the verified live/POST state.

Volume rules for every step above: new backups go directly to the documented
`H:\BEA-Ghidra-Backups` collection; D:, F:, and G: are not backup or staging
fallbacks. G: remains read-only evidence, D: retains the active Ghidra install,
and ACLs or volume ownership are never rewritten as a workaround.

## Local host layout (maintainer workstation)

Machine-local paths (not tracked). Agents on this host should use these unless
the user overrides them:

| Role | Path |
| --- | --- |
| Active Ghidra install | `D:\ghidra_12.1.2_PUBLIC_20260605\ghidra_12.1.2_PUBLIC` |
| Headless entry | `...\support\analyzeHeadless.bat` |
| Prior install archive | `H:\SoftwareArchives\Ghidra\` (verified 12.0.3 archive plus the 12.1.2 distribution ZIP; not an active install) |
| Working/maintainer project | `C:\Users\david\Ghidra\Projects` (`BEA.gpr` / `BEA.rep`) |
| Verified off-volume recovery | `H:\BEA-Ghidra-Backups\2026-08-28-name-cohort-battleengine-set-collision-shape-post-live` (exact current `db.18634` POST snapshot; independently copied, byte-identical to live/tracked, and read-only reopened) |
| Prior verified recovery | `H:\BEA-Ghidra-Backups\2026-08-17-tentacle-chain-a-post-live` (`db.18623`, ceremony B's PRE) and `...-tentacle-chain-a-pre-live` (`db.18622`, the chain's PRE) |
| Xbox Issue-11 POST recovery | `H:\BEA-Ghidra-Backups\2026-08-12-xbox-sparse-symbol-post-anchors-issue11\` (exact isolated project; restored semantic readback passed) |
| Xbox US-retail POST recovery | `H:\BEA-Ghidra-Backups\2026-08-12-xbox-sparse-symbol-post-anchors-us-retail\` (exact isolated project; restored semantic readback passed) |
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

The dated `ghidra-function-name-table-2026-07-27.tsv` is not a current name
oracle. Nine later historical edits changed 54 rows after its original seal,
and Generations 20–23 now pin that exact dated artifact. Do not restore or edit
it in place and break frozen replay. The 2026-08-12 and 2026-08-13 projections
are likewise frozen; the 2026-08-17 projection ends at `db.18626` and
intentionally predates the later SET_NAME cohorts through current `db.18634`.
Use the canonical database plus a fresh readback for current names. Preserve a
correction through its immutable cohort spec and receipts rather than rewriting
a dated projection in place.
