# Execution Program

Status: durable backlog; feature execution on hold; organization in progress
Last updated: 2026-09-05
Summary: remaining work, acceptance gates, and completed program items without the execution diary.

The [standing goal](GOAL.md) keeps retail RE, the Godot rebuild, and the WinUI
toolkit coequal. The storage-consolidation hold remains: new RE campaigns,
rebuild features, WinUI/CLI features, and semantic Ghidra mutation await David's
explicit resumption. Approved organization, routing repair, read-only audit, and
checksum validation can continue. Finishing relocation does not resume features.

Use `developer_state.json` → `current_re_authority` as the sole live campaign
selector. Capability claims belong in [CURRENT_CAPABILITIES.md](CURRENT_CAPABILITIES.md),
validation in [VALIDATION.md](VALIDATION.md), and database state in
[Ghidra's guide](reverse-engineering/ghidra/README.md). Dated receipts and prior
queue revisions remain in Git and existing evidence owners; do not recreate a diary here.

## Open work

### P3 — Simplify developer state — PARTIAL

Continue moving redundant `_HERMES_SLICE_*` and superseded narrative into existing
function-note owners under the state's `_maintenance` policy. Earlier batches
preserved their facts; the remaining state has not been fully reduced.
Acceptance: retain distinctive evidence and provenance, preserve unrelated values,
resolve every changed reference, validate JSON, and pass the docs gate. Preserve
`current_re_authority`, the standing objective, and actual open questions.

### P6 — Campaign bookkeeping relief — OPEN; NOT IMPLEMENTED

Close already-triaged-out questions with their existing terminal verdicts and
decouple campaign generations from purely structural Ghidra promotions, re-grounding
when semantic grades require it. This is proposed policy, not today's authority.
Acceptance: a verified generation cut closes the intended rows with zero semantic
movement and the policy is recorded in campaign owner documents. Feature hold applies.

### P7 — World-110 generalization — PARTIAL; NOT PLAYABLE

Accepted pieces include exact serialized player-start admission, the bounded
height-clamp prefix, ordered start-list selection, standalone player/engine assignment,
ordered composition over adapter-supplied identities, and all-40 initial-object seed
admission. These deterministic pieces do not construct a playable world.

Remaining: complete start/actor/player/Battle Engine construction, real ownership
and reader identities, physics/coordinate enrichment, squad/spawner expansion and
publication order, policy effects, player initialization, registry/state hashing,
real headless/interactive session, Godot lifecycle, and campaign 100→110 play.
The host still constructs only world 100. Acceptance: evidence-backed contracts
and focused production-path tests recorded in [PARITY.md](rebuild/PARITY.md),
working second-world lifecycle and campaign transition, and the current-truth
section of [rebuild/README.md](rebuild/README.md) updated without widening partial claims.
The serialized-seed ceiling is in
[world-110-initial-constructor-seeds.md](reverse-engineering/game-mechanics/world-110-initial-constructor-seeds.md).

### P8 — Human-input replay tapes — OPEN

Record an actual play session as a `CommandTape`, then replay it twice under
`--expect` with identical results. Acceptance: both runs pass and the recording
procedure is documented under `rebuild/tools/`. Windows input capture is required;
a synthetic tape does not meet this gate.

### P10 — WinUI release acceptance — SOURCE CUT COMPLETE; ACCEPTANCE OPEN

The v1.0.12 source cut is merged. Remaining Windows work: regenerate and verify
third-party notices, run [public signoff](release/readiness/PUBLIC_SIGNOFF_COMMANDS.md),
and pass the portable ZIP probe. Publication follows [README.RELEASE.md](README.RELEASE.md).
Linux static checks do not substitute for Windows acceptance. The evaluation guest
is staged under `local-data/windows-vm/`; read its guide before activation.

### P11 — CLI parity — OPEN

The documented remaining gaps are cheat-named save-copy creation, trainer hotkeys,
and music playback. `media list`, `lore search/show`, and advanced `saves patch`
options already exist; `trainer music --out` renders audio but does not play it.
Standalone asset-library parity remains unverified and in scope until the implemented
command surface and per-verb Windows tests establish it.
Acceptance: close the remaining gaps with per-verb Windows tests, keep
[CLI.md](CLI.md) aligned with the implemented command surface, and keep public
copy free of internal process language. Source inspection is not Windows acceptance.

### P12 — Repository storage and disposition audit — CUTOVER COMPLETE; AUDIT OPEN

The complete checkout now lives at `/srv/archive-b/Onslaught-Career-Editor`,
with a bind/automount at `/home/xsniper80/Projects/game-dev/Onslaught-Career-Editor`.
`local-lab/` and `local-data/` remain real ignored children of that one checkout.
The old ProjectData route stays absent. Current mount and recovery rules belong
in [AGENTS.md](AGENTS.md) and the existing local data guides.

Remaining acceptance: repair active tracked/tool/selector routing and classify
families as working authority, unique history, justified recovery copy, or proven
redundancy. Check real references and hashes before retirement; preserve unresolved
unique work. Existing Archive B mirrors share the project's physical drive and
therefore do not protect against its loss. Historical ignored non-lab recovery
coverage remains unresolved. Record material dispositions in the existing migration
queue under the approved scope, without inventing another approval gate or backup.

## Completed items

| Item | Completed scope and owner |
| --- | --- |
| P0 — Integration spine | Source/doc integration and branch consolidation landed. Later causal round-ID evidence superseded the geometric Blaster observer; measured tests belong in VALIDATION.md. |
| P1 — Sealed static-receipt reseat | The campaign cut completed. Select current state through `current_re_authority`; historical receipts do not select a parent. |
| P2 — Ghidra promotion/integration | The named cohort ceremonies and corrected offline integration completed. Read the Ghidra owner before any further promotion. |
| P4 — Function-triage packets | The exporter produced complete packets in one read-only headless run and served an RE question. Tool usage and focused tests are in tools/README.md. |
| P5 — Coverage index/query | The receipt-based index and preregistered cross-trace query completed. Raw TTD recordings were subsequently retired; this milestone does not promise raw replay or intact historical paths. |
| P9 — Ferry sweep split | The expensive sweep is separate from the default Core suite; the explicit command remains in VALIDATION.md. |

Completion requires the named acceptance evidence, not effort or an unrelated green
suite. Preserve fail-closed checks and use the smallest relevant existing validation.
Completed bookkeeping, document cleanup, or a partial World-110 owner does not close
the full RE, reconstruction, or toolkit goal.
