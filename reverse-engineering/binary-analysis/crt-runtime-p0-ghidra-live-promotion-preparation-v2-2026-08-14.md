# CRT/runtime P0 Ghidra live-promotion preparation v2

Status: **current db.18615 preparation; live promotion remains forbidden**

Date: 2026-08-14

Verdict: **PREPARATION_READY_LIVE_FORBIDDEN**

Policy: **`PREPARATION_ONLY`**

Evidence: MEASURED — the corrected sealed v2 scratch authority, exact current
live/tracked PRE, and two fresh disposable db.18616 prospective-POST replicas.
The preparation authority opens no Ghidra project and creates no live lane,
backup, tracked refresh, projection, or aggregate promotion receipt.

Specimen: pristine PC retail `BEA.exe`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.

Preparation base: Git commit
`c8678d80e4d0373d25e1452b8fcaf6af44761387`.

## Exact current PRE

Two independent read-only inventories prove the live maintainer project and
tracked canonical project are byte-identical after the
[JPEG/IJG callback promotion](jpeg-ijg-callback-ghidra-live-promotion-2026-08-14.md):

| PRE property | Exact value |
| --- | --- |
| Internal functions | 8,304 |
| Body ranges | 8,434 |
| Owned `.text` bytes | 1,810,287 |
| Unowned `.text` bytes | 118,830 |
| `.text` ownership | 93.840186987% |
| Instructions | 551,055 |
| References | 234,467 |
| Project files | 19 |
| Project bytes | 186,993,541 |
| Canonical project inventory | `3cd459d5461919934199e3346f6a92ce14946f42af400488ccde733173a40627` |
| Preceding database | `db.18614.gbf`, 68,337,664 bytes / `d7f0011ea337f58b710415d5664e73d91ca9f1f61e20a836278d3e71b71b2865` |
| Current database | `db.18615.gbf`, 68,354,048 bytes / `6c2fc2f12394cf7b63f4f335173ba0a19b52b92c50dc4d2da987170501bc9681` |
| Full function inventory | 7,177,776 bytes / `bceedfa2eec573ee95e42a703d6f3a552c4718115fa540f3eaca492322f9a173` |
| Program metrics | 1,267 bytes / `bcb364f619559879e815f8d95f5551ba10d9be0467023bd006ee1246b0f9b40f` |
| Tracked projection | 509,334 bytes / `5dd0d1145c2cf25004bd50208c624d9bf4f9c2fe0e4d307ac6c7ca88e8a5dfbc` |
| PRE body accounting | 1,202,661 bytes / `8e3640bfb280b6ce93a62db885183aa2239d1e74841685316b0117518eb63aaa` |

The underlying corrected scratch root remains
`local-lab/ghidra-crt23-p0-boundary-scratch-20260814-v2/`. Its create-new
receipt is 8,216 bytes / SHA-256
`e6b0dc6c99856836aeef2047eb7f1665064d21e5b5a49a166d03ebfbbbb25d23`;
the sealed tree excluding that receipt is 313 files / 1,574,566,435 bytes /
SHA-256
`e8cc6ab0c70f730719e8dea9a0c798a66a397c37b9911ff4ffa4620424cb36e4`.
That owner, rather than copied boundary-table fields, proves all 23 demo twins
and the exact corrected CRT22 run-c source cohort.

## Current-state disposable replicas

The new preparation root is
`local-lab/ghidra-crt23-p0-boundary-live-prep-db18615-v4/`: 102 files /
404,643,691 bytes / SHA-256
`d48aa7bf784a7a82f867adc259868eff16f60a4ae9d103ee44c8f57361ed41b0`.
It contains two fresh copies of the exact current PRE and frozen
[`GhidraApplyCrtP0BoundariesV4.java`](../../tools/GhidraApplyCrtP0BoundariesV4.java)
(57,278 bytes / SHA-256
`ac003bde10aea75cdf6849385017e15ef80c87e199ebeedf703108fb64334cc8`).
Relative to V3, V4 changes only its schema/class identity and the measured
db.18615 PRE/POST function, instruction, reference, and range counters.

Replica A and B independently reproduce all of the following:

- dry/apply/separate-readback boundary outputs and every semantic export are
  byte-identical between replicas;
- all 8,304 PRE function rows remain field-identical;
- exactly 23 function entries, 24 body ranges, 1,131 body bytes, and 312
  decoded body instructions are admitted;
- `0x00542720`, `0x005D0AD6`, and `0x005D0AEA` remain forbidden as function
  entries, and the separate P1 canary at `0x005B8500` remains absent;
- `0x0045AC20` remains a five-byte thunk to `0x0045AC30`; its inherited
  `CFEPGoodies__BuildStaticGoodieDataTable` identity is observed, not newly
  authored by this boundary campaign;
- no function is destroyed and no PRE body, name, signature, parameter,
  thunk flag, comment, repeatable comment, or tag changes; and
- the listing diagnostic, mechanical projection, body accounting, and
  direct-call graph reproduce exactly.

Each disposable save removes only `db.18614.gbf`, preserves exact
`db.18615.gbf` and every other common file, and adds one 68,354,048-byte
`db.18616.gbf`. The new databases have distinct exact hashes
`e309c00f67efb4f3ac93c72cad83e064efa9c7930b15c8b77bba268a407e2c36`
and
`6f806cce1543d0971d66b2ef3c9c2b5c3fe6de439556223b1a579b6ed7428eed`.
They differ at 53 physical bookkeeping bytes while yielding byte-identical
program inventories and exports. Both exact disposable identities are sealed;
neither is asserted as the identity of a future live save.

The superseded exploratory attempt and disposable project were recoverably
staged, not deleted, as quarantine IDs `163f4c59-exploratory` and
`11370559-exploratory-project`.

## Exact prospective POST

| POST property | Exact value |
| --- | --- |
| Internal functions | 8,327 (+23) |
| Preserved PRE rows | 8,304 field-identical |
| Body ranges | 8,458 (+24) |
| Owned `.text` bytes | 1,811,418 (+1,131) |
| Unowned `.text` bytes | 117,699 |
| `.text` ownership | 93.898814846% |
| Instructions | 551,133 (+78 net) |
| References | 234,478 (+11 net) |
| Full function inventory | 7,192,980 bytes / `8640c35a820b3c5e415b947fa8a13eeb5c7c535868780dc2fe511d020a54c40e` |
| Program metrics | 1,267 bytes / `185dbd4a9939edacf7302c00c7c48351ad23ad51be14bd5d431130d13848170a` |
| Mechanical projection | 510,353 bytes / `0b9f08cbd8849d22068d5ad6261a45b745bf80581744f4814a201b8fc4647804` |
| Exact body accounting | 1,205,737 bytes / `46138dc9b81ce2d0f835994f38581ba07564ddf17a7774ddbedfdb2e3d33e335` |
| Direct-call export | 1,397,680 bytes / `159f7c89aae54df927186d71263941b5f0857debe09556097820f098da8fa9d8` |
| Direct edges / call sites | 14,598 / 27,244 |

These are structural boundary results only. No provider-qualified CRT name is
promoted as an original linker symbol. No signature, ABI, source type,
comment, tag, data definition, executable byte, runtime behavior, semantic
grade, campaign generation, or rebuild contract may change.

## Read-only authority

[`ghidra_crt_p0_boundary_live_preparation_v2.py`](../../tools/ghidra_crt_p0_boundary_live_preparation_v2.py)
(34,889 bytes / SHA-256
`ad59a84a59705a54be1e6a72313978b1b6822460b1b6855e502c740d351002e6`)
is deliberately narrower than a live authority. Its focused test owner is
11,624 bytes / SHA-256
`3bba1eb9963dbc8a7c308a0e488d0adf27f7e828d1528ea206120243c469cc9a`.
The authority:

1. replays the corrected v2 scratch authority and rehashes its entire sealed
   tree;
2. validates every pinned repository input and the complete current preparation
   tree;
3. independently totals the PRE and POST body-range exports, checks all PRE
   function rows, and compares deterministic replica outputs byte-for-byte;
4. rehashes both physical disposable projects, binds their exact 53-byte
   database difference, and rejects common-file drift;
5. rehashes live and tracked Ghidra and requires exact db.18615 equality; and
6. refuses if a future live lane, PRE backup, POST backup, or aggregate
   authority root already exists.

The verified command is:

```powershell
py -3 -I -B tools\ghidra_crt_p0_boundary_live_preparation_v2.py preflight `
  --repo C:\Users\david\source\Onslaught-Career-Editor `
  --scratch-repo C:\Users\david\source\Onslaught-Career-Editor `
  --live-project C:\Users\david\Ghidra\Projects `
  --live-lane C:\Users\david\source\Onslaught-Career-Editor\local-lab\ghidra-crt23-p0-boundary-live-promotion-db18615-20260814-v2 `
  --pre-backup D:\BEA-Ghidra-Backups\2026-08-14-crt23-db18615-pre-live-v2 `
  --post-backup D:\BEA-Ghidra-Backups\2026-08-14-crt23-db18615-post-live-v2
```

Only this sentinel is success:

```text
CRT_P0_BOUNDARY_LIVE_PREPARATION_V2_READY ...
live_equals_tracked=true db=db.18615.gbf
policy=PREPARATION_ONLY mutation_authorized=false
blocker=future_ceremony_artifacts_absent
```

## Remaining blocker

Static and disposable-copy proof is complete, but action authority is absent.
A future ceremony still requires an exact off-volume PRE backup and read-only
restore, one separately authorized live apply/save, separate readback, POST
backup and restore, proof that tracked remained PRE, then a separately
authorized tracked refresh and retained restore. Until those artifacts exist
and a new live authority reproduces them, live and tracked mutation remain
forbidden.
