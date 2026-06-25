# WinUI ZIP Release v1.0.6 - 2026-06-25

Status: ready for GitHub Release publication after commit/tag

## Package

- Asset: `OnslaughtToolkit-winui-v1.0.6-win-x64.zip`
- Byte size: `243917871`
- SHA-256: `ce5cb69a836f1b9c759ec608407cee51520f147979816a8661c29bf32cd6d720`
- Shape: unsigned portable Windows x64 ZIP
- Root layout: `Launch Onslaught Toolkit.cmd`, `LICENSE`, `README.MD`,
  `app/`, `lore-book/`
- Product lane: WinUI 3 / AppCore

## Delta From v1.0.5

- Keeps the v1.0.5 friendly wrapper layout and Explorer-safe package shape.
- Keeps the packaged offline Lore reader limited to `BOOK.md`-linked files.
- Adds visible WinUI Lore copy that distinguishes packaged offline chapters
  from GitHub source links.
- Adds rendered Markdown badges for GitHub source links.
- Adds package-probe guards that reject stale packaged Lore copy claiming all
  internal links stay in-app while unbundled source links are externalized.
- Records the full-offline Lore plan as a generated short-path content pack,
  not a raw full `lore-book/` mirror in the app ZIP.

## Validation

- `py -3 tools\winui_zip_package_probe_test.py` - PASS, 14 tests.
- `dotnet test .\OnslaughtCareerEditor.AppCore.Tests\OnslaughtCareerEditor.AppCore.Tests.csproj --nologo --filter "FullyQualifiedName~LoreBrowserServiceTests"` - PASS, 6 tests.
- `npm run test:winui-primary-lane` - PASS; build succeeded with 0 warnings/0 errors, AppCore 1172 passed, UiTests 85 passed / 2 skipped.
- `npm run test:doc-commands` - PASS; 4232 documented npm commands checked.
- `npm run test:winui-zip-release-candidate-probe` - PASS with the exact
  `v1.0.6` asset name; extracted launch, Home, Lore, and representative Media
  smokes passed.
- `npm run test:md-links` - PASS; 3618 markdown files scanned, 6123 local links checked.
- `npm run release:curated-check` - PASS; selected files 625.
- `npm run release:profile-check` - PASS; `R0=6126 R2=0 R3=3 R4=13177`.
- `npm run test:public-allowlist` - PASS; public candidate files 19307, submodule candidate files 19491.
- `npm run test:winui-notices` - PASS; 74 packages.
- `npm run test:repo-hygiene` - PASS; repo text hygiene and 18459 explicit text files line-ending check.
- `git diff --check` - PASS.
- State JSON parse - PASS.

## Non-Claims

- No MSIX/AppInstaller package, certificate signing, Store distribution,
  SmartScreen/reputation proof, installer UX, or uninstall proof.
- No Battle Engine Aquila game files, copied executables, saves, media payloads,
  full Ghidra databases/backups, raw CDB logs, screenshots, or bulky runtime
  proof captures are included.
- No player-ready online multiplayer, gameplay parity, clean-room rebuild
  parity, or no-noticeable-difference claim.
