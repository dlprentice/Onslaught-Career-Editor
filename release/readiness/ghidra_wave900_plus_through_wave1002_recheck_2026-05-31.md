# Ghidra Wave900-Wave1002 Recheck Readiness Note

Status: validated current-scope structural static evidence gate
Date: 2026-05-31
Scope: `Wave900-Wave1002`

This note extends the current Wave900+ static re-audit gate through Wave1002 after the GroundAttackAircraft read-only review. It keeps older Wave900-Wave1001 notes as historical records and verifies the current public-safe evidence structure before later candidate work.

Validation command:

```powershell
cmd.exe /c npm run test:ghidra-wave900-plus-through-wave1002-recheck
```

Tool command:

```powershell
py -3 tools\ghidra_wave900_plus_through_wave983_recheck.py --last-wave 1002 --check
```

Validated scope after Wave1002 staging:

- Operational readiness notes through Wave1002.
- Focused package probe scripts through Wave1002.
- Ignored evidence bases under `subagents/ghidra-static-reaudit/`.
- On-disk `G:\GhidraBackups` references for operational waves, excluding non-backup Wave910/Wave911 planning waves.
- Wave900+ apply-script log coverage where a wave used a Ghidra mutation script.
- Direct Wave982-Wave1002 focused-probe reruns, with stale current-state/live-queue/doc-token failures classified separately from evidence mismatches.
- Current queue closure at `6222/6222 = 100.00%`, with `0` commentless functions, `0` exact-`undefined` signatures, and `0` `param_N` signatures.

Observed summary after Wave1002 validation:

- Readiness notes: `105`
- Covered waves: `103`
- Package probe scripts: `101`
- Evidence bases: `101`
- Backup references: `103`
- Apply scripts: `31`
- Wave982-Wave1002 direct probes: `21` total, `1` pass, `20` classified stale current-state/doc-token failures, `0` disallowed failures.
- Wave911 focused re-audit progress: `472/1408 = 33.52%`
- Expanded static surface progress: `629/1478 = 42.56%`
- Wave911 top-500 risk-ranked coverage: `359/500 = 71.80%`

Validation result: `PASS`. Direct probe reruns only passed for the current Wave1002 focused probe; earlier Wave982-Wave1001 focused probes intentionally fail against rolled-current state/docs and are classified as `current-state-baton` and/or `rolled-current-doc`, with no evidence-mismatch, missing-tool, or unclassified failure remaining.

Wave1002 extension anchor: `ground-attack-aircraft-review-wave1002`; `0x0047bbf0 CGroundAttackAircraft__Init`; `0x0047c040 CGroundAttackAircraft__AdvanceCloseShootAnimationState`; `0x004964d0 CMCGroundAttack__Constructor`; `0x00496540 CMCGroundAttack__VFunc_04_UpdateTurretTransform_00496540`; `0x004968a0 CMCGroundAttack__VFunc_08_CheckCachedMotionState_004968a0`; `G:\GhidraBackups\BEA_20260531-112128_post_wave1002_ground_attack_aircraft_review_verified`.

This recheck validates static evidence structure, focused-probe classification, backups, and live queue closure. It does not prove runtime behavior, exact source-layout identity, BEA patching behavior, or rebuild parity.
