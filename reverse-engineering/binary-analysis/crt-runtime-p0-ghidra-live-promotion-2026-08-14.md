# CRT runtime P0 Ghidra live promotion

Date: 2026-08-14

Status: reviewed completed live/tracked structural promotion; current project
state is superseded by the later
[CRT EH parent-range repair](crt-eh-parent-range-ghidra-live-promotion-2026-08-14.md)

Verdict: **LIVE_TRACKED_PROMOTION_REPRODUCED**

Evidence: MEASURED — corrected CRT22 static cohort, two current-state disposable
replicas, exact pristine and PC-demo body/CFG joins, read-only PRE and POST
inventories, one authorized live save, full function/program diffs,
mechanically regenerated projection and body/listing accounting, and
restore-tested PRE/POST/tracked projects. UNKNOWN — original private linker
names, runtime reachability and effects, source equivalence, signatures, and
rebuild parity.

Specimen: pristine PC retail `BEA.exe`, 2,506,752 bytes, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.

## Exact result

The reviewed CRT P0 cohort is now present as 23 default-metadata functions
owning 24 pairwise-disjoint body ranges. Every PRE function row remains
byte-identical:

| Measure | PRE | POST | Delta |
| --- | ---: | ---: | ---: |
| Internal functions | 8,304 | 8,327 | +23 |
| Exact body ranges | 8,434 | 8,458 | +24 |
| Multi-range functions | 76 | 77 | +1 |
| Owned `.text` bytes | 1,810,287 | 1,811,418 | +1,131 |
| `.text` ownership | 93.840186987% | 93.898814846% | +0.058627859 points |
| Unowned `.text` bytes | 118,830 | 117,699 | -1,131 |
| Instructions | 551,055 | 551,133 | +78 |
| References | 234,467 | 234,478 | +11 |

No existing function was destroyed or changed. No explicit name, signature,
parameter, calling convention, storage field, comment, tag, data definition,
stored non-function symbol, relocation, or program byte changed. The separate
POST inventory is 7,192,980 bytes, SHA-256
`8640c35a820b3c5e415b947fa8a13eeb5c7c535868780dc2fe511d020a54c40e`.
Program metrics are 1,267 bytes, SHA-256
`185dbd4a9939edacf7302c00c7c48351ad23ad51be14bd5d431130d13848170a`.
The regenerated 8,327-row tracked projection is 510,429 bytes, SHA-256
`17c7153cca64cf6b887dc0bd8d6a7576cfdcd41ce81528c516065ef7e9fa041c`.

The five-byte `0x0045AC20` entry remains a default-source thunk to the existing
`0x0045AC30` function. Ghidra consequently displays the target's existing name
on the thunk; the ceremony did not authorize or perform a name mutation. The
two-range `0x00542710` function owns its local tail beginning at `0x00542720`,
while `0x00542720` remains deliberately absent as a function entry.
`0x005D0AD6` and `0x005D0AEA` likewise remain non-entry EH labels, and the
separate P1 canary at `0x005B8500` remains undefined and excluded.

## Physical project and recovery

Live, tracked, the off-volume POST backup, and retained read-only POST/tracked
restore probes reproduce the same project:

- 19 files / 187,009,925 bytes;
- canonical inventory SHA-256
  `61f77b70fdf807c960a9441ea8e5c4a5b5bd6281675864089a52d61481432f1f`;
- stable `db.18615.gbf`: 68,354,048 bytes, SHA-256
  `6c2fc2f12394cf7b63f4f335173ba0a19b52b92c50dc4d2da987170501bc9681`;
- then-current `db.18616.gbf`: 68,354,048 bytes, SHA-256
  `f0d4988cfa1f36529ed3687816e231bfcc8323240e7d3f9837de48941b8f64fc`.

The sole physical transition removed `db.18614.gbf`, added `db.18616.gbf`,
and changed no common project file. The ceremony used exactly one writable live
apply between read-only PRE and separate read-only POST runs. PRE and POST
off-volume backups were created before their respective next mutation phase
and both reopened read-only. Tracked remained exact PRE through POST recovery,
then was refreshed and independently restored/read back as exact POST.

The PRE and POST backups are respectively
`D:\BEA-Ghidra-Backups\2026-08-14-crt23-db18615-pre-live-v2` and
`D:\BEA-Ghidra-Backups\2026-08-14-crt23-db18615-post-live-v2`. Their manifests
are each 7,589 bytes, SHA-256 `b636b235fc0192e711ad03b45cc6fa02c0df856bff09bea9c67178bf355ff211`
and `ae166c37785bc062a61e97656864a76179b4f82e4de4c69bb4f78a0c95d2f05c`.
The retained POST restore receipt is 5,927 bytes, SHA-256
`1f5377bb9d6036213c969ba4d030e2de7a75bab2030e8373064ba94ed4b1e2d2`;
the tracked restore receipt is 5,947 bytes, SHA-256
`1c8fcc98cb0853242831e984a41398c3da5a63d5ed0de09c9eb36f7f65fcfb55`.

## Authorities and then-current accounting

The reviewed manifest is
[`crt-runtime-p0-function-boundaries-2026-08-14.tsv`](crt-runtime-p0-function-boundaries-2026-08-14.tsv).
The immutable scratch result and prospective runbook remain in the corrected
[`scratch-admission report`](crt-runtime-p0-ghidra-scratch-admission-v2-2026-08-14.md)
and now-consumed
[`live-promotion preparation`](crt-runtime-p0-ghidra-live-promotion-preparation-v2-2026-08-14.md).

The ignored aggregate authority is
`local-lab/ghidra-crt23-p0-boundary-live-promotion-db18615-20260814-v2/live-promotion.ready.json`,
21,932 bytes, SHA-256
`07a085de0ef69c561dba94ad7668dc8d4b560b1b9cb7f419c7820ed2e99722b6`.
Its read-only verifier is
[`ghidra_crt_p0_boundary_live_authority_v2.py`](../../tools/ghidra_crt_p0_boundary_live_authority_v2.py),
57,301 bytes, SHA-256
`1fe983fb208fb1634cad360ae7a4b13a59ee95f11177c960ad1f6a22a7629eb8`.
The authority never launches or mutates Ghidra. It rehashes both preparation
replicas and every ceremony artifact, requires exactly one save marker, binds
the inspect/backup/restore roots and read-only commands, reconstructs all 8,304
unchanged rows plus the exact created set, and recomputes the projection and
body union from POST bytes.

A fresh read-only listing export and two byte-identical offline replays updated
the then-current ownership owner. The exact body-union receipt was 14,303 bytes,
SHA-256
`e27e2f5852a000156a582658ca82f4ee3c979b2175de9c5adb23b0487460c05d`;
the gap-accounting receipt is 3,399 bytes, SHA-256
`61d58f40096d438bbb03375b4b386ab561fadf27ea03e680055eba6bd7fde4d9`.
See
[`current-text-ownership-2026-08-13.md`](current-text-ownership-2026-08-13.md)
for that historical 117,699-byte partition and its current superseding result.

## Boundary

This is a structural boundary promotion. CRT/source-family identities and
PC-demo twins remain evidence in the manifest and scratch report at their
stated grades; default metadata deliberately avoids claiming original private
symbols. The promotion does not prove execution, original source equivalence,
runtime effects, signatures, or rebuild parity. Generation 26 remains the
frozen campaign authority for the preceding 8,304/db.18615 state; the next
campaign had to re-ground the new 8,327/db.18616 geometry rather than rewriting
Generation 26. Generation 27 subsequently did so; physical db.18617 now adds
only the separately sealed CRT EH parent-range repair.
