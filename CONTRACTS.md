# Retail function and behavior contracts

Status: active contract-system front door
Last updated: 2026-08-09
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

**Current complete-RE authority (2026-08-09):** do not treat historical
Generation 10 or candidate Generation 73 as the live replay parent. Read
`developer_state.json` → `current_re_authority`. Canonical Generation 19 has
8,126 functions, 14,245 contracts, 217 `C1_CANDIDATE_PARTIAL` functions, seven
`C2_BOUNDED_RUNTIME` functions, 7,902 opaque functions, 17 open residuals, and
zero `REBUILD_READY` contracts. Its exact READY is `f83dbb6e…ab9a`; frozen
reducer `151acbe5…f3e2`. Generation 73 is a projection oracle only. Generation
14 closed one residual as the consumer-bound TokenArchive dispatch-data
partition. Generation 15 replaces another 63-byte police-open residual with
15 NOP bytes, the exact 42-byte/17-instruction Mission-native
`IScript__SetPos`, and 6 NOP bytes. Generation 16 then advances SetPos from C1
to a bounded C2 for two replicated script-visible position-copy roundtrips and
adds a partial rebuild implementation. Its internal write set, broader
receiver/vector matrix, side effects, persistence, and failure behavior remain open.
Generation 17 adds only the retained non-null, sole-matching-node
`CBattleEngine::LockHit` removal path as bounded C2. Null, absent, multi-node,
global-free-head, destructor, return, target-identity, and rebuild questions stay
explicitly open.
Generation 18 adds only a static C1 TokenArchive parser/corpus/factory/direct-
writer contract; its runtime and refuter verdicts remain `UNSCORED`, runtime
replays are zero, and its rebuild mapping remains partial.
Generation 19 adds only the exact UnsetObjective 3-byte NOP / 13-byte wrapper /
3-byte NOP partition and its C1 static conditional-call/bit-clear contract.
Opaque callee `0x004E5BD0`, runtime/HUD/lifetime behavior, and complete rebuild
parity remain open; live Ghidra is unchanged.
The separately read-back live Ghidra ceremony added the SetPos function name,
signature, and comment without changing executable bytes, instructions, data,
or references. The bounded ApplyDamage C2 remains one replicated 1,000-damage,
zero-shield entry/write path, not an all-path law. The next valid campaign
generation is 20.

**Historical Gen10 immutable admission (2026-08-04):** READY SHA-256
`b349f0b2895849ba320b0b0b783c60a98794d01f375d57d9a04bbe4a5aebabb2`,
frozen reducer ID
`7dfa4015aad676bfeb22977adf3aadcddac49ba31fa8203a63a32f76d941f5d9`.
It preserves Generation 9's five live target-lock metadata corrections and
adds one separately replayed `TTD_CALL_CONTEXT_OBSERVATION` advance. That plate
remains valid historical dual-authority evidence; it is **not** the live tip
after Gen73.

The Level 521 `LockHit` plate is the first refuter-survived use of the
field-write owner: one invocation removed the supplied target's sole
`mFiredLocks` node. Its detailed evidence and exact limits are in
`local-lab/ttd-data-writes-level521-lockhit-removal-20260803-v1/README.md`.
It remains outside the authoritative campaign denominator until a successor to
Generation 10 explicitly ingests and verifies the contract.

The replicated call-context observation at
`local-lab/ttd-call-context-level521-impact-schema3-20260804-v1/` is admitted
by Generation 10. In the exact
window it proves raw same-thread call order and carriers for collision slot-39
`0x004D8AE0` → player `Damage` followed by collision-resolver → player `Hit`.
Only the `Hit` return is linked; three raw returns are orphans. The observation
does not name `0x004D8AE0`, type a return, prove writes, generalize outside the
window, or turn bounded zero-hit `StartDie` into a negative behavioral law.
Exactly those three positive rows advance to `C2_BOUNDED_RUNTIME`; three prior
questions close `SURVIVED` and three narrower successors remain open.
`StartDie @ 0x0040BFD0` remains `OPEN / C0_OPAQUE`, and no rebuild mapping,
parity result, name, range, or supersession changes.

**2026-08-10 successor evidence:** Gen10 itself remains immutable, but the
joined static/source proof now names `0x004D8AE0` as `CRound__Hit`, types its
`void __thiscall (CRound*, CThing*, CCollisionReport*)` ABI, records its direct
writes, and proves the observed non-null-report target-Damage arm carries
`CRoundDamage`. This is still a conditional bounded contract: the contrasting
invocation's rejecting gate and rebuild parity remain open. The connected
static pass also identifies `0x0044BF10` as
`CExplosion__Hit`, recovers its radial `CExplosionDamage` slot-40 dispatch,
names `0x0044C0F0` as `CExplosion__Move`, and corrects factory `0x0050FF10` to
`CWorldPhysicsManager__CreateExplosion`. The exact mode-3 impact helper now
closes the round-to-factory edge by resolving `CRoundExplosion`, creating the
object, and invoking `CExplosion__Init`. Its immediate `CThing` collision
registration allocates `CCSPersistentThing`, preserves ready bit `0x400`, scans
neighbor MapWho sectors synchronously, and reaches owner slot-39 `Hit` through
the shared collision response. For the tutorial's surviving target this closes
the conditional `0.8 + 1.0 = 1.8` same-receiver path; exact second-call mesh
part, other collision gates, and expanding-radius timing remain open. Owner:
[`cround-hit-damage-path-2026-08-10.md`](reverse-engineering/binary-analysis/cround-hit-damage-path-2026-08-10.md).

The connected factory-caller census then corrects all 22 containing functions
that still inherited the old pickup interpretation. Exact adapters bind unit
profile fields `+0xE8/+0xEC/+0xF0` to unit/small/stomp explosions, and strict
RTTI binds the virtual owners/slots. Those rows advance to bounded C1 creation
and initialization contracts; runtime reachability and downstream effects do
not. Owner:
[`cexplosion-factory-callers-2026-08-10.md`](reverse-engineering/binary-analysis/cexplosion-factory-callers-2026-08-10.md).

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
