# WinUI ZIP Release v1.0.5

Status: published and verified
Date: 2026-06-25
Scope: `winui-zip-release-v1.0.5`

This pass validates the unsigned portable Windows x64 ZIP intended to supersede
v1.0.4. The v1.0.4 package fixed the v1.0.3 Explorer path-too-long failure, but
its packaged Lore pages could still contain local relative links to deeper
source docs that were intentionally not bundled. v1.0.5 keeps the Explorer-safe
package shape and rewrites deeper unbundled source links to GitHub so the
downloaded app ZIP does not contain dead local Lore links.

| Field | Value |
| --- | --- |
| ZIP | `subagents/winui-zip-release-candidate-probe/current/OnslaughtToolkit-winui-v1.0.5-win-x64.zip` |
| Byte size | `243916186` |
| SHA-256 | `f8ba14a51ed57b14c3575a82f424de96c03b94453b03f19c6ed93a7ed5f65847` |
| Package script | `npm run test:winui-zip-release-candidate-probe` |
| GitHub release | `https://github.com/dlprentice/Onslaught-Career-Editor/releases/tag/v1.0.5` |
| ZIP asset | `https://github.com/dlprentice/Onslaught-Career-Editor/releases/download/v1.0.5/OnslaughtToolkit-winui-v1.0.5-win-x64.zip` |
| Checksum asset | `https://github.com/dlprentice/Onslaught-Career-Editor/releases/download/v1.0.5/OnslaughtToolkit-v1.0.5-SHA256SUMS.txt` |
| Published at | `2026-06-25T12:16:30Z` |

The package uses the friendly top-level layout:

- `Launch Onslaught Toolkit.cmd`
- `README.MD`
- `LICENSE`
- `app/`
- `lore-book/`

Lore packaging policy:

- The source repo keeps the full public `lore-book/` and RE documentation tree.
- The downloadable app ZIP carries the `lore-book/BOOK.md` reader documents
  only, because the ZIP is a user-facing app package and must remain safe for
  normal Explorer extraction.
- Links from bundled Lore pages to deeper source docs are rewritten to GitHub
  source/search links during packaging instead of remaining dead local paths.

Focused package results:

| Check | Result |
| --- | --- |
| Publish app files | PASS |
| Friendly launcher/readme/license | PASS |
| `BOOK.md`-linked Lore reader set | PASS (`53` files) |
| Package-only deeper source-link rewrite | PASS (`1888` GitHub source links) |
| Packaged Lore local link safety | PASS |
| No root DLL/EXE payload layout | PASS |
| Hard-payload release safety | PASS |
| Bundle Explorer path safety | PASS (`95` max entry chars / `180` budget) |
| ZIP Explorer path safety | PASS (`133` max default Extract All relative chars / `180` budget) |
| ZIP packaged Lore local link safety | PASS |
| Extracted folder Explorer path safety | PASS (`95` max entry chars / `180` budget) |
| ZIP create and SHA sidecar | PASS |
| Extracted launch smoke | PASS (`0`) |
| Extracted Home navigation smoke | PASS (`0`) |
| Extracted Lore reader smoke | PASS (`0`) |
| Extracted representative Media smoke | PASS (`0`) |
| UI skipped-row rejection | PASS |
| Process cleanup | PASS |

What this proves:

- The v1.0.5 ZIP uses the friendly wrapper layout and keeps the WinUI payload
  under `app/`.
- The packaged offline Lore reader has the `BOOK.md` tree files needed by the
  app without exposing users to deep internal proof-note filenames during
  Explorer extraction.
- Packaged Lore markdown has no dead local links after the package-only
  source-link rewrite.
- The exact package can be extracted, launched, navigated through Home, opened
  through Lore, and run through representative Media smoke without accepting
  skipped UI rows.

What this does not prove:

- MSIX/AppInstaller packaging.
- Code signing, Store distribution, SmartScreen reputation, or trusted
  installer UX.
- Battle Engine Aquila game-file redistribution.
- Private proof publication.
- Player-ready online multiplayer, Host/Join enablement, public matchmaking,
  native BEA netcode, gameplay parity, or clean-room rebuild parity.
