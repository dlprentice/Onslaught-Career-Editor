# CBattleEngine__Init

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static contract for `CBattleEngine__Init` at `0x00404dd0`; packet-described behavior is retained with explicit unknowns and no promotion claim.
Evidence: MEASURED — READY packet/decompile, structured edges, closure identity, and independently recomputed pristine body bytes; runtime and source limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: references/Onslaught/BattleEngine.cpp | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x00404dd0`

## Identity
- Body `[0x00404dd0,0x004058f9]`, 2858 bytes, 710 closure instructions. Raw pristine-body SHA-256 `44f563280d5c5748d2d09490113f4a5c27fa0d6c9e7d09a9abc8da0eece7dde0`; closure range SHA-256 `fc848420034efff85366537255817ba9888fab2c6a736cba271cd2ad845a6c13`; packet range-plus-bytes SHA-256 `77db742b0c392b685a3f8fd2892a485de35fd38cebfb70d6a1a65b1e41d16e3c`. All three were independently recomputed over the exact single contiguous inclusive range.
- Canonical name `CBattleEngine__Init` comes from the current closure/register row. Packet label matches canonical tracked name `CBattleEngine__Init`.
- Packet name source `USER_DEFINED` and signature source `USER_DEFINED` are counted provenance, not semantic proof.
- Campaign grade `C1_CANDIDATE_PARTIAL` / closure class `SEALED_STATIC_RECEIPT` / packet confidence `HIGH`. Proposed promotion: false.

## Calling convention
Packet records `__thiscall` for `void __thiscall CBattleEngine__Init(void * this, void * init)`. Register/stack placement beyond that packet declaration is not_determinable without a separate instruction-level ABI review.

## Prototype and parameter semantics
```c
void __thiscall CBattleEngine__Init(void * this, void * init)
```
- Packet-declared parameter list: `void * this, void * init`. Parameter labels are analyst/source intent; concrete object layouts, units, ownership, aliasing, and nullability remain not_determinable unless directly stated by the quoted packet comment below.

## Return value meaning
The packet signature declares `void`; no scalar return contract is claimed. Callee/side-effect completion and failure reporting remain bounded by the displayed body and its called/indirect targets.

## Globals read/written
- Decompile symbol references: `DAT_0062308c`, `DAT_006230a4`, `DAT_006601b0`, `DAT_006601b4`, `DAT_00663498`, `DAT_0066f580`, `DAT_00672fd0`, `DAT_0082b400`, `DAT_00896988`, `DAT_008a9a98`, `DAT_008a9d38`, `DAT_008a9d9c`, `DAT_009c3df0`, `s_BE_Energy_Critical_006231d4`, `s_BE_Energy_Low_006231c4`, `s_BE_Engines_in_flight__00623210`, `s_BE_Engines_land__006231fc`, `s_BE_Engines_takeoff__006231e8`, `s_BE_Ground_Effect_Land_Effect_006230e0`, `s_BE_Ground_Effect_Water_Effect_00623100`, `s_BE_Hydraulics_02_00623160`, `s_BE_Incoming_Missile_0062318c`, `s_BE_On_02_00623174`, `s_BE_Strafe_L_R_006231b4`, `s_BE_Target_00623180`, `s_BE_Target_Locked_006231a0`, `s_C__dev_ONSLAUGHT2_BattleEngine_c_006230bc`, `s_Engine_00622cec`, `s_Is_the_battle_engine_visible__00623034`, `s_LegMotion_00623074`, `s_Thruster_00623080`, `s_be_afterburner_effect_00623120`, `s_be_engine_effect_00623138`, `s_be_thruster_effect_0062314c`, `s_cg_battleenginevisible_0062301c`, `s_currently_running_level____d_00623054`, `s_m_be1_msh_006230b0`, `s_m_be2_msh_00623098`. Read/write direction for each symbol is not independently instruction-verified in this factory draft.

## Callees relied on / callers
- Callee `CGenericActiveReader__SetReader` `0x00401000` ×4 site(s) (STATIC_DIRECT).
- Callee `CBattleEngine__SwapPrimarySecondaryPartReadersForState` `0x00406460` ×1 site(s) (STATIC_DIRECT).
- Callee `CBattleEngine__HandleAutoAim` `0x0040b6d0` ×1 site(s) (STATIC_DIRECT).
- Callee `CBattleEngine__UpdateConfiguration` `0x0040c650` ×1 site(s) (STATIC_DIRECT).
- Callee `CBattleEngineJetPart__ctor` `0x00410210` ×1 site(s) (STATIC_DIRECT).
- Callee `CBattleEngineWalkerPart__ctor` `0x00412bc0` ×1 site(s) (STATIC_DIRECT).
- Callee `CCockpit__ctor` `0x004244b0` ×1 site(s) (STATIC_DIRECT).
- Callee `CConsole__RegisterVariable` `0x0042b040` ×1 site(s) (STATIC_DIRECT).
- Callee `CConsole__Printf` `0x00441740` ×1 site(s) (STATIC_DIRECT).
- Callee `CEventManager__AddEvent_AtTime` `0x0044b370` ×1 site(s) (STATIC_DIRECT).
- Callee `CGame__IsMultiplayer` `0x004725d0` ×1 site(s) (STATIC_DIRECT).
- Callee `CMCMech__Constructor` `0x004983b0` ×1 site(s) (STATIC_DIRECT).
- Callee `CMCMech__SetParams` `0x00498bf0` ×1 site(s) (STATIC_DIRECT).
- Callee `CMesh__FindAnimationIndexByName` `0x004aa630` ×1 site(s) (STATIC_DIRECT).
- Callee `ParticleEffectLink_T3_004cb040` `0x004cb040` ×2 site(s) (STATIC_DIRECT).
- Callee `CParticleSet__FindByNameAndTrackLinkSlot` `0x004cd7a0` ×5 site(s) (STATIC_DIRECT).
- Callee `CRadarWarningReceiver__Init` `0x004d65a0` ×1 site(s) (STATIC_DIRECT).
- Callee `Random__NextLCGAbs` `0x004de8d0` ×1 site(s) (STATIC_DIRECT).
- Callee `CSoundManager__GetEffectByName` `0x004e1910` ×11 site(s) (STATIC_DIRECT).
- Callee `CSPtrSet__Init` `0x004e5840` ×1 site(s) (STATIC_DIRECT).
- Callee `CSPtrSet__AddToHead` `0x004e5a80` ×1 site(s) (STATIC_DIRECT).
- Callee `CSPtrSet__AddToTail` `0x004e5b20` ×2 site(s) (STATIC_DIRECT).
- Callee `CUnit__Init` `0x004f86d0` ×1 site(s) (STATIC_DIRECT).
- Callee `PCRTID__CreateObject` `0x00516580` ×2 site(s) (STATIC_DIRECT).
- Callee `CDXMemoryManager__Alloc` `0x005490e0` ×8 site(s) (STATIC_DIRECT).
- Callee `CRT__EhVectorDestructorIterator_WithUnwind` `0x0055db0a` ×1 site(s) (STATIC_DIRECT).
- Callee `eh_vector_constructor_iterator` `0x0055dc20` ×1 site(s) (STATIC_DIRECT).
- Callers: none in the packet structured array.
- Structured packet arrays prove the listed direct/static edge identities and site counts only. Indirect vtable targets, library inlining, and data-driven dispatch remain unresolved unless separately named in the packet.

## Behavior summary
- Source-first owner/target branch: `references/Onslaught/BattleEngine.cpp` lines `63-353` defines `CBattleEngine::Init` as `void	CBattleEngine::Init(CInitThing* init)`; exact extracted source-body SHA-256 `4e8a6ae43eee67bdf775985b0dfd1214f4d13132af669f0a6af28ec8fb34c0cd`.
- Source algorithm skeleton (mechanical, not a retail claim): control counts if=14, switch=0, for=1, while=2; named call tokens `Add`, `AddEvent`, `AddMessage`, `AddVelocity`, `Append`, `CBattleEngineJetPart`, `CBattleEngineWalkerPart`, `CCOCKPIT`, `CCylinder`, `CMCBattleEngine`, `CMCBuggy`, `COfGHeight`, `CValidatedFoR`, `Engines`, `FVector`, `FloatRandom`, `GetAnimModeByName`, `GetCurrentlyRunningLevelNum`, `GetEffectByName`, `GetPD`, `GetRTEmitter`, `GetRTMesh`, `GetRadius`, `GetTime` (+15 more tokens).
- Source-to-retail status: tracked `SOURCE_EXACT` class supplies named identity plus tracked source-body-agreement evidence. The packet/pristine checks below independently pin the retail target; this factory does not silently widen the tracked exactness beyond that evidence row.
- Source-vs-retail delta/unknown boundary: no unlisted equivalence is assumed; platform conditionals, concrete layouts, omitted/inlined calls, constants, failure paths, and runtime causality remain open unless the packet comment/decompile or cited tracked evidence states the same fact.
- Existing packet analyst comment (quoted as bounded packet evidence, not silently upgraded): “Signature/comment correction: CBattleEngine init takes a CBattleEngineInitThing-like stack argument (ret 0x4), resolves sound/effect resources, constructs walker/jet parts, initializes reader/state fields, and zeros stealth-adjacent fields +0x5d4/+0x5d8/+0x5dc. Exact layouts/source identity, weapon_fire_breaks_stealth, runtime init behavior, and rebuild parity remain unproven.”
- The displayed decompile is non-empty and SHA-256 `6479db9dd127938e8a76427acf0eca0d9a72a391f109552a78d775e6e9767a5b`. This factory draft preserves that packet-described control/side-effect intent but does not infer unstated field meanings, units, ordering guarantees, or runtime causality.
- Structured inventory for this body: 0 caller record(s), 27 callee record(s), and 27 string-ref record(s).

## Error / edge behavior
Nullability, invalid-state behavior, allocation failure, indirect-call failure, NaN/overflow behavior, and rollback semantics are not_determinable as a class from the packet metadata. The decompile and quoted comment are the bounded static evidence; any missing branch-level edge contract remains an open question rather than an invented default.

## Runtime corroboration (TTD, bounded)
The bounded TTD table contains these exact rows; they establish only execution/coverage in the named captures unless the value itself states a stronger measured fact:
- Session `all level-openings`; question `corpus-open-core`; value: invariant across all 66 openings; 182,236 cumulative covered bytes; evidence `name=CBattleEngine__Init`.

## Evidence
- Writer-task authority: task `t_efc238f0`, cohort 7 immutable manifest SHA-256 `d2ac6ace069c4ff409cd9aaec49022fb08589f5637367a823baa4b65053cc9ef`, row 1; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750` and proposed promotion false. The task comment/independent-review receipts are the durable manifest authority; no writer-local scratch path is claimed as tracked evidence.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x00404dd0.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`); packet decompile SHA-256 `6479db9dd127938e8a76427acf0eca0d9a72a391f109552a78d775e6e9767a5b`.
- Digest derivation: closure SHA-256 hashes canonical range text `00404dd0:004058f9;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
- Closure execution state `PARTIAL` and confidence `HIGH`; these are inherited bounded grades, not this factory's promotion decision.
- Packet string ref `0x00622cec` length 7 SHA-256 `8e75ebbdb21505d2f18439f43fe046abc67fc567515bb1d53b855a020a179092` value “Engine”.
- Packet string ref `0x0062301c` length 23 SHA-256 `aa25ca8b0416bd3b4dab36d990a90417424a119b89d508092d066413e9e64025` value “cg_battleenginevisible”.
- Packet string ref `0x00623034` length 30 SHA-256 `543f1025f64c201bb433654ff47ab053705fe782455f302aad07ebfe2edaabad` value “Is the battle engine visible?”.
- Packet string ref `0x00623054` length 29 SHA-256 `32f2f2bbaa6b8a6c3337dc6bd92ce13a5720e089d458387c0445ef284affe5cb` value “currently running level = %d”.
- Packet string ref `0x00623074` length 10 SHA-256 `3951b9884ddd56735b97cba326c3cfca953a0710c18fd041686e27c83fc35984` value “LegMotion”.
- Packet string ref `0x00623080` length 9 SHA-256 `1225c9d3a468183402dde496d5651960c79c9d60e8ed85c7ee38a2d678006ef3` value “Thruster”.
- Packet string ref `0x0062308d` length 9 SHA-256 `359d441ba0517f942b5a4227d95555cb133a03703a56d7dda8a57519c9b8b755` value “_be2.msh”.
- Packet string ref `0x00623098` length 10 SHA-256 `c553a749f1a45c0ca5613ac83b71ae754c045391cf6e10dfe30aec3362b7d81f` value “m_be2.msh”.
- Packet string ref `0x006230a5` length 9 SHA-256 `3a06c1e2488830f047773e090ce65cdbf7ef1800838e44eaa5c5fb7d293cb2ff` value “_be1.msh”.
- Packet string ref `0x006230b0` length 10 SHA-256 `03d4c6dec5caef3af991521fe35873e83adf0e990629ec5eef7ae230b561c3cc` value “m_be1.msh”.
- Packet string ref `0x006230bc` length 35 SHA-256 `0469e415183a714b133ceb95e28409293389b49573750318193b95dfad3a1558` value “C:\\dev\\ONSLAUGHT2\\BattleEngine.cpp”.
- Packet string ref `0x006230e0` length 29 SHA-256 `800a70876654353d1bca52c6c29a7210712bcc8b29b17279e2f9d552a43141c1` value “BE Ground Effect Land Effect”.
- Packet string ref `0x00623100` length 30 SHA-256 `026d83c61b22a666b50034a2648262d6ed0ef2e30b951b0919a0e24fe2e01e24` value “BE Ground Effect Water Effect”.
- Packet string ref `0x00623120` length 22 SHA-256 `7ebd0556309c7bc96960a482dca03cfa01e8d652a97199a2d6f77eead39098ed` value “be afterburner effect”.
- Packet string ref `0x00623138` length 17 SHA-256 `89c586e6a437752ff6354a8c6a25ac3fb7426eddce964e4eebb2a1b99f43e024` value “be engine effect”.
- Packet string ref `0x0062314c` length 19 SHA-256 `da3dc743330a4abc9b07bcd392bcd905941a50917f29ead6d3b951a974c7fea0` value “be thruster effect”.
- Packet string ref `0x00623160` length 17 SHA-256 `588567a9e9f282bb91f7e84a8d3107a08ee81641e7e0379bfec413676460616a` value “BE Hydraulics 02”.
- Packet string ref `0x00623174` length 9 SHA-256 `a352476989a70e31c503605a0e69f4ce4a5c70f144df96407ad8a1a854ea69ef` value “BE On 02”.
- Packet string ref `0x00623180` length 10 SHA-256 `cf1b2be9588601d242455e6fc5f8eb805542d207e55c9228c2c202c8f94ef2e7` value “BE Target”.
- Packet string ref `0x0062318c` length 20 SHA-256 `b7898e6e7e4a48a909e6a8934120ebc5f68172154e226be06bd3adbe87c4341d` value “BE Incoming Missile”.
- Packet string ref `0x006231a0` length 17 SHA-256 `b4b8c04fac82d08db4d894bea6b199319724491c0f30aad0b78d0771325eb8b1` value “BE Target Locked”.
- Packet string ref `0x006231b4` length 14 SHA-256 `03322d49bd1a37e304a4ae010f1910e0a7a045544d7faf90a51d697e2a6acb27` value “BE Strafe L/R”.
- Packet string ref `0x006231c4` length 14 SHA-256 `2610d9d54175dc6534c7ee09cb9e392567a15e1d5cca3a0e98265c8e764c402e` value “BE Energy Low”.
- Packet string ref `0x006231d4` length 19 SHA-256 `2986d1d54af95f40912ba51204e8b38f024f40a0528b22acbb98207f684cd5f6` value “BE Energy Critical”.
- Packet string ref `0x006231e8` length 20 SHA-256 `2d390134a984a1364d5a31d30afd56944e99909e7f5d1eee7e248a1725e91541` value “BE Engines(takeoff)”.
- Packet string ref `0x006231fc` length 17 SHA-256 `33097444094236a2210fc144e079904bfd9a660969d1d5df438a46f82578e122` value “BE Engines(land)”.
- Packet string ref `0x00623210` length 22 SHA-256 `0500b4c88ba852747cd40a2b8e116ea2b2afd12e589fb2b467875031fcd69ce9` value “BE Engines(in-flight)”.
- Source crosswalk: `references/Onslaught/BattleEngine.cpp` `CBattleEngine::Init` line 63 (`SOURCE_EXACT`), evidence `reverse-engineering/binary-analysis/functions/BattleEngine.cpp/CBattleEngine__Init.md`. This is source/name architecture evidence at the stated class, not independent retail behavior proof.

## Confidence
1 — exact identity, contiguous pristine bytes, digest derivations, signature text, and structured edge inventory are reconciled; field-level semantics and runtime causality remain bounded to the packet/decompile and any cited source/TTD rows. A packet/canonical name discrepancy forces confidence 0. Proposed promotion: false.

## Unresolved questions
- Instruction-level read/write direction and concrete layout for every referenced field/global.
- Complete indirect-call target set and failure/nullability behavior.
- Runtime ordering, side effects, return-domain meaning, and caller expectations beyond the bounded packet evidence.
- Cheapest falsifier: cold-disassemble this exact raw-body digest, compare every branch/load/store/call against the packet decompile and structured arrays, then run a controlled copied-runtime probe for the named input/state transition.
