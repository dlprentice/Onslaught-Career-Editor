# ProjectileBurst__SpawnFromCurrentPreset

Status: active static contract (factory draft)
Last updated: 2026-08-23
Summary: specimen-bound static contract for `ProjectileBurst__SpawnFromCurrentPreset` at `0x005069f0` in the render/effects/platform-support cohort; bounded behavior, evidence limits, and no-promotion disposition are explicit.
Evidence: MEASURED — current name/register identity, READY packet/decompile, structured edges, closure range, and independently recomputed pristine body bytes; source and runtime limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no selected source-crosswalk owner) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x005069f0`

## Identity
- Body `[0x005069f0,0x005078ab]`, 3772 bytes, 906 closure instructions. Raw pristine-body SHA-256 `124b166f80acecc01ae2bf18b876c7c1202015aea1ba2b8303414fde973f8e5d`; closure range SHA-256 `108eb147c5146edb494ea2b5d0eda1d101ffebc3e030ff3cfefd60526373c9f3`; packet range-plus-bytes SHA-256 `6f92bd13c37aa98a8867493980688873fbef689ad6e95f7126790ac603372171`. All three were independently recomputed over the exact single contiguous inclusive range.
- Current 8,329-row name table and current EVIDENCE-REGISTER both name `ProjectileBurst__SpawnFromCurrentPreset`. The READY packet agrees. The dated closure spelling also matches the current identity.
- Packet name/signature provenance is counted metadata, not semantic proof. Packet file SHA-256 `2eeb1b06707a5971692d6c5faeb9d325676954528395de69cd4159a9f9524841` and decompile SHA-256 `79e49a0071b07eee21c4885af204c26f8695df5694ff92d8abf4fe6bfc58cf87` bind the retained review input without citing a writer-local scratch path.
- Campaign grade `C1_CANDIDATE_PARTIAL` / register grade `C1_CANDIDATE_PARTIAL` / register contract state `OPEN_EXECUTED` / closure class `SEALED_STATIC_RECEIPT` / packet confidence `MEDIUM_STATIC`. Proposed promotion: false.

## Calling convention
Packet records `__fastcall` for `int __fastcall ProjectileBurst__SpawnFromCurrentPreset(void * burstContext)`. Register/stack placement beyond that packet declaration is not_determinable without a separate instruction-level ABI review.

## Prototype and parameter semantics
```c
int __fastcall ProjectileBurst__SpawnFromCurrentPreset(void * burstContext)
```
- Packet-declared parameter list: `void * burstContext`. Parameter labels are analyst/source intent; concrete object layouts, units, ownership, aliasing, and nullability remain not_determinable unless directly stated by the quoted packet comment or source-first boundary below.

## Return value meaning
The packet signature declares `int`. Exact domain meaning of the returned bits/value is not_determinable from identity and decompile evidence alone; no stronger meaning is invented.

## Globals read/written
- Decompile symbol references: `DAT_00855040`, `DAT_00855044`, `DAT_00855048`, `DAT_0085504c`, `DAT_00896988`, `DAT_0089c9a0`, `DAT_008a9d9c`. Read/write direction for each symbol is not independently instruction-verified by this factory.

## Callees relied on / callers
- Callee `CGenericActiveReader__SetReader` `0x00401000` x1 site(s) (STATIC_DIRECT).
- Callee `Vec3__SetXYZ` `0x00401ec0` x8 site(s) (STATIC_DIRECT).
- Callee `Mat34__SetRows` `0x00401f10` x2 site(s) (STATIC_DIRECT).
- Callee `Vec3__Magnitude` `0x004026b0` x1 site(s) (STATIC_DIRECT).
- Callee `Mat34__SetFromEulerAngles_004062d0` `0x004062d0` x3 site(s) (STATIC_DIRECT).
- Callee `CBattleEngine__FireLock` `0x00407060` x1 site(s) (STATIC_DIRECT).
- Callee `CBattleEngine__DisplayLock` `0x00407310` x1 site(s) (STATIC_DIRECT).
- Callee `LinkedPtrCursor__MoveFirstAndGet` `0x00409760` x1 site(s) (STATIC_DIRECT).
- Callee `CUnit__PushTransformHistoryAndSetCurrent` `0x004097a0` x2 site(s) (STATIC_DIRECT).
- Callee `CBattleEngine__CanSpawnBurstForResolvedEntry` `0x0040c2e0` x1 site(s) (STATIC_DIRECT).
- Callee `CBattleEngine__RandomizeBurstOffsetsAndAccumulateRange` `0x0040c340` x1 site(s) (STATIC_DIRECT).
- Callee `CEngine__TrackBurstEventFromPreset` `0x0044a610` x1 site(s) (STATIC_DIRECT).
- Callee `OID__GetAttachmentOrBaseOrientationMatrix` `0x0044a930` x1 site(s) (STATIC_DIRECT).
- Callee `CInitThing__ctor` `0x0048dcf0` x2 site(s) (STATIC_DIRECT).
- Callee `OID__CreateObject` `0x004bf090` x1 site(s) (STATIC_DIRECT).
- Callee `ParticleEffectLink_T3_004cb040` `0x004cb040` x1 site(s) (STATIC_DIRECT).
- Callee `CParticleManager__RemoveOwnerLinkFromGlobalList` `0x004cb050` x1 site(s) (STATIC_DIRECT).
- Callee `CParticleManager__CreateEffect` `0x004cb3d0` x2 site(s) (STATIC_DIRECT).
- Callee `CRound__SetTargetReaderIfAllowed` `0x004daab0` x1 site(s) (STATIC_DIRECT).
- Callee `Random__NextLCGAbs` `0x004de8d0` x6 site(s) (STATIC_DIRECT).
- Callee `CShell__CopyResourceNameToInlineBuffer` `0x004df530` x1 site(s) (STATIC_DIRECT).
- Callee `CSoundManager__PlayEffect` `0x004e1940` x1 site(s) (STATIC_DIRECT).
- Callee `CThing__GetCentrePos` `0x004f3ac0` x1 site(s) (STATIC_DIRECT).
- Callee `Mat34__SetFromEulerDegrees` `0x004f8140` x1 site(s) (STATIC_DIRECT).
- Callee `ProjectileBurstPreset__GetListEntryIdByIndex` `0x005078b0` x1 site(s) (STATIC_DIRECT).
- Callee `CUnit__ComputeMaxBallisticTravelDistance` `0x005099a0` x1 site(s) (STATIC_DIRECT).
- Callee `CWorldPhysicsManager__CreateProjectile` `0x0050f7a0` x1 site(s) (STATIC_DIRECT).
- Callee `CRT__AcosDispatch_ST0` `0x0055dcb0` x1 site(s) (STATIC_DIRECT).
- Caller `ProjectileBurst__SpawnFromPercentBucketFallback` `0x00506010` x1 site(s) (instruction-flow).
- Caller `CWeapon__HandleFireBurstEvent` `0x00506930` x1 site(s) (instruction-flow).
- Structured packet arrays prove the listed direct/static edge identities and site counts only. Indirect vtable targets, library inlining, and data-driven dispatch remain unresolved unless separately named in the packet.

## Behavior summary
- Packet-first row: neither the current canonical crosswalk nor the five landed expansion receipts owns this VA. The retail packet/pristine body is therefore the first behavior envelope.
- Retail packet analyst comment (quoted as bounded packet evidence, never promoted by this file): “Owner-neutral correction for the current-preset projectile-burst body. It creates projectile/effect objects from burstContext +0xa0 and is reached from the weapon event handler plus the percent-bucket fallback helper. Static Ghidra evidence only; raw percent-bucket fallback callsites are now bounded at ProjectileBurstCallerBoundary_0044e020 and ProjectileBurstCallerBoundary_004f4920. Proof-boundary: exact CWeapon::Fire, CBattleEngine::WeaponFired, weapon_fire_breaks_stealth, runtime stealth behavior, tags/locals/types, and concrete layout remain unproven.”
- The non-empty packet decompile is bound by SHA-256 `79e49a0071b07eee21c4885af204c26f8695df5694ff92d8abf4fe6bfc58cf87`. This contract retains only its displayed control/side-effect envelope and does not infer unstated field meanings, units, ordering guarantees, or runtime causality.
- Structured inventory: 2 caller record(s), 28 callee record(s), and 0 string-ref record(s).

## Error / edge behavior
Nullability, invalid-state behavior, allocation/device failure, indirect-call failure, overflow/NaN behavior, and rollback semantics are not_determinable as a class from packet metadata. The decompile, quoted comment, and any source-first algorithm above are bounded evidence; missing branch-level behavior remains open rather than receiving an invented default.

## Runtime corroboration (TTD, bounded)
The bounded TTD table contains these exact rows; they establish only execution/coverage in the named captures unless a row states a stronger measured fact:
- Session `batch-1`; question `contract-round-impact`; value: corroborated in 7/10 coverage sessions; evidence `level-opening-3m-v1-level110, level-opening-3m-v1-level200, level-opening-3m-v1-level201, level-opening-3m-v1-level211 …`.
- Session `batch-2`; question `contract-round-impact`; value: corroborated in 7/10 coverage sessions; evidence `level-opening-3m-v1-level311, level-opening-3m-v1-level312, level-opening-3m-v1-level321, level-opening-3m-v1-level322 …`.
- Session `batch-3`; question `contract-round-impact`; value: corroborated in 8/10 coverage sessions; evidence `level-opening-3m-v1-level421, level-opening-3m-v1-level422, level-opening-3m-v1-level431, level-opening-3m-v1-level432 …`.
- Session `batch-4`; question `contract-round-impact`; value: corroborated in 2/10 coverage sessions; evidence `level-opening-3m-v1-level720, level-opening-3m-v1-level731`.
- Session `batch-5`; question `contract-round-impact`; value: corroborated in 5/10 coverage sessions; evidence `level-opening-3m-v1-level732, level-opening-3m-v1-level741, level-opening-3m-v1-level742, level-opening-3m-v1-level854 …`.
- Session `batch-6`; question `contract-round-impact`; value: corroborated in 5/11 coverage sessions; evidence `level-opening-3m-v1-level856, level-opening-3m-v1-level858, level-opening-3m-v1-level859, level-opening-3m-v1-level862 …`.
- Session `batch-7`; question `contract-round-impact`; value: corroborated in 2/7 coverage sessions; evidence `level521-native-20260802-0018-take1, level521-native-20260802-0018-take2`.
- Session `batch-8`; question `contract-round-impact`; value: corroborated in 1/4 coverage sessions; evidence `level521-native-20260802-0018-take4`.
- Session `batch-9`; question `contract-round-impact`; value: corroborated in 2/3 coverage sessions; evidence `q-pilot-cov-l742-20260731, q-pilot-cov-l742-rep2-20260731`.
- Session `batch-10`; question `contract-round-impact`; value: no coverage collector output for this batch's sessions; evidence `batch carries no BEA.exe coverage bitmap (query/infra captures)`.

## Evidence
- Writer authority: task `t_5b694f87`, immutable cohort-9 manifest SHA-256 `ebf607a5672b6d0dd95cf0ecf31d8fa9c2053b4ebe50fd2fe2f39bb8ceda9be8`, row 8; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, exact current identity, and proposed promotion false. The task comment and independent review receipt are the durable manifest route; no writer-local scratch path is cited here.
- Current identity joins: `reverse-engineering/binary-analysis/ghidra-function-name-table-2026-08-17.tsv`, `reverse-engineering/EVIDENCE-REGISTER.tsv`, and `reverse-engineering/binary-analysis/function-c1-closure-2026-08-11.tsv`. The current name table/register pair wins over any dated closure spelling.
- READY packet schema `bea.re.triage-packet.v1`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, packet-file SHA-256 `2eeb1b06707a5971692d6c5faeb9d325676954528395de69cd4159a9f9524841`, and packet decompile SHA-256 `79e49a0071b07eee21c4885af204c26f8695df5694ff92d8abf4fe6bfc58cf87`; retained locally for cold review without a tracked local-path citation.
- Digest derivation: closure SHA-256 hashes canonical range text `005069f0:005078ab;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
- Closure execution state `PARTIAL` and confidence `MEDIUM_STATIC`; these are inherited bounded grades, not this factory's promotion decision.
- Packet stringRefs array: empty.
- Source crosswalk: no selected canonical or landed-expansion row for this VA.

## Confidence
1 — exact current identity, contiguous pristine bytes, digest derivations, signature text, structured edge inventory, comments, strings, source joins, and TTD presence/absence are reconciled. Field-level semantics and runtime causality remain bounded. Proposed promotion: false.

## Unresolved questions
- Instruction-level read/write direction and concrete layout for every referenced field/global.
- Complete indirect-call target set and failure/nullability behavior.
- Runtime ordering, side effects, return-domain meaning, and caller expectations beyond the bounded packet/source/TTD evidence.
- Cheapest falsifier: cold-disassemble this exact raw-body digest, compare every branch/load/store/call against the packet decompile and structured arrays, then run a controlled copied-runtime probe for the named input/state transition.
