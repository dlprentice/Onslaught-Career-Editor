# CTree__dtor_base

| Property | Value |
| --- | --- |
| Address | `0x004f63c0` |
| Saved signature | `void __fastcall CTree__dtor_base(void * this)` |
| Wave | Wave520 CTree static re-audit |

Destructor body called by the existing scalar-deleting wrapper `CTree__scalar_deleting_dtor` at `0x004bfce0`. The body reinstalls CTree/CThing-adjacent vtables, frees the falling-tree data pointer at `this+0x48` through `CDXMemoryManager__Free` when present, clears the pointer, and delegates to `CThing__dtor_base`.

Evidence: xref from `0x004bfce3`, corrected saved name/signature/comment/tags, and post decompile read-back.

Claim boundary: static retail-binary evidence only. Destructor completeness, concrete CTree layout, runtime cleanup behavior, BEA patching, and rebuild parity remain unproven.
