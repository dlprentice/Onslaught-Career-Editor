# Historical PR #1 Merge Readiness

Status: **MERGED** (2026-05-27T05:41:04Z, merge commit `df6ed5a1`)
Date: 2026-05-27
Branch after merge: `main` (default)
PR: private maintainer integration record (not public release metadata)

## Scope warning

PR #1 carried the full private integration-branch history, not only the
2026-05-27 Home navigation / ZIP proof slice. Treat the merge as the historical
promotion of the WinUI/AppCore/tooling preservation tree onto `main`, not as a
small additive feature PR.

## `main` branch context (critical)

Before the merge, `main` was the legacy root-level WPF app and the private
integration branch held the WinUI 3 + AppCore + tooling + RE preservation tree
under `OnslaughtCareerEditor.WinUI/`, `tools/`, `reverse-engineering/`, etc.

A narrow cherry-pick of only the Home navigation commits onto the pre-merge
`main` was not viable because those paths did not exist there.

**Implication:** merging PR #1 is the integration path for the WinUI product lane (plus RE/docs/tooling on the branch), not a small additive feature PR. Review merge as a lane promotion, with the 2026-05-27 Home/ZIP work as the latest validated slice on top.

## Local gates

GitHub is now a git remote backup only for this repo. These are local validation gates:

| Job | Proves |
| --- | --- |
| Build and test (Windows) | `npm run test:winui-primary-lane` |
| Docs and hygiene | docsync, md-links, repo-hygiene, doc-commands, public-allowlist |

## Desktop-only gates

Run on a Windows workstation before claiming distribution or Home navigation proof:

- `npm run test:winui-zip-package-probe`
- `npm run test:winui-zip-release-candidate-probe`
- Explicit `WinUiHomeNavigationSmokeTests` when Home routing changes

Public-safe evidence:

- `release/readiness/winui_zip_package_probe_2026-05-27.md`
- `release/readiness/winui_zip_release_candidate_probe_2026-05-27.md`

## What merge does not prove

- MSIX / installer / trusted install (still `guarded-not-ready`)
- Ghidra 6113/6113 export-contract closure as runtime gameplay proof
- Full Home/page workflows beyond automation-marker reachability
- Visual/screenshot review of Home layout copy

## Post-merge verification (2026-05-27)

- GitHub **default branch** set to `main` (was `wip/sandbox`).
- Local `npm run test:winui-primary-lane` on merge tip `df6ed5a1`: **PASS** (build, AppCore 86, UiTests 52 pass / 2 skipped).
- Legacy WPF lives only under `archive/legacy-wpf/`.
- Primary Windows product lane: `OnslaughtCareerEditor.WinUI/`.

## Recommended operator checklist (post-merge)

1. Pull `origin/main` on workstations (`git checkout main && git pull`).
2. Confirm `wip/sandbox` remains retired; recovery history is preserved by tag `archive/wip-sandbox-final-2026-05-27`.
3. Re-run `npm run test:winui-zip-package-probe` after any WinUI publish or probe script change.
4. Optional: native visual/screenshot review of Home shortcuts (not in default primary-lane gate).

## Historical ZIP evidence

May 6 dated files remain historical (launch + Media only). Do not rewrite their PASS blocks; use the 2026-05-27 addenda for Home navigation claims.
