# CPauseMenu__Render

> Address: `0x004d11d0` | Source: `DXEngine.cpp:1371` caller alignment; PauseMenu.cpp source body is not present in `references/Onslaught/`

## Status

- **Named in Ghidra:** Yes (Wave481 correction)
- **Signature Set:** Yes
- **Verified vs Source:** Caller-aligned only; static retail-binary evidence

## Signature

```c
short * __thiscall CPauseMenu__Render(void * this);
```

## Evidence

- Wave481 corrected the stale `CEngine__RenderOverlayAndMenuTransitions` owner to `CPauseMenu__Render`.
- `CDXEngine__PostRender` calls this body with `DAT_008a9d8c` at the source-aligned `GAME.GetPauseMenu()->Render()` point in `references/Onslaught/DXEngine.cpp:1371`.
- `CFEPOptions__Update` also calls this body through `g_pOptionsContext`; `CFEPOptions__EnsureOptionsContext` allocates that context and initializes it through `PauseMenu__Init`.
- The body sets UI render state, handles pause/menu fade timing, draws the black fade and paired transition sprites, renders the selected `CMenuItemRange`, optionally renders child/prompt ranges, and restores render state / mouse cursor drawing.
- Return-type evidence is tied to `CMenuItemRange__Render`: the active range render returns the range title text pointer, and this function returns it only when the active range index is nonzero.

## Not Proven

Concrete `CPauseMenu` layout, exact source body identity, runtime pause/options UI behavior, BEA launch behavior, game patching, and rebuild parity remain unproven.
