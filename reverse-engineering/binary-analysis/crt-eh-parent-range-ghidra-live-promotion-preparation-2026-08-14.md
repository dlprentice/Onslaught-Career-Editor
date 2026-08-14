# CRT EH parent-range Ghidra live-promotion preparation

Date: 2026-08-14

Status: **preparation reproduced; live ceremony not started**

Verdict: **PREPARATION_READY_MUTATION_NOT_AUTHORIZED**

Policy: **`PREPARATION_ONLY`**

Evidence: MEASURED — exact current PRE and sealed scratch POST. The read-only
authority replays the complete retained scratch package, hashes the live project
twice around the tracked-project comparison, mechanically reproduces the
tracked name projection and body accounting, and refuses because every future
ceremony, backup, and aggregate-authority root is absent.

Specimen: pristine PC retail `BEA.exe`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Preparation base: Git commit
`1ae3b33dbaf1b8a96f32f871ddd6bc42cec9b0be`.

## Read-only PRE result

No Ghidra process was opened. The authority read live, tracked, then live again
and obtained byte-identical project inventories:

| PRE property | Exact value |
| --- | --- |
| Internal functions | 8,327 |
| Body ranges | 8,458 |
| Owned `.text` bytes | 1,811,418 |
| `.text` ownership | 93.898814846% |
| Instructions | 551,133 |
| References | 234,478 |
| Project files | 19 |
| Project bytes | 187,009,925 |
| Canonical project inventory | `61f77b70fdf807c960a9441ea8e5c4a5b5bd6281675864089a52d61481432f1f` |
| Stable database | `db.18616.gbf`, 68,354,048 bytes / `f0d4988cfa1f36529ed3687816e231bfcc8323240e7d3f9837de48941b8f64fc` |
| Preceding database | `db.18615.gbf`, 68,354,048 bytes / `6c2fc2f12394cf7b63f4f335173ba0a19b52b92c50dc4d2da987170501bc9681` |
| Full function inventory | 7,192,980 bytes / `8640c35a820b3c5e415b947fa8a13eeb5c7c535868780dc2fe511d020a54c40e` |
| Program metrics | 1,267 bytes / `185dbd4a9939edacf7302c00c7c48351ad23ad51be14bd5d431130d13848170a` |
| Name projection | 510,429 bytes / `17c7153cca64cf6b887dc0bd8d6a7576cfdcd41ce81528c516065ef7e9fa041c` |
| Body-range export | 1,205,737 bytes / `46138dc9b81ce2d0f835994f38581ba07564ddf17a7774ddbedfdb2e3d33e335` |
| Direct-call export | 1,397,680 bytes / `159f7c89aae54df927186d71263941b5f0857debe09556097820f098da8fa9d8` |

The direct-call graph has 14,598 exact direct edges and 27,244 direct call
sites. The added filter/handler contains no call instruction, so the prospective
POST must retain that export byte-for-byte.

## Reproduced scratch authority

The immutable retained package is
`local-lab/crt-eh-parent-repair-db18616-20260814-v1/formal/`.
Excluding its aggregate receipt, it is 283 files / 1,518,299,333 bytes / tree
SHA-256
`bd7545cd76571ec9a6c20f6a981a0f7933e0a9d629ad7867ecdddf8c0c6a8a49`.
Its 3,877-byte receipt has SHA-256
`3d472b734d4a3eeb19a896e713e1f2d2cc1dfbac5befcd66ef8c39ad0618eb82`.

That package re-proves two positive saved replicas and separate readbacks, two
forced-failure controls followed by exact PRE restoration, two containment
refusals, a recoverable backup with read-only open proof, exact retail/demo
scope-table lineage, and all 8,326 non-target function rows byte-identical.
Its `LIVE_FORBIDDEN` policy remains unchanged and grants no authority to touch
the canonical project.

## Exact prospective POST

The one-row
[manifest](crt-eh-parent-range-repair-2026-08-14.tsv) authorizes only the
existing owner `CRT__LongJmpProbe_NoOp @ 0x005D0A9F` to absorb
`0x005D0AD6..0x005D0AEF`. The resulting body is exactly
`0x005D0A9F..0x005D0B04`, 101 bytes, SHA-256
`50016632446f1259b35479440c4a14ca82c8ac59a6c4f78a34f146bd119b61c3`.
The filter entry `0x005D0AD6` and handler entry `0x005D0AEA` remain interior
addresses and must not become functions.

| POST property | Exact value |
| --- | ---: |
| Internal functions | 8,327 (unchanged) |
| Changed function rows | 1 |
| Exact non-target rows | 8,326 |
| Body ranges | 8,457 (-1) |
| Owned `.text` bytes | 1,811,443 (+25) |
| `.text` ownership | 93.900110776% |
| Unowned `.text` bytes | 117,674 |
| Instructions | 551,143 (+10) |
| References | 234,478 (unchanged) |
| Full function inventory | 7,192,981 bytes / `08886e03b846668681301f0f2ec2ba9ac1af0463faa1835c57abe9e717ebd866` |
| Program metrics | 1,267 bytes / `e77082ead314ccb44ba070a7b42222e063ec1078d22ab2203fa6ee8968f99909` |
| Mechanical projection | 510,431 bytes / `64c87111651ad37437be96ce3712abe6fafb762f0e545393c8dc65f8ac583669` |
| Exact body-range export | 1,205,601 bytes / `45e9521e8145c506842767604f10c04fdb0087ad199859207736e5e7d58bdbce` |

Program bytes, defined data, stored non-function symbols, names, signatures,
parameters, calling conventions, comments, tags, references, and the direct-call
graph must remain exact. Only the target's body bytes/digest/range count and
instruction count, the global instruction layout/count, and the corresponding
undefined-data count may change.

The future physical database hash is intentionally not guessed. Exactly one
successful live save must remove `db.18615.gbf`, retain exact `db.18616.gbf`,
add nonempty `db.18617.gbf`, and leave every common project file byte-identical.
The new rolling database is acceptable only when live, the POST backup,
tracked, and both retained POST restore views reproduce it exactly.

## Four-mode authority

[`ghidra_crt_eh_parent_range_live_authority.py`](../../tools/ghidra_crt_eh_parent_range_live_authority.py)
is 71,504 bytes, SHA-256
`8a1a4bd536992aae598d252d8059209a1d8c3c19678b64484280086c5116ddfd`.
It never launches Ghidra and never writes either project.

1. `preflight` replays the scratch receipt/tree, hashes live and tracked PRE,
   mechanically rebuilds the current projection, validates all 8,458 PRE body
   ranges and the exact call graph, and requires every future root to be absent.
2. `check-live` becomes usable only after a separately authorized PRE backup,
   retained read-only restore, dry run, single writable live apply, separate
   POST readback, POST backup/restore, and tracked-still-PRE inspection. It still
   reports `tracked_mutation_authorized=false`.
3. `seal` becomes usable only after a separately authorized exact tracked
   refresh, retained tracked restore, mechanical projection, and read-only body
   and direct-call accounting. Its sole write is create-new publication of one
   ignored aggregate receipt.
4. `verify` recomputes that saved aggregate and writes nothing.

Canonical future paths are:

- live evidence:
  `local-lab/ghidra-crt-eh-parent-range-live-promotion-db18616-20260814-v1/`;
- PRE backup:
  `D:\BEA-Ghidra-Backups\2026-08-14-crt-eh-parent-range-pre-live`;
- POST backup:
  `D:\BEA-Ghidra-Backups\2026-08-14-crt-eh-parent-range-post-live`;
- aggregate receipt:
  `local-lab/ghidra-crt-eh-parent-range-live-authority-20260814-v1/live-promotion.ready.json`.

All four are absent. That is the current fail-closed blocker, not missing
evidence.

## Reproduction

Run the read-only preparation from the repository root:

```powershell
$repoRoot = 'C:\Users\david\source\Onslaught-Career-Editor'
$liveProject = 'C:\Users\david\Ghidra\Projects'
$lane = Join-Path $repoRoot 'local-lab\ghidra-crt-eh-parent-range-live-promotion-db18616-20260814-v1'
$preBackup = 'D:\BEA-Ghidra-Backups\2026-08-14-crt-eh-parent-range-pre-live'
$postBackup = 'D:\BEA-Ghidra-Backups\2026-08-14-crt-eh-parent-range-post-live'

py -3 -I -B tools\ghidra_crt_eh_parent_range_live_authority.py preflight `
  --repo $repoRoot --evidence-repo $repoRoot --live-project $liveProject `
  --live-lane $lane --pre-backup $preBackup --post-backup $postBackup
```

Success is exactly the
`CRT_EH_PARENT_RANGE_LIVE_PREPARATION_READY ... db=db.18616.gbf
policy=PREPARATION_ONLY mutation_authorized=false
blocker=future_ceremony_artifacts_absent` sentinel.

The future ceremony must use one fresh headless process per dry/apply/readback
run, `-readOnly -noanalysis` for dry and readback, and exactly one writable
apply using `GhidraApplyCrtEhParentRange.java`. It must export the complete
function/program inventories before and after, create the inventory diff,
prove both off-volume restores read-only, capture tracked-still-PRE before any
tracked write, and pass `check-live`. Only then may the exact live project be
copied into tracked under the procedure in
[`reverse-engineering/ghidra/README.md`](../ghidra/README.md), followed by a
tracked restore proof, mechanical projection, read-only parity-graph export,
`seal`, and two `verify` replays.

## Claim boundary

This preparation changes no Ghidra file, campaign generation, function count,
grade, name, ABI, runtime claim, or rebuild behavior. It proves that the exact
25-byte structural correction is ready for an independently audited,
recoverable ceremony. Until that ceremony and its readback complete, canonical
ownership remains 1,811,418 bytes at 93.898814846%, not the prospective POST.
