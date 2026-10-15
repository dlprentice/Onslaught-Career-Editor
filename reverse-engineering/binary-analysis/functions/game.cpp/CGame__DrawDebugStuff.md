# CGame__DrawDebugStuff

- **Address:** `0x00470650`
- **Saved signature:** `void __fastcall CGame__DrawDebugStuff(void * this)`
- **Source context:** `references/Onslaught/game.cpp`, `CGame::DrawDebugStuff`

## Summary

Draws the source-parity game debug overlay path: render-state reset, selected squad/unit debug hooks, heap/memory pressure text, and selected squad/unit text labels.

## Notes

- Wave 381 supersedes the older `CGame__RenderDebugMemoryAndSelectionInfo` label.
- Saved via serialized headless dry/apply/read-back on 2026-05-13.
- Read-back evidence includes calls to `CGame__ResetRenderStateForWorldRender`, selected squad/unit text tokens, and CGame field reads around `+0xa04` and `+0x9f8`.

## Not Proven

- Runtime debug overlay behavior is not proven by this static pass.
- Concrete `CGame` structure layout, locals, and source line identity remain open.
- BEA launch behavior, game patching, and rebuild parity are not proven.
