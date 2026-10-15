# Public Assets And Modding Overview

Status: public-safe overview
Last updated: 2026-07-20

The current toolkit source tree and portable app do not include retail game
assets or converted copies. Resource analysis, copied-game workflows, and the
rebuild read a user's lawfully obtained installation as local input.

## Public Boundary

- Retail executable patching and local analysis still require a legally
  obtained installation or verified copied specimen.
- Public changes may add exact extraction/conversion recipes and bounded
  provenance, not retail asset payloads. Do not add bulk exports, saves,
  screenshots, copied executables, converted assets, or raw proof bundles.
- Patches must target copied executables or app-owned roots, not the installed
  Steam folder.
- Patch descriptions should say only what is byte-verified or runtime-proven.

## Proven Copied-Content Slice

The safe-copy product can replace one fixed-size English localization entry:
Level 100 `TUTORIAL_01`, text ID `4422830`, in
`data/language/english.dat`. AppCore verifies the supported Steam table hash
and original UTF-16 bytes, keeps the table and file length unchanged, writes a
backup, and records before/after hashes in the copied-profile manifest. A
controlled copied-game run rendered the unique replacement in Level 100.

The safe-copy product can also rebuild the supported
`data/resources/100_res_PC.aya` with one exact compiled mission-command change:
Level 100's initial `DisableFlightMode` call becomes `EnableFlightMode`.
AppCore verifies the original archive and decompressed payload hashes, changes
one byte in the `LevelScript` instruction stream, writes an original backup,
round-trips the four size-prefixed zlib members, and validates the exact
original/modified payload pair before launch. In controlled retail runs, the
same transform input reached the original rejection return with the clean
archive and the walker-to-jet state write with the changed archive. A
WinUI-created copy reproduced the accepted path with the runtime flight flag
set.

The retained implementation anchors are `LevelScript` instruction 33 (`CALL`,
opcode `24`) and its command byte at decompressed payload offset `3658889`:
descriptor `101` is `DisableFlightMode` and descriptor `100` is
`EnableFlightMode`. Retail observation distinguished the walker-to-jet state
write at `BEA.exe+0xA753` from the disabled-flight return at
`BEA.exe+0xA87D`. Stuart's `BattleEngine.cpp` supports the interpretation—the
walker morph returns while flight mode is disabled—but the copied Steam runtime
establishes the released behavior.

These slices establish that the retail engine consumes the copied language
table and this one rebuilt compiled mission archive. They do not establish
arbitrary string growth, other languages, loose `.msl` loading, a general
mission compiler/editor, texture replacement, general AYA repacking, or a mod
package format. The early-flight option deliberately bypasses Level 100's
training progression; it is not a claim about intended campaign behavior.

## Useful References

- [AYA Tags](quick-reference/aya-tags.md)
- [AYA Resource Chunks](quick-reference/aya-resource-chunks.md)
- [Command-Line Parameters](quick-reference/cli-parameters.md)
- [MSL Scripting Overview](game-assets/msl-scripting.md)
