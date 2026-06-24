# Technical Debt

Status: active WinUI-first debt
Last updated: 2026-05-26

Code quality, testing, release polish, and refactoring opportunities for the WinUI-first Onslaught Toolkit.

## Current Top-Level Debt

### WinUI product lane

- [x] Prove WinUI 3 build/test health after the strategy reset.
- [x] Run native automated WinUI visual smoke after the current product-lane cleanup.
- [ ] Decide whether WinUI should have a lane-specific solution after the current consolidation pass.
- [x] Review WinUI dependency/license/public-safety posture before any signed/installer public release claim.
- [x] Prove disposable unpackaged WinUI publish output launches and renders primary screens.
- [ ] Continue replacing awkward or inherited copy in WinUI with clear user-facing Windows app language.

### Shared correctness and support lanes

- [ ] Clarify AppCore's long-term shared-core role after WinUI product coverage grows.
- [ ] Retire C# CLI parity checks only after the Windows lane and automation fixtures cover the same edge cases.
- [ ] Keep WPF archived/reference only.
- [ ] Inventory `archive/legacy-python/` only for narrow ideas/fixtures worth porting; keep the historical Python GUI/CLI parity app archived/reference.
- [ ] Keep `archive/electron-workbench/` archived unless a later explicit strategy prompt reactivates it.

### Native boundary hardening

- [ ] Preserve copied-target rules for save/options/executable mutation workflows.
- [ ] Add structured negative tests for every mutation arm phrase and copied-target path boundary that enters WinUI/AppCore.
- [ ] Keep Ghidra/CDB/game-launch work in focused tools/scripts unless a future lane strategy reintroduces a typed workbench.
- [x] Improve `tools/BeaAssetExportHarness` mesh-conversion error reporting so legacy extractor target-invocation failures expose inner exception type/message.
- [ ] Keep asset export harness lanes serial unless the legacy extractor template-file locking behavior is eliminated.

## Test Coverage Needs

| Test type | Status | Action |
|---|---|---|
| AppCore tests | Active | Retain and expand for save/options/patch/media/lore behavior |
| WinUI tests | Active product | Expand during WinUI hardening and product sprints |
| C# CLI smoke | Active support | Keep help/read-only behavior healthy while CLI remains supported |
| WPF tests | Legacy/reference | Do not expand unless a historical parity question requires it |
| Archived Electron tests | Optional archive | Run only when intentionally inspecting `archive/electron-workbench/` |
| Regression fixtures | Active | Add fixtures for newly discovered save/options/patch edge cases |

## Priority Test Cases

1. True dword view mapping, packed kills, rank encoding, and options tail preservation.
2. Copied save/options apply and restore with backup/read-back verification.
3. Copied executable patch apply and restore with preimage/read-back verification.
4. Audio catalog/playback and PNG preview from catalog IDs without arbitrary file reads.
5. Release policy/export content excluding private paths and archived apps.

## Edge Cases To Handle

- [ ] Corrupted saves: truncated files, wrong version word, incompatible sizes.
- [ ] Console vs PC saves: detect and reject incompatible formats.
- [ ] Empty save slots and zero-progress saves.
- [ ] Maximum kill values near 24-bit limits.
- [ ] Unicode paths on Windows for saves, game root, and artifact root.

## Refactoring Opportunities

- [ ] Extract shared file-copy/path-safety helpers in AppCore where WinUI and C# CLI still duplicate behavior.
- [ ] Reduce AppCore.Host usage if it stops serving active diagnostics.
- [x] Archive legacy WinUI bundle scripts outside the active `release/` lane; current historical copies live under `archive/legacy-winui-release/`.
- [x] Archive the Electron/React/TypeScript detour under `archive/electron-workbench/`.
- [ ] Replace any remaining broad roadmap includes in public manifests with curated doc allowlists.

## Documentation Debt

- [ ] Keep `README.MD`, `CURRENT_CAPABILITIES.md`, `roadmap/status-current.md`, `roadmap/three-lane-product-strategy.md`, and `roadmap/repo-structure-and-archive-map.md` in sync after each feature wave.
- [ ] Keep lore-book mirrors aligned after roadmap/source docs change.
- [ ] Keep release docs explicit that WinUI is the product lane and archived apps are excluded from default public/community outputs.
- [x] Generate source-controlled WinUI third-party notice draft and LGPL redistribution checklist.
- [ ] Include final package notices/license files and complete legal/compliance review before any public WinUI binary release.

See [status-current.md](status-current.md), [three-lane-product-strategy.md](three-lane-product-strategy.md), and [app-validation-checklist.md](app-validation-checklist.md).
