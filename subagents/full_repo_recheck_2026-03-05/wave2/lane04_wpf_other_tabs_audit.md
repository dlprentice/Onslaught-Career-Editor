# Lane 04 - WPF Other Tabs Audit

Scope: Binary Patches, Media (Audio/Video), Lore Browser, and Settings WPF tabs.

Audit basis:
- Current shipped functionality only
- UX/layout/document wording focus
- Read-only review of current XAML and code-behind

## Summary

The strongest issues are guidance and responsiveness, not missing features. Binary Patches is close, but still exposes internal wording that a normal player will not parse confidently. Lore Browser has the most serious UX defect: search currently performs synchronous full-text reads on every keypress, which will scale poorly and can visibly stall the tab. Media and Settings are functional, but both rely too heavily on footer-status messaging instead of inline guidance.

## Findings

- HIGH | `Views/LoreBrowserView.xaml.cs:1165` | Lore search does synchronous content reads across the document corpus on every keypress once the query reaches three characters. `File.ReadAllText(...)` is executed inside the `TextChanged` handler, so the UI thread can block while the user is typing or deleting search text. | Debounce the search box and move content searching to a background task or cached index. Keep title/tree updates on the UI thread only after results are ready.

- MEDIUM | `Views/LoreBrowserView.xaml:76`, `Views/LoreBrowserView.xaml.cs:112`, `Views/LoreBrowserView.xaml.cs:137`, `Views/LoreBrowserView.xaml.cs:155`, `Views/LoreBrowserView.xaml.cs:174` | Lore Browser has no dedicated loading, empty, or error panel. The current behavior only changes the title/status text (`"Loading documents..."`, `"No documents found"`, `"Failed to load documents"`) while the main content area can remain visually blank. That feels broken rather than informative. | Add an inline placeholder surface in the right pane with distinct states: loading, missing `lore-book`, no documents, and load failure. Include one actionable next step per state.

- MEDIUM | `Views/BinaryPatchesView.xaml:79`, `Views/BinaryPatchesView.xaml:95`, `Views/BinaryPatchesView.xaml:111`, `Views/BinaryPatchesView.xaml.cs:295` | Binary patch wording still leans on internal terminology that a release user will not naturally understand: `"windowed-capable path"`, `"cardid.txt tweak overrides"`, and `"startup fullscreen toggle check"`. The confirm dialog also speaks in implementation terms (`"Companion version watermark writes"`) instead of user outcome. | Keep the technical detail in tooltips, but rewrite the visible labels and confirm copy in plain English. Example direction: `Start in windowed mode on launch`, `Ignore cardid.txt so extra graphics stay unlocked`, `Optional fallback if the game still reverts to fullscreen on startup`.

- MEDIUM | `Views/BinaryPatchesView.xaml:54`, `Views/BinaryPatchesView.xaml.cs:32` | The view logic tries to surface patch catalog provenance (`BinaryPatchEngine.CatalogStatus` / fallback state), but the top guidance block does not visibly present that status. Users cannot tell whether they are reviewing the canonical catalog or a fallback path. | Add a visible `Catalog status` row to the top callout and style fallback state as a warning. That makes verification trust much clearer before apply/restore actions.

- MEDIUM | `Views/AudioPlayerView.xaml:15`, `Views/AudioPlayerView.xaml:120`, `Views/AudioPlayerView.xaml.cs:68`, `Views/AudioPlayerView.xaml.cs:104`, `Views/VideoPlayerView.xaml:18`, `Views/VideoPlayerView.xaml:112`, `Views/VideoPlayerView.xaml.cs:133`, `Views/VideoPlayerView.xaml.cs:223` | Both media tabs rely on footer-status text for critical failure states (missing game directory, scan failure). The visible tab body remains an empty tree plus disabled controls, which gives weak recovery guidance. | Add inline empty-state banners near the tree or player pane with clear next actions: `Set Game Directory in Settings`, `Browse for install`, or `Reload`. Keep footer status as secondary confirmation, not the primary explanation.

- LOW | `Views/SettingsView.xaml:115` | The About copy is stale relative to the current app surface. It still describes the product as a `save editor and media browser`, which undersells the Configuration Editor, Binary Patches, and Lore Browser that now define the release. | Update the About copy to match the shipped scope. Suggested direction: `Retail save/options editor, executable patcher, lore browser, and media viewer for Battle Engine Aquila (2003).`

- LOW | `Views/AudioPlayerView.xaml.cs:435`, `Views/VideoPlayerView.xaml.cs:642` | Clearing media search triggers a full disk rescan (`LoadAudioFilesAsync` / `LoadVideoFilesAsync`) instead of restoring the already-loaded tree model. That is avoidable latency and makes search feel heavier than it should. | Keep the original category tree in memory and restore it instantly when the query is cleared. Reserve full rescans for explicit reload actions or path changes.

## Overall Assessment

- Binary Patches: functionally strong, but still a little too close to internal engineering language.
- Lore Browser: strongest information density, but currently the weakest perceived responsiveness because search work happens too eagerly on the UI thread.
- Media: functional, but first-run/empty/failure guidance is too dependent on the footer status strip.
- Settings: clear and usable overall; only the About wording looks behind the rest of the app.
