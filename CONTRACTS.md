# Retail function and behavior contracts

Status: active contract-system front door
Last updated: 2026-08-13
Summary: how Battle Engine Aquila contract evidence is graded, located,
refuted, promoted, and carried into the rebuild. Current replay authority is
selected only by `developer_state.json` → `current_re_authority`.

Evidence: MEASURED — the named immutable campaign ledgers and their frozen
verifiers own current per-entity state; this page defines routing and grade
semantics rather than duplicating their claims.
Specimen: pristine `BEA.exe.original.backup`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.

This page does not catalog contracts. The authoritative catalog is the
machine-verified campaign generation named by
[`reverse-engineering/RE-INDEX.md`](reverse-engineering/RE-INDEX.md) and
[`developer_state.json`](developer_state.json). A hand-maintained Markdown copy
of thousands of rows would drift immediately.

## What a contract is

A function boundary, plausible name, source resemblance, call count, or one
observed invocation is not a complete contract. A useful retail contract states,
as far as the evidence permits:

- the exact specimen-bound entity and body/range;
- receiver and input values, representations, units, and valid conditions;
- return value and other outputs;
- globals, structure fields, resources, and external state read or written;
- ordering, timing, side effects, and calls that matter to behavior;
- failure, rejection, and edge behavior;
- evidence grade, unresolved fields, rival explanations, and cheapest falsifier;
- the reconstruction owner and focused parity test when the behavior is ready
  to cross into `rebuild/`.

Unknown fields stay unknown. “No write observed in this trace” is not “this
function never writes.” A forced script-level `Damage` call can prove the
damage boundary it reaches without proving the natural projectile and collision
chain that ordinarily precedes it.

## Truth owners

| Evidence or decision | Owner |
| --- | --- |
| Current per-function and per-residual contract accounting | The named immutable campaign generation: `campaign-contracts.tsv` joined with its function, residual, question, adjudication, and supersession ledgers, `campaign.ready.json`, and frozen `_reducer` |
| Detailed controlled-runtime observation | The hash-bound scenario bundle and its real receipts, manifests, markers, controls, and refuter output under `local-lab/` |
| Existing-trace call/entry/raw-return observation | Hash-bound `bea-ttd-call-context.v3` JSONL bundles produced by the frozen historical [`tools/Invoke-TtdCallContext.ps1`](tools/Invoke-TtdCallContext.ps1); active bounded long-replay work uses [`tools/Invoke-TtdCallContextV2.ps1`](tools/Invoke-TtdCallContextV2.ps1), while the original bytes remain unchanged for historical Gen10 replay. Pending/active associations clear across conservative global barriers (including ContextSwitch today), raw returns remain visible as orphans, and only same-epoch ordinary returns may link. Raw registers/stack bytes are untyped. A proposed schema-v4 soft-ContextSwitch refinement (map no-op + barrier-kind ledger; Unrecorded/Large/continuity stay hard) requires a new schema id, new `association_policy` string, and fresh replay—not reinterpretation of v3. Design owner: `local-lab/SCHEMA-V4-CALL-CONTEXT-DESIGN-2026-08-04.md` (hypothesis until implemented). |
| Existing-trace field-write transition | Source-bound `bea.ttd.data-writes.v3` JSONL/receipt/manifest/`READY` bundles produced by [`tools/Invoke-TtdDataWrites.ps1`](tools/Invoke-TtdDataWrites.ps1); a positive contract requires an exact replay window, sequence-sourced ordered Overwrite/Write chain, explicit counts, and zero gaps/breaks, while a zero-write claim is only a bounded no-callback witness |
| Static address/body evidence | [`reverse-engineering/binary-analysis/`](reverse-engineering/binary-analysis/_index.md), current read-only exports, pristine bytes, and the reviewed Ghidra owner |
| Source-informed architecture or intent | Pinned source plus [`reverse-engineering/source-code/stuart-source-synthesis.md`](reverse-engineering/source-code/stuart-source-synthesis.md); never retail behavior by itself |
| Cross-source conflict and selected parity decision | [`reverse-engineering/delta.md`](reverse-engineering/delta.md) |
| Reconstruction behavior | Current `rebuild/` code, [`rebuild/PROVENANCE.md`](rebuild/PROVENANCE.md), and an executed focused test |
| Contract shape, runtime instrumentation, and experiment design | [`reverse-engineering/parity-lab.md`](reverse-engineering/parity-lab.md) and the controlled-probe owners under [`tools/probe/`](tools/probe/README.md) |

`developer_state.json` and `RE-INDEX.md` route to evidence; they do not replace
it. Candidate overlays and agent reports are inputs, not campaign authority,
until the reducer admits them through a new verified generation.

## Current authority routing

Resolve the immutable semantic campaign and its exact counts from
`developer_state.json` → `current_re_authority`; read the concise campaign
synopsis and next-generation pointer in
[`RE-INDEX.md`](reverse-engineering/RE-INDEX.md). Generation narratives,
controls, and unknowns stay with their immutable ledgers rather than being
copied into this front door.

Static-envelope accounting is separate. The dated 8,136-row closure is owned by
[`function-c1-closure-2026-08-11.tsv`](reverse-engineering/binary-analysis/function-c1-closure-2026-08-11.tsv),
and the 34 later functions by the reviewed
[`Mission-registry addendum`](reverse-engineering/binary-analysis/mission-script-registry-new-function-static-contracts-2026-08-13.md).
Neither broadens runtime causality, source equivalence, or reconstruction parity.
Read [`reverse-engineering/ghidra/README.md`](reverse-engineering/ghidra/README.md)
for the current backed-up structural database.

## Grade and state lifecycle

The campaign uses a deliberately strict progression:

1. `C0_OPAQUE`: the entity is accounted for, but its behavioral contract is
   not known.
2. `C1_CANDIDATE_PARTIAL`: static/source/runtime evidence proposes bounded
   fields, while named rivals or missing observations remain.
3. `C2_BOUNDED_RUNTIME`: controlled or exact-window replay evidence measured a
   limited runtime contract under explicitly bounded conditions.
4. Refuter-survived: predictions, controls, identity, receipts, and competing
   explanations passed the applicable can-fail gate.
5. Terminal or `REBUILD_READY`: the relevant behavior has enough evidence for
   its stated use, remaining uncertainty is explicit, and the reconstruction
   owner/test fields are satisfied where parity is in scope.

Grades are not percentages. Boundary promotion does not raise a semantic
contract grade. A campaign may contain one row for every entity while almost
all rows remain deliberately opaque.

## How to inspect one contract

1. Resolve the current campaign from `RE-INDEX.md`; do not guess from the newest
   directory name.
2. Replay its frozen verifier:

   ```powershell
   python -B <campaign>/_reducer/tools/re_campaign.py verify --campaign <campaign>
   ```

3. Locate the specimen/entity key in `campaign-functions.tsv` or
   `campaign-residuals.tsv` and join its row in `campaign-contracts.tsv`.
4. Read every open `campaign-questions.tsv` row and applicable adjudication or
   supersession. A condensed contract without its remaining questions is not
   the full state.
5. Open the cited detailed evidence bundle and rerun its own verifier/refuter
   before relying on a consequential claim.
6. Check the current function/subsystem note and rebuild owner/test rather than
   assuming the campaign row updated every human synthesis automatically.

## Promotion and reconstruction rule

When evidence advances a contract:

- create a new immutable campaign generation; never rewrite an old one;
- bind the exact evidence and record candidate-to-final supersession;
- update the relevant address/subsystem note with the bounded human claim;
- promote Ghidra names, types, signatures, comments, or references only through
  the separately authorized backup/dry-run/apply/readback/refutation gate;
- map behavior that is ready for reconstruction to a concrete Core, Client, or
  Godot owner and focused parity test;
- keep source architecture, released behavior, reconstruction decisions, and
  remaining hypotheses visibly separate.

Do not add per-function tables to this page. If a readable whole-campaign
catalog is useful, generate it from a verified campaign generation so Markdown
cannot become a competing database.
