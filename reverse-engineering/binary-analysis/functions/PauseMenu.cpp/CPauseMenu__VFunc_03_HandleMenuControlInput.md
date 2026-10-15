# CPauseMenu__VFunc_03_HandleMenuControlInput

> Address: `0x004d15d0` | Source: PauseMenu.cpp (source file not present in `references/Onslaught/` snapshot)

## Status

- **Named in Ghidra:** Yes (Wave474 correction)
- **Signature Set:** Yes
- **Verified vs Source:** No source-body match; static retail-binary evidence only

## Signature

```c
void __thiscall CPauseMenu__VFunc_03_HandleMenuControlInput(
    void * this,
    void * control_context,
    int button_id,
    int button_context);
```

## Evidence

- Wave474 dry/apply/read-back set the saved signature above and removed a stale extra stack argument.
- Raw disassembly has multiple `RET 0x0c` exits, proving three stack arguments after `this`.
- The body gates input by the timestamp at `this+0x2c`, fetches the selected menu range through `this+0x14` and `this+0x24`, and forwards ordinary input through child menu-item vfunc slots `+0x08` and `+0x04`.
- Button `0x33` dispatches a selected nested item through `CPauseMenu__ButtonPressed`.
- Button `0x2e` takes the resume/range-reset paths, including `Controls__FindFirstFreeBindingSlot`, localized warning ids `0xe8`/`0xe9`, `CMenuItemRange__ResetIterator`, and frontend sound feedback.
- Vtable xref at `0x005de708` anchors this as a CPauseMenu vtable slot target.

## Not Proven

Exact control constant names, concrete `CPauseMenu` layout, exact source method identity, runtime UI behavior, BEA launch behavior, game patching, and rebuild parity remain unproven.
