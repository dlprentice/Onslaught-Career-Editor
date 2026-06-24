# SharedGroundUnit__VFunc_09_InitGroundedMotionComponents_0049f820

> Address: 0x0049f820 | Source: retail `BEA.exe` static Ghidra evidence

## Status

- **Named in Ghidra:** Yes (Wave436)
- **Signature Set:** Yes (Wave436 headless apply/read-back, 2026-05-16)
- **Owner Confidence:** Shared/conservative. Vtable tables `0x005e0684` and `0x005e3074` both point slot `9` here, so this page avoids assigning a single concrete class owner.

## Signature

```c
void __thiscall SharedGroundUnit__VFunc_09_InitGroundedMotionComponents_0049f820(void * this, void * init_context);
```

`RET 0x4` confirms one stack argument after `this`.

## Observed Behavior

- Calls `CGroundUnit__Init(this, init_context)` at entry.
- Invokes vtable `+0xf0` with observed arguments `(1, 1, 0)`.
- Reads `*(init_context+0x3bc)` and copies observed values into `this+0x12c`, `this+0x130`, `this+0x134`, `this+0x100`, `this+0x104`, and `this+0x108`.
- Invokes vtable slots `117`, `118`, and `119` through offsets `+0x1d4`, `+0x1d8`, and `+0x1dc` around the component initialization sequence.
- Clears `this+0x264` and `this+0x268`, computes `this+0x260` from an init-context float minus `this+0x24`, then resolves a named child through `CDestroyableSegment__FindChildByNameI`.

## Vtable Evidence

| Vtable | Slot | Pointer |
| --- | ---: | --- |
| `0x005e0684` | `9` | `0x0049f820` |
| `0x005e3074` | `9` | `0x0049f820` |
| `0x005e0684` | `117` | `CMech__InitLegMotion` |
| `0x005e3074` | `117` | `CMech__InitLegMotion` |
| `0x005e3074` | `118` | `CMech__InitCockpit` |
| `0x005e0684` | `119` | `CMech__InitTargeting` |
| `0x005e3074` | `119` | `CMech__InitTargeting` |

Vtable `0x005e0684` slot `118` points to `CWarspite__Create`, so the table is not treated as a pure `CMech` table.

## Not Proven

Exact concrete owner, source virtual name, class layout, local variable names/types, runtime grounded-unit behavior, and rebuild parity remain unproven.
