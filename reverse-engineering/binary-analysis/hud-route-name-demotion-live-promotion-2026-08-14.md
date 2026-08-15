# HUD route descriptive-name demotion live promotion

Status: live promoted, separately read back, recoverably backed up, and
refreshed into the tracked Ghidra snapshot
Last updated: 2026-08-14
Evidence: MEASURED — the refuting callee evidence in
`local-lab/pc-hud-static-join-20260812-v1/NOTE.md`, an exact read-only PRE
inspection of the four targets, an immutable two-replica plus two-adverse-probe
scratch authority, live dry/apply/readback receipts, full PRE/POST function
inventories with a machine diff, raw project-tree hashes, retained restore
probes, and a deterministic name projection; UNKNOWN — original source spelling,
runtime causality, on-screen rendering roles, and reconstruction parity.
Verdict: four HUD route renderer rows in live and tracked Ghidra carry neutral
Tier-3 placeholder names (`CHud__RoutePanel_T*_<address>`) with measured-fact
comments and corrected tag sets, replacing four descriptive names their bodies
contradict. Exactly one writable live Ghidra process changed these four rows'
names, displayed signatures, comments, and tags. No program byte, instruction,
boundary, ABI/storage field, data unit, reference, or non-target function row
moved. Function count remains 8,329.
Specimen: pristine PC retail `BEA.exe`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.

## Demoted rows and evidence boundary

| Address | Route | Former name | Verdict | POST name |
| --- | --- | --- | --- | --- |
| `0x00483530` | T0 | `CHud__RenderControllerSlotStatusPanel` | refuted (no controller callee anywhere; 20× mission script variable reads, clock formats, meter bars) | `CHud__RoutePanel_T0_00483530` |
| `0x004858d0` | T3 | `CHud__RenderObjectiveProgressGaugeAndHeadingNeedle` | half refuted (gauge reads `GetWeaponCharge`; heading half supported) | `CHud__RoutePanel_T3_004858d0` |
| `0x00485d50` | T4 | `CHud__RenderObjectiveStatusPanel` | suspect (unit counting `x%d`, not decisively objective-contradicted) | `CHud__RoutePanel_T4_00485d50` |
| `0x00486940` | T5 | `CHud__RenderObjectiveSlotFillPanel` | refuted (only `IsEnergyWeapon` + `GetWeaponAmmoPercentage`) | `CHud__RoutePanel_T5_00486940` |

This demotion executes the naming-convention decision recorded in
[`function-naming-convention-2026-08-12.md`](function-naming-convention-2026-08-12.md):
the binary ships no name for these bodies, so the prior descriptive labels were
Tier 3 working labels, and known-false labels are worse than neutral ones. The
replacement names assert nothing semantic; each comment carries the measured
facts, the refutation verdict, and the evidence pointer. Replacement descriptive
naming awaits a body-reading or draw-route measurement; this change does not
provide one. It changes no campaign generation, runtime-causality grade,
reconstruction contract, or `REBUILD_READY` state, and it does not join any
structural boundary cohort.

## Scratch authority and ceremony base

The immutable scratch owner is
`local-lab/ghidra-hud-route-demotion-20260814-v1/scratch-authority.ready.json`
(8,685 bytes, SHA-256
`1c56847b07b8bcac4526e34881eaf6838508e6b7525aa646fb54804b08c36a0f`).
It binds two positive replicas (dry/apply/readback each, apply and readback
tables byte-identical across replicas), two adverse rollback probes
(after-one and post-inner with compensating PRE restore, zero published success
artifacts, exact PRE state proven by separate readbacks), the PRE full
inventory, and the replica POST full inventory with a machine diff proving
exactly four name and four displayed-signature changes and zero collateral.

## Live ceremony

The live lane is `local-lab/ghidra-hud-route-demotion-20260814-v1/`. Its Ghidra
logs contain exactly one writable process: `live-apply` (db.18618 → db.18619).
The phases completed in the required order after the fresh PRE backup and
before the POST backup.

| Phase artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| Dry target TSV | 2,174 | `03402c7226b6e80ac59ad4ebe749da6f93a74b938194ed544b49abd24866041b` |
| Apply target TSV | 2,192 | `1509ac4da75db4b48fae252ca8877e0516b89f51e41992cd8e439e061e988e8b` |
| Readback target TSV | 2,204 | `f9f99b1d05941b40907a98cd3e6cafe81317c6fe5aa9d41cce835d8d76cb6cd5` |
| Readback functions | 7,194,265 | `03f70745727f420bf726c26cb065e9fc1e5fdd1334d645704fdffc05f2d7d568` |
| Readback program | 1,267 | `229bebebdf7eccac77c5b1c7e5248e3d6d2fd4bb299655863064393262ac72fe` |

The live apply and readback tables are byte-identical to scratch replica A, and
the live POST full inventory equals the replica POST inventory. The inventory
diff over all 8,329 rows shows 8,325 non-target rows byte-identical and exactly
four `name` + `signature` changes. At program scope only `commentsSha256`
changed; functions (8,329), instructions (551,143), memory, data, symbols,
references, and comment count remained exact.

## Recovery and raw project equality

The verified PRE recovery is
`D:\BEA-Ghidra-Backups\2026-08-14-hud-route-demotion-pre-live` (manifest
SHA-256 `3dd08bbaf8170461be4ad903313918ed96b189a7f75b2e7d16080f0ebdb1a9dd`;
restore receipt
`db8c6c32bc67f254ac14d7ad466edcc65c3c51d1d8f6a76e7e75457bb35d04ee`). The
verified POST recovery is
`D:\BEA-Ghidra-Backups\2026-08-14-hud-route-demotion-post-live` (manifest
SHA-256 `f26c52b6085b79c2b911d43456ab55c03ab928c545e848a66a25b307269cf2a7`;
restore receipt
`637ab107e98bd36e25eb9dc228430ea4983a2083aad709582a4088e8cb7fa8a7`). Both were
reopened read-only in retained independent probes before and after mutation.
The tracked snapshot was proven still-PRE before refresh, then refreshed and
restore-probed (receipt SHA-256
`72d427018989894fbfca07136c919751481f17c9aecc704f0c690655e918b3a8`). At
verification time the live maintainer project, tracked snapshot, and POST
backup are byte-identical 19-file / 187,009,925-byte trees; the only file-set
change is the checkpoint swap `db.18617.gbf` → `db.18619.gbf` (new rolling
database 68,354,048 bytes, SHA-256
`dd809b9545a902639c54df39037021649af436ed1ec602c6134d07afa2193ca0`; db.18618
retained as the stable prior). The canonical project inventory
(sha256<TAB>bytes<TAB>relative-posix-path<LF>, sorted by rendered line) is
`f43e3d4f9287eca3e09925195f3d71519369e4727d959c58afe821df489c9f3f`.

## Current name projection

The refreshed projection is
`local-lab/ghidra-hud-route-demotion-20260814-v1/ghidra-function-name-table-2026-08-14.tsv`
(8,329 rows, 510,421 bytes, SHA-256
`93ef81dbad09d656a6918687ecb3d682cf995da7df010ed5db211ddedc0c5a89`),
mechanically derived from the live readback; it contains all four
`CHud__RoutePanel_*` rows and none of the four demoted names.

## Aggregate authority and repeatable verification

The read-only verifier is
[`tools/ghidra_hud_route_demotion_live_authority.py`](../../tools/ghidra_hud_route_demotion_live_authority.py)
(14,937 bytes, SHA-256
`7ec73df4fea632fc2b5ac19555d085374bcea3f826a6506dd781a150dcb8cb25`). It never
launches Ghidra. Reproduce the receipt with:

```powershell
python tools/ghidra_hud_route_demotion_live_authority.py verify `
  --output local-lab/ghidra-hud-route-demotion-live-authority-20260814-v1/live-promotion.ready.json
```

The integrated read-only aggregate authority is
`local-lab/ghidra-hud-route-demotion-live-authority-20260814-v1/live-promotion.ready.json`
(4,738 bytes, SHA-256
`42c8383f807bc2d645fe592dc88fd0f4c4b2386653a390ff973986189703b17b`); `seal`
was used once and refuses overwrite. The mutator and inspector are
[`tools/GhidraApplyHudRouteDemotion.java`](../../tools/GhidraApplyHudRouteDemotion.java)
and
[`tools/GhidraInspectHudRouteDemotion.java`](../../tools/GhidraInspectHudRouteDemotion.java).
The ignored raw logs, restore probes, and aggregate receipt remain workstation
evidence; this report carries only their bounded measured conclusions.
