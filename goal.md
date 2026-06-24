# Active Goal Slice

Status: active
Last updated: 2026-06-24
Policy: `goal.policy.md`

## Current Slice

Make this public repository the primary working repo by folding in the former
private maintainer tree as real project history and working material, then
commit and push the new public-primary baseline.

This is a broad migration slice, not a tiny release export. Track source, tools,
RE docs, wave notes, readiness notes, state batons, agent reports, scratch
checkers, and compact proof summaries when they are useful to contributors.
Keep only hard payloads out of git: actual game files, copied executables,
private media/input payloads, local save payloads, full Ghidra databases/backups,
secrets, build output, screenshots/frame dumps, raw CDB logs, and bulky copied
runtime captures.

After this slice is committed/pushed, normal development should happen from this
public repo by default. Short-lived private/local workspaces remain allowed only
for hard payloads, local runtime proof roots, full Ghidra databases, or other
material that cannot be represented safely as source/docs/tools/proof summaries.

## Current Truth

- Static Ghidra closure remains complete: `6411/6411 = 100.00%`, static debt `0 / 0 / 0`, active current-risk re-audit `1179/1179 = 100.00%`.
- `v1.0.2` app release remains published at `https://github.com/dlprentice/Onslaught-Career-Editor/releases/tag/v1.0.2`.
- The public repo is being converted from sparse release-shaped source into the active collaboration repo.
- The former private tracked tree has been broadly overlaid into this public checkout.
- `README.MD`, `AGENTS.md`, `CONTRIBUTING.md`, `LOCAL_LAB_OVERLAY.md`, `README.RELEASE.md`, `SECURITY.md`, and `release/readiness/PUBLIC_SIGNOFF_COMMANDS.md` now describe public-primary source work and hard-payload-only local overlays.
- `tools/public_allowlist_safety_check.py` is now a hard-payload safety check, not a censoring/export allowlist. `npm run test:public-allowlist` remains as a compatibility alias to that check.
- Extracted scratch texture PNGs and generated md-link reports are ignored; text RE/scratch/state/subagent material is tracked.
- Online multiplayer is still not player-ready. Host/Join remains disabled until distinct-endpoint command-source proof and source-bound copied-runtime causality proof exist.
- WinUI 3 remains the current shipped app lane. Blazor/Tauri/Godot remain future evaluations, not active replacements for this migration slice.

## Validation For This Slice

Passed in the public checkout before commit:

- `npm run test:hard-payload-safety`
- `npm run test:public-allowlist`
- `npm run test:doc-commands`
- `py -3 tools\docsync_check.py`
- `dotnet build .\OnslaughtCareerEditor.WinUI.slnx --nologo`
- `npm run test:md-links`
- `npm run test:repo-hygiene`
- `git diff --cached --check`
- staged hard-payload filename scan: no staged game/media roots, executables, DLLs, saves/options payloads, audio/video/model payloads, archives, or `.env` files

## Next Executable Work

1. Commit and push the public-primary migration baseline.
2. Treat `C:\Users\david\source\Onslaught-Career-Editor` as the default active repo.
3. Continue WinUI/mod/runtime/multiplayer work from the public repo, using local overlays only for hard payloads and runtime proof roots.
4. Keep the v1.0.2 release stable unless a new verified release slice is prepared.
5. Resume feature work with bounded normal/adversarial consults when available and useful; Codex root remains final owner of edits, validation, commits, pushes, and acceptance.

## Stop Conditions

- A proposed tracked file is an actual BEA executable/DLL/game archive/media/save payload, full Ghidra database/backup, secret, `.env*`, copied runtime output, screenshot/frame dump, raw CDB log, or build artifact.
- A proposed runtime or patch step mutates the installed Steam game folder or original `BEA.exe`.
- Online wording or UI implies player-ready online multiplayer before required proofs exist.
- A static RE contradiction appears; stop product/runtime work and correct the static claim with bounded evidence first.
