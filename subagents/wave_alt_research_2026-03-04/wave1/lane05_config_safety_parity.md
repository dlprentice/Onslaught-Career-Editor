# Lane 05 - Configuration Safety/Parity Re-evaluation (Read-Only)

Date: 2026-03-04
Scope: `Program.cs`, `patcher.py`, `Views/SaveEditorView.xaml.cs`, `onslaught/gui/tabs/save_editor.py`, parity docs (`README.MD`, `roadmap/csharp-python-parity.md`, `CURRENT_CAPABILITIES.md`, `roadmap/status-current.md`).

## Current-State Safety Matrix

| Surface | `.bes/.bea` workflow safety | Same-path handling | Backup semantics |
|---|---|---|---|
| C# CLI (`Program.cs`) | Blocks career-section patching on options-like files unless explicit override (`--allow-career-sections-on-options-file`) (`Program.cs:769-792`) | Hard-blocks same-path patching (`Program.cs:628-634`) | None (write-to-new-path only) |
| Python CLI (`patcher.py`) | Same options-file guard + override contract (`patcher.py:1958-1967`) | Hard-blocks same-path in CLI preflight and patch engine (`patcher.py:1910-1914`, `patcher.py:639-640`) | None (write-to-new-path only) |
| C# GUI Save/Config (`Views/SaveEditorView.xaml.cs`) | Configuration mode hides/disables career sections (`Views/SaveEditorView.xaml.cs:133-141`, `201-227`); save/config mode path class is enforced (`Views/SaveEditorView.xaml.cs:656-668`, `825-837`) | Save mode blocks same-path; Configuration mode explicitly allows same-path with confirmation (`Views/SaveEditorView.xaml.cs:928-945`, `947-963`, `1997-2008`) | In-place Configuration mode creates timestamped `.bak` before replace (`Views/SaveEditorView.xaml.cs:1004-1009`) |
| Python GUI Save/Config (`onslaught/gui/tabs/save_editor.py`) | Configuration mode disables career sections and enforces `.bea` input/output (`onslaught/gui/tabs/save_editor.py:556-586`, `1057-1069`) | Same-path always blocked, including Configuration mode (`onslaught/gui/tabs/save_editor.py:705-711`, `1073-1075`) | No `.bak` path in Save/Config flow |

## Re-evaluated Options

| Option | Description | Safety impact | Parity clarity | Cost/risk |
|---|---|---|---|---|
| A | Keep current divergence (C# config in-place + `.bak`; Python config no in-place) | Medium: both are safe, but user expectations differ by stack | Weak: “core parity” messaging stays noisy because same task behaves differently | Low code churn, ongoing docs/test burden |
| B | **Standardize on GUI safe in-place for Configuration mode in both stacks** (same-path allowed only for config, with confirm + temp patch + timestamped `.bak`) while keeping CLI same-path hard-block | **High**: direct `defaultoptions.bea` workflow keeps rollback guarantee and avoids manual replace without backup | **Strong**: one GUI rule, one CLI rule | Medium implementation and test work (mainly Python GUI) |
| C | Standardize on strict no in-place everywhere (C# GUI aligned down to Python/CLI model) | High for “never overwrite in tool”; lower ergonomic safety because users manually replace `defaultoptions.bea` later (often without structured backup) | Strong and simple | Medium product behavior change in primary C# UX |

## Recommendation

Recommendation: **Option B remains the best choice** for this lane’s objective (“standardized safe-mode configuration behavior across C#/Python”).

Why:
- It preserves the strongest practical rollback posture for the common `.bea` use case by making backup creation automatic at the point of replacement.
- It keeps save workflow safety strict (`.bes` same-path still blocked), and keeps CLI automation safety strict (no in-place in either CLI).
- It removes the most visible cross-stack parity drift currently documented in multiple places.

## Required Guardrails If Option B Is Adopted

1. Keep patch-engine invariants unchanged (`BesFilePatcher.PatchFile` / `patcher.patch_file` continue to reject same-path); implement in-place only as GUI wrapper flow (temp output -> backup -> replace).
2. Mirror C# confirmation/backup semantics in Python Configuration Editor only; keep Save mode same-path blocked.
3. Add parity tests for:
   - Config mode same-path allowed + `.bak` created.
   - Save mode same-path blocked.
   - Failure path leaves temp/output discoverable and does not silently discard patched bytes.
4. Clarify docs explicitly: “GUI Configuration mode supports safe in-place with backup; CLI always requires separate output path.”

## Parity-Doc Clarity Notes

- Current docs already acknowledge part of this divergence:
  - `README.MD:64`
  - `roadmap/csharp-python-parity.md:17`
- Broader status docs still use “core parity active” framing and should keep this caveat visible to avoid drift/confusion:
  - `CURRENT_CAPABILITIES.md:21-24`
  - `roadmap/status-current.md:21`

## Confidence

Confidence: **0.86** (high) based on direct code-path alignment checks across all four scoped implementations.
