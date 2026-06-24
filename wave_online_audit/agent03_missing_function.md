# Missing Function Mismatches (Canonical Only)

Source: `reverse-engineering/binary-analysis/semantic-audit-online-pass-2026-02-12.json` (missing_function only, canonical paths).

| File:Line | Address | Expected Name | Classification | Recommendation | Notes |
|---|---|---|---|---|---|
| `reverse-engineering/binary-analysis/README.md:64` | 0x004f7a80 | CScriptObjectCode__Run | Function entrypoint | Schedule manual function creation (F key) | Summary table expects real function. |
| `reverse-engineering/binary-analysis/functions/DataType.cpp.md:36` | 0x005e4af8 | CDataType__ScalarDeletingDestructor | Vtable/data label | Change doc | Vtable address for CIntDataType, not a function entrypoint. |
| `reverse-engineering/binary-analysis/functions/DataType.cpp.md:37` | 0x005e4ea4 | CDataType__ScalarDeletingDestructor | Vtable/data label | Change doc | Vtable address for CBool/CFloat data type. |
| `reverse-engineering/binary-analysis/functions/DataType.cpp.md:38` | 0x005e4e4c | CStringDataType__ScalarDeletingDestructor | Vtable/data label | Change doc | Vtable address for CStringDataType. |
| `reverse-engineering/binary-analysis/functions/DataType.cpp.md:39` | 0x005e4d50 | CDataType__ScalarDeletingDestructor | Vtable/data label | Change doc | Vtable address for CFloatDataType. |
| `reverse-engineering/binary-analysis/functions/DataType.cpp.md:40` | 0x005e4df8 | CThingPtrDataType__ScalarDeletingDestructor | Vtable/data label | Change doc | Vtable address for CThingPtrDataType. |
| `reverse-engineering/binary-analysis/functions/DataType.cpp.md:41` | 0x005e4da4 | CDataType__ScalarDeletingDestructor | Vtable/data label | Change doc | Vtable address for CPositionDataType. |
| `reverse-engineering/binary-analysis/functions/FEPGoodies.cpp/_index.md:16` | 0x0045d7e0 | CFEPGoodies__Process | Function entrypoint | Schedule manual function creation (F key) | Listed as main process loop. |
| `reverse-engineering/binary-analysis/functions/Cutscene.cpp/_index.md:17` | 0x0043f510 | CCutscene__InitAnimations | Function entrypoint | Schedule manual function creation (F key) | Doc already notes missing function in Ghidra. |
| `reverse-engineering/binary-analysis/functions/BSpline.cpp/_index.md:110` | 0x004d2f19 | CPlayer__GotoPanView | Function entrypoint | Schedule manual function creation (F key) | Listed as caller function. |
| `reverse-engineering/binary-analysis/functions/BSpline.cpp/_index.md:111` | 0x00533e20 | IScript__Create3PointPanCamera | Function entrypoint | Schedule manual function creation (F key) | Listed as caller function. |
| `reverse-engineering/binary-analysis/functions/BSpline.cpp/_index.md:112` | 0x0053421e | IScript__Create4PointPanCamera | Function entrypoint | Schedule manual function creation (F key) | Listed as caller function. |
| `reverse-engineering/binary-analysis/functions/CollisionSeekingRound.cpp/_index.md:78` | 0x004261be | CCollisionSeekingRound__Init | Callsite/inline | Change doc | Address is an allocation callsite, not a function start. |
| `reverse-engineering/binary-analysis/functions/CollisionSeekingRound.cpp/_index.md:79` | 0x0042627a | CCollisionSeekingRound__Init | Callsite/inline | Change doc | Address is an allocation callsite, not a function start. |
| `reverse-engineering/binary-analysis/functions/CollisionSeekingRound.cpp/_index.md:80` | 0x00426ad3 | CCollisionSeekingRound__CreateEffect | Callsite/inline | Change doc | Address is an allocation callsite, not a function start. |
| `reverse-engineering/binary-analysis/functions/EventFunction.cpp.md:47` | 0x005e4ef8 | CEventFunction__vtable | Vtable/data label | Change doc | Vtable address, not a function entrypoint. |
| `reverse-engineering/binary-analysis/functions/EventFunction.cpp.md:195` | 0x005e4d50 | CEventFunctionParam__vtable | Vtable/data label | Change doc | Vtable address, not a function entrypoint. |
| `reverse-engineering/binary-analysis/functions/EventFunction.cpp.md:43` | 0x005d92d4 | CRelaxedSquad__vtable | Vtable/data label | Change doc | Base class vtable address. |
| `reverse-engineering/binary-analysis/functions/EventFunction.cpp.md:347` | 0x00538fe4 | FUN_00538ec0 | Callsite/inline | Change doc | Address is callsite; function entrypoint is 0x00538ec0. |
| `reverse-engineering/binary-analysis/functions/EventFunction.cpp.md:348` | 0x0053913f | FUN_00539040 | Callsite/inline | Change doc | Address is callsite; function entrypoint is 0x00539040. |
| `reverse-engineering/binary-analysis/functions/EventFunction.cpp.md:349` | 0x00538c3b | FUN_00538b70 | Callsite/inline | Change doc | Address is callsite; function entrypoint is 0x00538b70. |
| `reverse-engineering/binary-analysis/functions/EventFunction.cpp.md:350` | 0x00538d68 | FUN_00538c70 | Callsite/inline | Change doc | Address is callsite; function entrypoint is 0x00538c70. |
| `reverse-engineering/binary-analysis/functions/Bomber.cpp/_index.md:14` | 0x004160e4 | CBomber__Constructor_1 | Inline block | Add "no function object" note | Doc already calls this inline; ensure audit treats as non-function. |
| `reverse-engineering/binary-analysis/functions/Bomber.cpp/_index.md:15` | 0x0041611d | CBomber__Constructor_2 | Inline block | Add "no function object" note | Doc already calls this inline; ensure audit treats as non-function. |
| `reverse-engineering/binary-analysis/functions/DXTrees.cpp.md:320` | 0x0046cfe2 | CGame__LoadLevel | Function entrypoint | Schedule manual function creation (F key) | Listed as caller function. |
| `reverse-engineering/binary-analysis/functions/DXTrees.cpp.md:321` | 0x0055aa2e | CDXTrees__Render | Function entrypoint | Schedule manual function creation (F key) | Listed as caller function. |
| `reverse-engineering/binary-analysis/functions/Cannon.cpp/_index.md:14` | 0x0041b1a0 | CCannon__Init | Function entrypoint | Schedule manual function creation (F key) | Doc already notes missing function in Ghidra. |
| `reverse-engineering/binary-analysis/functions/DXPatchManager.cpp.md:191` | 0x0055044d | CDXPatchManager__Init | Callsite/inline | Change doc | Address is an allocation callsite, not a function start. |
| `reverse-engineering/binary-analysis/functions/DXPatchManager.cpp.md:192` | 0x00550479 | CDXPatchManager__Init | Callsite/inline | Change doc | Address is an allocation callsite, not a function start. |
| `reverse-engineering/binary-analysis/functions/DXPatchManager.cpp.md:193` | 0x005504f4 | CDXPatchManager__Init | Callsite/inline | Change doc | Address is an allocation callsite, not a function start. |
| `reverse-engineering/binary-analysis/functions/DXPatchManager.cpp.md:194` | 0x0055057d | CDXPatchManager__Init | Callsite/inline | Change doc | Address is an allocation callsite, not a function start. |
| `reverse-engineering/binary-analysis/functions/DXPatchManager.cpp.md:195` | 0x005505f1 | CDXPatchManager__Init | Callsite/inline | Change doc | Address is an allocation callsite, not a function start. |
| `reverse-engineering/binary-analysis/functions/DXPatchManager.cpp.md:196` | 0x005507b5 | CDXPatch__LoadFromFile | Callsite/inline | Change doc | Address is an allocation callsite, not a function start. |
| `reverse-engineering/binary-analysis/functions/FrontEnd.cpp/CFrontEnd__Init.md:142` | 0x0041bcd0 | CCareer__UpdateOnWorldComplete | Function entrypoint | Schedule manual function creation (F key) | Listed as called function. |
| `reverse-engineering/binary-analysis/functions/FrontEnd.cpp/CFrontEnd__Init.md:163` | 0x004684ef | CFrontEnd__Run | Function entrypoint | Schedule manual function creation (F key) | Listed as caller function. |
| `reverse-engineering/binary-analysis/functions/GroundAttackAircraft.cpp/_index.md:14` | 0x0047bbe4 | CGroundAttackAircraft__Constructor | Function entrypoint | Schedule manual function creation (F key) | Doc already notes manual creation needed. |
| `reverse-engineering/binary-analysis/functions/gcgamut.cpp.md:186` | 0x004741b5 | CGamut__Init | Callsite/inline | Change doc | Address is an allocation callsite, not a function start. |
| `reverse-engineering/binary-analysis/functions/gcgamut.cpp.md:187` | 0x004741db | CGamut__Init | Callsite/inline | Change doc | Address is an allocation callsite, not a function start. |
| `reverse-engineering/binary-analysis/functions/FEPMain.cpp.md:19` | 0x00464520 | CFEPMain__Init | Function entrypoint | Schedule manual function creation (F key) | Vtable entry points here. |
| `reverse-engineering/binary-analysis/functions/FEPMain.cpp.md:21` | 0x004621e0 | CFEPMain__GetActionCount | Function entrypoint | Schedule manual function creation (F key) | Small method, undefined region. |
| `reverse-engineering/binary-analysis/functions/FEPMain.cpp.md:22` | 0x004621d0 | CFEPMain__GetMenuType | Function entrypoint | Schedule manual function creation (F key) | Small method, undefined region. |
| `reverse-engineering/binary-analysis/functions/FEPMain.cpp.md:24` | 0x00462c90 | CFEPMain__Update | Vtable entry/thunk | Change doc | Mark as vtable entry into update region; not a distinct function until confirmed. |
| `reverse-engineering/binary-analysis/functions/FEPMain.cpp.md:26` | 0x00466140 | CFEPMain__Cleanup | Function entrypoint | Schedule manual function creation (F key) | Vtable entry points here. |
| `reverse-engineering/binary-analysis/functions/FEPMain.cpp.md:35` | 0x00462638 | CFEPMain__Update | Function entrypoint | Schedule manual function creation (F key) | Large update/render loop. |
| `reverse-engineering/binary-analysis/functions/InitThing.cpp/_index.md:120` | 0x0050bc92 | CWorld__LoadWorld | Callsite/inline | Change doc | Callsite within CWorld__LoadWorld. |
| `reverse-engineering/binary-analysis/functions/InitThing.cpp/_index.md:121` | 0x0050bdd8 | CWorld__LoadWorld | Callsite/inline | Change doc | Callsite within CWorld__LoadWorld. |
| `reverse-engineering/binary-analysis/functions/InitThing.cpp/_index.md:122` | 0x0050bfc8 | CWorld__LoadWorld | Callsite/inline | Change doc | Callsite within CWorld__LoadWorld. |
| `reverse-engineering/binary-analysis/functions/InitThing.cpp/_index.md:123` | 0x0050c1dd | CWorld__LoadWorld | Callsite/inline | Change doc | Callsite within CWorld__LoadWorld. |
| `reverse-engineering/binary-analysis/functions/InitThing.cpp/_index.md:124` | 0x0050c29e | CWorld__LoadWorld | Callsite/inline | Change doc | Callsite within CWorld__LoadWorld. |
| `reverse-engineering/binary-analysis/functions/InitThing.cpp/_index.md:125` | 0x0050c9ab | CWorld__LoadWorld | Callsite/inline | Change doc | Callsite within CWorld__LoadWorld. |
| `reverse-engineering/binary-analysis/functions/InitThing.cpp/_index.md:126` | 0x0050caac | CWorld__LoadWorld | Callsite/inline | Change doc | Callsite within CWorld__LoadWorld. |
| `reverse-engineering/binary-analysis/functions/InitThing.cpp/_index.md:127` | 0x0050dd75 | FUN_0050dcb0 | Callsite/inline | Change doc | Callsite in unknown function. |
| `reverse-engineering/binary-analysis/functions/ibuffer.cpp/_index.md:32` | 0x00488460 | CIBuffer__CreateDynamic | Function entrypoint | Schedule manual function creation (F key) | Vtable entry currently not defined in Ghidra. |
| `reverse-engineering/binary-analysis/functions/ibuffer.cpp/_index.md:33` | 0x004884f0 | CIBuffer__CreateStatic | Function entrypoint | Schedule manual function creation (F key) | Vtable entry currently not defined in Ghidra. |
| `reverse-engineering/binary-analysis/functions/tgaloader.cpp/_index.md:126` | 0x00440cb8 | CDamage__LoadDamageTexture | Function entrypoint | Schedule manual function creation (F key) | Listed as caller function. |
| `reverse-engineering/binary-analysis/functions/tgaloader.cpp/_index.md:127` | 0x00491203 | FUN_004911c0 | Function entrypoint | Schedule manual function creation (F key) | Listed as caller function. |
| `reverse-engineering/binary-analysis/functions/HeightField.cpp/CHeightField__Load.md:79` | 0x004910d6 | FUN_00491060 | Function entrypoint | Schedule manual function creation (F key) | Listed as caller function. |
| `reverse-engineering/binary-analysis/functions/HeightField.cpp/CHeightField__InitColorGradient.md:88` | 0x0047f7ea | CHeightField__Load | Function entrypoint | Schedule manual function creation (F key) | Listed as caller function. |
| `reverse-engineering/binary-analysis/functions/Sentinel.cpp.md:24` | 0x004dea50 | CSentinel::Constructor | Function entrypoint | Schedule manual function creation (F key) | Doc already notes needs manual creation. |
| `reverse-engineering/binary-analysis/functions/ScriptEventNB.cpp.md:16` | 0x005e4f34 | CScriptEventNB__vtable_base | Vtable/data label | Change doc | Vtable address, not a function entrypoint. |
| `reverse-engineering/binary-analysis/functions/ScriptEventNB.cpp.md:54` | 0x005e4f44 | CScriptEventNB__vtable | Vtable/data label | Change doc | Vtable address, not a function entrypoint. |
| `reverse-engineering/binary-analysis/functions/ScriptEventNB.cpp.md:475` | 0x005e4f54 | CScriptEventNB__vtable_derived | Vtable/data label | Change doc | Vtable address, not a function entrypoint. |
