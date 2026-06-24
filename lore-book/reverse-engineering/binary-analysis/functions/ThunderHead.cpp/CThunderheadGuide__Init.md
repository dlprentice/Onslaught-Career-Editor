# CThunderheadGuide__Init

> Address: 0x004f4e00 | Source: ThunderHead.cpp line evidence adjacent to guide factory

## Status

- **Named in Ghidra:** Yes, corrected by Wave519
- **Signature Set:** Yes, headless dry/apply/read-back verified on 2026-05-18
- **Evidence Grade:** Static retail Ghidra evidence only

## Signature

```c
void * __thiscall CThunderheadGuide__Init(
    void * this,
    void * owner_unit,
    int copied_state_0,
    int copied_state_4,
    int copied_state_8,
    int copied_state_c
);
```

## Behavior

`CThunderHead__CreateGuide` calls this after allocating a `0x30`-byte guide object. The call passes the allocated guide in `ECX`, the owner unit, and four dwords copied from owner offsets `0x1c`, `0x20`, `0x24`, and `0x28`.

The saved body calls `CGuide__ctor_base(owner_unit)`, installs vtable `0x005df8d4`, writes the copied state dwords to `this+0x20..this+0x2c`, and returns `this`. Instruction read-back confirms `RET 0x14`, matching five stack arguments after the `this` receiver.

## Claim Boundary

This does not prove the semantic meaning of the copied state dwords, concrete CThunderheadGuide layout, runtime targeting behavior, exact source-body identity, BEA patching, or rebuild parity.
