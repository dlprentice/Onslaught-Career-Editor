# Private Directive Hygiene Guard - 2026-05-07

Status: pass
Source/evidence commit: fb2e9afa7bf6aa80eda46a778dd13834a75f4af1

## Objective

Make the repo hygiene gate fail if the tracked private operator directive loses its superseded/historical banner.

## Change

- `tools/repo_text_hygiene_check.py` now has a required-marker check for `onslaught_codex_directive.md`.
- `tools/repo_text_hygiene_check_test.py` covers the missing-banner failure path and the accepted superseded-banner path.
- This protects the WinUI-first repo reality from accidental reactivation of the older Electron-first directive text.

## Commands

```powershell
npm run test:repo-hygiene
```

Result: pass

Important output:

```text
Repo text hygiene check: PASS
Rules checked: 22 text, 2 path, 1 required marker
Ran 28 tests in 0.004s
OK
```

```powershell
git diff --check
```

Result: pass

Important output:

```text
exit 0
```

```powershell
py -3 tools\release_profile_snapshot.py --check
py -3 tools\release_curated_manifest.py --check
npm run test:public-allowlist
npm run test:md-links
npm run test:doc-commands
node -e "<parse developer_agent_state.json and documentation_agent_state.json>"
```

Result: pass

Important output:

```text
Release profile snapshot check: PASS
Curated allowlist check: PASS
Public allowlist safety check: PASS
Markdown link check: PASS
NPM script documentation check: PASS
state json ok
```

## Evidence Boundary

- This is a guardrail/tooling change, not a product UI or runtime proof.
- No archived app lane was reactivated.
- No private game files, copied saves, copied executables, media payloads, screenshots, or proof JSON were committed.
