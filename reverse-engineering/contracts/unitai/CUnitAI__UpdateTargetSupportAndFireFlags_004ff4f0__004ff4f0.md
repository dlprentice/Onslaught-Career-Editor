# CUnitAI__UpdateTargetSupportAndFireFlags_004ff4f0

Status: active multi-build static contract plus replicated bounded-runtime envelope
Last updated: 2026-08-27
Summary: specimen-bound branch-specific reader transactions, ordered prerequisite/final fire-feasibility results, and a replicated controlled Level-521 call-context envelope for `CUnitAI__UpdateTargetSupportAndFireFlags_004ff4f0` at `0x004ff4f0`.
Evidence: MEASURED — independently decoded pristine and console instructions establish the write/call ordering; the preregistered wrapper-READY replay establishes only the bounded caller/receiver/callee envelope.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no current source-crosswalk row) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x004ff4f0`

## Identity
- Body `[0x004ff4f0,0x004ff70a]`, 539 bytes, 185 closure instructions. Raw pristine-body SHA-256 `4bf6a880bceb0db303c5adab07deb05430df97d61a8bdbe34b99cb608958f60d`; closure range SHA-256 `eb32db4fa13f563e916c95412e477857feba7ff1609e22446facfc8c38e8e3fc`; packet range-plus-bytes SHA-256 `1d4d079d3222ad9c0d84b5284dbf21cd3b748085c0f4f416686c7a99055a2521`. All three were independently recomputed over the exact single contiguous inclusive range.
- Canonical name `CUnitAI__UpdateTargetSupportAndFireFlags_004ff4f0` comes from the current closure/register row. Packet label matches canonical tracked name `CUnitAI__UpdateTargetSupportAndFireFlags_004ff4f0`.
- Packet name source `USER_DEFINED` and signature source `USER_DEFINED` are counted provenance, not semantic proof.
- Campaign grade `C1_CANDIDATE_PARTIAL` / closure class `SEALED_STATIC_RECEIPT` / packet confidence `MEDIUM_STATIC`. Proposed promotion: true — the later runtime-replication manifest is the promotion witness; the frozen generation-32 register row remains unchanged.

## Calling convention
Packet records `__thiscall`; both retained call-context replays carry the receiver in `ECX`, preserve the call→entry register view, and return through the static void body. EAX at return is residual, not a scalar result.

## Prototype and parameter semantics
```c
void __thiscall CUnitAI__UpdateTargetSupportAndFireFlags_004ff4f0(void * this)
```
- Receiver: one untyped `void * this` in `ECX`. Concrete layout, ownership, aliasing, and nullability remain bounded to the static packet and measured receiver identities.

## Return value meaning
The packet signature declares `void`; no scalar return contract is claimed. Callee/side-effect completion and failure reporting remain bounded by the displayed body and its called/indirect targets.

## Globals read/written
- Decompile symbol references: `DAT_008550a0`. Read/write direction for each symbol is not independently instruction-verified in this factory draft.

## Callees relied on / callers
- Callee `CGenericActiveReader__SetReader` `0x00401000` ×2 site(s) (STATIC_DIRECT).
- Callee `CSquadNormal__IsValidLinkedSupportForTarget` `0x004fb3d0` ×1 site(s) (STATIC_DIRECT).
- Callee `CUnit__CanFireAtTarget_BallisticArcA` `0x004fb500` ×1 site(s) (STATIC_DIRECT).
- Callee `CUnit__CanFireAtTarget_BallisticArcB` `0x004fb5a0` ×2 site(s) (STATIC_DIRECT).
- Callee `CSquadNormal__SelectBestSupportOrEscort` `0x004fb840` ×2 site(s) (STATIC_DIRECT).
- Callee `CUnit__IsCandidateSideCompatibleForTargeting` `0x004fd3d0` ×1 site(s) (STATIC_DIRECT).
- Callee `CUnit__IsActiveAndNotInState12` `0x004fd5b0` ×1 site(s) (STATIC_DIRECT).
- Callee `CUnit__TrySpawnMembersForTarget` `0x004fdad0` ×1 site(s) (STATIC_DIRECT).
- The state helper exactly rejects null, `TF_DYING`, and Unit field `+0x244` values `1/2`; the allegiance helper implements the Forseti/Muspell/Independent opposing-pair table plus Neutral-under-`CUnitIndiscriminate`. The current helper names remain analysis labels. The `0x004fb3d0` body is CUnit-owned and also evaluates a candidate virtual plus ordered linked/weapon capability paths; its current `CSquadNormal` label overstates both ownership and semantics.
- Packet callers: none in the structured array. Runtime caller census is 167/169 from `CUnitAI__Update` at `0x004fef4a`, plus two from `CDiveBomberAI__VFunc_9_00445900` at `0x004459c9` and `0x004459f5`.
- Runtime also closes the packet's hottest missing callee edge: 86 calls to `CUnitAI__SelectOrRefreshCloseTarget_004ff710`, all at `0x004ff702`. Structured packet arrays prove only their listed direct/static identities; the runtime receipt owns these measured edges.

## Behavior summary
- Existing packet analyst comment (quoted as bounded packet evidence, not silently upgraded): “Shared CUnitAI-family update: may clear this+0xc reader when target flag bit2 set; if owner linked support missing/invalid, scans DAT_008550a0 candidates for side-compatible support, may CUnit__TrySpawnMembersForTarget, then evaluates CanFireAtTarget_BallisticArcB/A into this+0x1c/0x18 or calls this vfunc +0x2c; else clears fire flags and refreshes escort/fire gates on current reader. Static listing/xref/vtable evidence only; exact source virtual name, AI layout, runtime behavior, BEA patching, and rebuild parity remain unproven.”
- Independent decoding closes the branch-specific writes. The direct arm pre-clears `+0x18` then `+0x1C`, stores helper B first, and calls/stores A only when B is non-zero. The fallback scan preserves old result cells; its existing-reader arm stores B first and explicitly zeros A when B is zero. Otherwise virtual slot `+0x2C` transfers to `0x004FF710`. The displayed decompile SHA-256 remains `0d1500f4ad1433d6278da11d13d8de764daa6a251a23cfc38f16399ce799f7f9`.
- PC demo is instruction-shape identical; the paired Xbox and three PS2 slot-4 bodies carry the same transaction ordering. The independently decoded helper wrappers also reproduce classifier-first range admission, active/fallback selection, inclusive target-height gating, and distinct delegate dispatch across those families.
- B (`0x004fb5a0`) is stored at `AI+0x1C` and is the ballistic-reach/line-clearance feasibility prerequisite: all four UnitAI transactions branch away when it is zero. A (`0x004fb500`) is called with context zero only after B and stored at `AI+0x18`; `CUnitAI__Update` later requires it as the final aim-angle/obstruction fire-acceptance result. Those labels describe proved behavior, not recovered original identifiers. Complete PC wrapper/delegate exits are `{0,1}`; console delegate exits remain unenumerated.
- Structured inventory for this body: 0 caller record(s), 8 callee record(s), and 0 string-ref record(s).

## Error / edge behavior
Nullability, invalid-state behavior, allocation failure, indirect-call failure, NaN/overflow behavior, and rollback semantics are not_determinable as a class from the packet metadata. The decompile and quoted comment are the bounded static evidence; any missing branch-level edge contract remains an open question rather than an invented default.

## Runtime corroboration (TTD, bounded)
The historical bounded TTD table contains these breadth rows; they establish execution/coverage only:
- Session `batch-1`; question `contract-unit-ai`; value: CORROBORATED live in every coverage session of batch; evidence `level-opening-3m-v1-level100, level-opening-3m-v1-level110, level-opening-3m-v1-level200, level-opening-3m-v1-level201 …`.
- Session `batch-2`; question `contract-unit-ai`; value: CORROBORATED live in every coverage session of batch; evidence `level-opening-3m-v1-level300, level-opening-3m-v1-level311, level-opening-3m-v1-level312, level-opening-3m-v1-level321 …`.
- Session `batch-3`; question `contract-unit-ai`; value: CORROBORATED live in every coverage session of batch; evidence `level-opening-3m-v1-level421, level-opening-3m-v1-level422, level-opening-3m-v1-level431, level-opening-3m-v1-level432 …`.
- Session `batch-4`; question `contract-unit-ai`; value: CORROBORATED live in every coverage session of batch; evidence `level-opening-3m-v1-level524, level-opening-3m-v1-level600, level-opening-3m-v1-level611, level-opening-3m-v1-level612 …`.
- Session `batch-5`; question `contract-unit-ai`; value: CORROBORATED live in every coverage session of batch; evidence `level-opening-3m-v1-level732, level-opening-3m-v1-level741, level-opening-3m-v1-level742, level-opening-3m-v1-level800 …`.
- Session `batch-6`; question `contract-unit-ai`; value: corroborated in 10/11 coverage sessions; evidence `level-opening-3m-v1-level856, level-opening-3m-v1-level858, level-opening-3m-v1-level859, level-opening-3m-v1-level860 …`.
- Session `batch-7`; question `contract-unit-ai`; value: CORROBORATED live in every coverage session of batch; evidence `level-opening-3m-v1-level901, level-opening-3m-v1-level902, level-opening-3m-v1-level903, level-opening-3m-v1-level904 …`.
- Session `batch-8`; question `contract-unit-ai`; value: corroborated in 1/4 coverage sessions; evidence `level521-native-20260802-0018-take4`.
- Session `batch-9`; question `contract-unit-ai`; value: CORROBORATED live in every coverage session of batch; evidence `q-pilot-cov-l700-20260731, q-pilot-cov-l742-20260731, q-pilot-cov-l742-rep2-20260731`.
- Session `batch-10`; question `contract-unit-ai`; value: no coverage collector output for this batch's sessions; evidence `batch carries no BEA.exe coverage bitmap (query/infra captures)`.
- Corrected replay `level521-native-20260802-0018-take2`, full native window: 169 calls / 169 entries / 71 raw returns, 70 validated gap-free envelopes, 76 unique receivers. One raw return is explicitly orphaned rather than attached to a guessed invocation. All exact expectations passed and wrapper status is READY.
- Runtime callers: `0x004fef4a` ×167, `0x004459c9` ×1, `0x004459f5` ×1. The sole ff710 callee site is `0x004ff702` ×86; every nested call has equal `ECX` and a 52-byte stack-depth delta.
- Controls: ffdd0 ran 73/73/73 only from the two `CSquadNormal__BuildAttackFormation` sites and on receivers disjoint from ff710; exact CWaypoint body `0x004ffe00..0x004ffefa` stayed 0/0/0.
- Replication: all 1,169 event/invocation rows shared with earlier run-a are byte-identical after preregistered metadata/target exclusions; normalized SHA-256 `AD623E03146985419C58F13B3364C1C12457034EFD53B2912B74AA7DAC0CDB0F`.

## Evidence
- Writer-task authority: task `t_efc238f0`, cohort 6 immutable manifest SHA-256 `9f24ea299ab115b57de8eda78fd01e374647c888e41ce248a0624ee78fadd13e`, row 22; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750` and proposed promotion false. The task comment/independent-review receipts are the durable manifest authority; no writer-local scratch path is claimed as tracked evidence.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x004ff4f0.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`); packet decompile SHA-256 `0d1500f4ad1433d6278da11d13d8de764daa6a251a23cfc38f16399ce799f7f9`.
- Digest derivation: closure SHA-256 hashes canonical range text `004ff4f0:004ff70a;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
- Closure execution state `PARTIAL` and confidence `MEDIUM_STATIC`; these are inherited bounded grades, not this factory's promotion decision.
- Packet stringRefs: empty.
- Source crosswalk: no row for this VA in the current tracked crosswalk.
- Canonical runtime note `reverse-engineering/binary-analysis/functions/CUnitAI__UpdateTargetSupportAndFireFlags_004ff4f0.md`, SHA-256 `5cdb460b4541fd7e8adc90241223d5cc1c439a6c09e272c40f8114b26348a61c`.
- Runtime promotion manifest `reverse-engineering/binary-analysis/unitai-targeting-runtime-replication-promotion-manifest-2026-08-24.tsv`, SHA-256 `09810bac7b5d39eacadc512cb29a0a223899b6625f95238c3dfc98a4708ea16c`; corrected capture SHA-256 `84DB81290B00CE15FBCEB579FD8BC8B4C793C3F947001544FA44918F4189D171`; wrapper receipt `A3D9E421EB12526405DF718C9142CE5BBE0AB829CAE6C9D614242BCE0138A96D`; independent adjudication `2C4B7987EC08FBBFCC063C793196BD66BBF5093480B7D54899883F36AD6FF6A7`.
- Provenance limit: take2's recording receipt is RECONSTRUCTED/PARTIAL; capture-time target hash was not independently bound. The trace and copied runtime are hash-bound now, and no claim is widened beyond this scenario.

## Confidence
2 — exact identity, ABI, branch-specific state ordering, bounded helper semantics, PC helper result domain, console wrapper correspondence, executed caller/callee edges, receiver law, replicated entry→return envelope, and can-fail controls are reconciled. Per-invocation values, original helper names, console delegate exit domains, other scenarios, and rebuild wiring remain open. Proposed promotion: true.

## Unresolved questions
- Concrete gameplay names and layout ownership beyond the accessed offsets.
- Complete indirect-call target set, target RTTI, original helper/member names,
  console delegate exit domains, and helper side effects.
- Exact per-invocation receiver values and caller expectations outside the measured shared envelope.
- Cheapest falsifier: replay the corrected exact target table with the pinned v2 collector. Any non-READY result, count other than 169/169/71, caller outside the three measured sites, nested ff710/control/receiver failure, or normalized shared-row hash other than `AD623E03…CDB0F` invalidates the bounded promotion.
