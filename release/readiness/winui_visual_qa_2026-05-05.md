# WinUI Visual QA Evidence - 2026-05-05

Status: public-safe visual review

## Scope

This note records the first native WinUI visual QA wave for the WinUI product/RE campaign. The screenshots stay local and ignored under `subagents/`; this public-safe note lists filenames only and does not embed private screenshots, game paths, frame captures, or media data.

## Capture Method

- App: WinUI 3 product lane
- Command: `dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiVisualSmokeTests"`
- Screenshot location: ignored `ignored local visual QA artifact folder`
- Config isolation: the visual smoke uses an ignored app config root under `subagents/`; if a local game install is detected, that private path is written only to ignored test config.
- Latest capture source: disposable unpackaged WinUI publish output via `ONSLAUGHT_WINUI_TEST_EXE_PATH`.
- Screenshots are private/local QA evidence, not public release artifacts.

## Screen Review

| Screen | Screenshot filename | Status | Top visible issue | Reference intent fit |
| --- | --- | --- | --- | --- |
| Home / start | `01-home.png` | PASS/YELLOW | A dedicated task-router Home now exists; visual polish can improve, but it no longer drops users straight into dense Save Lab controls. | Mostly fits: the first screen now routes users by task and states copy-first safety. |
| Save Lab | `02-save-lab.png` | PASS | Save Lab now opens with a three-choice task guide and a clear analyzer empty prompt instead of blank metric cards; real-save analyzer and copied-save editor interaction are recorded separately in `winui_save_analyzer_real_save_smoke_2026-05-06.md` and `winui_save_editor_copied_save_smoke_2026-05-06.md`. | Fits the current first-run intent and the core save paths: a normal user can choose analyze, edit a copied save, or review options before entering deeper controls. |
| Media audio | `03-media-audio.png` | PASS/YELLOW | The configured game directory loads and source paths are collapsed; this visual-only capture shows the ready state. Follow-up interaction proof is now recorded separately in `winui_media_interaction_smoke_2026-05-06.md`. | Mostly fits: library groups, source summary, and inline transport are visible without private paths as primary text. |
| Media video | `04-media-video.png` | PASS | The video tab now reserves a clear player surface in the first viewport; follow-up playback interaction and layout proof are recorded in `winui_media_interaction_smoke_2026-05-06.md` and `winui_media_video_player_layout_2026-05-06.md`. | Fits the current video-browsing intent: video library, selected-player area, transport controls, and collapsed source details are visible without full private paths. |
| Asset Library texture | `05-asset-library-texture.png` | PASS | Texture preview now appears in the first viewport with a compact loaded-catalog banner and neutral preview canvas; real generated-catalog visual smoke is recorded separately in `winui_asset_texture_preview_visual_2026-05-06.md`. | Fits the current texture-inspection intent: generated catalog browsing, selected texture preview, and scoped open/copy actions are visible without bundling private assets. |
| Asset Library model | `06-asset-library-model.png` | PASS | Model export detail now shows a visible bounded wireframe preview in-app. Full 3D rendering is still intentionally unclaimed. | Fits the current lightweight model-inspection intent. |
| Lore | `07-lore.png` | PASS | The library and embedded reader render a real document with comfortable contrast and readable article width. | Fits the document-reader intent for the captured start document. |
| Patch Bench | `08-patch-bench.png`; scrolled workflow proof in `winui_patch_bench_copied_executable_smoke_2026-05-06.md` | PASS | Copied-executable workflow is visible; follow-up scrolled proof shows verify/apply/restore output with app-owned target and backup labels instead of full private paths in the primary log. | Fits the safe guided patch workflow intent: source stays read-only, actions target an app-owned copy, and deeper controls are reachable through accessibility automation plus scrolling. |
| Settings | `09-settings.png` | PASS | Settings now shows a friendly configured-install summary, states read-only source posture, and keeps full local paths collapsed under Path details. | Fits current safety posture without making the private install path the primary visual fact. |
| About | `10-about.png` | PASS | Product-lane language is clear and current. | Fits WinUI-first repo truth. |

## Result

The visual automation path is GREEN as infrastructure: the native WinUI app launches primary pages, captures ignored screenshots, and closes cleanly. The latest screenshot wave was captured from the disposable unpackaged publish output.

The visual/product state is PASS/YELLOW overall: the shell is safer and testable, Home routes users by task, Save Lab has first-run task guidance with a clear analyzer empty state plus real-save analyzer and copied-save editor interaction proof, Patch Bench has first-viewport and scrolled copied-executable workflow proof, Settings hides full local paths by default, Media has configured-directory audio/video screenshots with a larger video-player surface, and Asset Library captures both texture and model preview states. Follow-up native interaction smoke proves focused WinUI audio/video playback, real-catalog texture visual smoke proves a selected extracted texture can render visibly in the first viewport, and separate model coverage evidence now reports 352/352 generated model rows with bounded wireframe data. Remaining product gaps are broader media row coverage, full native 3D/material rendering, installer-grade packaging proof, and later RE/product workflow depth.

## What Did Not Change

- No game install, executable, save, media, or runtime proof artifact was mutated.
- No archived Electron/WPF/Python lane was reactivated.
- No private screenshot was committed.
