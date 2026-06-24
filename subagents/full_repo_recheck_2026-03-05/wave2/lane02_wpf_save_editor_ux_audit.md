# WPF Save Editor UX Audit

## Positives
- PASS | `Views/SaveEditorView.xaml:206` | Save mode defaults to `Safe Edit`, not `Quick Unlock`.
- PASS | `Views/SaveEditorView.xaml.cs:124` | Configuration mode hides career-only sections and relabels the patch action, which is the right direction for scope separation.

## Findings
- HIGH | `Views/SaveEditorView.xaml.cs:1995` | `Patch` enables on file validity alone, not on whether the user has actually selected any mutation. In `Safe Edit`, a user can click through and generate a no-op patched save; in Configuration mode that can mean an unnecessary in-place write/backup cycle. | Add a computed `HasPendingChanges` gate and disable `Patch` until at least one section, override, copy option, or keybind edit is active. Surface a short “Pending changes” summary next to the button.
- HIGH | `Views/SaveEditorView.xaml.cs:1079` | Selecting a copy-source in Configuration mode silently turns on `Copy keybind entries` by default. That is a hidden write behavior: browsing for a source file changes what `Patch` will do without a direct explicit opt-in. | Keep both copy checkboxes off by default in all modes, or show an immediate inline banner that states exactly what was auto-enabled and requires acknowledgment.
- HIGH | `Views/SaveEditorView.xaml.cs:689` | Output-path semantics change by mode, but the UI does not explain that near the field. Save mode auto-generates `_patched`; Configuration mode defaults to the original file path and patches in place after confirmation. Users have to infer that from status text or the confirm dialog. | Add a mode-specific helper line directly under `Output File` and, in Configuration mode, expose an explicit `Patch in place (create .bak backup)` choice instead of silently defaulting to the same path.
- MEDIUM | `Views/SaveEditorView.xaml:262` | High-value workflows are buried behind a master `Show advanced overrides` checkbox and then hidden again inside collapsed expanders (`Career Progress Overrides`, `Keybind and Global Settings Overrides`). Per-mission editing and configuration cloning are too easy to miss. | Replace the master reveal with always-visible section cards, or auto-expand the relevant block after file load. At minimum, add a compact advanced section index with buttons like `Per-Mission Ranks`, `Kill Overrides`, `Keybinds`, `Global Settings`.
- MEDIUM | `Views/SaveEditorView.xaml:628` | `Controller Config (P1/P2)` is exposed as a raw numeric index with no range, no friendly preset names, and no inline explanation of what values are known-good. This gives users too much rope. | Replace the raw text box with a preset-backed combo where possible, or add strict validation plus a nearby lookup/help text showing known configuration IDs and safe examples.
- MEDIUM | `Views/SaveEditorView.xaml:777` | The keybind area mixes three mental models: `slot0/slot1`, `left/right in-game column`, and `Player 1/Player 2`. The mapping is accurate, but the terminology is split across a note, column headers, and status text, which increases user doubt. | Collapse this to one labeling system in the grid header itself, e.g. `Player 1 (Left In-Game Column)` and `Player 2 (Right In-Game Column)`, and remove the need to reconcile separate notes.
- MEDIUM | `Views/SaveEditorView.xaml:497` | Several critical explanations are written as long prose blocks (`Steam build` note, copy-source explanation, keybind token explanation). The content is correct but cognitively heavy in a dense desktop form. | Convert long notes into short bullet callouts with headings like `What applies immediately`, `What only applies on next boot`, and `What this section copies`. Keep the detailed wording in tooltips or docs, not in the primary scan path.

## Recommended Fix Order
1. Gate `Patch` on real pending changes and add a visible pending-changes summary.
2. Remove the hidden auto-enable behavior for copy-source defaults.
3. Make output-path behavior explicit, especially Configuration-mode in-place patching.
4. Flatten advanced-section discoverability.
5. Replace or harden raw controller-config entry.
6. Unify keybind terminology and shorten the prose-heavy help blocks.
