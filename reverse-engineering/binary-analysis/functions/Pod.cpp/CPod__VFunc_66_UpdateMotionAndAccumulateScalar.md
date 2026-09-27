# CPOD Motion Scalar Vtable Override

Status: active function identity reference; earlier behavior claims retain their limits
Last updated: 2026-09-26 (virtual-method identity refresh; earlier behavioral evidence keeps its stated limits)
Summary: current method identities with preserved historical evidence and superseded labels.

> Source File: Pod.cpp | Binary: BEA.exe
> Wave: 486 | Evidence: saved Ghidra metadata, decompile, xrefs, CPOD RTTI/vtable rows, instruction rows, tags, and focused probe

## September 26 virtual-method identity correction

The [reviewed virtual-identity cohort](../../../ghidra/README.md#re-audit-thing-family-virtual-identities--september-26) updates the current labels
asserted below from pristine bytes and fixed RTTI slot identities. Earlier labels
in dated prose and filenames are retained aliases; the cohort manifest preserves
their exact mapping. This correction does not re-verify the rest of this note
or certify its prototypes or runtime behavior.

## Function

| Address | Name | Saved signature |
| --- | --- | --- |
| `0x004d3630` | `CPod__Move` | `void __fastcall CPod__Move(void * this)` |

## Evidence

- Wave486 corrected the stale `CEngine__AdvanceAndAccumulateMotionScalar` owner label.
- RTTI read-back resolves vtable `0x005dff8c` to `CPod`.
- CPOD vtable slot 66 at `0x005e0094` points to `0x004d3630`.
- The body calls `CUnit__UpdateMotionAttachmentsAndEffects(this)`.
- It dispatches `this` vfunc `+0xb4`.
- It adds the returned float-like scalar into `this+0x84`.

## Boundary

Static retail-binary evidence only. The current Stuart source snapshot does not contain a `CPod` source body. Exact slot contract, scalar meaning, concrete layout, runtime motion behavior, BEA launch behavior, game patching, and rebuild parity remain unproven.
