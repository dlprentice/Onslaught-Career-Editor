# CTree__VFunc_28_CreateFallingTreeAfterDelay

| Property | Value |
| --- | --- |
| Address | `0x004f68e0` |
| Saved signature | `void __thiscall CTree__VFunc_28_CreateFallingTreeAfterDelay(void * this, float elapsed_time, void * other_thing, int unused_arg2, int unused_arg3)` |
| Wave | Wave520 CTree static re-audit |

Recovered CTree vtable slot-40 boundary. The body skips when `this+0x48` already has falling data, decrements timer/cooldown field `this+0x44` by `elapsed_time`, and when the timer crosses zero computes a normalized vector from this tree position to `other_thing+0x1c` before calling `CTree__CreateFallingTree`.

Evidence: CTree vtable `0x005dd9d8` slot 40 points to `0x004f68e0`, body returns with `RET 0x10`, callsite `0x004f699c` calls `CTree__CreateFallingTree`, and post boundary probe read-back names the function.

Claim boundary: static retail-binary evidence only. Exact virtual name, source identity, caller contract, runtime collision/destruction behavior, BEA patching, and rebuild parity remain unproven.
