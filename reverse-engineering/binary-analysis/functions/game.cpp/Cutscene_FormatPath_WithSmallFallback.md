# Cutscene_FormatPath_WithSmallFallback

- **Address:** `0x0046d810`
- **Status:** Renamed, signature set, commented in Ghidra (read-back verified)
- **Signature:** `void Cutscene_FormatPath_WithSmallFallback(char *dst)`
- **Source Alignment:** Retail helper inferred from cutscene playback code paths (`references/Onslaught/game.cpp` `RunIntroFMV` / `RunOutroFMV` style naming logic).

## Behavior

1. Formats `dst` as `cutscenes\\%02d`.
2. Builds a probe path `data\\video\\<dst>.vid`.
3. If the file probe fails, rewrites `dst` to `cutscenes\\%02d_small`.
4. Leaves `dst` as the full path variant when the probe succeeds.

## Why It Matters

- This helper normalizes retail fallback behavior between full-size and `_small` cutscene assets.
- It explains why cutscene-award/playback helpers around `0x0046d890` and `0x0046d9f0` can run on reduced asset sets without hard-failing the playback path.

## Related Functions

- `CGame__RunIntroFMV` (`0x0046d890`)
- `CGame__RunOutroFMV` (`0x0046d9f0`)

## Verification Notes

- Rename/signature/comment were applied via GhydraMCP and verified with `functions_get(0x0046d810)`.
- This is metadata-only RE (no instruction-byte patching).
