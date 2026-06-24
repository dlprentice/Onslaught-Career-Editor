# CGame__IsRunningResources

- **Address:** `0x00472650`
- **Saved signature:** `bool __fastcall CGame__IsRunningResources(void * this)`
- **Source context:** `references/Onslaught/game.cpp`, `CGame::IsRunningResources`

## Summary

Compares the current CGame level field with the last resource-loaded level global `DAT_006317cc`.

## Notes

- Wave 381 hardened the saved signature/comment/tags without changing the existing name.
- Read-back evidence includes the `DAT_006317cc` global read and CGame field read at `this+0x30`.

## Not Proven

- Runtime resource loading behavior is not proven by this static pass.
- Exact CGame layout names and local variable types remain open.
- BEA launch behavior, game patching, and rebuild parity are not proven.
