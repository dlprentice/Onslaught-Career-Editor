# PC function-body fragment Ghidra live promotion

Date: 2026-08-14

Status: reviewed historical completed live/tracked structural promotion

Verdict: **LIVE_TRACKED_PROMOTION_REPRODUCED**

Evidence: MEASURED — exact pristine bodies, two sealed scratch replicas,
read-only PRE and POST inventories, one authorized live save, full function and
program diffs, mechanically regenerated projection and body accounting, and
restore-tested PRE/POST/tracked projects. UNKNOWN — new semantics, runtime
reachability, original source boundaries beyond the proved fragments, and
rebuild parity.

Specimen: pristine PC retail `BEA.exe`, 2,506,752 bytes, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.

## Exact result

Five existing functions now own their independently reviewed loose body
fragments. No function was created or destroyed:

| Existing owner | Added body interval | Bytes |
| --- | ---: | ---: |
| `CFEPMain__Process @ 0x00462640` | `0x0046282B..0x00462B64` | 825 |
| `CGame__HandleEvent @ 0x0046FF10` | `0x004700DA..0x004700F0` | 22 |
| `CHud__RenderTargetIndicatorOverlay @ 0x00482590` | `0x00482725..0x00482741` | 28 |
| `CExplosionInitThing__SelectNextPathStepDirection @ 0x004BE420` | `0x004BE82D..0x004BE93D` | 272 |
| `CDXTexture__CreateMipmaps @ 0x00559410` | `0x0055954C..0x005595BB` | 111 |

| Measure | PRE | POST | Delta |
| --- | ---: | ---: | ---: |
| Internal functions | 8,280 | 8,280 | 0 |
| Exact body ranges | 8,400 | 8,396 | -4 |
| Multi-range functions | 70 | 67 | -3 |
| Owned `.text` bytes | 1,794,212 | 1,795,470 | +1,258 |
| `.text` ownership | 93.006904195% | 93.072115377% | +0.065211182 points |
| Unowned `.text` bytes | 134,905 | 133,647 | -1,258 |
| Instructions | 550,991 | 551,014 | +23 |
| References | 234,495 | 234,478 | -17 |

Every exported field of 8,275 non-target function rows is byte-identical. The
five target rows differ only in their proved body fields. Names, signatures,
parameters, ABI/storage fields, comments, tags, program memory, defined data,
stored non-function symbols, and relocations did not change. The twelve exact
NOP bytes at `0x00462B64..0x00462B70` remain excluded alignment.

The separate read-only POST inventory is 7,161,943 bytes, SHA-256
`d2ff1e8e7bd91454fff9822fb7ecc8e624525fa5c6cbc9dcfe06f4e0212b750d`.
Program metrics are 1,267 bytes, SHA-256
`b389487a65d6271329703c9e3ec9186b7261aa871a154c31179322780e1c132e`.
The regenerated 8,280-row tracked projection is 508,239 bytes, SHA-256
`267210a78248f58da6bca1b4d11ee7b1812481602413e8bcac2fb4e4b4c4cb84`.

## Physical project and recovery

Live, tracked, the off-volume POST backup, and the retained read-only POST and
tracked restore probes reproduce the same project:

- 19 files / 186,977,157 bytes;
- canonical inventory SHA-256
  `cda0938c1a266fbe1751a8b0bf175b90c63b296f21fc9631b5bade1ecf93e541`;
- stable `db.18613.gbf`: 68,337,664 bytes, SHA-256
  `615497847b0c732077ee7164b0973b9012092523e9ad99b91c21781952420ebe`;
- then-current `db.18614.gbf`: 68,337,664 bytes, SHA-256
  `d7f0011ea337f58b710415d5664e73d91ca9f1f61e20a836278d3e71b71b2865`.

The sole physical transition removed `db.18612.gbf`, added `db.18614.gbf`,
and changed no common project file. The ceremony used exactly one writable live
apply between read-only PRE and separate read-only POST runs. PRE and POST
off-volume backups were created before their respective next mutation phase and
both reopened read-only. Tracked remained exact PRE through POST recovery, then
was refreshed and independently restored/read back as exact POST.

The POST backup is
`D:\BEA-Ghidra-Backups\2026-08-14-function-fragment5-ranges-post-live`.
Its manifest is 7,589 bytes, SHA-256
`0c9d163c145ae97dbe27549c8527fc53e20ebd30232bf8fb524cdb744cf3317a`;
the retained restore receipt is 5,934 bytes, SHA-256
`4c23fcdf78d02070465c8a1b27923f157721e3161f19e0ca1a03fc97d4fb9f36`.
The tracked restore receipt is 5,945 bytes, SHA-256
`facf9a67d54a67139f8d7b6b0205055cafb0c616e2d4ee03a8fca5c26ea6f4bc`.

## Authorities and then-current accounting

The reviewed manifest is
[`pc-function-body-fragment-repairs-2026-08-14.tsv`](pc-function-body-fragment-repairs-2026-08-14.tsv).
The immutable scratch result and the prospective runbook remain in the
[`scratch-admission report`](pc-function-body-fragment-ghidra-scratch-admission-2026-08-14.md)
and the now-consumed
[`live-promotion preparation`](pc-function-body-fragment-ghidra-live-promotion-preparation-2026-08-14.md).

The ignored aggregate authority is
`local-lab/ghidra-function-fragment5-range-live-authority-20260814-v1/live-promotion.ready.json`,
26,073 bytes, SHA-256
`18b8a7e75bf44108d72c7589dc2fa6a1ac0e2634fbb8ac387562b41ac2fdd451`.
Its read-only verifier is
[`ghidra_function_fragment_range_live_authority.py`](../../tools/ghidra_function_fragment_range_live_authority.py),
68,331 bytes, SHA-256
`bc6c7fdc9ee9a19ccff0c437166dbde2b08b98a7bcd78b4d3ca7a46de0cab30c`.
The authority itself never opens or mutates Ghidra; it reproduces the external
ceremony. Before the final seal, its backup validation was corrected to accept
the actual copy-receipt schema while retaining strict probe-path, command,
sentinel, tree, and hash validation in the separate restore receipts. A focused
regression covers that receipt boundary.

A fresh read-only listing export and two byte-identical offline replays updated
the then-current ownership owner. The exact body union receipt is 14,318 bytes,
SHA-256
`d2e35899eff73cf6ca22304010fbe219320832416c2a79e49b365fd3acfde056`;
the gap-accounting receipt is 3,401 bytes, SHA-256
`18084153a1577f08640268109520602669433b2ca2dd69cf56e97b8a6edd0d61`.
The prior five-row jump-fragment candidate class is now empty. See
[`current-text-ownership-2026-08-13.md`](current-text-ownership-2026-08-13.md)
for the historical 133,647-byte partition and its newer superseding results.

## Boundary

This is a body/range and listing repair, not five new semantic contracts. Static
source/demo/runtime evidence remains owned by the manifest and scratch report at
their stated grades. The promotion does not prove whole-function source
equivalence, execution of uncovered branches, field meanings, runtime effects,
or rebuild parity. Generation 24 remains the last sealed campaign authority;
its semantic carry is unchanged, and Generation 25 later re-grounded the
`db.18614` geometry without rewriting the frozen Generation 24 reducer. The
subsequent JPEG/IJG promotion then advanced the structural state to db.18615;
the later CRT P0 promotion advanced it to db.18616, and the still-later CRT EH
parent-range repair advanced it to db.18617. The later D3DX two-function
promotion now owns current db.18618.
