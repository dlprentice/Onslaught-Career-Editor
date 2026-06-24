# Lane 03 - WPF Analyzer / Configuration UX Audit

## Scope
- `Views/SaveAnalyzerView.xaml`
- `Views/SaveAnalyzerView.xaml.cs`
- `Views/ConfigurationEditorView.xaml`
- `Views/ConfigurationEditorView.xaml.cs`

## Semantic Baseline Used For Audit
Current repo truth is that `defaultoptions.bea` is the boot/global authority for keybinds and most global settings, while `.bes` carries stored copies that are not applied the same way at load time (`AGENTS.md:158-167`). The analyzer/configuration UX should therefore make the `.bea` vs `.bes` distinction explicit and hard to miss.

## Findings

### 1. High - Save Analyzer still under-explains `.bes` vs `.bea` runtime authority
- Refs: `Views/SaveAnalyzerView.xaml:94-95`, `Views/SaveAnalyzerView.xaml:100-115`, `Views/SaveAnalyzerView.xaml:200-202`, `Views/SaveAnalyzerView.xaml.cs:151-153`, `Views/SaveAnalyzerView.xaml.cs:197-223`
- Why it matters: the current UI says “choose a `.bes` or `.bea` file to inspect” and switches the mode text between “`.bea` global settings view” and “`.bes` career save view”, but it never clearly tells the user that `.bea` is the boot/global settings source while `.bes`-stored options are often not applied directly on load. The left summary also lists volumes, options entries, control-scheme index, mouse sensitivity, and screen shape as if they are equally authoritative in both file types.
- Recommended fix: add a persistent callout above the summary/output that explicitly states:
  - `.bea`: boot/global settings authority.
  - `.bes`: carries saved copies of options/global fields, but many of those are not runtime-authoritative on direct save load.
  - when relevant, note that frontend flows may later write `.bes` values back into `defaultoptions.bea`.
- Recommended UI treatment: split the options section into “Stored in file” vs “Runtime-effective on boot” wording instead of leaving the distinction implicit.

### 2. Medium - The analyzer currently exposes three overlapping refresh models
- Refs: `Views/SaveAnalyzerView.xaml:72-96`, `Views/SaveAnalyzerView.xaml.cs:66-80`, `Views/SaveAnalyzerView.xaml.cs:104-112`, `Views/SaveAnalyzerView.xaml.cs:446-469`
- Why it matters: selecting a detected file auto-runs analysis, browsing a file also auto-runs analysis, and the view still shows both `Analyze` and `Analyze Again`. That makes the interaction model feel indecisive and leaves users wondering which action is actually authoritative.
- Recommended fix: choose one model and make it obvious.
  - Best option: keep auto-analysis on file selection/open, then replace the second button set with a single `Refresh Report` action.
  - Alternate option: remove auto-analysis and require explicit `Analyze`.
- UX note: the helper copy at `Views/SaveAnalyzerView.xaml:94-95` is compensating for control ambiguity that the layout itself should remove.

### 3. Medium - The left-hand summary leads with raw/internal terminology instead of user meaning
- Refs: `Views/SaveAnalyzerView.xaml.cs:179-223`, `Views/SaveAnalyzerView.xaml.cs:309-327`
- Why it matters: entries like `Header dword view @0x0000`, `NewGoodieCount`, `Options entries`, and `tail @ 0x...` are valuable for reverse-engineering work, but they are not the first things a normal user needs from an analyzer. Presenting those raw terms at top level increases cognitive load and makes the view feel more forensic than practical.
- Recommended fix: reserve raw headers/offset-heavy details for an advanced subtree or show them only when the advanced dump option is enabled. Default summary order should prioritize:
  1. file kind / authority (`.bes` vs `.bea`)
  2. mission progress / ranks
  3. goodies / kill counts
  4. effective settings summary
  5. advanced/raw storage details

### 4. Medium - Compare mode wording is technically correct but not task-oriented enough
- Refs: `Views/SaveAnalyzerView.xaml:118-160`, `Views/SaveAnalyzerView.xaml.cs:378-434`
- Why it matters: the compare area is useful for verifying “original vs patched” files, but the current wording stays generic (“Compare Files”, “byte-by-byte”, “regions with differences”). It does not guide users toward the actual workflows this tool is good for.
- Recommended fix: reword the compare section around likely tasks:
  - “Compare original vs patched file”
  - “Confirm what changed after patching”
  - “See which save regions differ”
- Recommended detail tweak: when comparison involves a `.bea`, mention that the diff may reflect global-options authority rather than career-progress changes.

### 5. Medium - `ConfigurationEditorView` is only a thin wrapper, so it cannot present a genuinely configuration-first UX
- Refs: `Views/ConfigurationEditorView.xaml:9-10`, `Views/ConfigurationEditorView.xaml.cs:12-26`
- Why it matters: the tab name suggests a dedicated editor for `defaultoptions.bea` / global settings, but the implementation is just `SaveEditorView` hosted raw with a late mode switch. That means the tab cannot own its own introductory framing, section order, or configuration-specific warnings without relying on internal behavior inside another control.
- Recommended fix: either:
  - give `ConfigurationEditorView` its own shell (header + explanatory callout + hosted editor below), or
  - refactor `SaveEditorView` so configuration mode can provide a dedicated template/visual arrangement instead of only hiding unrelated sections.
- Minimum acceptable fix: add configuration-specific explanatory chrome in the wrapper so the user immediately understands that this tab is for `.bea`-style global settings rather than career progress.

### 6. Low - Configuration mode is applied later than it needs to be
- Refs: `Views/ConfigurationEditorView.xaml.cs:12-20`, `Views/ConfigurationEditorView.xaml.cs:23-26`
- Why it matters: applying `EditorMode` only on `Loaded` makes the wrapper feel bolted on and can expose the generic save-editor state during first render or UI automation timing.
- Recommended fix: set `SaveEditorControl.EditorMode = SaveEditorMode.Configuration;` immediately after `InitializeComponent()`, and keep `Loaded` only for any post-layout work that truly needs it.

## Recommended Fix Order
1. Fix the `.bes` vs `.bea` authority messaging in `SaveAnalyzerView` first.
2. Simplify the analyzer action model (`Analyze` / `Analyze Again` / auto-analyze).
3. Move raw RE/storage details behind a more obviously advanced presentation.
4. Give `ConfigurationEditorView` its own explanatory shell or a dedicated configuration-mode template.
5. Apply the mode switch earlier in the configuration wrapper lifecycle.

## Bottom Line
The current analyzer is mechanically functional, but it still explains file structure better than runtime truth. The configuration tab is also conceptually right but visually/architecturally too thin to feel like a first-class tool.
