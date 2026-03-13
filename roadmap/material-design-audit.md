# Material Design Audit

> Historical note (2026-03-07): this audit documents the retired WPF/Python design direction that was superseded by the WinUI 3 rewrite.

**Date:** 2026-03-06  
**Status:** C# app now uses Material Design for buttons and base controls; Python palette aligned with C# theme.  
**Last implementation:** 2026-03-06 — Phase 1–2–4 complete (see changelog below).

---

## 1. Executive Summary

**Verdict:** The C# WPF app loads Material Design at the application level but **overrides it with custom styles** for virtually all controls. The app is **not** "totally using Material Design XAML." The Python GUI uses Qt Fusion style with a custom light palette and has no Material Design integration.

| Stack | Material Design Status | Notes |
|-------|------------------------|-------|
| C# WPF | Partial (theme only) | BundledTheme + MaterialDesign3.Defaults loaded; all control styles overridden |
| C# CLI | N/A | Console output only |
| Python GUI | None | Fusion + `onslaught.gui.theme.apply_light_theme()` |
| Python CLI | N/A | Console output only |

---

## 2. C# WPF: Extent of Non–Material Design Usage

### 2.1 What *Is* Using Material Design

| Location | Usage |
|----------|-------|
| `App.xaml` | `materialDesign:BundledTheme` (Light, Teal, Lime) |
| `App.xaml` | `MaterialDesign3.Defaults.xaml` merged |
| `App.xaml` | `Style TargetType="Window" BasedOn="{StaticResource MaterialDesignWindow}"` |

**Total:** 3 references, all in `App.xaml`. No View XAML files use the `materialDesign:` namespace.

### 2.2 What Overrides Material Design

`App.xaml` defines **implicit styles** (no `x:Key`) for standard WPF controls. These override Material Design’s defaults because they appear later in the resource lookup chain:

| Control | App.xaml Style | Effect |
|---------|----------------|--------|
| `Button` | Custom (padding, colors, triggers) | Replaces Material Design button |
| `TextBox` | Custom (padding only) | Replaces Material Design text field |
| `ComboBox` | Custom (padding, MinHeight) | Replaces Material Design combo |
| `CheckBox` | Custom (margin) | Replaces Material Design checkbox |
| `Menu` / `MenuItem` | Custom | Replaces Material Design menu |
| `TreeView` | Custom (transparent bg, no border) | Replaces Material Design tree |
| `DataGrid` | Custom (row colors, gridlines) | Replaces Material Design data grid |
| `TabControl` / `TabItem` | Custom `RoundedTabItemTemplate` | Replaces Material Design tabs |
| `GroupBox` | Custom `SectionGroupBoxStyle` | Replaces Material Design card/group |
| `Expander` | Custom | Replaces Material Design expander |

### 2.3 Custom Color Palette (Not Material Design Tokens)

`App.xaml` defines 15+ custom colors and brushes that shadow Material Design’s theme tokens:

- `PageBackgroundColor`, `SurfaceColor`, `SurfaceMutedColor`, etc.
- `AccentColor`, `AccentDarkColor`, `WarmAccentColor`, `SuccessColor`, `DangerColor`
- `TabInactiveBackgroundColor`, `TabActiveBackgroundColor`, etc.
- `HeroBrush` (linear gradient)

Material Design provides `MaterialDesign.Brush.Primary`, `MaterialDesign.Brush.Background`, etc. These are not used.

### 2.4 View-Level Usage

| View | Controls Used | Material Design Controls |
|------|---------------|--------------------------|
| `MainWindow.xaml` | Border, TextBlock, TabControl, TabItem | 0 |
| `SaveEditorView.xaml` | GroupBox, TextBlock, ComboBox, Button, TextBox, CheckBox, Border, etc. | 0 |
| `SaveAnalyzerView.xaml` | GroupBox, ComboBox, Button, TextBox, TreeView, etc. | 0 |
| `ConfigurationEditorView.xaml` | Same pattern | 0 |
| `BinaryPatchesView.xaml` | GroupBox, Button, TextBox, CheckBox, Border | 0 |
| `SettingsView.xaml` | GroupBox, TextBox, Button, CheckBox, etc. | 0 |
| `LoreBrowserView.xaml` | TreeView, WebView2, Button | 0 |
| `AudioPlayerView.xaml` | TreeView, Button, etc. | 0 |
| `VideoPlayerView.xaml` | LibVLCSharp, Button | 0 |
| `AboutView.xaml` | TextBlock, Button | 0 |

**Total `materialDesign:` usages in Views:** 0.

---

## 3. Layout and Design Audit

### 3.1 Layout Structure (Good)

- Clear hierarchy: Window → TabControl → UserControl views
- Consistent use of `Grid`, `StackPanel`, `ScrollViewer`
- `Grid.IsSharedSizeScope` for aligned columns across sections
- Sensible margins and padding

### 3.2 Design Inconsistencies

| Issue | Location | Recommendation |
|-------|----------|-----------------|
| Hardcoded colors | `SettingsView.xaml` uses `Foreground="#666"` | Use `MutedTextBrush` or Material Design tokens |
| Inconsistent button padding | Some `Padding="15,5"`, others `Padding="12,4"` | Standardize or use Material Design buttons |
| Custom tab template | `RoundedTabItemTemplate` diverges from Material Design tabs | Use `materialDesign:TabControl` or Material Design tab styles |
| Hero banner | Custom `HeroBrush` gradient | Consider Material Design app bar / top app bar |
| Callout borders | `InfoCalloutBorderStyle`, `WarningCalloutBorderStyle` | Material Design has `Card`, `Alert`-style components |

### 3.3 Accessibility (Good)

- `AutomationProperties.Name` on key controls
- `AccessibleFocusVisualStyle` for keyboard focus
- `KeyboardNavigation.TabNavigation="Local"` on tab controls

---

## 4. Python GUI: Design System Status

### 4.1 Current Stack

- **Style:** `QStyleFactory.create("Fusion")`
- **Theme:** `onslaught.gui.theme.apply_light_theme(app)` — custom `QPalette` with:
  - `WINDOW_BG = "#f7f8fa"`
  - `ACCENT_COLOR = "#0078D4"`
  - `TEXT_COLOR`, `SUBTLE_TEXT`, etc.

### 4.2 Material Design

- PyQt6 does not ship Material Design.
- Options for a Material-like look:
  - **qt-material** (third-party)
  - **Custom QSS** that mimics Material Design
  - **Fusion + tuned palette** (current approach) — visual parity only, not true Material Design

### 4.3 Parity with C# WPF

- **Functional parity:** Documented as COMPLETE in `roadmap/csharp-python-parity.md`.
- **Visual parity:** Both use light themes and similar accent colors, but different frameworks (WPF vs Qt).
- **Design system parity:** Neither stack uses a shared Material Design implementation.

---

## 5. Recommendations

### 5.1 To Achieve Full Material Design in C# WPF

**Phase 1: Stop Overriding Material Design**

1. Remove or refactor implicit styles in `App.xaml`:
   - Either delete `TargetType="Button"`, `TargetType="TextBox"`, etc., and rely on Material Design defaults
   - Or change them to `BasedOn="{StaticResource MaterialDesignRaisedButton}"` (and equivalents) and only set app-specific overrides
2. Replace custom colors with Material Design tokens:
   - `{DynamicResource MaterialDesign.Brush.Primary}`
   - `{DynamicResource MaterialDesign.Brush.Background}`
   - etc.
3. Remove `HeroBrush` and custom tab template, or align them with Material Design components.

**Phase 2: Use Material Design Controls Where Appropriate**

1. Add `xmlns:materialDesign="http://materialdesigninxaml.net/winfx/xaml/themes"` to views.
2. Replace standard controls with Material Design variants where they add value:
   - `materialDesign:Button` (e.g. `Style="Primary"`, `Style="Outlined"`)
   - `materialDesign:TextField` for text inputs
   - `materialDesign:ComboBox` for dropdowns
   - `materialDesign:Card` for callouts/sections
   - `materialDesign:TabControl` for tabs (or keep WPF `TabControl` with Material Design styles)
3. Use `materialDesign:Snackbar` or `materialDesign:DialogHost` for notifications/modals if needed.

**Phase 3: Layout Adjustments**

1. Replace hardcoded `#666` and similar with theme brushes.
2. Standardize spacing using Material Design density (e.g. 8dp grid).
3. Consider `materialDesign:Card` for section containers instead of `GroupBox` + `Border`.

### 5.2 Python GUI Parity Options

**Option A: Visual Parity Only (Current)**

- Keep Fusion + custom palette.
- Tune Python palette to match C# colors (e.g. Teal primary if C# moves to Material Design Teal).
- Document that both use “light theme, similar accents” but different frameworks.

**Option B: Material Design–Inspired for Python**

- Add **qt-material** or similar and apply a Material-style theme.
- Align primary/secondary colors with C# Material Design theme.
- Document as “Material Design–inspired” for Python.

**Option C: Shared Design Tokens**

- Define a small shared spec (e.g. JSON or Markdown) with:
  - Primary/secondary colors
  - Spacing scale
  - Typography (font, sizes)
- C# maps to Material Design tokens; Python maps to QPalette/QSS.
- Keeps functional parity and improves visual consistency without forcing the same UI framework.

### 5.3 Suggested Priority Order

1. **High:** Fix C# implicit style overrides so Material Design defaults apply (Phase 1).
2. **High:** Replace hardcoded colors in views with theme resources.
3. **Medium:** Introduce Material Design controls in high-traffic views (Save Editor, Binary Patches).
4. **Medium:** Align Python palette with C# Material Design colors for visual consistency.
5. **Low:** Evaluate qt-material or shared design tokens for Python.

---

## 6. Implementation Changelog (2026-03-06)

### Phase 1: Button styles
- Removed implicit `TargetType="Button"` override; Material Design defaults now apply to plain buttons.
- `PrimaryButtonStyle` now `BasedOn="{StaticResource MaterialDesignRaisedButton}"`.
- `SuccessButtonStyle`, `WarmButtonStyle` `BasedOn` MaterialDesignRaisedButton with semantic color overrides.

### Phase 2: Hardcoded colors
- Replaced hardcoded `#666`, `#CCCCCC`, `#F9F9F9`, etc. in SettingsView, SaveAnalyzerView, LoreBrowserView, AudioPlayerView, VideoPlayerView, GoodieViewerView, AssetBrowserView with `StaticResource` theme brushes (MutedTextBrush, CardBorderBrush, SurfaceMutedBrush, PageBackgroundBrush).

### Phase 4: Python palette
- `onslaught/gui/theme.py`: ACCENT_COLOR → Teal #009688 (Material Design primary); WINDOW_BG, TEXT_COLOR, SUBTLE_TEXT, AlternateBase, Button aligned with App.xaml palette.

### Remaining (Phase 3 deferred)
- Material Design Card/TextField controls in views; custom tab template still in use.

---

## 7. References

- [Material Design in XAML Toolkit – Getting Started](https://github.com/MaterialDesignInXAML/MaterialDesignInXamlToolkit/wiki/Getting-Started)
- [Material Design 3 Defaults](https://github.com/MaterialDesignInXAML/MaterialDesignInXamlToolkit) (MaterialDesign3.Defaults.xaml)
- `roadmap/csharp-python-parity.md` — functional parity status
- `onslaught/gui/theme.py` — Python light theme
