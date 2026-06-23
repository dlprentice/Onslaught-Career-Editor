# WinUI Media Catalog Coverage Smoke - 2026-05-06

Status: pass

Source commit: 1c7e22f7
Evidence-report commit: 514c71dfedde9ae366efca4d60d31837084b7774

## Objective

Prove broader read-only Media catalog coverage from the local Battle Engine Aquila install without mutating files, playing media, committing private assets, or exposing private absolute paths.

This complements the focused WinUI Media interaction smoke. The interaction smoke proves one selected audio row and one selected video row can play through the native desktop UI. This coverage smoke proves the catalog layer sees broad retail audio/video families.

## Scope

- Read-only source material: local Battle Engine Aquila install.
- Output: ignored local JSON summary with counts and sample filenames only.
- No playback.
- No media payload extraction.
- No installed-game mutation.
- No copied executable/profile work.
- No public release of private media.

## Focused Smoke Result

Command:

```powershell
$env:ONSLAUGHT_BEA_GAME_DIR='C:\Program Files (x86)\Steam\steamapps\common\Battle Engine Aquila'; dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiMediaCatalogCoverageSmokeTests"
```

Working directory:

```text
repo root
```

Result: pass

Important output:

```text
Passed! - Failed: 0, Passed: 1, Skipped: 0, Total: 1, Duration: 1 s
```

What it proves:

- the AppCore media catalog can load the local retail install as read-only source material
- audio catalog coverage includes Music, Tutorial, Status Messages, mission-scoped voice rows, and other voice rows
- video catalog coverage includes Main Videos, Cutscenes, and Mission Briefings by episode
- selected sample rows point at existing files
- selected video rows expose human-readable size labels
- selected music rows expose parsed OGG duration labels
- ignored local proof output records counts without absolute paths or media payloads

## Public-Safe Coverage Summary

| Family | Count | Notes |
| --- | ---: | --- |
| Audio rows | 629 | Includes music, tutorial, status messages, mission voice, racing, and other voice groups. |
| Music rows | 10 | First five sampled music rows expose duration labels. |
| Video rows | 66 | Includes main videos, cutscenes, and mission briefing videos. |
| Main video rows | 6 | Selected sample rows exist and expose size labels. |
| Cutscene rows | 32 | Selected sample rows exist and expose size labels. |
| Mission briefing rows | 28 | Grouped by episode in the generated catalog. |

## Ignored Local Evidence

Ignored local JSON filename:

```text
media-catalog-coverage.json
```

The JSON is stored under ignored local evidence storage and records only counts, group/section names, and sample filenames. It does not contain absolute paths, raw media, screenshots, data URLs, base64, copied executables, saves, or proof frames.

## What Is Proven

- Broad read-only media catalog enumeration works against the local retail install.
- Catalog grouping covers the main audio and video families expected from the current install.
- The existing catalog service can parse durations for representative OGG music rows.
- The current WinUI/AppCore media layer has broader catalog evidence beyond the single-row playback smoke.

## What Is Not Proven

- Playback of all 629 audio rows.
- Playback of all 66 video rows.
- Packaged or installer-grade media runtime behavior.
- Public redistribution clearance for private media.
- Bink/video transcoding coverage beyond the existing focused playback evidence.
- Semantic interpretation of media contents.

## Safety Notes

- The smoke reads the configured install only as source material.
- It does not write into the game install.
- It does not launch the game.
- It does not mutate `BEA.exe`, save files, options files, media files, or generated catalogs.
