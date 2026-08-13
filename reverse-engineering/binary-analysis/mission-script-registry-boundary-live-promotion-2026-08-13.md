# Mission-script registry boundary live promotion

Status: promoted, separately read back, backed up, and synchronized
Last updated: 2026-08-13
Verdict: Ghidra now contains the 34 callable MissionScript handler boundaries
proved by the registry campaign, raising the saved internal-function census
from 8,136 to 8,170 without changing any instruction, data, reference, comment,
signature, or pre-existing function row.
Evidence: MEASURED — immutable manifest and specimen bytes, two persistent
scratch replicas, two forced-failure rollback controls, one live apply,
separate-process full-inventory readback, and independently opened PRE/POST
backups and tracked snapshot; UNKNOWN — original C++ names, signatures,
arguments, returns, side effects, runtime behaviour, and demo/Xbox parity.
Specimen: pristine PC retail `BEA.exe`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

## Result

The campaign owner and exact 34-row half-open range manifest are
[`mission-script-registry-missing-function-boundaries-2026-08-13.md`](mission-script-registry-missing-function-boundaries-2026-08-13.md)
and its sibling TSV. The live ceremony admitted those boundaries only. Each
new function retains a Ghidra default `FUN_*` name and default metadata.
The candidate owner's pre-promotion status text is intentionally frozen because
the live receipt pins that file's exact bytes; this report supersedes it for
current-state status.

| Measurement | PRE | POST |
| --- | ---: | ---: |
| Internal functions | 8,136 | 8,170 |
| Aggregate functions including 224 imports/externals | 8,360 | 8,394 |
| Instructions | 549,872 | 549,872 |
| Defined-data items | 48,585 | 48,585 |
| Undefined-data items | 3,912,345 | 3,912,345 |
| User-defined symbols | 6,016 | 6,016 |

The separate live readback is 8,170 rows / 7,082,637 bytes / SHA-256
`8aa8b4468f463053d25084de86bec2a701ed1064c13f77fd47d16f9dda6cf259`.
It is byte-identical to both independently mutated scratch replicas. Its
program inventory is 1,267 bytes / SHA-256
`cb4c2194e30e074e443779d9b42587072568f104fc76f671d40757af7b106075`;
only the `functions` metric changed.

## Mutation and recovery evidence

The final scratch authority is 17,489 bytes / SHA-256
`04f1c9ea5a434010e003f24a0e9da0c56323aa5453b0bb0062996911db0b2c91`.
It authorized one live mutation process. The final live receipt is 9,956 bytes
/ SHA-256
`363a57afda96560b214c01e3a75422702ae6ac2cdeb89ed2d069231414722322`
under
`local-lab/ghidra-mission-registry-boundary-live-promotion-20260813-v1/`.
Re-running its verifier reproduces that receipt exactly.

- PRE backup: `D:\BEA-Ghidra-Backups\2026-08-13-mission-registry-boundaries-pre-live`.
- POST backup: `D:\BEA-Ghidra-Backups\2026-08-13-mission-registry-boundaries-post-live`,
  19 files / 186,551,173 bytes. Its restore/open receipt is 5,940 bytes /
  SHA-256 `736bcbc2c0824240865010a3c70338288ca3e2018eee94e0d3b389fd727ba87b`.
- The live project, POST backup, and tracked `reverse-engineering/ghidra/`
  project files are byte-identical. The tracked restore/open receipt is 5,961
  bytes / SHA-256
  `d79325e4d092d8abdb92f0a62d7635d80ad30034b86aa14d247aa3ac815ca8fc`.
- Ghidra rotated one database filename while saving. The retired PRE
  `db.18606.gbf` was recoverably staged as quarantine item
  `c52c035d-db.18606.gbf`; the exact POST project uses `db.18608.gbf`.

The current tracked name projection is
[`ghidra-function-name-table-2026-08-13.tsv`](ghidra-function-name-table-2026-08-13.tsv),
8,170 rows / 502,664 bytes / SHA-256
`19312b424e357ea8a95102927d6464c874c491bdfcb28de82b1175e352fbb5bf`.
The 2026-08-12 table remains frozen because Generations 20–23 and two sealed
instruments pin its exact bytes.

## Layer boundary

This promotion changes the structural census only. The dated static-closure
table still grades its original 8,136 rows (8,129 C1 and seven C2); the 34 new
functions are outside that closure and are not silently promoted to C1. The
canonical Generation 23 campaign remains its immutable 8,126-row authority.
The 34 new functions also remain unmapped to the PC demo. Consequently neither
the dated zero-static-OPAQUE claim nor the former demo-map closure can be
projected over the current 8,170-function census.

The separate 75-row script-command name normalization and the independent
`0x0050FF10` explosion-factory correction remain future metadata ceremonies.
This boundary promotion authorizes neither.
