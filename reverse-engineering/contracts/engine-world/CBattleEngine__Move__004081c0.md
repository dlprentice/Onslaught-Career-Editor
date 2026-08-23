# CBattleEngine__Move

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static contract for `CBattleEngine__Move` at `0x004081c0`; packet-described behavior is retained with explicit unknowns and no promotion claim.
Evidence: MEASURED — READY packet/decompile, structured edges, closure identity, and independently recomputed pristine body bytes; runtime and source limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: references/Onslaught/BattleEngine.cpp | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x004081c0`

## Identity
- Body `[0x004081c0,0x00409751]`, 5522 bytes, 1487 closure instructions. Raw pristine-body SHA-256 `6ea00887045c25292f9830e1b2262230979614b616093f0f6453afbcf4493f0a`; closure range SHA-256 `9415968bf41cc923bf65084d24207fd77209174c140bb67fc32918c3d9bdbe70`; packet range-plus-bytes SHA-256 `e15183d856f5ecd78725d6d372c037445950dcfec3bb6f80dffd9b9736163c19`. All three were independently recomputed over the exact single contiguous inclusive range.
- Canonical name `CBattleEngine__Move` comes from the current closure/register row. Packet label matches canonical tracked name `CBattleEngine__Move`.
- Packet name source `USER_DEFINED` and signature source `USER_DEFINED` are counted provenance, not semantic proof.
- Campaign grade `C1_CANDIDATE_PARTIAL` / closure class `SEALED_STATIC_RECEIPT` / packet confidence `MEDIUM`. Proposed promotion: false.

## Calling convention
Packet records `__fastcall` for `void __fastcall CBattleEngine__Move(void * this)`. Register/stack placement beyond that packet declaration is not_determinable without a separate instruction-level ABI review.

## Prototype and parameter semantics
```c
void __fastcall CBattleEngine__Move(void * this)
```
- Packet-declared parameter list: `void * this`. Parameter labels are analyst/source intent; concrete object layouts, units, ownership, aliasing, and nullability remain not_determinable unless directly stated by the quoted packet comment below.

## Return value meaning
The packet signature declares `void`; no scalar return contract is claimed. Callee/side-effect completion and failure reporting remain bounded by the displayed body and its called/indirect targets.

## Globals read/written
- Decompile symbol references: `DAT_00672fd0`, `DAT_00704200`, `DAT_0083d9c0`, `DAT_00855090`, `DAT_00896988`, `DAT_008a9a98`, `DAT_008a9ac0`, `DAT_008a9ac4`, `DAT_009c3df0`, `_DAT_00622f08`, `_DAT_008969b8`, `s_hud__s_00623314`. Read/write direction for each symbol is not independently instruction-verified in this factory draft.

## Callees relied on / callers
- Callee `CActor__Move` `0x004015e0` ×1 site(s) (STATIC_DIRECT).
- Callee `Mat34__SetRows` `0x00401f10` ×1 site(s) (STATIC_DIRECT).
- Callee `ElapsedTime__BelowThreshold_D4` `0x00401fd0` ×1 site(s) (STATIC_DIRECT).
- Callee `CBattleEngine__HandleLocks` `0x00406560` ×1 site(s) (STATIC_DIRECT).
- Callee `CBattleEngine__UpdateCameraVectorsAndInput` `0x00407a50` ×1 site(s) (STATIC_DIRECT).
- Callee `LinkedPtrCursor__MoveFirstAndGet` `0x00409760` ×1 site(s) (STATIC_DIRECT).
- Callee `LinkedPtrCursor__MoveNextAndGet` `0x00409780` ×1 site(s) (STATIC_DIRECT).
- Callee `CUnit__PushTransformHistoryAndSetCurrent` `0x004097a0` ×1 site(s) (STATIC_DIRECT).
- Callee `CBattleEngine__GetLastValidRangeStep100` `0x00409880` ×1 site(s) (STATIC_DIRECT).
- Callee `CLine__ctor_copy` `0x004098e0` ×1 site(s) (STATIC_DIRECT).
- Callee `CMonitor__UpdateSoundEventPlaybackForReader` `0x00409950` ×1 site(s) (STATIC_DIRECT).
- Callee `CBattleEngine__Morph` `0x0040a580` ×1 site(s) (STATIC_DIRECT).
- Callee `CBattleEngine__UpdateAutoAim` `0x0040b120` ×1 site(s) (STATIC_DIRECT).
- Callee `CBattleEngine__AugmentWeapon` `0x0040de40` ×1 site(s) (STATIC_DIRECT).
- Callee `CMonitor__UpdateTrackedList_59C` `0x0040e940` ×1 site(s) (STATIC_DIRECT).
- Callee `CMonitor__FlushTrackedList_1D4` `0x0040eb50` ×1 site(s) (STATIC_DIRECT).
- Callee `CMonitor__UpdateTrackedList_620` `0x0040ebf0` ×1 site(s) (STATIC_DIRECT).
- Callee `CBattleEngine__GroundParticleEffect` `0x0040ef20` ×1 site(s) (STATIC_DIRECT).
- Callee `CBattleEngineJetPart__Move` `0x00410c50` ×1 site(s) (STATIC_DIRECT).
- Callee `CBattleEngineJetPart__LoseWeaponCharge` `0x00412000` ×1 site(s) (STATIC_DIRECT).
- Callee `CBattleEngineWalkerPart__Move` `0x00413760` ×2 site(s) (STATIC_DIRECT).
- Callee `CMonitor__ClearCurrentTrackedEntryFlag60` `0x00414010` ×1 site(s) (STATIC_DIRECT).
- Callee `CController__SetVibration` `0x0042e750` ×1 site(s) (STATIC_DIRECT).
- Callee `CEulerAngles__ctor_from_FMatrix` `0x0044adb0` ×1 site(s) (STATIC_DIRECT).
- Callee `CEventManager__AddEvent_AtTime` `0x0044b370` ×1 site(s) (STATIC_DIRECT).
- Callee `CGame__GetController` `0x004705d0` ×1 site(s) (STATIC_DIRECT).
- Callee `CMapWho__GetFirstEntryWithinRadius` `0x00491ea0` ×1 site(s) (STATIC_DIRECT).
- Callee `CMapWho__GetNextEntryWithinRadius` `0x00492020` ×1 site(s) (STATIC_DIRECT).
- Callee `CMapWhoEntry__GetOwner` `0x00492c90` ×1 site(s) (STATIC_DIRECT).
- Callee `CMCMech__TranslatePositions` `0x00499d60` ×1 site(s) (STATIC_DIRECT).
- Callee `CPlayer__GotoFPView` `0x004d28c0` ×1 site(s) (STATIC_DIRECT).
- Callee `CPlayer__GotoControlView` `0x004d2a50` ×1 site(s) (STATIC_DIRECT).
- Callee `CSoundManager__FadeTo` `0x004e1260` ×1 site(s) (STATIC_DIRECT).
- Callee `CSoundManager__GetSoundEventForThing` `0x004e1880` ×2 site(s) (STATIC_DIRECT).
- Callee `CSoundManager__SetPitch` `0x004e18d0` ×1 site(s) (STATIC_DIRECT).
- Callee `CSoundManager__GetEffectByName` `0x004e1910` ×7 site(s) (STATIC_DIRECT).
- Callee `CSoundManager__PlayEffect` `0x004e1940` ×8 site(s) (STATIC_DIRECT).
- Callee `CSoundManager__IsEffectPlaying` `0x004e1ab0` ×1 site(s) (STATIC_DIRECT).
- Callee `CSPtrSet__Remove` `0x004e5bd0` ×1 site(s) (STATIC_DIRECT).
- Callee `CWorld__FindFirstThingToHitLine` `0x0050b030` ×1 site(s) (STATIC_DIRECT).
- Callee `CDXMemoryManager__Free` `0x00549220` ×1 site(s) (STATIC_DIRECT).
- Callee `sprintf` `0x0055de9b` ×7 site(s) (STATIC_DIRECT).
- Callers: none in the packet structured array.
- Structured packet arrays prove the listed direct/static edge identities and site counts only. Indirect vtable targets, library inlining, and data-driven dispatch remain unresolved unless separately named in the packet.

## Behavior summary
- Source-first owner/target branch: `references/Onslaught/BattleEngine.cpp` lines `1270-1760` defines `CBattleEngine::Move` as `void CBattleEngine::Move()`; exact extracted source-body SHA-256 `8d6e8a6a4da057de1ad34bbc14c34b7024aafe2bd38000bf26f7ec0688a0745d`.
- Source algorithm skeleton (mechanical, not a retail claim): control counts if=76, switch=1, for=2, while=1; named call tokens `ActivateThrusters`, `AddEvent`, `AddMessage`, `AddMovement`, `AugmentWeapon`, `COfGHeight`, `Collide`, `Damage`, `DeactivateThrusters`, `DeclareOnGround`, `DeclareOnObject`, `Decloak`, `FVector`, `FadeTo`, `FindFirstThingToHitLine`, `GetAmmoDepletedTime`, `GetCharge`, `GetController`, `GetCurrentWeapon`, `GetDangerStartTime`, `GetFirstEntryWithinRadius`, `GetGameState`, `GetJetPart`, `GetNextEntryWithinRadius` (+46 more tokens).
- Source-to-retail status: `SOURCE_ANALOG` is architecture/name intent only. Every source branch, call, field name, and ordering rule remains a hypothesis until the retail packet/body below independently agrees.
- Source-vs-retail delta/unknown boundary: no unlisted equivalence is assumed; platform conditionals, concrete layouts, omitted/inlined calls, constants, failure paths, and runtime causality remain open unless the packet comment/decompile or cited tracked evidence states the same fact.
- Existing packet analyst comment (quoted as bounded packet evidence, not silently upgraded): “High-confidence static owner and source correction: the CBattleEngine RTTI/vtable slot at 0x005d8acc targets this register-only body. It processes damage, engine, stealth, safe-position, vibration, and HUD state; calls CBattleEngine__HandleLocks at 0x00408b84; dispatches WalkerPart or JetPart at +0x578 or +0x57c; then performs actor movement and collision, rotation, auto-aim and sound, and thruster and ground-effect work in Stuart CBattleEngine::Move order. Static retail identity and structure only; exact layouts, final calling-convention spelling, runtime timing or movement, controls, camera, gameplay, installed-game patching, and rebuild parity remain unproven.”
- The displayed decompile is non-empty and SHA-256 `4315eed68c6429ababdaafe8df46b35fcf71c84ef036d08b855e996cbbe33ddd`. This factory draft preserves that packet-described control/side-effect intent but does not infer unstated field meanings, units, ordering guarantees, or runtime causality.
- Structured inventory for this body: 0 caller record(s), 42 callee record(s), and 6 string-ref record(s).

## Error / edge behavior
Nullability, invalid-state behavior, allocation failure, indirect-call failure, NaN/overflow behavior, and rollback semantics are not_determinable as a class from the packet metadata. The decompile and quoted comment are the bounded static evidence; any missing branch-level edge contract remains an open question rather than an invented default.

## Runtime corroboration (TTD, bounded)
The bounded TTD table contains these exact rows; they establish only execution/coverage in the named captures unless the value itself states a stronger measured fact:
- Session `all level-openings`; question `corpus-open-core`; value: invariant across all 66 openings; 129,099 cumulative covered bytes; evidence `name=CBattleEngine__Move`.

## Evidence
- Writer-task authority: task `t_efc238f0`, cohort 7 immutable manifest SHA-256 `d2ac6ace069c4ff409cd9aaec49022fb08589f5637367a823baa4b65053cc9ef`, row 6; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750` and proposed promotion false. The task comment/independent-review receipts are the durable manifest authority; no writer-local scratch path is claimed as tracked evidence.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x004081c0.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`); packet decompile SHA-256 `4315eed68c6429ababdaafe8df46b35fcf71c84ef036d08b855e996cbbe33ddd`.
- Digest derivation: closure SHA-256 hashes canonical range text `004081c0:00409751;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
- Closure execution state `PARTIAL` and confidence `MEDIUM`; these are inherited bounded grades, not this factory's promotion decision.
- Packet string ref `0x006232bc` length 23 SHA-256 `3e78c301132a0cd17717e1944bfaea7d3762fcbd55b98ff3c06552f61418ea70` value “HUD_Weapon_Overheating”.
- Packet string ref `0x006232d4` length 24 SHA-256 `4a3ea7502a74e319c7c41c28df07a4cc797fd3c98f626c41c9d4d04d921fa5ca` value “hud_ammunition_depleted”.
- Packet string ref `0x006232ec` length 21 SHA-256 `d2be26056c51c0c2654d8541cab772ec0fb8b8962994ccacb40aefe6c7360eda` value “hud_incoming_warhead”.
- Packet string ref `0x00623304` length 15 SHA-256 `1b33fe393b15fec21a01c6bef3240d9bca946d26e25700692685a638a5d146c8` value “hud_energy_low”.
- Packet string ref `0x00623314` length 7 SHA-256 `48ef110d1220e76bbd22f8dccfacdcb1362806a52e54b1b40d026d007a2f7e29` value “hud\\%s”.
- Packet string ref `0x0062331c` length 15 SHA-256 `30e293dfee17e89ed8e07987ea2272b553838634e9e6ee7b383c9a4cb2ed251a` value “hud_armour_low”.
- Source crosswalk: `references/Onslaught/BattleEngine.cpp` `CBattleEngine::Move` line 1270 (`SOURCE_ANALOG`), evidence `reverse-engineering/binary-analysis/functions/BattleEngine.cpp/CBattleEngine__Move.md`. This is source/name architecture evidence at the stated class, not independent retail behavior proof.

## Confidence
1 — exact identity, contiguous pristine bytes, digest derivations, signature text, and structured edge inventory are reconciled; field-level semantics and runtime causality remain bounded to the packet/decompile and any cited source/TTD rows. A packet/canonical name discrepancy forces confidence 0. Proposed promotion: false.

## Unresolved questions
- Instruction-level read/write direction and concrete layout for every referenced field/global.
- Complete indirect-call target set and failure/nullability behavior.
- Runtime ordering, side effects, return-domain meaning, and caller expectations beyond the bounded packet evidence.
- Cheapest falsifier: cold-disassemble this exact raw-body digest, compare every branch/load/store/call against the packet decompile and structured arrays, then run a controlled copied-runtime probe for the named input/state transition.
