# Canonical Ghidra project

Status: active — reviewed checkpoint, never a writable project
Last updated: 2026-09-26
Summary: checkpoint identity, writable-project routing and external recovery.

`BEA.gpr` and `BEA.rep/` are the reviewed distributable checkpoint of the
Battle Engine Aquila analysis database. This is the single tracked database
owner; the mutable Linux project and historical recovery packages remain
untracked. The latest working correction is the
[second RE-audit label correction](#re-audit-label-corrections-second-cohort--september-26);
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
