# CUnit Ballistic Aim State Helpers

> Source File: Unit.cpp | Binary: BEA.exe
> Wave: 486 | Evidence: saved Ghidra metadata, decompile, xrefs, instruction rows, raw-caller rows, tags, and focused probe

## Functions

| Address | Name | Saved signature |
| --- | --- | --- |
| `0x004d36c0` | `CUnit__InitBallisticAimState` | `void __thiscall CUnit__InitBallisticAimState(void * this, float target_x, float target_y, float target_z, float target_w)` |
| `0x004d3730` | `CUnit__ComputeBallisticLaunchVelocity` | `void __fastcall CUnit__ComputeBallisticLaunchVelocity(void * this)` |

## Evidence

- `CUnit__InitBallisticAimState` uses ECX as `this`, consumes four stack dwords/floats, and ends with `RET 0x10`.
- When `this+0x254` is zero, it copies the target vector into `this+0x258..0x264`.
- It samples height through `CStaticShadows__SampleShadowHeightBilinear(&DAT_006fadc8, target_vector)` and overwrites `this+0x260` with the sampled height.
- It calls `CUnit__ComputeBallisticLaunchVelocity(this)`, then sets `this+0x254 = 1` and `this+0x250 = 0`.
- Raw no-function caller `0x005344f0` passes a 4-dword vector copied from a vfunc `+0x44` result.
- `CUnit__ComputeBallisticLaunchVelocity` uses only ECX/`this`.
- The compute helper derives yaw from target `this+0x258/0x25c` minus current position `this+0x1c/0x20`.
- It compares target height `this+0x260` against current height `this+0x24`.
- It reads a unit-data speed-like field at `this+0x164+0xb4`, scales by global `0x005d8584`, dispatches this vfunc `+0xb4`, and scans launch angles from `0x005d85c8` in steps of `0x005d8cb8`.
- It chooses the angle with the smallest horizontal-distance error, builds an orientation matrix through `CSquadNormal__BuildOrientationMatrixFromEuler`, and writes the scaled launch vector into `this+0x7c/0x80/0x84` plus `this+0x88`.

## Boundary

Static retail-binary evidence only. Exact constants, ballistic-state layout, source identity, runtime projectile/aim behavior, BEA launch behavior, game patching, and rebuild parity remain unproven.
