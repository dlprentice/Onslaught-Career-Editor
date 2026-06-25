# WinUI ZIP Release v1.0.7 - 2026-06-25

Status: published GitHub Release

## Artifact

- ZIP: `subagents/winui-zip-release-candidate-probe/current/OnslaughtToolkit-winui-v1.0.7-win-x64.zip`
- Byte size: `246757113`
- SHA-256: `033d9f65d51e884c7896fcd1180689988743c50ef6c57a6ce0c72f8b4f38c7ae`
- Release: https://github.com/dlprentice/Onslaught-Career-Editor/releases/tag/v1.0.7
- Download: https://github.com/dlprentice/Onslaught-Career-Editor/releases/download/v1.0.7/OnslaughtToolkit-winui-v1.0.7-win-x64.zip
- Checksum: https://github.com/dlprentice/Onslaught-Career-Editor/releases/download/v1.0.7/OnslaughtToolkit-v1.0.7-SHA256SUMS.txt
- Published at: `2026-06-25T17:33:53Z`
- Tag commit: `f9fb41b1a6090965778f770533367893b957ab98`

## Included

- `Launch Onslaught Toolkit.cmd`
- `README.MD`
- `LICENSE`
- `app/`
- short `lore-book/` entry files
- generated `lore-pack/` with `943` public-safe Markdown/TXT Lore documents

## Not Included

- Battle Engine Aquila game files or copied executables
- saves/options payloads
- media payloads or extracted assets
- full Ghidra databases or backups
- raw runtime proofs, frame captures, screenshots, raw CDB logs, or bulky generated proof archives
- MSIX/AppInstaller/signing/Store/SmartScreen proof

## Proven Locally

- Explorer-safe ZIP entry path budget.
- Friendly top-level layout with app payload under `app/`.
- Launcher checks for app executable, `lore-book/BOOK.md`, Lore pack index, and Lore pack JSONL before launch.
- Lore pack schema, hashes, payload safety, and packed local-link integrity.
- Raw deep `lore-book/` mirror entries do not leak beside the generated pack.
- Extracted app launch smoke.
- Extracted Home navigation smoke.
- Extracted Lore reader smoke.
- Representative Media smoke.
- Third-party notices check for `74` packages.
- No WinUI process remains after probe.

## Boundary

This is the current public downloadable app release. It is a portable unsigned
ZIP, not an MSIX/AppInstaller/signed installer or SmartScreen/reputation proof.
