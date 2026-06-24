# Lane 09 - Lore Mirror / Browser Audit

Date: 2026-03-05
Scope: `lore-book/BOOK.md`, `lore-book/Start-Here.md`, browser-facing lore-book mirror pages, and Lore Browser loading/navigation expectations in WPF + PyQt.

## Key Findings

1. HIGH - Browser-facing roadmap mirrors are stale relative to canonical roadmap docs that `Start-Here.md` sends readers into.
   - `lore-book/Start-Here.md:24` routes readers to `roadmap/app-validation-checklist.md` and `roadmap/app-delivery-phases.md` inside `lore-book/`.
   - Canonical `roadmap/app-delivery-phases.md:3` says `Last updated: 2026-03-05`, but mirror `lore-book/roadmap/app-delivery-phases.md:3` still says `2026-03-04`.
   - Canonical `roadmap/app-delivery-phases.md:48`, `roadmap/app-delivery-phases.md:50`, `roadmap/app-delivery-phases.md:54` still document the optional targeted C# subset, Windows `py -m pytest -q tests_pyqt`, and `release_profile_snapshot.py --check`; mirror `lore-book/roadmap/app-delivery-phases.md:48`, `lore-book/roadmap/app-delivery-phases.md:50`, `lore-book/roadmap/app-delivery-phases.md:53` instead promote a narrower unittest-only Python path and a mutating `release_profile_snapshot.py` command.
   - Canonical `roadmap/app-validation-checklist.md:3`, `roadmap/app-validation-checklist.md:20`, `roadmap/app-validation-checklist.md:22`, `roadmap/app-validation-checklist.md:26`, `roadmap/app-validation-checklist.md:32`, `roadmap/app-validation-checklist.md:33`, `roadmap/app-validation-checklist.md:34` differ materially from mirror `lore-book/roadmap/app-validation-checklist.md:3`, `lore-book/roadmap/app-validation-checklist.md:20`, `lore-book/roadmap/app-validation-checklist.md:21`, `lore-book/roadmap/app-validation-checklist.md:25`, `lore-book/roadmap/app-validation-checklist.md:31`. The mirror drops the Windows/WSL split, points at a different Python test set, and changes the pass criteria.
   - Impact: Lore Browser readers can land on outdated release/test instructions even when canonical roadmap docs are current.

2. MEDIUM - `Start-Here.md` overstates the lore-book containment model; one of its own canonical pointers is outside the lore-book tree.
   - `lore-book/Start-Here.md:5` says every document still lives under `lore-book/`.
   - `lore-book/Start-Here.md:10` links to `../CURRENT_CAPABILITIES.md`, which is repo-root, outside `lore-book/`.
   - WPF tree/home population is built from `lore-book/BOOK.md` / `lore-book/` content (`Views/LoreBrowserView.xaml.cs:273`, `Views/LoreBrowserView.xaml.cs:331`, `Views/LoreBrowserView.xaml.cs:337`, `Views/LoreBrowserView.xaml.cs:917`). PyQt does the same (`onslaught/gui/tabs/lore_browser.py:172`, `onslaught/gui/tabs/lore_browser.py:202`, `onslaught/gui/tabs/lore_browser.py:313`).
   - Impact: the linked root doc is loadable in-app via fallback, but it is not part of the left-tree/book model that `Start-Here.md` describes.

3. MEDIUM - Current docsync guardrails do not cover most browser-facing lore/roadmap mirrors, which is why stale lore-book pages can survive.
   - `tools/docsync_policy.json:2`-`tools/docsync_policy.json:12` strict-mirror only `reverse-engineering` -> `lore-book/reverse-engineering`.
   - `tools/docsync_policy.json:13`-`tools/docsync_policy.json:23` only pair-check two release allowlist files in `roadmap/`.
   - `tools/docsync_policy.json:25`-`tools/docsync_policy.json:41` only enforce curated hints for `BOOK.md`, `Start-Here.md`, `lore-book/roadmap/ROADMAP-INDEX.md`, and `lore-book/roadmap/agent-workflow.md`.
   - This leaves `lore-book/roadmap/app-delivery-phases.md`, `lore-book/roadmap/app-validation-checklist.md`, and the rest of `lore-book/lore/**/*` outside automatic parity enforcement.

## Verified Passes / Non-Findings

- PASS - `lore-book/BOOK.md` links resolved in this pass; no missing target files were found from the book TOC.
- PASS - `lore-book/Start-Here.md` links resolved in this pass; no missing target files were found from the entry page.
- PASS - WPF and PyQt Lore Browser implementations are broadly aligned on loader behavior:
  - both prefer `BOOK.md` when present (`Views/LoreBrowserView.xaml.cs:331`, `Views/LoreBrowserView.xaml.cs:337`; `onslaught/gui/tabs/lore_browser.py:802`, `onslaught/gui/tabs/lore_browser.py:803`),
  - both keep local markdown navigation in-app and open external URLs externally (`Views/LoreBrowserView.xaml.cs:1493`, `Views/LoreBrowserView.xaml.cs:1502`, `Views/LoreBrowserView.xaml.cs:1652`; `onslaught/gui/tabs/lore_browser.py:305`, `onslaught/gui/tabs/lore_browser.py:312`, `onslaught/gui/tabs/lore_browser.py:320`).
- NOTE - `lore-book/lore/_index.md` differs from `lore/_index.md`, but the diff observed in this pass is the relative-path/mirror-policy wording at `lore/_index.md:8` vs `lore-book/lore/_index.md:8`, which appears to be an intentional mirror rewrite rather than stale content.

## Bottom Line

The Lore Browser loaders are working the way the curated book expects, but the browser-facing roadmap mirror is not fully in sync with canonical roadmap docs. The primary accuracy risk right now is not loader behavior; it is stale mirrored release/test guidance under `lore-book/roadmap/` plus missing parity enforcement for those pages.
