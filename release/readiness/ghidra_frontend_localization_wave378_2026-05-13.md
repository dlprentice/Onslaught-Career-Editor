# Ghidra Frontend Localization Wave378 Evidence - 2026-05-13

Status: public-safe saved Ghidra evidence note

## Summary

Wave 378 is a serialized static Ghidra correction tranche for seven frontend localization/text helpers. It keeps the two already-valid `CFrontEnd` level/episode resolvers, corrects stale `CUnitAI` ownership on frontend text helpers, corrects a stale fallback text-id label to a briefing color helper, and corrects save-game-specific text-token ownership to broader `FrontEndText` ownership.

This note is public-safe. It records addresses, names, signatures, counts, and proof boundaries only. Raw decompile/read-back exports and generated proof JSON remain under ignored private artifact roots.

## Saved Targets

| Address | Saved Ghidra state | Evidence boundary |
| --- | --- | --- |
| `0x00469c20` | `short * __cdecl CFrontEnd__ResolveEpisodeNameTextByIndex(int episode_index)` | Return/signature hardening for episode index to localized text with `Unnamed Episode` fallback. |
| `0x00469cf0` | `int __cdecl CFrontEnd__ResolveLevelNameTextIdByCode(int level_code)` | Parameter/comment hardening for level/world code to localized text-id mapping; unmapped returns `-1`. |
| `0x0046a1f0` | `short * __cdecl FrontEndText__GetLevelNameTextAfterCode(int level_code, int after_index)` | Corrects stale `CUnitAI` ownership; callsite evidence shows returned wide text consumed by briefing render code. |
| `0x0046a210` | `uint __cdecl FrontEnd__GetBriefingLevelListTextColor(void)` | Corrects stale fallback text-id helper label; body returns `0xffffdf5f` and caller masks/shifts it as a draw-color component. |
| `0x0046a220` | `short * __cdecl FrontEndText__GetMultiplayerLevelDescriptionByType(int level_type)` | Corrects stale `CUnitAI` ownership; resolves multiplayer level-description text and has an ASCII fallback path. |
| `0x0046a2a0` | `short * __cdecl FrontEndText__GetLocalizedOrFallbackTextByToken(int text_token)` | Corrects save-game-specific ownership; xrefs show broad frontend modal, config, directory, keyboard, save/load, and level-select use. |
| `0x0046b1e0` | `short * __cdecl FrontEndText__GetAsciiFallbackTextByToken(int text_token)` | Corrects save-game-specific ownership and return type for the shared ASCII fallback text-token resolver. |

## Validation

Serialized dry/apply used `tools/ApplyFrontendLocalizationWave378.java`. The dry run reported `updated=0 skipped=7 renamed=0 would_rename=5 missing=0 bad=0`; the apply run reported `updated=7 skipped=0 renamed=5 would_rename=0 missing=0 bad=0` and `REPORT: Save succeeded`.

Read-back verified `7` metadata rows, `7` decompile exports, `104` xref rows, `3227` instruction rows, `7` tag rows, and `363` callsite-instruction rows. The focused probe reports `PASS` for `7` targets, with `13` xref evidence hits, `11` instruction evidence hits, and `6` callsite evidence hits.

The refreshed whole-database queue reports `6026` functions, `1378` commented functions, `4648` commentless functions, `1939` undefined signatures, and `1946` `param_N` signatures. Current confirmation proxies are telemetry only: comment-backed `1378/6026 = 22.87%`, strict clean-signature `1316/6026 = 21.84%`.

The actual live Ghidra project backup was verified on the out-of-repo `[maintainer-local-backup-volume]` backup drive with label `BEA_20260513_142838_post_wave378_frontend_localization_verified`, `19` files, `153619335` bytes, and `HashDiffCount=0`.

## Not Proven

- Runtime frontend localization, briefing rendering, color rendering, fallback-toggle behavior, or multiplayer frontend behavior.
- Exact class layouts, local variable types, structure recovery, or source method identity for every branch.
- BEA launch behavior, game patching, packaged WinUI behavior, or rebuild parity.
