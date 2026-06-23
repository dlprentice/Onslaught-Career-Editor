# WinUI Media Representative Playback Smoke - 2026-05-06

Status: public-safe evidence

Source branch: `wip/sandbox`

Source commit before this wave: `6198eb54862b`

Evidence-report commit: `a4f23882cc71147072c343d2c00793b42828693a`

Recorded at: 2026-05-06

## Scope

This smoke expands WinUI Media proof from one selected audio/video pair to a small representative playback sample across multiple catalog families.

It does not claim all-row playback. It proves the native WinUI Media page can select, play, and stop two real audio rows and two real video rows from the read-only local install while keeping raw paths and media payloads private.

## Private Evidence Policy

Ignored local evidence remains under `subagents/`. This report does not include private absolute paths, raw screenshot image data, video frames, media cache paths, source media paths, or media payloads.

Ignored evidence filenames:

- `representative-playback-summary.json`
- `representative-playback-complete.png`

The ignored summary JSON contains row names, group/section names, duration labels, and size labels only.

## Rows Sampled

Audio rows:

| Name | Group | Duration |
| --- | --- | --- |
| `BEA 01(Master)` | Music | 4:57 |
| `tutorial_01` | Tutorial | 0:04 |

Video rows:

| Name | Section | Size |
| --- | --- | --- |
| `Lost Toys Logo` | Main Videos | 1.8 MB |
| `01 - Intro - Forseti Invasion` | Cutscenes | 30.6 MB |

## Commands Run

### Representative Playback Smoke

Command:

```powershell
dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiMediaInteractionSmokeTests.MediaPage_PlaysRepresentativeAudioAndVideoRowsThroughUi"
```

Result: PASS

Important output:

- 1/1 focused UI test passed.
- The test launched the native WinUI app with isolated app state.
- The app used the configured read-only local install as source material.
- The test selected and played two audio rows, stopping each playback.
- The test selected and played two video rows, waiting for the video timer to advance before stopping each playback.
- The test captured an ignored private screenshot and an ignored public-safe JSON summary.

### Earlier Focused Media Checks In This Campaign

The active WinUI media evidence stack also includes:

- `release/readiness/winui_media_interaction_smoke_2026-05-06.md`: focused inline audio/video playback for selected rows.
- `release/readiness/winui_media_catalog_coverage_smoke_2026-05-06.md`: broader read-only catalog enumeration across 629 audio rows and 66 video rows.
- `release/readiness/winui_media_video_player_layout_2026-05-06.md`: video player layout polish and proof.

## What Is Proven

- The WinUI Media page can play more than one real audio row through the native UI.
- The audio sample covers a music track and a tutorial voice line.
- The WinUI Media page can play more than one real video row through the native UI.
- The video sample covers a main video and a cutscene.
- Inline playback controls become active and playback can be stopped after each sampled row.
- Video playback time advances for each sampled video.
- Primary UI source summaries remain public-safe and do not expose private absolute install paths.

## What Is Not Proven

- This does not prove every audio row plays.
- This does not prove every video row plays.
- This does not prove packaged installer/runtime media playback.
- This does not prove public redistribution rights for private media files.
- This does not mutate the installed game, saves, profiles, or executables.

## Release Posture

GREEN for representative WinUI Media playback breadth.

Remaining media gaps are row-by-row broader playback coverage, packaged installer/runtime playback proof, and any future release/licensing approval for public media redistribution.
