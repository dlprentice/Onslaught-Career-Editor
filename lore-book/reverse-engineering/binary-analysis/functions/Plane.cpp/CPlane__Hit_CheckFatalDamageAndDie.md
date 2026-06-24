# CPlane Hit And Animation Helpers

> Source File: Plane.cpp | Binary: BEA.exe
> Wave: 485 | Evidence: saved Ghidra metadata, decompile, xrefs, vtable/RTTI rows, instruction rows, raw-caller rows, tags, and focused probe

## Functions

| Address | Name | Saved signature |
| --- | --- | --- |
| `0x004d1f10` | `CPlane__Hit_CheckFatalDamageAndDie` | `void __thiscall CPlane__Hit_CheckFatalDamageAndDie(void * this, void * hit_thing, void * hit_context)` |
| `0x004d1f90` | `CPlane__PlayWingOpenAnimationOnce` | `void __fastcall CPlane__PlayWingOpenAnimationOnce(void * this)` |
| `0x004d1fd0` | `CPlane__PlayWingCloseAnimationOnce` | `void __fastcall CPlane__PlayWingCloseAnimationOnce(void * this)` |
| `0x004d2010` | `CPlane__UpdateAttackLaunchAnimationState` | `int __fastcall CPlane__UpdateAttackLaunchAnimationState(void * this)` |

## Evidence

- `CPlane` vtable `0x005e1930` slot 39 points to `0x004d1f10`, while `CDiveBomber`, `CGroundAttackAircraft`, and `CBomber` use different slot-39 hit handlers.
- `0x004d1f10` reads `this+0x164->0x11c`, hit flags at `hit_thing+0x34`, and compares `hit_thing+0x138` against `this+0x138`.
- The selected fatal path may call `hit_thing` vfunc `+0x194`, then calls `CExplosionInitThing__ctor_like_004fd230`, then dispatches `this` vfunc `+0x38`.
- `0x004d1f10` always tails to `CThing__Hit_TriggerDieOnUnitOrTypeMask02100000(this, hit_thing, hit_context)` and ends with `RET 0x8`.
- `0x004d1f90` checks `this+0x27c == 1`, resolves `wingopen` string `0x00624420`, calls `CMesh__FindAnimationIndexByName`, dispatches `this` vfunc `+0xf0`, and sets `this+0x27c = 2`.
- `0x004d1fd0` checks `this+0x27c == 4`, resolves `wingclose` string `0x0062442c`, calls `CMesh__FindAnimationIndexByName`, dispatches `this` vfunc `+0xf0`, and sets `this+0x27c = 3`.
- `CPlane` vtable `0x005e1930` slot 59 points to `0x004d2010`, while `CDiveBomber`, `CGroundAttackAircraft`, and `CBomber` use different slot-59 animation handlers.
- `0x004d2010` checks the linked object at `this+0x8` through vfunc `+0x58`, then advances `this+0x27c` from `2` to `4` by playing `attack` string `0x00624438` or from `3` to `1` by playing `launch` string `0x006243f8`.
- Raw caller instruction rows show `0x004d229f` and `0x004d2400` call the wing-open/wing-close helpers after loading `[ESI+0x8]` into `ECX`; those caller regions still have no recovered Ghidra function boundary.

## Boundary

Static retail-binary evidence only. The current Stuart source snapshot does not contain a `Plane.cpp` or `CPlane` source body. Exact CPlane layout, hit/death behavior, animation-state semantics, raw caller boundaries, source body identity, runtime behavior, BEA launch behavior, game patching, and rebuild parity remain unproven.
