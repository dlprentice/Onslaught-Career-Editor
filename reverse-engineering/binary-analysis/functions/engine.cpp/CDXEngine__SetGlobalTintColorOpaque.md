# CDXEngine__SetGlobalTintColorOpaque

> Address: `0x004d1710` | Source: retail-binary static evidence only

## Status

- **Named in Ghidra:** Yes
- **Signature Set:** Yes (Wave482 hardening)
- **Verified vs Source:** No source-body identity; caller/global write evidence only

## Signature

```c
void __cdecl CDXEngine__SetGlobalTintColorOpaque(uint tint_payload);
```

## Evidence

- Wave482 kept the existing name but replaced the stale `param_1` signature with `uint tint_payload`.
- The body reads the one stack argument, writes it to global `0x0082b494`, forces companion global `0x0082b4ec` to `0xff`, and returns.
- Exact global-operand search found only those two direct exact-address writes for `0x0082b494` and `0x0082b4ec`.
- Confirmed callers push small constants: `OptionsTail_Read` pushes `0xf6`, `CD3DApplication__Initialize3DEnvironment` pushes `0xe5` / `0xe6`, and render cleanup paths in `CRenderQueue__RenderAll`, `CDXEngine__RenderMultipassLayerA`, and `CDXEngine__RenderMultipassLayerB` push `0xe7`.
- The broader nearby global-prefix scan shows adjacent pause-menu globals around `0x0082b490` / `0x0082b4e8`, but Wave482 does not claim the exact layout or consumer for `0x0082b494` / `0x0082b4ec`.

## Not Proven

Exact global layout, palette/color packing, consumer path, runtime visual behavior, source identity, BEA launch behavior, game patching, and rebuild parity remain unproven.
