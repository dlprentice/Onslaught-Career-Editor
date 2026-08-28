# CUnitAI__SelectOrRefreshCloseTarget_004ff710

Status: active multi-build static contract plus replicated bounded-runtime envelope
Last updated: 2026-08-28
Summary: specimen-bound branch/order/scoring contract, corresponding PC-demo/Xbox/PS2 virtual-suite bodies, and a replicated controlled Level-521 call-context envelope for `CUnitAI__SelectOrRefreshCloseTarget_004ff710` at `0x004ff710`.
Evidence: MEASURED — independently decoded pristine instructions establish the PC transaction; raw and normalized console bodies independently carry the range, deterministic ladder/floor, indiscriminate draw/bypass, and tie shapes; the preregistered wrapper-READY replay establishes only its bounded caller/receiver/return envelope.
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
- The body reads the head of three embedded `CWorld` `CSPtrSet` objects: `0x00855090` is source-correlated `WORLD.GetThingNB()`, `0x008550B0` is the tail-ordered allegiance-`0/6` side index, and `0x008550C0` is the tail-ordered allegiance-`1/6` side index. It also reads the shared random owner at `DAT_008a9d9c`; this body does not write any of those globals.

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
- The current names for `0x004fd5b0` and `0x004fb3d0` are analysis metadata, not recovered source identifiers. Exact bodies contradict “active” for the former and `CSquadNormal` ownership plus “linked support” completeness for the latter; no live Ghidra rename is promoted here.
- The three current `CSquadNormal` labels at `0x004fb780/0x004fb7e0/0x004fb840` are likewise contradicted by exact bodies. Their receiver is `CUnit`: the large body selects an attack provider for one target, and the two small wrappers return that selected provider's minimum/maximum range. These evidence-bounded identities are documented without bypassing the Ghidra promotion procedure.
- Packet callers: none in the structured array. Runtime closes the hottest missing edge: 86/86 calls originate at the single direct site `0x004ff702` inside `CUnitAI__UpdateTargetSupportAndFireFlags_004ff4f0`, and every call is nested in an open same-`ECX` invocation of that owner.
- Structured packet arrays prove only their listed direct/static identities; the runtime receipt is authoritative for the measured ff4f0→ff710 edge. Other indirect/vtable/data-driven callers remain unresolved.

## Behavior summary
- Existing packet analyst comment (quoted as bounded packet evidence, not silently upgraded): “Shared CUnitAI-family close-target selector/refresher (reader distance gates, ballistic fire flags this+0x18/0x1c, side-keyed scan + SetReader, returns *(this+0xc) pointer may be null). ECX receiver; bare `RET` (caller cleanup). Declared `int __thiscall ...(void * this)` / boolean tag is false — returns a target/reader pointer, not a predicate. Shape is `void * __thiscall (void * this)` (do not invent typed unit/reader typedef beyond that plate). Static retail evidence only; exact scoring policy, runtime targeting UX, and rebuild parity remain unproven.”
- Independent instruction decoding closes the policy: three ordered eligibility gates; strict squared-range admission; first-match categories Vehicle, Infantry, Air Unit, Emplacement, Building, Naval mapped to `CUnitAttackPriority` indices `1,4,5,0,2,3` at profile offsets `+0x168,+0x174,+0x178,+0x164,+0x16C,+0x170`; the deterministic-only Component `0x80000` floor at index 6 / `+0x17C`; primary best `-999999`; equality-only secondary contest; `1000-distance` plus `1000000` in-band or `10000` above-band; and strict-greater stable replacement. A greater-primary candidate resets secondary but does not clear the old winner pointer.
- The first gate's exact 43-byte predicate requires a resolved non-null candidate, `TF_DYING` clear at `+0x2C`, and Unit field `+0x244` outside `{1,2}`. That field is not the source-crosswalked `EAIState` cell at `+0x210`. The second gate implements the complete allegiance table: `0`, `1`, and `6` accept only a different member of that set; candidate allegiance `2` accepts any owner only when live config `+0x128` is nonzero; all other values reject. Pinned source binds `0/1/2/6` to Forseti/Muspell/Neutral/Independent and repeatedly uses the spelling `IsTargetAlligence`, but its definition is absent.
- Owner allegiance selects the candidate list exactly as `1 -> CWorld+0x20` (`0/6` entries), `0 -> CWorld+0x30` (`1/6` entries), and every other value -> `GetThingNB` at `CWorld+0x00`. Each node is `{payload,next}` and is followed in stored order without using the set's shared iterator. Raw payload bit `0x20000000` identifies the `CSquad` resolver path through virtual slot `+0x128`; otherwise bit `0x10` retains a direct `CUnit`; unsupported or null resolutions skip. Eligibility, allegiance, capability, range reduction, and priority read the resolved unit, while the three distance loads at `0x004ff854..0x004ff863` still read the raw payload. This distinction is observable for squad wrappers.
- The third gate is a CUnit-owned candidate-capability transaction, not a simple linked-support predicate. It first requires candidate virtual slot 108; then accepts the first successful owner `+0x18C` list payload; otherwise it scans the ordered weapon-correlated `+0x17C` list. The first active target-mask match is final and passes only when terrain height minus candidate Z lies in that entry's selected `CWeaponMinTargetHeight`/`CWeaponMaxTargetHeight` window. A failed height window does not continue to a later weapon.
- Candidate vtable displacement `+0x164` is slot 89, source-backed as `CUnit::IsAThreat()`, not a candidate data offset. `CBattleEngine` overrides that slot with literal true exactly as `BattleEngine.h:250`; the base body at `0x004FD440` returns canonical zero/one from three ordered Unit subobject-list probes. Owner config `+0x138` is the normalized field written by shipped property `CUnitIgnoreThreats @ 0x00432E50`. If both are false/zero, retail substitutes positive-zero primary, skips the category ladder and Component floor, and still enters ordinary best-candidate comparison; this is not rejection.
- `CUnitIndiscriminate` owns normalized `config+0x128`. When nonzero, every candidate admitted through the three gates and strict range consumes one draw from the shared level-start-seeded gameplay stream and uses `(Random__NextLCGAbs()%65536)/8192`. This arm does not call `IsAThreat()` or read `CUnitIgnoreThreats`; it bypasses the category ladder and Component floor in all seven measured builds. Their RNG bodies share seed `123456`, multiplier `48271`, unusual modulus `214783647`, wrapped transition, sign-normalized return, and exact score domain `[0,65535/8192]`.
- `+0x0C` is a deletion-aware reader cell. Exact `CGenericActiveReader::SetReader` `[0x00401000,0x00401034)` (52 bytes, SHA-256 `5540848cb8c7cd9fd46fc6a2d068b76527166c61510dd33c36b2c4dc1e41dca2`) matches pinned source order: same-target no-op, unlink old, store new, register new. `+0x10` is a caller-supplied retained-target gate whose only proved nonzero producer supplies literal `1` during hierarchy propagation; it is not a timer. `+0x14` is construction-fixed fast-reuse eligibility: base init writes `1`, five PC construction paths overwrite it with `0`, slot 11 is its only accepted reader, and no post-construction writer was found.
- Fast reuse requires current target, target `GetStealth()`, nonzero `+0x14`, then the active/state predicate. PC's C3-only x87 test admits zero and unordered/NaN; Xbox and PS2 reject NaN. Fast reuse preserves reader and `+0x10`, then stores helper B before conditional helper A.
- Full selection pre-clears `+0x18` then `+0x1C`. A winner is passed to SetReader, receives one support update, then `+0x10=0`, then a second support update, the post-commit state gate, B, and conditional A; the common exit clears `+0x10` again. Later failure does not roll back the bound winner. No winner still invokes `SetReader(null)` before the gate clear. `RetailUnitAITargetTransaction` reproduces this ordered adapter plan. The displayed decompile SHA-256 remains `60e225ebd37a289c14b627b7c69c3984180efb23b6bf4687ed7941c12295ad99`.
- PC demo is instruction-shape identical. Two Xbox slot-11 bodies normalize identically, as do three PS2 slot-11 bodies; raw branches reproduce the deterministic and indiscriminate laws. This does not prove scenario stream phase, RNG period/frequency, helper purity, or all-float bit equivalence.
- `RetailUnitAITargetSelection` now supplies a pure adapter over three independently ordered, caller-captured world views. It reproduces the owner-side routing, squad/direct-unit transform, unsupported/null skip, stable traversal order, and raw-payload distance versus resolved-unit fields before executing the finite-domain scoring law. `RetailUnitAITargetTransaction` consumes that optional winner and emits the subsequent ordered calls/writes. The third capability transaction, mutable world/index ownership, monitor execution, and helper effects remain upstream; neither owner is wired to actor state.
- Structured inventory for this body: 0 caller record(s), 10 callee record(s), and 0 string-ref record(s).

## Error / edge behavior
Nullability, the finite branch/draw law, and the fast-reuse zero/NaN platform split are closed statically. Invalid objects, helper failures/side effects, scenario stream phase, RNG period/frequency, and other overflow/x87-versus-console scoring edges remain not_determinable and are not inferred from packet metadata.

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
- Canonical runtime note `reverse-engineering/binary-analysis/functions/CUnitAI__SelectOrRefreshCloseTarget_004ff710.md`, SHA-256 `cdc02acc5bb91b5b9d2f65aa076cff1c6306d293c4d4a5f2e647b655d146bd72`.
- Runtime promotion manifest `reverse-engineering/binary-analysis/unitai-targeting-runtime-replication-promotion-manifest-2026-08-24.tsv`, SHA-256 `09810bac7b5d39eacadc512cb29a0a223899b6625f95238c3dfc98a4708ea16c`; corrected capture SHA-256 `84DB81290B00CE15FBCEB579FD8BC8B4C793C3F947001544FA44918F4189D171`; wrapper receipt `A3D9E421EB12526405DF718C9142CE5BBE0AB829CAE6C9D614242BCE0138A96D`; independent adjudication `2C4B7987EC08FBBFCC063C793196BD66BBF5093480B7D54899883F36AD6FF6A7`.
- Provenance limit: take2's recording receipt is RECONSTRUCTED/PARTIAL; capture-time target hash was not independently bound. The trace and copied runtime are hash-bound now, and no claim is widened beyond this scenario.

## Confidence
2 — exact identity, ABI/return shape, branch-specific writes, all three eligibility transactions, deterministic and indiscriminate scoring policy, property/category identities, cross-build RNG law, console correspondence, one executed caller edge, receiver law, replicated entry→return envelope, and can-fail controls are reconciled. Pointed-to RTTI, remaining third-gate subobject names, scenario stream phase, numeric knife-edge parity, autonomous population, and other scenarios remain open. Proposed promotion: true.

## Unresolved questions
- Concrete gameplay names and layout ownership beyond the accessed offsets.
- Complete indirect-call target set, target RTTI, original name of Unit field `+0x244`, candidate slot-108 subclass behavior, and concrete first-list payload identity.
- RNG period/frequency, scenario-specific shared-stream phase, and
  cross-platform numeric knife-edge equivalence.
- Exact per-invocation receiver values, autonomous list population, and caller expectations outside the measured shared envelope.
- Cheapest falsifier: replay the corrected exact target table with the pinned v2 collector. Any non-READY result, count other than 86/86/41, non-`0x004ff702` caller, nesting/receiver/control failure, small-int/module-image validated return, or normalized shared-row hash other than `AD623E03…CDB0F` invalidates the bounded promotion.
