# CUnitAI__SelectOrRefreshCloseTarget_004ff710

Status: active replicated bounded-runtime contract
Last updated: 2026-08-24
Summary: specimen-bound static contract plus a replicated, controlled Level-521 call-context envelope for `CUnitAI__SelectOrRefreshCloseTarget_004ff710` at `0x004ff710`.
Evidence: MEASURED — READY packet/decompile, structured edges, closure identity, independently recomputed pristine body bytes, and a preregistered wrapper-READY replay with exact positive/dark controls; runtime provenance and state-write limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no current source-crosswalk row) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x004ff710`

## Identity
- Body `[0x004ff710,0x004ffb57]`, 1096 bytes, 353 closure instructions. Raw pristine-body SHA-256 `e4f2106e542daa0af8b3f92409641169e35f6c7a573c73956693545756703d05`; closure range SHA-256 `7ead23272dbaf8201b08bb45deb8c3a1f7bf1e62842f6d0383ef85995f2cf4ae`; packet range-plus-bytes SHA-256 `e4ec1b24639842f436ba85fc37bc9615aa0c0f1dab6c0fa1da9928db5ba92147`. All three were independently recomputed over the exact single contiguous inclusive range.
- Canonical name `CUnitAI__SelectOrRefreshCloseTarget_004ff710` comes from the current closure/register row. Packet label matches canonical tracked name `CUnitAI__SelectOrRefreshCloseTarget_004ff710`.
- Packet name source `USER_DEFINED` and signature source `USER_DEFINED` are counted provenance, not semantic proof.
- Campaign grade `C1_CANDIDATE_PARTIAL` / closure class `SEALED_STATIC_RECEIPT` / packet confidence `MEDIUM_STATIC`. Proposed promotion: true — the later runtime-replication manifest is the promotion witness; the frozen generation-32 register row remains unchanged.

## Calling convention
Packet records `__thiscall`; the static body uses a bare `RET`. Both retained call-context replays carry the receiver in `ECX`, preserve the call→entry register view, and carry the raw return in `EAX`. The packet's old scalar `int` spelling is not the measured domain.

## Prototype and parameter semantics
```c
void * __thiscall CUnitAI__SelectOrRefreshCloseTarget_004ff710(void * this)
```
- Receiver: one untyped `void * this` in `ECX`. Concrete class layout, ownership, aliasing, and nullability beyond the measured pointer-shaped return remain not_determinable.

## Return value meaning
The packet comment's corrected shape is borne out at runtime: all 41 validated returns in the controlled replay are non-null heap-shaped `EAX` values (seven distinct values), never small integers or module-image addresses. The bounded contract is therefore an untyped pointer-or-null shape; pointed-to RTTI, ownership, and behavior outside this trace remain unknown.

## Globals read/written
- Decompile symbol references: `DAT_00855090`, `DAT_008550b0`, `DAT_008550c0`, `DAT_008a9d9c`. Read/write direction for each symbol is not independently instruction-verified in this factory draft.

## Callees relied on / callers
- Callee `CGenericActiveReader__SetReader` `0x00401000` ×2 site(s) (STATIC_DIRECT).
- Callee `Random__NextLCGAbs` `0x004de8d0` ×1 site(s) (STATIC_DIRECT).
- Callee `CSquadNormal__IsValidLinkedSupportForTarget` `0x004fb3d0` ×1 site(s) (STATIC_DIRECT).
- Callee `CUnit__CanFireAtTarget_BallisticArcA` `0x004fb500` ×2 site(s) (STATIC_DIRECT).
- Callee `CUnit__CanFireAtTarget_BallisticArcB` `0x004fb5a0` ×2 site(s) (STATIC_DIRECT).
- Callee `CSquadNormal__GetSupportMinEngageDistance` `0x004fb780` ×1 site(s) (STATIC_DIRECT).
- Callee `CSquadNormal__GetSupportMaxEngageDistance` `0x004fb7e0` ×1 site(s) (STATIC_DIRECT).
- Callee `CSquadNormal__SelectBestSupportOrEscort` `0x004fb840` ×4 site(s) (STATIC_DIRECT).
- Callee `CUnit__IsCandidateSideCompatibleForTargeting` `0x004fd3d0` ×1 site(s) (STATIC_DIRECT).
- Callee `CUnit__IsActiveAndNotInState12` `0x004fd5b0` ×3 site(s) (STATIC_DIRECT).
- Packet callers: none in the structured array. Runtime closes the hottest missing edge: 86/86 calls originate at the single direct site `0x004ff702` inside `CUnitAI__UpdateTargetSupportAndFireFlags_004ff4f0`, and every call is nested in an open same-`ECX` invocation of that owner.
- Structured packet arrays prove only their listed direct/static identities; the runtime receipt is authoritative for the measured ff4f0→ff710 edge. Other indirect/vtable/data-driven callers remain unresolved.

## Behavior summary
- Existing packet analyst comment (quoted as bounded packet evidence, not silently upgraded): “Shared CUnitAI-family close-target selector/refresher (reader distance gates, ballistic fire flags this+0x18/0x1c, side-keyed scan + SetReader, returns *(this+0xc) pointer may be null). ECX receiver; bare `RET` (caller cleanup). Declared `int __thiscall ...(void * this)` / boolean tag is false — returns a target/reader pointer, not a predicate. Shape is `void * __thiscall (void * this)` (do not invent typed unit/reader typedef beyond that plate). Static retail evidence only; exact scoring policy, runtime targeting UX, and rebuild parity remain unproven.”
- The displayed decompile is non-empty and SHA-256 `60e225ebd37a289c14b627b7c69c3984180efb23b6bf4687ed7941c12295ad99`. Runtime now proves the shared ff4f0→ff710 call envelope and pointer-shaped return domain in the named trace; it does not prove packet-described field writes or exact scoring policy.
- Structured inventory for this body: 0 caller record(s), 10 callee record(s), and 0 string-ref record(s).

## Error / edge behavior
Nullability, invalid-state behavior, allocation failure, indirect-call failure, NaN/overflow behavior, and rollback semantics are not_determinable as a class from the packet metadata. The decompile and quoted comment are the bounded static evidence; any missing branch-level edge contract remains an open question rather than an invented default.

## Runtime corroboration (TTD, bounded)
- The older `ttd-deep-mine/values.tsv` corpus still has no row for this VA; that historical absence is not used as evidence.
- Corrected replay `level521-native-20260802-0018-take2`, full native window: 86 calls / 86 entries / 41 raw returns, 41 validated gap-free envelopes, 50 unique receivers. All exact expectations passed and wrapper status is READY.
- Every ff710 call is strictly nested in ff4f0 with equal `ECX`; stack-depth delta is 52 bytes for all 86. Unique caller site: `0x004ff702`. Receiver containment: `50⊆76`.
- Controls: ffdd0 ran 73/73/73 only from the two `CSquadNormal__BuildAttackFormation` sites and on receivers disjoint from ff710; exact CWaypoint body `0x004ffe00..0x004ffefa` stayed 0/0/0.
- Replication: all 1,169 event/invocation rows shared with the earlier run-a capture are byte-identical after preregistered metadata/target exclusions; normalized SHA-256 `AD623E03146985419C58F13B3364C1C12457034EFD53B2912B74AA7DAC0CDB0F`.

## Evidence
- Writer-task authority: task `t_efc238f0`, cohort 6 immutable manifest SHA-256 `9f24ea299ab115b57de8eda78fd01e374647c888e41ce248a0624ee78fadd13e`, row 23; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750` and proposed promotion false. The task comment/independent-review receipts are the durable manifest authority; no writer-local scratch path is claimed as tracked evidence.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x004ff710.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`); packet decompile SHA-256 `60e225ebd37a289c14b627b7c69c3984180efb23b6bf4687ed7941c12295ad99`.
- Digest derivation: closure SHA-256 hashes canonical range text `004ff710:004ffb57;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
- Closure execution state `PARTIAL` and confidence `MEDIUM_STATIC`; these are inherited bounded grades, not this factory's promotion decision.
- Packet stringRefs: empty.
- Source crosswalk: no row for this VA in the current tracked crosswalk.
- Canonical runtime note `reverse-engineering/binary-analysis/functions/CUnitAI__SelectOrRefreshCloseTarget_004ff710.md`, SHA-256 `f95a156f3127f6d674660c7b4a99bd8dc32b188bc25b8867d5aa91f0031d042d`.
- Runtime promotion manifest `reverse-engineering/binary-analysis/unitai-targeting-runtime-replication-promotion-manifest-2026-08-24.tsv`, SHA-256 `09810bac7b5d39eacadc512cb29a0a223899b6625f95238c3dfc98a4708ea16c`; corrected capture SHA-256 `84DB81290B00CE15FBCEB579FD8BC8B4C793C3F947001544FA44918F4189D171`; wrapper receipt `A3D9E421EB12526405DF718C9142CE5BBE0AB829CAE6C9D614242BCE0138A96D`; independent adjudication `2C4B7987EC08FBBFCC063C793196BD66BBF5093480B7D54899883F36AD6FF6A7`.
- Provenance limit: take2's recording receipt is RECONSTRUCTED/PARTIAL; capture-time target hash was not independently bound. The trace and copied runtime are hash-bound now, and no claim is widened beyond this scenario.

## Confidence
2 — exact identity, contiguous pristine bytes, ABI/return shape, one executed caller edge, receiver law, replicated entry→return envelope, and can-fail controls are reconciled. Field-write ordering, pointed-to RTTI, other scenarios, and rebuild parity remain open. Proposed promotion: true.

## Unresolved questions
- Instruction-level read/write direction and concrete layout for every referenced field/global.
- Complete indirect-call target set and failure/nullability behavior.
- Exact `this+0xc/+0x18/+0x1c` state-write ordering and caller expectations outside the measured shared envelope.
- Cheapest falsifier: replay the corrected exact target table with the pinned v2 collector. Any non-READY result, count other than 86/86/41, non-`0x004ff702` caller, nesting/receiver/control failure, small-int/module-image validated return, or normalized shared-row hash other than `AD623E03…CDB0F` invalidates the bounded promotion.
