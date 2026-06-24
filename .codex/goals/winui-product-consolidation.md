# WinUI Product Consolidation Goal

Status: active operating contract
Created: 2026-05-04

## Mission

Consolidate the repository around the WinUI 3 Windows application and its supporting CLI/core lanes.

The desired outcome is a repo where the WinUI 3 app is the obvious primary user-facing product, the CLI/AppCore support path is healthy, and the old Electron, WPF, and Python app/product surfaces are clearly shelved as maintainer infrastructure or archived reference. Do not delete them. Do not pretend they no longer exist. Move or reclassify only when references, builds, release policy, docs, and tests prove it is safe.

Work iteratively. Inspect, fix, validate, record, then repeat. Do not stop after a superficial pass. Stop only when high-confidence issues found in the inspected areas are fixed, validated, or clearly recorded as follow-ups that would be risky/speculative without a separate prompt.

## Strategic Truth

- WinUI 3 is the primary user-facing Windows GUI app.
- AppCore is shared correctness/core support for WinUI and parity checks.
- The C# CLI may remain as a useful support/diagnostic lane until explicitly retired.
- Electron is shelved as a product app. It may remain buildable/referenceable as maintainer/RE infrastructure, but should be out of the way for product-lane docs and release posture.
- The old Python GUI/CLI parity app is archived/reference. Active Python work should be limited to utility scripts and lab tooling under active tool paths, not by reviving the archived Python app.
- WPF is archived/reference only.
- Public release tooling must remain safe and explicit.

## Non-Negotiable Guardrails

- Inspect git status before each meaningful batch.
- Preserve unrelated uncommitted work.
- Do not commit unless the user explicitly asks.
- Do not delete private/game/media/evidence data.
- Do not patch or run the original Steam/Program Files `BEA.exe`.
- Do not mutate repo-local `game/BEA.exe`.
- Do not synthesize `.bes` saves.
- Do not weaken AppCore safety rules, release deny rules, or tests.
- Do not expand public release scope without explicit evidence and review.
- Do not hide failures by deleting tests or moving checks out of the way.
- Do not broadly rewrite architecture unless a concrete defect requires it.
- Do not claim "bug free." Claim only what was inspected and validated.

## Progress Ledger

Maintain:

```text
.codex/state/winui-product-consolidation.md
.codex/state/winui-product-consolidation-evidence.md
```

The ledger must track:

- current phase
- files inspected
- issues found
- fixes completed
- validation commands run
- validation failures and fixes
- moved/reclassified files
- release-policy effects
- remaining risks
- deferred follow-ups
- next inspection target

Update the ledger after every meaningful batch.

## Ralph-Style Loop

Repeat until the completion criteria are met or remaining work becomes risky/speculative/product-design-dependent.

### 1. Discover

Inspect these areas in priority order:

1. WinUI app shell, pages, settings, save/options workflow, media/lore/patch workflows.
2. WinUI build/test/project files and UI/static tests.
3. AppCore and C# CLI surfaces that directly support WinUI.
4. Repo docs that describe product direction, setup, testing, release, and current capabilities.
5. Release/readiness allowlists, profile snapshots, private inventory, and package scope.
6. Lore/lore-book indexes, links, mirrored docs, and stale product references.
7. Electron/Python/WPF app surfaces and docs that still appear primary or product-facing.
8. Archive/reference organization and solution/project references.

Look for:

- broken WinUI builds/tests
- stale Electron-first or Python-product wording
- WinUI still described as legacy/reference
- patch flows that imply original executable mutation
- save/options flows that imply unsafe in-place save mutation
- docs that point users to the wrong app
- release manifests that include shelved/private/product-confusing surfaces unintentionally
- lore/doc links that are broken or misleading
- archived/reference files that are still treated as active
- tests that no longer match the three-lane reality
- accessibility/contrast issues that are clear, objective, and low-risk to fix

### 2. Prioritize

Fix in this order:

1. Build/test/type/link/release-policy failures.
2. WinUI safety or correctness defects.
3. WinUI user-facing product copy that contradicts current strategy.
4. Release/public-safety issues.
5. Docs that send users or agents to Electron/Python/WPF as product apps.
6. Lore/index/link drift.
7. Safe archive/reclassification moves that keep old lanes buildable/referenceable.
8. Low-risk accessibility/contrast fixes.
9. Cosmetic cleanup only when already touching the area.

### 3. Patch

Make small, reviewable changes.

Allowed changes:

- WinUI product code fixes and small UX/product improvements.
- WinUI/AppCore/UI test additions or corrections.
- Docs/state/release policy updates that align with current reality.
- Safe moves into `archive/` only after reference checks prove the move will not break builds/tests/docs.
- Release/profile/allowlist regeneration when tracked generated artifacts become stale.

Disallowed without a later explicit prompt:

- deleting Electron/Python/WPF trees
- deleting evidence or private data
- broad Electron UX polish
- Python GUI/product work
- Python CLI parity-app work from `archive/legacy-python/`
- open-ended runtime automation
- signed installer release claims
- public release expansion

### 4. Validate

Use relevant repo commands. Prefer serial .NET commands.

Core WinUI/AppCore gates:

```powershell
dotnet build .\OnslaughtCareerEditor.WinUI\OnslaughtCareerEditor.WinUI.csproj --nologo
dotnet test .\OnslaughtCareerEditor.AppCore.Tests\OnslaughtCareerEditor.AppCore.Tests.csproj --nologo
dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName!~LegacyWpf"
```

Docs/release gates:

```powershell
py -3 tools\docsync_check.py
npm run test:doc-commands
npm run test:md-links
npm run test:repo-hygiene
npm run test:public-allowlist
py -3 tools\release_profile_snapshot.py --check
py -3 tools\release_curated_manifest.py --check
```

Use Electron/npm gates only if Electron/TypeScript/release-bundle files are changed. Electron is not the product-polish target.

If a validation command fails, fix the smallest relevant issue and rerun it. If a command is blocked by environment, record the exact blocker and run the strongest narrower check.

### 5. Review

After each batch:

- re-check git status
- review diff
- confirm changes are WinUI/product-consolidation scoped
- confirm no Electron/Python broad product polish was introduced
- confirm no release hard-deny family entered public allowlists
- update state/evidence ledgers

### 6. Continue

Choose the next highest-value inspection target and repeat.

## Completion Criteria

This goal is complete only when:

1. WinUI 3 is the clear primary product lane in app copy, docs, state, and release posture.
2. Electron, the old Python GUI/CLI parity app, and WPF app/product surfaces are shelved/out of the way without destructive deletion.
3. Old lanes that must remain reference/buildable have documented commands or documented blockers.
4. WinUI/AppCore build/test gates relevant to the changes pass.
5. Docs/lore links and mirrored docs relevant to the changes pass.
6. Release profile/manifest/allowlist checks pass.
7. State/evidence ledgers are updated.
8. Remaining risks and follow-ups are explicit.
9. No commits were made unless the user explicitly asked.

## Final Response Required

When stopping, report:

- what was inspected
- what changed
- files moved/reclassified
- validation commands and results
- failures fixed
- files changed
- remaining risks
- deferred follow-ups
- whether the next slice should be WinUI product hardening, release packaging, archive cleanup, or manual visual smoke

Do not say the repo is bug free. Say what was inspected and what confidence the validation provides.
