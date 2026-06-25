# WinUI ZIP Release v1.0.3

Status: superseded by v1.0.5 Explorer path-length and Lore link hotfixes
Date: 2026-06-24
Scope: `winui-zip-release-v1.0.3`

This pass validates the exact unsigned portable Windows x64 ZIP published to
GitHub Release `v1.0.3`:

Important follow-up: after publication, Explorer extraction from a normal
Downloads folder hit Windows `0x80010135` path-too-long failures on deep
`lore-book/` proof-plan paths. The app payload and short-path package smokes
below remain useful historical evidence, but v1.0.3 should not be recommended
for normal users. Use v1.0.5 or newer.

| Field | Value |
| --- | --- |
| ZIP | `subagents/winui-zip-release-candidate-probe/current/OnslaughtToolkit-winui-v1.0.3-win-x64.zip` |
| Byte size | `249834185` |
| SHA-256 | `406f34bdac0f1a39939e57eba9dab1dc37a889d780c9392470f9dc19a77c4044` |
| Package script at validation time | `npm run test:winui-zip-release-candidate-probe` |
| GitHub release | `https://github.com/dlprentice/Onslaught-Career-Editor/releases/tag/v1.0.3` |
| ZIP asset | `https://github.com/dlprentice/Onslaught-Career-Editor/releases/download/v1.0.3/OnslaughtToolkit-winui-v1.0.3-win-x64.zip` |

The package uses the friendly top-level layout:

- `Launch Onslaught Toolkit.cmd`
- `README.MD`
- `LICENSE`
- `app/`
- `lore-book/`

This is historical release evidence. The current
`npm run test:winui-zip-release-candidate-probe` command builds the latest
configured release candidate, not this archived v1.0.3 ZIP.

The probe rejects raw publish-root layouts where DLL/EXE payloads are exposed at
the ZIP root. The WinUI payload remains under `app/`, and offline Lore content
is included under `lore-book/`.

Focused package results:

| Check | Result |
| --- | --- |
| Publish app files | PASS |
| Friendly launcher/readme/license | PASS |
| Bundled `lore-book/BOOK.md` | PASS |
| No root DLL/EXE payload layout | PASS |
| Hard-payload release safety | PASS |
| ZIP create and SHA sidecar | PASS |
| Extracted launch smoke | PASS (`0`) |
| Extracted Home navigation smoke | PASS (`0`) |
| Extracted Lore reader smoke | PASS (`0`) |
| Extracted representative Media smoke | PASS (`0`) |
| UI skipped-row rejection | PASS |
| Process cleanup | PASS |

What this proves:

- The exact v1.0.3 ZIP could be extracted and launched in the probe's short
  artifact path through the friendly top-level command wrapper.
- The extracted package can navigate Home, open bundled Lore content, and run
  the representative Media smoke without accepting skipped UI test rows.
- The app package includes public-safe docs/lore needed for first-run browsing
  without requiring a private checkout.

What this did not prove, and what v1.0.4 adds:

- Explorer-safe extraction from normal user paths such as Downloads.
- Rejection of ZIP entries whose relative paths are too long for a normal
  Explorer Extract All destination.

What this does not prove:

- MSIX/AppInstaller packaging.
- Code signing, Store distribution, SmartScreen reputation, or trusted
  installer UX.
- Battle Engine Aquila game-file redistribution.
- Private proof publication.
- Player-ready online multiplayer, Host/Join enablement, public matchmaking,
  native BEA netcode, gameplay parity, or clean-room rebuild parity.
