# MissionScript new-function vocabulary live promotion

Status: live promoted, separately read back, recoverably backed up, and
refreshed into the tracked Ghidra snapshot
Last updated: 2026-08-13
Evidence: MEASURED — the reviewed 34-row manifest and static contracts, two
scratch replicas and adverse controls, one live dry/apply/readback sequence,
full function/program inventories, six raw project-tree inspections, and
independently reopened PRE, POST, and tracked copies; UNKNOWN — original C++
symbols, runtime reachability and causality, complete semantics, source
equivalence, and reconstruction parity.
Verdict: exactly 34 previously default-named MissionScript handler functions
now carry Tier-2 `IScript__<shipped command>` names, bounded row-specific C1
static comments, and the two existing registry-vocabulary tags. The operation
changed no function boundary, body, instruction, ABI/storage field, parameter,
repeatable comment, program byte, data unit, reference, or non-target row.
Specimen: pristine PC retail `BEA.exe`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.

## Claim boundary

The immutable preparation owner is
[`mission-script-registry-new-function-vocabulary-normalization-2026-08-13.md`](mission-script-registry-new-function-vocabulary-normalization-2026-08-13.md)
and its 34-row manifest. Each saved name records only the shipped registry
vocabulary for that exact handler entry. It is not asserted as an original C++
symbol, ABI recovery, complete ordinary-language behavior, or runtime proof.
Twelve registry labels agree with the visible bounded mechanism and 22 are
broader than it; every saved comment retains that row-specific distinction,
unknowns, and cheapest falsifier.

The cohort is disjoint from the earlier 75 existing-entry vocabulary
normalizations, the structural creation of these 34 boundaries, indices 114/115
whose Tier-1 error strings win over registry labels, the shared SetSpeed no-op,
and the separate `0x0050FF10` explosion-factory repair.

## Scratch and live gates

The scratch authority at
`local-lab/ghidra-mission-registry-new34-vocabulary-20260813-v1/scratch-authority.ready.json`
is 31,501 bytes, SHA-256
`8a6aedbe69f6eb9f5d222830b54bd231c5719378261d02c06986c13b89f1e118`.
It binds two positive replicas, rollback and post-inner compensation controls,
two external-path preflight controls, exact PRE readbacks, and a restore-opened
POST backup. It authorized integration review, not a live mutation.

The live lane is
`local-lab/ghidra-mission-registry-new34-live-promotion-20260813-v1/`.
After a fresh PRE inspection and restore-opened off-volume backup, exactly
three Ghidra processes ran in this order:

1. read-only dry at `2026-08-13T22:36:25.545708600Z`;
2. the sole writable apply at `2026-08-13T22:37:20.812321300Z`; and
3. separate read-only readback at `2026-08-13T22:37:39.155546700Z`.

Dry retained all 34 exact PRE rows and a raw inspection proved the project
unchanged. Apply saved once. Readback reopened the project, verified every POST
row, and exported the full inventories.

| Live artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| dry target TSV | 13,389 | `3695eadee1f7542935391b2ed7b06da69200697667ba57febb275527d5ac2885` |
| dry receipt | 2,492 | `f76a75c852abea7cea16bcbb02b52f21f4494b15358487a44536db92ea436b29` |
| apply target TSV | 15,702 | `35d73c89c5d29dd4f3daf8c308ee5e8a31eebc623abaaa5955ddc017950f6c52` |
| apply receipt | 2,496 | `ab7799f4aa290528a2b8c5f094ecbe59cd10f6b8c180ffbb36630459679f136e` |
| readback target TSV | 15,804 | `d40eb04c09459652d634c341d3bb3bfe04effdc14e7d75d83344713e041180d7` |
| readback receipt | 2,502 | `d08990d8016b9f781f1a8e7ca4ac7886ccffb00cc82d4f41dea7e484921e9680` |
| readback full functions | 7,089,535 | `ee3090360bd4f4b68d1ac52c59ab397e7ac37d81c76029d492e2a9d046902f1d` |
| readback program | 1,267 | `2360923e0fa95648a708ee44297006dee222036662d7b34108d10a1fa405dc02` |

## Exact collateral

The PRE and POST inventories contain the same 8,170 function addresses. Exactly
34 rows differ. Each differs only in primary/fq name and hashes, name source,
name-derived rendered signature text and hashes, function comment and hashes,
and tag associations. All 8,136 non-target rows are byte-identical.

At program scope the only changes are:

- user-defined symbols `6,070 -> 6,104`;
- default/other symbols `61,628 -> 61,594`;
- program-wide listing comment records `9,165 -> 9,199`;
- the observed `+34` consists exactly of the 34 new target function comments;
  and
- the corresponding comment digest.

Functions remain 8,170 and instructions remain 549,872. Memory, data,
references, relocations, blocks, and all other program-inventory fields are
unchanged. The name projection now contains 8,170 rows, 878 literal `FUN_*`
names, 7,050 commented functions, and 6,012 tagged functions. The 8,170-row
census is a measured lower bound, not a final ceiling.

## Aggregate read-only verification

The reusable verifier is `tools/ghidra_live_promotion_authority.py`; its cohort
configuration is
`reverse-engineering/binary-analysis/mission-script-registry-new-function-vocabulary-live-authority-2026-08-13.json`.
The ignored aggregate receipt is
`local-lab/ghidra-mission-registry-new34-live-authority-20260813-v1/authority.ready.json`
at 18,373 bytes, SHA-256
`db946cefffbda039a9e368ad6dfec6ec90b69aa4d5222fdf6ec3ab1017be951a`,
with schema `bea.ghidra.live-promotion-authority.v1` and verdict
`LIVE_PROMOTION_AUTHORITY_READY`.

The verifier pins and inventories all 26 retained non-project live artifacts,
recomputes the exact PRE-to-POST function and program deltas, compares every
retained probe project with its state owner, proves live/tracked/POST tree
equality and PRE/POST rolling-database scope, replays chronology through the
full readback export, and regenerates the current name projection. It launches
no Ghidra process and writes only the explicit ignored receipt in `seal` mode.
Tracked and tool identities are recorded by repository-relative role, so the
saved receipt also verifies after moving the same tracked bytes to the shared
checkout root. The historical scratch and live receipts remain unmodified.

Final verifier SHA-256:
`db290f95731704b8ac330846ff98ee2b022064e47cad7826058384e1782efcdd`.
Final manifest SHA-256:
`e627277a455a2a89160c057b4bb6c4a03658925de78c2c5a41fb737814467a22`.

## Recovery and synchronized project state

The PRE backup is
`D:\BEA-Ghidra-Backups\2026-08-13-mission-registry-new34-pre-live`.
Its 19 project files total 186,747,781 bytes and reproduce canonical inventory
SHA-256
`8eb664062a8ba67005e9f8ad8f61aa2222585622c41022a69080c5e408cd3cf6`.
Its restore/open receipt is 5,909 bytes, SHA-256
`efd08ad068e32f454dde7e7e9b02005db1608d0f9cc47a37658d1e44d8f63920`.

The POST backup is
`D:\BEA-Ghidra-Backups\2026-08-13-mission-registry-new34-post-live`.
Live, tracked, and POST backup each contain exactly 19 project files / 186,813,317
bytes at canonical inventory SHA-256
`cf3b36f5a8d9183bdc0b66041445fb5451160fb21edaed9fb21bed74a9f6ee0d`.
The new `db.18611.gbf` is 68,288,512 bytes, SHA-256
`6f45cdac7ae1f10987280f0ec247e6b5d6dcf866eae79e5982efa78dd68455ce`.

The POST backup restore/open receipt is 5,913 bytes, SHA-256
`878cbbe532f1fea830fde9e8de9fa791e4b0f7181060841181dc8920793cd620`.
The refreshed tracked snapshot was independently copied and reopened read-only;
that receipt is 5,935 bytes, SHA-256
`daa5458c5853239828a54ba3f9f8b744d48f1b5102a2b9105e0c4552ef362582`.

The current tracked projection is 503,177 bytes, SHA-256
`d61f9866d9dbf67bae817a710d50a1a136b7c2156ec6eb7f862d82dea70f26fd`.
It is byte-identical to the projection generated from the separate live
readback. The dated 2026-08-12 and earlier tables remain frozen artifacts and
were not repinned.

This promotion changes no Generation-23 campaign row and does not make any
contract `REBUILD_READY`. Generation 24 remains a separate reducer/campaign
decision.
