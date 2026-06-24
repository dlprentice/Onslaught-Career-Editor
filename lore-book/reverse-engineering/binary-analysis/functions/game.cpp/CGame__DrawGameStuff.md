# CGame__DrawGameStuff

- **Address:** `0x004714c0`
- **Saved signature:** `void __thiscall CGame__DrawGameStuff(void * this)`
- **Source context:** `references/Onslaught/game.cpp`, `CGame::DrawGameStuff`

## Summary

Runs the source-parity game overlay/status pass after `CGame__DrawDebugStuff` from `CDXEngine__PostRender`. Retail read-back covers the PC screenshot/selection key branch, periodic FPS trace/status-buffer text, developer/game status overlays, encoded frontend cheat text rendering through `Frontend__XorWideTextBlock100BytesToScratch`, console status-history rendering, and game-over/objective overlay paths.

## Notes

- Wave 405 supersedes the stale `FrontendUpdate_CheatChecks` label.
- Saved via serialized headless dry/apply/read-back on 2026-05-14.
- Caller read-back shows `CDXEngine__PostRender` calling `CGame__DrawDebugStuff(&DAT_008a9a98)` and then `CGame__DrawGameStuff(&DAT_008a9a98)` at callsite `0x0053ef9b`.
- Target decompile still contains an internal `extraout_ECX` artifact around `CRT__AllocaProbe` / ECX preservation modeling; the caller read-back supplies the stronger `CGame` receiver evidence.
- Read-back evidence includes one metadata row, one tag row, one caller xref, `261` instruction rows, post-rename caller decompile text, and focused probe status `PASS`.

## Not Proven

- Runtime overlay behavior is not proven by this static pass.
- Exact `CGame` layout, local variable types, and PC key/input semantics remain open.
- This does not prove all cheat behavior, BEA launch behavior, game patching, or rebuild parity.
