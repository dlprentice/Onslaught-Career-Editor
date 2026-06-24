# Lane 07/10 Final Synthesis: Release Readiness, Packaging, and Private->Public PR Prep

## Objective
Create a deterministic, repeatable public-release flow from private `wip/sandbox` using allowlist-first selection, explicit denylist enforcement, and auditable pass/fail checks.

## Decision Policy (R0-R4)
- `R0`: include by default.
- `R1`: include after lightweight content sanity review.
- `R2`: include only when all required gates pass (provenance, derivative-content, privacy/endpoints, submodule, payload).
- `R3`: deny by default.
- `R4`: hard deny.

## Public Allowlist Baseline

### Approved by default (`R0`)
- `Program.cs`
- `BesFilePatcher.cs`
- `App*.cs`
- `MainWindow*.xaml*`
- `Views/**`
- `Onslaught - Career Editor.csproj`
- `Onslaught - Career Editor.sln`
- `patcher.py`
- `onslaught/**`
- `onslaught_explorer.py`
- `OnslaughtCareerEditor.UiTests/**`
- `tests_pyqt/**`

### Approved with quick review (`R1`)
- `README.MD`
- `LICENSE`
- selected root `.md`
- `roadmap/**`
- `lore/**`
- `lore-book/**`
- `reverse-engineering/save-file/**`
- `reverse-engineering/game-mechanics/**`
- `reverse-engineering/project-meta/**`

### Conditional queue (`R2`, must pass all applicable gates)
- `reverse-engineering/source-code/**`
- `reverse-engineering/game-assets/**`
- `reverse-engineering/binary-analysis/functions/**`
- curated file-level subset of `reverse-engineering/binary-analysis/*`
- `.gitmodules`
- `references/Onslaught` (gitlink only)
- `references/AYAResourceExtractor` (gitlink only)
- curated subset of `tools/**`
- curated subset of `patches/**`
- `media/generated-art/**` with explicit provenance note

## Public Denylist Baseline

### Hard deny (`R4`)
- `game/**`
- `BEA_Widescreen.exe`
- `BEA.exe.gzf`
- `media/packaging/**`
- `media/publications/**`
- `media/wallpapers/**`
- `media/portraits/**`
- `media/flash/**`
- `reverse-engineering/binary-analysis/scratch/**`
- `discord_channel_dumps/**`

### Deny by default (`R3`)
- `reverse-engineering/binary-analysis/*.jsonl`
- `reverse-engineering/binary-analysis/function_mutation_tracking_state.json`
- `media/patches/**`
- `save-attempts/**`
- `subagents/**`
- `wave_online_audit*/**`
- `*_state.json`
- `*_state.json.tmp`
- `bin/**`
- `obj/**`
- `.venv/**`
- `__pycache__/**`
- `.tmp_*/**`

## Packaging Plan (Public Source)

### Phase 1: Public-prep branch bootstrap (clean-room)
1. Fetch both remotes and start from public default branch, not from private history tip.
2. Create a dedicated prep branch, for example `release/public-prep-YYYYMMDD`.
3. Import only allowlisted path families from `private/wip/sandbox`.
4. Add approved `R2` families only after gate sign-off.

Recommended commands:
```bash
git fetch origin private --prune
git switch -c release/public-prep-$(date +%Y%m%d) origin/main
```

### Phase 2: Curated import
Use path-spec import from private branch for `R0`/`R1` first, then gated `R2`.

Pattern:
```bash
# Example form; run once per approved path/pattern
git checkout refs/remotes/private/wip/sandbox -- "Program.cs"
```

### Phase 3: Build source artifact from public-prep commit
```bash
mkdir -p dist
STAMP=$(date +%Y%m%d)
PKG="dist/onslaught-career-editor-public-src-${STAMP}.tar.gz"
git archive --format=tar.gz -o "$PKG" HEAD
tar -tf "$PKG" | sort > "dist/public-src-${STAMP}.manifest.txt"
sha256sum "$PKG" > "dist/public-src-${STAMP}.sha256.txt"
```

### Phase 4: Optional binary packaging (post-source gate)
Only after source gate passes:
```bash
dotnet publish "Onslaught - Career Editor.csproj" -c Release -r win-x64 --self-contained false -o dist/wpf-win-x64
```
Publish app binaries separately from source snapshot; do not bundle denied assets.

## Repo Split Strategy (Private -> Public PR)
Recommended strategy: clean-room public-prep branch based on `origin/main` with explicit file import.

Why this strategy:
- minimizes accidental carryover of private-only files
- keeps public PR diff reviewable by path family
- avoids bringing private-only commit history into public branch

Execution steps:
1. Freeze source reference commit in private branch (`private/wip/sandbox`) and record SHA in PR notes.
2. Build public-prep branch from `origin/main`.
3. Import `R0` + `R1` paths.
4. Run `R2` gate review; include only explicit pass set.
5. Run readiness checks (below).
6. Commit in review-friendly slices:
- commit A: app code + tests
- commit B: docs
- commit C: gated utilities and conditional files
7. Open PR to public repo with:
- included families
- excluded families
- check results
- private source SHA used for traceability

## Concrete Readiness Checks (Must All Pass)

### CK-01 Branch baseline
```bash
git rev-parse --abbrev-ref HEAD
```
Pass: branch name matches `release/public-prep-*`.

### CK-02 Denylist path sweep (tracked files)
```bash
git ls-files | rg -n '^(game/|save-attempts/|discord_channel_dumps/|subagents/|wave_online_audit|media/(packaging|publications|wallpapers|portraits|flash)/|reverse-engineering/binary-analysis/scratch/|reverse-engineering/binary-analysis/.*\.jsonl$|.*_state\.json(\.tmp)?$|BEA_Widescreen\.exe$|BEA\.exe\.gzf$|bin/|obj/|\.venv/|__pycache__/|\.tmp_)'
```
Pass: no output.

### CK-03 Allowlist presence sanity
```bash
git ls-files | rg -n '^(Program\.cs|BesFilePatcher\.cs|patcher\.py|onslaught/|onslaught_explorer\.py|Views/|OnslaughtCareerEditor\.UiTests/|tests_pyqt/|README\.MD|LICENSE$)'
```
Pass: expected core files and directories are present.

### CK-04 Submodule URL safety (`R2` gate)
```bash
if [ -f .gitmodules ]; then git config -f .gitmodules --get-regexp '^submodule\..*\.url$'; fi
```
Pass: all URLs are intended public endpoints and license-compatible.

### CK-05 Private path/endpoint leakage scan (`R1`/`R2` gate)
```bash
rg -n '(C:\\\\Users\\\\|/mnt/c/Users/|/home/[A-Za-z0-9._-]+/|172\.26\.|discord_channel_dumps|private repo|internal only)' \
  README.MD roadmap lore lore-book reverse-engineering tools patches . 2>/dev/null
```
Pass: no unapproved private endpoint/path leakage in public-included files.

### CK-06 Package manifest denylist sweep
```bash
STAMP=$(date +%Y%m%d)
MANIFEST="dist/public-src-${STAMP}.manifest.txt"
rg -n '^(game/|save-attempts/|discord_channel_dumps/|subagents/|wave_online_audit|media/(packaging|publications|wallpapers|portraits|flash)/|reverse-engineering/binary-analysis/scratch/|reverse-engineering/binary-analysis/.*\.jsonl$|.*_state\.json(\.tmp)?$|BEA_Widescreen\.exe$|BEA\.exe\.gzf$)' "$MANIFEST"
```
Pass: no output.

### CK-07 Build sanity (source integrity)
```bash
dotnet build "Onslaught - Career Editor.sln"
python3 -m unittest -v tests_pyqt.test_cli_readonly_modes_unittest
```
Pass: build and at least one read-only Python CLI test module pass on public-prep branch.

### CK-08 R2 explicit decision log
Create a one-page decision table in PR description with columns:
- `family`
- `decision` (`include` or `exclude`)
- `gates_checked`
- `evidence`

Pass: every `R2` family is explicitly resolved; unresolved defaults to `exclude`.

## Go/No-Go Rule
- Go only if CK-01..CK-08 all pass.
- Any failed `R2` gate or denylist hit is immediate no-go.
- If uncertain, exclude the family for this release cycle and defer to next cycle with documented evidence.

## Release Output Set
On pass, ship:
1. Public PR from `release/public-prep-*` to `origin/main`.
2. Source archive + manifest + sha256 in `dist/` generated from the same PR HEAD.
3. Optional app binaries built only from the accepted public-prep commit.
