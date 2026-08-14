# PC function-body fragment Ghidra live-promotion preparation

Date: 2026-08-14

Status: **prepared only; no live or tracked Ghidra mutation performed**

Verdict: **PREPARATION_READY_MUTATION_NOT_AUTHORIZED**

Policy: **`PREPARATION_ONLY`**

Evidence: MEASURED PRE / prospective POST. The exact retained scratch authority
and its full tree reproduce; the live maintainer project and tracked canonical
project independently hash to the same current PRE twice around the comparison.
The POST semantic shape is fixed by two sealed scratch replicas, but the future
rolling Ghidra database bytes are deliberately unknown until a separately
authorized save.

Specimen: pristine PC retail `BEA.exe`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Preparation integration base: Git commit
`add5571c0779287f2e575c371e477cd33872662c`.

## Read-only preparation result

The preparation authority rehashed the live project, then tracked, then live
again without launching Ghidra. All three reads are byte-identical:

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
| Current rolling database | `db.18613.gbf`, 68,337,664 bytes, `615497847b0c732077ee7164b0973b9012092523e9ad99b91c21781952420ebe` |
| Stable preceding database | `db.18612.gbf`, 68,321,280 bytes, `424775377ea0f40d9e429c9219b9310d427760acc40548dbc588ca285f932f7b` |
| Full function inventory | 7,161,942 bytes, `c3942b9e340cef71b731290b845843697af5c53204449c51949b779e896272d6` |
| Program metrics | 1,267 bytes, `3e51ce1d5e926c632869b2058c9d89e91f48345a329a724ea9520570bd91212d` |
| Tracked projection | 508,242 bytes, `6e22a93a4792a2b5a9a6109a65e3b6460dc1ef6dc0606cc195a9a50e30ebdd68` |
| PRE body-range export | 1,198,388 bytes, `0101e6e8b34eaea8bd646a0fa9a8e4e448bef586c8b2b898c78241befde3aa6b` |

The retained scratch root is
`local-lab/ghidra-function-fragment5-range-scratch-20260814-v1/`. Its exact
whole-tree identity is 515 files / 3,085,497,716 bytes / SHA-256
`a4124ecf6186e977e86903cfef47535fece7a77bd202bcbceb34b2764cbad890`.
The portable aggregate receipt is 9,348 bytes / SHA-256
`a35f35ac99cd5d7251a86b7cf54c5aac2e2919870efca6566600045138571a04`.
It reproduces two saved positive replicas, two separate readbacks, two adverse
controls with exact PRE restoration, two containment refusals, and read-only
backup openability. The retained scratch package remains immutable; the future
ceremony does not append to it or reinterpret its `LIVE_FORBIDDEN` policy.

The canonical future evidence root, PRE backup, POST backup, and aggregate
authority root are all absent. That absence is the deliberate current blocker:
**future ceremony artifacts do not yet exist**. No directory was pre-created,
no Ghidra process was opened, and no file in live or tracked Ghidra changed.

## Exact prospective semantic POST

The reviewed five-row manifest permits only body-range addition and bounded
disassembly in five existing functions:

| Existing owner | Exact repair | Bytes |
| --- | ---: | ---: |
| `CFEPMain__Process @ 0x00462640` | `0x0046282B..0x00462B64` | 825 |
| `CGame__HandleEvent @ 0x0046FF10` | `0x004700DA..0x004700F0` | 22 |
| `CHud__RenderTargetIndicatorOverlay @ 0x00482590` | `0x00482725..0x00482741` | 28 |
| `CExplosionInitThing__SelectNextPathStepDirection @ 0x004BE420` | `0x004BE82D..0x004BE93D` | 272 |
| `CDXTexture__CreateMipmaps @ 0x00559410` | `0x0055954C..0x005595BB` | 111 |

The semantic POST is fixed:

| POST property | Exact value |
| --- | ---: |
| Internal functions | 8,280 (unchanged) |
| Changed owner rows | 5 |
| Byte-identical non-target rows | 8,275 |
| Body ranges | 8,396 |
| Owned `.text` bytes | 1,795,470 (+1,258) |
| `.text` ownership | 93.072115377% |
| Unowned `.text` bytes | 133,647 |
| Instructions | 551,014 (+23 net) |
| References | 234,478 (-17 net) |
| Full function inventory | 7,161,943 bytes / `d2ff1e8e7bd91454fff9822fb7ecc8e624525fa5c6cbc9dcfe06f4e0212b750d` |
| Program metrics | 1,267 bytes / `b389487a65d6271329703c9e3ec9186b7261aa871a154c31179322780e1c132e` |
| Mechanical projection | 508,239 bytes / `267210a78248f58da6bca1b4d11ee7b1812481602413e8bcac2fb4e4b4c4cb84` |
| Exact body-range export | 1,197,803 bytes / `495f1a86490e7b2646d2a0a6cd86bf6e4cdb071d5932b7d65ded1377621582e2` |

The twelve bytes at `0x00462B64..0x00462B70` remain excluded exact NOP
alignment. No function, name, signature, parameter, ABI/storage field, comment,
tag, data unit, stored non-function symbol, or memory byte may be created or
changed. The five body rows are the complete allowed inventory diff.

The physical POST is intentionally not guessed. One successful live save must
remove `db.18612.gbf`, retain exact `db.18613.gbf`, add nonempty
`db.18614.gbf`, and leave every other common project file byte-identical. The
new `db.18614.gbf` size and hash become acceptable only when live, the POST
backup, tracked, and both retained POST restore views reproduce the same bytes.

## Authority phases

[`ghidra_function_fragment_range_live_authority.py`](../../tools/ghidra_function_fragment_range_live_authority.py)
is 68,448 bytes, SHA-256
`01ba56f624943c5cd11f78242264b39b76919a0caf787ae699e0147c8882da80`.
It never launches Ghidra and never writes either project.

1. `preflight` reproduces the entire retained scratch identity, hashes live and
   tracked PRE twice around the comparison, verifies the current projection and
   accounting baseline, and refuses pre-existing ceremony or backup roots.
2. `check-live` is valid only after the PRE backup/open proof, one read-only PRE
   run, one separately authorized writable live apply, a separate read-only
   POST run, POST backup/restore, and a tracked-still-PRE inspection exist. It
   still says `tracked_mutation_authorized=false`.
3. `seal` is valid only after a separately authorized tracked refresh, tracked
   read-only restore, exact mechanical projection, and exact body accounting.
   Its only write is create-new publication of an ignored aggregate receipt.
4. `verify` reproduces that saved aggregate without writing.

The low-level Ghidra script retains its frozen scratch-era
`READY_FOR_SCRATCH_ONLY` / `LIVE_FORBIDDEN` receipt. That receipt never grants
authority. A future live run is permitted only by an explicit action-specific
authorization outside the script; the outer authority then treats the inner
receipt solely as a byte-exact structural measurement. This preparation grants
no such authorization.

## Prospective ceremony

This is a future runbook, not permission to run it. Use it only with Ghidra
closed, the maintainer project quiescent, and separate explicit authorization
for the live save. Stop on the first discrepancy.

Set the exact roots:

```powershell
$ErrorActionPreference = 'Stop'
$repoRoot = 'C:\Users\david\source\Onslaught-Career-Editor'
$evidenceRepo = $repoRoot
$toolsRoot = Join-Path $repoRoot 'tools'
$headless = 'D:\ghidra_12.1.2_PUBLIC_20260605\ghidra_12.1.2_PUBLIC\support\analyzeHeadless.bat'
$liveProject = 'C:\Users\david\Ghidra\Projects'
$trackedRoot = Join-Path $repoRoot 'reverse-engineering\ghidra'
$lane = Join-Path $repoRoot 'local-lab\ghidra-function-fragment5-range-live-promotion-20260814-v1'
$preBackup = 'D:\BEA-Ghidra-Backups\2026-08-14-function-fragment5-ranges-pre-live'
$postBackup = 'D:\BEA-Ghidra-Backups\2026-08-14-function-fragment5-ranges-post-live'
$authorityReceipt = Join-Path $repoRoot 'local-lab\ghidra-function-fragment5-range-live-authority-20260814-v1\live-promotion.ready.json'
```

Run the read-only preflight first:

```powershell
py -3 -I -B (Join-Path $toolsRoot 'ghidra_function_fragment_range_live_authority.py') preflight `
  --repo $repoRoot --evidence-repo $evidenceRepo --live-project $liveProject `
  --live-lane $lane --pre-backup $preBackup --post-backup $postBackup
```

Only the exact `FUNCTION_FRAGMENT_RANGE_LIVE_PREPARATION_READY ...
policy=PREPARATION_ONLY mutation_authorized=false
blocker=future_ceremony_artifacts_absent` sentinel is success. After separate
authorization, create the new lane and its exact manifest copy, inspect PRE,
make the off-volume PRE backup, and prove a retained read-only restore:

```powershell
New-Item -ItemType Directory -Path (Join-Path $lane 'static\final-a') | Out-Null
New-Item -ItemType Directory -Path (Join-Path $lane 'runs') | Out-Null
Copy-Item -LiteralPath (Join-Path $repoRoot 'reverse-engineering\binary-analysis\pc-function-body-fragment-repairs-2026-08-14.tsv') `
  -Destination (Join-Path $lane 'static\final-a\fragment-manifest.tsv')
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

Use one fresh process per run. Read-only PRE and POST export the full inventory;
the only writable invocation is `live-apply`:

```powershell
function Invoke-FunctionFragmentRun {
    param(
        [Parameter(Mandatory=$true)][string]$RunName,
        [Parameter(Mandatory=$true)][ValidateSet('dry','apply','readback')][string]$Mode,
        [bool]$ExportInventory = $false
    )
    $runRoot = Join-Path $lane ('runs\' + $RunName)
    New-Item -ItemType Directory -Path $runRoot | Out-Null
    $arguments = @($liveProject, 'BEA', '-process', 'BEA.exe')
    if ($Mode -ne 'apply') { $arguments += '-readOnly' }
    $arguments += @(
        '-noanalysis', '-scriptPath', $toolsRoot,
        '-postScript', 'GhidraApplyFunctionFragmentRanges.java',
        $lane, (Join-Path $runRoot 'result.tsv'),
        (Join-Path $runRoot 'result.ready.json'), $Mode
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

Invoke-FunctionFragmentRun 'live-pre-readback' 'dry' $true
py -3 -I -B (Join-Path $toolsRoot 'ghidra_project_backup.py') inspect $liveProject --output (Join-Path $lane 'live-before-apply-inspect.json')
Invoke-FunctionFragmentRun 'live-apply' 'apply'
Invoke-FunctionFragmentRun 'live-readback' 'readback' $true
py -3 -I -B (Join-Path $toolsRoot 'ghidra_inventory_diff.py') `
  (Join-Path $lane 'runs\live-pre-readback\functions.tsv') `
  (Join-Path $lane 'runs\live-readback\functions.tsv') `
  --json (Join-Path $lane 'runs\live-readback\inventory-diff.json')
```

Capture POST and prove tracked is still PRE before any tracked write:

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
py -3 -I -B (Join-Path $toolsRoot 'ghidra_function_fragment_range_live_authority.py') check-live `
  --repo $repoRoot --evidence-repo $evidenceRepo --live-project $liveProject `
  --live-lane $lane --pre-backup $preBackup --post-backup $postBackup
```

Do not refresh tracked unless `check-live` reports
`LIVE_PHASE_REPRODUCED_TRACKED_STILL_PRE`. With separate tracked-write
authorization, copy the exact live project pair into tracked, require the sole
path rotation `db.18612.gbf` -> `db.18614.gbf`, and remove only the obsolete
tracked `db.18612.gbf`:

```powershell
$sourceRoot = (Resolve-Path -LiteralPath $liveProject).Path
$trackedRoot = (Resolve-Path -LiteralPath $trackedRoot).Path
$sourceFiles = @((Get-Item -LiteralPath (Join-Path $sourceRoot 'BEA.gpr'))) +
    @(Get-ChildItem -LiteralPath (Join-Path $sourceRoot 'BEA.rep') -Recurse -File)
$trackedFiles = @((Get-Item -LiteralPath (Join-Path $trackedRoot 'BEA.gpr'))) +
    @(Get-ChildItem -LiteralPath (Join-Path $trackedRoot 'BEA.rep') -Recurse -File)
$sourceRelative = @($sourceFiles | ForEach-Object {
    $_.FullName.Substring($sourceRoot.Length + 1).Replace('\', '/')
})
$trackedRelative = @($trackedFiles | ForEach-Object {
    $_.FullName.Substring($trackedRoot.Length + 1).Replace('\', '/')
})
if ($sourceRelative.Count -ne 19 -or $trackedRelative.Count -ne 19) {
    throw 'Unexpected project file count'
}
$difference = Compare-Object $trackedRelative $sourceRelative
$removed = @($difference | Where-Object SideIndicator -eq '<=' | ForEach-Object InputObject)
$added = @($difference | Where-Object SideIndicator -eq '=>' | ForEach-Object InputObject)
if ($removed.Count -ne 1 -or $removed[0] -cne 'BEA.rep/idata/00/~00000000.db/db.18612.gbf') {
    throw 'Unexpected tracked-only path'
}
if ($added.Count -ne 1 -or $added[0] -cne 'BEA.rep/idata/00/~00000000.db/db.18614.gbf') {
    throw 'Unexpected live-only path'
}
foreach ($source in $sourceFiles) {
    $relative = $source.FullName.Substring($sourceRoot.Length + 1)
    $destination = [IO.Path]::GetFullPath((Join-Path $trackedRoot $relative))
    if (-not $destination.StartsWith(
        $trackedRoot + [IO.Path]::DirectorySeparatorChar,
        [StringComparison]::OrdinalIgnoreCase
    )) { throw 'Tracked destination escape' }
    $parent = Split-Path -Parent $destination
    if (-not (Test-Path -LiteralPath $parent)) {
        New-Item -ItemType Directory -Path $parent | Out-Null
    }
    Copy-Item -LiteralPath $source.FullName -Destination $destination -Force
}
Remove-Item -LiteralPath (
    Join-Path $trackedRoot 'BEA.rep\idata\00\~00000000.db\db.18612.gbf'
) -Force
```

Then inspect and restore-probe tracked POST:

```powershell
py -3 -I -B (Join-Path $toolsRoot 'ghidra_project_backup.py') inspect $trackedRoot --output (Join-Path $lane 'tracked-post-inspect.json')
py -3 -I -B (Join-Path $toolsRoot 'ghidra_project_backup.py') verify $trackedRoot `
  --scratch-root (Join-Path $lane 'tracked-post-restore-probe') `
  --receipt (Join-Path $lane 'tracked-post-restore.ready.json') `
  --program-md5 '3b456964020070efe696d2cc09464a55' `
  --program-sha256 '74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750' `
  --analyze-headless $headless --script-path $toolsRoot --keep-probe-copy
```

Refresh the projection mechanically from the exact live POST inventory, then
export exact body accounting from tracked POST in a separate read-only process:

```powershell
$laneProjection = Join-Path $lane 'ghidra-function-name-table-2026-08-13.tsv'
$trackedProjection = Join-Path $repoRoot 'reverse-engineering\binary-analysis\ghidra-function-name-table-2026-08-13.tsv'
py -3 -I -B (Join-Path $toolsRoot 're_ghidra_name_projection.py') create `
  --inventory (Join-Path $lane 'runs\live-readback\functions.tsv') `
  --output $laneProjection `
  --expected-inventory-sha256 'd2ff1e8e7bd91454fff9822fb7ecc8e624525fa5c6cbc9dcfe06f4e0212b750d' `
  --source-label 'local-lab/ghidra-function-fragment5-range-live-promotion-20260814-v1/runs/live-readback/functions.tsv' `
  --projection-date '2026-08-14' `
  --specimen-sha256 '74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750'
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

Only after both refreshes reproduce their prospective exact stamps may the
aggregate be sealed and verified:

```powershell
py -3 -I -B (Join-Path $toolsRoot 'ghidra_function_fragment_range_live_authority.py') seal `
  --repo $repoRoot --evidence-repo $evidenceRepo --live-project $liveProject `
  --live-lane $lane --pre-backup $preBackup --post-backup $postBackup `
  --output $authorityReceipt
py -3 -I -B (Join-Path $toolsRoot 'ghidra_function_fragment_range_live_authority.py') verify `
  --repo $repoRoot --evidence-repo $evidenceRepo --live-project $liveProject `
  --live-lane $lane --pre-backup $preBackup --post-backup $postBackup `
  --output $authorityReceipt
```

## Current blocker

The preparation is complete and reproducible, but the live lane, PRE backup,
POST backup, tracked POST restore, refreshed projection/accounting, and final
aggregate receipt do not exist. That is intentional. Until an explicit future
authorization creates them in the exact order above, the only valid verdict is
`PREPARATION_READY_MUTATION_NOT_AUTHORIZED`.
