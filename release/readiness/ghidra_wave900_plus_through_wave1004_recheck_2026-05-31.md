# Ghidra Wave900-Wave1004 Recheck Readiness Note

Status: validated current-scope structural static evidence gate
Date: 2026-05-31
Scope: `Wave900-Wave1004`

This note extends the current Wave900+ static re-audit gate through Wave1004 after the HUD render-body read-only review. It keeps older Wave900-Wave1003 notes as historical records and verifies the current public-safe evidence structure before later candidate work.

Validation command:

```powershell
cmd.exe /c npm run test:ghidra-wave900-plus-through-wave1004-recheck
```

Tool command:

```powershell
py -3 tools\ghidra_wave900_plus_through_wave983_recheck.py --last-wave 1004 --check
```

Validated scope after Wave1004 staging:

- Operational readiness notes through Wave1004.
- Focused package probe scripts through Wave1004.
- Ignored evidence bases under `subagents/ghidra-static-reaudit/`.
- On-disk `[maintainer-local-ghidra-backup-root]` references for operational waves, excluding non-backup Wave910/Wave911 planning waves.
- Wave900+ apply-script log coverage where a wave used a Ghidra mutation script.
- Direct Wave982-Wave1004 focused-probe reruns, with stale current-state/live-queue/doc-token failures classified separately from evidence mismatches.
- Current queue closure at `6223/6223 = 100.00%`, with `0` commentless functions, `0` exact-`undefined` signatures, and `0` `param_N` signatures.

Observed summary after Wave1004 validation:

- Readiness notes: 107
- Covered waves: 105
- Package probe scripts: 103
- Evidence bases: 103
- Backup references: 105
- Apply scripts: 32
- Wave982-Wave1004 direct probes: 23 total, 1 pass, 22 classified stale-current failures, 0 disallowed failures
- Wave911 focused re-audit progress: `485/1408 = 34.45%`
- Expanded static surface progress: `654/1478 = 44.25%`
- Wave911 top-500 risk-ranked coverage: `380/500 = 76.00%`

Validation result: PASS.

Wave1004 extension anchor: `hud-render-body-review-wave1004`; `0x00482590 CHud__RenderTargetIndicatorOverlay`; `0x00484c50 CHud__RenderTacticalRadarContacts`; `0x004857e0 HudOverlay__DrawSpriteQuad`; `0x004879e0 CHud__RenderOverlayForViewpoint`; `0x00487bc0 CHud__RenderOverlay`; `0x00487d10 CHud__RenderBattleline`; `0x00488090 CHud__RenderActiveHudComponentPass`; `0x004881e0 CHud__ResolveOverlaySlotRenderMode`; `0x0053ecc0 CDXEngine__PostRender`; `[maintainer-local-ghidra-backup-root]\BEA_20260531-124610_post_wave1004_hud_render_body_review_verified`.

This recheck validates static evidence structure, focused-probe classification, backups, and live queue closure. It does not prove runtime HUD behavior, runtime render behavior, exact source-layout identity, BEA patching behavior, or rebuild parity.
