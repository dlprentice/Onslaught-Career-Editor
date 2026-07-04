# Ghidra CGame IsMultiplayer Correction - 2026-05-14

Status: public-safe static Ghidra evidence note

Wave406 corrected the saved Ghidra metadata for `0x004725d0` from the stale `CExplosionInitThing__CheckValueRange_852_899` label to `CGame__IsMultiplayer`. Stuart source CGame::IsMultiplayer is the source-alignment anchor for the corrected owner/name. This is a serialized static Ghidra correction/read-back wave only.

| Address | Previous saved label | Saved state | Static evidence summary |
| --- | --- | --- | --- |
| `0x004725d0` | `CExplosionInitThing__CheckValueRange_852_899` | `int __thiscall CGame__IsMultiplayer(void * this)` | Source and binary evidence align with Stuart source `CGame::IsMultiplayer`: source checks `mCurrentlyRunningLevel >849` and `mCurrentlyRunningLevel < 900`, while retail read-back checks the current-level field at `CGame+0x2a0` through the same `850..899` range. Retail xrefs show cross-cutting callers that pass the `CGame` singleton, including `CCareer__DoesBaseThingExist`, `CDXEngine__Render`, `CDXCompass__Render`, tactical radar/objective/HUD helpers, sound, landscape, BattleLine, BattleEngine init, monitor, and pause-menu contexts. |

## Source Boundary

Stuart source is useful here because `CGame::IsMultiplayer` contains the distinctive `mCurrentlyRunningLevel >849 && mCurrentlyRunningLevel < 900` predicate. Retail still remains the authority for exact instructions and differences: the read-back records the retail `CGame+0x2a0` field access, the `0x351 < level < 900` gate, and the caller graph that reaches the helper from multiple subsystems.

## Validation

- `ApplyCGameIsMultiplayerWave406.java` dry run passed with `updated=0 skipped=1 renamed=0 would_rename=1 missing=0 bad=0`.
- `ApplyCGameIsMultiplayerWave406.java` apply run passed with `updated=1 skipped=0 renamed=1 would_rename=0 missing=0 bad=0` and `REPORT: Save succeeded`.
- Read-back verified `1` metadata row, `1` tag row, `54` xref rows, `81` instruction rows, and the post-rename decompile text with the `CGame+0x2a0` / `850..899` predicate.
- Refreshed queue telemetry reports `6028` functions, `1559` commented functions, `4469` commentless functions, `1909` undefined signatures, and `1857` `param_N` signatures.
- Current confirmation proxies are telemetry only: comment-backed `1559/6028 = 25.86%`, strict clean-signature `1497/6028 = 24.83%`.
- The actual live Ghidra project backup was verified at `[maintainer-local-ghidra-backup-root]\BEA_20260514_070751_post_wave406_cgame_is_multiplayer_verified` with `19` files, `154798983` bytes, and `HashDiffCount=0`.

## Claim Boundary

This note does not prove exact CGame field layout, does not prove world-type semantics, does not prove runtime multiplayer behavior, does not prove rebuild parity, and does not involve launching or patching `BEA.exe`.
