# Lane 05 - C# Parity Audit

Date: 2026-03-05
Scope: C# GUI/CLI/core drift against current repo truths for save semantics, binary patch catalog/behavior, release/readiness docs, and active feature set.

## Summary

The C# save/config core is mostly aligned with current repo truths: `.bes` vs `.bea` semantics, options-tail handling, same-path safety, and binary-patch verify-before-apply behavior all match the current canonical docs.

The main remaining drift is in the binary-patch/catalog surface and release/readiness curation:
- the WPF Binary Patches tab is not truly catalog-driven even though `patches.v2.json` is documented as canonical,
- release/readiness artifacts still ship shelved C# prototype surfaces,
- release/readiness artifacts still include the dormant `CardIdPresetEngine.cs` lane even though cardid companion controls are shelved from the active app,
- one parity doc row still overstates Save Analyzer completeness.

## Findings (severity-ordered)

### 1. High - The C# Binary Patches surface is not actually catalog-driven; catalog v2 metadata and identity checks are documented but not consumed/enforced.

Evidence:
- `patches/README.md:27-37` declares `patches/catalog/patches.v2.json` the canonical machine-readable patch catalog and says it is consumed by the C# `BinaryPatchEngine` / WPF Binary Patches tab.
- `patches/catalog/patches.v2.json:7-30`, `:34-57`, `:60-83`, `:86-109` carry richer v2 fields such as `target_binary_hashes`, `purpose`, `preconditions`, `side_effects`, `rollback_strategy`, `verification_probe`, `confidence`, and `evidence_refs`.
- `BinaryPatchEngine.cs:10-17` defines `BinaryPatchSpec` with only `Key`, `Track`, `DisplayName`, `FileOffset`, `Original`, `Patched`, and `Optional`.
- `BinaryPatchEngine.cs:175-210` only parses `id`, `title`, `track`, `file_offset`, `expected_original_bytes`, `patched_bytes`, and `optional`; all other catalog fields are ignored.
- `BinaryPatchEngine.cs:305-397` verifies/applies patches by checking only the selected byte span at the file offset; there is no whole-binary identity/hash gate despite the catalog carrying `target_binary_hashes` and retail-layout preconditions.
- `Views/BinaryPatchesView.xaml.cs:52-90` hardcodes the visible patch keys one by one.
- `Views/BinaryPatchesView.xaml:71-99` hardcodes the checkbox labels/tooltips instead of rendering them from catalog metadata.

Impact:
- Adding or changing a patch row in `patches.v2.json` does not automatically update the WPF surface.
- Changing catalog metadata (`purpose`, `preconditions`, `confidence`, `evidence_refs`) has no user-visible effect in C#.
- The documented retail-layout precondition is advisory only in C#; the engine will patch any file whose bytes happen to match at the listed offsets.

### 2. Medium - Release/readiness scope still includes shelved C# prototype tabs that are no longer part of the active app surface.

Evidence:
- `roadmap/csharp-python-parity.md:20-21` says `Goodie Viewer` and `Asset Browser` are shelved and removed from the active UI.
- `MainWindow.xaml:101-131` shows the active WPF shell tabs: `Saves`, `Media`, `Lore`, `Binary Patches`, `Settings`; there is no routed Goodie Viewer or Asset Browser tab.
- `Views/AssetBrowserView.xaml.cs:16-18` and `Views/GoodieViewerView.xaml.cs:13-15` show the prototype C# views still exist in-tree.
- `release/readiness/public_candidate_allowlist.tsv:25-26` and `:33-34` still include `Views/AssetBrowserView.*` and `Views/GoodieViewerView.*` in the public candidate set.

Impact:
- Public/release-facing scope still ships inactive prototype UI code that the current app no longer exposes.
- That is likely to confuse contributors about what is supported vs intentionally shelved.

### 3. Medium - Release/readiness artifacts still include `CardIdPresetEngine.cs` even though the active C# path is the binary-patch lane and cardid companion controls are shelved.

Evidence:
- `roadmap/csharp-python-parity.md:18` says the Binary Patches tab is complete and that cardid companion controls are intentionally shelved from the active UI.
- `CardIdPresetEngine.cs:15-18` shows a standalone cardid preset engine still present in the C# root.
- `MainWindow.xaml:101-131` and `Views/BinaryPatchesView.xaml.cs:52-90` show the active WPF surface only wires the byte-verified BEA.exe patch set, not a visible cardid preset lane.
- `release/readiness/public_candidate_allowlist.tsv:11` and `roadmap/release-allowlist-profile.md:31-34` still include `CardIdPresetEngine.cs` in the public candidate set.

Impact:
- Release/readiness docs still advertise a dormant C# core surface that is not part of the active UI contract.
- This is a curation drift rather than a runtime bug, but it increases release noise and support ambiguity.

### 4. Low - The parity doc still overstates Save Analyzer completeness while acknowledging a real C# gap.

Evidence:
- `roadmap/csharp-python-parity.md:16` marks `Save Analyzer` as `COMPLETE` but immediately notes that Python includes an explicit path row while C# currently does not.
- `Views/SaveAnalyzerView.xaml.cs:180-223` builds the C# summary tree with file size, version, file kind, volumes, options-tail fields, etc., but no explicit full-path row in the summary tree itself.
- `Views/SaveAnalyzerView.xaml:51-69` does expose the selected path in the left-side input textbox, so the gap is presentation parity rather than missing data.

Impact:
- This is a documentation/parity-label drift, not a core correctness issue.
- The current doc should describe Save Analyzer as complete with a minor presentation delta, or mark the delta as an explicit remaining polish item.

## Areas checked with no material drift found

### Save format semantics
- `BesFilePatcher.cs:78-86` and `:1568-1615` align with the current repo truths for the options entries + fixed 0x56-byte tail snapshot, defaultoptions boot semantics, and `.bes` volume/keybind caveats.
- `Views/SaveEditorView.xaml:499`, `:675-735` and `Views/SaveEditorView.xaml.cs:744-809` correctly warn that `defaultoptions.bea` is authoritative at boot for keybinds and most globals.
- `Program.cs:158-160` and `:730-750` correctly keep `--allow-career-sections-on-options-file` as an explicit advanced override instead of default behavior.

### Configuration Editor same-path safety
- `Views/SaveEditorView.xaml.cs:939-1009` correctly blocks in-place patching for normal `.bes` save flow, but allows in-place `.bea` patching only in Configuration mode with a confirmation prompt and timestamped `.bak` backup.
- `Views/SaveEditorView.xaml.cs:2003-2032` reflects the same state in the UI status logic.
- `release/readiness/LOCAL_SIGNOFF_COMMANDS.md:67-71` matches the current WPF behavior for `.bea` in-place patching and BEA.exe verify/apply/restore.

### Binary patch safety basics
- `Views/BinaryPatchesView.xaml.cs:122-136`, `:160-196`, and `:281-321` correctly require selection validation and a fresh verify pass before apply.
- `BinaryPatchEngine.cs:345-397` and `:400-414` correctly use a single full-file `BEA.exe.original.backup` snapshot for restore.

## Recommended main-agent follow-up

1. Decide whether `patches.v2.json` should remain the true public contract.
   - If yes: make the WPF surface data-driven from catalog rows and either enforce or explicitly de-scope `target_binary_hashes` / metadata fields.
   - If no: narrow the docs so they describe the current byte-row-only implementation honestly.
2. Tighten release curation so shelved C# prototype files and dormant `CardIdPresetEngine.cs` are either excluded or explicitly labeled as inactive/internal.
3. Fix the parity doc wording for Save Analyzer completeness.
