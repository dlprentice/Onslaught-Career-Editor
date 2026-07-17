# CPhysicsScriptStatements.cpp function map

Status: active static function map

This page retains the address, signature, serialization, registry, apply, and
destructor relationships that support the PhysicsScript parser/schema and
rebuild interface. Current metadata corrections are owned by the
[reviewed correction plan](../ghidra-reviewed-correction-plan-2026-07-13.json).

The debug-path anchor points to a maintainer-local `CPhysicsScriptStatements.cpp`
export. It is provenance context, not copied source and not proof of exact retail
source-body identity.

## Top-Level Statement Bodies

| Address | Saved signature | Current evidence |
| --- | --- | --- |
| `0x0042ede0` | `void __fastcall CUnitStatement__CreateUnitAndRecurse(void * this)` | Recovered missing statement-update boundary. It creates/registers UnitAI by statement name, resolves the created UnitAI from `DAT_008553fc`, and recurses into child statements. |
| `0x0042f230` | `int __fastcall CUnitStatement__GetSerializedSize(void * this)` | Recovered top-level unit-statement serialized-size body; counts the statement name and first value-list payload before recursive value-list sizing. |
| `0x0042f2b0` | `void __thiscall CUnitStatement__LoadFromMemBuffer(void * this, void * memBuffer)` | Recovered top-level unit-statement load body; reads the name, creates the first value-list node, dispatches type-2 child load helpers, or skips unknown payload bytes. |
| `0x0042f5b0` | `void __fastcall CWeaponStatement__CreateWeaponAndRecurse(void * this)` | Corrected from stale vfunc label to top-level weapon create-and-recurse update body. |
| `0x0042f5f0` | `void __cdecl CWeaponStatement__Create(char * name)` | Creates a `0x4c` weapon-like record by name, initializes defaults, and appends it to `DAT_008553e8`. |
| `0x0042f700` | `int __fastcall CWeaponStatement__GetSerializedSize(void * this)` | Recovered top-level weapon-statement serialized-size body; the previous top-level name at `0x0042f750` was a value-list helper. |
| `0x0042f780` | `void __thiscall CWeaponStatement__LoadFromMemBuffer(void * this, void * memBuffer)` | Recovered top-level weapon-statement load body; dispatches type-3 child load helpers or skips unknown payload bytes. |
| `0x0042fa40` | `void __fastcall CWeaponModeStatement__CreateWeaponModeAndRecurse(void * this)` | Corrected from stale vfunc label to top-level weapon-mode create-and-recurse update body. |
| `0x0042fa80` | `void __cdecl CWeaponModeStatement__Create(char * name)` | Creates a `0xc0` weapon-mode-like record by name and appends it to `DAT_008553ec`. |
| `0x0042fc20` | `int __fastcall CWeaponModeStatement__GetSerializedSize(void * this)` | Recovered top-level weapon-mode-statement serialized-size body. |
| `0x0042fca0` | `void __thiscall CWeaponModeStatement__LoadFromMemBuffer(void * this, void * memBuffer)` | Recovered top-level weapon-mode-statement load body; dispatches type-4 child load helpers or skips unknown payload bytes. |
| `0x0042ff60` | `void __fastcall CRoundStatement__CreateRoundAndRecurse(void * this)` | Corrected from stale vfunc label to top-level round create-and-recurse update body. |
| `0x0042ffa0` | `void __cdecl CRoundStatement__Create(char * name)` | Creates a `0xa8` round-like record, handles `Stream_Laser` / `Gill_M_Breath` special-case flags, and appends it to `DAT_008553f0`. |
| `0x00430190` | `int __fastcall CRoundStatement__GetSerializedSize(void * this)` | Recovered top-level round-statement serialized-size body. |
| `0x00430210` | `void __thiscall CRoundStatement__LoadFromMemBuffer(void * this, void * memBuffer)` | Recovered top-level round-statement load body; dispatches type-5 child load helpers or skips unknown payload bytes. Wave991 re-exported this row as part of the `0x00426150 CCollisionSeekingRound__Init` round config bridge context. |
| `0x004304d0` | `void __fastcall CSpawnerStatement__CreateSpawnerAndRecurse(void * this)` | Corrected from stale vfunc label to top-level spawner create-and-recurse update body. |
| `0x00430510` | `void __cdecl CSpawnerData__CreateAndRegisterByName(char * name)` | Creates a `0x3c` spawner-data-like record by name, initializes default spawner fields, and appends it to `DAT_008553f4`. |
| `0x00430660` | `int __fastcall CSpawnerStatement__GetSerializedSize(void * this)` | Recovered top-level spawner-statement serialized-size body. |
| `0x004306e0` | `void __thiscall CSpawnerStatement__LoadFromMemBuffer(void * this, void * memBuffer)` | Recovered top-level spawner-statement load body; dispatches type-6 child load helpers or skips unknown payload bytes. |
| `0x004309a0` | `void __fastcall CExplosionStatement__CreateExplosionAndRecurse(void * this)` | Corrected from stale vfunc label to top-level explosion create-and-recurse update body. |
| `0x004309e0` | `void __cdecl CExplosionStatement__Create(char * name)` | Creates a `0x50` explosion-like record by name and appends it to `DAT_008553f8`. |
| `0x00430ae0` | `int __fastcall CExplosionStatement__GetSerializedSize(void * this)` | Recovered top-level explosion-statement serialized-size body. |
| `0x00430b60` | `void __thiscall CExplosionStatement__LoadFromMemBuffer(void * this, void * memBuffer)` | Recovered top-level explosion-statement load body; dispatches type-7 child load helpers or skips unknown payload bytes. |
| `0x00430e20` | `void __fastcall CComponentStatement__CreateComponentAndRecurse(void * this)` | Corrected from stale vfunc label to top-level component create-and-recurse update body. |
| `0x00430e60` | `void __cdecl CComponentStatement__CreateAndRegisterByName(char * name)` | Creates a `0x1ac` component-like record by name and appends it to `DAT_00855400`. |
| `0x00430fa0` | `void __thiscall CStatementChain__InvokeVFunc04OnNodes(void * this, void * context)` | Adjacent chained-statement dispatcher that walks linked statement nodes and invokes vtable slot `+0x4`. |
| `0x00430fd0` | `int __fastcall CComponentStatement__GetSerializedSize(void * this)` | Recovered top-level component-statement serialized-size body. |
| `0x00431050` | `void __thiscall CComponentStatement__LoadFromMemBuffer(void * this, void * memBuffer)` | Recovered top-level component-statement load body; dispatches type-10 child load helpers or skips unknown payload bytes. |
| `0x00431310` | `void __fastcall CFeatureStatement__CreateFeatureAndRecurse(void * this)` | Corrected from stale vfunc label to top-level feature create-and-recurse update body. |
| `0x00431350` | `void __cdecl CFeatureStatement__CreateAndRegisterByName(char * name)` | Creates a `0x24` feature-like record by name and appends it to `DAT_00855404`. |
| `0x00431420` | `int __fastcall CFeatureStatement__GetSerializedSize(void * this)` | Recovered top-level feature-statement serialized-size body. |
| `0x004314a0` | `void __thiscall CFeatureStatement__LoadFromMemBuffer(void * this, void * memBuffer)` | Recovered top-level feature-statement load body; dispatches type-8 child load helpers or skips unknown payload bytes. |
| `0x00431760` | `void __fastcall CHazardStatement__CreateHazardAndRecurse(void * this)` | Corrected from stale vfunc label to top-level hazard create-and-recurse update body. |
| `0x004317a0` | `void __cdecl CHazardStatement__CreateAndRegisterByName(char * name)` | Creates a `0x1c` hazard-like record by name and appends it to `DAT_00855408`. |
| `0x00431870` | `int __fastcall CHazardStatement__GetSerializedSize(void * this)` | Recovered top-level hazard-statement serialized-size body. |
| `0x004318f0` | `void __thiscall CHazardStatement__LoadFromMemBuffer(void * this, void * memBuffer)` | Recovered top-level hazard-statement load body; dispatches type-9 child load helpers or skips unknown payload bytes. |
| `0x00431bb0` | `void * __cdecl CPhysicsScriptStatements__CreateStatementType2(int valueType)` | Type-2/unit value factory over value type ids through `0x46`; exact value classes/layouts remain unproven. |
| `0x00434300` | `void * __cdecl CPhysicsScriptStatements__CreateStatementType3(int valueType)` | Type-3/weapon value factory over observed value ids `0x74` through `0x81`; exact value classes/layouts remain unproven. |
| `0x00435010` | `void * __cdecl CPhysicsScriptStatements__CreateStatementType4(int valueType)` | Type-4/weapon-mode value factory over observed value ids `0x1` through `0x26`; exact value classes/layouts remain unproven. |
| `0x00437490` | `void * __cdecl CPhysicsScriptStatements__CreateStatementType5(int valueType)` | Type-5/round value factory over observed value ids `0x1` through `0x26`; exact value classes/layouts remain unproven. |
| `0x00439b40` | `void * __cdecl CPhysicsScriptStatements__CreateStatementType6(int valueType)` | Type-6/spawner value factory over observed spawner value ids; exact value classes/layouts remain unproven. |
| `0x0043a860` | `void * __cdecl CPhysicsScriptStatements__CreateStatementType7(int valueType)` | Type-7/explosion value factory over observed value ids `0x1` through `0xf`; exact value classes/layouts remain unproven. |
| `0x0043b990` | `void * __cdecl CPhysicsScriptStatements__CreateStatementType8(int valueType)` | Type-8/feature value factory over observed value ids `0x1` through `0x7`; exact value classes/layouts remain unproven. |
| `0x0043c0b0` | `void * __cdecl CPhysicsScriptStatements__CreateStatementType9(int valueType)` | Type-9/hazard value factory over observed value ids `0x1` through `0x4`; exact value classes/layouts remain unproven. |
| `0x0043c500` | `void * __cdecl CPhysicsScriptStatements__CreateStatementType10(int valueType)` | Type-10/component value factory over observed ids `0x1..0x19` except `0x5`; exact value classes/layouts remain unproven. |
| `0x0043dcd0` | `void * __cdecl CPhysicsScriptStatements__CreateStatementType11(int valueType)` | Type-11/seek value factory over observed ids `1..3`; exact value classes/layouts remain unproven. |
| `0x0043ddc0` | `void * __cdecl CPhysicsScriptStatements__CreateStatementType12(int valueType)` | Type-12/behaviour value factory over observed ids `0x1..0x19`; exact value classes/layouts remain unproven. |
| `0x0043e310` | `void * __cdecl CPhysicsScriptStatements__CreateStatementType13(int valueType)` | Type-13/alligence value factory over observed ids `1..3`; exact value classes/layouts remain unproven. |
| `0x0043e400` | `void * __cdecl CPhysicsScriptStatements__CreateStatementType14(int valueType)` | Type-14/navmap value factory over observed ids `1..4`; exact value classes/layouts remain unproven. |
| `0x0043e540` | `void * __cdecl CPhysicsScriptStatements__CreateStatementType15(int valueType)` | Type-15/state value factory over observed ids `1..3`; exact value classes/layouts remain unproven. |

## Value-List Helpers

| Address | Saved signature | Current evidence |
| --- | --- | --- |
| `0x0042f280` | `int __fastcall CPhysicsUnitValueList__GetSerializedSize(void * this)` | Corrected from stale `CUnitAI__ComputeRecursiveNodeSize_Base8`; this is the unit value-list size helper, not UnitAI. |
| `0x0042f3d0` | `void __thiscall CPhysicsUnitValueList__LoadFromMemBuffer(void * this, void * memBuffer)` | Corrected from constructor-like label to recursive value-list load helper. |
| `0x0042f4b0` | `void * __thiscall CPhysicsUnitValueList__scalar_deleting_dtor(void * this, int flags)` | Corrected from generic vfunc label to scalar-deleting destructor wrapper for value-list nodes; Wave1040 corrected stale free wording to `CDXMemoryManager__Free(&DAT_009c3df0, this)` via `0x00549220`. |
| `0x0042f750` | `int __fastcall CPhysicsWeaponValueList__GetSerializedSize(void * this)` | Corrected from stale top-level `CWeaponStatement__GetSerializedSize`; this is the recursive weapon value-list size helper. |
| `0x0042f8a0` | `void __thiscall CPhysicsWeaponValueList__LoadFromMemBuffer(void * this, void * memBuffer)` | Corrected from constructor-like label to recursive weapon value-list load helper. |
| `0x0042f980` | `void * __thiscall CPhysicsWeaponValueList__scalar_deleting_dtor(void * this, int flags)` | Corrected from generic vfunc label to scalar-deleting destructor wrapper; Wave1040 corrected stale free wording to `CDXMemoryManager__Free(&DAT_009c3df0, this)` via `0x00549220`. |
| `0x0042fc70` | `int __fastcall CPhysicsWeaponModeValueList__GetSerializedSize(void * this)` | Corrected from stale top-level `CWeaponModeStatement__GetSerializedSize`; this is the recursive weapon-mode value-list size helper. |
| `0x0042fdc0` | `void __thiscall CPhysicsWeaponModeValueList__LoadFromMemBuffer(void * this, void * memBuffer)` | Corrected from constructor-like label to recursive weapon-mode value-list load helper. |
| `0x0042fea0` | `void * __thiscall CPhysicsWeaponModeValueList__scalar_deleting_dtor(void * this, int flags)` | Corrected from generic vfunc label to scalar-deleting destructor wrapper; Wave1040 corrected stale free wording to `CDXMemoryManager__Free(&DAT_009c3df0, this)` via `0x00549220`. |
| `0x004301e0` | `int __fastcall CPhysicsRoundValueList__GetSerializedSize(void * this)` | Corrected from stale top-level `CRoundStatement__GetSerializedSize`; this is the recursive round value-list size helper. |
| `0x00430330` | `void __thiscall CPhysicsRoundValueList__LoadFromMemBuffer(void * this, void * memBuffer)` | Corrected from constructor-like label to recursive round value-list load helper. |
| `0x00430410` | `void * __thiscall CPhysicsRoundValueList__scalar_deleting_dtor(void * this, int flags)` | Corrected from generic vfunc label to scalar-deleting destructor wrapper; Wave1040 corrected stale free wording to `CDXMemoryManager__Free(&DAT_009c3df0, this)` via `0x00549220`. |
| `0x004306b0` | `int __fastcall CPhysicsSpawnerValueList__GetSerializedSize(void * this)` | Corrected from stale top-level `CSpawnerStatement__GetSerializedSize`; this is the recursive spawner value-list size helper. |
| `0x00430800` | `void __thiscall CPhysicsSpawnerValueList__LoadFromMemBuffer(void * this, void * memBuffer)` | Corrected from constructor-like label to recursive spawner value-list load helper. |
| `0x004308e0` | `void * __thiscall CPhysicsSpawnerValueList__scalar_deleting_dtor(void * this, int flags)` | Corrected from generic vfunc label to scalar-deleting destructor wrapper. |
| `0x00430b30` | `int __fastcall CPhysicsExplosionValueList__GetSerializedSize(void * this)` | Corrected from stale `CUnitAI__ComputeRecursiveNodeSize_NodeTreeA`; this is the recursive explosion value-list size helper. |
| `0x00430c80` | `void __thiscall CPhysicsExplosionValueList__LoadFromMemBuffer(void * this, void * memBuffer)` | Corrected from constructor-like label to recursive explosion value-list load helper. |
| `0x00430d60` | `void * __thiscall CPhysicsExplosionValueList__scalar_deleting_dtor(void * this, int flags)` | Corrected from generic vfunc label to scalar-deleting destructor wrapper. |
| `0x00431020` | `int __fastcall CPhysicsComponentValueList__GetSerializedSize(void * this)` | Corrected from stale top-level `CComponentStatement__GetSerializedSize`; this is the recursive component value-list size helper. |
| `0x00431170` | `void __thiscall CPhysicsComponentValueList__LoadFromMemBuffer(void * this, void * memBuffer)` | Corrected from constructor-like label to recursive component value-list load helper. |
| `0x00431250` | `void * __thiscall CPhysicsComponentValueList__scalar_deleting_dtor(void * this, int flags)` | Corrected from generic vfunc label to scalar-deleting destructor wrapper. |
| `0x00431470` | `int __fastcall CPhysicsFeatureValueList__GetSerializedSize(void * this)` | Corrected from stale `CUnitAI__ComputeRecursiveNodeSize_NodeTreeB`; this is the recursive feature value-list size helper. |
| `0x004315c0` | `void __thiscall CPhysicsFeatureValueList__LoadFromMemBuffer(void * this, void * memBuffer)` | Corrected from constructor-like label to recursive feature value-list load helper. |
| `0x004316a0` | `void * __thiscall CPhysicsFeatureValueList__scalar_deleting_dtor(void * this, int flags)` | Corrected from generic vfunc label to scalar-deleting destructor wrapper. |
| `0x004318c0` | `int __fastcall CPhysicsHazardValueList__GetSerializedSize(void * this)` | Corrected from stale `CUnitAI__ComputeRecursiveNodeSize_NodeTreeC`; this is the recursive hazard value-list size helper. |
| `0x00431a10` | `void __thiscall CPhysicsHazardValueList__LoadFromMemBuffer(void * this, void * memBuffer)` | Corrected from constructor-like label to recursive hazard value-list load helper. |
| `0x00431af0` | `void * __thiscall CPhysicsHazardValueList__scalar_deleting_dtor(void * this, int flags)` | Corrected from generic vfunc label to scalar-deleting destructor wrapper. |

## Unit And Weapon Value Helpers

| Address | Saved signature | Current evidence |
| --- | --- | --- |
| `0x00432a20` | `void __thiscall CUnitAlligence__LoadFromMemBuffer(void * this, void * memBuffer)` | Wave947 recovered this vtable-backed boundary from CUnitAlligence vtable `0x005d9d28` slot 3 / DATA xref `0x005d9d34`; reads a child value type and dispatches `CPhysicsScriptStatements__CreateStatementType13`. |
| `0x00432ac0` | `void * __thiscall CPhysicsUnitValue__base_vtable_scalar_deleting_dtor(void * this, int flags)` | Wave947 recovered the CPhysicsUnitValue base-vtable scalar-deleting destructor wrapper at vtable `0x005d9e54` slot 0; restores base vtable state and optionally calls `OID__FreeObject`. |
| `0x004347b0` | `void * __thiscall CPhysicsWeaponValue__base_vtable_scalar_deleting_dtor(void * this, int flags)` | Wave947 recovered the CPhysicsWeaponValue base-vtable scalar-deleting destructor wrapper at vtable `0x005d9f80` slot 0; restores base vtable state and optionally calls `OID__FreeObject`. |
| `0x00432bd0` | `void __thiscall CUnitImportance__ApplyToUnitData(void * this, void * unitData)` | Wave947 recovered this apply helper from vtable `0x005d9cec` slot 1 / DATA xref `0x005d9cf0`; copies the value at `this+0x8` to unit/init-like field `+0xf8`. |
| `0x00432c00` | `void __thiscall CUnitSoundMaterial__ApplyToUnitData(void * this, void * unitData, void * context)` | Applies the rounded scalar at `this + 0x8` into unit data/init-like field `+0xe4`. |
| `0x00432c60` | `void __thiscall CUnitStandingLegPlacementArea__ApplyToUnitData(void * this, void * unitData)` | Wave947 recovered this apply helper from vtable `0x005d9c24` slot 1 / DATA xref `0x005d9c28`; copies the value at `this+0x8` to unit/init-like field `+0x150`. |
| `0x00432c70` | `void __thiscall CUnitMaxLegsLifted__ApplyToUnitData(void * this, void * unitData, void * context)` | Applies the rounded scalar at `this + 0x8` into unit data/init-like field `+0x140`. |
| `0x00432f10` | `void __thiscall CUnitStrafeChange__ApplyToUnitData(void * this, void * unitData)` | Wave947 recovered this apply helper from vtable `0x005d9bac` slot 1 / DATA xref `0x005d9bb0`; copies the value at `this+0x8` to unit/init-like field `+0x180`. |
| `0x00432f50` | `void __thiscall CUnitNavMap__ApplyToUnitData(void * this, void * unitData)` | Wave947 recovered this apply helper from vtable `0x005d9b98` slot 1 / DATA xref `0x005d9b9c`; applies the child value at `this+0x8` and writes the result to unit/init-like field `+0xfc`. |
| `0x00432f70` | `void __thiscall CUnitNavMap__LoadFromMemBuffer(void * this, void * memBuffer)` | Reads a child statement type and dispatches `CreateStatementType14`; stores the child statement at `+0x8`. |
| `0x00433010` | `void __thiscall CUnitBehaviour__ApplyToUnitData(void * this, void * unitData)` | Wave947 recovered this apply helper from vtable `0x005d9d50` slot 1 / DATA xref `0x005d9d54`; applies a child behavior id into unit/init-like field `+0xe0` and maps selected ids into `+0xfc`. |
| `0x004330b0` | `void __thiscall CUnitBehaviour__LoadFromMemBuffer(void * this, void * memBuffer)` | Reads a child statement type and dispatches `CreateStatementType12`; stores the child statement at `+0x8`. |
| `0x00433150` | `void __thiscall CUnitUse__ApplyToUnitData(void * this, void * unitData)` | Wave947 recovered this apply helper from vtable `0x005d9d64` slot 1 / DATA xref `0x005d9d68`; passes `this+0x8`, unit/init-like field `+0x108`, and `this+0x208` into helper `0x005119e0`. |
| `0x00434770` | `void __thiscall CWeaponChargeLevel__LoadFromMemBuffer(void * this, void * memBuffer)` | Loads a charge-level scalar into `+0x108` and a name string into the owned string field. |
| `0x00434930` | `void __thiscall CWeaponConsumption__ApplyToWeaponByName(void * this, char * weaponName)` | Wave947 recovered this weapon-list apply helper from vtable `0x005d9f30` slot 1 / DATA xref `0x005d9f34`; searches global weapon list `DAT_008553e8` by name and applies the value payload. |
| `0x00434de0` | `void __thiscall CWeaponVersusAir__ApplyToWeaponByName(void * this, char * weaponName)` | Wave947 recovered this weapon-list apply helper from vtable `0x005d9e68` slot 1 / DATA xref `0x005d9e6c`; searches global weapon list `DAT_008553e8` by name and applies the value payload. |
| `0x00434f20` | `void __thiscall CWeaponIconName__ApplyToWeaponByName(void * this, char * weaponName, void * context)` | Searches global weapon list `DAT_008553e8` by name and replaces the matching weapon record icon string. |

## Weapon Mode Value Helpers

| Address | Saved signature | Current evidence |
| --- | --- | --- |
| `0x00435840` | `void __thiscall CWeaponBasedOn__ApplyToWeaponByName(void * this, char * weaponName)` | Searches global weapon list `DAT_008553e8` by name and copies selected fields from the base/source weapon named by `this + 0x8`. |
| `0x004359c0` | `void __fastcall CPhysicsWeaponModeValue__dtor_base(void * this)` | Base destructor body called by `0x00437080` before optional object free; this supersedes the Wave 336 constructor-base wording. Wave987 removed the stale `constructor` tag and preserved `destructor` plus `supersedes-wave336-ctor-label`. |
| `0x00435b20` | `void __thiscall CPhysicsWeaponModeValue__LoadTwoScalarsFromMemBuffer(void * this, void * memBuffer)` | Shared load helper for two 4-byte scalar fields at `this + 0x8` and `this + 0xc`. |
| `0x00435c90` | `void __thiscall CWeaponLaunchAngle__LoadFromMemBuffer(void * this, void * memBuffer)` | Launch-angle load helper for three 4-byte fields at `this + 0x8`, `this + 0xc`, and `this + 0x10`. |
| `0x00436130` | `void __thiscall CWeaponVolleySize__ApplyToWeaponModeByName(void * this, char * weaponModeName)` | Searches global weapon-mode list `DAT_008553ec` by record name at `+0x30`, rounds the scalar at `this + 0x8`, and writes record field `+0x48`. |
| `0x00436320` | `void __thiscall CWeaponPreFireEffect__ApplyToWeaponModeByName(void * this, char * weaponModeName)` | Replaces the pre-fire effect owned string at weapon-mode record `+0x20`. |
| `0x00436410` | `void __thiscall CWeaponMuzzleEffect__ApplyToWeaponModeByName(void * this, char * weaponModeName)` | Replaces the muzzle effect owned string at weapon-mode record `+0x1c`. |
| `0x00436500` | `void __thiscall CWeaponClip__ApplyToWeaponModeByName(void * this, char * weaponModeName)` | Replaces the clip string reference after matching the weapon-mode record name. |

## Round Value Helpers

| Address | Saved signature | Current evidence |
| --- | --- | --- |
| `0x00437080` | `void * __thiscall CPhysicsWeaponModeValue__scalar_deleting_dtor(void * this, int flags)` | Scalar-deleting destructor wrapper that calls `CPhysicsWeaponModeValue__dtor_base`, optionally frees `this` through `OID__FreeObject` when flags bit 0 is set, and returns `this`. |
| `0x004370a0` | `void __thiscall CWeaponRound__ApplyToWeaponModeByName(void * this, char * weaponModeName)` | Searches global weapon-mode list `DAT_008553ec` by record name at `+0x30`, searches global round list `DAT_008553f0` by the round name at `this + 0x8` against round record names at `+0x18`, and writes the selected reader/index through `CWeaponRound__SetReaderFromGlobalListByIndex`. |
| `0x004371c0` | `void __thiscall CWeaponLaunchSound__ApplyToWeaponModeByName(void * this, char * weaponModeName)` | Searches global weapon-mode list `DAT_008553ec` by record name at `+0x30` and replaces the owned launch-sound string at weapon-mode record `+0x24` from the value string at `this + 0x8`. |
| `0x004372b0` | `void __thiscall CWeaponPreFireSound__ApplyToWeaponModeByName(void * this, char * weaponModeName)` | Searches global weapon-mode list `DAT_008553ec` by record name at `+0x30` and replaces the owned pre-fire sound string at weapon-mode record `+0x28` from the value string at `this + 0x8`. |
| `0x004373a0` | `void __thiscall CWeaponPostFireSound__ApplyToWeaponModeByName(void * this, char * weaponModeName)` | Searches global weapon-mode list `DAT_008553ec` by record name at `+0x30` and replaces the owned post-fire sound string at weapon-mode record `+0x2c` from the value string at `this + 0x8`. |

## Round Value Tail Helpers

| Address | Saved signature | Current evidence |
| --- | --- | --- |
| `0x00437fe0` | `void __thiscall CPhysicsRoundValue__SetOwnedAuxStringAt0C(void * this, char * sourceString)` | Owned string-copy helper for round/value records; frees `this+0xc` and copies `sourceString` into replacement storage allocated with the observed `0x23c` tag. |
| `0x00438050` | `void __thiscall CPhysicsRoundValue__SetOwnedValueStringAt08(void * this, char * sourceString)` | Supersedes stale `CUnitAI` ownership; frees `this+0x8` and copies `sourceString` into the owned value string slot used by round-value handlers. |
| `0x004380c0` | `void __fastcall CPhysicsRoundValue__dtor_base(void * this)` | Base destructor body that installs vtable `0x005da584`; that vtable slot 0 points at recovered boundary `0x004380d0`. |
| `0x004380d0` | `void * __thiscall CPhysicsRoundValue__scalar_deleting_dtor(void * this, int flags)` | Recovered missing base scalar-deleting destructor wrapper from vtable `0x005da584`; optionally frees `this` through `OID__FreeObject`. |
| `0x00438400` | `void * __thiscall CPhysicsRoundValueLeaf__shared_scalar_deleting_dtor(void * this, int flags)` | Shared leaf scalar-deleting destructor wrapper that calls `CPhysicsRoundValue__dtor_base` and, when flags bit 0 is set, frees `this` through `CDXMemoryManager__Free(&DAT_009c3df0, this)` via `0x00549220`, not `OID__FreeObject`. |
| `0x00438b40` | `void __thiscall CRoundGridOfFear__ApplyToRoundByName(void * this, char * roundName)` | Searches `DAT_008553f0` by round name and writes `ROUND(this+0x8)` to round record `+0x58`. |
| `0x004394e0` | `void __thiscall CRoundSeek__ApplyToRoundByName(void * this, char * roundName)` | Recovered function boundary from `CRoundSeek` vtable context; writes nested child value result from `this+0x8` to round record `+0x48`. |
| `0x00439580` | `void __thiscall CRoundSeek__LoadFromMemBuffer(void * this, void * memBuffer)` | Reads nested value type id, dispatches `CPhysicsScriptStatements__CreateStatementType11`, and stores the child value at `this+0x8`. |
| `0x004395b0` | `void * __thiscall CRoundSeek__scalar_deleting_dtor(void * this, int flags)` | Scalar-deleting destructor wrapper around `CRoundSeek__dtor_base`. |
| `0x004395d0` | `void __fastcall CRoundSeek__dtor_base(void * this)` | Destructor body that destroys the owned child at `this+0x8` before restoring the base round-value vtable. |
| `0x00439620` | `void __thiscall CRoundMesh__ApplyToRoundByName(void * this, char * roundName)` | Searches `DAT_008553f0` and replaces the owned mesh string at round record `+0xc`. |
| `0x00439710` | `void __thiscall CRoundEffect__ApplyToRoundByName(void * this, char * roundName)` | Searches `DAT_008553f0` and replaces the owned effect string at round record `+0x10`. |
| `0x00439800` | `void __thiscall CRoundWaterEffect__ApplyToRoundByName(void * this, char * roundName)` | Searches `DAT_008553f0` and replaces the owned water-effect string at round record `+0x14`. |
| `0x00439910` | `void __thiscall CRoundExplosion__ApplyToRoundByName(void * this, char * roundName)` | Searches `DAT_008553f0` and replaces the owned explosion string at round record `+0x8`. |
| `0x00439a00` | `void __thiscall CRoundTreeCollision__ApplyToRoundByName(void * this, char * roundName)` | Recovered function boundary from `CRoundTreeCollision` vtable context; writes nested child value result from `this+0x8` to round record `+0xa4`. |
| `0x00439aa0` | `void __thiscall CRoundTreeCollision__LoadFromMemBuffer(void * this, void * memBuffer)` | Reads nested value type id, dispatches `CPhysicsScriptStatements__CreateStatementType15`, and stores the child value at `this+0x8`. |
| `0x00439ad0` | `void * __thiscall CRoundTreeCollision__scalar_deleting_dtor(void * this, int flags)` | Scalar-deleting destructor wrapper around `CRoundTreeCollision__dtor_base`. |
| `0x00439af0` | `void __fastcall CRoundTreeCollision__dtor_base(void * this)` | Destructor body that destroys the owned child at `this+0x8` before restoring the base round-value vtable. |

## Spawner Value Helpers

| Address | Saved signature | Current evidence |
| --- | --- | --- |
| `0x004014c0` | `void __thiscall SharedVFunc__NoOpOneArg_004014c0(void * this, int arg0)` | Wave 339 superseded the older frontend-specific label after vtable-slot evidence showed broad shared no-op use. |
| `0x00405930` | `int __thiscall SharedVFunc__ReturnZero_00405930(void * this)` | Wave 339 superseded the older controller-specific label after vtable-slot evidence showed broad shared return-zero use. |
| `0x00434b60` | `void __thiscall CPhysicsScriptValue__LoadScalarAt08FromMemBuffer(void * this, void * memBuffer)` | Recovered shared scalar load boundary for the value object field at `this+0x8`. |
| `0x004398f0` | `int __fastcall CPhysicsScriptValue__GetOwnedStringAt08SerializedSize(void * this)` | Recovered shared owned-string serialized-size boundary. |
| `0x00439b40` | `void * __cdecl CPhysicsScriptStatements__CreateStatementType6(int valueType)` | Hardened the type-6/spawner value factory signature/comment. |
| `0x00439e70` | `void __thiscall CSpawnerBasedOn__ApplyToSpawnerByName(void * this, char * spawnerName)` | Applies base-spawner fields after resolving the named spawner record. |
| `0x0043a040` | `void __fastcall CPhysicsSpawnerValue__dtor_base(void * this)` | Base destructor body for `CPhysicsSpawnerValue`; adjacent vtable evidence points at the recovered scalar-deleting wrapper. |
| `0x0043a050` | `void * __thiscall CPhysicsSpawnerValue__scalar_deleting_dtor(void * this, int flags)` | Recovered base scalar-deleting destructor wrapper from spawner value vtable context. |
| `0x0043a080` | `void __thiscall CSpawnerUnit__ApplyToSpawnerByName(void * this, char * spawnerName)` | Recovered spawner unit apply helper. |
| `0x0043a170` / `0x0043a200` | `CSpawnerDelay__ApplyToSpawnerByName`, `CSpawnerAmount__ApplyToSpawnerByName` | Recovered scalar spawner apply helpers for delay and amount-style fields. |
| `0x0043a290` / `0x0043a320` | `CSpawnerConditions__ApplyToSpawnerByName`, `CSpawnerSquadSize__ApplyToSpawnerByName` | Recovered spawner apply helpers for conditions and squad-size-style fields. |
| `0x0043a3b0` / `0x0043a440` | `CSpawnerSquadDelay__ApplyToSpawnerByName`, `CSpawnerSeekDelay__ApplyToSpawnerByName` | Recovered spawner timing apply helpers. |
| `0x0043a4d0` | `CSpawnerRecall__ApplyToSpawnerByName` | Recovered spawner recall apply helper. |
| `0x0043a570` / `0x0043a600` | `CSpawnerMinRange__ApplyToSpawnerByName`, `CSpawnerMaxRange__ApplyToSpawnerByName` | Recovered spawner range apply helpers. |
| `0x0043a690` / `0x0043a720` | `CSpawnerPreSpawnDelay__ApplyToSpawnerByName`, `CSpawnerPostSpawnDelay__ApplyToSpawnerByName` | Recovered pre/post-spawn delay apply helpers. |
| `0x0043a7b0` | `CSpawnerInfinite__ApplyToSpawnerByName` | Recovered spawner infinite apply helper. |
| `0x0043a840` | `void * __thiscall CPhysicsSpawnerValueLeaf__shared_scalar_deleting_dtor(void * this, int flags)` | Shared leaf scalar-deleting destructor wrapper for spawner value vtables; Wave1183 corrected the optional-free path to `CDXMemoryManager__Free(&DAT_009c3df0, this)` via `0x00549220`, not `OID__FreeObject`. |
| `0x0043b1a0` | `void __thiscall CPhysicsScriptValue__LoadOwnedStringAt08FromMemBuffer(void * this, void * memBuffer)` | Recovered shared owned-string load boundary. |
| `0x004db8c0` | `int __fastcall CPhysicsScriptValue__GetScalarSerializedSize4(void * this)` | Recovered shared scalar serialized-size helper returning fixed size `4`. |

## Explosion Value Helpers

| Address | Saved signature | Current evidence |
| --- | --- | --- |
| `0x0043a860` | `void * __cdecl CPhysicsScriptStatements__CreateStatementType7(int valueType)` | Hardened the type-7/explosion value factory over ids `0x1..0xf`; factory vtable evidence spans `0x005da6c4` through `0x005da7dc`, with exact classes/layouts still unproven. |
| `0x0043abd0` | `void __thiscall CExplosionBasedOn__ApplyToExplosionByName(void * this, char * explosionName)` | Searches `DAT_008553f8`, resolves the base/source explosion name at `this+0x8`, and copies selected fields from the source explosion record. |
| `0x0043aea0` | `void __thiscall CExplosionBasedOn__CopySoundString28(void * this, char * sourceString)` | Helper that copies/clones the sound string into the explosion-based value string slot for record field `+0x28`; exact layout remains unproven. |
| `0x0043af10` | `void __thiscall CExplosionBasedOn__CopyWaterSoundString2C(void * this, char * sourceString)` | Helper that copies/clones the water-sound string into the explosion-based value string slot for record field `+0x2c`; exact layout remains unproven. |
| `0x0043af80` / `0x0043af90` | `CPhysicsExplosionValue__dtor_base` / `CPhysicsExplosionValue__scalar_deleting_dtor` | Corrected stale constructor-like evidence to the base destructor body and recovered adjacent scalar-deleting wrapper. |
| `0x0043afc0` / `0x0043b0b0` | `CExplosionAirEffect__ApplyToExplosionByName`, `CExplosionGroundEffect__ApplyToExplosionByName` | Owned-string explosion apply helpers for record fields `+0x18` and `+0x20`. |
| `0x0043b1c0` / `0x0043b2b0` | `CExplosionWaterEffect__ApplyToExplosionByName`, `CExplosionUnitEffect__ApplyToExplosionByName` | Owned-string explosion apply helpers for record fields `+0x1c` and `+0x24`. |
| `0x0043b3a0`, `0x0043b430`, `0x0043b4c0`, `0x0043b700` | `CExplosionScalar34__ApplyToExplosionByName`, `CExplosionScalar38__ApplyToExplosionByName`, `CExplosionScalar3C__ApplyToExplosionByName`, `CExplosionScalar40__ApplyToExplosionByName` | Recovered offset-backed scalar apply helpers for explosion record fields `+0x34`, `+0x38`, `+0x3c`, and `+0x40`; scalar field semantics remain unproven. |
| `0x0043b550`, `0x0043b5e0`, `0x0043b670` | `CExplosionScalar44__ApplyToExplosionByName`, `CExplosionScalar48__ApplyToExplosionByName`, `CExplosionScalar4C__ApplyToExplosionByName` | Recovered offset-backed scalar apply helpers for explosion record fields `+0x44`, `+0x48`, and `+0x4c`; scalar field semantics remain unproven. |
| `0x0043b790` / `0x0043b880` | `CExplosionSound__ApplyToExplosionByName`, `CExplosionWaterSound__ApplyToExplosionByName` | Owned-string explosion sound apply helpers for record fields `+0x28` and `+0x2c`. |
| `0x0043b970` | `void * __thiscall CPhysicsExplosionValueLeaf__shared_scalar_deleting_dtor(void * this, int flags)` | Corrected stale vfunc-slot label to shared leaf scalar-deleting destructor wrapper evidence; Wave1183 corrected the optional-free path to `CDXMemoryManager__Free(&DAT_009c3df0, this)` via `0x00549220`, not `OID__FreeObject`. |

## Feature Value Helpers

| Address | Saved signature | Current evidence |
| --- | --- | --- |
| `0x0043b990` | `void * __cdecl CPhysicsScriptStatements__CreateStatementType8(int valueType)` | Hardened the type-8/feature value factory over ids `0x1..0x7`; factory vtable evidence spans `0x005da804` through `0x005da87c`, with exact classes/layouts still unproven. |
| `0x0043bb30` / `0x0043bbf0` | `CFeatureScalar18__ApplyToFeatureByName`, `CFeatureScalar1C__ApplyToFeatureByName` | Recovered offset-backed scalar apply helpers for feature record fields `+0x18` and `+0x1c`; scalar field semantics remain unproven. |
| `0x0043bc80` / `0x0043bd40` | `CFeatureFlag10__ApplyToFeatureByName`, `CFeatureFlag14__ApplyToFeatureByName` | Recovered flag-style apply helpers for feature record fields `+0x10` and `+0x14`; they compare the value scalar with `0.0` before writing `1` or `0`. |
| `0x0043be00` / `0x0043bbc0` / `0x0043bff0` | `CPhysicsFeatureValue__dtor_base`, `CPhysicsFeatureValue__scalar_deleting_dtor`, and `CPhysicsFeatureValueLeaf__shared_scalar_deleting_dtor` | Corrected stale constructor/vfunc labels to the feature-value destructor family; Wave1183 corrected the leaf wrapper optional-free path to `CDXMemoryManager__Free(&DAT_009c3df0, this)` via `0x00549220`, not `OID__FreeObject`. |
| `0x0043be10` / `0x0043bf00` | `CFeatureMesh__ApplyToFeatureByName`, `CFeatureNoise__ApplyToFeatureByName` | Corrected stale vfunc labels to owned-string apply helpers against the feature record context. |
| `0x0043c010` | `void __thiscall CFeatureTexture__ApplyToFeatureByName(void * this, char * featureName)` | Recovered texture apply boundary; resolves the feature record and calls the existing texture-name/index helper. |

## Hazard Value Helpers

| Address | Saved signature | Current evidence |
| --- | --- | --- |
| `0x0043c0b0` | `void * __cdecl CPhysicsScriptStatements__CreateStatementType9(int valueType)` | Hardened the type-9/hazard value factory over ids `0x1..0x4`; factory vtable evidence spans `0x005da8a4` through `0x005da8e0`, with exact classes/layouts still unproven. |
| `0x0043c1a0` / `0x0043c280` | `CHazardScalar14__ApplyToHazardByName`, `CHazardScalar18__ApplyToHazardByName` | Recovered offset-backed scalar apply helpers for hazard record fields `+0x14` and `+0x18`; scalar field semantics remain unproven. |
| `0x0043c230` / `0x0043c250` / `0x0043c310` | `CPhysicsHazardValueLeaf__shared_scalar_deleting_dtor`, `CPhysicsHazardValue__scalar_deleting_dtor`, and `CPhysicsHazardValue__dtor_base` | Corrected stale constructor/vfunc labels to the hazard-value destructor family and recovered the base scalar-deleting wrapper; Wave1183 corrected the leaf wrapper optional-free path to `CDXMemoryManager__Free(&DAT_009c3df0, this)` via `0x00549220`, not `OID__FreeObject`. |
| `0x0043c320` / `0x0043c410` | `CHazardNoise__ApplyToHazardByName`, `CHazardEffect__ApplyToHazardByName` | Corrected stale vfunc labels to owned-string apply helpers for hazard record fields `+0xc` and `+0x8`. |

## Component Value Helpers

| Address | Saved signature | Current evidence |
| --- | --- | --- |
| `0x0043c500` | `void * __cdecl CPhysicsScriptStatements__CreateStatementType10(int valueType)` | Hardened the type-10/component-value factory over ids `0x1..0x19` except `0x5`; factory vtable evidence spans `0x005da908` through `0x005daad4`, with exact classes/layouts still unproven. |
| `0x0043ca70` / `0x0043cb40` / `0x0043cbe0` / `0x0043cc80` / `0x0043cd20` / `0x0043cdc0` / `0x0043d460` | component scalar apply helpers | Recovered offset-backed scalar apply helpers for component record fields `+0xd8`, `+0xdc`, `+0xc0`, `+0x158`, `+0xb8`, `+0xbc`, and `+0x160`; scalar field semantics remain unproven. |
| `0x0043ce60` / `0x0043cf20` / `0x0043cfe0` / `0x0043d0a0` / `0x0043d160` / `0x0043d220` / `0x0043d2e0` / `0x0043d3a0` | component flag apply helpers | Recovered flag-style helpers for component record fields `+0x124`, `+0x128`, `+0x12c`, `+0x198`, `+0x114`, `+0x19c`, `+0x134`, and `+0x108`; Wave1039 corrected stale positive-only wording because the bodies compare `this+0x8` with zero constant `0x005d856c` and write `0` on the zero-comparison path and `1` otherwise, with field semantics still unproven. |
| `0x0043d760` / `0x0043d8f0` / `0x0043da90` | `CComponentMesh__ApplyToComponentByName`, `CComponentVent__ApplyToComponentByName`, `CComponentNoise__ApplyToComponentByName` | Corrected stale vfunc labels to owned-string component apply helpers for record fields `+0x2c`, `+0x98`, and `+0xa8`. |
| `0x0043db90` | `void __thiscall CComponentBasedOn__ApplyToComponentByName(void * this, char * componentName)` | Resolves the destination component, resolves the source name at `this+0x8`, and calls `CComponentBasedOn__CopyFrom(destination, source/null)`. |
| `0x0043d500` | `void __thiscall CComponentIndexedScalar164__ApplyToComponentByName(void * this, char * componentName)` | Writes the scalar using component record field `+0x164` plus the dword index at `this+0xc`; exact array semantics remain unproven. |
| `0x004175b0` / `0x00433170` / `0x004331e0` / `0x00433220` | shared and compound load/size helpers | Hardened two-scalar serialized-size evidence plus conservative `CComponentValue02` and `CComponentValue13` load/size helpers. |
| `0x0043d5c0` / `0x0043d670` / `0x0043d6b0` / `0x0043d850` / `0x0043d9f0` | conservative component value apply/size helpers | Hardened `CComponentValue02`, `CComponentValue13`, `CComponentValue04`, and `CComponentValue0E` apply/size labels where value ids are still conservative. |
| `0x0043d5a0` / `0x0043dcc0` | `CPhysicsComponentValueLeaf__shared_scalar_deleting_dtor` and `CPhysicsComponentValue__dtor_base` | Recovered the shared leaf scalar-deleting destructor wrapper and base destructor body; the base destructor restores vtable `0x005daae8`, and Wave1183 corrected the leaf wrapper optional-free path to `CDXMemoryManager__Free(&DAT_009c3df0, this)` via `0x00549220`, not `OID__FreeObject`. |

## Seek / Behaviour / NavMap / State Value Helpers

| Address | Saved signature | Current evidence |
| --- | --- | --- |
| `0x0043dcd0` | `void * __cdecl CPhysicsScriptStatements__CreateStatementType11(int valueType)` | Hardened the type-11/seek value factory over ids `1..3`; factory vtable evidence spans `0x005daafc` through `0x005dab14`, with exact classes/layouts still unproven. |
| `0x0043dd60` / `0x0043dd90` / `0x0043ddb0` | `CPhysicsSeekType__scalar_deleting_dtor`, `CPhysicsSeekTypeLeaf__shared_scalar_deleting_dtor`, and `CPhysicsSeekType__dtor_base` | Recovered the base scalar-deleting destructor boundary and corrected stale vfunc/constructor-like labels to seek-value destructor evidence. |
| `0x0043ddc0` | `void * __cdecl CPhysicsScriptStatements__CreateStatementType12(int valueType)` | Hardened the type-12/behaviour value factory over ids `0x1..0x19`; factory vtable evidence spans `0x005dab2c` through `0x005dac4c`, with exact classes/layouts still unproven. |
| `0x0043e2b0` / `0x0043e2d0` / `0x0043e300` | `CPhysicsBehaviourTypeLeaf__shared_scalar_deleting_dtor`, `CPhysicsBehaviourType__scalar_deleting_dtor`, and `CPhysicsBehaviourType__dtor_base` | Recovered the base scalar-deleting destructor boundary and corrected stale constructor/vfunc evidence to behaviour-value destructor evidence. |
| `0x0043e310` | `void * __cdecl CPhysicsScriptStatements__CreateStatementType13(int valueType)` | Hardened the type-13/alligence value factory over ids `1..3`; factory vtable evidence spans `0x005dac64` through `0x005dac7c`, with exact classes/layouts still unproven. |
| `0x0043e3a0` / `0x0043e3c0` / `0x0043e3d0` | `CPhysicsAlligenceTypeLeaf__shared_scalar_deleting_dtor`, `CPhysicsAlligenceType__dtor_base`, and `CPhysicsAlligenceType__scalar_deleting_dtor` | Recovered the base scalar-deleting destructor boundary and separated shared leaf wrapper, base destructor body, and base scalar-deleting wrapper evidence. |
| `0x0043e400` | `void * __cdecl CPhysicsScriptStatements__CreateStatementType14(int valueType)` | Hardened the type-14/navmap value factory over ids `1..4`; factory vtable evidence spans `0x005dac94` through `0x005dacb8`, with exact classes/layouts still unproven. |
| `0x0043e4e0` / `0x0043e500` / `0x0043e530` | `CPhysicsNavMapTypeLeaf__shared_scalar_deleting_dtor`, `CPhysicsNavMapType__scalar_deleting_dtor`, and `CPhysicsNavMapType__dtor_base` | Recovered the base scalar-deleting destructor boundary and corrected stale constructor/vfunc evidence to navmap-value destructor evidence. |
| `0x0043e540` | `void * __cdecl CPhysicsScriptStatements__CreateStatementType15(int valueType)` | Hardened the type-15/state value factory over ids `1..3`; factory vtable evidence spans `0x005dacd0` through `0x005dace8`, with exact classes/layouts still unproven. |
| `0x0043e5d0` / `0x0043e5f0` / `0x0043e620` | `CPhysicsStateTypeLeaf__shared_scalar_deleting_dtor`, `CPhysicsStateType__scalar_deleting_dtor`, and `CPhysicsStateType__dtor_base` | Recovered the base scalar-deleting destructor boundary and corrected stale constructor/vfunc evidence to state-value destructor evidence. |
| `0x0043e630` | `void __cdecl CFlexArray__SkipBytesFromMemBuffer(void * memBuffer, int byteCount)` | Hardened the adjacent shared serialization helper as a byte-count skip loop over `CDXMemBuffer__Read`. |

## Destructor Chain

| Address | Saved signature | Current evidence |
| --- | --- | --- |
| `0x00432a50` | `void * __thiscall CUnitAlligence__scalar_deleting_dtor(void * this, int flags)` | Scalar-deleting wrapper around `CUnitAlligence__dtor`; spelling retained from current binary/source-adjacent evidence. |
| `0x00432a70` | `void __fastcall CUnitAlligence__dtor(void * this)` | Corrected from constructor-like label; deletes child value pointer at `+0x8` and restores the base value vtable. |
| `0x00432cc0` | `void __fastcall CPhysicsUnitValue__dtor_base(void * this)` | Corrected from constructor-like label; base destructor body for `CPhysicsUnitValue`. |
| `0x00432fa0` | `void * __thiscall CUnitNavMap__scalar_deleting_dtor(void * this, int flags)` | Scalar-deleting wrapper around `CUnitNavMap__dtor`. |
| `0x00432fc0` | `void __fastcall CUnitNavMap__dtor(void * this)` | Corrected from constructor-like label; deletes child statement pointer at `+0x8` and restores the base value vtable. |
| `0x004330e0` | `void * __thiscall CUnitBehaviour__scalar_deleting_dtor(void * this, int flags)` | Scalar-deleting wrapper around `CUnitBehaviour__dtor`. |
| `0x00433100` | `void __fastcall CUnitBehaviour__dtor(void * this)` | Corrected from constructor-like label; deletes child statement pointer at `+0x8` and restores the base value vtable. |
| `0x00434100` | `void * __thiscall CPhysicsUnitValue__scalar_deleting_dtor(void * this, int flags)` | Shared scalar-deleting wrapper used by many unit value vtables. |
| `0x004347a0` | `void __fastcall CPhysicsWeaponValue__dtor_base(void * this)` | Corrected from constructor-like label; base destructor body for `CPhysicsWeaponValue`. |
| `0x00434a80` | `void * __thiscall CPhysicsWeaponValue__scalar_deleting_dtor(void * this, int flags)` | Shared scalar-deleting wrapper used by weapon value vtables. |
| `0x0042f4f0` | `void * __thiscall CUnitStatement__scalar_deleting_dtor(void * this, int flags)` | Scalar-deleting wrapper around `CUnitStatement__dtor`. |
| `0x0042f510` | `void __fastcall CUnitStatement__dtor(void * this)` | Corrected from constructor-like label; deletes child pointer at `+0x10c` and restores the base vtable; Wave1143 refreshed this destructor-family evidence with statement destructor bodies and scalar-deleting wrapper xrefs. |
| `0x0042f570` | `void __fastcall CPhysicsScriptStatement__dtor(void * this)` | Corrected from constructor-like label; base destructor restores vtable `0x005d9894`. |
| `0x0042f580` | `void * __thiscall CPhysicsScriptStatement__scalar_deleting_dtor(void * this, int flags)` | Recovered missing base scalar-deleting destructor wrapper. |
| `0x0042f9c0` | `void * __thiscall CWeaponStatement__scalar_deleting_dtor(void * this, int flags)` | Scalar-deleting wrapper around `CWeaponStatement__dtor`. |
| `0x0042f9e0` | `void __fastcall CWeaponStatement__dtor(void * this)` | Corrected from constructor-like label; deletes child pointer at `+0x10c` and restores the base vtable. |
| `0x0042fee0` | `void * __thiscall CWeaponModeStatement__scalar_deleting_dtor(void * this, int flags)` | Scalar-deleting wrapper around `CWeaponModeStatement__dtor`. |
| `0x0042ff00` | `void __fastcall CWeaponModeStatement__dtor(void * this)` | Corrected from constructor-like label; deletes child pointer at `+0x10c` and restores the base vtable. |
| `0x00430450` | `void * __thiscall CRoundStatement__scalar_deleting_dtor(void * this, int flags)` | Scalar-deleting wrapper around `CRoundStatement__dtor`. |
| `0x00430470` | `void __fastcall CRoundStatement__dtor(void * this)` | Corrected from constructor-like label; deletes child pointer at `+0x10c` and restores the base vtable. |
| `0x00430610` | `void * __thiscall CSpawnerData__scalar_deleting_dtor(void * this, int flags)` | Scalar-deleting wrapper for spawner-data-like records with owned pointer cleanup. |
| `0x00430920` | `void * __thiscall CSpawnerStatement__scalar_deleting_dtor(void * this, int flags)` | Scalar-deleting wrapper around `CSpawnerStatement__dtor`. |
| `0x00430940` | `void __fastcall CSpawnerStatement__dtor(void * this)` | Corrected from constructor-like label; deletes child pointer at `+0x10c` and restores the base vtable. |
| `0x00430da0` | `void * __thiscall CExplosionStatement__scalar_deleting_dtor(void * this, int flags)` | Scalar-deleting wrapper around `CExplosionStatement__dtor`. |
| `0x00430dc0` | `void __fastcall CExplosionStatement__dtor(void * this)` | Corrected from constructor-like label; deletes child pointer at `+0x10c` and restores the base vtable. |
| `0x00431290` | `void * __thiscall CComponentStatement__scalar_deleting_dtor(void * this, int flags)` | Scalar-deleting wrapper around `CComponentStatement__dtor`. |
| `0x004312b0` | `void __fastcall CComponentStatement__dtor(void * this)` | Corrected from constructor-like label; deletes child pointer at `+0x10c` and restores the base vtable. |
| `0x004316e0` | `void * __thiscall CFeatureStatement__scalar_deleting_dtor(void * this, int flags)` | Scalar-deleting wrapper around `CFeatureStatement__dtor`. |
| `0x00431700` | `void __fastcall CFeatureStatement__dtor(void * this)` | Corrected from constructor-like label; deletes child pointer at `+0x10c` and restores the base vtable. |
| `0x00431b30` | `void * __thiscall CHazardStatement__scalar_deleting_dtor(void * this, int flags)` | Scalar-deleting wrapper around `CHazardStatement__dtor`. |
| `0x00431b50` | `void __fastcall CHazardStatement__dtor(void * this)` | Corrected from constructor-like label; deletes child pointer at `+0x10c` and restores the base vtable. |

## Adjacent Component Copy Helper

| Address | Saved signature | Current evidence |
| --- | --- | --- |
| `0x00433390` | `void __thiscall CComponentBasedOn__CopyFrom(void * this, void * sourceComponent)` | Deep-copy helper for component-based statement resource fields. It clones scalar fields, owned string/resource pointer fields through `OID__FreeObject` / `OID__AllocObject`, rebuilds linked/list members including `this+0x5c` through `CSPtrSet__AddToTail`, and copies a fixed dword block beginning at `this+0x164`. Wave 335 corrected the stale extra `param_N` argument; caller decompile read-back for `CComponentBasedOn__VFunc_01_0043db90` now passes only the destination and source/null. |


## Claim boundary

These rows are static Ghidra findings. They do not prove concrete class layouts,
local variables, complete serialized formats, runtime PhysicsScript behavior,
installed-game patch safety, gameplay outcomes, or rebuild parity. Use the
[PhysicsScript static contract](../physics-script-static-contract.md) for the
current subsystem boundary.
