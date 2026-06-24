# Manual Defaults Checklist (Save/Configuration Editors)

Run this after launching the C# app.

## Launch

```powershell
dotnet run --project ".\Onslaught - Career Editor.csproj"
```

## 1) Save Editor default safety state

1. Open `Saves -> Save Editor`.
2. Do not pick input yet.
3. Verify in **Patch Sections**:
   - `Mission Nodes` unchecked
   - `Mission Links` unchecked
   - `Goodies` unchecked
   - `Kill Counts` unchecked
   - `Kills Only Mode` unchecked
4. Expand **Advanced Options** and verify in **Copy Keybind/Global Settings From File**:
   - Source shows no selection placeholder
   - `Copy keybind entries (controls/actions)` unchecked + disabled
   - `Copy global settings tail (...)` unchecked + disabled

Expected: Safe edit baseline with no section pre-enabled.

## 2) Save Editor copy-source first selection behavior

1. In Save Editor advanced block, click `Browse...` for copy source.
2. Select any valid `.bes` (for example `save-attempts\haha-cannon-goes-brrrrr.bes`).
3. Verify:
   - `Copy keybind entries` remains unchecked (opt-in)
   - `Copy global settings tail` remains unchecked (opt-in)
   - Both checkboxes are now enabled
4. Click `Clear`.
5. Verify both checkboxes return to unchecked + disabled.

Expected: Save mode keeps copy options opt-in even after first source selection.

## 3) Configuration Editor default safety state

1. Open `Saves -> Configuration Editor`.
2. Verify career progression sections are hidden in configuration mode:
   - No mission/link/goodie/kill progression patch controls should be shown
3. In advanced copy block (before source selection):
   - Both copy checkboxes unchecked + disabled.

Expected: Career sections cannot be patched by accident in Configuration Editor.

## 4) Configuration Editor copy-source first selection behavior

1. In Configuration Editor advanced block, browse copy source and select same `.bes` file.
2. Verify:
   - `Copy keybind entries` auto-checks ON
   - `Copy global settings tail` stays OFF
   - both are enabled
3. Click `Clear` and verify both return unchecked + disabled.

Expected: Config mode enables entries by default on first source selection; tail remains opt-in.

## 5) Quick no-op patch guard (optional)

1. In Save Editor, keep all patch sections unchecked and leave copy source empty.
2. Pick a `.bes` input and output path.
3. Click Patch.

Expected: app warns that nothing is selected to patch (no output should be written).

## 6) Quick `.bea` scoping guard (optional)

1. In Save Editor, try loading a `.bea` file.
2. In Configuration Editor, try loading a `.bes` file.

Expected:
- Save Editor rejects `.bea` and prompts to use Configuration Editor.
- Configuration Editor rejects `.bes` and prompts to use Save Editor.
