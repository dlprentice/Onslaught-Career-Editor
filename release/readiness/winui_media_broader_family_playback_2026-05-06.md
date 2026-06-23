# WinUI Media Broader Family Playback Smoke - 2026-05-06

Status: public-safe evidence

Source branch: `wip/sandbox`

Source commit before this wave: `79e1f6948744d8e9c5338ffd6b2ef3c0afe55b59`

Evidence-report commit: `95d0995d64ea709dfe22a74aa692287b1b1b7289`

Recorded at: 2026-05-06

## Scope

This smoke expands WinUI Media proof beyond the earlier representative Music/Tutorial/Main Videos/Cutscenes sample.

It proves the native WinUI Media page can select, play, and stop a broader family sample from the read-only local install:

- five audio rows across Music, Tutorial, Status Messages, Mission voice, and Racing
- three video rows across Main Videos, Cutscenes, and Mission Briefings

It does not claim every media row plays. It does not mutate the installed game, saves, profiles, or executables.

## Private Evidence Policy

Ignored local evidence remains under `subagents/`. This report does not include private absolute paths, raw screenshot image data, video frames, media cache paths, source media paths, or media payloads.

Ignored evidence filenames:

- `broader-family-playback-summary.json`
- `broader-family-playback-complete.png`

The ignored summary JSON contains row names, group/section names, duration labels, and size labels only.

## Rows Sampled

Audio rows:

| Name | Group | Duration |
| --- | --- | --- |
| `BEA 01(Master)` | Music | 4:57 |
| `tutorial_01` | Tutorial | 0:04 |
| `base_damaged_1` | Status Messages | 0:02 |
| `003_east_sphere_a` | Mission 3 | 0:03 |
| `racing_start_1` | Racing | 0:00 |

Video rows:

| Name | Section | Size |
| --- | --- | --- |
| `Lost Toys Logo` | Main Videos | 1.8 MB |
| `01 - Intro - Forseti Invasion` | Cutscenes | 30.6 MB |
| `Mission 100` | Mission Briefings / Episode 1 | 1.5 MB |

## Commands Run

### Broader Family Playback Smoke

Command:

```powershell
$env:ONSLAUGHT_BEA_GAME_DIR='<read-only local BEA install>'
dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiMediaInteractionSmokeTests.MediaPage_PlaysBroaderFamilySampleRowsThroughUi"
Remove-Item Env:\ONSLAUGHT_BEA_GAME_DIR -ErrorAction SilentlyContinue
```

Result: PASS

Important output:

- 1/1 focused UI test passed.
- The test launched the native WinUI app with isolated app state.
- The app used the configured read-only local install as source material.
- The test selected and played five audio rows, stopping playback after each row.
- The test selected and played three video rows, waiting for the video timer to advance before stopping each row.
- The test captured an ignored private screenshot and an ignored public-safe JSON summary.

## What Is Proven

- The WinUI Media page can play more than one real audio family through the native UI.
- The audio sample covers music, tutorial voice, status messages, mission voice, and racing rows.
- The WinUI Media page can play more than one real video family through the native UI.
- The video sample covers a main video, a cutscene, and a mission briefing row.
- Inline playback controls become active and playback can be stopped after each sampled row.
- Video playback time advances for each sampled video.
- Primary UI source summaries remain public-safe and do not expose private absolute install paths.

## What Is Not Proven

- This does not prove every audio row plays.
- This does not prove every video row plays.
- This does not prove trusted installer/MSIX runtime media playback.
- This does not prove public redistribution rights for private media files.
- This does not mutate the installed game, saves, profiles, or executables.

## Release Posture

GREEN for broader-family WinUI Media playback breadth.

Remaining media gaps are all-row playback coverage, trusted installer/runtime playback proof, and any future release/licensing approval for public media redistribution.
