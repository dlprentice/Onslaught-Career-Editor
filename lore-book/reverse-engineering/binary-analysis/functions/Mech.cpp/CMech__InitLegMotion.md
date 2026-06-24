# CMech__InitLegMotion

> Address: 0x0049f940 | Source: Mech.cpp (source file not present in `references/Onslaught/` snapshot)

## Status

- **Named in Ghidra:** Yes
- **Signature Set:** Yes (Wave436 headless apply/read-back, 2026-05-16)
- **Verified vs Source:** Partial static evidence only; the allocation path cites `C:\dev\ONSLAUGHT2\Mech.cpp` line `0x3d`, but the matching source body is not present in the current reference snapshot.

## Purpose

Saved static evidence shows this slot initializes the mech leg-motion component when a `LegMotion` animation is present. It allocates a `0xf0` `CMCMech` motion-controller object, stores the result at `this+0x70`, and passes initialization values from `init_context+0x3bc` into `CMCMech__SetParams`.

## Signature

```c
void __thiscall CMech__InitLegMotion(void * this, void * init_context);
```

`RET 0x4` confirms one stack argument after `this`.

## Observed Behavior

- Looks up the `LegMotion` animation string (`s_LegMotion_00623074`) through the model/mesh object at `this+0x30`.
- If the animation is missing, writes zero to `this+0x70` and returns.
- Allocates `0xf0` bytes from pool `0x1b` with Mech.cpp line evidence `0x3d`.
- Calls `CMCMech__Constructor`, stores the returned controller pointer at `this+0x70`, and calls `CMCMech__SetParams`.
- The observed parameter feed uses fields from `*(init_context+0x3bc)` at offsets `0x140`, `0x144`, `0x148`, `0x14c`, and `0x150`, plus constants `0.4` and `0.9`.

## Not Proven

Runtime leg animation behavior, walk/run/jump semantics, exact `CMech` or init-context layouts, exact source-body identity, local variable names/types, and rebuild parity remain unproven.

## Related Functions

- [CMech__InitCockpit](./CMech__InitCockpit.md)
- [CMech__InitTargeting](./CMech__InitTargeting.md)
- [../GroundUnit.cpp/_index.md](../GroundUnit.cpp/_index.md) - shared grounded-unit slot-9 initialization context
- [../MCMech.cpp.md](../MCMech.cpp.md) - `CMCMech` motion-controller context
