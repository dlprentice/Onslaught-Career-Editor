# Ghidra Wave900 Through Wave1013 Static Re-Audit Recheck

Status: PASS
Date: 2026-05-31
Scope: Wave900-Wave1013 static re-audit evidence

Wave1013 extends the current Wave900+ recheck gate after `hud-lifecycle-render-support-review-wave1013` re-read HUD lifecycle/render-support rows with no mutation. The gate preserves the earlier Wave900-Wave981 structural audits, reruns Wave982-Wave1013 focused probes directly, and checks current queue closure.

Current Wave1013 anchors: `0x00481450 CHud__Init`, `0x004815c0 CHud__Reset`, `0x00481650 CHud__LoadTextures`, `0x00481af0 CHud__PostLoadProcess`, `0x00481f40 CHud__SetHudComponent`, `0x004821e0 CDXCompass__ApplyRenderStateAdditive`, `0x00488330 CIBuffer__CreateConfigured`, `0x004885e0 CIBuffer__LockDirect`, `0x0048f540 CLevelBriefingLog__ctor`, `0x0048f5a0 CLevelBriefingLog__scalar_deleting_dtor`, and `0x0048f5c0 CLevelBriefingLog__dtor`. Queue closure after Wave1013 is `6238/6238 = 100.00%`. Re-audit progress after Wave1013 is Wave911 focused `505/1408 = 35.87%`, expanded static surface `718/1493 = 48.09%`, and Wave911 top-500 risk-ranked `420/500 = 84.00%`.

The Wave1013 verified backup is `[maintainer-local-ghidra-backup-root]\BEA_20260531-182125_post_wave1013_hud_lifecycle_render_support_review_verified`, 18 files, 173968263 bytes, `DiffCount=0`, `HashDiffCount=0`.

Probe token anchor: Wave1013; hud-lifecycle-render-support-review-wave1013; 0x00481450 CHud__Init; 0x004815c0 CHud__Reset; 0x00481650 CHud__LoadTextures; 0x00481af0 CHud__PostLoadProcess; 0x00481f40 CHud__SetHudComponent; 0x004821e0 CDXCompass__ApplyRenderStateAdditive; 0x00488330 CIBuffer__CreateConfigured; 0x004885e0 CIBuffer__LockDirect; 0x0048f540 CLevelBriefingLog__ctor; 0x0048f5a0 CLevelBriefingLog__scalar_deleting_dtor; 0x0048f5c0 CLevelBriefingLog__dtor; 505/1408 = 35.87%; 718/1493 = 48.09%; 420/500 = 84.00%; 6238/6238 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260531-182125_post_wave1013_hud_lifecycle_render_support_review_verified; no mutation.

Validation command:

```powershell
cmd.exe /c npm run test:ghidra-wave900-plus-through-wave1013-recheck
```

Validation result: PASS. The Wave900-Wave1013 gate verified 116 readiness notes, 114 covered waves, 112 package probe scripts, 112 ignored evidence bases, 114 backup references, and 37 apply scripts. Direct Wave982-Wave1013 focused-probe classification wrote `subagents/ghidra-static-reaudit/wave900-plus-through-wave1013-recheck/wave982-wave1013-direct-probe-results.tsv` with 32 results: 1 direct pass, 31 classified stale-current failures, and 0 disallowed evidence failures. Current queue remained `6238/6238 = 100.00%` with 0 commentless functions, 0 exact-undefined signatures, and 0 `param_N` signatures.

Boundary note: this gate validates static evidence structure, backups, apply logs, focused probe classifications, and current queue closure. It does not prove runtime HUD, compass, briefing-log, index-buffer, or gameplay behavior; exact source-layout identity; concrete layouts; BEA patching; or rebuild parity.

Prior current gate: `release/readiness/ghidra_wave900_plus_through_wave1012_recheck_2026-05-31.md`.
