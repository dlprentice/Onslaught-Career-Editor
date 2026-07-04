# WinUI Offline Lore Pack Plan

Status: implemented for current ZIP package shape
Last updated: 2026-07-04

The published `v1.0.7` portable app ZIP ships a short `lore-book/` entry point
plus a generated `lore-pack/` content pack. This avoids the raw full
`lore-book/` tree because the full mirror has long reverse-engineering and proof
filenames that can exceed Windows Explorer `Extract All` path limits under
normal Downloads folders.

The desired shape is broad offline Lore reading inside the app through a
generated content pack, not raw long filenames.

## Target Shape

- Keep `lore-book/BOOK.md` and a short human entry point in the ZIP.
- Add the generated offline pack `lore-pack/onslaught-lore.v1.jsonl` plus
  `lore-pack/onslaught-lore.v1.index.json`.
- Store each public-safe Markdown/TXT Lore document with a
  stable ID, title, original logical path, hash, byte range or short entry path,
  and outbound-link metadata.
- Resolve internal links through AppCore document IDs so packed documents stay
  in the WinUI reader.
- Keep source paths visible as metadata only; do not use long logical paths as
  extracted ZIP filenames.

## Acceptance

- The app can search and open tracked public-safe Markdown/TXT Lore documents
  offline.
- Internal packed-document links stay inside the reader.
- GitHub or external links are visibly identified as source/external links.
- ZIP path safety still passes with default Explorer extraction-folder
  accounting.
- Package probes reject hard payloads, stale all-in-app copy, and raw deep
  `lore-book/` mirror leakage.
- Search is debounced or asynchronous enough that typing does not visibly block
  the WinUI thread.

## Current Implementation

- `tools/winui_lore_pack_builder.py` builds/checks the deterministic JSONL plus
  index pack from tracked public-safe `lore-book/` Markdown/TXT files. Non-packed
  source/data references are externalized to repository source/search links.
- `tools/winui_zip_package_probe.py` stages `lore-pack/` beside the short
  `lore-book/` entry point, verifies schema and hashes, rejects payload-like
  pack content, keeps Explorer path checks, and rejects raw deep `lore-book/`
  mirror leakage.
- `LoreBrowserService` prefers the content pack when present and falls back to
  the existing `lore-book/BOOK.md` file reader when the pack is absent.
- AppCore and package-probe coverage includes above-root link rejection, encoded
  traversal cases, root-contained file fallback, schema/hash checks, and public
  safe error wording. This is source/package validation, not runtime UI proof or
  broad release publication authority.

## Non-Goals

- Do not bundle game binaries, copied executables, saves, extracted assets,
  screenshots, raw CDB logs, or full Ghidra databases/backups.
- Do not add SQLite or another native storage dependency unless JSONL/index
  search is measured and insufficient.
- Do not replace the repo source tree; this is only the downloadable app ZIP's
  offline reader payload.
