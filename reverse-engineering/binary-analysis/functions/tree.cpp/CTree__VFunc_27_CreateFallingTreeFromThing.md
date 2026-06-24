# CTree__VFunc_27_CreateFallingTreeFromThing

| Property | Value |
| --- | --- |
| Address | `0x004f6aa0` |
| Saved signature | `void __thiscall CTree__VFunc_27_CreateFallingTreeFromThing(void * this, void * other_thing, int unused_context)` |
| Wave | Wave520 CTree static re-audit |

Recovered CTree vtable slot-39 boundary. The body checks `other_thing` flags at `+0x34`, skips when falling-tree data already exists at `this+0x48`, computes a vector between this tree position and `other_thing+0x1c`, applies an alternate distance threshold when flag `0x01000000` is set, normalizes the vector, and calls `CTree__CreateFallingTree` when the threshold gate passes.

Evidence: CTree vtable `0x005dd9d8` slot 39 points to `0x004f6aa0`, body returns with `RET 0x8`, callsite `0x004f6b6f` calls `CTree__CreateFallingTree`, and post boundary probe read-back names the function.

Claim boundary: static retail-binary evidence only. Exact virtual name, caller contract, runtime collision/destruction behavior, BEA patching, and rebuild parity remain unproven.
