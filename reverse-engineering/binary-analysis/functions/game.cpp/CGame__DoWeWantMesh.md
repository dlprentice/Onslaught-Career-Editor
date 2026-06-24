# CGame__DoWeWantMesh

- **Address:** `0x00472570`
- **Saved signature:** `bool __thiscall CGame__DoWeWantMesh(void * this, char * mesh)`
- **Source context:** `references/Onslaught/game.cpp`, `CGame::DoWeWantMesh`

## Summary

Filters requested mesh names against the player cockpit and wingman mesh strings in the CGame settings block.

## Notes

- Wave 381 hardened the saved signature/comment/tags without changing the existing name.
- Read-back evidence includes `stricmp`, `mesh`, and field-offset context around `+0x22c`, `+0x25e`, and `+300`.

## Not Proven

- Runtime resource loading behavior is not proven by this static pass.
- Exact settings layout and local variable types remain open.
- BEA launch behavior, game patching, and rebuild parity are not proven.
