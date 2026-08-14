# JPEG/IJG callback Ghidra live-promotion preparation

Status: **current db.18614 preparation reproduced; live promotion remains forbidden**

Date: 2026-08-14

Verdict: **PREPARATION_READY_LIVE_FORBIDDEN**

Policy: **`PREPARATION_ONLY`**

Evidence: MEASURED — exact current PRE plus two disposable prospective-POST
replicas. The authority hashes live and tracked Ghidra without opening either
project, reproduces the retained JPEG24 scratch authority, and validates two
fresh db.18614 replicas. No future live lane, backup, save, tracked refresh, or
aggregate authority exists.

Specimen: pristine PC retail `BEA.exe`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.

Preparation base: Git commit
`07417cadd227ab8d91bd2d1ab90554bd64fc3cf5`.

## Current PRE

Two read-only hashes prove the live maintainer project and tracked canonical
project are byte-identical after the five-body db.18614 promotion:

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
| Preceding database | `db.18613.gbf`, 68,337,664 bytes, `615497847b0c732077ee7164b0973b9012092523e9ad99b91c21781952420ebe` |
| Current database | `db.18614.gbf`, 68,337,664 bytes, `d7f0011ea337f58b710415d5664e73d91ca9f1f61e20a836278d3e71b71b2865` |
| Full function inventory | 7,161,943 bytes, `d2ff1e8e7bd91454fff9822fb7ecc8e624525fa5c6cbc9dcfe06f4e0212b750d` |
| Program metrics | 1,267 bytes, `b389487a65d6271329703c9e3ec9186b7261aa871a154c31179322780e1c132e` |
| Tracked projection | 508,239 bytes, `267210a78248f58da6bca1b4d11ee7b1812481602413e8bcac2fb4e4b4c4cb84` |
| PRE body accounting | 1,197,803 bytes, `495f1a86490e7b2646d2a0a6cd86bf6e4cdb071d5932b7d65ded1377621582e2` |

The retained scratch root is
`local-lab/ghidra-jpeg24-boundary-current-scratch-20260814-v1/`. Its
create-new receipt is 7,077 bytes / SHA-256
`573c550c7197e15cc098ff0dd09ce55467c7bae95ca2ec4efcf9e045e0954b63`;
the sealed tree excluding that receipt is 258 files / 1,013,137,450 bytes /
SHA-256
`7c3df3b029b3f175a41bbbf698c1b47dfd5f18c02f7616494794225f3dc2058c`.
It retains two saved positive replicas, exact PRE recovery after both adverse
controls, two path-containment refusals, and read-only backup recovery.

## Current-state disposable replicas

The new preparation root is
`local-lab/ghidra-jpeg24-boundary-live-prep-db18614-v2/`. It contains two
fresh copies of the exact current PRE and the frozen V2 mutator. Its exact
tree is 94 files / 410,373,323 bytes / SHA-256
`6a25263ce240c1311bc857b57937f37ad652a94859efb853c4d40e9bc8ef22f0`:

- `GhidraApplyJpegCallbackBoundariesV2.java`: 61,045 bytes / SHA-256
  `dcb2e8e92b6b877ae6c6e1f5839c298e48f0fd4a649a568d228b657af7c420dc`;
- [24-row manifest](jpeg-ijg-callback-function-boundaries-2026-08-14.tsv):
  15,295 bytes / SHA-256
  `6253c29d77e6676f2843ca8adf3d9c52b4b4fa86f088f6086ea00b90dde89fd6`;
- replica A and B dry/apply/separate-readback outputs are semantically
  byte-identical;
- all 8,280 PRE function rows remain field-identical;
- exactly 24 default-metadata functions and 38 pairwise-disjoint ranges are
  added; no existing row is destroyed or changed;
- both readbacks independently reproduce the exact listing-state correction,
  projection, body accounting, call graph, and program counters below.

The physical disposable copies each rotate `db.18613` to `db.18615` while
preserving exact `db.18614` and every other common file. Their new rolling
database bytes differ, as expected for separately saved Ghidra copies. The
authority therefore does not pin a guessed future `db.18615` identity; only a
future authorized live save and its backups may establish it.

## Exact prospective POST

| POST property | Exact value |
| --- | --- |
| Internal functions | 8,304 (+24) |
| Preserved PRE rows | 8,280 byte-identical |
| Body ranges | 8,434 (+38) |
| Owned `.text` bytes | 1,810,287 (+14,817) |
| Unowned `.text` bytes | 118,830 |
| `.text` ownership | 93.840186987% |
| Instructions | 551,055 (+41 net) |
| References | 234,467 (-11 net) |
| Full function inventory | 7,177,776 bytes / `bceedfa2eec573ee95e42a703d6f3a552c4718115fa540f3eaca492322f9a173` |
| Program metrics | 1,267 bytes / `bcb364f619559879e815f8d95f5551ba10d9be0467023bd006ee1246b0f9b40f` |
| Mechanical projection | 509,334 bytes / `5dd0d1145c2cf25004bd50208c624d9bf4f9c2fe0e4d307ac6c7ca88e8a5dfbc` |
| Exact body accounting | 1,202,661 bytes / `8e3640bfb280b6ce93a62db885183aa2239d1e74841685316b0117518eb63aaa` |
| Direct-call export | 1,396,670 bytes / `e2c3e2d0ace69d13b4bffa4d12690e60f6cf0cc50d2ff846cdc37ace680a756f` |
| Direct edges / call sites | 14,584 / 27,229 |

The `0x005B6800..0x005B6A86` body is one 646-byte function. At POST,
`0x005B6900` is neither data nor a function entry. It is the final byte of
`0F B6 00` / `MOVZX EAX,byte ptr [EAX]` beginning at `0x005B68FE` and is
owned only by `FUN_005b6800`. The seven DWORDs at `0x005B4EB0` and the four
NOP bytes at `0x005B4ECC` remain outside the cohort and unchanged.

No provider-qualified IJG name is promoted as an original linker symbol. No
signature, parameter, storage field, comment, tag, data definition, executable
byte, runtime contract, campaign grade, or rebuild behavior may change.

## Authority boundary

[`ghidra_jpeg_callback_boundary_live_authority.py`](../../tools/ghidra_jpeg_callback_boundary_live_authority.py)
never launches Ghidra and never writes the live or tracked project.

1. `preflight` reproduces the retained scratch tree, validates both current
   disposable replicas, proves live equals tracked at exact db.18614 PRE, and
   refuses if any future ceremony root already exists.
2. `check-live` can validate a separately authorized one-save live phase only
   while tracked remains exact PRE. It still prints
   `tracked_mutation_authorized=false`.
3. `seal` can validate a separately authorized tracked refresh, retained POST
   restores, mechanical projection, and body accounting. Its only write is
   create-new publication of one ignored aggregate receipt.
4. `verify` reproduces that receipt without writing.

The verified read-only preflight command is:

```powershell
py -3 -I -B tools\ghidra_jpeg_callback_boundary_live_authority.py preflight `
  --repo C:\Users\david\source\Onslaught-Career-Editor `
  --scratch-repo C:\Users\david\source\Onslaught-Career-Editor `
  --live-project C:\Users\david\Ghidra\Projects `
  --live-lane C:\Users\david\source\Onslaught-Career-Editor\local-lab\ghidra-jpeg24-boundary-live-promotion-20260814-v2 `
  --pre-backup D:\BEA-Ghidra-Backups\2026-08-14-jpeg24-db18614-pre-live-v2 `
  --post-backup D:\BEA-Ghidra-Backups\2026-08-14-jpeg24-db18614-post-live-v2
```

Only this sentinel is success:

```text
JPEG_CALLBACK_BOUNDARY_LIVE_PREPARATION_READY ...
live_equals_tracked=true db=db.18614.gbf
policy=PREPARATION_ONLY mutation_authorized=false
blocker=future_ceremony_artifacts_absent
```

## Remaining blocker

The current static and disposable-copy proof is complete, but action authority
is deliberately absent. A live ceremony still requires an exact off-volume PRE
backup and read-only restore, one separately authorized live apply/save,
separate readback, POST backup and restore, proof that tracked remained PRE,
then a separately authorized tracked refresh and retained restore. The physical
POST must remove only `db.18613.gbf`, preserve exact `db.18614.gbf`, add one
nonempty `db.18615.gbf`, and preserve every other common file. Until those
artifacts exist and the aggregate verifies, live and tracked mutation remain
forbidden.
