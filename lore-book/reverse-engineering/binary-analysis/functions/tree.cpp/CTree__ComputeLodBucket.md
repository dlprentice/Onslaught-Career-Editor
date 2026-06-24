# CTree__ComputeLodBucket

| Property | Value |
| --- | --- |
| Address | `0x004f6430` |
| Saved signature | `int __fastcall CTree__ComputeLodBucket(void * this)` |
| Wave | Wave520 CTree static re-audit |

Computes a clamped tree LOD bucket. The helper dispatches through the render/resource object at `this+0x08` virtual slot `+0x54`, reads resource floats at `+0x10` and `+0x14`, keeps the larger/non-NaN value, multiplies by the scale constant at `0x005d8be8`, rounds to a byte, and clamps the result to bucket `6`.

Evidence: call from `CEngine__InitDamageSystem` at `0x0044a15e`, post metadata/tag/decompile read-back, and Wave520 probe coverage.

Claim boundary: static retail-binary evidence only. Exact LOD field names, resource-object type, runtime tree LOD behavior, BEA patching, and rebuild parity remain unproven.
