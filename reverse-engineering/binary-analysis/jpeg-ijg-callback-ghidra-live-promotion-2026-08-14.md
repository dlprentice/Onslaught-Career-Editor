# JPEG/IJG callback Ghidra live promotion

Date: 2026-08-14

Status: reviewed completed live/tracked structural promotion

Verdict: **LIVE_TRACKED_PROMOTION_REPRODUCED**

Evidence: MEASURED — exact pristine bodies, sealed scratch and current-state
replicas, read-only PRE and POST inventories, one authorized live save, full
function/program diffs, mechanically regenerated projection and body
accounting, and restore-tested PRE/POST/tracked projects. UNKNOWN — original
private linker names, runtime reachability, new semantic contracts, and rebuild
parity.

Specimen: pristine PC retail `BEA.exe`, 2,506,752 bytes, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.

## Exact result

The reviewed JPEG/IJG callback cohort is now present as 24 default-metadata
functions owning 38 pairwise-disjoint body ranges. Every PRE row remains
field-identical:

| Measure | PRE | POST | Delta |
| --- | ---: | ---: | ---: |
| Internal functions | 8,280 | 8,304 | +24 |
| Exact body ranges | 8,396 | 8,434 | +38 |
| Multi-range functions | 67 | 76 | +9 |
| Owned `.text` bytes | 1,795,470 | 1,810,287 | +14,817 |
| `.text` ownership | 93.072115377% | 93.840186987% | +0.768071610 points |
| Unowned `.text` bytes | 133,647 | 118,830 | -14,817 |
| Instructions | 551,014 | 551,055 | +41 |
| References | 234,478 | 234,467 | -11 |

No existing function was destroyed or changed. No signature, parameter,
calling convention, storage field, comment, tag, data definition, stored
non-function symbol, relocation, or program byte changed. The separate POST
inventory is 7,177,776 bytes, SHA-256
`bceedfa2eec573ee95e42a703d6f3a552c4718115fa540f3eaca492322f9a173`.
Program metrics are 1,267 bytes, SHA-256
`bcb364f619559879e815f8d95f5551ba10d9be0467023bd006ee1246b0f9b40f`.
The regenerated 8,304-row tracked projection is 509,334 bytes, SHA-256
`5dd0d1145c2cf25004bd50208c624d9bf4f9c2fe0e4d307ac6c7ca88e8a5dfbc`.

The 646-byte function at `0x005B6800..0x005B6A86` owns `0x005B6900` only
as the final byte of the `MOVZX EAX,byte ptr [EAX]` instruction beginning at
`0x005B68FE`; `0x005B6900` is neither a function entry nor data. The seven-DWORD
table at `0x005B4EB0` and four following NOP bytes remain outside this cohort.

## Physical project and recovery

Live, tracked, the off-volume POST backup, and retained read-only POST/tracked
restore probes reproduce the same project:

- 19 files / 186,993,541 bytes;
- canonical inventory SHA-256
  `3cd459d5461919934199e3346f6a92ce14946f42af400488ccde733173a40627`;
- stable `db.18614.gbf`: 68,337,664 bytes, SHA-256
  `d7f0011ea337f58b710415d5664e73d91ca9f1f61e20a836278d3e71b71b2865`;
- ceremony-current `db.18615.gbf`: 68,354,048 bytes, SHA-256
  `6c2fc2f12394cf7b63f4f335173ba0a19b52b92c50dc4d2da987170501bc9681`.

The sole physical transition removed `db.18613.gbf`, added `db.18615.gbf`,
and changed no common project file. The ceremony used exactly one writable live
apply between read-only PRE and separate read-only POST runs. PRE and POST
off-volume backups were created before their respective next mutation phase and
both reopened read-only. Tracked remained exact PRE through POST recovery, then
was refreshed and independently restored/read back as exact POST.

The POST backup is
`D:\BEA-Ghidra-Backups\2026-08-14-jpeg24-db18614-post-live-v2`.
Its manifest is 7,589 bytes, SHA-256
`f5f0a6445f20d208673ea5d5b5f8ef5548842bcc1a95f4911f2e6991b7a3a4d9`;
the retained restore receipt is 5,908 bytes, SHA-256
`08fe8690f3c8e7d71ce708dcd708d2cfa5d41a9515358f80a6eaa3a0ca4b040e`.
The tracked restore receipt is 5,927 bytes, SHA-256
`de189f7146b63027ca2a05bee3202637606d8733a183615a940dfed4d420ccb8`.

## Authorities and current accounting

The reviewed manifest is
[`jpeg-ijg-callback-function-boundaries-2026-08-14.tsv`](jpeg-ijg-callback-function-boundaries-2026-08-14.tsv).
The immutable scratch result and prospective runbook remain in the
[`scratch-admission report`](jpeg-ijg-callback-ghidra-scratch-admission-2026-08-14.md)
and now-consumed
[`live-promotion preparation`](jpeg-ijg-callback-ghidra-live-promotion-preparation-2026-08-14.md).

The ignored aggregate authority is
`local-lab/ghidra-jpeg24-boundary-live-authority-20260814-v2/live-promotion.ready.json`,
34,732 bytes, SHA-256
`17a5631120e3342f64aaabd512926a0f4ed2b24c39b7879ee0209db59b0d165a`.
Its read-only verifier is
[`ghidra_jpeg_callback_boundary_live_authority.py`](../../tools/ghidra_jpeg_callback_boundary_live_authority.py).
The authority itself never opens or mutates Ghidra; it reproduces the external
ceremony. Before sealing, backup validation was corrected to match the actual
root-free copy-manifest schema while retaining exact physical destination,
project-tree, inspect, chronology, command, probe, and sentinel validation.
Focused hostile tests cover injected roots, a wrong destination, and an
unexpected open record.

A fresh read-only listing export and two byte-identical offline replays update
the current ownership owner. The exact body-union receipt is 14,303 bytes,
SHA-256
`7196209a58c4902d9a14ddb5c20f3364d4aebbd20421a7714131955d7efe6c39`;
the gap-accounting receipt is 3,399 bytes, SHA-256
`f88810826489dbce703a0b375bc4f587dbc4fffd5c6eaeaaaf76966d5e4aec10`.
See
[`current-text-ownership-2026-08-13.md`](current-text-ownership-2026-08-13.md)
for the then-current 118,830-byte partition and its later superseding current
accounting.

## Boundary

This is a structural boundary promotion. Provider/IJG identities and PC-demo
twins remain evidence in the manifest and scratch report at their stated
grades; default `FUN_*` names deliberately avoid claiming original private
symbols. The promotion does not prove execution, original source equivalence,
runtime effects, signatures, or rebuild parity. Generation 25 remains the
frozen campaign authority for the preceding 8,280/db.18614 state; the next
campaign must re-ground the new 8,304/db.18615 geometry rather than rewriting
Generation 25.
