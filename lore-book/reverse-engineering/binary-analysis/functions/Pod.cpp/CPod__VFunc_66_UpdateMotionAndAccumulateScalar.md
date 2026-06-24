# CPOD Motion Scalar Vtable Override

> Source File: Pod.cpp | Binary: BEA.exe
> Wave: 486 | Evidence: saved Ghidra metadata, decompile, xrefs, CPOD RTTI/vtable rows, instruction rows, tags, and focused probe

## Function

| Address | Name | Saved signature |
| --- | --- | --- |
| `0x004d3630` | `CPod__VFunc_66_UpdateMotionAndAccumulateScalar` | `void __fastcall CPod__VFunc_66_UpdateMotionAndAccumulateScalar(void * this)` |

## Evidence

- Wave486 corrected the stale `CEngine__AdvanceAndAccumulateMotionScalar` owner label.
- RTTI read-back resolves vtable `0x005dff8c` to `CPod`.
- CPOD vtable slot 66 at `0x005e0094` points to `0x004d3630`.
- The body calls `CUnit__UpdateMotionAttachmentsAndEffects(this)`.
- It dispatches `this` vfunc `+0xb4`.
- It adds the returned float-like scalar into `this+0x84`.

## Boundary

Static retail-binary evidence only. The current Stuart source snapshot does not contain a `CPod` source body. Exact slot contract, scalar meaning, concrete layout, runtime motion behavior, BEA launch behavior, game patching, and rebuild parity remain unproven.
