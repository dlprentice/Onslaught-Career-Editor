# Canonical Ghidra project

Status: active — reviewed checkpoint, never a writable project
Last updated: 2026-09-27
Summary: checkpoint identity, writable-project routing and external recovery.

`BEA.gpr` and `BEA.rep/` are the reviewed distributable checkpoint of the
Battle Engine Aquila analysis database. This is the single tracked database
owner; the mutable Linux project and historical recovery packages remain
untracked. The latest working correction is the
[GenericSPtrSet identities](#re-audit-genericsptrset-identities--september-27);
`developer_state.json` → `current_re_authority.latestLiveGhidraState` owns its measured identity.

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
until an explicitly scoped checkpoint refresh. The working owner has since
received the first-training corrections below; never synchronize the two homes automatically.
Re-inspect the selected working owner before every mutation.

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
refresh must be part of an authorized promotion plan, not an automatic sync. Its ordinary
approved gates do not need repeated permission. That ceremony's ignored live
readback is
`local-lab/name-cohort-battleengine-set-collision-shape-ceremony-2026-08-28/readback.json`
(2,264 bytes, SHA-256
`839a43c189e4dbeb9cec36ff84e8b33fd43ff9d8efc40f4aeab4a9e17beb9572`),
and the tracked-snapshot reopen receipt beside it is 5,795 bytes, SHA-256
`300f30085b8ffdae99d8b82850821d0671305002bb1fec97298d14809621e3f5`.

**Linux activation evidence (2026-08-31).** OpenJDK 21.0.12.1 is installed at
`/usr/lib/jvm/java-21-openjdk`, and the verified Ghidra 12.1.3 PUBLIC runtime is
installed at `/home/xsniper80/.local/opt/ghidra_12.1.3_PUBLIC` (5,218 files,
905,553,502 bytes, inventory SHA-256
`636e51e4d487f64fcfcc4f9516181708827aedd25f2b9ca133c53977519c066b`).
At activation, the sole mutable PC project became
`local-lab/ghidra-projects/BEA/`: Ghidra 12.1.3 `db.18635`, owner `xsniper80`,
18 files / 118,934,388 bytes, inventory
`4320a3500a559da663562046fe3f87a519c9482c3ce8c36d36d80b8e87ee225e`.
It was activated only after a restore-open-verified Archive A PRE, explicit
writable open, separate-process readback, exact full semantic comparison, and a
restore-open-verified POST. PRE and POST agree byte-for-byte across all 8,329
internal function rows and all program metrics; the storage migration changed
no reviewed semantics. This tracked tree remains the reviewed
`db.18634` checkpoint. Historical recovery is
the sealed content-addressed package at
`/srv/archive-a/onslaught-ghidra-cold/codex-consolidated-2026-08-31/`; restore
from it to a new path before opening anything.

**First-training corrections (2026-09-07).** After this cohort the working project measured
`db.18636`: 18 payload files, 118,967,156 bytes, inventory SHA-256
`40abc51047b99c98171c475e41df109843b43ec8d62453f094fc3176ac932df4`.
Its main database is 68,665,344 bytes, SHA-256
`213d1f864708a8c3da88f107aa94a163c7faa171f9ff52ab95b61023704e6104`.
The immutable [manifest](../../tools/cohort-specs/first-training-semantic-corrections.manifest.tsv)
and [spec](../../tools/cohort-specs/first-training-semantic-corrections.spec.tsv)
correct exactly five names and their nonrepeatable comments: Battle Engine charge
dispatch, Jet charge dispatch, weapon charge readiness, weapon fire, and the bitmap
font glyph gate. Source/body evidence and unresolved type/behavior limits are in
each comment. No function boundary, prototype, tag or repeatable comment changed.

The isolated rehearsal and separate live readback agree byte-for-byte over all
8,329 function rows and program metrics. Exactly five rows changed names/comments;
8,324 stayed unchanged, and only the program-wide comment digest moved. A stale
comment negative control was rejected before writes. Evidence is in
`local-lab/ghidra-first-training-20260907-v1/`: `live-readback.json` is 2,329 bytes,
SHA-256 `18e87726fc587bd4244ab8b65d923eae142807cdc2a086f239770495a23e516f`.
Both PRE and POST under
`/srv/archive-a/onslaught-ghidra-cold/2026-09-07-first-training-semantics/`
were copied, hash-compared, restored elsewhere and opened read-only successfully;
the POST restore receipt is 5,676 bytes, SHA-256
`9157c8aca6d1cdb3edb779c3ddf3def082f98d06702d695df9e0cb4a06cdb74c`.

The tracked project payload remains the exact `745c00ad…` checkpoint above.
This cohort deliberately excludes its refresh. A read-only checkpoint-copy open
was refused by its historical `david` owner; comparison instead used its retained
activation export, tied to the freshly matching checkpoint payload, and the fresh
working PRE export, which was byte-identical to that export. No checkpoint reopen
or runtime-parity result is claimed. Current documentation names compose the
frozen August 31 table with the five-row manifest through
`tools/re_function_doc_names_check.py`; historical explicit-table consumers stay frozen.

**First-training keyboard boundary (2026-09-08).** After this cohort the working project
measured `db.18637`: 18 payload files, 118,967,156 bytes, inventory SHA-256
`92f271aaa7070b8a321be330458c0983f494ae8b907c83b76a80dca3c6ef2980`.
Its main database is 68,665,344 bytes, SHA-256
`16eb1a51eea34c68f703e4e351848c1b4ef9aa0cd1271a37cc79f0ae30936fa3`.
The [manifest](../../tools/cohort-specs/first-training-keyboard-boundary.manifest.tsv)
and [spec](../../tools/cohort-specs/first-training-keyboard-boundary.spec.tsv)
create exactly one default function, `FUN_0051feb0`, over existing instructions
at `[0x0051feb0,0x0051ff83)`: 211 bytes, 73 instructions, pristine body SHA-256
`c69d375fab72143d7a3d6fcc01aa0f5a792404853818e05231bca532875c7d8b`.
All branches stay inside this body, no other function/data owns it, and external
references target its entry. The former gap/padding classification missed the
physical keyboard callback. The function retains a default undefined prototype:
caller stack cleanup and AL use do not yet establish exact argument types or a
source-compatible declaration.

The shared framework's new bounded `CREATE_FUNCTION` verb passed isolated
rehearsal, separate readback and controls rejecting existing ownership and a
clipped final return before writes. Independent review and the full live export
confirmed all 8,329 prior function rows unchanged; only the default function and
its symbol were added. The full program export changes only the function count
to 8,330. No instruction, byte, data unit, reference or existing metadata changed.
Live and separately reopened rehearsal exports agree exactly. Evidence is under
`local-lab/ghidra-first-training-20260907-v1/keyboard-boundary/`;
`live-readback.json` is 2,274 bytes, SHA-256
`f374306294f2c68bf4ff10e1dc13ad3d848e5ca3d7b956157422db10062a3a06`.

The restore-proven September 7 POST above matched live exactly and served as
this cohort's PRE. The new independent POST is
`/srv/archive-a/onslaught-ghidra-cold/2026-09-08-first-training-keyboard/post-working/`.
It was hash-compared, restored elsewhere and opened read-only successfully;
`post-working-restore.json` is 5,711 bytes, SHA-256
`ac3ea68ba3e9bfa5c98e05cdb574d5184805bfeb480c012d4d56ab8ee9aa3d16`.
The tracked payload still matches `745c00ad…`; checkpoint refresh remains
excluded. The current-name checker composes the frozen table, five-name manifest
and this one-function manifest without rewriting historical tables or consumers.

**Bounding-box reader metadata (2026-09-08).** After this cohort the working project measured
`db.18638`: 18 payload files, 118,967,156 bytes, inventory SHA-256
`9da943a8b4ac1d0b3abc383e19a187bf2a77ce85945aa2bb1bf7dfbf34ca2c60`.
Its main database is 68,665,344 bytes, SHA-256
`dd70a143d8ed72214c7ec178bc2fc78ab8a71dfa09a4b4debcb7f3fb821cca6f`.
The [manifest](../../tools/cohort-specs/mesh-bounding-box-metadata.manifest.tsv)
and [spec](../../tools/cohort-specs/mesh-bounding-box-metadata.spec.tsv) correct
exactly `0x004b3180`: role name `BoundingBox__ReadChunk_004b3180`, destination
parameter `existing_box`, measured-contract comment, and `material` tag replaced
by `bounding-box`. The [MeshPart evidence](../binary-analysis/functions/MeshPart.cpp.md#bbox-reader-correction)
does not recover its original source name or class.

The isolated rehearsal, independent review, stale-tag rejection before writes,
sealed checks, live apply and separate-process readback passed. All 8,329 other
function rows remain identical; bodies, instructions, data and references are
unchanged. The only program-export change is the comment digest. The separate
return/parameter export preserves types, storage, source and comments exactly,
changing only the declared destination name. Live function, program and
parameter exports equal the reopened rehearsal POST byte-for-byte. Evidence is
under `local-lab/ghidra-first-training-20260907-v1/bounding-box/`;
`live-readback.json` is 2,413 bytes, SHA-256
`d6b4e7f489ce2e9636f2e17d383331d45738d90217d49c94fe1ed6a4ef46079e`.

The restore-proven keyboard POST above matched live and served as PRE. The new
independent POST is
`/srv/archive-a/onslaught-ghidra-cold/2026-09-08-mesh-bounding-box/post-working/`.
It was hash-compared, restored elsewhere and opened read-only successfully;
`post-working-restore.json` is 5,695 bytes, SHA-256
`10fa53f348631ed705120f56d3d5655827663474b0a3719ad4a528a291ec230d`.
The tracked payload still matches `745c00ad…`; its refresh remains excluded.
The current-name checker additionally composes this exact one-row manifest;
historical tables and explicit-table consumers remain unchanged. The adjacent
stream-loader comment was outside this cohort; the follow-up below corrects it.
No runtime-parity result is claimed.

**Bounds contract comments (2026-09-08).** After this cohort the working project measured
`db.18639`: 18 payload files, 118,967,156 bytes, inventory SHA-256
`fdafa7bdb0966e6fe11840285d45db0981a58e701ce64f13620f73106bf62a3a`.
Its main database is 68,665,344 bytes, SHA-256
`0169f476474d907bd17d96159d05b0ff1e06d5e2664a30503626e00fcf9d6c38`.
The [manifest](../../tools/cohort-specs/bounds-contract-comments.manifest.tsv)
and [spec](../../tools/cohort-specs/bounds-contract-comments.spec.tsv) change only
two nonrepeatable comments. `0x00479770` now records the shipped all-three-axes
distance branch's doubled Z term. `0x004b27a0` now identifies its BBOX helper
call and returned pointer store, replacing the old material interpretation.
Names, prototypes, tags, repeatable comments, bodies, bytes and references are
unchanged. These static corrections establish neither original source identity
nor runtime parity.

Fresh PRE identity, isolated apply, independent review, sealed checks, live
apply and separate readback passed. Exactly two comment rows moved; all 8,328
other function rows remain identical. Only the program comment digest changed.
The complete live function/program exports equal the separately reopened
rehearsal POST. Evidence is under
`local-lab/ghidra-first-training-20260907-v1/bounds-comments/`:
`live-readback.json` is 2,259 bytes, SHA-256
`cbade41628461d9c366e47671a9c3b73fd74f146324780f6a02ab28fb442bf4f`.

The restore-proven BBOX POST above matched live and served as PRE. The new
independent POST is
`/srv/archive-a/onslaught-ghidra-cold/2026-09-08-bounds-contract-comments/post-working/`.
It was copied, hash-compared, restored elsewhere and opened read-only successfully;
`post-working-restore.json` is 5,708 bytes, SHA-256
`cfc4a9e9aebe0bd3144368f7bc6045244fde63370558f302ae17315ca24f662c`.
The tracked checkpoint still matches `745c00ad…`; its refresh remains excluded.
Current-name projection is unchanged by this comment-only cohort.

**Segment-controller ownership (2026-09-08).** The working project now measures
`db.18640`: 18 payload files, 118,967,156 bytes, inventory SHA-256
`6d9e0cccc25aae89a0096ea58d758ca12cd5dba854c7cdab589cb547529106f2`.
Its main database is 68,665,344 bytes, SHA-256
`9f8b93ca89aef4f80897edf75d8b62d267e8840d631932d5f890ac2e260ed047`.
The [manifest](../../tools/cohort-specs/segment-controller-ownership.manifest.tsv)
and [spec](../../tools/cohort-specs/segment-controller-ownership.spec.tsv) correct
four names, nonrepeatable comments and exact tag sets at `0x00444f00`,
`0x00444f20`, `0x00494fa0` and `0x00494ff0`. The first two belong to the
segments controller; the latter two are its motion-controller bridges. The
[receiver evidence](../binary-analysis/functions/DestructableSegmentsController.cpp/CUnitAI__CanUseIndexedSegmentEntry.md)
refutes the old UnitAI classification. These are analyst role names; original
source method names and runtime parity remain unproven.

Fresh PRE identity, isolated apply, independent review, sealed readback,
live dry/apply and separate readback passed. All 8,326 other function rows
remain identical; each target retains its signature shape, parameters, body
and repeatable comment. The program export changes only its comment digest.
The full live exports equal the separately reopened rehearsal POST. The current
name/extent projection also matches all 8,330 live rows without changing frozen
tables. Framework derivation/comment checks passed 11/11. An initial unprefixed
address draft was refused before writes and remains in the private evidence.
Evidence root: `local-lab/ghidra-first-training-20260907-v1/segment-controller-ownership/`.
`live-readback.json` is 2,211 bytes, SHA-256
`2541d9f6fe5885c2f086ad6d0414173d0712950fdc202e45a39faeb5d89ebff9`.

The restore-proven bounds-comment POST above matched live and served as PRE.
The new independent POST is
`/srv/archive-a/onslaught-ghidra-cold/2026-09-08-segment-controller-ownership/post-working/`.
It was copied, hash-compared, restored elsewhere and opened read-only successfully.
`post-working-restore.json` is 5,738 bytes, SHA-256
`9aa80129d73e9d0cf5eca20a23972cd45a6f9c5cc6a3417e9bd6c243f63b25e5`.
The tracked checkpoint still matches `745c00ad…`; its refresh remains excluded.

## Air-contact shutdown correction (2026-09-08)

The working project now measures `db.18641`: 18 payload files, 118,967,156 bytes,
canonical inventory SHA-256
`00b7454c77b3afbe329f613d5bda15d117f3e132bb5e3bd25748214f2df562f1`.
Its main database is 68,665,344 bytes, SHA-256
`7b090c03af8297d3ac1fc479058bb7784ad79d43f9e79938e39d082d5e21f6ca`.
The [manifest](../../tools/cohort-specs/air-contact-shutdown.manifest.tsv) and
[spec](../../tools/cohort-specs/air-contact-shutdown.spec.tsv) correct exactly
the names and nonrepeatable comments at `0x00403ba0` and `0x004d1f10`.
The [Plane contact evidence](../binary-analysis/functions/Plane.cpp/CPlane__Hit_CheckFatalDamageAndDie.md)
distinguishes contact-triggered shutdown from fatal damage and leaves the shared
handler's declaring class uncertain. These are analyst role names.

Fresh PRE identity, isolated apply, independent review, sealed checks, live
dry/apply and separate readback passed. Exactly two function rows changed;
8,328 stayed identical. Bodies, ABI, tags and repeatable comments remained
unchanged. Program metadata changes only its comment digest. Full live exports
equal the separately reopened rehearsal POST. Framework derivation/comment
checks passed 11/11. Evidence is under
`local-lab/ghidra-first-training-20260907-v1/air-contact-shutdown/`;
`live-readback.json` is 2,283 bytes, SHA-256
`f8d23d4bb32ed9b535594494080979ffaa4f74db43c9dc24eea15f3c72f2ce43`.

The restore-proven segment-controller POST matched live and served as PRE.
The new independent POST is
`/srv/archive-a/onslaught-ghidra-cold/2026-09-08-air-contact-shutdown/post-working/`.
It was copied, hash-compared, restored elsewhere and opened read-only successfully.
`post-working-restore.json` is 5,724 bytes, SHA-256
`5d30061c04776b960ff8e3a0c03aa6cb27cdcd638f84b22a7dbfd104dac59a21`.
The tracked checkpoint still matches `745c00ad…`; its refresh remains excluded.
Current documentation names additionally compose this exact two-row manifest.

## Plane-controller event argument (2026-09-12)

The working project measures `db.18642`: 18 payload files,
118,967,156 bytes, canonical inventory SHA-256
`b0e2c584d854ecfba7be36d9273f9bb9cb78f34d7545f41616bd425f5c70aca4`.
Its main database is 68,665,344 bytes, SHA-256
`c947c9d9e0c460242f0e2d49df189796f81a0c32dc5acc133a767f8b45d2344e`.
The [manifest](../../tools/cohort-specs/plane-controller-event-argument.manifest.tsv)
and [spec](../../tools/cohort-specs/plane-controller-event-argument.spec.tsv)
correct the existing function at `0x004d21c0` to an ECX receiver and one
stack event argument. The return remains `undefined`; name, body, comments
and tags are unchanged. Both disputed wing-helper call sites were already
inside its saved body, so the old missing-boundary note was corrected.

Fresh PRE identity, isolated apply/readback, independent review, refusal
controls, sealed rehearsal, live apply and separate readback passed.
All 8,329 other function rows, all program metrics, non-target variable rows,
type/bookmark definitions and all saved stack-purge metadata stayed identical.
Full live exports equal the sealed rehearsal. The decompiler still emits
incorrect return-address/local-vector expressions; the [controller evidence](../binary-analysis/functions/CComplexThing.cpp.md)
records this separate analysis limit. A corrected prototype is not a complete
semantic audit or a runtime-parity claim.

Evidence is under `local-lab/ghidra-first-training-20260907-v1/aircraft-audit-20260912/plane-event-argument/`.
`live-readback.json` is 2,431 bytes, SHA-256
`bff707a4e950aaf2faa126225999a737cae51faba769c738c4fffb07b795d439`.
The preceding air-contact POST was freshly restore-proven and matched PRE.
The new independent POST is
`/srv/archive-a/onslaught-ghidra-cold/2026-09-12-plane-controller-event-argument/post-working/`;
its copy and separate restore/reopen passed with no file mismatch.
`post-working-restore.json` is 5,817 bytes, SHA-256
`1d87e5fc25c6098b44e29f35ebdaf40d0768524263a49f2704107fde584a46d8`.
The tracked checkpoint's two retained main database files were freshly
hash-matched before and after; neither was opened or refreshed. Names did not
change, so the existing documentation-name projection remains valid.

## Script callback arguments (2026-09-12)

After this cohort the working project measured `db.18643`: 18 payload files,
118,967,156 bytes, inventory SHA-256
`dd3c65b9a3c014b97320fbcba63145d81c6ba0c8f03b9baf5c006c5483ee0b59`.
Its main database is 68,665,344 bytes, SHA-256
`32e5f75743396b79b2e4afb388061dfceb9348bed0351ca2dc2c0a2594bc3dea`.
The [manifest](../../tools/cohort-specs/script-callback-arguments.manifest.tsv)
and [spec](../../tools/cohort-specs/script-callback-arguments.spec.tsv)
correct only the prototypes of `SetSpawnScript` (`00535ca0`) and
`IScript__SetAIState` (`005361a0`). The [script owner](../binary-analysis/functions/IScript.cpp.md#native-callback-transport--september-12-static-audit)
binds ECX plus arguments/count/output stack slots to the retail dispatcher.
Return types remain `undefined`. Native `RET 0ch` and declared parameter size
12 are separate from saved stack-purge values, which remain UNKNOWN.

Isolated and sealed apply/readback, independent raw and metadata review,
stale-second-row refusal before any write, live apply and separate readback
passed. Exactly eight parameter rows were added; all 8,328 other function
rows, non-target variables, all program metrics, types, bookmarks and saved
purge metadata stayed unchanged. Full live exports equal the sealed rehearsal.
Evidence is under `local-lab/ghidra-first-training-20260907-v1/aircraft-audit-20260912/script-callback-arguments/`.
`live-readback.json` is 2,414 bytes, SHA-256
`714542c62200d7fe126ebdba26eeb84c86bdc09c34a37e5f7a87ddcd82a08213`.

The preceding Plane-argument POST was restore-proven and matched PRE.
The new independent POST is
`/srv/archive-a/onslaught-ghidra-cold/2026-09-12-script-callback-arguments/post-working/`.
Copy, separate restore and read-only reopen passed with no file mismatch.
`post-working-restore.json` is 5,821 bytes, SHA-256
`6cecf1ad5379b50332f8ea0d8ae68805b1e8d4731e460a7e77231f882b36a962`.
Both retained main files in the tracked checkpoint still match their hashes;
no checkpoint was opened or refreshed. Names and their projection are unchanged.

## Weapon provider semantics (2026-09-12)

The working project measures `db.18644`: 18 payload files,
118,983,540 bytes, inventory SHA-256
`bfb9caa7054ee25558de39906045c0dde3270e80db37d3425d0ba330bfa24294`.
Its main database is 68,681,728 bytes, SHA-256
`632465da170914893e24e026284ae05a7ecfa4b46a651ebf2808c1343f3ba4a7`.
The [manifest](../../tools/cohort-specs/weapon-provider-semantics.manifest.tsv)
and [spec](../../tools/cohort-specs/weapon-provider-semantics.spec.tsv) correct
five descriptive names, nonrepeatable comments and semantic tag sets:
the Unit attack-provider selector, Weapon readiness, two raw mask intersections
and the incomplete-burst predicate. The [Unit evidence](../binary-analysis/functions/CComplexThing.cpp.md)
separates static ownership from bounded original-code execution. These are
descriptive corrections, not recovered original source spellings.

Exact manifest and independent full-metadata review, isolated and sealed
apply/readback, stale-fifth-row refusal, live dry/apply and separate readback
passed. All 8,325 non-target rows remain identical. Target signatures change
only their displayed function names; bodies, ABI, variables, types, bookmarks,
repeatable comments and saved stack metadata remain unchanged. Only the
program-wide comment digest changes. All eight live exports equal the sealed
rehearsal. The current-name checker composes this manifest with its prior
overlays; frozen name tables remain unchanged.

Evidence is under
`local-lab/ghidra-first-training-20260907-v1/aircraft-audit-20260912/weapon-provider-semantics/`.
`live-readback.json` is 2,319 bytes, SHA-256
`c49d8928fa1efd9fcbe250b9523ab0e2d68fca20d75ec1f45d1a73d54c066448`.
The preceding script-callback POST matched PRE and was freshly restored and
reopened read-only. New independent POST recovery is
`/srv/archive-a/onslaught-ghidra-cold/2026-09-12-weapon-provider-semantics/post-working/`.
Copy, separate restore and read-only reopen passed without file mismatches;
`post-working-restore.json` is 5,787 bytes, SHA-256
`67305bd0ab9c89eb59860df956837d60e901032bbe6870b5cfa4722a842ee7f9`.
The tracked checkpoint was freshly hash-compared and remains unchanged.

## UnitAI initializer and event arguments (2026-09-12)

Two sequential, independently preserved cohorts correct three existing rows:

| Cohort | Exact change |
| --- | --- |
| [Initializer manifest](../../tools/cohort-specs/unit-ai-initializer.manifest.tsv), [spec](../../tools/cohort-specs/unit-ai-initializer.spec.tsv) | `004fe710`: `CWarspite__Init` → `CUnitAI__Init`, nonrepeatable comment and one tag substitution. RTTI identifies the shared base; its ABI is unchanged. |
| [Event-argument manifest](../../tools/cohort-specs/unit-ai-event-arguments.manifest.tsv), [spec](../../tools/cohort-specs/unit-ai-event-arguments.spec.tsv) | `004ff330`: integer argument → opaque event pointer named `eventRecord`; `004ffbb0`: existing pointer renamed from `candidate` to `eventRecord`. Both nonrepeatable comments corrected; names, tags and provisional `int` returns retained. |

The initializer produced working `db.18645`; the event-argument cohort produced
`db.18646`. The final working payload has 18 files, 118,983,540 bytes, inventory
SHA-256 `9d8a4d34275898513705a1aed5205ba58cab70112d4b17c45cc0d756ffe43b7e`.
Its main database is 68,681,728 bytes, SHA-256
`0f945c759cb0e993c45c22c229dc99d5a5b1b86e5aee8b8bcee7b616f58ec626`.

Exact body/RTTI/comment review, isolated apply, separate full comparison, sealed
readback, live dry/apply and separate live readback passed for each cohort.
All eight live exports match the corresponding rehearsal. The initializer
preserves 8,329 other rows and every ABI field; the event cohort preserves 8,328
other rows and changes only two explicit parameter rows. Types, bookmarks,
saved stack/frame data and program structure remain unchanged. At program
scope only the comment digest moves. No runtime-parity or recovered-source-name
claim follows from these metadata corrections.

Evidence owners are the `unit-ai-initializer/` and `unit-ai-event-arguments/`
children of `local-lab/ghidra-first-training-20260907-v1/aircraft-audit-20260912/`.
Each contains the exact commands, manifests, full exports, comparison and
recovery receipts. The preceding weapon-provider POST was freshly restored
and matched initializer PRE. New independent POST copies are
`/srv/archive-a/onslaught-ghidra-cold/2026-09-12-unit-ai-initializer/post-working/`
and `/srv/archive-a/onslaught-ghidra-cold/2026-09-12-unit-ai-event-arguments/post-working/`.
Both were hash-compared, restored elsewhere and reopened read-only; the first
then served as the second cohort's matching PRE. The tracked checkpoint stayed
byte-identical throughout. Current name projection composes the initializer
manifest; dated tables remain frozen.

## UnitAI exit contract comment (2026-09-12)

The [manifest](../../tools/cohort-specs/unit-ai-exit-contract.manifest.tsv) and
[spec](../../tools/cohort-specs/unit-ai-exit-contract.spec.tsv) change only the
nonrepeatable comment at `004ffbb0`: GetVulnerable, the distinct CST collision-ignore
pointer, and GoTo's TRUE override. Names, ABI, tags, repeatable comments and bodies
remain unchanged. The [Unit evidence](../binary-analysis/functions/CComplexThing.cpp.md#aircraft-spawner-exit-and-script-readiness--september-12)
owns the static and composed original-code witnesses.

Working POST measures `db.18647`: 18 files, 118,983,540 bytes, inventory SHA-256
`b14df79459f8bb857163075f63b3fcb76946f336f8dcb4f1797c89248be8086e`.
Its main database is 68,681,728 bytes, SHA-256
`6ca29ea137989ab18776a495c5629fbc317da98d546aa5ac28f76ab8c28073f8`.
Isolated dry/apply, sealed separate readback and independent metadata comparison,
then live dry/apply/readback passed. All eight live exports equal rehearsal;
8,329 other function rows and every variable/type/bookmark/stack export hold.
Only the target comment and program comments digest change.

Evidence is in the `unit-ai-exit-contract/` child of
`local-lab/ghidra-first-training-20260907-v1/aircraft-audit-20260912/`.
`live-readback.json` is 2,250 bytes, SHA-256
`943858aa7cb15af1ab0c0f9d726139e341cf61f4cc7a79211d0cd5391d280736`.
The preceding event-argument POST was freshly matched, restored and reopened as PRE.
The new independent POST is
`/srv/archive-a/onslaught-ghidra-cold/2026-09-12-unit-ai-exit-contract/post-working/`.
Copy, separate restore and read-only reopen passed without file mismatches;
`post-working-restore.json` is 5,775 bytes, SHA-256
`af60ead07bfa8c2cd09050b79e10ada8e3849ca2ca760fd2309d150a7a260f9e`.
The full tracked checkpoint payload still matches its recorded inventory.
No checkpoint refresh, name-projection change or runtime-parity claim follows.

## Aim-provider metadata correction (2026-09-19)

The exact [manifest](../../tools/cohort-specs/aim-provider-semantics.manifest.tsv)
and [spec](../../tools/cohort-specs/aim-provider-semantics.spec.tsv) correct these
four function names, nonrepeatable comments and semantic tags:

| Address | Previous name | Corrected name | Native return |
| --- | --- | --- | --- |
| `00404120` | `CAnimal__CopyVector7CToOut` | `CActor__GetVelocity` | `void *`, EAX output buffer |
| `00445070` | `CDiveBomber__SelectTarget` | `CDestructableSegmentsController__GetAimPosition` | `void`, unchanged |
| `004fd4d0` | `CUnit__SelectTarget` | `CUnit__GetAimPosition` | `void`, unchanged |
| `0050a0e0` | `OID__ComputeForwardProjectedPointTowardTarget` | `CWeapon__ComputeTargetAimPoint` | `void *`, EAX output buffer |

The two pointer returns express observed native output-buffer ABI, not original
C++ pointer-return declarations. All formal parameters and locals remain intact.
[Provider ownership and ordered part selection](../binary-analysis/functions/DiveBomber.cpp/CDiveBomber__SelectTarget.md)
and [endpoint prediction](../binary-analysis/functions/CComplexThing.cpp.md#target-point-providers-and-weapon-prediction)
own the static and isolated-execution findings and their limits.

Fresh PRE matched the independent September 12 exit-contract recovery, which was
restored and reopened read-only. Rehearsal dry/apply, separate readback and an
independent comparison passed: exactly four of 8,330 internal function rows,
two return records among 32,697 variable records, and only the program comment
digest changed. Types, bookmarks, saved stack, Plane-depth and all 239 selected
instructions remain unchanged. A stale-PRE dry control refused before writes.
The sealed live dry/apply/separate-readback passed; all nine exports match the
reviewed rehearsal byte-for-byte.

Measured working POST is `db.18648`: 18 files / 118,983,540 bytes, inventory
SHA-256 `2176c30bd69c5b2be5ba60beae1498491f4df4b7f4eefed75608031c6afe823b`.
The main database is 68,681,728 bytes, SHA-256
`16f40a8a8c3f2bd2b4260939f873d55d186456b782d1bd7493c1e77e51d41025`.
Independent POST recovery at
`/srv/archive-a/onslaught-ghidra-cold/2026-09-19-aim-provider-semantics/post-working/`
was copied, hash-compared, restored elsewhere and reopened read-only successfully.
The tracked checkpoint payload is unchanged; it was not writable-opened.

Receipts and exports are in
`local-lab/ghidra-first-training-20260907-v1/aircraft-audit-20260919/aim-provider-semantics/`.
`live-readback.json`: 2,402 bytes, SHA-256
`f01d3a76a8b5f147bc2a032a9af986df82093f3318218d25f49e3a512ba36e6f`.
`post-working-restore.json`: 5,778 bytes, SHA-256
`6fd0bc9a4ce89fd5b9958b97135a1e51fff4706cc9bb7c8c7724328a4e293883`.
This corrects analysis metadata; it does not establish retail gameplay acceptance.

## Asin-helper metadata correction (2026-09-19)

The exact [manifest](../../tools/cohort-specs/asin-helper-semantics.manifest.tsv)
and [spec](../../tools/cohort-specs/asin-helper-semantics.spec.tsv) correct two
misleading names, nonrepeatable comments and semantic tags:

| Address | Previous name | Corrected name |
| --- | --- | --- |
| `0055dcb0` | `CRT__AcosDispatch_ST0` | `CRT__AsinDispatch_ST0` |
| `0055dccd` | `CRT__Acos` | `CRT__AsinCoreWithFpuGuards` |

The [Weapon B finite experiment](../binary-analysis/functions/CComplexThing.cpp.md#weapon-b-finite-elevation-and-arithmetic-boundaries)
executes the original helper closure and establishes signed elevation behavior
under its supplied inputs and floating-point state. The wrapper classifies a
saved double copy while the core uses retained ST0 for arithmetic. Comments
distinguish these paths, and obsolete verified-signature tags are removed.
All prototypes and parameter/local storage remain frozen and explicitly
unresolved. This does not repair the shared error helper at `00561547` or define
the alternate entry at `0055dcc4`; those require separate structural/ABI work.

Fresh PRE matched the independent aim-provider POST above and was restored and
opened read-only. The final rehearsal and independent comparison changed only
two of 8,330 internal function rows. All 32,697 variable records, types,
bookmarks, saved stack, Plane-depth and the 54 selected instructions/194 bytes
remain unchanged; only the program comment digest moves. A stale second-row
comment control refused before writes. Sealed readback, live dry/apply and a
separate readback passed. All nine live exports equal the reviewed rehearsal.

Measured working POST is `db.18649`: 18 files / 118,983,540 bytes, inventory
SHA-256 `a38825aab32f3741d826740381c19284c6f79f44ac830618cf831482ef342345`.
The main database is 68,681,728 bytes, SHA-256
`ed633e07053ad8e51104842cf6e2124da449160a34207ab2c47b9382a63e8591`.
Independent POST at
`/srv/archive-a/onslaught-ghidra-cold/2026-09-19-asin-helper-semantics/post-working/`
was copied, hash-compared, restored elsewhere and reopened read-only. The tracked
checkpoint payload remains byte-identical and was not writable-opened.

Commands, comparisons and receipts are in
`local-lab/ghidra-first-training-20260907-v1/aircraft-audit-20260919/asin-helper-semantics/`.
`live-readback.json`: 2,306 bytes, SHA-256
`d8d8ca16a4a4df45e4eca52c9184a8a3e80a4ed15ffe69d6670801fb07a49bde`.
`post-working-restore.json`: 5,773 bytes, SHA-256
`e42a86cf77d6b115c28435e529a96fda0d30a980cc77b6e4dd439bebd8a3625f`.
This is an analysis correction, not retail gameplay or full math-library acceptance.

## Shared math-error ABI correction (2026-09-19)

The working project now measures `db.18650`: 18 payload files, 118,999,924 bytes,
inventory SHA-256
`dc3df9fdb2cc9c390f70421e47f2a25ecbcb18db5f8adcbb6763140a3a305c65`.
Its main database is 68,698,112 bytes, SHA-256
`f750ca22556143ee48fb2075f0715f4620e12ecb1b354e718b50b85c5ade86ec`.
The [manifest](../../tools/cohort-specs/math-error-custom-abi.manifest.tsv) and
[spec](../../tools/cohort-specs/math-error-custom-abi.spec.tsv) correct only
`00561547`'s prototype, nonrepeatable comment and tags. Its retained name is
`__startOneArgErrorHandling`. The physical ABI uses EAX, EDX, ECX and ST0 plus
the two actual enclosing-frame arguments at stack offsets `+4` and `+c`, with
ST0 return and zero purge. It removes the invented hidden-result pointer and
keeps the enclosing return-address slot out of the parameter list.

The [contract and original-code controls](../binary-analysis/functions/CComplexThing.cpp.md#shared-unary-math-error-bridge)
distinguish the `float10` register carrier from the binary64 spill/reload.
Eight controlled calls establish the observed bridge behavior; they do not
validate the actual CRT dispatcher, exceptional inputs, Windows or gameplay.
The related record-type model, sibling ABI and outer entries remain separate.

The existing framework now supports explicitly pinned custom storage. Its
92 tests passed, as did ten actual-database refusals before writes and three
datatype-comment controls. The fresh independent PRE matched working exactly,
was restored elsewhere and reopened read-only. Isolated dry/apply/separate
readback, independent full review and the sealed repetition all passed.
Live dry/apply/separate readback equals that rehearsal in all nine exports.
Only the declared function row changes; all 8,329 others, every local variable,
type definition, body, byte, bookmark and saved stack offset remain unchanged.
The removed auto parameter reduces saved variable records by one. Only the
comment digest changes among 29 program metrics. Exact ABI and protected-state
pins also cover storage, hidden/indirect flags, local first-use offsets,
unrelated external functions and datatype metadata omitted by rendered text.

PRE recovery is the verified asin-helper POST above. New independent POST is
`/srv/archive-a/onslaught-ghidra-cold/2026-09-19-math-error-custom-abi/post-working/`.
It was copied, hash-compared, independently restored and opened read-only;
the restored bytes equal working. The tracked checkpoint remains the exact
`745c00ad…` payload; no refresh occurred. Commands and comparisons belong to
`local-lab/ghidra-first-training-20260907-v1/aircraft-audit-20260919/math-error-abi/promotion/`.
`live-readback.json`: 2,490 bytes, SHA-256
`f426dfc5ac9a8e93a93f0fadf52ab8e93d0a7b09d3fdcddcd915de61ec92d456`.
`post-working-restore.json`: 5,779 bytes, SHA-256
`c89ebc6389d77a9465759f1f174610727df56d3923bdd6577877f402d5f1a999`.

## Renderer arguments and shared return-4 correction (2026-09-19)

Two sequential, independently recovered cohorts correct the three functions
used by the [selected-round registry investigation](../binary-analysis/functions/Actor.cpp.md#selected-round-renderer-admission).
The [argument manifest](../../tools/cohort-specs/render-registry-arguments.manifest.tsv)
and [spec](../../tools/cohort-specs/render-registry-arguments.spec.tsv) correct
`004f35d0` to `void __thiscall CThing__InitRenderThing(void *this, void *init)`:
ECX carries the receiver, the unused initializer occupies stack `+4`, and the
callee purges four bytes. `005164b0` retains its existing name, return type and
cdecl convention, with arguments `int class_id, void *render_interface`.
Its old descriptor-table/owner-tag parameter labels described the wrong inputs.
Both receive evidence-bound nonrepeatable comments and additive tags.

The first POST measured `db.18651`: 18 files, 118,999,924 bytes, inventory SHA-256
`122c67e9919e250b2b8515973f980e4b4dcde4c49dc1fee4e456f5e05236e8d6`.
The main database was 68,698,112 bytes, SHA-256
`1f4b7eb5472ee7cef522515a5e260e9c7c1f0ac7498fbdd2a1f48578cd456d36`.
Exactly two function rows changed; 8,328 did not. The recovered initializer
adds one parameter record; all locals and returns remain unchanged.

The [leaf manifest](../../tools/cohort-specs/shared-return4-leaf.manifest.tsv)
and [spec](../../tools/cohort-specs/shared-return4-leaf.spec.tsv) then rename
`004db8c0` from `CPhysicsScriptValue__GetScalarSerializedSize4` to
`SharedVFunc__Return4_004db8c0`, with contextual comment and additive tags.
Its two instructions return 4 at 166 RTTI-resolved vtable slots, including
Round's object ID and several unrelated meanings. The former name remains
valid context for some PhysicsScript callers, not a unique implementation owner.
The existing prototype/storage are preserved: a leaf that reads no arguments
cannot distinguish thiscall from fastcall. All 8,329 other function rows and
every variable record remain unchanged.

The final working project measures `db.18652`: 18 files, 118,999,924 bytes,
inventory SHA-256
`4f82e35962a3db179afa71da1ee4712017b16cb89d6e87bf27d3f8c0eec98830`.
Its main database is 68,698,112 bytes, SHA-256
`600baa3b1fd9ef97634e047320fc70ba9e69ba3d41e8183f8634eb41ac5355d9`.
Each cohort passed restored PRE, isolated dry/apply/separate readback,
independent full comparison, live dry/apply/separate readback and independent
POST restore. Each live result equals its rehearsal in all nine exports.
Final spec pins were sealed from those measured rehearsals before live work;
no second sealed rehearsal is claimed. Across both cohorts, types, locals,
bookmarks, saved stack offsets, instructions, bytes and function boundaries
are unchanged; only the comment digest moves among 29 program metrics.
The framework implementation is unchanged; its live allowlist admits these
two manifests, and all 92 focused framework tests passed.

Independent POST copies are
`/srv/archive-a/onslaught-ghidra-cold/2026-09-19-render-registry-arguments/post-working/`
and `/srv/archive-a/onslaught-ghidra-cold/2026-09-19-shared-return4-leaf/post-working/`.
The verified math-error POST served as the first PRE, and the restored argument
POST as the second. Each new cold copy was hash-compared, restored elsewhere
and reopened read-only. The tracked checkpoint still matches `745c00ad…`;
no refresh occurred. Evidence and commands belong to
`local-lab/ghidra-first-training-20260907-v1/aircraft-audit-20260919/round-render-registry/`:

| Receipt | Bytes | SHA-256 |
| --- | ---: | --- |
| `arguments-live-readback.json` | 2,395 | `f75e3ccea72ed342fba3f76fbf06cffcfc26a543c8eef4428b92b8cc142a0386` |
| `arguments-post-restore.json` | 5,799 | `53b5ee067709899330329813d7a1736b06417a842cfb81da3c321e30ff88679b` |
| `leaf-live-readback.json` | 2,300 | `ce2bb08babf1602053905505f1c94ad9ed946ff3028b52c3f6df9a36f4c68d03` |
| `leaf-post-restore.json` | 5,778 | `2c7337330c05a9d58b63026ed22072610253ec505f1acd08f2c3bd938a66df9b` |

The current-name projection now includes the neutral leaf manifest. Frozen
tables and explicit-table consumers remain unchanged. These metadata repairs
and the 22 isolated registry cases do not establish complete shot ordering,
renderer execution or player-observed parity.

## Scheduled-event constructor boundary (2026-09-19)

The [manifest](../../tools/cohort-specs/scheduled-event-constructor-boundary.manifest.tsv)
and [spec](../../tools/cohort-specs/scheduled-event-constructor-boundary.spec.tsv)
create exactly one default function, `FUN_0044b190`, over existing instructions
at `[0044b190,0044b1d0)`: 64 bytes, 15 instructions, pristine body SHA-256
`ac037f0505dbe8d73f87d932a80e3bfd59551027bb49926cd041dccefe391adc`.
Fresh read-only inspection found no function owner for these instructions.
Scheduler Init supplies this literal callback to construct 20,000 records
of size `0x14`; the iterator supplies each record in ECX. The body clears only
target `+0` and payload `+0c`, increments the construction count, and restores
its exception linkage before returning. Source and byte evidence belong to
the [scheduler owner](../binary-analysis/functions/CEventManager.cpp.md).
Its semantic role does not establish a complete prototype: the new function
retains default name, undefined return, unknown calling convention, no formal
arguments, no comments and no tags.

The working project now measures `db.18653`: 18 files, 118,999,924 bytes,
inventory SHA-256
`867862c7ef056d685ce8cdf622da83e2e85a1e5bcb2b66d850048c11989c8e0e`.
The main database is 68,698,112 bytes, SHA-256
`879afcf636bc5305cac2304e16e7a8b26f5a28462ce315e57b817708f65cb871`.
All 8,330 prior function rows, 32,697 prior variable records and prior stack
records are unchanged. The new function contributes only its default return
and unknown-purge stack records. Types, bookmarks and saved Plane stack-depth
observations remain identical. Of 29 program metrics, only the internal
function count changes, to 8,331; instructions, bytes, references, data and
existing metadata are preserved. The open probe reports 8,555 including
224 external functions, a different count from the internal inventory.

The preceding shared-leaf POST matched working bytes and was restored/opened
as PRE. Isolated dry/apply/separate readback and independent comparison passed;
wrong-hash and clipped-final-RET controls both failed before writes with an
unchanged replica. Final spec pins were sealed from that separately reopened
rehearsal; no second sealed rehearsal is claimed. Live dry/apply/separate
readback passed, and all nine live exports equal rehearsal exports exactly.
The unchanged base framework and derived live allowlist passed 92 tests.

The new independent recovery is
`/srv/archive-a/onslaught-ghidra-cold/2026-09-19-scheduled-event-constructor/post-working/`.
It was copied, hash-compared, restored elsewhere and opened read-only; the
restored payload is stable and matches the working project. The tracked
checkpoint still matches `745c00ad…`; no checkpoint refresh occurred.
Commands and evidence are in
`local-lab/ghidra-first-training-20260907-v1/aircraft-audit-20260919/event-constructor-boundary/`:

| Receipt | Bytes | SHA-256 |
| --- | ---: | --- |
| `live-readback.json` | 2,286 | `39ae2910f25fcc99f18f061d36bce51f170876ab712291332f9715e6d6d2300a` |
| `post-restore.json` | 5,767 | `238e5af4d7bc2b7b631599748e85260ced3846b38b240606552f7957643b374b` |

The current-name checker composes this second default-function manifest with
its existing overlays, preserving frozen tables and explicit-table consumers.
This closes a demonstrated analysis boundary gap; no retail execution,
complete scheduler audit or reconstruction parity is claimed.

Related (not this folder):

| Role | Path |
| --- | --- |
| Expedition ops (ignored repo-local lab) | `local-lab/ghidra-fullpass-2026-07-23/` in the canonical checkout (runbook, state, corrections) |
| Wave discovery notes (tracked) | `reverse-engineering/binary-analysis/ghidra-fullpass-findings/` |
| Isolated Xbox oracle evidence | `local-lab/xbox-sparse-symbol-ghidra-20260812-v1/` in the canonical checkout (exports/receipts remain; project databases are restored only through the sealed external catalog, not used as PC live owners) |
| Mutable Linux PC project | `local-lab/ghidra-projects/BEA/` in the canonical checkout (Ghidra 12.1.3, owner `xsniper80`; measured version above) |
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

## Debug-log metadata — September 19

The [manifest](../../tools/cohort-specs/debug-log-metadata.manifest.tsv) and
[spec](../../tools/cohort-specs/debug-log-metadata.spec.tsv) correct exactly five
names, nonrepeatable comments and tag sets. Four functions at `004416e0`,
`00441740`, `004418a0` and `004419e0` now identify `CDebugLog` history/reset,
formatting and rendering. The generic store at `00441730` has the neutral name
`StoreField04_00441730`; its known setup-history use does not establish an
exclusive class owner. RTTI, initialization, output gating and evidence limits
are documented in the [logger contract](../binary-analysis/functions/string-helpers.md#debug-log-ownership-and-history--september-19).

All 8,326 non-target functions and every prototype, variadic flag, parameter,
local, type, stack record, function body and instruction remain unchanged.
The old parameter spelling `console` remains intentionally frozen. The full
program export changes only `commentsSha256`; all nine live exports equal the
separately reopened final rehearsal. The default constructor boundary from the
preceding cohort remains present; internal function count stays 8,331.

PRE was the freshly matched and restored scheduled-event-constructor POST.
Isolated rehearsal, stale-comment/name-collision refusals, independent review,
live dry/apply/separate readback and independent POST recovery passed. Review
narrowed two comments before live application; the original and revised
rehearsals remain preserved. An initial census with missing column bindings
refused before writes; the corrected census passed and the replica remained
unchanged. This is not a new full-game semantic audit or runtime acceptance.

Working identity: `db.18654`, 18 files / 118,999,924 bytes,
inventory SHA-256 `09872845704237ea08b32e678aad961510f0e20756e10229b27774c1594b6326`; main database
68,698,112 bytes, SHA-256 `c3c294fa7b94b3f64e03b34d32feca928b57eeda80d98e865081641802681df7`.
Independent POST: `/srv/archive-a/onslaught-ghidra-cold/2026-09-19-debug-log-metadata/post-working`. It was copied, hash-compared, restored elsewhere
and reopened read-only. The tracked `db.18634` checkpoint remains exactly
`745c00ad…`; no refresh occurred.

Private evidence owner:
`local-lab/ghidra-first-training-20260907-v1/aircraft-audit-20260919/debug-log-metadata/`.
`live-readback.json`: 2,298 bytes, SHA-256 `9bad6511c12e60a5f07f742a93ae420d0833c8c0b3bd10060bceafe9ac66aa78`.
`post-restore.json`: 5,742 bytes, SHA-256 `9edea84ddd1f2be128a4c9107109aa1694616d9b1ec1c82e3a2f1707c98e274d`.
Current name projection uses this manifest; frozen logger census tools,
explicit name tables and historical receipt schemas remain unchanged.

## CLI initializer ownership — September 19

The [manifest](../../tools/cohort-specs/cli-initializer-ownership.manifest.tsv) and
[spec](../../tools/cohort-specs/cli-initializer-ownership.spec.tsv) correct exactly
one name, nonrepeatable comment and tag set: `004239f0` is now
`CLIParams__InitDefaults`. Its startup wrapper and WinMain/parser share the
same receiver; the previous Unit AI ownership and missing-caller-boundary
claims were wrong. Complete byte and isolated execution evidence belongs to
the [CLI owner](../binary-analysis/functions/CLIParams.cpp/CLIParams__ParseCommandLine.md).

All 8,330 other function rows and all ABI, parameters, locals, types, stack
records, instructions and bodies remain unchanged. The target's displayed
signature changes only its name. Of 825 exported instruction rows, 113 change
only the displayed initializer name. Only `commentsSha256` moves among the
program metrics. All nine live exports exactly match the separately reopened
rehearsal; the internal function count remains 8,331.

Fresh PRE equality and restored read-only opening, isolated dry/apply/separate
readback, two stale-comment/name-collision refusals, independent exact-cohort
review, live dry/apply/separate readback and independent POST recovery passed.
The first dry invocation used unsupported mode `dry-run` and refused before
writes; the replica remained byte-identical and the corrected `dry` route
passed. Final spec pins came from the measured rehearsal; no second sealed
rehearsal is claimed. The unchanged base framework and extended live allowance
passed 92 focused tests. Four isolated initializer cases are separate from
the complete static parser audit; no full parser or retail runtime acceptance
is claimed.

Working identity: `db.18655`, 18 files / 118,999,924 bytes,
inventory SHA-256 `5d1f226fc00b44409429edbdb53e2f57ec8d98e16fb1ff7a3add6e1782fb4f31`; main database
68,698,112 bytes, SHA-256 `38577307e6858ecbd3ad72fb43f7f6f371bf8e406a7475ab5aa43bbde0481bb3`.
PRE was the freshly matched debug-log POST. Independent POST:
`/srv/archive-a/onslaught-ghidra-cold/2026-09-19-cli-initializer-ownership/post-working`.
It was copied, hash-compared, restored elsewhere and reopened read-only.
The reviewed tracked checkpoint remains exactly `745c00ad…`; no refresh.

Private owner: `local-lab/ghidra-first-training-20260907-v1/aircraft-audit-20260919/cli-initializer-ownership/`.
`live-readback.json`: 2,318 bytes, SHA-256 `c466a5dc45e2e238880aa50e098481f00f8e9e630cd7520f76618e3b4d07b91e`.
`post-restore.json`: 5,763 bytes, SHA-256 `cac2d9e1f3ff7287899c019b9ceed3edea68ff783c2d773fe48ed8d580d7a53d`.
The current name projection composes the exact new manifest; frozen tables and
historical receipts remain unchanged.

## Sample-loading metadata — September 22

The [loading manifest](../../tools/cohort-specs/audio-sample-loading.manifest.tsv)
and [spec](../../tools/cohort-specs/audio-sample-loading.spec.tsv) correct
`00517290` to `CPCSoundManager__LoadNewSample_StubFail` and `005172a0` to
`CPCSoundManager__LoadSampleFromBuffer`, with their filename/music parameter
names. The [parameter manifest](../../tools/cohort-specs/audio-sample-parameters.manifest.tsv)
and [spec](../../tools/cohort-specs/audio-sample-parameters.spec.tsv) rename
the outer CreateSample music argument and bank-loader reuse argument. All four
comments/tag sets now distinguish pristine instructions, isolated execution,
source-drop differences and unexecuted device/lifetime behavior. The
[compatibility contract](../binary-analysis/save-options-static-review-2026-05-26.md#outer-sample-admission-and-registration)
owns the behavioral evidence.

Exactly two loader names, four formal parameter names, four nonrepeatable comments and four tag sets corrected. All return/parameter types, calling conventions, storage, locals, stack cleanup, type definitions, instructions, bodies and the 8,327 non-target function rows are preserved.
All 32,694 other variable rows are unchanged. Of 413 selected instruction rows,
only displayed function names change. Only `commentsSha256` moves among program
metrics. All nine live exports exactly equal the separately reopened rehearsal;
the internal function count remains 8,331.

Fresh independent PRE equality and restored read-only opening, both isolated
dry/apply/separate readbacks, sealed-spec readbacks, wrong-comment/extent
read-only refusals, independent exact-cohort review, live dry/apply/separate
readbacks and independent POST restore passed. Final POST pins came from the
measured rehearsal; the later spec addition admits only the derived live
applier hash. The shared framework preserves the bank's one-byte `char` extent
and four-byte purge. Its narrow existing-shape exception passed a proxy positive
and 16 negatives within 93 focused tests; actual database exports establish the
unchanged storage. Review corrected a draft stub-control count and clarified
bounded name copying before their respective rehearsal applies.

Working identity: `db.18657`, 18 files / 119,016,308 bytes,
inventory SHA-256 `188003d0a677a5db5b99eac870a343530422bfe81bebf4c8568896254916aba7`; main database
68,714,496 bytes, SHA-256 `ebc06917631cf137aad8bd6c77827f7d278c0b27181336037a19c26d94807d36`.
PRE was the freshly matched CLI-initializer POST. Independent POST:
`/srv/archive-a/onslaught-ghidra-cold/2026-09-22-audio-sample-loading/post-working`.
It was copied, hash-compared, restored elsewhere and reopened read-only.
The reviewed tracked checkpoint remains exactly `745c00ad…`; no refresh.

Private owner: `local-lab/ghidra-first-training-20260907-v1/aircraft-audit-20260919/audio-sample-loading/`.
`completion.json` records the exact live readbacks, recovery receipts and full
export hashes. Current name lookup composes the new manifest; frozen tables
and historical receipts remain unchanged.

## RE-audit GenericSPtrSet identities — September 27

The [fourteen-row manifest](../../tools/cohort-specs/sptrset-identities-20260927.manifest.tsv) and
[spec](../../tools/cohort-specs/sptrset-identities-20260927.spec.tsv) replace the historical
`CSPtrSet` labels with the source-proven `GenericSPtrSet` owner and method names.
The object constructor and static pool Init are distinguished; Add/Append and
RemoveAll take their actual source identities. Specimen SHA-256:
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.

Fourteen shared GenericSPtrSet names, comments and tag sets corrected from complete source/body/caller evidence. All saved interfaces, locals, stack layouts, 1,065 code bytes / 363 instructions, the separately named forwarding entry and 8,318 other function records remain unchanged.

The pinned GenericSPtrSet source owner matches complete target bodies, allocation anchors, node/pool layout and eleven complete caller spans. Two source-graph direct edges corroborate rather than establish the identities. Copy/assignment/search stop at null items, self-assignment clears its list, and RemoveAll leaves the iterator unchanged. Five source-parity tags are removed and exact prior comments remain qualified leads. No concrete template type, exhaustive alias identity, full ABI, allocator correctness or gameplay parity is claimed. An initial rehearsal caught an automatic forwarding-name mutation; its failed replica/seal remain preserved and the separate forwarding promotion precedes this successful rehearsal. No safety gate was relaxed.

All 4,707 earlier comment bytes remain qualified leads. Independent complete
body/caller and exact-payload reviews were reproduced by root. The reviewer
corrected a misleading stack-pointer phrase before this final seal. Fresh PRE
restoration, rehearsal, separate/sealed readbacks, five byte-stable refusal
controls, exact live readback and independently restored Archive A POST passed.
All nine live exports match rehearsal. The forwarding record, thunk association
and every interface remain unchanged; the original collateral failure is resolved.

The [list experiment](../../VALIDATION.md#original-pointer-list-operations--september-27)
separately ran five unchanged original bodies in 42 cases plus two altered-copy
controls. The career child/parent-link notes distinguish that execution from
static composition of their callers. Full career/save graphs, allocation
failure, invalid traversal, Windows exception handling and real gameplay remain
open. Seven target interfaces and their thunk dependency need a separate ABI
cohort; this name correction does not certify those saved signatures.

Working identity: `db.18705`, 18 files / 125,553,524 bytes,
inventory SHA-256 `013d44b5277c4ae0bbb54da2ac95de33a3d509fd106d99a7c78ae12d91333606`; main database 75,251,712 bytes,
SHA-256 `d0f22777d6026cbb874d44f5c3dfdfa30e321e0261d0d89691be6bfa89f4c8b6`. Restored forwarding-entry POST is PRE.
Independent POST: `/srv/archive-a/onslaught-ghidra-cold/2026-09-27-sptrset-identities/post-working`. Tracked checkpoint remains `745c00ad…`.
Private receipts: `local-lab/ghidra-first-training-20260907-v1/re-audit-20260926/sptrset-identities/`; logs:
`local-data/test-runs/re-audit-20260926/sptrset/identities-*`.

## RE-audit GenericSPtrSet forwarding entry — September 27

The [one-row manifest](../../tools/cohort-specs/sptrset-forwarder-20260927.manifest.tsv) and
[spec](../../tools/cohort-specs/sptrset-forwarder-20260927.spec.tsv) name the direct forwarding
entry `0042f220` as `GenericSPtrSet__RemoveAll_thunk`. Specimen SHA-256:
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.

One structural forwarding name, comment and tag set corrected at 0042f220. Its five-byte direct jump to 004e5c60, saved thunk association, complete interface, variables and all 8,331 other function records remain unchanged.

Fresh pristine instructions establish receiver/stack-neutral forwarding. Complete target-body/source/caller review identifies GenericSPtrSet::RemoveAll; the target itself is corrected only by a subsequent cohort. The name does not certify a concrete template instantiation, unique source wrapper or full target ABI. The prior DEFAULT name followed its target automatically; a disposable fourteen-row rehearsal caught that fifteenth mutation and refused it before any live change. The rejected evidence is retained. An explicit one-row forwarding name avoids changing the collision or collateral gates. All prior comment bytes remain qualified leads.

The exact 4,091-byte manifest was independently reviewed and reproduced by root.
All 616 old comment bytes and historical tags remain. Fresh PRE restoration,
rehearsal, separate/sealed readback, five byte-stable refusal controls, live
readback and independently restored Archive A POST passed. All nine live exports
match rehearsal. The exact comparator includes name-source promotion from
DEFAULT to USER_DEFINED; the target record and thunk association remain frozen.
The later fourteen-row rehearsal must independently confirm no follower change.

Working identity: `db.18704`, 18 files / 125,471,604 bytes,
inventory SHA-256 `c249dc325c2efff362472e5cde8fe9af09dcfb47cdd6f3f215fd4ea436598e8e`; main database 75,169,792 bytes,
SHA-256 `0f386541105ef23af0fa9fb91a418d5aa9b119f9395c99fede44777591bd4d3e`. Restored verified-music POST is PRE.
Independent POST: `/srv/archive-a/onslaught-ghidra-cold/2026-09-27-sptrset-forwarder/post-working`. Tracked checkpoint remains `745c00ad…`.
Private receipts: `local-lab/ghidra-first-training-20260907-v1/re-audit-20260926/sptrset-forwarder/`; logs:
`local-data/test-runs/re-audit-20260926/sptrset/forwarder-*`.

## RE-audit verified music records — September 27

The [eight-row manifest](../../tools/cohort-specs/music-verified-20260927.manifest.tsv) and
[spec](../../tools/cohort-specs/music-verified-20260927.spec.tsv) retain eight shared music names,
correct their plate notes and qualify tags. Specimen SHA-256:
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.

Eight existing shared-music names verified within complete static-body/source correspondence; only comments and tag sets change. Earlier notes remain qualified leads. All names, prototypes, variables, locals, frames, 1,432 code bytes / 542 instructions and 8,324 other function records stay unchanged.

All eight complete pristine bodies were freshly decoded and read against pinned Music.cpp/Music.h. The allocation file/line anchor, source-correlated device calls,selection switch table and concrete coefficient/string bytes support the stated identities and bounded behavior. This is not full ABI, device, filesystem, audible or runtime acceptance. The null-song assignment is source agreement, not divergence; SetVolume uses linear 127.0f then x87 FISTP with ambient rounding, not the non-PS2 tangent formula. Retail filename overrides remain distinct from unproved high-level meanings of their guard globals. Source-parity tags are removed; exact historical notes stay as fallible leads.

The notes distinguish strict fade thresholds, deferred target updates, actual
null-pointer stop branches, selection-state writes only on the immediate path,
playlist node ordering and unchecked filename copies. SetVolume has no local
clamp or device submission; Shutdown directly clears only the list head among
the three list/current/queued pointers. These are instruction/source findings,
not new executions of the older audio experiments.

Fresh PRE restoration, rehearsal, separate/sealed readbacks, five byte-stable
refusal controls, independent exact review with root reproduction, live readback
and independently restored Archive A POST passed. All nine live exports equal
rehearsal; every variable/stack/type/body record is preserved. All 8,332 names
match the unchanged production projection. Draft review caught ambiguous hex
notation and an overbroad empty-playlist claim before the manifest was sealed.

Working identity: `db.18703`, 18 files / 125,471,604 bytes,
inventory SHA-256 `93a4a060bbc46507e297e75cf0a4c9bbe251af88e80b873af7b69ef05cec4a43`; main database 75,169,792 bytes,
SHA-256 `b27f0a098edd9eb14fcf811e9fd4de92e04c80d8884e9bab3946607595e9d004`. Restored Thing gameplay interface POST is PRE.
Independent POST: `/srv/archive-a/onslaught-ghidra-cold/2026-09-27-music-verified/post-working`. Tracked checkpoint remains `745c00ad…`.
Private receipts: `local-lab/ghidra-first-training-20260907-v1/re-audit-20260926/music-verified/`; execution logs:
`local-data/test-runs/re-audit-20260926/music/verified-*`.

## RE-audit Thing gameplay interfaces — September 27

The [32-row manifest](../../tools/cohort-specs/thing-gameplay-abi-20260927.manifest.tsv) and
[spec](../../tools/cohort-specs/thing-gameplay-abi-20260927.spec.tsv) correct saved physical
interfaces in pristine `BEA.exe.original.backup`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.

Thirty-two Thing gameplay interfaces corrected: six scalar queries, sixteen Activate/Deactivate methods and ten Hit/Damage rows. Twenty-two explicit ECX receivers normalize to automatic thiscall. Five scalar predicates use int/EAX:4; CRound GetMaxVelocity uses source float with ST0:10 preserved. Void interface returns, opaque pointer and float/int argument types are made explicit. AirUnit and HiveBoss arguments gain interface-correct names; CTree Damage only changes elapsed_time to amount. All 3,299 body bytes / 1,035 instructions, names, argument stack locations/arity, 29 locals, frame sizes and 8,300 other function records are preserved.

Pinned thing.h declarations, complete source-correlated callers, the retail script registry and callback transport, complete target bodies and 103 raw RTTI uses support the selected interfaces. Original-code runs and retail/device observations were not performed for this static metadata cohort. Incidental EAX/x87 contents do not establish a source result; callback RET12 is not target argument cleanup. Unread Hit/Damage arguments remain present. Five full-EAX predicates are not narrowed to AL, and x87 float returns are not changed to ST0:4. Ten additional custom-storage floating rows remain outside this cohort because the current framework cannot express their source-type correction while preserving ST0:10. This is not full class-layout or derived-semantic certification. All older notes remain explicitly fallible leads.

The Tree Damage correction matters to reconstruction: the body subtracts damage
amount from its field, not elapsed time from a cooldown. It stores float32 before
comparing the still-held x87 result. Its initial field meaning, exceptional-float
behavior and callee effects remain separate questions. Only three local vector
words are initialized; no full four-word vector contract is asserted.

Fresh PRE restoration, rehearsal, separate/sealed readbacks, seven byte-stable
refusal controls, independent exact review with root reproduction, live readback
and independently restored Archive A POST passed. All nine live exports equal
rehearsal. Full variable comparison checks receiver-auto and declared return/type
changes, preserves every local/frame and rejects changes outside the cohort.
The current name projection is unchanged and equals all 8,332 live entries.
The initial comparator incorrectly expected USER_DEFINED provenance for fourteen
preserved `param_N` names. Installed Ghidra `VariableSymbolDB` and
`SymbolUtilities` require DEFAULT for those names. The corrected comparison
derives that exact expectation from manifest names; all other equalities stay
strict. The sealed mutation was unchanged, and independent review reproduced
the rule and every variable delta before live application.

Working identity: `db.18702`, 18 files / 125,438,836 bytes,
inventory SHA-256 `7ad24d16602a2c266e72888d8ee29b5199a7d621e4a67ff8075d77fc86de6dec`; main database 75,137,024 bytes,
SHA-256 `92d7c7305218d87c32b810560bde32072577a40a539273f19be7be8b1a763d47`. Restored Thing identity POST is PRE.
Independent POST: `/srv/archive-a/onslaught-ghidra-cold/2026-09-27-thing-gameplay-abi/post-working`. Tracked checkpoint remains `745c00ad…`.
Private receipts: `local-lab/ghidra-first-training-20260907-v1/re-audit-20260926/thing-gameplay-abi/`; fresh evidence and execution logs:
`local-data/test-runs/re-audit-20260926/thing-gameplay/abi-*`.

## RE-audit Thing gameplay identities — September 27

The [sixty-row manifest](../../tools/cohort-specs/thing-gameplay-identities-20260927.manifest.tsv) and
[spec](../../tools/cohort-specs/thing-gameplay-identities-20260927.spec.tsv) correct gameplay interface
identities in pristine `BEA.exe.original.backup`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.

Sixty Thing-family gameplay names corrected across eleven interface roles: speed limit, activation/deactivation, Hit, Damage and the six ground/gravity queries. All 7,714 body bytes / 2,386 instructions, existing signatures apart from name text, variables, locals, types and 8,272 other function records are preserved. Forty-seven old notes remain explicitly fallible leads; thirteen targets gain their first comments. The demonstrably stale infantry vfunc38 tag is replaced with vtable-slot-39; the old note is preserved and its shifted table start explicitly corrected.

Source-correlated Actor movement and Thing initialization/collision callers, complete retail script-registry bindings and independently checked receiver-bound dispatches establish the eleven methods; fixed-primary RTTI and all recognized aliases delimit their holders. Fresh parsing agrees with the cached 724-table model using the same parser, which is cache consistency rather than independent algorithmic evidence. The packet covers 62 Thing-family holders and 86 unique targets; 60 names are admitted, eight kept names remain for separate comment disposition and eighteen ambiguous/unresolved targets are withheld. Shared constants, conflicting methods, incomplete aliases, ambiguous least-derived owners and an unresolved indirect tail are not renamed. Two earlier rehearsals passed their mechanical checks but their seals remain under rejected-v1 and rejected-v2: review corrected overclaimed RTTI independence, ambiguous offset/argument prose, the stale infantry slot tag, and precise COL-pointer/source-value wording before the final fresh seal and rehearsal. Method identities do not certify full derived behavior, saved parameter/return types, source-body ownership or runtime parity. Existing physical-interface defects remain a separate explicitly scoped correction.

The fresh packet includes 97 complete body spans (29,429 bytes) and fourteen
registry/dispatch spans. The Activate, Deactivate and Damage script names are
bound to their callbacks through the complete straight-line registry
initializer, rather than inferred from saved handler names. The Hit argument
order is peer then report at target entry; the machine pushes report first.
CUnit's ObeyGravity query is bounded to its observed pointer/field predicate;
the meaning of that state value remains unknown.

Fresh PRE restoration, rehearsal, separate/sealed readbacks, five byte-stable
refusal controls, independent exact review with root reproduction, live readback
and independently restored Archive A POST passed. All nine live exports equal
rehearsal; only comment-count/digest program metrics change. The tracked name
projection is separately checked against all 8,332 live function rows.

Working identity: `db.18701`, 18 files / 124,980,084 bytes,
inventory SHA-256 `9c31783f31a6e5a4e8caa58acc62f72e9465517aba8e9a73293be9ae2645b86f`; main database 74,678,272 bytes,
SHA-256 `24d6dea1315667594543b4473939bec798687a296ecb6a58216a471e83362642`. Restored music identity POST is PRE.
Independent POST: `/srv/archive-a/onslaught-ghidra-cold/2026-09-27-thing-gameplay-identities/post-working`. Tracked checkpoint remains `745c00ad…`.
Private receipts: `local-lab/ghidra-first-training-20260907-v1/re-audit-20260926/thing-gameplay-identities/`; fresh evidence and execution logs:
`local-data/test-runs/re-audit-20260926/thing-gameplay/`.

## RE-audit music identities — September 27

The [ten-row manifest](../../tools/cohort-specs/music-identities-20260927.manifest.tsv) and
[spec](../../tools/cohort-specs/music-identities-20260927.spec.tsv) correct music source/interface
identities in pristine `BEA.exe.original.backup`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.

Ten music names corrected: the shared Initialise, DeviceChangeTrack and AddDirectoryToPlaylist identities, plus seven PC device adapter roles. All 543 body bytes / 184 instructions, signatures apart from their name text, variables, locals, types and 8,322 other function records are preserved. The two direct-tail entries remain thunks to their unchanged destinations. Eight old notes (5,848 bytes) remain explicitly fallible leads; two targets gain their first comments. The shared DeviceChangeTrack implementation is named for CMusic, separately from its CPCMusic table holder.

Fresh complete bodies, nine base declarations, raw fixed-primary CPCMusic-to-CMusic RTTI, singleton installation and shared-body dispatch sites corroborate every selected slot. Shared-source bodies and the Music.cpp allocation anchor independently bind the surrounding subsystem. Pinned PC source differs: the retail directory wrapper requests OGG once, initialization omits the source console-registration block, and volume uses linear float times127 plus x87 integer conversion rather than the tangent expression. The metadata correction rechecks previously documented facts; the August11 demo comparison and September20 isolated execution are not rerun here. Eight additional kept-name comments remain a separate cohort. Shared slot8 is excluded; missing PCMusic source, complete interfaces, filesystem outcomes, worker scheduling, device and audible acceptance remain open. No old tags were removed; previous groupings remain explicitly historical.

The existing [shared-music](../binary-analysis/cmusic-shared-semantics-2026-08-11.md)
and [device-interface](../binary-analysis/cpcmusic-vtable-semantics-2026-08-11.md)
owners retain the prior experiments and their limits. The source graph checks
three direct edges among eleven mapped shared functions with zero contradictions;
that sparse graph alone cannot distinguish Play from DeviceChangeTrack.
Fresh entry decoding corrects the analysis tool's cached switch-table spill
at SetVolume; this is not evidence of a saved Ghidra boundary defect there.

The source/body packet honestly pins the previous kept-menu export. Full-table
comparison with this freshly restored PRE finds only the intervening vertex
argument row changed; all eighteen music rows are identical. The private
`report-pre-binding.json` records both hashes and that bounded correspondence.

Fresh PRE restoration, rehearsal, separate/sealed readbacks, five byte-stable
refusal controls, independent exact review with root reproduction, live readback
and independently restored Archive A POST passed. All nine live exports equal
rehearsal; only comment-count/digest program metrics change.

Working identity: `db.18700`, 18 files / 124,783,476 bytes,
inventory SHA-256 `3a4413ec43c3a6cd76241fad7a4c5f853bef9bb36e2b2dde678f17c88fadcace`; main database 74,481,664 bytes,
SHA-256 `50e71c9ffd385ceb69a41f50bea2a6e2cedff3a6c249e5eace3f67dc196fdd11`. Restored vertex-menu argument POST is PRE.
Independent POST: `/srv/archive-a/onslaught-ghidra-cold/2026-09-27-music-identities/post-working`. Tracked checkpoint remains `745c00ad…`.
Private receipts: `local-lab/ghidra-first-training-20260907-v1/re-audit-20260926/music-identities/`; fresh evidence and execution logs:
`local-data/test-runs/re-audit-20260926/music/`.

## RE-audit vertex-menu argument interface — September 27

The [one-row manifest](../../tools/cohort-specs/vertex-menu-abi-20260927.manifest.tsv) and
[spec](../../tools/cohort-specs/vertex-menu-abi-20260927.spec.tsv) correct parameter/convention
metadata in pristine `BEA.exe.original.backup`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.

One vertex-menu argument interface, comment and tag set corrected: 00503ef0 now takes automatic ECX this, an integer index at Stack[4] and an output character buffer at Stack[8]. Both exits physically RET8. Saved undefined return type and unassigned return storage remain unchanged, as do all names, 146 code bytes / 47 instructions, locals, types and 8,331 other function records. Signature source changes from analysis to user-defined. Old notes and tags remain historical leads rather than complete certification.

Fresh complete instruction and stack analysis agrees with 23 isolated original-code cases (16 GetEntry and seven stack-probe sizes) plus two altered-copy controls. The actual __chkstk body preserves original ECX and reserves 4096 bytes; the selected-body stack argument references resolve to entry ESP+4/+8. RET8 and the receiver+0x14 branch are independently falsified by disposable ELF changes. Formatting/shader-text callees are hooks; the hook EAX is incidental and no meaningful returned-value API is established. Output guards cover boundary words, not all writes; no invalid-list, real formatting, Windows guard-page, graphics, player or audible acceptance is claimed. No independent receiver-bound indirect callsite was recovered. Evidence: local-data/test-runs/re-audit-20260926/console-menu/vertex-t4bw7ii_/receipt.json.

The initial exact export comparator rejected the expected signature-source
transition from ANALYSIS to USER_DEFINED; its target-specific expectation was
corrected without changing the sealed payload or rerunning the mutation.
Independent review and root reproduction checked the exact payload and the
retained original-code harness. Fresh PRE restoration, rehearsal, separate/sealed
readbacks, seven byte-stable refusal controls, live readback and independently
restored Archive A POST passed. All nine live exports equal rehearsal; only
the program comment digest changes. No names are added to audit dispositions.

Working identity: `db.18699`, 18 files / 124,750,708 bytes,
inventory SHA-256 `05e9215ced568c00cd20c289c2570951dacb82b52a1c21dca23cf70bbc3db0c6`; main database 74,448,896 bytes,
SHA-256 `16db4e1a18b4d4df6ea03973a4639ac7309970d142a0e49f552005c5f819404b`. Restored verified-console-menu POST is PRE.
Independent POST: `/srv/archive-a/onslaught-ghidra-cold/2026-09-27-vertex-menu-abi/post-working`. Tracked checkpoint remains `745c00ad…`.
Private receipts: `local-lab/ghidra-first-training-20260907-v1/re-audit-20260926/vertex-menu-abi/`; evidence and execution logs:
`local-data/test-runs/re-audit-20260926/console-menu/`.

## RE-audit verified console-menu names — September 27

The [nine-row comment manifest](../../tools/cohort-specs/console-menu-verified-20260927.manifest.tsv) and
[spec](../../tools/cohort-specs/console-menu-verified-20260927.spec.tsv) record bounded verification of existing interface names
in pristine `BEA.exe.original.backup`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.

Nine existing console-menu callback names are verified within inherited-interface identity limits; only comments and tags change. All names, 758 body bytes, 257 instructions, saved interfaces, locals, types and 8,323 other function rows are unchanged. All 5,027 old comment bytes are retained as explicitly fallible historical leads. Old recovery/signature tags are historical provenance, not certification of complete current types or behavior.

Complete source overrides and fresh retail bodies establish GetName, GetNumEntries, GetEntry and OnClick roles. Seven table-specific raw RTTI chains, inherited abstract-prefix/concrete-suffix continuity, two same-object base/derived constructions, exact physical cleanup and all-holder agreement support propagation. Saved labels are not proof inputs; the missing CConsoleMenu header is not invented. The ordinary VC6 slot-continuity premise is explicit. The real click consumer confirms slot1 count then signed-upper-bound selection to slot3, without a nonnegative guard. Folded stubs and unanchored slots remain withheld. The GetShowSubmenus declaration order differs from its retail slot4. Source-exact implementation ownership, complete ABI, correct behavior and runtime acceptance remain open. In particular VertexShader GetEntry at00503ef0 retains an incomplete zero-argument stdcall signature; its consumed ECX and two stack arguments are a separately recorded physical-interface correction.

Independent review and root reproduction checked the exact payload. Tool review
first reproduced conditional-source, macro, numeric-address, partial-register and
aggregated-RTTI counterexamples; the corrected evidence suite passes 164 tests.
Fresh PRE restoration, rehearsal, separate/sealed readbacks, five byte-stable
refusal controls, live readback and independently restored Archive A POST passed.
All nine live exports equal rehearsal; only the program comment digest
changes. Together with the prior twelve renames, all 21 admitted interface identities
have current bounded evidence; shared/conflicting targets remain withheld.

Working identity: `db.18698`, 18 files / 124,734,324 bytes,
inventory SHA-256 `0a53d52e240e63a1350aa6738191328a292706bf40bcc8815dbfe10012a8a97a`; main database 74,432,512 bytes,
SHA-256 `9261cc8eb95fd5a2505fa63fa46bb03f1e9adc649888d977e3c79187c8a7125e`. Restored console-menu identity POST is PRE.
Independent POST: `/srv/archive-a/onslaught-ghidra-cold/2026-09-27-console-menu-verified/post-working`. Tracked checkpoint remains `745c00ad…`.
Private receipts: `local-lab/ghidra-first-training-20260907-v1/re-audit-20260926/console-menu-verified/`; proof, tests and execution logs:
`local-data/test-runs/re-audit-20260926/console-menu/`.

## RE-audit console-menu identities — September 27

The [twelve-row manifest](../../tools/cohort-specs/console-menu-identities-20260927.manifest.tsv) and
[spec](../../tools/cohort-specs/console-menu-identities-20260927.spec.tsv) record inherited interface names
in pristine `BEA.exe.original.backup`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.

Twelve primary console-menu interface names are corrected across Music, Sound, Variable and VertexShader menus. Only names, comments and tags change; all 734 body bytes, 276 instructions, saved interfaces, locals, types and 8,320 other function rows remain unchanged. All 6,842 prior comment bytes remain explicitly fallible leads; five targets gain their first comments. Signature text changes only its function name.

Complete source overrides and fresh retail bodies establish GetName, GetNumEntries, GetEntry and OnClick roles. Seven table-specific raw RTTI chains, inherited abstract-prefix/concrete-suffix continuity, two same-object base/derived constructions, exact physical cleanup and all-holder agreement support propagation. Saved labels are not proof inputs; the missing CConsoleMenu header is not invented. The ordinary VC6 slot-continuity premise is explicit. The real click consumer confirms slot1 count then signed-upper-bound selection to slot3, without a nonnegative guard. Folded stubs and unanchored slots remain withheld. The GetShowSubmenus declaration order differs from its retail slot4. Source-exact implementation ownership, complete ABI, correct behavior and runtime acceptance remain open. In particular VertexShader GetEntry at00503ef0 retains an incomplete zero-argument stdcall signature; its consumed ECX and two stack arguments are a separately recorded physical-interface correction.

Independent review and root reproduction checked the exact payload. Tool review
first reproduced conditional-source, macro, numeric-address, partial-register and
aggregated-RTTI counterexamples; the corrected evidence suite passes 164 tests.
Fresh PRE restoration, rehearsal, separate/sealed readbacks, five byte-stable
refusal controls, live readback and independently restored Archive A POST passed.
All nine live exports equal rehearsal; only comment count/digest program metrics
change. Nine additional kept-name comment dispositions remain a separate cohort.

Working identity: `db.18697`, 18 files / 124,668,788 bytes,
inventory SHA-256 `fd03e659a6b5e66d169851c4cac8ad1a49e946f1aa5ea775959decf7973a95a8`; main database 74,366,976 bytes,
SHA-256 `e94c2b511adc783c588d4777fbe16d2c3e11c732a351b4c6683b2e464124763b`. Restored CPostEventData POST is PRE.
Independent POST: `/srv/archive-a/onslaught-ghidra-cold/2026-09-27-console-menu-identities/post-working`. Tracked checkpoint remains `745c00ad…`.
Private receipts: `local-lab/ghidra-first-training-20260907-v1/re-audit-20260926/console-menu-identities/`; proof, tests and execution logs:
`local-data/test-runs/re-audit-20260926/console-menu/`.

## RE-audit CPostEventData cleanup identity — September 27

The [one-row manifest](../../tools/cohort-specs/postevent-cleanup-20260927.manifest.tsv) and
[spec](../../tools/cohort-specs/postevent-cleanup-20260927.spec.tsv) record the corrected cleanup identity
in pristine `BEA.exe.original.backup`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.

One class-associated nondeleting cleanup at 005386d0 is named CPostEventData__dtor_body instead of DestructorBody_005386d0. Only the name, comment and tags change; all 105 body bytes, 29 instructions, physical ABI/storage, variables, types and 8,331 non-target rows are unchanged. All 1,955 old comment bytes remain as fallible history, including a short analytic opcode witness. Saved signature text changes only its function name.

Fresh RTTI binds table 005e4f34 to CPostEventData; its sole matching deleting wrapper 005386b0 calls this cleanup. The cleanup installs that table at 005386ed and its normal return is dominated by the original-this call 00538724 to CMonitor at 004bac40. The existing cleanup admission tool reproduces those facts from fresh complete bodies. July history already recognized this positive owner but deliberately stopped at removing the false CScriptEventNB label; this promotion closes that disposition without calling the old constrained correction wrong. The retained scripteventnb and wave586 tags denote legacy subsystem/wave grouping, not exclusive class identity; they also label IScript and the corrected CPostEventData wrapper. Source-exact spelling, exceptions, callee internals, prototype types and complete cleanup/runtime behavior remain open.

Independent review re-derived the raw RTTI, unique wrapper, primary-vptr and
normal teardown, and compared the exact payload and POST. Root reproduced it;
a message's instruction-count typo was corrected to 29. Fresh PRE restoration,
rehearsal, separate/sealed readbacks, five byte-stable refusal controls, live
readback and independently restored Archive A POST passed. All nine live exports
match rehearsal; only the program comment digest changes. The full current name
projection remains exact for 8,332 entries.

Working identity: `db.18696`, 18 files / 124,652,404 bytes,
inventory SHA-256 `5618b157f1f63879518fd74408de473be758bf190d6ea5d3932cd78e15088d7e`; main database 74,350,592 bytes,
SHA-256 `159aae7eaf6a971f6b437a968a942d1405c0c15c5d5834dbe6a0f90c26bce4c4`. Restored verified-cleanup POST is PRE.
Independent POST: `/srv/archive-a/onslaught-ghidra-cold/2026-09-27-postevent-cleanup/post-working`. Tracked checkpoint remains `745c00ad…`.
Private receipts: `local-lab/ghidra-first-training-20260907-v1/re-audit-20260926/postevent-cleanup/`; proof, tests and logs use `postevent-` under
`local-data/test-runs/re-audit-20260926/frontend-options/`.

## RE-audit verified cleanup bodies — September 27

The [43-row manifest](../../tools/cohort-specs/cleanup-body-verified-20260927.manifest.tsv) and
[spec](../../tools/cohort-specs/cleanup-body-verified-20260927.spec.tsv) verify existing cleanup names
in pristine `BEA.exe.original.backup`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.

Exactly 43 existing cleanup names verified within bounded class-associated nondeleting identity limits. Only comments and tag sets change. All names, prototypes, locals, types, saved stack metadata, 6,586 body bytes and 1,973 instructions are unchanged; 8,289 non-target function rows remain exact. All 16,761 previous comment bytes remain verbatim as qualified fallible leads. The authored comments total 102,111 bytes. No complete cleanup or runtime behavior is claimed.

The cleanup-bodies extension to re_name_evidence.py passes 152 tests and independently reviewed negative controls. It checks fresh RTTI, first literal primary-vptr store through unchanged-this, own-table slot1 backlink to a byte-recognized deletion wrapper, every matching wrapper byte shape, full fresh decoding and recursive normal-return teardown to reviewed CMonitor at 004bac40. Cached names never enter evidence admission. The mechanism inspected 154 full bodies and admitted 44 cleanup identities; 43 already-correct spellings form this cohort, while CPostEventData at 005386d0 remains a separate name correction. CUnit is included through a mechanically admitted wrapper whose earlier output spelling collided; 113 wrapper names, not 114, had been promoted. The 69 rejected owner-prefix cases remain unresolved. CUnitAI at 00415080 and MechAI context at 004a03b0 are not conflated. Root reproduced first-store encoding and overlapping-ownership bugs before fixing them; segment changes and indexed/overlapping stores are refused. SDK/source-exact spelling, prototype typing, exceptions, arbitrary indirect callers and full callee behavior remain outside this normal-flow proof.

Independent review checked every target/pin/old note and the bounded shared
comment template. The private public-comment review initially listed only
cohort-specific added tags; its corrected accounting records the full delta
without changing the sealed payload. Fresh PRE restore, rehearsal,
separate/sealed readbacks, five byte-stable refusal controls, exact payload/POST
review with root reproduction, live readback and independently restored Archive A
POST passed. All nine live exports match rehearsal; program scope changes only
the comment digest. The name projection remains exact for all 8,332 entries.

Working identity: `db.18695`, 18 files / 124,652,404 bytes,
inventory SHA-256 `7488b9377a3b2cc6460f1a798fe4b08527bb50719ecff3d7ff139197f4f0de7d`; main database 74,350,592 bytes,
SHA-256 `a95e4355b32be6cbc3d52e56ba0bc1a95306a3d629810d55033885079e86d59b`. Restored WndProc POST is PRE.
Independent POST: `/srv/archive-a/onslaught-ghidra-cold/2026-09-27-cleanup-body-verified/post-working`. Tracked checkpoint remains `745c00ad…`.
Private receipts: `local-lab/ghidra-first-training-20260907-v1/re-audit-20260926/cleanup-body-verified/`; proof, tests and logs use `cleanup-` under
`local-data/test-runs/re-audit-20260926/frontend-options/`.

## RE-audit window callback identity and interface — September 27

The [one-row manifest](../../tools/cohort-specs/window-callback-abi-20260927.manifest.tsv) and
[spec](../../tools/cohort-specs/window-callback-abi-20260927.spec.tsv) describe the source-correlated
Windows message callback in pristine `BEA.exe.original.backup`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.

One default function FUN_00529070 is named WndProc and given a physical stdcall interface: four undefined4 stack parameters hWnd/uMsg/wParam/lParam and undefined4 EAX return, with no incoming receiver. One authored comment and tag set added; the old default name remains in the note. All 34 code bytes, 12 instructions, 8,331 other functions, locals, types and other variables remain unchanged. Stack purge stays the saved unknown value2147483647; the physical RET16 is established from instructions, not a changed purge annotation. The declared symbol source moves DEFAULT to USER_DEFINED; one comment is added.

Source-correlated callback in pinned d3dapp.cpp79-81/114, with identical source body in EditorD3DApp.cpp73, so no unique translation-unit attribution. RegisterClassA setup stores the callback at00529151 and registers at005291a4. Constructor00528fb3 assigns the global receiver0089c0f4. The callback overwrites ECX from that global, forwards four entry stack DWORDs in order to virtual slot12 and returns the complete EAX unchanged. Retained original-code evidence has34 callback cases but set incoming ECX to the surrogate receiver; static overwrite, not a poison-ECX experiment, establishes lack of an incoming receiver requirement. SDK typedefs/signedness, Windows dispatch, receiver lifetime, reentrancy and device/player acceptance stay open. No runtime experiment was rerun.

Fresh PRE restore, dry/apply rehearsal, separate/sealed readbacks, nine actual
byte-stable refusal controls, independent exact-payload review with root
reproduction, live readback and independently restored Archive A POST passed.
All nine live exports equal rehearsal. The comparison initially omitted the
expected DEFAULT-to-USER_DEFINED symbol count and added-comment count; it now
requires exactly +1/-1 symbol sources and +1 comment as well as the comment
digest. No unexplained change was accepted. No saved stack-purge value was changed.

Working identity: `db.18694`, 18 files / 124,439,412 bytes,
inventory SHA-256 `75c76af4d2b65f0bc4ec2e0bdf26799fbc843db5407f528f8e76f28bfde88ead`; main database 74,137,600 bytes,
SHA-256 `4f9db6700c6bdec9524a5b5be05053f7326225738feea8617f1461e22245eb07`. Restored frontend-argument POST is PRE.
Independent POST: `/srv/archive-a/onslaught-ghidra-cold/2026-09-27-window-callback-abi/post-working`. Tracked checkpoint remains `745c00ad…`.
Private cohort receipts: `local-lab/ghidra-first-training-20260907-v1/re-audit-20260926/window-callback-abi/`; logs use `abi-` under
`local-data/test-runs/re-audit-20260926/window-callback-boundary/`.

## RE-audit frontend argument interfaces — September 27

The [22-row manifest](../../tools/cohort-specs/frontend-argument-abi-20260927.manifest.tsv) and
[spec](../../tools/cohort-specs/frontend-argument-abi-20260927.spec.tsv) correct argument metadata from
pristine `BEA.exe.original.backup`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.

Twenty-two argument interfaces, comments and tag sets corrected. Six transitions lose an invented EDX formal; four render and one button interfaces gain the correct stack meanings; eleven other methods gain their missing formal receiver. All use automatic ECX this. Fifteen render interfaces retain float transition at stack+4 and opaque other-page DWORD at+8; ButtonPressed uses button DWORD then float value; transitions use one page DWORD. Names, all return types/storage (including three undefined/unassigned returns), stack purge, locals, 8,059 code bytes / 2,234 instructions and 8,310 non-target functions remain unchanged. Older notes remain fallible leads.

The ordered extension to re_name_evidence.py validates source declarations/calls, fresh versus cached receiver/slot decoding, values frozen at each PUSH, stack offsets and every known holder. Independent review and root reproduction cover all 32 holder words and exact selected bodies. The timed SetPage path carries page on stack while EDX holds the vptr, disproving a required EDX page argument; the immediate path alone could mislead because EDX coincidentally equals the pushed word. Source typedef signedness, external-premise aliasing, return semantics, whole-caller domination and actual menu/input/render behavior remain outside this local-path proof. Shared CALL joins and the nine-holder RenderPreCommon qualification remain explicit. Tool review exposed stale dispatch, assignment-expression loss and outgoing-stack reload cases; the fixes pass the 141-test suite and the real 22-target packet. No new retail runtime experiment is claimed.

The [frontend render note](../binary-analysis/functions/FrontEnd.cpp/CFrontEnd__Render.md#september-27-ordered-page-argument-interfaces)
records exact source/caller locations, the three schemas, preserved returns
and limits. The source spells its page argument `dest`; retail incoming and
outgoing pages receive the opposite endpoint. No page-enum definition or SINT
typedef is synthesized. Existing signed annotations weaken to undefined4.

Fresh PRE restoration, rehearsal, separate/sealed readbacks, seven actual
byte-stable refusal controls, independent review/root reproduction, live
readback and independently restored Archive A POST passed. All nine live
exports equal rehearsal. All 8,332 current names match the projection; this
cohort adds no newly verified or corrected names. It adds 22 interface
corrections to the audit count, preserving unrelated return uncertainty.

Working identity: `db.18693`, 18 files / 124,439,412 bytes,
inventory SHA-256 `36dc1b5d6c90a3d05bb2249bce4e406b33e6452fdfa225e6696e44eaa9b2213b`; main database 74,137,600 bytes,
SHA-256 `653db8824a0d8e48554c00513452596e20aa440684d6cef318e4a2dc9dbd4e18`. Restored window-callback POST is PRE.
Independent POST: `/srv/archive-a/onslaught-ghidra-cold/2026-09-27-frontend-argument-abi/post-working`. Tracked checkpoint remains `745c00ad…`.
Private cohort receipts: `local-lab/ghidra-first-training-20260907-v1/re-audit-20260926/frontend-argument-abi/`; proof, tests and logs:
`local-data/test-runs/re-audit-20260926/frontend-options/`.

## RE-audit window callback boundary — September 27

The [one-row manifest](../../tools/cohort-specs/window-callback-boundary-20260927.manifest.tsv) and
[spec](../../tools/cohort-specs/window-callback-boundary-20260927.spec.tsv) add a default boundary from
pristine `BEA.exe.original.backup`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.

One default FUN_00529070 function added over the existing 34-byte / 12-instruction window callback. All 8,331 existing function rows, code, references, data, variables, comments, types and bookmarks are preserved. New metadata remains default: undefined return, unknown convention, no parameters, tags or comments. Only the program function count rises to 8,332; this is a boundary correction, not a completed semantic or ABI disposition.

Fresh pristine instructions, RegisterClassA callback-field assignment at 00529151, source d3dapp.cpp lines 79–81 and a read-only disposable-project ownership inspection establish the separate extent 00529070–00529091. The source-correlated WndProc name and four-argument callee-clean interface require a separate metadata cohort. Previously retained isolated message experiments are reused, not rerun. Dynamic Windows dispatch, all indirect entries and full runtime behavior remain outside this correction. Existing CREATE_FUNCTION gates require fully decoded instructions and refuse conflicting code/data/function/symbol ownership; no disassembly or framework weakening was needed.

The [platform note](../source-code/core/platform-system.md#retail-startup-shell--september-27-correction)
records callback registration and forwarding. The complete body loads the
application global, forwards four stack arguments through slot 12 and returns
with RET 16; surrounding padding stays outside the new function.

Fresh PRE restoration, rehearsal, separate/sealed readbacks, five actual
byte-stable refusal controls, independent review/root reproduction, live
readback and independently restored Archive A POST passed. All nine live
exports equal rehearsal; the complete name projection matches all 8,332 entries.

Working identity: `db.18692`, 18 files / 124,029,812 bytes,
inventory SHA-256 `d673c565915343f5955fffef0250e390550de5e47e63788c67d28af69d8b5b0f`; main database 73,728,000 bytes,
SHA-256 `9c41d793cc8f5d635ca41c7d0ebb41b360e2f1031b02c47e44df044693e9190c`. Restored GetBPP POST is PRE.
Independent POST: `/srv/archive-a/onslaught-ghidra-cold/2026-09-27-window-callback-boundary/post-working`. Tracked checkpoint remains `745c00ad…`.
Private cohort receipts: `local-lab/ghidra-first-training-20260907-v1/re-audit-20260926/window-callback-boundary/`; evidence and focused-test logs:
`local-data/test-runs/re-audit-20260926/window-callback-boundary/`.

## RE-audit GetBPP identity and interface — September 27

The [one-row manifest](../../tools/cohort-specs/getbpp-abi-20260927.manifest.tsv) and
[spec](../../tools/cohort-specs/getbpp-abi-20260927.spec.tsv) correct the shell texture-depth
helper from pristine `BEA.exe.original.backup`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.

One name, physical prototype, comment and tag set corrected: PCLTShell GetBPP retains int/EAX return, gains automatic ECX receiver and one undefined4 stack format argument. The eight body bytes / two instructions, return transport, existing stack purge, locals and 8,330 non-target rows are unchanged. The old note remains a fallible lead; two misleading identity/signature tags are removed. Only the program comment digest changes.

Eight complete retail caller transports, the singleton constructor/RTTI chain and pinned source establish GetBPP. The body reads neither ECX nor its stack argument: thiscall expresses the source-correlated caller interface, not a necessary receiver dereference. The format enum typedef/signedness remain unknown. Constant32 agrees with the available source whose first condition contains a nonzero enum operand; historical compiler/header inputs are unknown. Five previously retained original-code cases are reused, not rerun. No actual texture allocation, Windows/device behavior or complete source equivalence is certified. Independent exact-payload and interface review was reproduced by root.

The [platform note](../source-code/core/platform-system.md#constant-bpp-helper-identity-and-physical-interface)
records the caller/source witnesses and limits. The previous `CEngine` owner
and no-argument cdecl declaration were misleading. The combined name/prototype
operation uses the existing gate with exact PRE/POST names and signatures;
no framework check was weakened.

Fresh PRE restoration, rehearsal, separate/sealed readbacks, nine actual
byte-stable refusal controls, independent review/root reproduction, live
readback and independently restored Archive A POST passed. All nine live
exports equal rehearsal; the complete name projection matches all 8,331 entries.

Working identity: `db.18691`, 18 files / 124,029,812 bytes,
inventory SHA-256 `f305f4899b08712ccb03f8bd3e26418f9c3430027d46e3a9b880dbd59b61b77b`; main database 73,728,000 bytes,
SHA-256 `595b1589164a1794265fe24a17f6323c5c424ba3b25a4d8269e10b640495158b`. Restored startup-shell POST is PRE.
Independent POST: `/srv/archive-a/onslaught-ghidra-cold/2026-09-27-getbpp-abi/post-working`. Tracked checkpoint remains `745c00ad…`.
Private cohort receipts: `local-lab/ghidra-first-training-20260907-v1/re-audit-20260926/getbpp-abi/`; evidence and focused-test logs:
`local-data/test-runs/re-audit-20260926/getbpp-abi/`.

## RE-audit startup shell identities — September 27

The [eight-row manifest](../../tools/cohort-specs/startup-shell-20260927.manifest.tsv) and
[spec](../../tools/cohort-specs/startup-shell-20260927.spec.tsv) correct startup-shell
identities from pristine `BEA.exe.original.backup`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.

Eight startup-shell names/comments/tag sets corrected: seven independently witnessed virtual methods and DeviceObject registration. All prototypes, locals, 1,538 body bytes / 492 instructions and 8,323 non-target rows remain unchanged. All five earlier comments and every prior tag are retained; three comments were newly added. Only the program comment count/digest change.

Fresh source/retail callers, literals, imports, complete bodies and RTTI establish the shell methods and its singleton registration context. The seven virtual corrections use partial reviewed slot anchors, not positional equivalence: retail has14 slots versus13 source declarations and reorders lifecycle entries. The six-undefine source-selection profile is explicit and does not prove historical compiler flags. Ten direct registration calls, the singleton/base constructor chain and exact prepend body match AddDeviceObject. Independent review and root reproduction corrected a non-target Create anchor that overclaimed ShowWindow/UpdateWindow calls; revised evidence has identical dispositions and the sealed eight-row payload is unchanged. Existing Create/base MsgProc names are not counted as promoted kept names here. The GetBPP physical interface and absent WndProc function boundary remain separate scoped corrections. No game, Windows dispatch, real device, callback lifetime or complete source equivalence is certified.

The [platform note](../source-code/core/platform-system.md#retail-device-lifecycle--september-27-correction)
records wrapper addresses, list order, source divergences and open runtime
questions. This family determines method roles, not complete implementation
semantics. Existing semantic names are retained as leads in every changed
plate comment.

Fresh PRE restoration, rehearsal, separate/sealed readbacks, five actual
byte-stable refusal controls, independent review/root reproduction, live
readback and independently restored Archive A POST passed. All nine live
exports equal rehearsal; the complete name projection matches all 8,331 entries.

Working identity: `db.18690`, 18 files / 124,029,812 bytes,
inventory SHA-256 `77de16820005410f23efcc0b4b7b02ab7cbf43fd243aabdfa4f243e105e53787`; main database 73,728,000 bytes,
SHA-256 `de31f4e35c5f7d04c794a89b130bf2d24660b2e0ba785da3ab1d3d1be7b0bb58`. Restored device-lifecycle POST is PRE.
Independent POST: `/srv/archive-a/onslaught-ghidra-cold/2026-09-27-startup-shell/post-working`. Tracked checkpoint remains `745c00ad…`.
Private cohort receipts: `local-lab/ghidra-first-training-20260907-v1/re-audit-20260926/startup-shell/`; evidence and focused-test logs:
`local-data/test-runs/re-audit-20260926/startup-shell/`.

## RE-audit device lifecycle identities — September 27

The [31-row manifest](../../tools/cohort-specs/device-lifecycle-20260927.manifest.tsv) and
[spec](../../tools/cohort-specs/device-lifecycle-20260927.spec.tsv) correct resource lifecycle
identities from pristine `BEA.exe.original.backup`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.

Thirty-one DeviceObject lifecycle names corrected across forty known RTTI holder occurrences. All prototypes, locals, bodies, 3,716 code bytes / 1,282 instructions and 8,300 non-target function rows remain unchanged. Thirty-one comments updated, including six previously absent comments; all 25 older notes and every prior tag retained as fallible leads. Only the program comment count/digest change.

Four source/retail wrapper correspondences and the two-list receiver layout were independently rederived from complete pristine bodies, RTTI, literals and reset/teardown ordering. The validated typed-list checker binds the source declaration/call/advancement to exact ECX/vptr/slot transports and propagates only through unique fixed primary ancestry, complete known holder coverage and aligned non-code pointer-cell agreement. All fresh target body decodes and return cleanup gates pass; three bounded texture switches and a stack/receiver-neutral direct tail were independently reproduced. Review exposed source type/identifier lookalikes, result-variable shadowing and control-flow bypasses; the root reproduced and fixed these, with 144 evidence/source-graph tests passing. The first seal and its successful rehearsal were rejected before live for an off-by-one source citation in eight Restore comments. Root reproduced line1074 as the call and1075 as its result test, retained that seal in device-lifecycle/rejected-v1, and repeated fresh PRE/rehearsal/review/refusal gates for the exact eight-digit correction. Two shared stubs remain excluded for conflicting method identities; a texture initializer remains withheld for a conservative WORD-store switch grammar, not a proved retail defect. Retail has two lists and restores during initialization, unlike the source route. No DeviceObject header was fabricated. No prototype, callback lifetime, resource algorithm, exclusive source-body ownership or retail graphics behavior is certified. Normal callee ABI and readable post-callback nodes remain premises. No runtime launch.

The [platform note](../source-code/core/platform-system.md#retail-device-lifecycle--september-27-correction)
records wrapper addresses, list order, source divergences and open runtime
questions. This family determines method roles, not complete implementation
semantics. Existing semantic names are retained as leads in every changed
plate comment.

Fresh PRE restoration, rehearsal, separate/sealed readbacks, five actual
byte-stable refusal controls, independent review/root reproduction, live
readback and independently restored Archive A POST passed. All nine live
exports equal rehearsal; the complete name projection matches all 8,331 entries.

Working identity: `db.18689`, 18 files / 123,997,044 bytes,
inventory SHA-256 `3c078eeefd21c803da4dc997b78e9d1c54eaea980b52a335dee8dcf88bfda161`; main database 73,695,232 bytes,
SHA-256 `24cf8d2555f786ce76e68c941670b22af176ae450814d14944fb7126271b34cd`. Restored camera copy-return POST is PRE.
Independent POST: `/srv/archive-a/onslaught-ghidra-cold/2026-09-27-device-lifecycle-v2/post-working`. Tracked checkpoint remains `745c00ad…`.
Private cohort receipts: `local-lab/ghidra-first-training-20260907-v1/re-audit-20260926/device-lifecycle-v2/`; evidence and focused-test logs:
`local-data/test-runs/re-audit-20260926/device-lifecycle/`.

## RE-audit camera copy-return interfaces — September 27

The [six-row manifest](../../tools/cohort-specs/camera-copy-abi-20260927.manifest.tsv) and
[spec](../../tools/cohort-specs/camera-copy-abi-20260927.spec.tsv) correct physical result returns
without changing names or code. Specimen: pristine `BEA.exe.original.backup`,
SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.

Six camera copy-leaf physical returns corrected to the existing four-byte generic pointer in EAX. Five saved undefined/unassigned returns and one void return omitted that value. The calling convention remains thiscall with automatic ECX receiver and one unchanged stack result pointer. All parameter names, types, source flags and storage, every name, local, stack/type definition and non-target variable stay exact. 193 body bytes / 76 instructions and 8,325 non-target function rows are unchanged. Six comments are updated (one previously absent), all older notes/tags retained as fallible leads; three audit tags added. Only the program comment count/digest change.

Root freshly decoded every pristine byte and reproduced the six destination-in-EAX paths and RET4 cleanup. The existing 30 isolated original-code cases and two separate mutants independently support normal-result transport, copy order and cleanup with surrogate buffers. The physical signature does not claim a source-level pointer return, complete aggregate layout, exclusive body owner or orientation identity. The REP bodies assume clear DF. Valid result/object storage and result storage outside saved stack are required; overlapping source/result memory follows ordered copying. No original caller, full camera path or retail presentation was run. The first dry seal refused an empty-string encoding for one absent comment before writes; the null sentinel correction and rejected receipt are retained. Independent read-only review and root reproduction checked all six return types, EAX storage, preserved default-named argument sources and automatic receiver flags. No saved thunk depends on these targets.

Fresh PRE restoration, rehearsal, separate/sealed readbacks, seven actual
byte-stable refusal controls, independent review/root reproduction, live
readback and independently restored Archive A POST passed. All nine live
exports equal rehearsal. Parameter source flags and auto status are preserved, including DEFAULT-named
`param_1` values; return and signature sources become USER_DEFINED. The [camera note](../binary-analysis/player-camera-attach-and-mesh-hfov-2026-07-26.md#september-27-position-identities-and-result-transport)
separates static findings, isolated original code and runtime unknowns.

Working identity: `db.18688`, 18 files / 123,898,740 bytes,
inventory SHA-256 `5c85495c72f1930f2a64ae09fe0ca314f89ac74d7fb1c1fc38530f976b3c179f`; main database 73,596,928 bytes,
SHA-256 `a41f19d2e8d797ef1dc2c8b91d2614eb9c1b671fbc7c56d422bdb4e5b1ed4835`. Restored camera position POST is PRE.
Independent POST: `/srv/archive-a/onslaught-ghidra-cold/2026-09-27-camera-copy-abi/post-working`. Tracked checkpoint remains `745c00ad…`.
Private receipts: `local-lab/ghidra-first-training-20260907-v1/re-audit-20260926/camera-copy-abi/`.

## RE-audit camera position identities — September 27

The [nine-row manifest](../../tools/cohort-specs/camera-position-20260927.manifest.tsv) and
[spec](../../tools/cohort-specs/camera-position-20260927.spec.tsv) correct current/previous position
method names against pristine `BEA.exe.original.backup`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.

Nine current/previous camera-position method names corrected, with comments and tag additions only. All interfaces, locals, 1,660 body bytes / 519 instructions and 8,322 non-target function rows remain unchanged. All five earlier notes and every prior tag are retained as fallible leads. Four previously empty comments are added.

Pinned Camera.h declarations, complete result-copy leaves and the source-matched constructor call sequence establish position/old-position interface slots. All 11 known RTTI holder occurrences agree; naming contexts remain nonexclusive. The caller witness proves local receiver/ESP-relative result-pointer transport under normal ABI and valid nonaliasing storage premises, not full frame lifetime or intervening callee behavior. Full-body return-cleanup checks preserve unknown prototype and aggregate component types. Review defects in the checker were reproduced and fixed; 113 focused tests pass. The first seal was rejected for imprecise pointer/owner wording and retained privately. Fresh PRE, revised exact rehearsal/readbacks and five byte-stable refusals passed. Separately, six unchanged copy leaves passed 30 syscall-confined original-code cases plus two discriminating mutant controls; these exercise surrogate buffers and register/stack transport, not original callers, camera geometry, timing or retail presentation.

All nine live exports equal the separately reopened revised rehearsal. Independent
read-only payload/PRE review with root reproduction, live readback and restored
Archive A POST passed. The checkpoint was never write-opened. Five existing
position names remain comment-audit candidates. Orientation callers with raw
interior-pointer candidates remain withheld; those words are not proven incoming
branches. The copy getters' saved return metadata still needs a separate ABI
correction; this names-only cohort does not certify it.

Working identity: `db.18687`, 18 files / 123,882,356 bytes,
inventory SHA-256 `1bbdd130acb8a019fd749e65826a6af948c9f2ab674b9702d0538d310fe691d3`; main database 73,580,544 bytes,
SHA-256 `9163d76228eb91c7d3616f134f0caef3649cdc1807b1fdedb869e13757fcc10e`. Restored verified-switch POST is PRE.
Independent POST: `/srv/archive-a/onslaught-ghidra-cold/2026-09-27-camera-position-v2/post-working`. Tracked checkpoint remains `745c00ad…`.
Private gate receipts: `local-lab/ghidra-first-training-20260907-v1/re-audit-20260926/camera-position-v2/`; source/caller/leaf proofs and original-code
controls: `local-data/test-runs/re-audit-20260926/camera-interface/`.

## RE-audit verified switch-backed methods — September 27

The [17-row manifest](../../tools/cohort-specs/switch-verified-20260927.manifest.tsv) and
[spec](../../tools/cohort-specs/switch-verified-20260927.spec.tsv) preserve every method name and
attach its interface evidence. Pristine `BEA.exe.original.backup`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.

Seventeen existing frontend/listener method names verified with comments and tags only. All names, interfaces, locals, 27,072 body bytes / 7,455 instructions and 8,314 non-target function rows remain unchanged. All 17 earlier notes and every prior tag are retained, explicitly outside this semantic certification.

Fresh evidence reports against the preceding complete live export preserve every selected body, RTTI, admission and switch proof. Independently bound page-array and event-recipient callers establish method slots; all 46 known holder occurrences agree. Complete bodies, 22 tables / 135 words and 11 zero-extended remaps passed bounded normal-flow admission. Main/DemoMain, Game/DXGame and the 28 Unit holders are nonexclusive naming contexts. BEConfig ButtonPressed has an unproved saved int player_index where the interface has a float; two other second arguments are undefined. These and inherited confidence tags need separate ABI review. No full behavior, exclusive source-body ownership, exceptions, stack balance or runtime table immutability is certified.

Fresh PRE restoration, exact rehearsal, separate/sealed readbacks, five
byte-stable refusal controls, independent payload/PRE review with root
reproduction, live readback and independently restored Archive A POST passed.
All nine live exports equal rehearsal. Only the program comment digest changes.
The two raw guard-interior pointer questions stay withheld; they are not
established incoming control-flow edges. Saved prototype corrections remain
separate, including the pointer argument of MessageBox from the preceding cohort.

Working identity: `db.18686`, 18 files / 123,865,972 bytes,
inventory SHA-256 `0f93cb947333e459ee54471ed3d5cf75cec5cd9f6597b1d27c2271c90e852684`; main database 73,564,160 bytes,
SHA-256 `a17bd3a23ad4ae72979cd1cb2ea36b767a3ea8eb15952da588a95fa4e0bf3b6f`. Restored six-name switch POST is PRE.
Independent POST: `/srv/archive-a/onslaught-ghidra-cold/2026-09-27-switch-verified/post-working`. Tracked checkpoint remains `745c00ad…`.
Private gate receipts: `local-lab/ghidra-first-training-20260907-v1/re-audit-20260926/switch-verified/`; exact identity reports and retained controls:
`local-data/test-runs/re-audit-20260926/switch-admission/`.

## RE-audit switch-backed method identities — September 27

The [six-row manifest](../../tools/cohort-specs/switch-identities-20260927.manifest.tsv) and
[spec](../../tools/cohort-specs/switch-identities-20260927.spec.tsv) correct method names against
pristine `BEA.exe.original.backup`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.

Six virtual method identities corrected: multiplayer Init/Shutdown, Options Process and MessageBox/Round/UnitAI HandleEvent. All 2,215 code bytes / 679 instructions, interfaces, locals and 8,325 non-target function rows remain unchanged. One previously empty comment is added; only the program comment count/digest change. Prior names and comments remain fallible leads. Source-body ownership uncertainty tags are preserved.

The existing header/RTTI tool now admits unsigned-bounded absolute switches with separately pinned tables. Independent page-array and guarded event-recipient callers establish slots; every known holder agrees. Complete bodies and 49 table words passed entry decoding, unsigned guard/selector preservation, possible bypass checks and return-cleanup agreement. Matching switch shapes do not supply method identities. Independent review rejected the first seal for dropping CRound source-identity-deferred; an inherited interface plus nonexclusive RTTI context does not identify a missing source body. The tag was retained and a fresh PRE and exact revised rehearsal/readbacks and five byte-stable refusal controls passed. These are names and bounded normal-flow evidence, not complete ABI, stack-balance, source-body or runtime semantics. The separate Options experiment runs unchanged code with two intercepted callees; its contract carries the limits.

All nine live exports equal the separately reopened revised rehearsal.
Independent read-only review, root reproduction, live readback and independently
restored Archive A POST passed. The tracked checkpoint was never write-opened.
Seventeen additional kept-name candidates and two withheld raw-pointer leads
remain outside this six-row promotion. Saved prototype types are unchanged;
in particular MessageBox's event argument still needs its separate correction.

Working identity: `db.18685`, 18 files / 123,767,668 bytes,
inventory SHA-256 `7c19c9ce263e11a16cdc9c728ffb914cdf37430ababfb0016c760a3749c69f95`; main database 73,465,856 bytes,
SHA-256 `70c4d0899b3d81059f8a856ef15f244fe6f970eac07270a7276b34c5b74c5649`. Restored chunk-reader POST is PRE.
Independent POST: `/srv/archive-a/onslaught-ghidra-cold/2026-09-27-switch-identities/post-working`. Tracked checkpoint remains `745c00ad…`.
Private gate receipts: `local-lab/ghidra-first-training-20260907-v1/re-audit-20260926/switch-identities/`; proof and original-code controls:
`local-data/test-runs/re-audit-20260926/switch-admission/`.

## RE-audit chunk-reader interfaces — September 27

The [six-row manifest](../../tools/cohort-specs/reader-abi-20260927.manifest.tsv) and
[spec](../../tools/cohort-specs/reader-abi-20260927.spec.tsv) correct reader interfaces
without changing names or code. Specimen: pristine `BEA.exe.original.backup`,
SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.

Six CChunkReader interfaces/comments/tags corrected. Five no-stack-argument members change explicit fastcall ECX receivers to automatic thiscall receivers at the same physical ECX location. Read changes bool/AL:1 to int/EAX:4 while retaining its three stack arguments and unresolved size/count signedness. All six existing method identities are independently supported and kept. Every name, local, code byte, instruction, reference, bookmark and non-target variable stays unchanged; 8,325 non-target rows remain exact. Two historical confidence tags per target are removed; older comments remain explicitly fallible leads. Only the program comment digest changes.

Complete pristine coverage is 300 bytes and 111 instructions. The constructor allocation literal/line anchor, pinned member declarations, complete bodies and resource-dispatch caller transports establish the family. The constructor retains its machine EAX=this pointer return and the destructor remains void. Return-width evidence for Read comes from the complete callee and BOOL declaration, not a caller AL/EAX distinction. The existing 49 original-code reader cases and two explicit counterfactuals support bounded arithmetic/ordering/return statements with intercepted buffer calls; Read cases copy zero destination bytes. Low-word multiplication does not settle signedness; full class layouts, exact typedefs, underlying buffer operations, heap/EH and real file acceptance remain outside this correction. Independent review reproduced every sealed signature, transport and authored comment, including all old PRE pins and tag changes. No thunk dependent exists in the complete current function inventory.

Fresh PRE restoration, rehearsal, separate/sealed readbacks, seven actual
byte-stable refusal controls, independent review/root reproduction, live
readback and independently restored Archive A POST passed. All nine live
exports equal rehearsal. Both Open overloads remain unchanged; the previous
identity cohort owns their names. The [reader contract](../source-code/io/chunker-system.md)
separates interfaces, original-code experiments and runtime unknowns.

Working identity: `db.18684`, 18 files / 123,751,284 bytes,
inventory SHA-256 `3d3747eebb2094cf7caed6bffcefafd97faffb8ec365d5cd331572c197cf9974`; main database 73,449,472 bytes,
SHA-256 `4b64645063466390ade5bf0172789bf536a50275da7584e5792097a6d8d5b57c`. Restored resource-reader identity POST is PRE.
Independent POST: `/srv/archive-a/onslaught-ghidra-cold/2026-09-27-reader-abi/post-working`. Tracked checkpoint remains `745c00ad…`.
Private receipts: `local-lab/ghidra-first-training-20260907-v1/re-audit-20260926/reader-abi/`.

## RE-audit resource-reader identities — September 27

The [five-row manifest](../../tools/cohort-specs/resource-reader-identities-20260927.manifest.tsv) and
[spec](../../tools/cohort-specs/resource-reader-identities-20260927.spec.tsv) correct resource-loader
and reader identities against pristine `BEA.exe.original.backup`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.

Five names/comments/tags corrected: resource GetFileName and ReadResources, the two CChunkReader Open overloads, and CPCPlatform Deserialize. All 3,504 code bytes / 1,084 instruction rows, saved interfaces/storage/locals and 8,326 non-target function rows remain unchanged. Only the program comment digest changes. Earlier notes remain fallible leads, with the old platform numbering explicitly disproved.

Complete caller/source correspondence includes twelve literal-selected consumer calls, nine unconditional source clauses and three withheld conditional clauses. The checker rejects enclosing source conditions and internal calls bypassing the producer, and distinguishes visible RETs from complete cleanup. Current saved names are not identity evidence. Both Open overloads have one argument; parameter-spelling suffixes disambiguate them. Retail platform values are 1 PC, 3 PS2, 2 XBOX. The dispatcher has a third argument gating later payloads after metadata/MESH, a real level-minus-three early return and a VSDS call absent from the pinned PC source route. The PLAT normal path has four font allocations/deserializations, with a debug-font vtable distinct from the uniform class spelling in source. Independent review rejected the first sealed rehearsal for incorrect Open header citations and an insufficiently qualified retained platform mapping; it remains in rejected-v1. The corrected exact payload passed fresh PRE, rehearsal, separate/sealed readbacks and five no-write refusal controls. These names do not certify saved prototypes, missing concrete type aliases, full resource schemas or runtime loading.

Independent read-only exact-payload review, root reproduction, live readback
and independently restored Archive A POST passed. All nine live exports
equal rehearsal. The [reader/dispatch contract](../source-code/io/chunker-system.md)
separates these identities, source differences, bounded original-code reader
experiments and remaining payload/runtime questions. No other name or ABI
correction is implied by this cohort.

Working identity: `db.18683`, 18 files / 123,718,516 bytes,
inventory SHA-256 `b542325d1b1ba25ba0fbec7d9b608d37c3e3e2c6c44ee0695a3487172493c766`; main database 73,416,704 bytes,
SHA-256 `2e54b9c671e07af6885123d73b94dd3b3599ab70bbe34494bb92d810b7e37e96`. Restored memory-buffer ABI POST is PRE.
Independent POST: `/srv/archive-a/onslaught-ghidra-cold/2026-09-27-resource-reader-identities/post-working`. Tracked checkpoint remains `745c00ad…`.
Private gate receipts: `local-lab/ghidra-first-training-20260907-v1/re-audit-20260926/resource-reader-identities/`; byte/call/source evidence:
`local-data/test-runs/re-audit-20260926/resource-dispatch/`.

## RE-audit memory-buffer ABI — September 27

The [eight-row manifest](../../tools/cohort-specs/membuffer-abi-20260927.manifest.tsv) and
[spec](../../tools/cohort-specs/membuffer-abi-20260927.spec.tsv) correct six member interfaces
and their two direct thunk dependents, without changing names or code.
Specimen: pristine `BEA.exe.original.backup`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.

Eight saved interfaces corrected across six CDXMemBuffer bodies and two direct thunks. The destructor and its thunk gain implicit ECX receivers. InitFromMem, InitFromFile, Close, the Close thunk and EndOfFile change bool/AL:1 to int/EAX:4. Close, its thunk and EndOfFile keep the same physical ECX but normalize explicit fastcall to automatic thiscall receivers. Write size becomes signed int at unchanged Stack[8]:4. Every name, local, code byte, instruction, reference, bookmark and non-target variable stays unchanged; 8,323 non-target function rows remain exact. Argument cleanup and frame sizes stay unchanged. Prior notes remain fallible leads.

Complete pristine coverage is 2,002 bytes and 678 instructions. Pinned member declarations, full EAX exits/callers and the signed Write guard establish the declared transports. Exact typedef spelling and class layouts remain unproved; generic pointers are retained. The first six-row isolated rehearsal was rejected because saved thunks inherited two undeclared signature changes. That failed replica and its sealed inputs remain in rejected-v1; neither reached live. The root and independent reviewer then read both entire five-byte direct JMP bodies, declared their matching interfaces and repeated preservation/rehearsal on fresh PRE. A second read-only dry refused thunk rows under the original blanket rule; the replica was rechecked byte-equal to live/cold before reuse. The existing framework now requires each direct follower and its target to be declared, byte-checks the forwarding jump, compares their interface shapes and refuses any undeclared dependent before writes. Only the target receives a prototype write; followers are read back after all targets. Review also made the hexadecimal receiver offsets and JLE location/target explicit before sealing. The successful third rehearsal was withheld when independent review caught a stale two-receiver count in all eight proposed comments; its inputs/receipts remain in rejected-v3. The corrected comments name all three normalization entries, and fresh PRE rehearsal, readbacks and eleven controls were repeated before live. The retained 67 ReadString and 71 Write/Close original-code cases use authored buffers and intercepted APIs; no real Windows persistence or runtime handler acceptance follows.

Fresh PRE restoration, rehearsal, independent/sealed readbacks, eleven actual
byte-stable refusal controls, independent review/root reproduction, live
readback and independently restored Archive A POST passed. All nine live
exports equal rehearsal. Only `commentsSha256` changes at program scope.
The [memory-buffer contract](../binary-analysis/functions/DXMemBuffer.cpp.md)
separates these interfaces from isolated experiments and real I/O unknowns.

Working identity: `db.18682`, 18 files / 123,702,132 bytes,
inventory SHA-256 `fa1a50d9db128ced79095e102be468343007c7900f8d2739a3395d046bac3cd0`; main database 73,400,320 bytes,
SHA-256 `f4e975ce235e6166b78c47d1fc847f65b0a2390233d61b0f6db9c0be4bca8029`. The restored event-listener POST is PRE.
Independent POST: `/srv/archive-a/onslaught-ghidra-cold/2026-09-27-membuffer-abi/post-working`. Tracked checkpoint remains `745c00ad…`.
Private receipts: `local-lab/ghidra-first-training-20260907-v1/re-audit-20260926/membuffer-abi/`.

## RE-audit event-listener identities — September 27

The [sixteen-row manifest](../../tools/cohort-specs/listener-identities-20260927.manifest.tsv)
and [spec](../../tools/cohort-specs/listener-identities-20260927.spec.tsv) correct shared
`HandleEvent` interface identities from guarded retail calls and fixed RTTI.
Specimen: pristine `BEA.exe.original.backup`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.

Both complete guarded EventManager queue transports bind IListener slot 0 to the surviving CThing HandleEvent(CEvent*) declaration. The tool verifies the unique fixed primary RTTI chain, all holders, complete body/return cleanup, naming owner and collisions. Fresh RTTI and 169 table uses were checked; the sixteen renamed entries are all primary-offset handlers. Review corrected reversed CThing event-branch wording in the first private packet: 2000 reaches slot 2, 2002 reaches slot 50. Root reproduced the adverse implicit-register-write and indirect-jump controls; a diagnostic must be a decoded PUSH. The 75 focused evidence-tool cases passed. The first tool commit called that 90 incorrectly; the actual log and corrected VALIDATION record 75. Missing interface headers, default-path semantics, saved types and all runtime handler behavior remain uncertified.

The other proposed kept names are a separate cohort. Purecall, a shared no-op,
ambiguous owners, unresolved switch dispatches and two cached whole-image
instruction gaps are excluded. The latter gaps are not demonstrated Ghidra
boundary defects. Saved signatures remain unchanged, including known pointer
and return-type problems; no per-handler event semantics are inferred from an
interface name. EBP preservation across callbacks assumes the x86 ABI.

Fresh PRE restoration, rehearsal, separate/sealed readbacks, five actual
byte-stable refusal controls, independent read-only review/root reproduction,
live readback and independently restored POST passed. All nine live exports
match rehearsal. Exactly sixteen event-listener names/comments/tags corrected to the observed IListener HandleEvent interface. The complete 2,037 code bytes / 708 instruction rows, saved prototype types/storage, locals and 8,315 non-target function rows remain unchanged. Earlier notes remain fallible leads; saved pointer/return type defects, including CInfluenceMap float-as-event, are separate declared follow-up work. Only the program comment count (+7) and digest
change; the full current name projection is checked against live.

Working identity: `db.18681`, 18 files / 123,669,364 bytes,
inventory SHA-256 `f81a43030a7e5322f4f931615c48338baf7129fe233d13fb4c829c21fa0e8c34`; main database 73,367,552 bytes,
SHA-256 `3b57260d99b836abf90bb007fbe7a10f901678a496ad871d6e01094a4faec236`. Restored memory-buffer POST is PRE.
Independent POST: `/srv/archive-a/onslaught-ghidra-cold/2026-09-27-listener-identities/post-working`. Tracked checkpoint remains `745c00ad…`.
Private gate receipts: `local-lab/ghidra-first-training-20260907-v1/re-audit-20260926/listener-identities/`; interface/tool witnesses and rejected drafts:
`local-data/test-runs/re-audit-20260926/listener/`.

## RE-audit memory-buffer identities — September 27

The [five-row manifest](../../tools/cohort-specs/membuffer-identities-20260927.manifest.tsv) and
[spec](../../tools/cohort-specs/membuffer-identities-20260927.spec.tsv) replace descriptive aliases
with supported `CDXMemBuffer` source-method identities: SetNextReadBufferSize,
InitFromMem, ReadString, Write and EndOfFile. Specimen: pristine
`BEA.exe.original.backup`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.

Pristine complete bodies, the pinned nonvirtual header/definitions, source-named allocation anchors and shared field/consumer flows support SetNextReadBufferSize, InitFromMem, ReadString, Write and EndOfFile. Retail/source block-size, buffering and sidecar/compression differences are explicit. The 67 ReadString and 71 raw Write/Close original-code cases establish bounded consumption/failure behavior with authored buffers and checked API substitutes, not Windows/file acceptance. ReadString CR/non-LF and stale-byte behavior and Write/Close failure continuation are also present in partial-source control flow. Independent review confirmed every row and old-note suffix; a one-line source citation and hexadecimal-offset notation were corrected before resealing, with the first successful rehearsal preserved.

The [memory-buffer contract](../binary-analysis/functions/DXMemBuffer.cpp.md)
corrects the check-byte cursor/sidecar-slot layout and distinguishes static
compression findings from the two native experiments. Close returning one
after failed/short writes is not proof of persistence. No original file was
written and no game or Godot instance ran. All earlier plate notes are retained
exactly as fallible leads; old confidence tags do not certify unchanged types.

Fresh PRE restoration, revised rehearsal, separate/sealed readbacks, five
byte-stable refusal controls, independent review/root reproduction, live
readback and independently restored POST passed. All nine live exports equal
rehearsal. Exactly five CDXMemBuffer names/comments/tags corrected to source-supported method identities. The complete 1,262 code bytes / 423 instruction rows, saved prototype types/storage, locals and 8,326 non-target function rows remain unchanged. Earlier notes remain fallible leads; saved destructor/size/return-width ABI findings and seven retained-name comments are separate follow-up work. Only the program comment digest changes. The full
8,331-name projection is checked against live; frozen historical tables remain.

Working identity: `db.18680`, 18 files / 123,587,444 bytes,
inventory SHA-256 `cf87fbf3376ad7ee71e35e4fb401000f1e1ef17626df127d2558be0b2b340dfd`; main database 73,285,632 bytes,
SHA-256 `ff1050c9dfa44d7870887557b2016e0ab03055d6459820d2c223d0dd8abab267`. Restored class-name POST is PRE.
Independent POST: `/srv/archive-a/onslaught-ghidra-cold/2026-09-27-membuffer-identities/post-working`. Tracked checkpoint remains `745c00ad…`.
Private receipts: `local-lab/ghidra-first-training-20260907-v1/re-audit-20260926/membuffer-identities/`. Full persistence behavior, Windows I/O and
runtime decoder/CRC acceptance remain separate.

## RE-audit class-name getter identities — September 27

The [62-row manifest](../../tools/cohort-specs/class-name-identities-20260927.manifest.tsv) and
[spec](../../tools/cohort-specs/class-name-identities-20260927.spec.tsv) bind `_GetClassName` to
observed retail interface entries across the CThing family. Specimen: pristine
`BEA.exe.original.backup`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.

Pinned source `5352a81c`, `game.cpp:943`, copies the result of
`item->ToRead()->_GetClassName()`. The unique caller literal and active-reader
flow bind this to `0046d519`, primary slot 7. The exact 46-byte dispatch and
inlined string-copy sequence is checked. Each target has one zero-offset
CThing base, one RTTI holder and aligned non-code pointer cell, an exact
six-byte literal getter and an initially matching class-name string.
The method's leading underscore is retained, hence labels such as
`CThing___GetClassName`. Saved labels never supply identity evidence.

The 62 names replace 47 structural placeholders and 15 descriptive spellings.
All initial strings are in writable `.data`; immutability and source constness
are not asserted. Missing declaration macros/qualifiers and possible inlined
forwarding remain unresolved. All earlier plate notes are retained as fallible
leads. Fourteen inherited `signature-hardened` tags describe earlier metadata
work; they do not renew ABI certification. Prototype coverage does not increase.

The reviewed game.cpp:943 source call is bound to the pristine caller by its unique fatal-count literal, active-reader receiver flow and complete 46-byte virtual-dispatch/string-copy window. Every admitted getter has a unique fixed primary CThing base, one raw RTTI holder/slot 7, exact six-byte immediate-pointer/plain-RET body and matching initialized class literal. All literals are writable .data; runtime immutability, missing macro/declaration/qualifiers, possible inlined forwarding and saved prototypes remain unproved. Independent review found incomplete copy-tail and repeated-base guards in the draft matcher; both were fixed and covered by adversarial re-pinned inputs before sealing. All 85 focused evidence-tool cases passed. The existing generic header-vtable admission was not relaxed.

Fresh PRE restoration, rehearsal, separate/sealed readbacks, five byte-stable
refusals, independent review/root reproduction, live readback and independently
restored POST passed. All nine live exports equal rehearsal. Exactly 62 primary CThing-family class-name getter names/comments/tags corrected. The complete 372 code bytes / 124 instruction rows, all saved prototype types/storage, locals and 8,269 non-target function rows remain unchanged. Twenty-seven previously empty plate comments are added. Retained notes and undated ABI confidence tags are historical leads, not renewed prototype certification.
Only `comments` (+27) and `commentsSha256` change at program scope. The full
8,331-name projection is checked against live; frozen historical tables remain.

Working identity: `db.18679`, 18 files / 123,571,060 bytes,
inventory SHA-256 `1d781d6f26689c03519bccf8103c581981d10c6fd4dd451bc6f45626a3e2444b`; main database 73,269,248 bytes,
SHA-256 `b1150cc71145b4bb44f10eaf3f2968f243feb02fa2d070e04f47dd4c79360046`. The restored frontend ABI POST is PRE.
Independent POST: `/srv/archive-a/onslaught-ghidra-cold/2026-09-27-class-name-identities/post-working`. Tracked checkpoint remains `745c00ad…`.
Private receipts: `local-lab/ghidra-first-training-20260907-v1/re-audit-20260926/class-name-identities/`. Complete persistence behavior and retail runtime
acceptance are separate from these static interface identities.

## RE-audit frontend callback ABI — September 27

The [manifest](../../tools/cohort-specs/frontend-callback-abi-20260927.manifest.tsv) and
[spec](../../tools/cohort-specs/frontend-callback-abi-20260927.spec.tsv) correct three saved interfaces
without changing their names or the executable. Specimen: pristine
`BEA.exe.original.backup`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.

- `00468200` CFrontEnd Render: implicit ECX receiver, one stack DWORD,
  full-width int result; both direct callers push zero and test EAX. The source
  calls the unused argument forcerender. Retail omits the source's local 60 Hz
  elapsed-time gate; this does not establish global frame pacing.
- `0051be70` Intro TransitionNotification: implicit ECX receiver and one unused
  source-page DWORD. The old signature omitted the stack argument consumed by RET 4.
- `0051f700` Options Render: implicit interface receiver, float transition then
  other endpoint page at stack offsets 4/8, RET 8. The old stdcall prototype
  interpreted the float as a pointer and the page as a float. No class layout
  or missing enum definition is synthesized.

Complete three-body pristine comparison covers990bytes and278instructions, with raw interface tables, receiver installations and direct/common callers. Source force_render names an unused retail DWORD; its signedness/exact typedef is unproved, and retail lacks the source function-local60Hz throttle. Options and Intro identities were already promoted; this cohort changes only their ABI/comment/tag records. The first read-only dry refused empty-tag encoding without writes; it was preserved and replaced after confirming the replica still byte-equaled cold. Review made offset radices and Options unordered-to-zero behavior explicit. The first comparator omitted two derived frameSize changes; installed Ghidra source confirms their exact declared parameter-size dependency, and every unchanged local remains checked.

Fresh PRE restoration, rehearsal, independent/sealed readbacks, seven
byte-stable refusal controls, independent review/root reproduction, live readback
and independently restored Archive A POST passed. All nine live exports equal
rehearsal. Exactly three frontend interfaces corrected to dynamic thiscall: CFrontEnd Render and Intro TransitionNotification gain their missing four-byte stack argument; Options Render gains the implicit ECX interface receiver and reinterprets stack4 as float transition and stack8 as int other_page. Every name, return type/storage, local, body, instruction, reference, bookmark and non-target variable stays unchanged; 8,328 other function rows remain exact. Stack cleanup remains4/4/8. Render and Intro frameSize increase by4 solely because Ghidra computes localSize+parameterSize. Historical notes remain fallible leads. Only `commentsSha256` changes at program scope.
These are bounded ABI corrections; the complete page helpers and runtime remain
unvalidated. The existing [render note](../binary-analysis/functions/FrontEnd.cpp/CFrontEnd__Render.md)
records the source divergence and separate original-tail experiments.

Working identity: `db.18678`, 18 files / 123,407,220 bytes,
inventory SHA-256 `a572eba6a688f2774eb1c463c7a739caf1d926182bc3fdc4d37f5ec552096353`; main database 73,105,408 bytes,
SHA-256 `6033df536766f83d2545be99ed66b05e2a4aa602a37ec7ee247b9272e59e6184`. The restored 74-name frontend POST is PRE.
Independent POST: `/srv/archive-a/onslaught-ghidra-cold/2026-09-27-frontend-callback-abi/post-working`. Tracked checkpoint remains `745c00ad…`.
Private receipts: `local-lab/ghidra-first-training-20260907-v1/re-audit-20260926/frontend-callback-abi/`.

## RE-audit verified frontend page identities — September 27

The [manifest](../../tools/cohort-specs/frontend-page-verified-20260927.manifest.tsv) and
[spec](../../tools/cohort-specs/frontend-page-verified-20260927.spec.tsv) retain 74 already supported
names and attach their authored interface evidence and audit tags. The preceding
23 corrected entries and 35 withheld candidates are excluded.

Pristine specimen: `BEA.exe.original.backup`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
The seven reviewed surviving declarations, common retail callers and receiver installations from the preceding frontend cohort apply unchanged. Alignment v5 differs from v4 only in the full-export pin and the 23 already-promoted name/status outputs. All body, RTTI and admission structures remain identical. This cohort includes exactly the original 74 keep outputs, excluding those 23 renamed entries and all 35 withheld targets. All 74 complete bodies, 8,184 instructions and 29,477 bytes match pristine. The first seal was rejected before live for stale Intro Process category tags; the corrected rehearsal uses an independently restored, byte-identical PRE. The initial copied unique-owner preparation refused before sealing on shared entry 0051ae50; the revised retention check admits only an independently derived holder/method alias and explicitly records all nine uses, without selecting an exclusive defining class.

At `0051ae50`, nine page tables dispatch the same 28-byte slot-4 entry:
Level Select, Language Test, Directory, Virtual Keyboard, Multiplayer, Save Game,
Load Game, Dev Select and Goodies. The surviving Goodies declaration and common
pre-render caller independently establish RenderPreCommon. The retained
CFEPLanguageTest prefix is one valid RTTI holder alias, not proof of exclusive
source ownership or of which object file contributed the shared code. Complete
holder coverage and equal method identity are required before retaining it.

Fresh PRE restoration, rehearsal, separate/sealed readbacks, five byte-stable
refusal controls, independent review with root reproduction, live readback and
independently restored Archive A POST passed. All nine live exports equal
rehearsal. Exactly 74 existing frontend page-method names verified within bounded static interface identity limits, with authored comments and audit tags only, including correction of Intro Process category tags. Every saved name, prototype, variable, body, instruction, reference and bookmark stays unchanged; 8,257 other function rows remain exact. Older plate notes remain fallible leads. The shared RenderPreCommon entry lists all nine known page holders; its retained Language Test prefix is nonexclusive. All 8,184 instruction rows remain exact. Only
`commentsSha256` changes at program scope. Full page behavior, saved ABI types,
rendered appearance and runtime acceptance remain outside this identity batch.

Working identity: `db.18677`, 18 files / 123,374,452 bytes,
inventory SHA-256 `696da4a81bceb424c044147452806cd94e36e10b1c598e7d114d247f45d67d1f`; main database 73,072,640 bytes,
SHA-256 `6ee2f883e1eb0ec6cc09c7f45580e7c4f833d369d57e2f8fc7283a4caac0af17`. The restored 23-name frontend POST is PRE.
Independent POST: `/srv/archive-a/onslaught-ghidra-cold/2026-09-27-frontend-page-verified/post-working`. Tracked checkpoint remains `745c00ad…`.
Private receipts: `local-lab/ghidra-first-training-20260907-v1/re-audit-20260926/frontend-page-verified/`; raw method/RTTI proof remains in sibling
`frontend-page-identities/`.

## RE-audit frontend page identities — September 27

The [manifest](../../tools/cohort-specs/frontend-page-identities-20260927.manifest.tsv) and
[spec](../../tools/cohort-specs/frontend-page-identities-20260927.spec.tsv) correct 23 names and their
comments/tags. The common page interface distinguishes Init, Shutdown,
Process, ButtonPressed, RenderPreCommon, Render and TransitionNotification.
Examples: Options Update is Render; Wingmen Destroy is Shutdown; several
initialization/timer labels are TransitionNotification callbacks. Intro and
Multiplayer had misleading historical category tags, now corrected from their
retail RTTI and separate member installations.

Specimen: `BEA.exe.original.backup`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Pinned source `5352a81c`: explicit `CFEPGoodies` declarations and the common
`CFrontEnd` dispatch callers identify seven slots. The absent base header is
not reconstructed by guessing declaration order. Calls `00466522`, `0046690d`,
`00466dc4`, `00466a58`, `0046836f`, `00468415` and `00466b29` bind slots 0–6.
The Goodies member/table installation and common receiver array connect those
callers to raw RTTI; all known holders must agree and all admitted bodies must
pass bounded instruction/return checks. No saved name supplies identity.

Seven surviving CFEPGoodies declarations are bound to common retail virtual callers and the constructor/page-array receiver installation. No absent base-header layout or saved-name authority is invented. Complete known RTTI aliases, fixed zero-offset ancestry, bounded argument transport, complete instruction bodies and direct-tail cleanup are checked. Fresh PRE follows the reviewed Options instruction repair. Alignment v4 preserves every v2 proof structure with only the export pin changed; v3 omitted the macro profile and is retained as an unused attempt. The fresh 97-target proof covers 98 bodies, 10,814 instructions and 38,403 bytes. This 23-row subset has 2,573 instructions and 8,721 bytes. Seventy-four kept names await their separate comment cohort; 35 ambiguous or unsupported candidates remain withheld.

The first PRE attempt stopped before sealing on the Options split instruction;
its records and pre-repair drivers remain preserved. That structural defect was
promoted separately before this fresh PRE. This exact cohort passed rehearsal,
separate/sealed readbacks, five byte-stable refusals, independent method and
payload review with root reproduction, live readback and independently restored
Archive A POST. All nine live exports equal rehearsal. Exactly 23 frontend page names corrected to independently proven common-interface identities, with authored comments and tag corrections. Displaced names and older notes remain fallible leads. All prototypes, types, conventions, storage, bodies, instructions, references and bookmarks stay unchanged; 8,308 other function rows remain exact. Intro/multiplayer category tags and Wingmen Shutdown versus destructor are corrected. Names do not establish complete behavior or certify the two separately recorded ABI defects.
All 2,573 target instruction rows remain exact. Program changes are confined to
comment content and four newly added plate comments; symbol-source counts and
all other program metrics remain unchanged.

Options and Intro saved argument layouts remain separately recorded ABI defects;
this identity promotion does not bless them. Rendered behavior, full helpers,
real clock pacing, sound and player acceptance remain outside this cohort.
The Options original-tail experiment is documented in the existing render note.

Working identity: `db.18676`, 18 files / 122,932,084 bytes,
inventory SHA-256 `438595cd2a659d71dde6f37fad952855eab5fb2799d4cfa7bcd9798afceff70c`; main database 72,630,272 bytes,
SHA-256 `06a8d6f90b352e7d35a2addce79edd4c28384fcfd6dcb71443aeb7853508d9d4`. The restored Options instruction POST is PRE.
Independent POST: `/srv/archive-a/onslaught-ghidra-cold/2026-09-27-frontend-page-identities/post-working`. Tracked checkpoint remains `745c00ad…`.
Private receipts: `local-lab/ghidra-first-training-20260907-v1/re-audit-20260926/frontend-page-identities/`.

## RE-audit Options instruction repair — September 27

The [manifest](../../tools/cohort-specs/frontend-options-instruction-20260927.manifest.tsv) and
[spec](../../tools/cohort-specs/frontend-options-instruction-20260927.spec.tsv) repair the saved listing
within `[0051f7be,0051f7c6)` in the existing Options render function. The
frontend name preparation refused before sealing because the old listing
contained instruction starts at `0051f7c0` and `0051f7c2`, separated by four
undefined bytes. Fresh pristine decoding establishes one eight-byte MOV
writing float 1.0 into the first stack argument. Both existing conditional
branches at `0051f771` and `0051f776` target its correct start. The successor
at `0051f7c6`, RET 8 at `0051f7d8` and 219-byte function body stay unchanged.

Pristine specimen: `BEA.exe.original.backup`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
The eight-byte span hashes to `25725d401eefab6ee1b43edfcf8209285b9daa48b1b17e3994e00e960b17e625`;
the complete body hashes to `12d6f1309699a794d9dd19f8ce7d169e0a1fb5c916782ade5f820f8e66359e6e`.
An independent raw-byte review was reproduced; a separate read-only Ghidra
inspection confirmed the actual units and incoming references, with no saved
interior metadata. This repairs analysis, not retail executable bytes.

The existing promotion framework now has a standalone instruction-gap verb.
Its old geometry verbs require body growth and could not express this repair.
Review caught possible loss of equates, outgoing references and undefined-data
settings, a non-function preflight bypass and delay-slot range expansion. The
final tool refuses these cases, pins the exact PRE layout/bytes and POST
instruction, and freezes code/references outside the range and all function
metadata. Root checked the relevant installed Ghidra clearing implementation.
The 94 framework tests include real Java gate execution (valid PRE/POST, 19
refusals and equal-count outside-code/reference controls). Six malformed-input
checks on actual disposable databases refused without changing a project byte.

The first isolated repair passed. After hardening the tool, a fresh PRE copy
reproduced the same nine exports; the earlier spec and receipts remain private.
The independent export comparator initially demanded byte-identical function
rows, then was corrected to admit exactly the target's measured `instrCount`
69→68. It admits no other function-field change. Live dry/apply/separate
readback and independently restored Archive A POST passed. One saved instruction-layout defect repaired in Options render at [0051f7be,0051f7c6): two misaligned instructions and four undefined bytes replaced by one eight-byte MOV. No executable bytes, function names/prototypes/comments/tags/bodies, references, locals, types, bookmarks or symbols changed. Only the target instruction count and program instruction-layout/undefined-byte metrics changed. This is static analysis repair, not retail runtime acceptance.
All 67 other target instructions and all nine live/rehearsal exports agree.
Names and ABI defects remain for separate frontend cohorts; audit name counts
do not increase for this structural repair.

Working identity: `db.18675`, 18 files / 122,801,012 bytes,
inventory SHA-256 `41cf3db276c5876058f381d46592b877351271718ded629377e0b4051696448e`; main database 72,499,200 bytes,
SHA-256 `f81c8b9b004acc40b7b4403e14d507426473a6c68dc45d1bfbf6eb699ccb92b9`. The verified compiler deleting-entry POST served as PRE.
Independent POST: `/srv/archive-a/onslaught-ghidra-cold/2026-09-27-frontend-options-instruction/post-working`. Tracked checkpoint remains `745c00ad…`.
Private receipts: `local-lab/ghidra-first-training-20260907-v1/re-audit-20260926/frontend-options-instruction/`.

## RE-audit verified compiler deleting entries — September 27

The [manifest](../../tools/cohort-specs/compiler-destructor-verified-20260927.manifest.tsv) and
[spec](../../tools/cohort-specs/compiler-destructor-verified-20260927.spec.tsv) verify 80 existing names
within the preceding compiler-entry proof's limits, changing comments and tags
only. The 33 already normalized entries and seven withheld entries are excluded.
All names and prototypes remain unchanged; this is an identity disposition,
not full destructor, ABI or runtime validation.

Pristine specimen: `BEA.exe.original.backup`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
The exact 32-byte compiler body calls cleanup with original this, tests bit 0
of the low byte in its first four-byte stack argument, conditionally frees
unchanged this through `00549220` on manager `009c3df0`, returns this in EAX
and executes RET 4. Nonexclusive naming context comes from all known fixed
zero-offset CMonitor slot-1 RTTI holders, never the saved name itself.
Normal-return teardown is bounded to the reviewed CMonitor base, a dominating
original-this call or a stack-neutral direct tail. Full member cleanup,
exception paths, callee ABI compliance and saved prototype types remain open.

The fresh PRE function export and source/specimen pins bind admission v4.
Root and the independent reviewer compared every body/RTTI/admission structure
with v3: they are identical; only the export pin and 33 already promoted
name/status outputs differ. The preceding fresh 5,590-instruction proof is
therefore reused, while all 80 current wrappers, 880 instruction rows and
2,560 bytes are checked against pristine again. CMonitor itself correctly uses
the reviewed-base case. Older plate text remains explicitly fallible; for
example, CRound's old RET 8 note is retained as a lead below the corrected
RET 4 entry evidence, not endorsed as current behavior.

Independent review confirmed the exact 80-row scope and authored payload,
and found a copied 14-row assertion in the private comparison helper. It was
corrected to 80 before the root comparison ran; no payload or seal changed.
Fresh PRE restoration, rehearsal and separate/sealed readbacks, five byte-stable
refusal controls, root reproduction, live readback and independently restored
Archive A POST passed. All nine live exports equal rehearsal.
Exactly 80 existing compiler scalar-deleting-entry names verified within bounded static identity limits; comments/tags updated without renames or prototype changes. Earlier plate notes remain explicitly fallible leads. All names, prototypes, types, conventions, storage, bodies, instructions and bookmarks remain unchanged; 8,251 non-target function rows remain exact. No new gameplay or runtime acceptance is claimed. All 880 target instructions remain exact. Program-scope change
is only `commentsSha256`.

Working identity: `db.18674`, 18 files / 122,801,012 bytes,
inventory SHA-256 `c4c94e00cae487891d3814e604f3396bfac7cb5daf8b6278460d8e46e931ce5c`; main database 72,499,200 bytes,
SHA-256 `40d1410afd7805ee48158e294635fce2d14fd64325cfaf3c2d427b55b0081106`. The preceding compiler identities POST served as PRE.
Independent POST: `/srv/archive-a/onslaught-ghidra-cold/2026-09-27-compiler-destructor-verified/post-working`. Tracked checkpoint remains `745c00ad…`.
Private receipts: `local-lab/ghidra-first-training-20260907-v1/re-audit-20260926/compiler-destructor-verified/`; shared proof evidence is in sibling
`compiler-destructors/`. The six shared-context entries and CUnit collision
remain excluded pending their own evidence-backed disposition.

## RE-audit compiler deleting-entry identities — September 27

The [manifest](../../tools/cohort-specs/compiler-destructor-identities-20260927.manifest.tsv) and
[spec](../../tools/cohort-specs/compiler-destructor-identities-20260927.spec.tsv) normalize 33 names and update
their comments/tags. These were mostly already called deleting destructors;
the new work independently verifies their identity and standardizes spelling.
CSentinelAI's contradictory slot-0 tag is corrected to slot 1.

The pristine specimen is `BEA.exe.original.backup`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
`CThing` source at pinned `5352a81c` and the complete retail chain
`004f3480 → 004f3640 → 004bac40` identify the CMonitor slot-1 entry
`00419a20` at table `005d92d4`. Free at `00549220` on manager `009c3df0`
matches the pinned allocator's null/tiny-pool/type-selected release structure.
Each admitted wrapper calls its cleanup with original this, tests bit 0 of
the low byte in its four-byte stack argument, conditionally frees unchanged
this, returns this in EAX and executes RET 4. This does not select a source
integer type for the flag or certify the saved prototype.

The existing evidence tool checks the exact compiler pattern, complete
boundaries, fixed zero-offset ancestry, every known raw RTTI holder and a
normal-flow base-teardown proof. Explicit returns need a dominating call with
original this; direct tails require unchanged this and a stack-neutral prefix.
The CMCMech backward block is included through CFG analysis. A closed set of
supported opcodes avoids false register provenance from XADD or implicit writes.
An independent review found that false-admission case before promotion; the
corrected checker and adverse cases passed 69 focused evidence-tool tests.

The family report contains 120 wrappers, 165 mapped slot uses and 113 admitted
identities: these 33 renames and 80 pending kept-name comments. Six ambiguous
folded owners and the CUnit occupied-name collision are withheld. Broader
compiler matches outside this family need independent family evidence.
Root freshly recovered all 724 recognized RTTI tables and read every mapped
slot; fresh PE disassembly matches all 5,590 instructions in the 227 admitted
entry/cleanup proof bodies. Independent research separately checked raw RTTI,
seed/source/allocator evidence and sampled teardown paths. These results do
not establish exhaustive RTTI discovery, complete cleanup, exception behavior,
callee ABI compliance or retail runtime acceptance.

The first seal had stale September 26 audit tags and is retained in
`rejected-v1/`; it never reached live. The corrected exact cohort passed fresh
PRE restoration, rehearsal and separate/sealed readbacks, five byte-stable
refusal controls, independent review with root reproduction, live readback and
an independent Archive A POST restore. All nine live exports equal rehearsal.
Exactly 33 proven compiler deleting-entry labels normalized to the project scalar_deleting_dtor spelling; comments/tags updated and CSentinelAI slot tag corrected from 0 to 1. Every displaced label and plate note remains an explicitly fallible lead. No prototype, type, convention, storage, body, instruction, bookmark or non-target row changed; 8,298 other function rows remain exact. These are identity dispositions, predominantly spelling normalizations, not 33 newly discovered behavioral defects. All 363 target instruction rows are unchanged. Program-scope
change is only `commentsSha256`.

Working identity: `db.18673`, 18 files / 122,506,100 bytes,
inventory SHA-256 `099b1a8f38ba3c90be5cc8f324eb548d530b470a25c77d54e7375e93e6a977c9`; main database 72,204,288 bytes,
SHA-256 `067649503a478f0f8d463d6e416ea18eae42bd51bac21e055b8d75167fdd0dc9`. Restored Controller/Engine POST served as PRE.
Independent POST: `/srv/archive-a/onslaught-ghidra-cold/2026-09-27-compiler-destructor-identities/post-working`. Tracked checkpoint remains `745c00ad…`.
Private receipts: `local-lab/ghidra-first-training-20260907-v1/re-audit-20260926/compiler-destructor-identities/`; compiler evidence is in its sibling
`compiler-destructors/`.

## RE-audit verified Controller and Engine identities — September 27

The [manifest](../../tools/cohort-specs/controller-engine-verified-20260927.manifest.tsv) and
[spec](../../tools/cohort-specs/controller-engine-verified-20260927.spec.tsv) change 14 comments/tag sets,
retaining all names. Twelve explicit source/body anchors and raw table words
cover all 15 known RTTI uses. All 643 target instruction rows match pristine
`BEA.exe.original.backup`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.

Nine Controller identities are bound individually because the source header's
15 slots do not describe retail's 18-slot layout. The
[Controller contract](../binary-analysis/cpccontroller-vtable-semantics-2026-08-11.md#september-27-joystick-and-recording-recheck)
records signed upper-only pad guards, RightY's earlier indexed flag access,
exact x87 scaling and three-DWORD Record/Read transfers. The source's four
further analogue transfers are absent in these retail bodies. No device input
or recording file was exercised by this cohort.

Five [Engine methods](../source-code/core/engine-system.md#september-27-retail-initialization-recheck)
retain their names with corrected evidence. Init and InitResources occupy
slots 1 and 2 of `0x005e4fc4`; their old slot tags are replaced. Direct CGame
calls are not virtual dispatch. KempyCube was incorrectly described as a HUD
allocation. The `Sun Sprite` particle descriptor is not established physics
node data. Source screen-texture/capture and basicpanel operations omitted
from the inspected retail bodies are documented as local divergences.

Exactly 14 existing names retained and verified within static identity limits: nine Controller methods and five Engine methods. Comments/tags only; two Engine slot tags corrected. All names, prototypes, conventions, storage, parameters, locals, types, bookmarks, bodies, instructions and all 8,317 non-target rows preserved. Historical notes remain marked leads. Only program `commentsSha256` changes. Exact fresh PRE,
rehearsal/separate and sealed readback, five byte-stable refusal controls,
independent semantic/payload and preservation reviews with root reproduction,
live readback and independent POST restoration passed. All nine live exports
equal the reopened rehearsal. These are static identity/comment dispositions,
not certification of every existing prototype or full behavioral equivalence.

Working identity: `db.18672`, 18 files / 122,325,876 bytes,
inventory SHA-256 `3993994fe38f6de587da64c309a013cfb9bc1a4039cdfdfad8f14143db48d378`; main database 72,024,064 bytes,
SHA-256 `473a138be77ec7652ac21d4815f5a82c71a0c2eeeba5ee287c572571ebee45c5`. Freshly restored header-interface POST served as PRE.
Independent POST: `/srv/archive-a/onslaught-ghidra-cold/2026-09-27-controller-engine-verified/post-working`. Tracked checkpoint remains `745c00ad…`.
Private receipts: `local-lab/ghidra-first-training-20260907-v1/re-audit-20260926/controller-engine-verified/`.

## RE-audit header interface identities — September 26

The [manifest](../../tools/cohort-specs/header-interface-identities-20260926.manifest.tsv) and
[spec](../../tools/cohort-specs/header-interface-identities-20260926.spec.tsv) correct 16 identities:
15 initializer Copy/Load bodies and `CDXEngine::ShutDown`. Seven independently
reviewed source/byte anchors establish the interfaces; all 27 known target uses
across 15 RTTI tables agree. The admitted report has five additional kept Engine
names and a shared Sphere/Unit Copy body; those six targets are not mutated here.
Saved names are not alignment inputs. All 2,045 target instruction rows match
pristine bytes. Slot, alias, source-width and complete-body checks passed.

The case-distinct `ShutDown` appends Engine slot 3 rather than overriding base
`Shutdown` in slot 0. The old slot-2 tag is corrected. Squad's typed Copy has
slot 2; its base-pointer overload in slot 0 omits Squad-specific fields.
The [initializer contract](../game-mechanics/world-initializer-copy-load.md)
records selective copies, version-dependent loads and signed-byte string loops.
Eight unchanged original Copy bodies separately passed 64 isolated cases;
that experiment does not execute loaders or establish complete game loading.

The first seal is retained under `rejected-v1/`. Independent review rejected
four draft comments: the old base Load arm reads no strings, Start fields are
plane mode/player number, and Wall Copy/Load handle a wall-type string. Root
reproduced every correction. The replacement seal passed fresh PRE restoration,
rehearsal, separate and sealed readback, five byte-stable refusal controls and
independent exact-payload review. No rejected comment reached the live project.

Exactly 16 function names, nonrepeatable comments and tag sets corrected: 15 initializer Copy/Load identities and case-distinct CDXEngine::ShutDown. Seven source/byte anchors establish the interfaces; every known RTTI use and owner is checked. Every prototype, storage, parameter, local, type, bookmark, instruction and body and all 8,315 non-target function rows are preserved. Earlier names and notes remain fallible leads. Program comment count increases by 2; only that metric and
`commentsSha256` change. All nine live exports equal separately reopened
rehearsal. Live readback and independently restored Archive A POST passed.
No checkpoint refresh, prototype certification or retail runtime launch occurred.
The evidence tool now withholds unknown source cleanup and destructor entry
kinds; it cannot borrow a purecall seed's return cleanup as an ABI proof.

Working identity: `db.18671`, 18 files / 122,276,724 bytes,
inventory SHA-256 `829ef9cee960b6d43cf404dd24c1c4e36355f65629ddbe3815f48d476296a285`; main database 71,974,912 bytes,
SHA-256 `a686cbc760cc5754575b05e76c7f0bf6be0060aa65d6c082d02dc9c95b99500e`. PRE is the restored verified-Thing POST.
Independent POST: `/srv/archive-a/onslaught-ghidra-cold/2026-09-26-header-interface-identities/post-working`. Tracked checkpoint remains `745c00ad…`.
Private receipts: `local-lab/ghidra-first-training-20260907-v1/re-audit-20260926/header-interface-identities/`.

## RE-audit verified Thing-family identities — September 26

The [manifest](../../tools/cohort-specs/thing-virtual-verified-20260926.manifest.tsv) and
[spec](../../tools/cohort-specs/thing-virtual-verified-20260926.spec.tsv) retain 65 existing names and
refresh their identity evidence, nonrepeatable comments and tags. They are the
original kept-name proposals from the preceding Thing-family alignment, excluding
its 205 promoted renames. Fresh source/RTTI alignment and independent review cover
727 table uses, 62 tables and all 7,962 target instruction rows. Root rechecked the
pristine table words and reproduced the consequential comment corrections.

Five older claims needed attention:

- Carver Init's saved body is already recovered through `RET 4` at `0x00422555`;
  its old truncated-prologue claim is stale. This cohort changes no boundary.
- GroundAttackAircraft Init occupies slot 9 of primary table `0x005e2bcc`;
  `0x005e2bf0` is its slot cell, not a table start.
- Sentinel Init likewise occupies slot 9 of `0x005e08e0`, not slot 0 of
  `0x005e0904`. Its incorrect slot tag is replaced.
- ComplexThing's call at `0x004f4102` is reached for every nonzero initialization
  mode, although only mode 1 copies the authored matrix. Calling the entire arm
  the authored-matrix path was too narrow.
- Static list insertion and direct-caller counts do not prove unique Thing
  receiver lifetimes. The old repeated-initialization impossibility inference is
  withheld pending a trace of receiver identity, repeated Init and intervening
  removals. Historical TTD counts are retained, not revalidated; retired recordings
  cannot be queried again.

All older notes remain explicitly unverified leads. Source-identity uncertainty
tags are retained: proving a virtual method's identity does not establish every
body claim or its exact correspondence with the partial source. The static
specimen is the pristine `BEA.exe.original.backup`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.

Exactly 65 existing virtual-method identities verified and their nonrepeatable comments and tags updated. Five stale comment claims are corrected or explicitly qualified; the Sentinel Init slot tag changes from 0 to 9. Every name, prototype, calling convention, storage, parameter, local, type, bookmark, instruction and body and all 8,266 non-target function rows are preserved. Earlier notes remain explicitly fallible leads. Only `commentsSha256` changes at program scope. All nine live
exports equal the separately reopened rehearsal. Fresh PRE restoration,
dry/apply/separate and sealed readback, five byte-stable refusal controls,
independent read-only reviews, live readback and independently restored POST
passed. No checkpoint refresh or runtime launch occurred.

Working identity: `db.18670`, 18 files / 122,194,804 bytes,
inventory SHA-256 `ea7742b0070f2d13a6f8be860b588d0ad53660ee8ee7e586b5b0ddfb60d26824`; main database 71,892,992 bytes,
SHA-256 `6df6f0d82c340572c07244f256360217ae2b9239b8031812dc68ba0c9fcd6cbb`. PRE is the restored Thing virtual-identity POST.
Independent POST: `/srv/archive-a/onslaught-ghidra-cold/2026-09-26-thing-virtual-verified/post-working`. Tracked checkpoint remains `745c00ad…`.
Private receipts: `local-lab/ghidra-first-training-20260907-v1/re-audit-20260926/thing-virtual-verified/`.

## RE-audit Thing-family virtual identities — September 26

The [manifest](../../tools/cohort-specs/thing-virtual-identities-20260926.manifest.tsv) and
[spec](../../tools/cohort-specs/thing-virtual-identities-20260926.spec.tsv) correct 205 method identities.
Twenty-nine anchors were re-derived from pristine instructions, source declarations,
script registrations and observed virtual call sites, then independently reviewed.
Fixed RTTI inheritance carries those slots through 1,677 table uses and 298 distinct
targets. Saved names were never alignment inputs. The strengthened admission tool
supports 205 rename proposals and 65 existing-name proposals; 28 targets are withheld
for unresolved dispatch, alias or owner evidence. Only the 205 renames are promoted.

Notable corrections include `CAirUnit__dtor_base` to `CAirUnit__Shutdown` (the
deleting destructor has a separate slot/body), `CCarver__Fire` and
`CSentinel__Deactivate` to their animation-completion callback identities, and
`CBattleEngine__ResetAndSetActiveReader` to `CBattleEngine__DeclareOnObject`.
The latter matches the source receiver/standing-object call chain. These names
describe the virtual interfaces; earlier descriptive behavior notes remain leads.
Script `Stop` calls `GoToPoint` with the current position, so its name is not proof
of the virtual `Stop` slot. The Actor `Stop` body zeros XYZ but copies an
uninitialized fourth stack word. Numeric flag masks come from the retail bytes.

Independent reviews covered all 29 anchors, the propagation/admission method,
every flagged alias/owner case, representative surprising overrides and all encoded
comments. Root reproduced the byte witnesses and all 1,677 fresh RTTI table words.
Adversarial controls hardened decoding, branch, tail-stack and argument-width checks.
The first seal was retained under `rejected-v1/`: two flag-mask comments needed
explicit hexadecimal notation. The corrected seal repeated the preservation gate.
A parent command ended with exit 143 after the live read-only dry receipt; no apply
command had begun. Working bytes were rechecked equal to cold PRE before the exact
apply/readback steps resumed. The termination cause was not established.
This is static identity evidence, not full stack/type/behavior or runtime proof.
Unknown prototypes and unreviewed retained notes remain in the audit queue.

Exactly 205 function names, nonrepeatable comments and tag sets are corrected
through reviewed CThing, CComplexThing and CActor virtual-slot anchors and fixed
RTTI inheritance. Every prototype shape, calling convention, storage, parameter,
local, type, bookmark, instruction and body and all 8,126 non-target function
rows are preserved. Earlier names and notes remain fallible leads.
Program comment count increases by 33; only that metric and
`commentsSha256` change. All nine live exports equal separately reopened rehearsal.
Fresh PRE restoration, dry/apply/separate readback, sealed readback, five byte-stable
refusal controls, independent review, live readback and independently restored POST
passed. No checkpoint refresh or runtime launch occurred.

Working identity: `db.18669`, 18 files / 121,932,660 bytes,
inventory SHA-256 `9d3698fc7228741547cd7f5c6f306ec409f640696a76f98a8c46be0173b8a80e`; main database 71,630,848 bytes,
SHA-256 `193408a2ebb40d55812f06ced45782f7d7ef2e4beb88774f766afe30d91e0544`. PRE is the restored cockpit-shake POST.
Independent POST: `/srv/archive-a/onslaught-ghidra-cold/2026-09-26-thing-virtual-identities/post-working`. Tracked checkpoint remains `745c00ad…`.
Private receipts: `local-lab/ghidra-first-training-20260907-v1/re-audit-20260926/thing-virtual-identities/`.

## RE-audit cockpit shake ABI — September 26

The [manifest](../../tools/cohort-specs/cockpit-shake-abi-20260926.manifest.tsv) and
[spec](../../tools/cohort-specs/cockpit-shake-abi-20260926.spec.tsv) correct
`CCockpit__AddShockShake`'s argument from `int randomRange` to `float amount`.
FDIV reads the stack slot as binary32; its caller passes already-capped float
bits. The [function contract](../binary-analysis/functions/Cockpit.cpp/CCockpit__AddShockShake.md)
records the independent CRT RNG stream, four replacement writes and three-component
clamp. Forty-one bounded original-code cases include the engine/cockpit chain;
at amount 0.25 the unclamped fourth component is -0.1171875.

Exactly one explicit parameter is corrected from int randomRange to float amount in CCockpit__AddShockShake, with a corrected comment and tag set. The four-byte stack slot, automatic ECX receiver, void return, names, locals, types, bookmarks, instructions and all 8,330 non-target function rows remain unchanged. The exact variable comparison preserves every storage and local;
only this explicit parameter's name and type change. Five protected exports are
byte-identical. All nine live exports equal separately reopened rehearsal.
Fresh PRE, rehearsal, separate/sealed readback, seven byte-stable refusal
controls, independent review with root reproduction, live readback and
independently restored POST recovery passed. Authored objects and substituted
CRT thread-data provision do not establish Windows TLS, rendered movement,
physical rumble or complete-game acceptance.

Working identity: `db.18668`, 18 files / 121,408,372 bytes,
inventory SHA-256 `239157fd1d6ad443e1ba5a0e8bc8db666889d23f900312b3ddd37173e2b4c1cc`; main database 71,106,560 bytes,
SHA-256 `ef45ff511dc864ca1c4b81ff338177ddc9cf6ad764c1085823aa7279bb4445b2`. PRE is the restored Damage/shake-comment POST.
Independent POST: `/srv/archive-a/onslaught-ghidra-cold/2026-09-26-cockpit-shake-abi/post-working`. Tracked checkpoint remains `745c00ad…`;
no checkpoint refresh. Private receipts: `local-lab/ghidra-first-training-20260907-v1/re-audit-20260926/cockpit-shake-abi/`.

## RE-audit damage and shake comments — September 26

The [manifest](../../tools/cohort-specs/damage-shake-comments-20260926.manifest.tsv) and
[spec](../../tools/cohort-specs/damage-shake-comments-20260926.spec.tsv) correct the Damage and
Battle Engine shake comments/tag sets. Exactly two nonrepeatable comments and tag sets corrected: CBattleEngine__Damage and CBattleEngine__AddShockShake. Every name, signature, storage, variable, type, bookmark, instruction, body and all 8,329 non-target function rows are preserved.

Damage's old plate miscopied three offsets; the retained Level 521 observations
already had the correct map. Frozen receipts and the historical applier remain
unchanged. Complete pristine bodies, callers and 41 isolated original-code cases
now distinguish positive damage from the common repair/tail path, late
invulnerability restoration, floating conversion, shake thresholds and separate
game/CRT RNG streams. See the [Damage contract](../binary-analysis/functions/BattleEngine.cpp/CBattleEngine__Damage.md).
The cockpit's demonstrated float parameter is a separate ABI cohort.

Fresh PRE, rehearsal, separate/sealed readback, five byte-stable refusal
controls, independent review with root reproduction, live readback and
independently restored POST recovery passed. The first seal and rehearsal
remain in `rejected-v1/`: review corrected an overstated threshold distinction,
the monitored block radix and the NaN-shield wording before any live write.
All nine live exports equal rehearsal; only the program comment digest changes. Explicit death/thread-data
substitutes and a null attacker bound the experiment; full-game death/flash,
Windows, rendering, devices and player acceptance remain open.

Working identity: `db.18667`, 18 files / 121,408,372 bytes,
inventory SHA-256 `6e63e7af99a81bf68839f3cd5a35a6a66ebcff9ed4e06860535bfe6b28e82185`; main database 71,106,560 bytes,
SHA-256 `5ce637a154a82672a1af2f55d7c188bdd0099674ae8768f31b020728859fecda`. PRE is the restored startup-identity POST.
Independent POST: `/srv/archive-a/onslaught-ghidra-cold/2026-09-26-damage-shake-comments/post-working`. Tracked checkpoint remains `745c00ad…`;
no checkpoint refresh. Private receipts: `local-lab/ghidra-first-training-20260907-v1/re-audit-20260926/damage-shake-comments/`.

## RE-audit startup identities — September 26

The [manifest](../../tools/cohort-specs/startup-identities-20260926.manifest.tsv) and
[spec](../../tools/cohort-specs/startup-identities-20260926.spec.tsv) correct four identities:
`CCLIParams__GetParams`, `CPCController__ctor`, `CPCPlatform__InitFonts`
and `CPCSoundManager__DeviceInit`. Pristine bodies, callers and RTTI support
the pinned-source counterparts without importing source-only arguments or
behavior. The controller has three explicit arguments; the font filename is
`font22.512.tga`, with a distinct debug font and cleared Xbox slots; sound
initialization uses 64 slots and quality-dependent primary output. The numeric
source-line overlap with PlaySound was a false lead. The sound-device index
check normalizes only values at or above the count, not negative indices.

Exactly four function names, nonrepeatable comments and tag sets corrected: CCLIParams__GetParams, CPCController__ctor, CPCPlatform__InitFonts and CPCSoundManager__DeviceInit. Every prototype shape, calling convention, storage, parameter, local, type, bookmark, instruction and body and all 8,327 non-target function rows are preserved. Only `commentsSha256` changes among program metrics. All nine
live exports equal the separately reopened rehearsal. Fresh PRE restore,
rehearsal, sealed readback, five byte-stable refusal controls, independent
review with root reproduction, live dry/apply/readback and independently
restored POST recovery passed. Earlier plate text remains explicitly marked
as a lead; the incorrect font spelling and broad index-clamp claim are corrected.
This cohort establishes static identity and documented differences, not retail
startup, rendering, device or audible acceptance.

Working identity: `db.18666`, 18 files / 121,408,372 bytes,
inventory SHA-256 `4129420634535b7e36ba6df6b78cc2f410c73409b3a20ffacf5025ca38b4533f`; main database 71,106,560 bytes,
SHA-256 `0d92337f04386ea1a4723db0f111deac32ba86736487e2bee8bcb790000d5f1f`. PRE is the freshly restored keyboard-query POST.
Independent POST: `/srv/archive-a/onslaught-ghidra-cold/2026-09-26-startup-identities/post-working`. Tracked checkpoint remains `745c00ad…`;
no checkpoint refresh. Private receipts: `local-lab/ghidra-first-training-20260907-v1/re-audit-20260926/startup-identities/`.

## RE-audit keyboard query ABI — September 26

The [manifest](../../tools/cohort-specs/input-key-abi-20260926.manifest.tsv) and
[spec](../../tools/cohort-specs/input-key-abi-20260926.spec.tsv) correct four query interfaces:
`00514850`, `00514870` and `00514890` gain their virtual ECX receiver and
full-EAX integer return; `00513a80` retains its AL return storage with a raw
unsigned-byte type. Every explicit key stays at stack `+4`; no source-only
pad-number argument is added. The third table is release-event state; its old
held-state/source-KeyOn identification is explicitly marked disproved. Neutral
saved names remain where historical spelling is unknown.

Exactly four keyboard-query prototypes, plate comments and tag sets corrected. Three virtual wrappers gain automatic ECX receivers and int/EAX returns; the raw release helper retains AL storage as uchar. All explicit key parameters remain at stack +4. Every name, body, instruction, local, type and bookmark, all stack metadata and all 8,327 non-target function rows are preserved. Five protected exports are byte-identical; every variable row
matches the declared return/automatic-receiver change. All nine live exports
equal the separately reopened rehearsal. Fresh PRE restoration, seven byte-stable
no-write refusals, independent review, live readback and independently restored
POST recovery passed. The first isolated seal and rehearsal remain in
`rejected-v1/` because the historical-note introductions needed clearer
disproved-claim wording; that seal never reached the working project.

The [keyboard contract](../binary-analysis/cpccontroller-vtable-semantics-2026-08-11.md#september-26-keyboard-recheck)
records pristine instruction/caller evidence and 27 original-code cases with
135 operations. The pump's message/device/timer/pad dependencies were explicit
substitutes. These are bounded ABI and internal-state findings, not Windows
event delivery, physical-input or rebuild acceptance.

Working identity: `db.18665`, 18 files / 121,408,372 bytes,
inventory SHA-256 `97863cea4c23c6b0894d6ac9d6301b8a0353a5628c19d4df8ece8579c3957a87`; main database 71,106,560 bytes,
SHA-256 `748d0dbd2cbd7ed9c59f97ffe2e7c1b52a7a953364bdc4f508ac127d8f04f3f5`. PRE is the freshly restored library-comment POST.
Independent POST: `/srv/archive-a/onslaught-ghidra-cold/2026-09-26-input-key-abi/post-working`. Tracked checkpoint remains `745c00ad…`;
no checkpoint refresh. Private receipts: `local-lab/ghidra-first-training-20260907-v1/re-audit-20260926/input-key-abi/`.

## RE-audit verified library comments — September 26

The [manifest](../../tools/cohort-specs/library-verified-20260926.manifest.tsv) and
[spec](../../tools/cohort-specs/library-verified-20260926.spec.tsv) refresh 191 library evidence
comments and their verification tags, with no renames. Sixty previously
unaudited comments receive specimen-backed identity evidence; 129 earlier
proofs change with the combined library match and corrected ownership logic;
two additional PE import thunks receive explicit local-body evidence.
The planner leaves 1,376 already matching comments alone and excludes the
program-owned WinMain and unresolved names or bodies.

The independent checker uses LLVM COFF parsing, GNU PE imports and its own
byte/reference analysis. All 1,542 admitted code comparisons pass, with 118
verified data sections, no conflicting global references, 14 checked layout
claims and three import thunks. A first attempt missed a second reference to
the type_info vtable because it traversed data only once. Root independently
verified the pristine RTTI chain; the corrected fixed-point traversal resolves
the discrepancy without weakening the required count. The original failure
is retained in the private owner. The first 190-row seal was rejected before live application because reference-only `_wcsdup` was incorrectly described as byte-identical to `_strdup`. Its seal and rehearsal remain in `rejected-v1/`. Root reproduced the mismatch and added regression cases before this replacement repeated the full gate. The comments distinguish folded bodies,
layout-supported ownership and import thunks from imported implementations.
They do not certify current Ghidra prototypes or runtime semantics.

Exactly 191 library evidence comments and verification tag sets corrected. Every function name, symbol source, prototype, storage, parameter, local, type, bookmark, instruction and body is preserved, as are all 8,140 non-target function rows. The only program metric change is commentsSha256. All nine live exports equal the separately reopened rehearsal.
Fresh independent PRE restore, isolated dry/apply/readback and sealed readback,
five byte-stable refusal controls, independent read-only review, live readback
and independently restored POST recovery passed.

Working identity: `db.18664`, 18 files / 121,391,988 bytes,
inventory SHA-256 `55b2bffa9d76a3eeea15acd0f50ae94a774539bb156bc21141cb0ede02761025`; main database 71,090,176 bytes,
SHA-256 `0821893c0b1b4f9d9900bea41b3635e8457111a69db0c1194420fc8652323bba`. PRE is the freshly matched NvTriStrip POST.
Independent POST: `/srv/archive-a/onslaught-ghidra-cold/2026-09-26-library-verified/post-working`. The tracked checkpoint remains `745c00ad…`;
no checkpoint refresh. Private receipts: `local-lab/ghidra-first-training-20260907-v1/re-audit-20260926/library-verified/`.

## RE-audit NvTriStrip library identities — September 26

The [manifest](../../tools/cohort-specs/library-nvtristrip-20260926.manifest.tsv) and
[spec](../../tools/cohort-specs/library-nvtristrip-20260926.spec.tsv) identify the 72 saved functions
in the NvTriStrip and associated VC6 STL block. Fifty-seven had misleading
`CFastVB__` names; the remaining labels also mixed game classes and generic
helpers into this library. These are structural identities supported by retail
instructions, callers, diagnostic strings and pinned later reference source;
there is no byte-identical compiled NvTriStrip reference.

The source graph has 69 compatible call edges and two explicitly checked
return-size differences. Its 37 absent/transitive-call notes are limitations of
that comparison, not 37 proven behavioral divergences. Independent body review
and root reproduction establish the proposed roles. The comments retain the
four-argument retail GenerateStrips/CreateStrips APIs, two-byte indices,
24-byte faces without the newer fake-face member, uncertain STL template types
and wrapper provenance, and the empty-vector allocation difference in
RemoveSmallStrips. Existing prototypes are preserved, not certified.

Exactly 72 function identities, nonrepeatable comments and tag sets corrected in the NvTriStrip block: 71 prior labels replaced and one default function named. The evidence is structural, not an exact match to a compiled library. All prototypes, storage, parameters, locals, types, bookmarks, instructions, bodies and the 8,259 non-target function rows are preserved. Only the comment digest, one added comment and one symbol's
DEFAULT-to-USER_DEFINED counts change among program metrics. All nine live
exports equal the separately reopened rehearsal. Fresh PRE restore, rehearsal,
sealed readback, five no-write negative controls, independent review, live
readback and independently restored POST recovery passed. The first seal was
rejected before live application because FindOtherFace's comment excluded a
second null-return path. Its plan, seal and rehearsal remain in `rejected-v1/`;
the replacement changes only that comment and repeats the preservation and
rehearsal gates. This does not
establish runtime equivalence or complete semantic coverage of the library.

Working identity: `db.18663`, 18 files / 121,162,612 bytes,
inventory SHA-256 `6f34839c7db5326abb5de5addcc50ace1ada389082467d71712bd91e155a5d1c`; main database 70,860,800 bytes,
SHA-256 `032bf7ea693eb297907728d23756df345017f82ba0409fc7d1fe079856fbc9a9`. PRE is the freshly matched third label-cohort POST.
Independent POST: `/srv/archive-a/onslaught-ghidra-cold/2026-09-26-library-nvtristrip/post-working`. The tracked checkpoint remains `745c00ad…`;
no checkpoint refresh. Private receipts: `local-lab/ghidra-first-training-20260907-v1/re-audit-20260926/library-nvtristrip/`.

## RE-audit label corrections, third cohort — September 26

The [manifest](../../tools/cohort-specs/label-audit-3-20260926.manifest.tsv) and
[spec](../../tools/cohort-specs/label-audit-3-20260926.spec.tsv) correct eight names, comments
and tag sets: `SYSTEM__Init`, `SYSTEM__Run`, `SYSTEM__Shutdown`,
`CVBufTexture__ClearOut`, `CMonitor__dtor_thunk`,
`CComplexThing__SetThingType`, `CActor__IsOnGround` and `CActor__IsOnObject`.
The startup caller matches the pinned source's SYSTEM expression; its missing
header does not prove a class name. The actor predicates use x87 C0, including
masked unordered results; the buffer cleanup retains zero targets for zero
counts. Shared destructor callers and composed type bits are described without
inventing linker provenance or absent constant definitions.

Exactly eight function names, nonrepeatable comments and tag sets corrected by the RE record audit (third label cohort): SYSTEM startup, CVBufTexture cleanup, shared base destruction, complex-thing type bits and actor contact predicates. All prototypes, storage, parameters, locals, types, bookmarks, instructions, bodies and the 8,323 non-target function rows are preserved. Only `commentsSha256` changes among program metrics. All nine
live exports equal the separately reopened rehearsal. Fresh PRE restore,
rehearsal, sealed readback, five no-write negative controls, independent review,
live dry/apply/readback and independently restored POST recovery passed.
The first sealed rehearsal remains under `rejected-v1/`: review found ambiguous
Init success-branch wording, corrected before a fresh PRE restore and repeated
rehearsal/controls. These are static identity and metadata corrections, not
retail-play acceptance.

Working identity: `db.18662`, 18 files / 121,064,308 bytes,
inventory SHA-256 `3fe519b1b91297eb4fbe30e03b8821ede355d8201a9814fb0fe6f1e798ca68bf`; main database 70,762,496 bytes,
SHA-256 `2fe3643045358a0b06f61ee21569fb6d1e3b837f6136e4117ddb3e736fa17e13`. PRE is the freshly matched C runtime POST.
Independent POST: `/srv/archive-a/onslaught-ghidra-cold/2026-09-26-label-audit-3/post-working`. The tracked checkpoint remains `745c00ad…`;
no checkpoint refresh. Private receipts: `local-lab/ghidra-first-training-20260907-v1/re-audit-20260926/label-audit-3/`.

## RE-audit C runtime library names — September 26

The [manifest](../../tools/cohort-specs/library-crt-20260926.manifest.tsv) and
[spec](../../tools/cohort-specs/library-crt-20260926.spec.tsv) name 370
functions, each with an evidence comment and tag set: 351 Visual C++ 6.0 C
runtime functions and the 15 fragments that saved boundaries split off them, in
`0055d6a0`-`0056eb50` and `005be622`-`005d0f10` matched byte for byte against
the pinned `LIBCMT.LIB` by `tools/re_lib_match.py` (relocation fields masked;
private, untracked references, pins in the comments), DxErr9's
`_DXGetErrorString9A` (`005be628`), `D3DXCore__CFile__ctor` (`0058864a`, held
back from the D3DX cohort), `_asm_isMMX` (`005890f1`, whose D3DX-cohort name had
lost the identifier's underscore) and the program's `WinMain` (`00512130`,
formerly `CLTShell__WinMain`, placed by the runtime startup's reference; its
earlier note stays as a marked lead). Saved names that already equal a proven
spelling stay: the C name of a decorated symbol, an `OLDNAMES.LIB` alias
(`stricmp`) or a trailing `@N`. The NvTriStrip block `0056eb50`-`00574270` is
left for its own cohort.

The gate passed: fresh PRE restore, rehearsal with separate and sealed-spec
readbacks, five negative controls, independent review, live dry/apply/readback
and an independent POST restore. Only program comment and symbol-source counts
move (symbolsUserDefined 6338->6368, symbolsAnalysis 18005->18004,
symbolsImported 907->906, symbolsDefaultOther 61535->61507, comments
9352->9379). Working `db.18661`, 18 files / 121,064,308 bytes, inventory SHA-256
`79c57e7dea81a5e22d880e50041a94715d33c08fa0c082fc1bee6d6da6090105`. PRE: the
D3DX library POST. POST:
`/srv/archive-a/onslaught-ghidra-cold/2026-09-26-library-crt/post-working`.
Tracked checkpoint unchanged. Receipts:
`local-lab/ghidra-first-training-20260907-v1/re-audit-20260926/library-crt/`.

## RE-audit D3DX library names — September 26

The [manifest](../../tools/cohort-specs/library-d3dx-20260926.manifest.tsv) and
[spec](../../tools/cohort-specs/library-d3dx-20260926.spec.tsv) name 1,139 functions of the
statically linked library code, each with an evidence comment and tag set.
`tools/re_lib_match.py` matched the DirectX 9.0 SDK's static `d3dx9.lib`
(a private, untracked reference; pin in the comments) byte for byte with
relocation fields masked. It decides 1,112 of the 1,114 functions from
`00574270` to `005be622`; the other two are Ghidra's `Catch@00589200` and
`0058920c`, a fragment of `IsIntelSSEProcessor` split off by a saved boundary.
The D3DX code's own calls also name 26 C runtime functions and the program's
global `operator_new` (`00426fd0`) and `operator_delete` (`00449d40`).
Most of these carried game-class labels (`CFastVB__`, `CDXTexture__`,
`CTexture__`, `Platform__`); comments keep user-defined former labels as leads.
`0058864a` shares its saved label with `0057cc53` and moves in the next cohort.
The `CFastVB__` labels from `0056eb50` to `00574250` are NVIDIA's NvTriStrip
and its STL containers, also for a later cohort.

The gate passed: fresh PRE restore, rehearsal with separate and sealed-spec
readbacks, five negative controls, independent review, live
dry/apply/readback and an independent POST restore. Only program comment and
symbol-source counts move (`symbolsUserDefined` 6185->6338, `symbolsAnalysis`
18006->18005, `symbolsDefaultOther` 61687->61535, `comments` 9200->9352).
Working `db.18660`, 18 files / 120,605,556 bytes, inventory SHA-256
`8de23434a63a013d84a57cc0bba9eec61bd98aec13d9afde4269e7b3eb33752a`. PRE: the
second label-audit POST. POST:
`/srv/archive-a/onslaught-ghidra-cold/2026-09-26-library-d3dx/post-working`.
Tracked checkpoint unchanged. Receipts:
`local-lab/ghidra-first-training-20260907-v1/re-audit-20260926/library-d3dx/`.

## RE-audit label corrections, second cohort — September 26

The [manifest](../../tools/cohort-specs/label-audit-2-20260926.manifest.tsv) and
[spec](../../tools/cohort-specs/label-audit-2-20260926.spec.tsv) correct eighteen
function names that the RE record audit disproved from the pristine bytes, with a
comment and tag set each: `004247a0` `CCockpit__AddShockShake`, `004d3020`
`CPlayer__SetIsGod`, `005335d0` `IScript__FireArrivedEvent`, `00538470`
`IScript__UpdateWaypointFollowing`, `0040e910` `CBattleEngine__GetImportance`,
`00409e60` `CBattleEngine__ZoomModifier`, `0040e7d0` `CBattleEngine__CanBeLocked`,
`00489650` `CInfantryUnit__Damage`, `0044bf10` `CExplosion__Hit`, `0044a130`
`CEngine__BuildLevelSpecifics`, `004bac40` `CMonitor__dtor_base`, `00501450`
`CVBufTexture__ReleaseUnreferencedAndReportLeaks`, `00428500`
`CComponent__RefreshCachedTransform`, `0051b610` `CFEPIntro__Func_0051b610`,
`00513a50` `PCLTShell__D3D_SetTexture`, `004eb9a0` `InitMaterialPair_0083d248`,
`00527c90` `CRenderMethod__ctor` and `0050f680` `Spawner_SelectorKeepsSquadSize`.
`005015c0` is `CVBufTexture::ClearOut`, but that name was held by `00501450` in
PRE and the framework refuses order-dependent swaps, so it moves in a later cohort.
Each new comment ends with the former label as a lead.

Exactly eighteen function names, nonrepeatable comments and tag sets corrected by the RE record audit (second label cohort). All prototypes, storage, parameters, locals, types, bookmarks, instructions, bodies and the 8,313 non-target function rows are preserved; one previously absent comment is added.
Only `commentsSha256` and the comment count move among program metrics. All nine
live exports exactly equal the separately reopened rehearsal; the internal
function count remains 8,331.

Fresh independent PRE equality and restored read-only opening, isolated
dry/apply/separate readback, a sealed-spec readback, five negative controls,
independent exact-cohort review, live dry/apply/separate readback and independent
POST restore passed. The review blocked three comment overclaims in the first
seal (the component cache's skip path, the leak reporter's caller, the waypoint
update's resume arm) and one more in the second (the resume arm's game-state-4
discard); each was re-derived from the bytes, fixed and re-rehearsed from a fresh
PRE restore before its GO. The live applier's allowlist gained this cohort, and
the framework's 93 tests pass.

Working identity: `db.18659`, 18 files / 119,032,692 bytes,
inventory SHA-256 `0723845d8ee4ed37090609c976b9f8824dca0a15f6011b82ac270c154a76db5e`; main database
68,730,880 bytes, SHA-256 `e5ead994165cf216bb980bc45c0ccc3575677063e3cd5bab4decada247bedd3d`.
PRE was the freshly matched first label-audit POST. Independent POST:
`/srv/archive-a/onslaught-ghidra-cold/2026-09-26-label-audit-2/post-working`.
It was copied, hash-compared, restored elsewhere and reopened read-only.
The reviewed tracked checkpoint remains exactly `745c00ad…`; no refresh.

Private owner: `local-lab/ghidra-first-training-20260907-v1/re-audit-20260926/label-audit-2/`.
`completion.json` records the exact live readback, recovery receipts and full
export hashes. Current name lookup composes the new manifest.

## RE-audit label corrections — September 26

The [manifest](../../tools/cohort-specs/label-audit-20260926.manifest.tsv) and
[spec](../../tools/cohort-specs/label-audit-20260926.spec.tsv) correct ten
function names that the RE record audit disproved from the pristine bytes, with
a comment and tag set each: `0042efd0` `CWorldPhysicsManager__InitUnitRecordDefaults`,
`00509c80` `CWeapon__GetActualMaxRange`, `004f8140` `Mat34__SetFromEulerUnits4096`,
`0040c2e0` `CBattleEngine__WeaponFired`, `0040c340` `CBattleEngine__RecoilWeapon`,
`00407940` `CBattleEngine__AddShockShake`, `00407a50` `CBattleEngine__UpdateRotation`,
`004f99b0` `CUnit__StartPlayingInitNoise`, `00459810` `CFEPDevSelect__SetCurrentCard`
and `00465f10` `CFrontEnd__ctor`. `00407310` `CBattleEngine__DisplayLock` was
queued too but is the source name, so it is excluded.

Exactly ten function names, nonrepeatable comments and tag sets corrected by the RE record audit. All prototypes, storage, parameters, locals, types, bookmarks, instructions, bodies and the 8,321 non-target function rows are preserved.
Only `commentsSha256` moves among program metrics. All nine live exports
exactly equal the separately reopened rehearsal; the internal function count
remains 8,331.

Fresh independent PRE equality and restored read-only opening, isolated
dry/apply/separate readback, a sealed-spec readback, stale-comment and
name-collision dry refusals on a second fresh PRE restore, wrong-name, comment
and tag readback refusals, independent exact-cohort review, live
dry/apply/separate readback and independent POST restore passed. The review
first blocked three factual errors in the draft comments (the Euler sine
rounding, the UpdateRotation state-3 gate and a source range); they were fixed
and the whole rehearsal re-run before its GO. The live applier's allowlist
gained this cohort, and the framework's 93 tests pass.

Working identity: `db.18658`, 18 files / 119,016,308 bytes,
inventory SHA-256 `5b4b4fe9519d44f217464f7533ca8fee254f970e556687f56cff411c12dffc00`; main database
68,714,496 bytes, SHA-256 `e1d1f5be5af284466810afb9cc217b59e72a736172b14ac6f25c2e605baf7b02`.
PRE was the freshly matched sample-loading POST. Independent POST:
`/srv/archive-a/onslaught-ghidra-cold/2026-09-26-label-audit/post-working`.
It was copied, hash-compared, restored elsewhere and reopened read-only.
The reviewed tracked checkpoint remains exactly `745c00ad…`; no refresh.

Private owner: `local-lab/ghidra-first-training-20260907-v1/re-audit-20260926/label-audit/`.
`completion.json` records the exact live readback, recovery receipts and full
export hashes. Current name lookup composes the new manifest.

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
| Mutable Linux PC project | `local-lab/ghidra-projects/BEA/` (sole writable owner; latest measured state above) |
| Activation evidence | `local-lab/ghidra-linux-12.1.3-activation-20260830-v1/` (ignored completion receipt and semantic PRE/POST) |
| External recovery | `/srv/archive-a/onslaught-ghidra-cold/codex-consolidated-2026-08-31/` (sealed package; restore elsewhere before opening) |
| First-training correction recovery | `/srv/archive-a/onslaught-ghidra-cold/2026-09-07-first-training-semantics/` (verified working PRE and POST; restore elsewhere before opening) |
| Dated copies of both homes | `/srv/archive-a/onslaught-ghidra-cold/2026-09-04/` (checkpoint and mutable project stored separately) |

The former Samsung raw snapshot, Archive A Windows `source/` tree, Recovery
reconciliation folder and verified redundant B cold mirror have been deleted. Their old receipts are
history, not additional surviving database copies. Keep Archive A's independent cold
recovery and David's explicit historical-project retention holds. Reconcile proven redundant
copies under the approved storage plan with exact-path/hash records; do not ask again solely
for a batch number. A larger database generation counter in a rehearsal
copy does not make it the reviewed or writable authority.

Expedition overlays (RO clones, wave exports, ops state, correction ledgers)
live under real, ignored canonical-checkout `local-lab/` — do not commit them.
The complete repository is on encrypted Archive B with a bind/automount at its familiar Projects
path; both Ghidra homes moved without database mutation. Child worktrees use the canonical
absolute lab path; never create a duplicate lab, symlink or separately mounted/read-only substitute.
Prefer **headless CLI** exports
and scripts under `tools/` for automation only after the selected project and
ceremony gate permit them. Do not assume a Ghidra MCP
extension is installed or required. A mutation/promotion plan must explicitly cover its
cohort, live apply and tracked refresh; those approved steps do not need separate permission
requests. David resumed scoped development on September 6 and explicitly requested
a Ghidra quality/correction pass on September 7; the historical blanket development
hold no longer applies. Default inspection is read-only on a
disposable copy, never an automatic live open or checkpoint synchronization.

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
