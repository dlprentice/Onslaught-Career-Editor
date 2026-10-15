# CFrontEnd__ReceiveButtonAction

- Address: 0x004669a0
- Status: Renamed (headless batch, Wave 377 read-back verified)
- Current saved signature: `void __thiscall CFrontEnd__ReceiveButtonAction(void * this, void * from_controller, int button, float action_value)`
- Source match: references/Onslaught/frontEnd.cpp (CFrontEnd::ReceiveButtonAction-style frontend button dispatch)

## Purpose

Receives a controller-originated frontend button action and dispatches it through frontend controller, cheat, modal, and page handling paths.

## Notes

Wave 377 corrected the older generic `VFuncSlot_03_004669a0` label. Static source/decompile/vtable evidence shows a controller pointer, button id, and action value stack shape, including player-0 capture on frontend menu select and cheat-button handling.

This is static evidence only. Runtime frontend input behavior remains unproven by this page.
