# CBattleEngineWalkerPart__ctor

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static contract for `CBattleEngineWalkerPart__ctor` at `0x00412bc0`; packet-described behavior is retained with explicit unknowns and no promotion claim.
Evidence: MEASURED — READY packet/decompile, structured edges, closure identity, and independently recomputed pristine body bytes; runtime and source limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: references/Onslaught/BattleEngineWalkerPart.cpp | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x00412bc0`

## Identity
- Body `[0x00412bc0,0x00412cec]`, 301 bytes, 87 closure instructions. Raw pristine-body SHA-256 `9bc6dd206e4cca155b0f523f03a552928e3f51816eede3cc18e1516ec2702ccd`; closure range SHA-256 `61eec54c5b24acf070dd2094393c5f8022738c1d3e78898f270c4402328ef4d1`; packet range-plus-bytes SHA-256 `877ae22680cd8a0eab395cb9ffbb71f8bc589db0920b1c99676561a74204f51d`. All three were independently recomputed over the exact single contiguous inclusive range.
- Canonical name `CBattleEngineWalkerPart__ctor` comes from the current closure/register row. Packet label matches canonical tracked name `CBattleEngineWalkerPart__ctor`.
- Packet name source `USER_DEFINED` and signature source `USER_DEFINED` are counted provenance, not semantic proof.
- Campaign grade `C1_CANDIDATE_PARTIAL` / closure class `SEALED_STATIC_RECEIPT` / packet confidence `HIGH_STATIC`. Proposed promotion: false.

## Calling convention
Packet records `__thiscall` for `void * __thiscall CBattleEngineWalkerPart__ctor(void * this, void * mainPart)`. Register/stack placement beyond that packet declaration is not_determinable without a separate instruction-level ABI review.

## Prototype and parameter semantics
```c
void * __thiscall CBattleEngineWalkerPart__ctor(void * this, void * mainPart)
```
- Packet-declared parameter list: `void * this, void * mainPart`. Parameter labels are analyst/source intent; concrete object layouts, units, ownership, aliasing, and nullability remain not_determinable unless directly stated by the quoted packet comment below.

## Return value meaning
The packet signature declares `void *`. Exact domain meaning of the returned bits/value is not_determinable from identity and decompile evidence alone; no stronger meaning is invented here.

## Globals read/written
- Decompile symbol references: `DAT_006236ac`, `DAT_006236b0`, `DAT_006236b4`, `DAT_006236b8`, `DAT_006236bc`, `DAT_006236c0`, `DAT_00663498`, `s_Ag_dash_velocity_006236c3`, `s__default_0_2__Dash_move_kicks_of_006237e0`, `s__default_0_8__When_the_dash_sepe_00623850`, `s__default_0_9__When_the_dash_sepe_006238b8`, `s__default_15__Number_of_game_turn_00623784`, `s__default_25_0__Initial_velocity_g_006236d4`, `s__default_5__Number_of_game_turns_0062371c`, `s_g_dash_end_00623844`, `s_g_dash_friction_0062370c`, `s_g_dash_length_00623774`, `s_g_dash_start_006238a8`, `s_g_dash_time_006237d4`. Read/write direction for each symbol is not independently instruction-verified in this factory draft.

## Callees relied on / callers
- Callee `CBattleEngineWalkerPart__ResetConfiguration` `0x004146b0` ×1 site(s) (STATIC_DIRECT).
- Callee `CConsole__RegisterVariable` `0x0042b040` ×6 site(s) (STATIC_DIRECT).
- Callee `CSPtrSet__Init` `0x004e5840` ×1 site(s) (STATIC_DIRECT).
- Caller `CBattleEngine__Init` `0x00404dd0` ×1 site(s) (instruction-flow).
- Structured packet arrays prove the listed direct/static edge identities and site counts only. Indirect vtable targets, library inlining, and data-driven dispatch remain unresolved unless separately named in the packet.

## Behavior summary
- Existing packet analyst comment (quoted as bounded packet evidence, not silently upgraded): “Owner/signature correction: CBattleEngineWalkerPart constructor stores mainPart, initializes weapon/dash fields, calls CBattleEngineWalkerPart__ResetConfiguration, and registers g_dash_* console variables. Static source/caller evidence only; concrete layout, runtime dash behavior, and rebuild parity remain unproven.”
- The displayed decompile is non-empty and SHA-256 `b899e4be350517d0eda451110f34956c5ba40ae6d1f96241225c4bf1f9ce03ef`. This factory draft preserves that packet-described control/side-effect intent but does not infer unstated field meanings, units, ordering guarantees, or runtime causality.
- Structured inventory for this body: 1 caller record(s), 3 callee record(s), and 11 string-ref record(s).

## Error / edge behavior
Nullability, invalid-state behavior, allocation failure, indirect-call failure, NaN/overflow behavior, and rollback semantics are not_determinable as a class from the packet metadata. The decompile and quoted comment are the bounded static evidence; any missing branch-level edge contract remains an open question rather than an invented default.

## Runtime corroboration (TTD, bounded)
No TTD execution row exists for this VA in the bounded `ttd-deep-mine/values.tsv` corpus. This absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Writer-task authority: task `t_efc238f0`, corrected cohort-5 immutable manifest SHA-256 `a501cc526ae9f6caed0e4e42581ac21cabd87aa03a3eb4266432bdb7fd1ed7a8`, row 12; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750` and proposed promotion false. Review card `t_b435bd68` preserves the superseded manifest and exact RED/correction receipt; no writer-local scratch path is claimed as tracked evidence.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x00412bc0.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`); packet decompile SHA-256 `b899e4be350517d0eda451110f34956c5ba40ae6d1f96241225c4bf1f9ce03ef`.
- Digest derivation: closure SHA-256 hashes canonical range text `00412bc0:00412cec;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
- Closure execution state `COVERED` and confidence `HIGH_STATIC`; these are inherited bounded grades, not this factory's promotion decision.
- Packet string ref `0x006236d4` length 56 SHA-256 `525daa27643032b18a9a4335dab9ec2ef82d64c0c567762a6edd553a71f1fb90` value `(default 25.0) Initial velocity given at start of boost`.
- Packet string ref `0x0062370c` length 16 SHA-256 `a50f8633a42fc0e2b511532e8194165e89d0689b658321d3a615b3341e688249` value `g_dash_friction`.
- Packet string ref `0x0062371c` length 88 SHA-256 `5d935fd023e66fae69a3caa6c855f43716fbf5a62031802889af279b87e78f2d` value `(default 5) Number of game turns left on length when friction kicks in (i.e. stops you)`.
- Packet string ref `0x00623774` length 14 SHA-256 `e92d59445de7a55343cc4bcd6c718bc732d77de4c843122e0906ec678fabe7d3` value `g_dash_length`.
- Packet string ref `0x00623784` length 80 SHA-256 `16bd5a3de81a62a98da0d86fc9246489cd8d116e9f8fe508d921877ec44b8d92` value `(default 15) Number of game turns until user has control of Battle engine again`.
- Packet string ref `0x006237d4` length 12 SHA-256 `3ead782fd045620b29d7943037b8edb9b5473ae6181f4934ce05d56c10e12e8a` value `g_dash_time`.
- Packet string ref `0x006237e0` length 97 SHA-256 `e8b50669bb1f4b8a7ce426590c01ec5fd36ffa3650089bffaab42864762e8582` value `(default 0.2) Dash move kicks off if start move is done and then end move in less than this time`.
- Packet string ref `0x00623844` length 11 SHA-256 `d12c415c4ee64e13b97da3dfb92bb27fb1effca18e6620ee97b83522ae28c3fd` value `g_dash_end`.
- Packet string ref `0x00623850` length 86 SHA-256 `d3ff48a5564ef5f41343e82327e11b8632e7dfe875ab7018be35100d8fda45ef` value `(default 0.8) When the dash sepecial move ends when joy is over this value (0.0..1.0)`.
- Packet string ref `0x006238a8` length 13 SHA-256 `b0f43c46df0160ed6f6d7a08787835486995456687ba5bb0b8ffb4aa86616d1f` value `g_dash_start`.
- Packet string ref `0x006238b8` length 88 SHA-256 `baa3d09d01ee0f04e2d6d09e9858b4f38008c35e1140daaeef428e2915fa943d` value `(default 0.9) When the dash sepecial move starts when joy is over this value (0.0..1.0)`.
- Source crosswalk: `references/Onslaught/BattleEngineWalkerPart.cpp` `CBattleEngineWalkerPart::CBattleEngineWalkerPart` line 61 (`SOURCE_ANALOG`), evidence not supplied in this crosswalk row. This is source/name architecture evidence at the stated class, not independent retail behavior proof.

## Confidence
1 — exact identity, contiguous pristine bytes, digest derivations, signature text, and structured edge inventory are reconciled; field-level semantics and runtime causality remain bounded to the packet/decompile and any cited source/TTD rows. A packet/canonical name discrepancy forces confidence 0. Proposed promotion: false.

## Unresolved questions
- Instruction-level read/write direction and concrete layout for every referenced field/global.
- Complete indirect-call target set and failure/nullability behavior.
- Runtime ordering, side effects, return-domain meaning, and caller expectations beyond the bounded packet evidence.
- Cheapest falsifier: cold-disassemble this exact raw-body digest, compare every branch/load/store/call against the packet decompile and structured arrays, then run a controlled copied-runtime probe for the named input/state transition.
