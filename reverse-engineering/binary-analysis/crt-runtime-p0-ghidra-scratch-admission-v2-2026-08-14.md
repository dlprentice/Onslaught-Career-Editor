# CRT/runtime P0 Ghidra scratch admission v2

Status: active — hostile-audit correction sealed in scratch; live and tracked mutation forbidden
Last updated: 2026-08-14
Summary: replaces the inadmissible v1 receipt shape, not its structural result;
reruns the exact 23-boundary CRT22 run-c cohort through two fresh db.18613
replicas and validates every field retained by the corrected v2 receipts.

Verdict: **SCRATCH_READY_LIVE_FORBIDDEN**

Evidence: **MEASURED** — corrected run-c plus two byte-identical fresh
reproofs, exact retail/demo body comparisons, two persistent disposable Ghidra
replicas, full PRE/POST inventories, two rollback readbacks, two containment
controls, and a read-only backup/restore/open proof.

Specimen: pristine PC retail `BEA.exe`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`;
PC demo `BEA.exe`, SHA-256
`d8637dd755b21c720c0cb8f71923f94d2a04a184d90f5343c2e868ce8606e5c2`.

## Audit correction

V1 copied JPEG-oriented columns into its boundary TSV: provider identity,
identity grade, source location, CFG counts/hashes, normalized hashes, demo
entry/delta/raw equality, terminal kinds, and peer transfers. Several were
empty or placeholder values supplied by the mutator rather than measurements.
That made the receipt inadmissible even though its boundary result was sound.

The v2 schema `bea.ghidra.crt-p0-boundaries.v2` removes all twelve borrowed
fields. It retains only values the mutator reads from the exact manifest,
measures from Ghidra, or validates before publication: candidate/cohort/entry,
status, displayed default name/source, expected and actual body envelopes,
bytes and hashes, external and Ghidra instruction counts, expected and actual
thunk state/target, forbidden entries, residual key, contract, and promotion
lane. The v2 authority checks every retained TSV column and every READY field;
its hostile unit test changes each TSV column independently and requires every
change to fail.

Demo claims stay with corrected CRT22 run-c, their actual owner. Two exact fresh
run-c reproofs remain byte-identical to the canonical output. Against the exact
retail and demo specimens, the authority independently verifies all 23 selected
retail/demo entries and derived deltas, equal body lengths, all 23 normalized-
plus-CFG equal results, and six raw-equal bodies. The canonical selected-row
entry/delta projection is 4,672 bytes, SHA-256
`abcdeea9ed0d8db95075bc0d7e6bd0869f0331a70c42958ef909f98e4265907a`.

## Fresh result

The source remains pristine PC retail `BEA.exe`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
PRE is the exact 19-file / 186,960,773-byte db.18613 project, inventory
SHA-256 `ae422079966978ec2f8f5b951b0ef5812b1074bd708ab8d782179f51c90efcf2`;
`db.18613.gbf` is 68,337,664 bytes, SHA-256
`615497847b0c732077ee7164b0973b9012092523e9ad99b91c21781952420ebe`.

Two fresh project copies independently pass dry/apply/save/close/separate
readback:

- 23 entries, 24 pairwise-disjoint ranges, 1,131 pristine bytes, and 312 body
  instructions;
- 8,280 → 8,303 functions and 8,400 → 8,424 function ranges;
- all 8,280 PRE rows field-identical and exactly the 23 manifest rows added;
- 550,991 → 551,069 instructions and 234,495 → 234,506 references, with every
  delta proved body-contained before commit;
- `0x00542720`, `0x005D0AD6`, and `0x005D0AEA` remain forbidden entries;
  `0x005B8500` remains excluded; and
- `0x0045AC20` remains a default-source thunk to `0x0045AC30`. Its inherited
  target display name/signature is relational Ghidra presentation, not a name
  or signature mutation.

| V2 export | Bytes | SHA-256 |
| --- | ---: | --- |
| Dry structural TSV | 5,182 | `f2ddf6eb485eb535c7e451f87f31a49c24e9af8b54f6c479632dffa707408723` |
| Apply structural TSV | 7,663 | `e04f1632d0c06f4c589788c7800310e05156d13cc1148a297639b40c101fcd22` |
| Readback structural TSV | 7,686 | `d98a4113ee4fedea7232dfeed43a4679f3e88768bb031e28747fc614e16b87fb` |
| PRE full functions | 7,161,942 | `c3942b9e340cef71b731290b845843697af5c53204449c51949b779e896272d6` |
| POST full functions | 7,177,146 | `2c1e2842fabd8be4cb840c35bc56074559041404e0c474fee50aad6e98cf4dc5` |
| POST program metrics | 1,267 | `7bce8becc7dc4cbbf9f513bec0effc75889e90079882c5623933aba335f59a4b` |

Memory bytes, defined data and digest, user/analysis/imported symbol counts,
stored non-function-symbol digest, comments and digest, relocations, and every
pre-existing function field remain exact. No name, signature, ABI, parameter,
comment, tag, data definition, executable byte, explicit reference, live
project, tracked project, canonical snapshot, or rebuild mutation is authorized.

## Adversarial and preservation controls

Fresh forced failures after one target and after the complete validated batch
both reopen to exact PRE at the structural, full-function, program, and focused
listing layers. Fresh external-output and external-READY probes both refuse
before mutation and separately reopen to exact PRE. A fresh exact backup copy
opens read-only with analysis and commit disabled and remains byte-identical.

The historical v1 lane is preserved exactly: 367 files / 1,783,242,373 bytes,
tree SHA-256
`56b95b8568e248f58288f2362c4097a3d5771b3ac2a2d99557db98838efe6067`.
It is retained for audit history but is not the current receipt authority.

The ignored v2 lane is
`local-lab/ghidra-crt23-p0-boundary-scratch-20260814-v2/`. Its create-new
`scratch-authority-v2.ready.json` is 8,216 bytes, SHA-256
`e6b0dc6c99856836aeef2047eb7f1665064d21e5b5a49a166d03ebfbbbb25d23`.
The sealed tree excluding that self-referential receipt contains 313 files /
1,574,566,435 bytes, SHA-256
`e8cc6ab0c70f730719e8dea9a0c798a66a397c37b9911ff4ffa4620424cb36e4`.
The authority tool SHA-256 is
`2c37c094b4b89f1c93111e00165164c0e56beee9934efb2ed37aa47d862958dd`;
the v2 mutator SHA-256 is
`b5de94c375005821684ec2ba66a5fd390d265cc775f56a12092ba637389981b8`.

Shared main `8b9e376e86c543ec5f8fce554b8a3e3b09579484` retains the exact tracked
Ghidra tree and every load-bearing map/helper byte. Its Generation 24 and
rebuild/documentation changes are non-inputs to this campaign. The complete
tracked-prep patch applies cleanly there while preserving Generation 24; the
compatibility receipt SHA-256 is
`6c5170aa71f55c64d7426df54201968a00de1255e7b28ce663adf9ecc85ab4e9`.

Reproduce the saved decision only where the v2 lane exists:

```powershell
python -I -B tools/ghidra_crt_p0_boundary_scratch_authority_v2.py verify
```

Any live or tracked admission still requires a separate authorized ceremony.
