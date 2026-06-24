# Private Directive Lane Truth - 2026-05-07

Status: pass
Source/evidence commit: 2aee7e637ef8dcd8e7a593aa7b999bf02fabeb97

## Objective

Prevent the tracked private operator directive from overriding current WinUI-first repo truth with obsolete Electron-first instructions.

## Change

- `onslaught_codex_directive.md` now begins with a superseded/historical banner.
- The active context bullets now point to WinUI 3 + Windows App SDK over AppCore as the product direction.
- Electron, WPF, and the old Python GUI/CLI parity app are described as archived/reference surfaces.
- The historical Electron-first work order remains in the file for private provenance, but it is explicitly marked as not executable as an active plan.

## Commands

```powershell
npm run test:repo-hygiene
```

Result: pass

Important output:

```text
Repo text hygiene check: PASS
Rules checked: 22 text, 2 path
Ran 27 tests in 0.003s
OK
```

```powershell
npm run test:md-links
```

Result: pass

Important output:

```text
Markdown link check: PASS
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
npm run test:doc-commands
node -e "<parse developer_agent_state.json and documentation_agent_state.json>"
```

Result: pass

Important output:

```text
Release profile snapshot check: PASS
Curated allowlist check: PASS
Public allowlist safety check: PASS
NPM script documentation check: PASS
state json ok
```

## Evidence Boundary

- This is private-operator documentation cleanup, not a product code change.
- The directive itself remains excluded from public/community release policy.
- No runtime proof, screenshots, private game files, copied executables, copied saves, or media payloads were committed.
