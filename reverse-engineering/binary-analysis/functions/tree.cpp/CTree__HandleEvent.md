# CTree__HandleEvent

| Property | Value |
| --- | --- |
| Address | `0x004f7050` |
| Saved signature | `void __thiscall CTree__HandleEvent(void * this, void * event)` |
| Wave | Wave520 CTree static re-audit |

Recovered CTree vtable slot-0 event-handler boundary. The event word at `event+0x04` is compared against `3000` and `3001`; the `3000` path calls `CTree__UpdateFallingTree`, the `3001` path dispatches through the object at `this+0x38` with argument `-1`, and other events delegate to `CThing__HandleEvent`.

Evidence: CTree vtable `0x005dd9d8` slot 0 points to `0x004f7050`, body returns with `RET 0x4`, callsite `0x004f7078` calls `CTree__UpdateFallingTree`, and post boundary probe read-back names the function.

Claim boundary: static retail-binary evidence only. Exact event names, `this+0x38` target type, runtime scheduler behavior, BEA patching, and rebuild parity remain unproven.
