# WinUI primary lane on `main` (2026-05-27)

Status: public-safe lane summary
Date: 2026-05-27
Branch: `main` (default as of 2026-05-27)
Merge: PR #1 — `df6ed5a1` (lane promotion from `wip/sandbox`)

## What changed

- **`main` is now the WinUI 3 + AppCore + tooling + RE preservation tree**, not the legacy root-level WPF app.
- Legacy WPF remains under `archive/legacy-wpf/` for reference only.
- Primary product project: `OnslaughtCareerEditor.WinUI/`.
- GitHub is a git remote backup only; validation is local.

## Local automated gates on `main`

| Gate | Local command | Scope |
| --- | --- | --- |
| Primary lane | `npm run test:winui-primary-lane` | WinUI build, AppCore tests, default UiTests (excludes LegacyWpf) |

## Local desktop gates

| Gate | When to run |
| --- | --- |
| `npm run test:winui-zip-package-probe` | After WinUI publish output or probe script changes |
| `npm run test:winui-zip-release-candidate-probe` | Before claiming RC ZIP readiness |
| Explicit `WinUiHomeNavigationSmokeTests` | After Home routing / deep-link changes |
| Explicit `WinUiVisualSmokeTests` | After visible layout/copy changes on primary surfaces |

## Existing public-safe evidence (2026-05-27)

- Home navigation on extracted Release ZIP: `release/readiness/winui_zip_package_probe_2026-05-27.md`
- RC ZIP probe: `release/readiness/winui_zip_release_candidate_probe_2026-05-27.md`
- PR merge / publish: `release/readiness/pr1_merge_readiness_2026-05-27.md`, `release/readiness/post_merge_operator_sync_2026-05-27.md`

## Does not prove

- MSIX / installer / trusted install (still **guarded-not-ready**)
- Ghidra 6113/6113 export-contract closure as runtime gameplay proof
- Full visual/screenshot review unless a dated visual evidence note exists
- Private `subagents/` screenshot trees in public releases (R4 deny)

## Operator defaults

- Target PRs to **`main`** or a new short-lived branch; historical `wip/sandbox` is retired.
- Run serial `dotnet build` / `dotnet test` on Windows (shared `obj/` locks).
- Maximize WinUI for visual evidence; scroll long pages when claiming full-page health.
