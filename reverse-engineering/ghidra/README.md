# Canonical Ghidra project

Status: active — reviewed checkpoint, never a writable project
Last updated: 2026-09-05
Summary: checkpoint identity, writable-project routing and external recovery.

`BEA.gpr` and `BEA.rep/` are the reviewed distributable checkpoint of the
Battle Engine Aquila analysis database. This is the single tracked database
owner; the mutable Linux project and historical recovery packages remain
untracked.

- Snapshot date: 2026-08-28 (seventeenth refresh: the one-row
  `name-cohort-battleengine-set-collision-shape` SET_NAME)
- Ghidra lineage used for the latest review: 12.1.2
- Imported Steam specimen SHA-256:
  `74154BFAE14DDC8ECB87A0766F5BC381C7B7F1AB334ED7A753040EDA1E1E7750`
- Imported specimen MD5: `3b456964020070efe696d2cc09464a55`
- Project payload: 19 files, 187,517,829 bytes
- Canonical project inventory SHA-256:
  `745c00ad15a0fc1c3098533143caded4b1b825583322669df22699b5e99585a5`
- Reviewed tracked checkpoint database `db.18634.gbf`: 68,616,192 bytes, SHA-256
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
files and 187,517,829 bytes. The tracked checkpoint is fixed at `db.18634`
until an authorized semantic promotion. The sole mutable Linux owner was
measured at `db.18635` during activation; re-inspect it before a separately
authorized mutation and never overlap ceremonies.

**Promotion note (superseded in place 2026-08-17).** This header previously still
described the 2026-08-14 HUD route demotion while its `db` and payload pins had
already been advanced by three later promotions — the stale-prose-with-current-
pins failure mode. The pins above are current for the reviewed tracked
checkpoint; the promotion history is:
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

The 19-file tree was measured byte-identical to the then-live Windows project on
2026-08-28 after the `name-cohort-battleengine-set-collision-shape` refresh —
19 files, 187,517,829 bytes, inventory `745c00ad…` from live, tracked, and POST,
with zero per-file mismatches. The independently copied and read-only-reopened
POST recovery was created at
`H:\BEA-Ghidra-Backups\2026-08-28-name-cohort-battleengine-set-collision-shape-post-live`
and is now represented by the sealed Archive A recovery package;
it reopened as `BEA.exe`, MD5 `3b456964020070efe696d2cc09464a55`, specimen
SHA-256 `74154bfa…7750`. Future live work can make the snapshot lag again; each
refresh remains a separately authorized promotion. That ceremony's ignored live
readback is
`local-lab/name-cohort-battleengine-set-collision-shape-ceremony-2026-08-28/readback.json`
(2,264 bytes, SHA-256
`839a43c189e4dbeb9cec36ff84e8b33fd43ff9d8efc40f4aeab4a9e17beb9572`),
and the tracked-snapshot reopen receipt beside it is 5,795 bytes, SHA-256
`300f30085b8ffdae99d8b82850821d0671305002bb1fec97298d14809621e3f5`.

**Linux activation status (2026-08-31).** OpenJDK 21.0.12.1 is installed at
`/usr/lib/jvm/java-21-openjdk`, and the verified Ghidra 12.1.3 PUBLIC runtime is
installed at `/home/xsniper80/.local/opt/ghidra_12.1.3_PUBLIC` (5,218 files,
905,553,502 bytes, inventory SHA-256
`636e51e4d487f64fcfcc4f9516181708827aedd25f2b9ca133c53977519c066b`).
The sole mutable PC project is now
`local-lab/ghidra-projects/BEA/`: Ghidra 12.1.3 `db.18635`, owner `xsniper80`,
18 files / 118,934,388 bytes, inventory
`4320a3500a559da663562046fe3f87a519c9482c3ce8c36d36d80b8e87ee225e`.
It was activated only after a restore-open-verified Archive A PRE, explicit
writable open, separate-process readback, exact full semantic comparison, and a
restore-open-verified POST. PRE and POST agree byte-for-byte across all 8,329
internal function rows and all program metrics; the storage migration changed
no reviewed semantics. Therefore this tracked tree remains the reviewed
`db.18634` checkpoint until a future semantic promotion. External recovery is
the sealed content-addressed package at
`/srv/archive-a/onslaught-ghidra-cold/codex-consolidated-2026-08-31/`; restore
from it to a new path before opening anything.

Related (not this folder):

| Role | Path |
| --- | --- |
| Expedition ops (ignored repo-local lab) | `local-lab/ghidra-fullpass-2026-07-23/` in the canonical checkout (runbook, state, corrections) |
| Wave discovery notes (tracked) | `reverse-engineering/binary-analysis/ghidra-fullpass-findings/` |
| Isolated Xbox oracle evidence | `local-lab/xbox-sparse-symbol-ghidra-20260812-v1/` in the canonical checkout (exports/receipts remain; project databases are restored only through the sealed external catalog, not used as PC live owners) |
| Mutable Linux PC project | `local-lab/ghidra-projects/BEA/` in the canonical checkout (`db.18635`, Ghidra 12.1.3, owner `xsniper80`) |
| Linux activation evidence | `local-lab/ghidra-linux-12.1.3-activation-20260830-v1/` in the canonical checkout (completion receipt, PRE/POST semantic exports, logs) |
| Xbox promotion evidence | `reverse-engineering/binary-analysis/xbox-source-line-anchor-ghidra-2026-08-12.md` (1,166 instruction-local source maps per build; no whole-function transfer) |

The database retains program bytes needed by Ghidra together with functions,
symbols, types, comments, references, and reviewed analysis state. It does not
contain a standalone retail executable, save, debugger transcript, or runtime
capture. This canonical database is the repository's explicitly retained
analysis artifact; its inclusion is not a claim of affiliation, endorsement,
or broader permission for retail game assets. Original game-derived material
remains copyright of its respective rights holders, and the repository's source
licenses do not independently relicense that material.

For writable work, open only `local-lab/ghidra-projects/BEA/BEA.gpr`; use a
disposable restored copy for experiments and default to read-only inspection.
Ghidra may update project metadata when opening or upgrading it. Static database contents remain
evidence, not a claim that every inferred signature or semantic label is
correct; controlled copied-runtime observation continues to own behavioral
claims.

## Historical Windows live-ceremony contract (suspended)

This is the exact ceremony that produced the preserved Windows checkpoint. It
remains normative history for interpreting its receipts, but its drive letters
are not actionable on Linux. The Linux-native contract is defined by the
activation status and routing table above; this Windows contract remains
provenance only. Steps were ordered; each
gate had to pass before the next began, and a failed or skipped gate aborted the
ceremony — there was no in-process rollback in this Ghidra build, so
reversibility was restore-from-verified-backup only.

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

Historical Windows volume rules for every step above: new backups went directly
to the documented `H:\BEA-Ghidra-Backups` collection; D:, F:, and G: were not
backup or staging fallbacks. G: remained read-only evidence, D: held the active
Ghidra install, and ACLs or volume ownership were never rewritten as a
workaround.

## Current Linux host routing

The prior Windows drive-letter layout is historical receipt provenance. Agents
on this host should use the following routing and must not translate drive
letters speculatively:

| Role | Path |
| --- | --- |
| Installed Java | `/usr/lib/jvm/java-21-openjdk` — OpenJDK 21.0.12.1 |
| Installed Ghidra runtime | `/home/xsniper80/.local/opt/ghidra_12.1.3_PUBLIC` — verified PUBLIC 12.1.3 inventory `636e51e4…066b` |
| Headless entry | `/home/xsniper80/.local/opt/ghidra_12.1.3_PUBLIC/support/analyzeHeadless` |
| Reviewed tracked checkpoint | `reverse-engineering/ghidra/` (this tree; `db.18634`; preserve in place) |
| Mutable Linux PC project | `local-lab/ghidra-projects/BEA/` (`db.18635`; sole writable owner) |
| Activation evidence | `local-lab/ghidra-linux-12.1.3-activation-20260830-v1/` (ignored completion receipt and semantic PRE/POST) |
| External recovery | `/srv/archive-a/onslaught-ghidra-cold/codex-consolidated-2026-08-31/` (sealed package; restore elsewhere before opening) |
| Dated copies of both homes | `/srv/archive-a/onslaught-ghidra-cold/2026-09-04/` (checkpoint and mutable project stored separately) |
| Second-disk cold mirror | `/srv/archive-b/onslaught-ghidra-cold-mirror/` (recovery only; never open in place) |

The former Samsung raw snapshot, Archive A Windows `source/` tree, and
Recovery reconciliation folder have been deleted. Their old receipts are
history, not additional surviving database copies. Keep the current cold
copies and the historical rehearsal projects until David approves a specific
numbered deletion batch. A larger database generation counter in a rehearsal
copy does not make it the reviewed or writable authority.

Expedition overlays (RO clones, wave exports, ops state, correction ledgers)
live under real, ignored canonical-checkout `local-lab/` — do not commit them.
Child worktrees use the canonical absolute path; never create a duplicate lab,
symlink, bind mount, or read-only substitute. Prefer **headless CLI** exports
and scripts under `tools/` for automation only after the selected project and
ceremony gate permit them. Do not assume a Ghidra MCP
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
intentionally predates the later SET_NAME cohorts through the reviewed tracked
`db.18634` checkpoint. Use the mutable database plus a fresh readback for
current names, and compare it with the tracked checkpoint before promotion. Preserve a
correction through its immutable cohort spec and receipts rather than rewriting
a dated projection in place.
