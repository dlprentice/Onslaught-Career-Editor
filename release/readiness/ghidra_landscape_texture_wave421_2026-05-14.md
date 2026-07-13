# Ghidra LandscapeTexture Wave421 Static Correction

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 live correction closeout:** Historical record; `0x0048e950` comment correction. The original text below remains provenance rather than current semantic authority. It is superseded only where confirmed. Use the [closeout](../../reverse-engineering/binary-analysis/ghidra-full-reaudit-closeout-2026-07-13.md); final per-address decisions and exact before/after metadata are in `reverse-engineering/binary-analysis/ghidra-reviewed-correction-decisions-2026-07-13.jsonl` and `reverse-engineering/binary-analysis/ghidra-reviewed-correction-plan-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

Date: 2026-05-14

## Summary

Wave421 saved a focused static-Ghidra correction for fourteen existing `CLandscapeTexture` terrain-texture helpers. The pass hardened signatures, function comments, and tags for the texture lifetime, mip setup, update-queue, tile-copy, tile-update, RGB565 alpha-blend, and range-update functions from `0x0048e310` through `0x0048ef00`.

This is public-safe saved static retail-binary evidence. It is not runtime terrain rendering proof, not texture upload proof, not complete concrete class-layout recovery, not local-variable/type recovery, not complete vtable recovery, and not rebuild parity.

## Saved Ghidra Changes

| Address | Saved state | Evidence boundary |
| --- | --- | --- |
| `0x0048e310` | `CLandscapeTexture__FreeTexture` | Hardened as a `this` texture/surface release helper for field `+0x08`. |
| `0x0048e330` | `CLandscapeTexture__Constructor` | Hardened as the base constructor that calls `CIBuffer__Constructor`, installs vtable pointer `0x005dc1d8`, and clears state at `+0x2c`. |
| `0x0048e360` | `CLandscapeTexture__SetupMipLevel` | Hardened as the mip/edge setup helper that stores `+0x24/+0x28`, derives tile-edge/count fields, sets shared/static mode, and dispatches vtable slot `+0x04`. |
| `0x0048e430` | `CLandscapeTexture__ConstructorMip` | Hardened as the mip-texture constructor that calls the `CUMTexture` constructor-like path, installs vtable pointer `0x005dc1f0`, and clears `+0x2c/+0x40`. |
| `0x0048e450` | `CLandscapeTexture__Destructor` | Hardened as the cleanup path that frees update buffer `+0x40`, updates global count `0x006fabf8`, and releases shared state `0x006fabf4` when the count reaches zero. |
| `0x0048e4d0` | `CLandscapeTexture__Init` | Hardened as the mip/tile-set initializer that writes mask and size fields, allocates nonzero-mip update storage, and configures texture/device state. |
| `0x0048e610` | `CLandscapeTexture__Reset` | Hardened as the reset path that calls the texture reset/vfunc path, clears or fills dirty update state, or refreshes full tile range `0..63`. |
| `0x0048e7b0` | `CLandscapeTexture__ResetUpdateQueue` | Hardened as the global queue-cursor reset to base `0x006fa7d8`. |
| `0x0048e7c0` | `CLandscapeTexture__FlushUpdateQueue` | Hardened as the 20-byte record walker/compactor that calls `UpdateTile` for eligible entries. |
| `0x0048e880` | `CLandscapeTexture__QueueTileUpdate` | Hardened as the queue append/dedupe helper that derives mip/mask-adjusted texture coordinates and flushes near the queue cap. |
| `0x0048e950` | `CLandscapeTexture__CopyTileToTexture` | Hardened as the RGB565 tile-copy helper from the landscape buffer to shared/per-instance locked texture memory. |
| `0x0048ea80` | `CLandscapeTexture__UpdateTile` | Hardened as the tile-update helper that marks dirty state, blits terrain tile data, applies overlay alpha entries, copies/unlocks the tile, and refreshes device state for shared textures. |
| `0x0048ee00` | `CLandscapeTexture__BlendAlpha` | Hardened as an RGB565 alpha-mask blend helper using the `0x07e0f81f` parallel-channel mask. |
| `0x0048ef00` | `CLandscapeTexture__UpdateTileRange` | Hardened as an inclusive tile-range updater that blits tiles, applies linked overlay alpha entries, and copies the updated rect. |

Stuart's current source snapshot does not contain a matching `LandscapeTexture` source file, so this tranche relies on retail binary read-back, xrefs, callsites, constants, vtable-adjacent context, and existing function context. Source remains useful architecture evidence where present, but the Steam retail Ghidra database is the authority for these saved function boundaries, names, signatures, comments, and tags.

## Validation

- Focused probe tests passed: `py -3 tools\ghidra_landscape_texture_wave421_probe_test.py`.
- Python compile check passed for the Wave421 probe and tests.
- Pre-apply package-script probe failed as expected because the saved/read-back artifacts did not exist yet.
- Headless dry run: `updated=0 skipped=14 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`.
- Headless apply: `updated=14 skipped=0 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`, with `REPORT: Save succeeded`.
- Read-back exports verified `14` metadata rows, `14` tag rows, `30` xref rows, `1862` instruction rows, `14` decompile exports, and `64` vtable-adjacent rows.
- The initial xref read-back command used the wrong script name and failed before doing any mutation; the corrected serial rerun passed.
- Focused probe passed through npm: `cmd.exe /c npm run test:ghidra-landscape-texture-wave421`.
- Full static queue refreshed to `6043` functions, `1663` commented functions, `4380` commentless functions, `1861` undefined signatures, and `1817` `param_N` signatures.
- Current confirmation proxies are telemetry only: comment-backed `1663/6043 = 27.52%`; strict comment-plus-clean-signature `1600/6043 = 26.48%`.
- Actual live Ghidra project backup was verified at `[maintainer-local-ghidra-backup-root]\BEA_20260514_153419_post_wave421_landscape_texture_verified` with `19` files, `155159431` bytes, `HashDiffCount=0`, and `MissingCount=0`.

## Not Proven

- Runtime terrain texture rendering is not proven.
- Runtime GPU upload behavior is not proven.
- Runtime update-queue ordering and scheduling are not proven.
- Complete concrete `CLandscapeTexture` / `CUMTexture` / `CIBuffer` layouts are not proven.
- Exact local-variable names and recovered Ghidra data types remain open.
- The vtable-adjacent export remains provisional; it includes checked slots and `NO_FUNCTION_AT_POINTER` rows, not complete vtable recovery.
- BEA was not launched, patched, or debugged in this wave.
- This does not prove rebuild parity or game-behavior equivalence.
