# Public-Primary Working Repo Plan

Status: active
Last updated: 2026-06-24

## Decision

Use the public repository as the primary collaboration and day-to-day working
repo. Stop treating public source as a tiny sparse export.

The repo still uses ignored local overlays for hard payloads: actual game files,
private media/input payloads, saves, copied executable/runtime output, full
Ghidra databases/backups, bulky frame captures, raw CDB logs, secrets, and build
output.

## Why

- The old curated public/private split made the public repo too sparse for
  collaboration.
- The app, AppCore, tests, tooling, patch metadata, static RE writeups, runtime
  proof summaries, state batons, and agent reports are useful to outside
  contributors.
- Agents work better when the active repo has the real source/docs/tools instead
  of a minimal release-shaped subset.
- Local ignored overlays let maintainers keep payload-heavy lab material close
  to the repo without publishing binaries, copied game data, or secrets.

## Migration Policy

Move aggressively to public:

- Product source, tests, and project files.
- Tools and scripts.
- Patch catalogs and schemas.
- Reverse-engineering docs, maps, contracts, and structured fact exports.
- Release/readiness docs, wave notes, state batons, and agent reports.
- Local validation and contribution docs.

Keep ignored/local-only:

- `game/`, private media/input payloads, local saves/options payloads, copied
  runtime profile output, and raw runtime proof roots.
- Full Ghidra project databases/backups.
- Binary game payloads, extracted assets, audio/video/model files, screenshots,
  frame captures, CDB logs, and copied executable output.
- Secrets, `.env*`, credentials, local config, and build/test output.

## Migration Target

The migration target is broad private-to-public working-tree parity for tracked
project material. Include `reverse-engineering/**`, `roadmap/**`, `release/**`,
`tools/**`, `archive/**`, state batons, agent reports, and project directives
unless a file is an actual game/runtime payload, secret, full Ghidra database,
build output, or bulky generated capture.

## Done Criteria For This Transition

- Public docs say this is the primary working repo.
- `.gitignore` explicitly supports local lab overlays.
- Public repo contains the meaningful source/docs/tools/RE/runtime-proof surface,
  not only a tiny release export.
- Local gates still pass after the migration.
- Contributors can clone, build, run tests, and understand where local game or
  Ghidra material belongs without receiving proprietary payloads.
