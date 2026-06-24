# Ghidra Wave900-Wave1003 Recheck Readiness Note

Status: validated current-scope structural static evidence gate
Date: 2026-05-31
Scope: `Wave900-Wave1003`

This note extends the current Wave900+ static re-audit gate through Wave1003 after the HUD head/render-state review and `CGame__Shutdown` boundary recovery. It keeps older Wave900-Wave1002 notes as historical records and verifies the current public-safe evidence structure before later candidate work.

Validation command:

```powershell
cmd.exe /c npm run test:ghidra-wave900-plus-through-wave1003-recheck
```

Tool command:

```powershell
py -3 tools\ghidra_wave900_plus_through_wave983_recheck.py --last-wave 1003 --check
```

Validated scope after Wave1003 staging:

- Operational readiness notes through Wave1003.
- Focused package probe scripts through Wave1003.
- Ignored evidence bases under `subagents/ghidra-static-reaudit/`.
- On-disk `G:\GhidraBackups` references for operational waves, excluding non-backup Wave910/Wave911 planning waves.
- Wave900+ apply-script log coverage where a wave used a Ghidra mutation script.
- Direct Wave982-Wave1003 focused-probe reruns, with stale current-state/live-queue/doc-token failures classified separately from evidence mismatches.
- Current queue closure at `6223/6223 = 100.00%`, with `0` commentless functions, `0` exact-`undefined` signatures, and `0` `param_N` signatures.

Observed summary after Wave1003 validation:

- Readiness notes: 106
- Covered waves: 104
- Package probe scripts: 102
- Evidence bases: 102
- Backup references: 104
- Apply scripts: 32
- Wave982-Wave1003 direct probes: 22 total, 1 pass, 21 classified stale-current failures, 0 disallowed failures
- Wave911 focused re-audit progress: `472/1408 = 33.52%`
- Expanded static surface progress: `641/1478 = 43.37%` plus one newly recovered out-of-seed boundary
- Wave911 top-500 risk-ranked coverage: `371/500 = 74.20%`

Validation result: PASS.

Wave1003 extension anchor: `hud-head-render-state-review-wave1003`; `0x0046c990 CGame__Shutdown`; `0x00481b00 CHud__ShutDown`; `0x00481400 CHud__ctor_base`; `0x00482090 HudRenderState__ApplyOverlaySpriteState`; `0x004821b0 CDXCompass__ApplyRenderStateModulate`; `0x00482210 CHud__RenderSegmentedMeterBar`; `G:\GhidraBackups\BEA_20260531-120949_post_wave1003_hud_head_render_state_review_verified`.

This recheck validates static evidence structure, focused-probe classification, backups, and live queue closure. It does not prove runtime behavior, exact source-layout identity, BEA patching behavior, or rebuild parity.
