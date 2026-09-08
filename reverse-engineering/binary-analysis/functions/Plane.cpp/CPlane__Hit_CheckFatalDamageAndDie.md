# CPlane Hit And Animation Helpers

Status: active static function note; reviewed contact role names
Last updated: 2026-09-08
Summary: contact-triggered Plane shutdown and retained animation helpers; the
hit body does not inspect life or require fatal damage.

> Source File: Plane.cpp absent from the pinned partial source | Binary: BEA.exe
> Wave: 485 | Evidence: saved Ghidra metadata, decompile, xrefs, vtable/RTTI rows, instruction rows, raw-caller rows, tags, and focused probe

## Functions

| Address | Name | Saved signature |
| --- | --- | --- |
| `0x004d1f10` | `CPlane__Hit_RequestShutdownOnQualifiedContact` | `void __thiscall CPlane__Hit_RequestShutdownOnQualifiedContact(void * this, void * hit_thing, void * hit_context)` |
| `0x00403ba0` | `AirContact__Hit_RequestShutdownOnDyingContact` | `void __thiscall AirContact__Hit_RequestShutdownOnDyingContact(void * this, void * otherThing, void * collisionReport)` |
| `0x004d1f90` | `CPlane__PlayWingOpenAnimationOnce` | `void __fastcall CPlane__PlayWingOpenAnimationOnce(void * this)` |
| `0x004d1fd0` | `CPlane__PlayWingCloseAnimationOnce` | `void __fastcall CPlane__PlayWingCloseAnimationOnce(void * this)` |
| `0x004d2010` | `CPlane__UpdateAttackLaunchAnimationState` | `int __fastcall CPlane__UpdateAttackLaunchAnimationState(void * this)` |

## Evidence

- September 8 re-read pristine `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`,
  2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
  The former fatal-damage label was misleading: this body reads no life/damage
  value and its main arm does not require `TF_DYING`. The reviewed labels above
  describe measured roles, not recovered source method names.
- `CPlane` vtable `0x005e1930` slot 39 points to `0x004d1f10`, while `CDiveBomber`, `CGroundAttackAircraft`, and `CBomber` use different slot-39 hit handlers.
- The main arm requires `this+0x164->0x11c == 0`. `hit_thing+0x34` is the
  **type mask**, not the flag word. Same-allegiance AirUnit (`0x400`) contact
  skips this arm unless the other object is a BattleEngine (`0x8`). Otherwise
  other Unit (`0x10`) or raw mask `0x02100000` contact qualifies.
- A qualifying Unit first receives virtual `+0x194(this)`. Then the plane
  calls `CUnit__SpawnProfileDropPickup` (`0x004fd230`) and its own virtual
  `+0x38` (AddShutdownEvent). The previous constructor label for `0x004fd230`
  was wrong. This arm does not itself mark `TF_DYING`.
- Every path then calls `0x00403ba0` and returns with `RET 0x8`. That inherited
  hit helper independently requires profile `+0x11c == 0`, self `TF_DYING`, and
  other Unit/raw-mask contact before profile-drop/AddShutdownEvent. It has no
  friendly-air exemption, so that exemption is not a whole-call veto. Its
  own unconditional tail is `0x004fcc30`. The former CThing prefix did not
  establish its owner. Strict RTTI binds this shared handler to slot 39 of
  CDiveBomber (`0x005e123c`) and CGroundAttackAircraft (`0x005e2bcc`). Those
  classes inherit through CSmallAirUnit into CAirUnit, but CAirUnit's own table
  (`0x005e3778`) uses `0x004fcc30` for slot 39. The exact declaring class remains
  unproved, so its corrected name retains only the air-contact role.
- `0x004d1f90` checks `this+0x27c == 1`, resolves `wingopen` string `0x00624420`, calls `CMesh__FindAnimationIndexByName`, dispatches `this` vfunc `+0xf0`, and sets `this+0x27c = 2`.
- `0x004d1fd0` checks `this+0x27c == 4`, resolves `wingclose` string `0x0062442c`, calls `CMesh__FindAnimationIndexByName`, dispatches `this` vfunc `+0xf0`, and sets `this+0x27c = 3`.
- `CPlane` vtable `0x005e1930` slot 59 points to `0x004d2010`, while `CDiveBomber`, `CGroundAttackAircraft`, and `CBomber` use different slot-59 animation handlers.
- `0x004d2010` checks the linked object at `this+0x8` through vfunc `+0x58`, then advances `this+0x27c` from `2` to `4` by playing `attack` string `0x00624438` or from `3` to `1` by playing `launch` string `0x006243f8`.
- Raw caller instruction rows show `0x004d229f` and `0x004d2400` call the wing-open/wing-close helpers after loading `[ESI+0x8]` into `ECX`; those caller regions still have no recovered Ghidra function boundary.

## Boundary

The re-read complete bodies, with half-open extents, are:

| Body | Bytes | SHA-256 |
| --- | ---: | --- |
| `0x004d1f10..0x004d1f81` | 113 | `70d2d7d13cc1cb5ac40bc5c8d54cb8552742240bf7733c9ec44cf248ec5685ca` |
| `0x00403ba0..0x00403bec` | 76 | `e7e8b6987a232be7149a3d849871561ee2454b5cc9614bd03e94af9328b49638` |

Static retail-byte contracts establish the bounded gates above. The pinned
source has no `Plane.cpp`. Full actor layout, collision delivery, dying motion,
animation behavior, the retained raw caller boundaries, native runtime behavior
and rebuild parity remain open. The two names and nonrepeatable comments were
corrected through the [air-contact cohort](../../../ghidra/README.md#air-contact-shutdown-correction-2026-09-08).
Both ABI shapes, tags and bodies were preserved; the tracked checkpoint was not refreshed.
