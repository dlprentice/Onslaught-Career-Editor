# CMech__VFunc_09_InitGroundedMotionComponents_0049f820

> Address: 0x0049f820 | Source: retail `BEA.exe` static Ghidra evidence

## Status

- **Named in Ghidra:** `CMech__VFunc_09_InitGroundedMotionComponents_0049f820`
  (the earlier conservative label was `SharedGroundUnit__...`)
- **Signature Set:** Yes (Wave436 headless apply/read-back, 2026-05-16)
- **Owner Confidence:** `CMech` is the base-most evidenced vtable owner. A
  read-only MSVC RTTI walk of pristine
  `BEA.exe.original.backup` (SHA-256
  `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`)
  identifies `0x005e0684` as `CWarspite`, `0x005e3074` as `CMech`, and
  `CWarspite` as deriving from `CMech`. An exhaustive dword scan found
  `0x0049f820` only in those two slot-9 entries.

## Signature

```c
void __thiscall CMech__VFunc_09_InitGroundedMotionComponents_0049f820(void * this, void * init_context);
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

Vtable `0x005e0684` slot `118` points to `CWarspite__Create`. The earlier note
stopped there and treated the hierarchy as unknown. The pristine RTTI base
array now establishes `CWarspite -> CMech -> CGroundUnit -> CUnit`, so the
shared slot is ordinary inheritance rather than evidence against `CMech`
ownership.

## Not Proven

Exact source virtual name, complete class layout, local variable names/types,
runtime grounded-unit behavior, and rebuild parity remain unproven.

The historical filename is retained for link stability.
