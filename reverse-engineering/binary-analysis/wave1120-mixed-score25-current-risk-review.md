# Wave1120 Mixed Score-25 Current-Risk Review

Status: validated static read-only evidence
Date: 2026-06-05
Tag: `wave1120-mixed-score25-current-risk-review`

Wave1120 accounts for `8 rows` from the Wave1108 current focused denominator as the score-25 mixed current-risk head, moving current focused accounting to `118/1179 = 10.01%` of current focused candidates: 1179. The wave used a fresh read-only Ghidra export and no mutation. Static closure debt remains `0 / 0 / 0` for commentless / exact-undefined / `param_N`.

Reviewed anchors:

| Address | Static read-back evidence |
| --- | --- |
| `0x00405d80 CParticleManager__RemoveFromGlobalList_Thunk` | Jump thunk to `0x004cb050 CParticleManager__RemoveFromGlobalList`, reached by many unwind cleanup callbacks plus CWeapon/OID/CFEPDebriefing DATA contexts; the older saved tag row is empty but metadata/decompile remain coherent. |
| `0x0040dfb0 CGeneralVolume__SpawnPickupAndDispatch` | `CUnit__ProcessStateSwapAndDeathChecks`, `CBattleEngine__StartDieProcess`, and raw caller `0x0040738b` reach a pickup spawn/dispatch helper that resolves a pickup name from `this+0x4b0/+0x68`, calls `CWorldPhysicsManager__CreatePickup`, initializes launch/influence stack state, copies position fields, and dispatches the created pickup vfunc when available. |
| `0x004bfe00 CUnit__dtor_base_Thunk_004bfe00` | Existing Wave460/Wave1097 cleanup thunk remains a direct jump to `0x004f84e0 CUnit__dtor_base`, with callers from unwind cleanup and `CUnit__scalar_deleting_dtor`. |
| `0x004d3630 CPod__VFunc_66_UpdateMotionAndAccumulateScalar` | DATA xref `0x005e0094` keeps the CPod vtable slot-66 assignment; the body calls `CUnit__UpdateMotionAttachmentsAndEffects`, dispatches vfunc `+0xb4`, and accumulates the returned float into `this+0x84`. |
| `0x004ef100 CUnit__VFunc64_SpawnConfiguredPickupThreeTimes` | DATA xref `0x005e1610` keeps the CUnit-family slot-64 assignment; the body loops three calls to `CUnit__SpawnConfiguredPickupIfAboveWater`. |
| `0x0052d3d0 CAsmInstruction__SpawnFromOpcode` | `CScriptObjectCode__CScriptObjectCode` caller reaches the bytecode opcode factory; it switches opcode values into `0x0c`-byte instruction allocations and reports the fatal unknown-instruction string for unsupported opcodes. |
| `0x0052ec60 CDataType__CreateFromType` | `CScriptObjectCode__ReadSymbolTable` caller reaches the datatype factory; it switches serialized type ids `1..6` into int, float, string, observed bool-result, thing-pointer, and position datatype vtable regions. |
| `0x00599d80 CFastVB__FlattenNodeTreeLeafByLinearIndex` | `CFastVB__ScoreNodeTreePairMismatchBits` and `CFastVB__AreNodeTreesCompatible` callers reach the node-tree leaf flattening helper; it walks wrapper kinds `1`, `5`, `7`, and `10`, descends to leaf kind `8`, writes normalized leaf scratch fields, and returns `0` or `0x80004005`. |

Fresh export evidence:

- Metadata: `8` rows, `targets=8 found=8 missing=0`.
- Tags: `8` rows, `missing=0`; `0x00405d80` and `0x0040dfb0` are older rows with empty saved tag strings, documented rather than normalized in this read-only wave.
- Xrefs: `59` rows.
- Instructions: `936` rows, `targets=8 missing=0`.
- Decompile: `8` rows, `targets=8 dumped=8 missing=0 failed=0`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260605-025952_post_wave1120_mixed_score25_current_risk_review_verified`, `19` files, `175541127` bytes, `DiffCount=0`.
- Previous latest completed Ghidra review backup: `[maintainer-local-ghidra-backup-root]\BEA_20260605-022812_post_wave1119_mixed_score26_current_risk_review_verified`.

Boundary:

This is static read-only Ghidra/source-reference evidence. It does not prove runtime particle/list behavior, runtime pickup/drop behavior, runtime unit cleanup/pickup behavior, runtime pod motion behavior, runtime MissionScript behavior, runtime FastVB parser/render behavior, exact concrete layouts, exact source-body identity, BEA patching behavior, gameplay outcomes, visual QA, or rebuild parity.
