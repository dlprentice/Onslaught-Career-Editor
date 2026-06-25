# WinUI ZIP Release v1.0.4

Status: published release package validated
Date: 2026-06-25
Scope: `winui-zip-release-v1.0.4`

This pass validates the unsigned portable Windows x64 ZIP intended to supersede
v1.0.3. The v1.0.3 app payload was usable, but its bundled full deep
`lore-book/` mirror exposed long proof-plan paths that could fail Windows
Explorer extraction from normal Downloads folders with `0x80010135`.

| Field | Value |
| --- | --- |
| ZIP | `subagents/winui-zip-release-candidate-probe/current/OnslaughtToolkit-winui-v1.0.4-win-x64.zip` |
| Byte size | `243908905` |
| SHA-256 | `641f17a44343e19efa858af30d6194f6e2b844f06d35a5753b3eb03156ac72b3` |
| Package script | `npm run test:winui-zip-release-candidate-probe` |
| GitHub release | `https://github.com/dlprentice/Onslaught-Career-Editor/releases/tag/v1.0.4` |
| ZIP asset | `https://github.com/dlprentice/Onslaught-Career-Editor/releases/download/v1.0.4/OnslaughtToolkit-winui-v1.0.4-win-x64.zip` |

The package uses the friendly top-level layout:

- `Launch Onslaught Toolkit.cmd`
- `README.MD`
- `LICENSE`
- `app/`
- `lore-book/`

The repo still carries the full public `lore-book/` and RE documentation tree.
The downloadable app ZIP carries the deterministic `BOOK.md`-linked offline
Lore reader set only, because the ZIP is a user-facing app package and must be
safe for Explorer extraction. The v1.0.4 package includes 53 `BOOK.md`-linked
Lore files and the longest packaged entry is 95 characters, inside the probe's
180-character Explorer-safe ZIP entry budget.

Focused package results:

| Check | Result |
| --- | --- |
| Publish app files | PASS |
| Friendly launcher/readme/license | PASS |
| Deterministic `BOOK.md`-linked Lore reader set | PASS (`53` files) |
| No root DLL/EXE payload layout | PASS |
| Hard-payload release safety | PASS |
| Bundle Explorer path safety | PASS (`95` max entry chars / `180` budget) |
| ZIP create and SHA sidecar | PASS |
| ZIP Explorer path safety | PASS (`95` max entry chars / `180` budget) |
| Extracted folder Explorer path safety | PASS (`95` max entry chars / `180` budget) |
| Extracted launch smoke | PASS (`0`) |
| Extracted Home navigation smoke | PASS (`0`) |
| Extracted Lore reader smoke | PASS (`0`) |
| Extracted representative Media smoke | PASS (`0`) |
| UI skipped-row rejection | PASS |
| Process cleanup | PASS |

What this proves:

- The v1.0.4 ZIP uses the friendly wrapper layout and keeps the WinUI payload
  under `app/`.
- The packaged offline Lore reader has the `BOOK.md`-linked files needed by the
  app without exposing users to deep internal proof-note filenames during
  Explorer extraction.
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
