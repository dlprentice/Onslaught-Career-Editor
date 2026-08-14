# CRT/runtime P0 Ghidra live-promotion preparation

Status: **historical db.18614 preparation; re-grounding required before promotion**

Date: 2026-08-14

Verdict: **PREPARATION_READY_LIVE_FORBIDDEN**

Policy: **`PREPARATION_ONLY`**

Evidence: MEASURED — the corrected sealed v2 scratch authority, exact
preparation-time live/tracked PRE, and two fresh disposable db.18614
prospective-POST replicas.
The preparation authority opens no Ghidra project and creates no live lane,
backup, tracked refresh, projection, or aggregate promotion receipt.

Specimen: pristine PC retail `BEA.exe`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.

Preparation base: Git commit
`4d7ba6f938ea54ed1312e0f61ba208b0d285b84e`.

## Preparation-time PRE

Read-only inventories proved the live maintainer project and tracked canonical
project were byte-identical after the five-body db.18614 promotion. The later
[JPEG/IJG callback promotion](jpeg-ijg-callback-ghidra-live-promotion-2026-08-14.md)
advanced both to 8,304 functions on db.18615, so this preparation must not be
used for a current live write without a fresh geometry re-ground:

| PRE property | Exact value |
| --- | --- |
| Internal functions | 8,280 |
| Body ranges | 8,396 |
| Owned `.text` bytes | 1,795,470 |
| Instructions | 551,014 |
| References | 234,478 |
| Project files | 19 |
| Project bytes | 186,977,157 |
| Canonical project inventory | `cda0938c1a266fbe1751a8b0bf175b90c63b296f21fc9631b5bade1ecf93e541` |
| Preceding database | `db.18613.gbf`, 68,337,664 bytes / `615497847b0c732077ee7164b0973b9012092523e9ad99b91c21781952420ebe` |
| Current database | `db.18614.gbf`, 68,337,664 bytes / `d7f0011ea337f58b710415d5664e73d91ca9f1f61e20a836278d3e71b71b2865` |
| Full function inventory | 7,161,943 bytes / `d2ff1e8e7bd91454fff9822fb7ecc8e624525fa5c6cbc9dcfe06f4e0212b750d` |
| Program metrics | 1,267 bytes / `b389487a65d6271329703c9e3ec9186b7261aa871a154c31179322780e1c132e` |
| Tracked projection | 508,239 bytes / `267210a78248f58da6bca1b4d11ee7b1812481602413e8bcac2fb4e4b4c4cb84` |
| PRE body accounting | 1,197,803 bytes / `495f1a86490e7b2646d2a0a6cd86bf6e4cdb071d5932b7d65ded1377621582e2` |

The corrected scratch root is
`local-lab/ghidra-crt23-p0-boundary-scratch-20260814-v2/`. Its create-new
receipt is 8,216 bytes / SHA-256
`e6b0dc6c99856836aeef2047eb7f1665064d21e5b5a49a166d03ebfbbbb25d23`;
the sealed tree excluding that receipt is 313 files / 1,574,566,435 bytes /
SHA-256
`e8cc6ab0c70f730719e8dea9a0c798a66a397c37b9911ff4ffa4620424cb36e4`.
It preserves the superseded v1 receipt, reruns two positive replicas, two
rollback controls, two containment refusals, and read-only recovery, while
validating demo identities only through their actual corrected run-c owner.

## Current-state disposable replicas

The new preparation root is
`local-lab/ghidra-crt23-p0-boundary-live-prep-db18614-v3/`. Its exact tree is
91 files / 411,654,188 bytes / SHA-256
`668406c2b262c072837e985fec97c4de53f6ffeba0d5d208e98a83f23a50a966`.
It contains two fresh copies of the exact current PRE and the frozen
[`GhidraApplyCrtP0BoundariesV3.java`](../../tools/GhidraApplyCrtP0BoundariesV3.java)
(57,278 bytes / SHA-256
`e92b445e34d183ae0102fe3bfa8c608cf324dad11f4ff7aedd3b04381bbc5211`).
Relative to corrected V2, V3 changes only its schema/class identity and the
measured db.18614 PRE/POST instruction, reference, and range counters.

Replica A and B independently reproduce all of the following:

- dry/apply/separate-readback boundary outputs are byte-identical between
  replicas;
- all 8,280 PRE function rows remain field-identical;
- exactly 23 function entries, 24 body ranges, 1,131 body bytes, and 312
  decoded body instructions are admitted;
- `0x00542720`, `0x005D0AD6`, and `0x005D0AEA` remain forbidden as function
  entries, and the separate P1 canary at `0x005B8500` remains absent;
- `0x0045AC20` remains a five-byte thunk to `0x0045AC30`; its inherited
  `CFEPGoodies__BuildStaticGoodieDataTable` identity is observed, not newly
  authored by this boundary campaign;
- no function is destroyed and no PRE body, name, signature, parameter,
  thunk flag, comment, repeatable comment, or tag changes;
- the listing diagnostic, function projection, body accounting, and direct-call
  graph reproduce exactly.

Each disposable save removes only `db.18613.gbf`, preserves exact
`db.18614.gbf` and every other common file, and adds one nonempty
`db.18615.gbf`. The separately saved `db.18615` bytes are intentionally not
pinned as a future live identity.

## Exact prospective POST

| POST property | Exact value |
| --- | --- |
| Internal functions | 8,303 (+23) |
| Preserved PRE rows | 8,280 field-identical |
| Body ranges | 8,420 (+24) |
| Owned `.text` bytes | 1,796,601 (+1,131) |
| Unowned `.text` bytes | 132,516 |
| `.text` ownership | 93.130743236% |
| Instructions | 551,092 (+78 net) |
| References | 234,489 (+11 net) |
| Full function inventory | 7,177,147 bytes / `a05b55051aad3dc5ab0ea76a1afa79c7bc00ffae2e66749bdac96d3a6c46aac5` |
| Program metrics | 1,267 bytes / `3749f822330ece0e56c9120274b76d10faea5fe10d3c130dd9f1d97e86e9c41d` |
| Mechanical projection | 509,317 bytes / `a9725f263a11c13c7bad2ca944f06d6f7d91a5622a22febaa8c711aa5e08a713` |
| Exact body accounting | 1,200,879 bytes / `2cefa1f3d3efaaccdec5e0624c1d7bbd81d2b03747822c738f070c913ae1c3f9` |
| Direct-call export | 1,396,248 bytes / `d44397b910123ddabb4c598bf3be3b33b22af9df78645e258a6049f7e7878b6f` |
| Direct edges / call sites | 14,582 / 27,211 |

These are structural boundary results only. No provider-qualified CRT name is
promoted as an original linker symbol. No signature, ABI, source type,
comment, tag, data definition, executable byte, runtime behavior, semantic
grade, campaign generation, or rebuild contract may change.

## Read-only authority

[`ghidra_crt_p0_boundary_live_preparation.py`](../../tools/ghidra_crt_p0_boundary_live_preparation.py)
(32,440 bytes / SHA-256
`67d4d746ef836f1e4b97821a2adbaebebb4a99a0b7068cf356ce58d699efe5f2`)
is deliberately narrower than a live authority. It:

1. replays the corrected v2 scratch authority and rehashes its entire sealed
   tree;
2. validates every pinned repository input and the complete current preparation
   tree;
3. independently totals the PRE and POST body-range exports, checks all PRE
   function rows, and compares deterministic replica outputs byte-for-byte;
4. rehashes live and tracked Ghidra and requires exact db.18614 equality; and
5. refuses if a future live lane, PRE backup, POST backup, or aggregate
   authority root already exists.

The verified command is:

```powershell
py -3 -I -B tools\ghidra_crt_p0_boundary_live_preparation.py preflight `
  --repo C:\Users\david\source\Onslaught-Career-Editor `
  --scratch-repo C:\Users\david\source\Onslaught-Career-Editor `
  --live-project C:\Users\david\Ghidra\Projects `
  --live-lane C:\Users\david\source\Onslaught-Career-Editor\local-lab\ghidra-crt23-p0-boundary-live-promotion-20260814-v1 `
  --pre-backup D:\BEA-Ghidra-Backups\2026-08-14-crt23-db18614-pre-live-v1 `
  --post-backup D:\BEA-Ghidra-Backups\2026-08-14-crt23-db18614-post-live-v1
```

Only this sentinel is success:

```text
CRT_P0_BOUNDARY_LIVE_PREPARATION_READY ...
live_equals_tracked=true db=db.18614.gbf
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
