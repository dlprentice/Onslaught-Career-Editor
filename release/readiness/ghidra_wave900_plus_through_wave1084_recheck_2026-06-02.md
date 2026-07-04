# Ghidra Wave900+ Through Wave1084 Recheck Note

Status: PASS
Date: 2026-06-02
Scope: `wave900-plus-through-wave1084-recheck`

This note extends the post-Wave900 recheck chain through Wave1084 and records the Wave1084 local validation gate:

```powershell
npm run test:ghidra-wave900-plus-through-wave1084-recheck
```

Wave1084 (`top500-residual-pre900-correction-review-wave1084`) re-read six Wave911 top-500 risk-ranked rows that were corrected in pre-900 waves but had not yet been represented by a post-900 readiness note: `0x004d1f10 CPlane__Hit_CheckFatalDamageAndDie`, `0x004de1d0 CSafeSide__ShutdownAndUnlinkFactionAnchor`, `0x004ea8d0 CRelaxedSquad__CreateIterator`, `0x00505960 CWaypoint__Load`, `0x00523db0 Input__ResetMouseTransientState`, and `0x005245e0 COggFileRead__scalar_deleting_dtor`. The focused readiness note is [`ghidra_top500_residual_pre900_correction_review_wave1084_2026-06-02.md`](ghidra_top500_residual_pre900_correction_review_wave1084_2026-06-02.md).

Aggregate result:

- Status: `PASS`
- Readiness notes: `187`
- Covered waves: `185`
- Package probe scripts: `183`
- Evidence bases: `183`
- Backup references: `185`
- Apply scripts: `63`
- Wave982-Wave1084 direct probes: `resultCount=103`, `passCount=1`, `failCount=102`, `disallowedFailureCount=0`
- Current queue: `totalFunctions=6307`, `commentlessFunctionCount=0`, `undefinedSignatureCount=0`, `paramSignatureCount=0`, `status=PASS`

Coverage anchors:

- Static function-quality closure is `6307/6307 = 100.00%`.
- Wave911 focused re-audit progress remains `812/1408 = 57.67%`.
- Expanded static surface progress advances to `1424/1560 = 91.28%`.
- Wave911 top-500 risk-ranked coverage remains `500/500 = 100.00%`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260602-122026_post_wave1084_top500_residual_pre900_correction_review_verified`, `19` files, `174820231` bytes, `DiffCount=0`.

Boundary: this is static Ghidra/documentation/probe coverage evidence only. Runtime plane hit/death behavior, SafeSide/faction-anchor behavior, squad iterator lifetime, waypoint navigation/load behavior, mouse/input behavior, Ogg streaming/audio behavior, exact source-body identity, concrete layouts, BEA patching behavior, gameplay outcomes, and rebuild parity remain separate proof.

Probe token anchor: Wave1084; top500-residual-pre900-correction-review-wave1084; 0x004d1f10 CPlane__Hit_CheckFatalDamageAndDie; 0x004de1d0 CSafeSide__ShutdownAndUnlinkFactionAnchor; 0x004ea8d0 CRelaxedSquad__CreateIterator; 0x00505960 CWaypoint__Load; 0x00523db0 Input__ResetMouseTransientState; 0x005245e0 COggFileRead__scalar_deleting_dtor; 1424/1560 = 91.28%; 812/1408 = 57.67%; 500/500 = 100.00%; 6307/6307 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260602-122026_post_wave1084_top500_residual_pre900_correction_review_verified; no mutation.
