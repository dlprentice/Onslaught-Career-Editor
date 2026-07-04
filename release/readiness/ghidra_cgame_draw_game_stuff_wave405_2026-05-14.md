# Ghidra CGame DrawGameStuff Correction - 2026-05-14

Status: public-safe static Ghidra evidence note

Wave405 corrected the saved Ghidra metadata for `0x004714c0` from the stale `FrontendUpdate_CheatChecks` label to `CGame__DrawGameStuff`. Stuart source CGame::DrawGameStuff is the source-alignment anchor for the corrected owner/name. This is a serialized static Ghidra correction/read-back wave only.

| Address | Previous saved label | Saved state | Static evidence summary |
| --- | --- | --- | --- |
| `0x004714c0` | `FrontendUpdate_CheatChecks` | `void __thiscall CGame__DrawGameStuff(void * this)` | Source and binary evidence align with Stuart source `CGame::DrawGameStuff`: `CDXEngine__PostRender` calls `CGame__DrawDebugStuff(&DAT_008a9a98)` and then calls this function with `ECX = DAT_008a9a98` at `0x0053ef9b`. Retail read-back covers the PC screenshot/selection key branch, periodic FPS trace/status-buffer text, developer/game status overlays, encoded frontend cheat text rendering through `Frontend__XorWideTextBlock100BytesToScratch`, console status-history rendering through `CConsole__RenderStatusHistoryOverlay`, and game-over/objective overlay paths. |

## Source Boundary

Stuart source is useful here because `CDXEngine::PostRender` explicitly calls `GAME.DrawDebugStuff()` and then `GAME.DrawGameStuff()`, matching the retail caller order after the saved rename. Retail still remains the authority for exact instructions and differences: the read-back records the retail key token `0x42`, retail globals, and retail helper calls, so this wave does not overwrite retail evidence with source-only assumptions.

## Validation

- `ApplyCGameDrawGameStuffWave405.java` dry run passed with `updated=0 skipped=1 renamed=0 would_rename=1 missing=0 bad=0`.
- `ApplyCGameDrawGameStuffWave405.java` apply run passed with `updated=1 skipped=0 renamed=1 would_rename=0 missing=0 bad=0` and `REPORT: Save succeeded`.
- Read-back verified `1` metadata row, `1` tag row, `1` caller xref from `CDXEngine__PostRender` at `0x0053ef9b`, `261` instruction rows, and post-rename caller decompile text showing `CGame__DrawDebugStuff(&DAT_008a9a98)` followed by `CGame__DrawGameStuff(&DAT_008a9a98)`.
- Refreshed queue telemetry reports `6028` functions, `1558` commented functions, `4470` commentless functions, `1909` undefined signatures, and `1858` `param_N` signatures.
- Current confirmation proxies are telemetry only: comment-backed `1558/6028 = 25.85%`, strict clean-signature `1496/6028 = 24.82%`.
- The actual live Ghidra project backup was verified at `[maintainer-local-ghidra-backup-root]\BEA_20260514_063725_post_wave405_cgame_draw_game_stuff_verified` with `19` files, `154798983` bytes, and `HashDiffCount=0`.

## Claim Boundary

This note does not prove exact CGame layout, does not prove runtime overlay behavior, does not prove all cheat behavior, does not prove rebuild parity, and does not involve launching or patching `BEA.exe`.
