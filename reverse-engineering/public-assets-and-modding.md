# Public Assets And Modding Overview

Status: public-safe overview
Last updated: 2026-07-17

The project has full permission to use, modify, and distribute the original
game assets. The current toolkit source and portable app remain intentionally
small: they support resource analysis, copied-game workflows, and selected
asset use rather than tracking a bulk retail extraction.

## Public Boundary

- Retail executable patching and local analysis still require a legally
  obtained installation or verified copied specimen.
- Public changes may add curated original assets only when a live product or
  rebuild slice consumes them and attribution/provenance is explicit. Do not
  add bulk exports, saves, screenshots, copied executables, or raw proof bundles.
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

This establishes that the retail engine consumes the copied language table. It
does not establish arbitrary string growth, other languages, loose `.msl`
loading, texture replacement, AYA repacking, or a general mod-package format.

## Useful References

- [AYA Tags](quick-reference/aya-tags.md)
- [AYA Resource Chunks](quick-reference/aya-resource-chunks.md)
- [Command-Line Parameters](quick-reference/cli-parameters.md)
- [MSL Scripting Overview](game-assets/msl-scripting.md)
