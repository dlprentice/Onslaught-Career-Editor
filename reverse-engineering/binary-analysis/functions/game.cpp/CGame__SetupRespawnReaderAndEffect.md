# Deprecated: CGame__SetupRespawnReaderAndEffect

- **Address:** `0x004eaf20`
- **Current saved name:** `CStart__SpawnBattleEngine`
- **Source context:** `references/Onslaught/game.cpp` respawn fallback flow plus Wave510 retail Ghidra read-back

## Summary

Wave510 corrected this stale `CGame` owner label to `CStart__SpawnBattleEngine`. `CGame__RespawnPlayer` calls this helper during fallback start-point selection; the function operates on the `CStart` object in `ECX`, creates OID type `3`, binds it through the start's active-reader cell, initializes the BattleEngine from embedded start init data, and optionally spawns the ground/air respawn particle effect.

## Notes

- Recovered and semantically renamed via headless decompile + batch-rename workflow (2026-02-25).
- Superseded by Wave510 on 2026-05-17 after serialized dry/apply/read-back and focused probe verification.
- Canonical current documentation lives in [`../SpawnPoint.cpp/_index.md`](../SpawnPoint.cpp/_index.md).
