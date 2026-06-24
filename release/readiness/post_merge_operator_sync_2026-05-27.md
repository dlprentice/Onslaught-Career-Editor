# Post-merge operator sync (2026-05-27)

Status: **published / archived** (origin/main synced 2026-05-27; `wip/sandbox` retired 2026-05-27)
Date: 2026-05-27
Merge commit on `origin/main`: `df6ed5a1`
Release allowlist hygiene: `a2e41405` (R0=4000 snapshot), state closeout `ebb59a6f`

## Current remote truth

| Item | Value |
| --- | --- |
| Default branch | `main` (changed from `wip/sandbox` on 2026-05-27) |
| `origin/main` tip | `1fca716b` (allowlist R0=4001, idle gate, MSIX decision status, operator handoff) |
| `origin/wip/sandbox` | Retired/deleted; final tip archived as tag `archive/wip-sandbox-final-2026-05-27` (`49c1ed12`) |

## Publish local doc/state commits

**Done 2026-05-27** — `origin/main` updated and `origin/wip/sandbox` retired/deleted after archival tagging. Historical steps below are retained for audit only.

```powershell
cd C:\Users\david\source\Onslaught-Career-Editor-private
git checkout main
git pull origin main
git log -1 --oneline
git push origin main
```

## Gates to run after push (desktop)

```powershell
npm run test:winui-primary-lane
npm run test:winui-zip-package-probe
npm run test:winui-zip-release-candidate-probe
```

Re-run ZIP probes only when WinUI publish output or probe scripts change.

## GitHub / Branch Notes

- GitHub is a git remote backup only for this repo; validation is local.
- `wip/sandbox` has been retired; target future work to `main` or a new short-lived branch.

## Truth boundaries

- PR #1 was a **lane promotion**, not a narrow Home-nav-only merge.
- `6113/6113` Ghidra closure = export-contract static review, not runtime gameplay proof.
- Installer / MSIX / trusted install: **guarded-not-ready**.
