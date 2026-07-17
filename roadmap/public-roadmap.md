# Public Roadmap

## Current priorities

1. Keep WinUI 3 polished and safe for saves, options, media, Lore, generated
   asset catalogs, and copied-game patching.
2. Keep save-byte preservation, copied-target enforcement, parsers, and guarded
   file publication in AppCore with focused regression coverage.
3. Grow the GPL, RE-informed rebuild through deterministic Core behavior and a
   presentation-only Godot client that needs no proprietary payload.
4. Improve useful copied-game patches and mods only to the level supported by
   byte checks and bounded runtime evidence.
5. Preserve unique Lore and reverse-engineering evidence without mirroring it
   into release notes, generated inventories, or parallel documentation trees.

## Explicit limits

- No mutation of the installed game or original `BEA.exe`.
- No synthesized career saves; edits start from a real baseline and preserve
  unknown bytes.
- No bundled retail assets, executables, saves, media, or debugger captures.
- No player-ready online Host/Join, public matchmaking, or native BEA netcode.
- No signed installer claim and no rebuild parity or strict clean-room claim.

Good first contributions are focused WinUI polish, AppCore correctness fixes,
patch metadata improvements, bounded documentation corrections, and deterministic
rebuild work within [`rebuild/PROVENANCE.md`](../rebuild/PROVENANCE.md).
