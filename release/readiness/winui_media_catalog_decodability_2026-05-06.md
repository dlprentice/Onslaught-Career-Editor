# WinUI Media Catalog Decodability Smoke - 2026-05-06

Status: public-safe evidence

Source branch: `wip/sandbox`

Source commit before this wave: `14f49460e5f22af6d940aea2dd8ac28697739225`

Evidence-report commit: `b3df75e36d3bc1909c0e988c674a211c05db3489`

Recorded at: 2026-05-06

## Scope

This smoke adds a catalog-wide read-only sanity layer for the WinUI Media lane.

It does not drive every row through UI playback. It verifies that every cataloged audio row resolves to an existing OGG file with a parsed duration label, and every cataloged video row resolves to an existing Bink video file with a readable `BIK` header.

The source game install is treated as read-only source material.

## Private Evidence Policy

Ignored local evidence remains under `subagents/`. This report does not include private absolute paths, raw media headers, raw screenshot image data, video frames, media cache paths, source media paths, or media payloads.

Ignored evidence filename:

- `media-catalog-decodability.json`

The ignored JSON contains counts, group names, and section names only.

## Coverage Counts

| Check | Result |
| --- | ---: |
| Cataloged audio rows | 629 |
| Audio rows with parsed duration labels | 629 |
| Cataloged video rows | 66 |
| Video rows with readable Bink headers | 66 |

Top audio groups by row count:

| Group | Rows |
| --- | ---: |
| Other | 110 |
| Mission 612 | 51 |
| Status Messages | 46 |
| Tutorial | 46 |
| Mission 400 | 26 |
| Mission 512 | 23 |
| Mission 300 | 20 |
| Mission 200 | 19 |
| Mission 231 | 17 |
| Mission 600 | 17 |

Video sections:

| Section | Rows |
| --- | ---: |
| Cutscenes | 32 |
| Main Videos | 6 |
| Mission Briefings / Episode 1 | 2 |
| Mission Briefings / Episode 2 | 4 |
| Mission Briefings / Episode 3 | 4 |
| Mission Briefings / Episode 4 | 4 |
| Mission Briefings / Episode 5 | 5 |
| Mission Briefings / Episode 6 | 3 |
| Mission Briefings / Episode 7 | 5 |
| Mission Briefings / Episode 8 | 1 |

## Commands Run

### Catalog Decodability Smoke

Command:

```powershell
$env:ONSLAUGHT_BEA_GAME_DIR='<read-only local BEA install>'
dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiMediaCatalogCoverageSmokeTests.MediaCatalog_VerifiesRetailAudioDurationsAndVideoHeadersFromReadOnlyInstall"
Remove-Item Env:\ONSLAUGHT_BEA_GAME_DIR -ErrorAction SilentlyContinue
```

Result: PASS

Important output:

- 1/1 focused UI test passed.
- The test read the configured local install without writing to it.
- 629/629 cataloged audio rows had parsed duration labels.
- 66/66 cataloged video rows had readable Bink headers.
- The test wrote ignored public-safe JSON counts under `subagents/`.

## What Is Proven

- The WinUI/AppCore Media catalog resolves every currently cataloged audio row to a readable OGG source with duration metadata.
- The WinUI/AppCore Media catalog resolves every currently cataloged video row to a readable Bink source header.
- The catalog-wide audio/video source coverage is stronger than a row-count inventory because it checks the actual file readability needed before playback.
- The proof is read-only against the local install and keeps raw paths and media data out of public evidence.

## What Is Not Proven

- This does not prove every audio row can be played through the native UI.
- This does not prove every video row can be played through the native UI.
- This does not prove trusted installer/MSIX runtime media playback.
- This does not prove public redistribution rights for private media files.
- This does not mutate the installed game, saves, profiles, or executables.

## Release Posture

GREEN for catalog-wide media source decodability/header coverage.

Remaining media gaps are all-row native playback coverage, trusted installer/runtime playback proof, and release/licensing approval for any public media redistribution.
