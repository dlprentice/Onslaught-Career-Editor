# HUD source-identity correction

Status: promoted, bounded static source-method identity
Last updated: 2026-08-12
Evidence: MEASURED — sealed pristine-body, source-line, call-edge,
cross-build, scratch/readback, live-promotion, backup/restore, and tracked-
snapshot receipts
Verdict: three mutually displaced HUD labels were corrected and saved in live
and tracked Ghidra; runtime-visible output and reconstruction parity remain
open.

Specimen: pristine PC retail `BEA.exe`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

## Result

Three saved HUD labels were mutually displaced. The corrected identities are:

| Retail address | Superseded label | Current identity | Retail body |
| --- | --- | --- | --- |
| `0x00482050` | `CHud__PromotePendingHudComponent` | `CHud__SwitchInOverlay` | `0x00482050..0x00482088` |
| `0x00487BC0` | `CHud__RenderOverlay` | `CHud__Render` | `0x00487BC0..0x00487D0B` |
| `0x00488090` | `CHud__RenderActiveHudComponentPass` | `CHud__RenderOverlay` | `0x00488090..0x004881DF` |

The sealed proof is
`local-lab/hud-source-identity-reproof-20260812-v1/proof.ready.json`, 9,029
bytes, SHA-256
`37de27d99272b4f55b6024a987bab2e4655043623752ba3b5b4cfe708a92ecae`.
Six focused adversarial tests passed.

## Why the correction is warranted

Two supplied source variants preserve the same method order. `PCEngine.cpp`
calls `HUD.Render()` at line 846, `HUD.RenderOverlay()` at line 900, and
`HUD.SwitchInOverlay()` at line 936. `DXEngine.cpp` calls `HUD.Render()` at
line 1333, `HUD.RenderBattleline(viewport)` at line 1354,
`HUD.RenderOverlay()` at line 1418, and `HUD.SwitchInOverlay()` at line 1457.

The pristine retail `CDXEngine__PostRender` body at `0x0053ECC0` preserves that
order against the same receiver, `0x008AA4E8`:

| Call site | Retail target | Source-method identity |
| --- | --- | --- |
| `0x0053ED01` | `0x00487BC0` | `CHud::Render` |
| `0x0053ED79` | `0x00487D10` | `CHud::RenderBattleline` |
| `0x0053EF26` | `0x00488090` | `CHud::RenderOverlay` |
| `0x0053EF5E` | `0x00482050` | `CHud::SwitchInOverlay` |

Independent body landmarks agree with those identities. `0x00487BC0` performs
the broad HUD render spine and calls the per-viewpoint path at `0x00487C57`.
`0x00488090` reads the active overlay slot at `this+0x1FC`, invokes its render
path, reads its state byte, and may clear the slot. `0x00482050` reads the
pending slot at `this+0x200`, clears it, and installs the value at
`this+0x1FC`.

The Xbox sparse source-line oracle has no anchor on these source lines and was
not counted as supporting evidence. The supplied source establishes identity
and order correspondence, not byte-for-byte retail source-body equality.

## Ghidra promotion and recovery

The correction was promoted only after exact PRE validation, an off-volume PRE
backup, two persistent scratch replicas, a fail-after-first-target rollback
probe, a fail-after-inner-commit compensating-restore probe, separate-process
readback, and full-inventory comparison. Exactly three names, three displayed
signatures, three comments, and three tag sets changed. Program bytes,
instructions, function bodies and boundaries, data units, and references did
not change. Function and instruction counts remain 8,136 and 549,872.

The live POST project was copied to
`D:\BEA-Ghidra-Backups\2026-08-12-hud-source-identity-post-live`, compared
exactly, and reopened read-only. Its 19-file, 186,485,637-byte tree was then
promoted to `reverse-engineering/ghidra/` and independently restored and
reopened. The promotion authority is
`local-lab/ghidra-hud-source-identity-live-promotion-20260812-v1/live-promotion.ready.json`,
6,905 bytes, SHA-256
`cd524c7976d27c7688800919eb0ef385795cdfe84715c880c153684ace27a5a5`.
The tracked restore receipt is
`local-lab/ghidra-hud-source-identity-live-promotion-20260812-v1/tracked-snapshot-restore.ready.json`,
5,947 bytes, SHA-256
`42c5ca3cf7394b1ad20b4e53598dd40404addca87a36a38dc5880d6e19cb535e`.

The separate live readback is 8,136 rows, 7,059,968 bytes, SHA-256
`fa2c9d749c97f1ab439b90572fd8f2292c9f5dcf4cc8b9b4f29f1756f088fed1`.
Its deterministic four-column tracked projection is
[`ghidra-function-name-table-2026-08-12.tsv`](ghidra-function-name-table-2026-08-12.tsv),
8,136 rows, 501,131 bytes, SHA-256
`49d6639a62268e394c85f7111b562357ca408390c2e9b08ede27d900d7e66653`.
`tools/re_ghidra_name_projection.py` reproduces and verifies that projection
from the exact sealed readback.

## Historical boundary

The July name table, fullpass wave reports, PC demo/retail map, static-C1
closure, and Generation 23 campaign are dated evidence. They retain the labels
present when they were sealed and are not silently rewritten. This report and
the 2026-08-12 projection supersede those three labels for current identity;
the historical bodies, mappings, observations, and accounting remain intact.

This correction does not establish visible rendering results, every branch or
side effect, final field semantics, failure behavior, reconstruction parity, or
`REBUILD_READY` status.
