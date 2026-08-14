# External-table gap Ghidra live-promotion preparation

Date: 2026-08-14

Status: mechanically prepared and read-only preflighted; live and tracked
promotion remain forbidden until separately authorized and executed

Verdict: **LIVE_AUTHORITY_CANDIDATE_READY_CEREMONY_NOT_RUN**

Evidence: **MEASURED PRE / PROSPECTIVE POST** — the committed scratch authority
reproduces exactly, and the current live and tracked projects independently
rehash to the required PRE. No live, tracked, backup, or canonical-project byte
was changed while preparing this authority. The future physical POST database
is deliberately not guessed; it must be measured after the one authorized live
save and then reproduced by the POST backup, tracked snapshot, and retained
read-only restore copies.

Specimen: pristine PC retail `BEA.exe`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Preparation base: Git commit
`2509f65d90c86d6328c0b584dcf5eb0e08e02471`.

## Read-only result

The exact committed scratch authority at
`local-lab/ghidra-external-table-gap-boundary-current-scratch-20260814-v1/`
re-verified from the current repository:

- authority receipt: 7,597 bytes, SHA-256
  `a8e196c3dee91c1fb0600ea63fb5096ad7665159066c7ca40f58a124be48a691`;
- sealed tree excluding that receipt: 205 files, 1,344,777,896 bytes,
  SHA-256
  `1bd79dd25c07c256c0963dd0bd0444b89565eec4be8a44ad5ae8b90cf1e45893`;
- exact result: 79 pairwise-disjoint bodies / 9,234 bytes, 8,201 -> 8,280
  functions, 550,982 -> 550,991 instructions, and 234,537 -> 234,495
  references; and
- every field of all 8,201 PRE function rows remains byte-identical in both
  persistent scratch replicas.

The new authority's `preflight` mode then independently measured the live
maintainer project and tracked canonical project. Both are byte-identical at:

| PRE property | Exact value |
| --- | --- |
| Project files | 19 |
| Project bytes | 186,911,621 |
| Canonical project inventory | `91776fb4a67579950afc4fb3b48ea8a866733628aecfdae7a2cb918c615fe211` |
| `db.18611.gbf` | 68,288,512 bytes / `6f45cdac7ae1f10987280f0ec247e6b5d6dcf866eae79e5982efa78dd68455ce` |
| `db.18612.gbf` | 68,321,280 bytes / `424775377ea0f40d9e429c9219b9310d427760acc40548dbc588ca285f932f7b` |
| Full functions | 7,109,943 bytes / `2cc0b74f9284a3d6d59effa857cb6766bb78b08d50a7896d0dda8631f7c93314` |
| Program metrics | 1,267 bytes / `be169e6bae9bbd32c822a70c180e43960336fd85ee8ad52f5f494090c0a1e636` |
| Tracked projection | 504,598 bytes / `c6084999cefebdb900ec752be5c4cb45ed1d7dcbdd086a53cbd207b91db84d20` |

The canonical future live lane and both named backup destinations were absent
at preflight, so a later ceremony cannot accidentally append to or reinterpret
an earlier partial run.

## Prospective exact POST contract

The scratch result predetermines the semantic POST without predetermining
Ghidra's rolling serialization:

| POST artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| Full functions | 7,161,942 | `c3942b9e340cef71b731290b845843697af5c53204449c51949b779e896272d6` |
| Program metrics | 1,267 | `3e51ce1d5e926c632869b2058c9d89e91f48345a329a724ea9520570bd91212d` |
| Dry boundaries | 21,022 | `a09a264de05e7394384eac466ad8ab1357252e1bd2c663a8ee7858db39462594` |
| Apply boundaries | 29,018 | `97db9f391eb4a42a6a5f192ed37dfe3f29bdf6229c3437f17b1bd787a6007592` |
| Readback boundaries | 29,097 | `2f4b23ac985f55562a1897dc3d4163bd546b8b752c1c302e7d35f1d6ae365eb9` |
| Mechanical 8,280-row projection | 508,242 | `6e22a93a4792a2b5a9a6109a65e3b6460dc1ef6dc0606cc195a9a50e30ebdd68` |

The physical project gate requires exactly one path rotation:
`db.18611.gbf` disappears, `db.18613.gbf` appears, and `db.18612.gbf` plus
every other common project file remains byte-identical. The future
`db.18613.gbf` size and SHA-256 are unknown until the save. The authority accepts
them only when live, POST backup, tracked snapshot, and both retained POST
restore views reproduce the same measured project. Disposable replicas may
differ in rolling-database bytes, but must have the exact same path set,
non-rolling files, rolling-database size, and full semantic exports.

## Authority phases

[`ghidra_external_table_gap_boundary_live_authority.py`](../../tools/ghidra_external_table_gap_boundary_live_authority.py)
is read-only except for create-new aggregate-receipt publication by `seal`.
It never launches Ghidra.

1. `preflight` reproduces the scratch authority, hashes live and tracked PRE,
   verifies the current projection, and refuses existing ceremony/backup roots.
2. `check-live` is run only after replica, live, POST-backup, POST-restore, and
   create-new tracked-still-PRE inspection evidence exists. It requires the
   tracked project to remain exact PRE after POST recovery, proves exactly one
   successful live save, replays all semantic and collateral gates, and
   therefore durably separates the live write from the tracked refresh.
3. `seal` is run only after a separately authorized tracked refresh, tracked
   read-only restore, and mechanical projection. It replays every gate and
   writes one new ignored, repository-relative aggregate receipt.
4. `verify` reproduces that saved receipt without writing.

All aggregate paths are POSIX repository-relative roles. Absolute execution
history may remain inside the retained backup/open receipts, but it is checked
and never copied into the aggregate payload. Every PRE/live/tracked inspection,
replica copy, dry/apply/readback receipt, full inventory, project transition,
backup, retained restore, open-probe log, projection, and chronology edge is
recomputed rather than trusted as a saved success boolean. The live-lane census
requires exactly the nine named run directories, exactly their registered files,
and exactly those nine recursive `ghidra.log` paths.

## Required ceremony sequence

This runbook is a future procedure, not present authorization. Use it only on a
quiescent host after deliberately authorizing the live write and, later, the
tracked refresh. Stop on the first discrepancy. Never redirect any command
onto an existing receipt or log.

Set the exact roots in a PowerShell session:

```powershell
$ErrorActionPreference = 'Stop'
$repoRoot = (Resolve-Path -LiteralPath 'C:\Users\david\source\Onslaught-Career-Editor').Path
$toolsRoot = Join-Path $repoRoot 'tools'
$headless = 'D:\ghidra_12.1.2_PUBLIC_20260605\ghidra_12.1.2_PUBLIC\support\analyzeHeadless.bat'
$liveProject = 'C:\Users\david\Ghidra\Projects'
$trackedRoot = (Resolve-Path -LiteralPath (Join-Path $repoRoot 'reverse-engineering\ghidra')).Path
$lane = Join-Path $repoRoot 'local-lab\ghidra-external-table-gap-boundary-live-promotion-20260814-v1'
$preBackup = 'D:\BEA-Ghidra-Backups\2026-08-14-external-table-gap-boundaries-pre-live'
$postBackup = 'D:\BEA-Ghidra-Backups\2026-08-14-external-table-gap-boundaries-post-live'
$authorityReceipt = Join-Path $repoRoot 'local-lab\ghidra-external-table-gap-boundary-live-authority-20260814-v1\live-promotion.ready.json'
```

With Ghidra closed and the live project quiescent, run the read-only preflight:

```powershell
python -I -B (Join-Path $toolsRoot 'ghidra_external_table_gap_boundary_live_authority.py') preflight `
  --repo $repoRoot --scratch-repo $repoRoot --live-project $liveProject `
  --live-lane $lane --pre-backup $preBackup --post-backup $postBackup
```

Only the exact `EXTERNAL_TABLE_GAP_LIVE_PREFLIGHT_READY ...
mutation_authorized=false` sentinel is success. Then create the new evidence
root, capture PRE inspections, make the recoverable off-volume PRE backup, and
prove its retained read-only restore:

```powershell
New-Item -ItemType Directory -Path $lane | Out-Null
python -I -B (Join-Path $toolsRoot 'ghidra_project_backup.py') inspect $liveProject --output (Join-Path $lane 'live-pre-inspect.json')
python -I -B (Join-Path $toolsRoot 'ghidra_project_backup.py') inspect $trackedRoot --output (Join-Path $lane 'tracked-pre-inspect.json')
python -I -B (Join-Path $toolsRoot 'ghidra_project_backup.py') copy $liveProject $preBackup
python -I -B (Join-Path $toolsRoot 'ghidra_project_backup.py') verify $preBackup `
  --scratch-root (Join-Path $lane 'pre-backup-restore-probe') `
  --receipt (Join-Path $lane 'pre-backup-restore.ready.json') `
  --program-md5 '3b456964020070efe696d2cc09464a55' `
  --program-sha256 '74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750' `
  --analyze-headless $headless --script-path $toolsRoot --keep-probe-copy
python -I -B (Join-Path $toolsRoot 'ghidra_project_backup.py') copy $preBackup (Join-Path $lane 'projects\replica-a')
python -I -B (Join-Path $toolsRoot 'ghidra_project_backup.py') copy $preBackup (Join-Path $lane 'projects\replica-b')
```

Use one fresh headless process per mode. The helper below creates new run
directories, uses `-readOnly -noanalysis` for dry/readback, and permits a
writable project only for apply:

```powershell
function Invoke-ExternalTableGapRun {
    param(
        [Parameter(Mandatory=$true)][string]$ProjectRoot,
        [Parameter(Mandatory=$true)][string]$RunName,
        [Parameter(Mandatory=$true)][ValidateSet('dry','apply','readback')][string]$Mode,
        [bool]$ExportInventory = $false
    )
    $runRoot = Join-Path $lane ("runs\" + $RunName)
    New-Item -ItemType Directory -Path $runRoot | Out-Null
    $arguments = @($ProjectRoot, 'BEA', '-process', 'BEA.exe')
    if ($Mode -ne 'apply') { $arguments += '-readOnly' }
    $arguments += @(
        '-noanalysis', '-scriptPath', $toolsRoot,
        '-postScript', 'GhidraApplyExternalTableGapBoundaries.java',
        $repoRoot,
        (Join-Path $runRoot 'boundaries.tsv'),
        (Join-Path $runRoot 'boundaries.ready.json'),
        $Mode
    )
    if ($ExportInventory) {
        $arguments += @(
            '-postScript', 'ExportFullFunctionInventory.java',
            (Join-Path $runRoot 'functions.tsv'),
            (Join-Path $runRoot 'program.tsv')
        )
    }
    $arguments += @('-log', (Join-Path $runRoot 'ghidra.log'))
    & $headless @arguments
    if ($LASTEXITCODE -ne 0) { throw "Headless run failed: $RunName" }
}
```

Run both replicas through dry, apply, and separate readback before touching
live. Then run live dry/PRE export, re-inspect live immediately before apply,
perform exactly one live apply, and start a separate read-only POST process:

```powershell
Invoke-ExternalTableGapRun (Join-Path $lane 'projects\replica-a') 'replica-a-dry' 'dry'
Invoke-ExternalTableGapRun (Join-Path $lane 'projects\replica-b') 'replica-b-dry' 'dry'
Invoke-ExternalTableGapRun (Join-Path $lane 'projects\replica-a') 'replica-a-apply' 'apply'
Invoke-ExternalTableGapRun (Join-Path $lane 'projects\replica-b') 'replica-b-apply' 'apply'
Invoke-ExternalTableGapRun (Join-Path $lane 'projects\replica-a') 'replica-a-readback' 'readback' $true
Invoke-ExternalTableGapRun (Join-Path $lane 'projects\replica-b') 'replica-b-readback' 'readback' $true

Invoke-ExternalTableGapRun $liveProject 'live-pre-readback' 'dry' $true
python -I -B (Join-Path $toolsRoot 'ghidra_project_backup.py') inspect $liveProject --output (Join-Path $lane 'live-before-apply-inspect.json')
Invoke-ExternalTableGapRun $liveProject 'live-apply' 'apply'
Invoke-ExternalTableGapRun $liveProject 'live-readback' 'readback' $true
python -I -B (Join-Path $toolsRoot 'ghidra_inventory_diff.py') `
  (Join-Path $lane 'runs\live-pre-readback\functions.tsv') `
  (Join-Path $lane 'runs\live-readback\functions.tsv') `
  --json (Join-Path $lane 'runs\live-readback\inventory-diff.json')
```

Capture and restore-probe POST before any tracked write:

```powershell
python -I -B (Join-Path $toolsRoot 'ghidra_project_backup.py') inspect $liveProject --output (Join-Path $lane 'live-post-inspect.json')
python -I -B (Join-Path $toolsRoot 'ghidra_project_backup.py') copy $liveProject $postBackup
python -I -B (Join-Path $toolsRoot 'ghidra_project_backup.py') verify $postBackup `
  --scratch-root (Join-Path $lane 'post-backup-restore-probe') `
  --receipt (Join-Path $lane 'post-backup-restore.ready.json') `
  --program-md5 '3b456964020070efe696d2cc09464a55' `
  --program-sha256 '74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750' `
  --analyze-headless $headless --script-path $toolsRoot --keep-probe-copy
python -I -B (Join-Path $toolsRoot 'ghidra_project_backup.py') inspect $trackedRoot --output (Join-Path $lane 'tracked-still-pre-inspect.json')

python -I -B (Join-Path $toolsRoot 'ghidra_external_table_gap_boundary_live_authority.py') check-live `
  --repo $repoRoot --scratch-repo $repoRoot --live-project $liveProject `
  --live-lane $lane --pre-backup $preBackup --post-backup $postBackup
```

Do not refresh tracked unless `check-live` reports verdict
`LIVE_PHASE_REPRODUCED_TRACKED_STILL_PRE`. Its sentinel still says
`tracked_mutation_authorized=false`; with that evidence and separate
tracked-write authorization, copy only the exact project pair and rotate only
the expected old database:

```powershell
$sourceRoot = (Resolve-Path -LiteralPath $liveProject).Path
$sourceFiles = @((Get-Item -LiteralPath (Join-Path $sourceRoot 'BEA.gpr'))) +
    @(Get-ChildItem -LiteralPath (Join-Path $sourceRoot 'BEA.rep') -Recurse -File)
$trackedFiles = @((Get-Item -LiteralPath (Join-Path $trackedRoot 'BEA.gpr'))) +
    @(Get-ChildItem -LiteralPath (Join-Path $trackedRoot 'BEA.rep') -Recurse -File)
$sourceRelative = @($sourceFiles | ForEach-Object { $_.FullName.Substring($sourceRoot.Length + 1).Replace('\', '/') })
$trackedRelative = @($trackedFiles | ForEach-Object { $_.FullName.Substring($trackedRoot.Length + 1).Replace('\', '/') })
if ($sourceRelative.Count -ne 19 -or $trackedRelative.Count -ne 19) { throw 'Unexpected project file count' }
$difference = Compare-Object $trackedRelative $sourceRelative
$removed = @($difference | Where-Object SideIndicator -eq '<=' | ForEach-Object InputObject)
$added = @($difference | Where-Object SideIndicator -eq '=>' | ForEach-Object InputObject)
if ($removed.Count -ne 1 -or $removed[0] -cne 'BEA.rep/idata/00/~00000000.db/db.18611.gbf') { throw 'Unexpected tracked-only path' }
if ($added.Count -ne 1 -or $added[0] -cne 'BEA.rep/idata/00/~00000000.db/db.18613.gbf') { throw 'Unexpected live-only path' }
foreach ($source in $sourceFiles) {
    $relative = $source.FullName.Substring($sourceRoot.Length + 1)
    $destination = [IO.Path]::GetFullPath((Join-Path $trackedRoot $relative))
    if (-not $destination.StartsWith($trackedRoot + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)) { throw 'Tracked destination escape' }
    $parent = Split-Path -Parent $destination
    if (-not (Test-Path -LiteralPath $parent)) { New-Item -ItemType Directory -Path $parent | Out-Null }
    Copy-Item -LiteralPath $source.FullName -Destination $destination -Force
}
Remove-Item -LiteralPath (Join-Path $trackedRoot 'BEA.rep\idata\00\~00000000.db\db.18611.gbf') -Force
```

Inspect and restore-probe tracked POST, generate the exact projection into the
lane, verify the old tracked projection before replacing it, then seal and
re-verify the aggregate receipt:

```powershell
python -I -B (Join-Path $toolsRoot 'ghidra_project_backup.py') inspect $trackedRoot --output (Join-Path $lane 'tracked-post-inspect.json')
python -I -B (Join-Path $toolsRoot 'ghidra_project_backup.py') verify $trackedRoot `
  --scratch-root (Join-Path $lane 'tracked-post-restore-probe') `
  --receipt (Join-Path $lane 'tracked-post-restore.ready.json') `
  --program-md5 '3b456964020070efe696d2cc09464a55' `
  --program-sha256 '74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750' `
  --analyze-headless $headless --script-path $toolsRoot --keep-probe-copy

$laneProjection = Join-Path $lane 'ghidra-function-name-table-2026-08-13.tsv'
$trackedProjection = Join-Path $repoRoot 'reverse-engineering\binary-analysis\ghidra-function-name-table-2026-08-13.tsv'
python -I -B (Join-Path $toolsRoot 're_ghidra_name_projection.py') create `
  --inventory (Join-Path $lane 'runs\live-readback\functions.tsv') `
  --output $laneProjection `
  --expected-inventory-sha256 'c3942b9e340cef71b731290b845843697af5c53204449c51949b779e896272d6' `
  --source-label 'local-lab/ghidra-external-table-gap-boundary-live-promotion-20260814-v1/runs/live-readback/functions.tsv' `
  --projection-date '2026-08-14' `
  --specimen-sha256 '74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750'
if ((Get-Item -LiteralPath $trackedProjection).Length -ne 504598) { throw 'PRE projection byte count drift' }
if ((Get-FileHash -LiteralPath $trackedProjection -Algorithm SHA256).Hash.ToLowerInvariant() -ne 'c6084999cefebdb900ec752be5c4cb45ed1d7dcbdd086a53cbd207b91db84d20') { throw 'PRE projection hash drift' }
Copy-Item -LiteralPath $laneProjection -Destination $trackedProjection -Force

python -I -B (Join-Path $toolsRoot 'ghidra_external_table_gap_boundary_live_authority.py') seal `
  --repo $repoRoot --scratch-repo $repoRoot --live-project $liveProject `
  --live-lane $lane --pre-backup $preBackup --post-backup $postBackup `
  --output $authorityReceipt
python -I -B (Join-Path $toolsRoot 'ghidra_external_table_gap_boundary_live_authority.py') verify `
  --repo $repoRoot --scratch-repo $repoRoot --live-project $liveProject `
  --live-lane $lane --pre-backup $preBackup --post-backup $postBackup `
  --output $authorityReceipt
```

Only after the saved aggregate independently verifies may the promotion report,
canonical Ghidra metadata, post-admission gap accounting, and downstream
campaigns be updated. This preparation itself changes none of them.

## Current blocker

There is no missing input for preparation. The deliberate blocker is that the
future ceremony has not run: no live lane, PRE/POST backup, `db.18613.gbf`,
tracked POST restore, or final aggregate receipt exists. Creating those requires
the later live/tracked mutation authority; this candidate does not grant it.
