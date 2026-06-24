# CGeneralVolume__InitRandomizedVelocityOffsets

> Address: `0x004247a0` | Source family: `CGeneralVolume`

## Status

- Saved Ghidra name/signature/comment: yes, Wave 321
- Saved signature: `void __thiscall CGeneralVolume__InitRandomizedVelocityOffsets(void * this, int randomRange)`
- Runtime behavior proof: not yet
- Exact source-file identity: not yet

## Summary

Initializes randomized velocity-offset fields at `this + 0x90`, `+0x94`, `+0x98`, and `+0x9c`, then zeroes phase-like field `+0xa0`. The callsite at `CGeneralVolume__RandomizeOffsets4B8_4C0` shows one explicit scalar argument, so the older saved extra float parameter was removed.

The helper also clamps the generated offset components against the observed `0.01` range token.

## Boundaries

- This is static Ghidra read-back and saved metadata only.
- It does not prove exact `CGeneralVolume` layout, random distribution semantics, runtime camera/noise behavior, tags, local names, or rebuild parity.
- It does not launch, patch, or mutate `BEA.exe`.
