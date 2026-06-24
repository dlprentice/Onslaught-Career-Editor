# User Sanity Check

> **SUPERSEDED — archived/historical (2026-05-26):** Electron is **not** the active product surface. Use WinUI build/test gates in `RELEASE_SCOPE_AND_TEST_COMMANDS.md` and `README.MD` for current product validation. The Electron workbench under `archive/electron-workbench/` is archived/reference only.

Status: deprecated / archived/historical
Last updated: 2026-05-01
Replacement: `README.MD` quick start, `RELEASE_SCOPE_AND_TEST_COMMANDS.md`, and WinUI/AppCore test gates

This archived note is a historical C#/WPF sanity checklist. Do not use it as an active release gate for any product lane.

Use this list only when deliberately checking the archived WPF app. It is not an active WinUI, Electron, or other product gate.

## Launch

- Build archived WPF app (Windows PowerShell, historical reference only):
  - `dotnet build ".\archive\legacy-wpf\Onslaught - Career Editor.sln"`
- Run:
  - use the executable generated under `archive\legacy-wpf\bin\...` after that build.

## Smoke checks (C# app)

1. **Tabs load**
   - Click: Saves, Media, Lore, Binary Patches, Settings.
   - Expect: UI renders without freezes or blank panes.

2. **Saves tab**
   - Select a `.bes` file (use `save-attempts/haha-cannon-goes-brrrrr.bes`).
   - Run Analyze.
   - Expect: summary fields populate; no exceptions.

3. **Save Editor**
   - Verify the **Advanced Options** section is visible.
   - Expand both nested sections and confirm controls render:
     - `Career Progress Overrides (.bes)`
     - `Configuration Overrides (.bea/.bes)`
   - Change a field, then **Copy output** (if available).
   - Expect: UI updates and output text reflects changes.

4. **Lore browser (Lore Book)**
   - Click several docs in the tree.
   - Click **Home**, then **Back/Forward** to verify navigation history.
   - Click a **.md** link inside a doc.
   - Expect: navigates in-app (no OS prompt).
   - Click an **https://** link.
   - Expect: opens in default browser.
   - Use search to filter and confirm the tree updates.

5. **Media > Audio**
   - Double-click a track, then double-click another.
   - Expect: Now Playing updates to the new track; controls reflect current track.

6. **Media > Video**
   - Play a video.
   - Switch tabs and return.
   - Expect: no "player not initialized" error.

7. **Settings**
   - Verify game path is detected and saved when available.

## Known failure signals

- Link clicks opening Microsoft Store or "select app to open .html" dialogs.
- Lore nav links don't respond or open external prompts.
- Audio controls stuck on previous track after double-clicking a new one.
- Video errors after switching tabs.

Record any failures with screenshot + steps.
