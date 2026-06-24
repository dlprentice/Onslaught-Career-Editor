# WinUI Asset Library Catalog Coverage Summary - 2026-05-07

## Scope

This pass moved the asset provenance/viewer-truth boundary into the WinUI Asset Library itself. After a generated catalog loads, the app now shows a visible coverage summary that distinguishes real local extraction from the current bounded viewer.

## Product Change

The Asset Library catalog browser now includes `AssetCatalogCoverageSummary`.
Selected model detail now also includes `AssetModelTextureLinks`, which lists catalog-matched texture links from the selected FBX export without exposing local private paths.
When a selected model has a matched catalog texture, the detail panel now offers `View linked texture` to jump directly to the texture row and preview.
The Goodies tab now includes local browser filters for `All`, `Wall`, `Hidden`, `Models`, `Artwork`, and `Videos`, allowing the WinUI app to behave more like a static Goodies browser without claiming runtime unlock replay.
The Goodies filter strip now includes a visible status line for the active filter. In particular, the hidden filter tells users that shipped Goodies without a known wall coordinate are static catalog evidence, not runtime reachability proof.
The maximized visual smoke also caught and fixed a startup/deep-link state issue where the Goodies subtab could show one visible catalog row while the filter status still said zero rows. The status is now refreshed after the Goodies item source is assigned, and the visual smoke asserts the deterministic startup count.
A full-install Goodies visual smoke now captures representative model, artwork, and video Goodie rows under ignored `subagents/` evidence. Model/artwork Goodies prove local extracted preview paths; video Goodies are catalog-linked and now offer an `Open in Media` handoff instead of exposing a fake export action.
The video handoff searches by the linked video sequence/file stem, lands on the Media video tab, selects the human-labeled Media row, and preserves the real Bink source filename in the selected-video summary. The proof row currently covers `Goodie 077 - Development` -> `UsTheMovie` -> `Credits Video` / `UsTheMovie.vid`.

For the private full-install catalog, the summary states:

- real local extraction is being used,
- texture PNG preview coverage is available,
- FBX model export coverage is available,
- wireframe preview coverage is available,
- model texture-binding resolution is counted,
- Goodies texture/model/video coverage is counted,
- model viewing is currently wireframe/export-based,
- textured 3D rendering remains future work.

The catalog path remains behind the existing Path details disclosure.

## Commands

```powershell
dotnet build OnslaughtCareerEditor.WinUI/OnslaughtCareerEditor.WinUI.csproj --nologo
$env:ONSLAUGHT_WINUI_REAL_ASSET_CATALOG = "<private catalog.json>"
dotnet test OnslaughtCareerEditor.UiTests/OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~AssetLibrary_CyclesRepresentativeRealRowsWhenCatalogProvided"
dotnet test OnslaughtCareerEditor.UiTests/OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~AssetLibrary_CapturesRealGoodiesBrowserWhenCatalogProvided"
```

Results:

- WinUI build: PASS, 0 warnings, 0 errors.
- Focused native Asset Library UIA smoke: PASS, 1 passed, 0 failed, 0 skipped.
- Focused native Goodies visual/handoff smoke: PASS, 1 passed, 0 failed, 0 skipped.

## Smoke Assertions Added

The focused native smoke now asserts that `AssetCatalogCoverageSummary` contains:

- `Real local extraction`
- `352/352 model rows have catalog-matched texture links`
- `194/194 texture Goodies preview-ready`
- `45/45 model Goodies wireframe-ready`
- `wireframe/export-based`

The same smoke now asserts that selected model detail includes:

- `catalog-matched texture link`
- an enabled `View linked texture` handoff that changes the selected detail to a texture preview

The same smoke now asserts that the Goodies browser can:

- switch to the `Models` filter and select representative model Goodies,
- switch to the `Hidden` filter and select representative hidden artwork Goodies,
- read human filter-status text for model Goodies and hidden Goodies,
- verify the initial Goodies visual-smoke route reports the same cataloged count as the visible deterministic row set,
- capture representative private full-install Goodies model, artwork, and video states without committing screenshots,
- click a video Goodie's `Open in Media` action and verify the Media page selects `Credits Video` from `UsTheMovie.vid`,
- keep selected Goodie previews routed through the existing model/artwork detail surfaces.

## Operating Lessons Recorded

- Native WinUI smoke should maximize the app before visual or interaction evidence. The app has useful surfaces below the laptop first viewport, so first-viewport screenshots are not enough; UIA tests must scroll or invoke controls by automation ID when sections are offscreen.
- Startup/deep-link screen state needs direct assertions. Interaction tests that click into a later filter state can miss stale initialization copy, as shown by the Goodies status count fix.
- Screenshot review remains useful even with passing UIA tests. The stale Goodies count was a visible trust issue, not a backend/catalog failure.
- Representative full-catalog Goodies screenshots are needed alongside generic model/texture screenshots. A model export, artwork export, and video link exercise different truth boundaries.
- Cross-page WinUI handoffs need settled destination-state assertions, not just source-button assertions. The video Goodie handoff first looked wired because it searched `UsTheMovie`, but screenshot/UIA proof showed the selected-video panel was being cleared by transient TreeView selection events.
- Tree/group focus changes should not wipe an already selected media item. The Media page now keeps the selected player stable while users expand/collapse or focus a group row.
- Filtered native UI tests can rebuild the test assembly while leaving the WinUI executable stale. Rebuild `OnslaughtCareerEditor.WinUI` before running UIA smoke after app-code changes.
- `rg` is unreliable in this Windows/Codex lane. Agent searches should use `git ls-files` plus targeted Node/Python scans instead of wasting cycles retrying a broken search command.
- Goodies catalog rows are static extraction/catalog evidence. Optional copied-save state can describe locked/unlocked/viewed labels, but catalog browsing is not runtime proof that the retail Goodies wall, unlock animation, or model viewer loop has been replayed.
- Model viewing in WinUI is currently wireframe/export-based. Catalog-matched texture links and `View linked texture` handoff prove linkage and preview navigation, not a textured in-app 3D renderer.
- Full-install catalog paths, generated catalog JSON, screenshots, extracted images/models, and runtime proof files remain private under ignored locations such as `subagents/`.

## What This Proves

- The native WinUI app surfaces the real-extraction/viewer-limitation truth directly after catalog load.
- The summary is visible through UI Automation and not only buried in docs.
- Selecting representative model rows exposes catalog-matched texture-link names in the native detail panel.
- The selected-model texture link is actionable inside the WinUI Asset Library instead of being only documentation text.
- The Goodies tab can narrow the static catalog to model Goodies and hidden artwork Goodies through native UI controls.
- The Goodies visual smoke now shows representative full-install model, artwork, and video rows through the native WinUI browser.
- A video Goodie can hand off to Media and select the matching local Bink video by human label and source filename.
- The full private catalog still loads and representative texture/model/Goodies rows still pass the existing row-breadth smoke.

## What This Does Not Prove

- It does not add a full textured or animated in-app model viewer.
- It does not prove runtime replay of every Goodies wall slot.
- It does not prove that every Goodie unlock criterion has been reconstructed from retail runtime behavior.
- It does not prove Bink conversion/playback from the Goodie row itself; playback still happens in Media.
- It does not commit private catalog JSON, paths, screenshots, frames, or extracted assets.
