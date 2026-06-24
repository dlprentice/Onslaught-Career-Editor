# Lane 02 Audit: C# Core / CLI / Save + Binary Patch Surfaces

Date: 2026-03-05
Scope: `Program.cs`, `BesFilePatcher.cs`, `BinaryPatchEngine.cs`, `AppConfig.cs`, WPF command surfaces tied to save/binary patch flows, and app-facing docs/help text.
Method: read-only code/doc review plus live probes against the existing built exe in `bin/Debug/net10.0-windows/Onslaught - Career Editor.exe`.
Note: `dotnet run` hit a transient WPF markup-cache lock during probing, so live CLI/help checks were done with the already-built exe instead.

## Findings

1. Medium: the binary patch catalog is documented as canonical, but the C# engine silently falls back to embedded specs if the catalog is missing or malformed.
   - Evidence: `patches/README.md:27-37` says `patches/catalog/patches.v2.json` is the canonical machine-readable authority consumed by C#.
   - Evidence: `BinaryPatchEngine.cs:37-89` embeds a full hardcoded fallback catalog, and `BinaryPatchEngine.cs:97-129` returns that fallback on missing file, parse failure, empty array, or any exception.
   - Risk: a packaging mistake or JSON drift can leave WPF patching with stale offsets/bytes while appearing healthy. Because the fallback is silent, maintainers get no signal that the documented authority was bypassed.

2. Medium: the C# CLI still emits Unicode box-drawing and checkmark glyphs, contradicting the roadmap claim that Unicode CLI characters were replaced with ASCII, and the live output still mojibakes in practice.
   - Evidence: `roadmap/technical-debt.md:16` and `lore-book/roadmap/technical-debt.md:16` mark this as completed: `Unicode CLI characters replaced with ASCII ([OK]/[X] instead of checkmark/X)`.
   - Evidence: `BesFilePatcher.cs:1425-1537` and `BesFilePatcher.cs:1549-1862` still emit `═`, `─`, `✓`, and `✗` in compare/analyze reports.
   - Live probe: running `bin/Debug/net10.0-windows/Onslaught - Career Editor.exe save-attempts/haha-cannon-goes-brrrrr.bes --analyze` produced mojibake separators/checkmarks instead of clean ASCII output.
   - Impact: user-facing CLI readability is degraded exactly on the Windows console/codepage path the roadmap item claimed was already fixed.

3. Medium: binary patch restore is a whole-file revert to the first saved backup, not a “undo last apply” operation, and the UI copy does not warn about clobbering later unrelated edits.
   - Evidence: `BinaryPatchEngine.cs:345-349` creates `BEA.exe.original.backup` only if it does not already exist.
   - Evidence: `BinaryPatchEngine.cs:373-387` restores by copying the backup file over the entire target exe.
   - Evidence: `Views/BinaryPatchesView.xaml:125-127` only says a backup is created once; `Views/BinaryPatchesView.xaml:111-115` / `Views/BinaryPatchesView.xaml.cs:238-255` label the action generically as `Restore Backup`.
   - Risk: if a user applies patches, then later makes unrelated binary edits, restore will roll the whole exe back to the older first-backup state and discard those later changes.

4. Low: the WPF Binary Patches surface still presents the patch family as “Display / Windowed Patches” even though the active stable set now includes extra-graphics and `cardid.txt` override behavior.
   - Evidence: `Views/BinaryPatchesView.xaml:44-55` titles the group `Display / Windowed Patches (Stable + Experimental)` and frames the explanatory copy around windowing.
   - Evidence: the same view exposes `unlock extra graphics features by default` and `ignore cardid.txt tweak overrides` at `Views/BinaryPatchesView.xaml:72-85`.
   - Evidence: repo docs describe the current surface more broadly: `README.RELEASE.md:42`, `patches/README.md:22-25`.
   - Impact: user-facing copy understates the actual patch surface and makes the non-windowing patches look like side effects of a windowing tool rather than first-class supported specs.

5. Low: save patch error wording is still `.bes`-specific even though `.bea/defaultoptions.bea` is a supported first-class workflow.
   - Evidence: `Program.cs:88-96` and `Program.cs:111-157` expose `.bes/.bea` as supported CLI inputs and options-file workflows.
   - Evidence: `BesFilePatcher.cs:368-376` still reports `Invalid .bes file` / `Invalid .bes version word`, and `BesFilePatcher.cs:369` says `career save file`.
   - Impact: when a `.bea` file fails validation, the user gets stale `.bes`/career-only wording from the core engine.

6. Low: core comments still point at stale or underspecified documentation paths, which weakens traceability for the save/keybind logic.
   - Evidence: `BesFilePatcher.cs:891` references `reverse-engineering/executable-analysis.md`, but that file is no longer present in the repo.
   - Evidence: `Program.cs:1345` references `ControlBindings.md` without a usable repo path; the actual doc now lives at `reverse-engineering/binary-analysis/functions/Controller.cpp/ControlBindings.md`.
   - Impact: future audits have to rediscover the evidence trail instead of following the inline references.

7. Low: the CLI’s manual fallback usage string does not match the generated `System.CommandLine` help command name.
   - Evidence: `Program.cs:535-537` prints `Usage: onslaught-career-editor ...` when required input is missing.
   - Live probe: `bin/Debug/net10.0-windows/Onslaught - Career Editor.exe --help` reports `Usage: Onslaught-CareerEditor [<input> [<output>]] [options]`.
   - Impact: minor command/help drift for packaged-exe users; the app currently presents two different command names depending on the failure/help path.

## Notes

- I did not find evidence that the current save-format docs are out of sync with the major C# save patch offsets/semantics; the main save-engine problems in this lane are copy/help drift and stale references, not obvious true-view offset regressions.
- Binary patch spec values in `BinaryPatchEngine.cs` and `patches/catalog/patches.v2.json` appear aligned for the currently shipped set.
