# Wave1147 Frontend/Game Shell Score20 Current-Risk Review Readiness Note

Status: complete static read-back evidence
Date: 2026-06-05
Scope: `wave1147-frontend-game-shell-score20-current-risk-review`

Wave1147 reviewed ten frontend/game-shell score20 current-risk rows from the Wave1108 current focused denominator. The wave found and corrected one saved Ghidra comment/tag issue at `0x00456830 GlobalListNode__ClearField4AndPushGlobalList`: the body calls the Wave822-corrected `ParticleEffectLink__PushGlobalList` at `0x004cb040`, so the older `CWorldPhysicsManager`-only callee wording was too narrow.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x00451a40 FEPBEConfig__FindSelectedEntryByGlobalId` | Walks the selected/global-id list state and compares entries against `DAT_0089d94c`. |
| `0x00452ce0 CFrontEnd__RenderVideoQuadScaledToWindow` | Uses platform window dimensions for sentinel-centered video quad rendering through `CDXFrontEndVideo__Render`. |
| `0x00456830 GlobalListNode__ClearField4AndPushGlobalList` | Saved comment/tag correction: clears `this+0x4`, calls `0x004cb040 ParticleEffectLink__PushGlobalList`, and returns `this`. |
| `0x004659a0 CDXFont__DrawTextScaledWithShadow` | Calls `CDXFont__DrawTextScaled` twice: alpha shadow at `x+1/y+1`, then foreground text. |
| `0x004662a0 CFrontEnd__Init` | Source-bridged frontend startup initializer. |
| `0x004679e0 CFrontEnd__RenderPreCommonFade` | Clamps transition alpha and calls the shared video-quad helper. |
| `0x0046c210 CGame__ctor` / `0x0046c2d0 CGame__dtor` | CGame lifecycle owner-corrected rows remain static-consistent. |
| `0x004729e0 CGameInterface__ResetMenuState` / `0x00472ad0 CGameInterface__AdvanceMenuSelectionWithWrap` | Pause/menu state reset and selection wrap helpers remain static-consistent. |

Read-back evidence:

- `ApplyFrontendGameShellWave1147.java dry`: `updated=0 skipped=1 comment_only_updated=1 missing=0 bad=0`
- `ApplyFrontendGameShellWave1147.java apply`: `updated=1 skipped=0 comment_only_updated=1 missing=0 bad=0`
- `ApplyFrontendGameShellWave1147.java final dry`: `updated=0 skipped=1 comment_only_updated=0 missing=0 bad=0`
- Pre exports: `10` metadata rows, `10` tag rows, `64` xref rows, `708` instruction rows, and `10` decompile rows.
- Post exports: `10` metadata rows, `10` tag rows, `64` xref rows, `708` instruction rows, and `10` decompile rows.
- Queue after Wave1147: `6411` total, `6411` commented, `0` commentless, `0` exact-undefined signatures, `0` `param_N`.
- Wave1108 current focused accounting: `316/1179 = 26.80%`; live regenerated current focused candidates remain `1178`; remaining active focused work is `863`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260605-182213_post_wave1147_frontend_game_shell_score20_current_risk_review_verified`, `19` files, `175967111` bytes, `DiffCount=0`, `HashDiffCount=0`.

What this proves:

- The ten target rows exist in the saved Ghidra project and remain name/signature clean.
- The saved `0x00456830` comment/tags now identify `ParticleEffectLink__PushGlobalList` as the callee and carry `wave1147-readback-verified`.
- The static closure counters remain `6411/6411 = 100.00%` and `0 / 0 / 0` commentless / exact-undefined / `param_N`.

What remains unproven:

- Runtime frontend behavior.
- Runtime video/fade/font output.
- Runtime GameInterface pause/menu/input behavior.
- Runtime CGame lifecycle behavior.
- Exact layouts and exact source-body identity.
- BEA patching behavior, gameplay outcomes, visual QA, and rebuild parity.

Probe token anchor: Wave1147; wave1147-frontend-game-shell-score20-current-risk-review; 316/1179 = 26.80%; 10 current-risk rows; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 863; current risk candidates: 6166; frontend/game shell score20 current-risk review; fresh Ghidra export; one saved comment/tag correction; ParticleEffectLink__PushGlobalList; 0x004cb040; read-back verified; no rename; no signature change; no Codex subagent; 0 / 0 / 0; 6411/6411 = 100.00%; FEPBEConfig__FindSelectedEntryByGlobalId; CFrontEnd__RenderVideoQuadScaledToWindow; GlobalListNode__ClearField4AndPushGlobalList; CDXFont__DrawTextScaledWithShadow; CFrontEnd__Init; CFrontEnd__RenderPreCommonFade; CGame__ctor; CGame__dtor; CGameInterface__ResetMenuState; CGameInterface__AdvanceMenuSelectionWithWrap; [maintainer-local-ghidra-backup-root]\BEA_20260605-182213_post_wave1147_frontend_game_shell_score20_current_risk_review_verified; [maintainer-local-ghidra-backup-root]\BEA_20260605-174520_post_wave1146_mixed_engine_score20_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction.
