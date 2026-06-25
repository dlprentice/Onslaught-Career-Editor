# WinUI Offline Lore Pack Plan

Status: planned
Last updated: 2026-06-25

The current portable app ZIP ships the `lore-book/BOOK.md` reading set as normal
files. This is intentionally smaller than the full `lore-book/` tree because
the full mirror has long reverse-engineering/proof filenames that can exceed
Windows Explorer `Extract All` path limits under normal Downloads folders.

The desired future state is still full offline Lore inside the app. The safe
shape is a generated content pack, not raw long filenames.

## Target Shape

- Keep `lore-book/BOOK.md` and a short human entry point in the ZIP.
- Add a generated offline pack such as `lore-pack/onslaught-lore.v1.jsonl` plus
  `lore-pack/onslaught-lore.v1.index.json`, or an equivalent single short-path
  archive.
- Store each public-safe Lore document with a stable ID, title, original logical
  path, hash, byte range or short entry path, and outbound-link metadata.
- Resolve internal links through AppCore document IDs so packed documents stay
  in the WinUI reader.
- Keep source paths visible as metadata only; do not use long logical paths as
  extracted ZIP filenames.

## Acceptance

- The app can search and open all tracked public-safe Lore documents offline.
- Internal packed-document links stay inside the reader.
- GitHub or external links are visibly identified as source/external links.
- ZIP path safety still passes with default Explorer extraction-folder
  accounting.
- Package probes reject hard payloads, stale all-in-app copy, and raw deep
  `lore-book/` mirror leakage.
- Search is debounced or asynchronous enough that typing does not visibly block
  the WinUI thread.

## Non-Goals

- Do not bundle game binaries, copied executables, saves, extracted assets,
  screenshots, raw CDB logs, or full Ghidra databases/backups.
- Do not add SQLite or another native storage dependency unless JSONL/index
  search is measured and insufficient.
- Do not replace the repo source tree; this is only the downloadable app ZIP's
  offline reader payload.
