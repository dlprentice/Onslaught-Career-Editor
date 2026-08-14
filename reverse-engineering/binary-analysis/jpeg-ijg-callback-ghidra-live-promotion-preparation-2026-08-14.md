# JPEG/IJG callback Ghidra live-promotion preparation

Status: **historical pre-fragment preparation; current db.18614 re-ground required**

Date: 2026-08-14

Verdict: **PREPARATION_SUPERSEDED_REQUIRES_CURRENT_REGROUND**

Policy: **`PREPARATION_ONLY`**

Evidence: MEASURED — historical PRE / prospective POST. Raw-file hashing
re-grounded the then-current live maintainer project and tracked canonical project twice around their
comparison without opening Ghidra. The retained JPEG24 scratch authority and
whole evidence tree reproduce exactly. The semantic POST is fixed by two saved
scratch replicas, while the future rolling database bytes remain deliberately
unknown until a separately authorized save.

Specimen: pristine PC retail `BEA.exe`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Preparation base: Git commit
`3a2397aec192330a9d26f4615b3e1aee599e7850`.

Current-state note: this preparation performed no Ghidra write. The separate
five-body repair has since advanced live/tracked Ghidra from `db.18613` to
`db.18614` without changing the 8,280-function count. The JPEG24 structural
proof remains retained, but every PRE, POST, projection, and physical-database
pin below must be regenerated before a new promotion ceremony.

## Read-only preparation result

At preparation time, the live and tracked projects were byte-identical at the
then-current 8,280-function PRE:

| PRE property | Exact value |
| --- | --- |
| Internal functions | 8,280 |
| Body ranges | 8,400 |
| Owned `.text` bytes | 1,794,212 |
| Instructions | 550,991 |
| References | 234,495 |
| Project files | 19 |
| Project bytes | 186,960,773 |
| Canonical project inventory | `ae422079966978ec2f8f5b951b0ef5812b1074bd708ab8d782179f51c90efcf2` |
| Current database | `db.18613.gbf`, 68,337,664 bytes, `615497847b0c732077ee7164b0973b9012092523e9ad99b91c21781952420ebe` |
| Preceding database | `db.18612.gbf`, 68,321,280 bytes, `424775377ea0f40d9e429c9219b9310d427760acc40548dbc588ca285f932f7b` |
| Full function inventory | 7,161,942 bytes, `c3942b9e340cef71b731290b845843697af5c53204449c51949b779e896272d6` |
| Program metrics | 1,267 bytes, `3e51ce1d5e926c632869b2058c9d89e91f48345a329a724ea9520570bd91212d` |
| Tracked projection | 508,242 bytes, `6e22a93a4792a2b5a9a6109a65e3b6460dc1ef6dc0606cc195a9a50e30ebdd68` |
| PRE body accounting | 1,198,388 bytes, `0101e6e8b34eaea8bd646a0fa9a8e4e448bef586c8b2b898c78241befde3aa6b` |

The retained scratch root is
`local-lab/ghidra-jpeg24-boundary-current-scratch-20260814-v1/`. Its
create-new READY is 7,077 bytes / SHA-256
`573c550c7197e15cc098ff0dd09ce55467c7bae95ca2ec4efcf9e045e0954b63`.
The sealed tree excluding that receipt is 258 files / 1,013,137,450 bytes /
SHA-256
`7c3df3b029b3f175a41bbbf698c1b47dfd5f18c02f7616494794225f3dc2058c`.
It reproduces two saved positive replicas, separate readbacks, exact
preservation of all 8,280 PRE rows, two rollback controls, two external-path
refusals, and retained read-only backup recovery.

No future live lane, PRE backup, POST backup, or aggregate-authority directory
was created. Their absence is the deliberate current blocker.

## Exact prospective POST

The exact [24-row manifest](jpeg-ijg-callback-function-boundaries-2026-08-14.tsv)
permits only default-metadata function creation and bounded disassembly inside
38 pairwise-disjoint body ranges:

| POST property | Exact value |
| --- | --- |
| Internal functions | 8,304 (+24) |
| Preserved PRE rows | 8,280 byte-identical |
| Body ranges | 8,438 (+38) |
| Owned `.text` bytes | 1,809,029 (+14,817) |
| Unowned `.text` bytes | 120,088 |
| `.text` ownership | 93.774975805% |
| Instructions | 551,032 (+41 net) |
| References | 234,484 (-11 net) |
| Full function inventory | 7,177,775 bytes / `dce886c9ee9ddee96a2e27baff616723211b7818c2d9277e19e3202d6a307804` |
| Program metrics | 1,267 bytes / `b154869020140b266e06dd5ef07d4fd99c71e328a1ffb1223d4d4c6db4b3a5e9` |
| Mechanical projection | 509,334 bytes / `e7ac5b35d0535c6d8bfd42fe46aea72edd24caf0772f2b9ba74a718dabdb474b` |
| Exact body accounting | 1,203,246 bytes / `0050347df1e78eafb9ef758ebd86acdbfc05bf4a349381c7960e174c16df0ef0` |

The `0x005B6800..0x005B6A86` body is one 646-byte function. At POST,
`0x005B6900` must be neither data nor a function entry. It is owned by
`FUN_005b6800` only as the final byte of `0F B6 00` / `MOVZX EAX,byte ptr
[EAX]` beginning at `0x005B68FE`. The pinned PRE misaligned decode at
`0x005B6900` must be gone. The seven DWORDs at `0x005B4EB0` and four NOP bytes
at `0x005B4ECC` remain unchanged and outside the cohort.

No provider-qualified IJG label is promoted as an original linker name. No
signature, parameter, ABI/storage field, comment, tag, data definition,
executable byte, runtime contract, campaign grade, or rebuild behavior may
change.

The physical POST is intentionally not guessed. One successful live save must
remove `db.18612.gbf`, retain exact `db.18613.gbf`, add nonempty
`db.18614.gbf`, and preserve every other common project file byte-for-byte.
The new database size and hash become acceptable only when live, POST backup,
tracked, and both retained POST restore views reproduce them.

## Authority phases

[`ghidra_jpeg_callback_boundary_live_authority.py`](../../tools/ghidra_jpeg_callback_boundary_live_authority.py)
never launches Ghidra and never writes either project.

1. `preflight` reproduces the exact retained scratch receipt and tree, hashes
   live and tracked PRE, verifies the PRE projection and accounting, derives
   the exact prospective projection/accounting in memory, and refuses any
   pre-existing future ceremony root.
2. `check-live` accepts only a PRE backup/open proof, one read-only PRE run,
   exactly one separately authorized live save, separate read-only POST
   inventory and listing-state readback, POST backup/restore, and a durable
   tracked-still-PRE inspection. Its sentinel still says
   `tracked_mutation_authorized=false`.
3. `seal` accepts only the separately authorized tracked refresh, tracked
   read-only restore, exact mechanical projection, and exact body accounting.
   Its sole write is create-new publication of one ignored aggregate receipt.
4. `verify` reproduces the saved aggregate without writing.

The inner mutator's body-set authorization is not action authority. The outer
policy remains `PREPARATION_ONLY` until a future action-specific authorization
permits one live save and, separately, one tracked refresh.

## Prospective ceremony

This is a future runbook, not permission to execute it. Use it only with
Ghidra closed, the maintainer project quiescent, and explicit authorization.
Stop at the first discrepancy.

Set the exact roots:

```powershell
$ErrorActionPreference = 'Stop'
$repoRoot = 'C:\Users\david\source\Onslaught-Career-Editor'
$scratchRepo = 'C:\Users\david\source\Onslaught-Career-Editor-lane-jpeg24-scratch-admission'
$toolsRoot = Join-Path $repoRoot 'tools'
$headless = 'D:\ghidra_12.1.2_PUBLIC_20260605\ghidra_12.1.2_PUBLIC\support\analyzeHeadless.bat'
$liveProject = 'C:\Users\david\Ghidra\Projects'
$trackedRoot = Join-Path $repoRoot 'reverse-engineering\ghidra'
$lane = Join-Path $repoRoot 'local-lab\ghidra-jpeg24-boundary-live-promotion-20260814-v1'
$preBackup = 'D:\BEA-Ghidra-Backups\2026-08-14-jpeg24-boundaries-pre-live'
$postBackup = 'D:\BEA-Ghidra-Backups\2026-08-14-jpeg24-boundaries-post-live'
$authorityReceipt = Join-Path $repoRoot 'local-lab\ghidra-jpeg24-boundary-live-authority-20260814-v1\live-promotion.ready.json'
```

Run the read-only preflight. It creates nothing:

```powershell
py -3 -I -B (Join-Path $toolsRoot 'ghidra_jpeg_callback_boundary_live_authority.py') preflight `
  --repo $repoRoot --scratch-repo $scratchRepo --live-project $liveProject `
  --live-lane $lane --pre-backup $preBackup --post-backup $postBackup
```

Only `JPEG_CALLBACK_BOUNDARY_LIVE_PREPARATION_READY ...
policy=PREPARATION_ONLY mutation_authorized=false
blocker=future_ceremony_artifacts_absent` is success.

After separate authorization, create only the new evidence roots and freeze the
manifest plus diagnostic address list:

```powershell
New-Item -ItemType Directory -Path (Join-Path $lane 'static\final-a') | Out-Null
New-Item -ItemType Directory -Path (Join-Path $lane 'runs') | Out-Null
Copy-Item -LiteralPath (Join-Path $repoRoot 'reverse-engineering\binary-analysis\jpeg-ijg-callback-function-boundaries-2026-08-14.tsv') `
  -Destination (Join-Path $lane 'static\final-a\jpeg-boundaries.tsv')
Copy-Item -LiteralPath (Join-Path $scratchRepo 'local-lab\ghidra-jpeg24-boundary-current-scratch-20260814-v1\inputs\diagnostic-addresses.txt') `
  -Destination (Join-Path $lane 'static\final-a\diagnostic-addresses.txt')
py -3 -I -B (Join-Path $toolsRoot 'ghidra_project_backup.py') inspect $liveProject --output (Join-Path $lane 'live-pre-inspect.json')
py -3 -I -B (Join-Path $toolsRoot 'ghidra_project_backup.py') inspect $trackedRoot --output (Join-Path $lane 'tracked-pre-inspect.json')
py -3 -I -B (Join-Path $toolsRoot 'ghidra_project_backup.py') copy $liveProject $preBackup
py -3 -I -B (Join-Path $toolsRoot 'ghidra_project_backup.py') verify $preBackup `
  --scratch-root (Join-Path $lane 'pre-backup-restore-probe') `
  --receipt (Join-Path $lane 'pre-backup-restore.ready.json') `
  --program-md5 '3b456964020070efe696d2cc09464a55' `
  --program-sha256 '74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750' `
  --analyze-headless $headless --script-path $toolsRoot --keep-probe-copy
```

Use a new directory and process for each phase. Only `live-apply` is writable:

```powershell
function Invoke-JpegBoundaryRun {
    param(
        [Parameter(Mandatory=$true)][ValidateSet('dry','apply','readback')][string]$Mode,
        [Parameter(Mandatory=$true)][string]$RunName,
        [bool]$ExportState = $false
    )
    $run = Join-Path $lane ('runs\' + $RunName)
    New-Item -ItemType Directory -Path $run | Out-Null
    $args = @($liveProject, 'BEA', '-process', 'BEA.exe')
    if ($Mode -ne 'apply') { $args += '-readOnly' }
    $args += @(
        '-noanalysis', '-scriptPath', $toolsRoot,
        '-postScript', 'GhidraApplyJpegCallbackBoundaries.java',
        $repoRoot, (Join-Path $run 'boundaries.tsv'),
        (Join-Path $run 'boundaries.ready.json'), $Mode
    )
    if ($ExportState) {
        $args += @(
            '-postScript', 'ExportFullFunctionInventory.java',
            (Join-Path $run 'functions.tsv'), (Join-Path $run 'program.tsv'),
            '-postScript', 'DiagnoseAddressListingState.java',
            (Join-Path $lane 'static\final-a\diagnostic-addresses.txt'),
            (Join-Path $run 'listing-state.tsv')
        )
    }
    $args += @('-log', (Join-Path $run 'ghidra.log'))
    & $headless @args
    if ($LASTEXITCODE -ne 0) { throw "Headless run failed: $RunName" }
}

Invoke-JpegBoundaryRun 'dry' 'live-pre-readback' $true
py -3 -I -B (Join-Path $toolsRoot 'ghidra_project_backup.py') inspect $liveProject --output (Join-Path $lane 'live-before-apply-inspect.json')
Invoke-JpegBoundaryRun 'apply' 'live-apply'
Invoke-JpegBoundaryRun 'readback' 'live-readback' $true
py -3 -I -B (Join-Path $toolsRoot 'ghidra_inventory_diff.py') `
  (Join-Path $lane 'runs\live-pre-readback\functions.tsv') `
  (Join-Path $lane 'runs\live-readback\functions.tsv') `
  --json (Join-Path $lane 'runs\live-readback\inventory-diff.json')
```

Capture POST recovery and prove tracked is still PRE:

```powershell
py -3 -I -B (Join-Path $toolsRoot 'ghidra_project_backup.py') inspect $liveProject --output (Join-Path $lane 'live-post-inspect.json')
py -3 -I -B (Join-Path $toolsRoot 'ghidra_project_backup.py') copy $liveProject $postBackup
py -3 -I -B (Join-Path $toolsRoot 'ghidra_project_backup.py') verify $postBackup `
  --scratch-root (Join-Path $lane 'post-backup-restore-probe') `
  --receipt (Join-Path $lane 'post-backup-restore.ready.json') `
  --program-md5 '3b456964020070efe696d2cc09464a55' `
  --program-sha256 '74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750' `
  --analyze-headless $headless --script-path $toolsRoot --keep-probe-copy
py -3 -I -B (Join-Path $toolsRoot 'ghidra_project_backup.py') inspect $trackedRoot --output (Join-Path $lane 'tracked-still-pre-inspect.json')
py -3 -I -B (Join-Path $toolsRoot 'ghidra_jpeg_callback_boundary_live_authority.py') check-live `
  --repo $repoRoot --scratch-repo $scratchRepo --live-project $liveProject `
  --live-lane $lane --pre-backup $preBackup --post-backup $postBackup
```

Do not refresh tracked unless `check-live` reports
`LIVE_PHASE_REPRODUCED_TRACKED_STILL_PRE` and a separate tracked-write
authorization exists. The copy must contain exactly 19 files, remove only
`BEA.rep/idata/00/~00000000.db/db.18612.gbf`, add only
`BEA.rep/idata/00/~00000000.db/db.18614.gbf`, and preserve exact
`db.18613.gbf` plus every other common file. Reuse the guarded project-pair
copy procedure in the preceding
[external-table preparation](external-table-gap-ghidra-live-promotion-preparation-2026-08-14.md)
with those exact path substitutions; do not use an unbounded directory copy.

After that bounded refresh, inspect and restore-probe tracked POST, then derive
the projection and accounting after the restore proof:

```powershell
py -3 -I -B (Join-Path $toolsRoot 'ghidra_project_backup.py') inspect $trackedRoot --output (Join-Path $lane 'tracked-post-inspect.json')
py -3 -I -B (Join-Path $toolsRoot 'ghidra_project_backup.py') verify $trackedRoot `
  --scratch-root (Join-Path $lane 'tracked-post-restore-probe') `
  --receipt (Join-Path $lane 'tracked-post-restore.ready.json') `
  --program-md5 '3b456964020070efe696d2cc09464a55' `
  --program-sha256 '74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750' `
  --analyze-headless $headless --script-path $toolsRoot --keep-probe-copy

$laneProjection = Join-Path $lane 'ghidra-function-name-table-2026-08-13.tsv'
$trackedProjection = Join-Path $repoRoot 'reverse-engineering\binary-analysis\ghidra-function-name-table-2026-08-13.tsv'
py -3 -I -B (Join-Path $toolsRoot 're_ghidra_name_projection.py') create `
  --inventory (Join-Path $lane 'runs\live-readback\functions.tsv') `
  --output $laneProjection `
  --expected-inventory-sha256 'dce886c9ee9ddee96a2e27baff616723211b7818c2d9277e19e3202d6a307804' `
  --source-label 'local-lab/ghidra-jpeg24-boundary-live-promotion-20260814-v1/runs/live-readback/functions.tsv' `
  --projection-date '2026-08-14' `
  --specimen-sha256 '74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750'
if ((Get-Item $trackedProjection).Length -ne 508242) { throw 'PRE projection bytes drift' }
if ((Get-FileHash $trackedProjection -Algorithm SHA256).Hash.ToLowerInvariant() -ne '6e22a93a4792a2b5a9a6109a65e3b6460dc1ef6dc0606cc195a9a50e30ebdd68') { throw 'PRE projection hash drift' }
Copy-Item -LiteralPath $laneProjection -Destination $trackedProjection -Force

$accounting = Join-Path $lane 'tracked-post-accounting'
New-Item -ItemType Directory -Path $accounting | Out-Null
& $headless $trackedRoot 'BEA' '-process' 'BEA.exe' '-readOnly' '-noanalysis' `
  '-scriptPath' $toolsRoot '-postScript' 'ExportParityLabGraph.java' `
  (Join-Path $accounting 'body-ranges.tsv') `
  (Join-Path $accounting 'direct-calls.tsv') `
  (Join-Path $accounting 'parity-graph.ready.json') `
  '-log' (Join-Path $accounting 'ghidra.log')
if ($LASTEXITCODE -ne 0) { throw 'Tracked POST accounting export failed' }
```

Only after every exact gate reproduces may the aggregate be sealed and
verified:

```powershell
py -3 -I -B (Join-Path $toolsRoot 'ghidra_jpeg_callback_boundary_live_authority.py') seal `
  --repo $repoRoot --scratch-repo $scratchRepo --live-project $liveProject `
  --live-lane $lane --pre-backup $preBackup --post-backup $postBackup `
  --output $authorityReceipt
py -3 -I -B (Join-Path $toolsRoot 'ghidra_jpeg_callback_boundary_live_authority.py') verify `
  --repo $repoRoot --scratch-repo $scratchRepo --live-project $liveProject `
  --live-lane $lane --pre-backup $preBackup --post-backup $postBackup `
  --output $authorityReceipt
```

## Current blocker

The retained semantic fixtures and ceremony topology remain useful, but the
exact PRE pins describe historical `db.18613`. A fresh current-state authority
must re-ground `db.18614`, prove all 8,280 current rows and 8,396 ranges, and
derive a new prospective POST before any ceremony. The live lane, backups,
one-save evidence, tracked POST restore, and aggregate receipt also remain
absent. Therefore this preparation cannot authorize the next promotion.
