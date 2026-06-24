# Tracked artifact hygiene review (2026-05-27)

Status: public-safe audit note
Date: 2026-05-27
Branch: `main`
Scope: tracked binary/private-ish artifacts after PR #1 WinUI lane promotion

Superseded release-boundary note, 2026-06-22: `gold_career_save.bin` is no
longer treated as public payload. It remains a private maintainer-tree
regression fixture and is excluded from curated public candidates by
`tests_shared/fixtures/**` plus binary suffix safety checks.

## Summary

The tracked-artifact risk review originally found **no public release allowlist leak**.
The public policy has since been tightened.

- A tracked path/extension scan found `5577` binary/private-risk matches.
- All sampled large private/game/media/operator artifacts are classified **R4_DENY** by the release profile.
- The historical non-R4 exception was `tests_shared/fixtures/gold_career_save.bin`.
- Current policy treats that file as private maintainer-tree fixture material,
  not public candidate payload.

## Evidence

Commands run from the repo root:

```powershell
py -3 tools\release_profile_snapshot.py --check
py -3 tools\release_curated_manifest.py --check
npm run test:public-allowlist
```

Result:

- `release_profile_snapshot.py --check`: **PASS** (`R0=4031 R2=0 R3=2 R4=18188`)
- `release_curated_manifest.py --check`: **PASS** (`3456` selected)
- `npm run test:public-allowlist`: **PASS** (`3456` rows)

Focused tracked-artifact scan result:

```text
NON_R4_RISK_MATCHES 1
R0_ALLOW 10004 tests_shared/fixtures/gold_career_save.bin
```

Fixture metadata:

```text
size: 10004 bytes
header: d14b
tracked blob: 040ff15907ceb07b394f44bfbd3edea1e65bd015
```

## Decision

No tracked files were deleted or moved.

The private/full-game, media, `.codex`, scratch, and temporary-save surfaces remain private-repo material and are excluded from public/community release output by the release profile. Removing or rewriting them would be destructive provenance work and is not needed to protect public packages.

## Follow-up

If repository size or private-branch hygiene becomes the next goal, do a separate history/storage review. That review should not be mixed with release allowlist safety, because the current public release gates already exclude these artifacts.
