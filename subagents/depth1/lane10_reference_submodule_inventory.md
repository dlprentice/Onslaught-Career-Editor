# Summary

- The repo declares and pins two reference submodules in [`.gitmodules`](../../.gitmodules):
  - `references/Onslaught` @ `792545b996365f383781c666d145ea6cbda83f3a`
  - `references/AYAResourceExtractor` @ `fee6623854e8214f2ecddf404219ed5b0db823db`
- `references/Onslaught` is a high-impact **documentation/reverse-engineering** dependency (many RE docs cite it), but it is not directly referenced by active app runtime code paths.
- `references/AYAResourceExtractor` has explicit **integration hooks** in dormant Asset Browser implementations (C# and PyQt), but is not part of the active tab shells and is not a compile-time dependency of the main app solution.

# Dependency Touchpoints

## Submodule registration and baseline metadata

- [`.gitmodules`](../../.gitmodules:1) registers both submodules and URLs.
- [`AGENTS.md`](../../AGENTS.md:331) documents expectations for both reference repos, including:
  - AYA extractor build/toolchain assumptions and local fix notes.
  - Onslaught source mismatch warning (internal build vs retail Steam behavior).

## Runtime/app-code touchpoints

### `references/AYAResourceExtractor` (direct code path references)

- C# WPF asset browser hardcodes extractor executable candidates and repo paths:
  - [`Views/AssetBrowserView.xaml.cs`](../../Views/AssetBrowserView.xaml.cs:30)
  - Repo root discovery relies on `references/AYAResourceExtractor` presence: [`Views/AssetBrowserView.xaml.cs`](../../Views/AssetBrowserView.xaml.cs:653)
  - Extraction/launch UX points users to build folder under submodule: [`Views/AssetBrowserView.xaml.cs`](../../Views/AssetBrowserView.xaml.cs:226)
- PyQt asset browser mirrors the same assumptions:
  - [`onslaught/gui/tabs/asset_browser.py`](../../onslaught/gui/tabs/asset_browser.py:182)
  - Exe candidate resolution under `references/AYAResourceExtractor/Code/AyaResourceExtractor/bin/...`: [`onslaught/gui/tabs/asset_browser.py`](../../onslaught/gui/tabs/asset_browser.py:252)
- Current mount status of these hooks is dormant/shelved:
  - WPF main tabs do not include `AssetBrowserView`: [`MainWindow.xaml`](../../MainWindow.xaml:48)
  - PyQt main window does not add `AssetBrowserTab`: [`onslaught/gui/main_window.py`](../../onslaught/gui/main_window.py:70)
  - Repo guidance explicitly says Asset/Goodie viewer tabs are shelved: [`AGENTS.md`](../../AGENTS.md:22), [`CURRENT_CAPABILITIES.md`](../../CURRENT_CAPABILITIES.md:84)

### `references/Onslaught` (active runtime code references)

- No direct `.cs`/`.py` runtime references were found to `references/Onslaught`.
- Practical dependency is through RE/docs evidence, not through executable wiring.

## Documentation/research touchpoints

### `references/Onslaught` (primary RE evidence source)

- Broad citation footprint across RE docs (including save-format and function-level mapping docs).
- Representative anchors:
  - Save format and slot/controller mapping references: [`reverse-engineering/save-file/save-format.md`](../../reverse-engineering/save-file/save-format.md:206)
  - Grade conversion logic source mapping: [`reverse-engineering/save-file/grade-system.md`](../../reverse-engineering/save-file/grade-system.md:31)
  - Goodie unlock logic mapping: [`reverse-engineering/save-file/goodies-system.md`](../../reverse-engineering/save-file/goodies-system.md:204)
  - Career graph structural source mapping: [`reverse-engineering/save-file/career-graph.md`](../../reverse-engineering/save-file/career-graph.md:5)
  - Semantic audit explicitly checks `references/Onslaught` citation integrity at scale: [`reverse-engineering/binary-analysis/semantic-audit-2026-02-12.md`](../../reverse-engineering/binary-analysis/semantic-audit-2026-02-12.md:3)

### `references/AYAResourceExtractor` (asset workflow and parity docs)

- Source-code inventory explicitly tracks AYA submodule corpus:
  - [`reverse-engineering/source-code/_index.md`](../../reverse-engineering/source-code/_index.md:27)
  - [`reverse-engineering/source-code/source-file-inventory.md`](../../reverse-engineering/source-code/source-file-inventory.md:11)
- App/roadmap docs keep AYA extractor integration scenarios and CLI spot checks:
  - [`roadmap/app-validation-checklist.md`](../../roadmap/app-validation-checklist.md:86)
  - [`roadmap/csharp-python-parity.md`](../../roadmap/csharp-python-parity.md:158)
  - [`reverse-engineering/game-assets/_index.md`](../../reverse-engineering/game-assets/_index.md:9)

# Build/Usage Impact

- Main solution/app build has **no direct project reference** to either submodule:
  - No `ProjectReference`/solution linkage from top-level app projects to `references/Onslaught` or `references/AYAResourceExtractor` was found.
  - The AYA extractor has its own solution within the submodule: [`references/AYAResourceExtractor/Code/AyaResourceExtractor/AYAResourceExtractor.sln`](../../references/AYAResourceExtractor/Code/AyaResourceExtractor/AYAResourceExtractor.sln:6)
- Functional impact split:
  - Core save/config/media/lore workflows: low direct dependency on submodules.
  - Asset extraction UX (when re-enabled): depends on built `AYAResourceExtractor.exe` under expected submodule bin paths.
- Toolchain impact for AYA lane:
  - AYA extractor build requires VS2022 + C++ desktop workload + .NET 6 + x86 target assumptions: [`AGENTS.md`](../../AGENTS.md:331), [`roadmap/app-validation-checklist.md`](../../roadmap/app-validation-checklist.md:87)

# Release Risk Notes

- `references/Onslaught` is deeply embedded in documentation correctness claims; missing/incorrect submodule content degrades RE confidence, source-parity claims, and function-note integrity.
  - Risk signal: semantic audit process explicitly validates source-citation quality against this snapshot: [`reverse-engineering/binary-analysis/semantic-audit-2026-02-12.md`](../../reverse-engineering/binary-analysis/semantic-audit-2026-02-12.md:17)
  - Snapshot incompleteness remains a known limitation (not all source files available), so some mappings are intentionally partial: [`reverse-engineering/source-code/source-file-inventory.md`](../../reverse-engineering/source-code/source-file-inventory.md:29), [`STUART_SOURCE_REQUIREMENTS_FOR_FULL_CLARITY.md`](../../STUART_SOURCE_REQUIREMENTS_FOR_FULL_CLARITY.md:65)
- `references/AYAResourceExtractor` poses a feature-risk mainly for shelved/dormant asset-browser flows; if those tabs are reactivated, missing submodule checkout or missing extractor build output will cause immediate UX failures (repo-not-found / exe-not-found messaging paths).
- Public-release/legal distribution risk is explicitly called out for submodule-sourced content (especially Onslaught source) in project docs:
  - [`reverse-engineering/project-meta/attribution.md`](../../reverse-engineering/project-meta/attribution.md:198)
- Operational risk: the main README does not currently provide explicit submodule initialization/build steps, so new-environment setup can silently miss these dependencies until a dependent workflow is attempted.
