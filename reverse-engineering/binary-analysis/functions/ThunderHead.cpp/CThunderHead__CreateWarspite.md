# CThunderHead__CreateWarspite

Status: active static function note; saved caller name remains provisional
Last updated: 2026-09-12
Summary: ThunderHead allocates the shared CUnitAI controller; the older Warspite-specific attribution is withdrawn.
Source File: ThunderHead.cpp line 43, absent from the pinned partial source | Binary: BEA.exe
Specimen: `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.

| Address | Current saved name | Saved signature |
| --- | --- | --- |
| `0x004f4830` | `CThunderHead__CreateWarspite` | `void __thiscall CThunderHead__CreateWarspite(void * this, void * init_context)` |

The saved caller name remains unchanged by the initializer correction. Its
older `warspite`/`mWarspite` aliases were inferred labels, not recovered fields
or proof of a CWarspite object. The callee is now correctly saved as
`CUnitAI__Init`; see the [shared initializer correction](../../../ghidra/README.md#unitai-initializer-and-event-arguments-2026-09-12).

## Instruction-backed behavior

Fresh inspection of `[0x004f4830,0x004f4897)` found:

- The caller preserves its ECX receiver in ESI and submits allocation size
  `0x60`, pool `0x16`, source-string pointer `0x00633240` and line `0x2b` to
  `CDXMemoryManager__Alloc` at call site `0x004f4859`.
- If allocation succeeds, `0x004f486e..0x004f4876` pushes the original
  `init_context`, then the owner ESI, and puts the allocation in ECX before
  calling `CUnitAI__Init` at `0x004fe710`.
- The caller performs no subclass-vtable overwrite. It stores the returned
  pointer at owner `+0x13c` (`0x004f4883`); allocation failure stores zero.
- The original SEH chain is restored and `0x004f4894` executes `RET4`.

The initializer's table is independently identified by RTTI as CUnitAI. These
instructions therefore support shared-controller allocation, not the old
Warspite-specific classification. They do not establish complete ThunderHead
behavior, a source-compatible object layout or runtime combat parity.

## Retained history

Wave519 reported the saved caller signature and slot-2 ownership in ThunderHead
table `0x005e11b0` on May 18. The September 12 caller inspection above is fresh;
that wider vtable census was not rerun. Earlier illustrative pseudocode and
unsupported Warspite-specific behavior claims remain recoverable from Git.
