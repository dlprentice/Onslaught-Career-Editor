# Repository Authority Map

Status: active

Use the implementation and its focused tests as current truth. Root contributor
docs and `package.json` own the normal workflow; dated reports and historical
plans do not override them.

## Current Sources

- `OnslaughtCareerEditor.WinUI/` — primary Windows application.
- `OnslaughtCareerEditor.AppCore/` — shared save, options, patch, media, Lore,
  and asset behavior.
- `OnslaughtCareerEditor.Cli/` and `OnslaughtCareerEditor.AppCore.Host/` —
  support interfaces.
- `rebuild/` — separate GPL RE-informed reconstruction lane.
- `tools/` — focused release, validation, RE, extraction, and lab tooling.
- `reverse-engineering/`, `roadmap/`, and `lore/` — canonical technical,
  planning, and narrative sources.

## Derived Material

- `lore-book/` is a tracked projection and packaging source. Edit its canonical
  source first and use the existing docsync command when that source changes.
- `release/readiness/public_package.json`, `public_AGENTS.md`, and
  `public_gitignore.txt` are release-boundary projections; root files remain the
  working source authority.
- Generated indexes and manifests belong to their owning generator.

## Local Output

Game payloads, copied executables, saves, extracted media, Ghidra databases,
debugger logs, screenshots, build output, `.artifacts/`, and `subagents/` are
local disposable inputs or outputs and must stay out of Git and release ZIPs.
They are not durable project state.

Retired Electron, WPF, and Python application implementations are available in
Git history only. Do not restore them as source lanes without an explicit
product decision.

When two sources disagree, prefer current behavior, then focused tests, then the
nearest current contract. Keep verification proportional to the actual change.
