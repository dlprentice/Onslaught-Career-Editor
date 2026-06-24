# Deprecated: CGame__HasNearbyHostileWithinRadius

- **Address:** `0x004eb130`
- **Current saved name:** `CStart__Available`
- **Source context:** `references/Onslaught/game.cpp` respawn fallback flow plus Wave510 retail Ghidra read-back

## Summary

Wave510 corrected this stale `CGame` owner label to `CStart__Available`. `CGame__RespawnPlayer` calls this helper during fallback start-point selection; the function operates on the `CStart` object in `ECX`, queries `CMapWho` near the start position, rejects active hostile/non-excluded owners, and returns true when the start is clear.

## Notes

- Recovered and semantically renamed via headless decompile + batch-rename workflow (2026-02-25).
- Superseded by Wave510 on 2026-05-17 after serialized dry/apply/read-back and focused probe verification.
- Canonical current documentation lives in [`../SpawnPoint.cpp/_index.md`](../SpawnPoint.cpp/_index.md).
