# CThunderheadGuide__VFunc_03_004f4e40

> Address: 0x004f4e40 | Recovered by Wave519 | Vtable: `0x005df8d4` slot 3

## Status

- **Named in Ghidra:** Conservative boundary name, exact virtual method name unknown
- **Signature Set:** Yes, headless dry/apply/read-back verified on 2026-05-18
- **Evidence Grade:** Static retail Ghidra boundary and behavior evidence only

## Signature

```c
void __fastcall CThunderheadGuide__VFunc_03_004f4e40(void * this);
```

## Behavior

CThunderheadGuide vtable `0x005df8d4` slot 3 points to `0x004f4e40`. Wave519 created the missing function boundary there and verified that the function starts with an ECX-based prologue (`SUB ESP, 0x48`; `MOV ESI, ECX`) and returns at `0x004f51b4`.

Current decompile/read-back evidence shows:

- owner pointer access through `this+0x18`;
- an owner flag gate at owner offset `0x2c` bit `0x4`;
- fallback owner virtual dispatch through slot `+0x100`;
- vector/state updates around owner offsets `0x14c..0x158`;
- terrain/guide-state branching that logs `"ERROR - Unknown Terrain guide st"` for unexpected state values;
- early exits for missing guide state, small distance, and deploy animation state.

The following address `0x004f51c0` remains outside this function and starts a separate non-function data-initializer block, which guards the recovered boundary end.

## Claim Boundary

The exact virtual name, concrete guide/owner layouts, targeting or firing semantics, runtime behavior, source-body identity, BEA patching, and rebuild parity remain unproven.
