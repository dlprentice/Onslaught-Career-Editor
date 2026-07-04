# Wave1147 Frontend/Game Shell Score20 Current-Risk Review

Status: complete static read-back evidence
Date: 2026-06-05
Scope: `wave1147-frontend-game-shell-score20-current-risk-review`

Wave1147 re-read ten current-risk rows from the Wave1108 current focused denominator. The slice covers frontend selection/render/font/init/fade rows plus adjacent CGame and GameInterface shell/menu rows. Fresh Ghidra metadata, tag, xref, instruction, and decompile exports found one stale comment phrase: `0x00456830 GlobalListNode__ClearField4AndPushGlobalList` still said the helper pushed through `CWorldPhysicsManager__PushNodeGlobalList`, while the current saved callee is the Wave822-corrected `0x004cb040 ParticleEffectLink__PushGlobalList`.

Wave1147 corrected that one saved function comment and added the `wave1147-frontend-game-shell-score20-current-risk-review` / `wave1147-readback-verified` tags. It made no renames, no signature changes, no function-boundary changes, no executable-byte changes, no BEA launch, no installed-game mutation, no save mutation, and no runtime-file mutation.

## Coverage

| Address | Static read-back |
| --- | --- |
| `0x00451a40 FEPBEConfig__FindSelectedEntryByGlobalId` | Selected/global-id list helper over `0x0089da14`/`DAT_0089d94c`; saved owner correction remains consistent. |
| `0x00452ce0 CFrontEnd__RenderVideoQuadScaledToWindow` | Window-scaled frontend video quad helper; sentinel center uses platform width/height before `CDXFrontEndVideo__Render`. |
| `0x00456830 GlobalListNode__ClearField4AndPushGlobalList` | Corrected saved comment now says the body clears `this+0x4`, calls `ParticleEffectLink__PushGlobalList` at `0x004cb040`, and returns `this`; older `CWorldPhysicsManager`-only callee wording is superseded. |
| `0x004659a0 CDXFont__DrawTextScaledWithShadow` | Draws alpha-only `x+1/y+1` shadow, then foreground text through `CDXFont__DrawTextScaled`; current xref count is `43`. |
| `0x004662a0 CFrontEnd__Init` | Source-bridged startup initializer for loading ranges, shared frontend resources, page wiring, controller allocation, initial page selection, text-set init, and music start. |
| `0x004679e0 CFrontEnd__RenderPreCommonFade` | Clamps transition-derived alpha and calls `CFrontEnd__RenderVideoQuadScaledToWindow` with the composed ARGB value. |
| `0x0046c210 CGame__ctor` | CGame constructor row remains owner-corrected; installs CGame vtable `0x005dbbb4` after base/controller-style initialization. |
| `0x0046c2d0 CGame__dtor` | CGame destructor row remains owner-corrected; unregisters active-reader style links at `this+0xa04` and `this+0x9f8`, then calls `CMonitor__Shutdown`. |
| `0x004729e0 CGameInterface__ResetMenuState` | Clears fade/selection/menu-active fields, enables six menu entries, enables background rendering, and sets menu mode `1`. |
| `0x00472ad0 CGameInterface__AdvanceMenuSelectionWithWrap` | Advances selected menu entry with wrap, respects disabled entry flags, limits option submenu mode `2`, and plays frontend move sound on change. |

## Evidence Counts

- Dry/apply/final dry for `ApplyFrontendGameShellWave1147.java`: `updated=0 skipped=1 comment_only_updated=1 missing=0 bad=0`, then `updated=1 skipped=0 comment_only_updated=1 missing=0 bad=0`, then `updated=0 skipped=1 comment_only_updated=0 missing=0 bad=0`, with `REPORT: Save succeeded`.
- Pre exports: `10` metadata rows, `10` tag rows, `64` xref rows, `708` instruction rows, and `10` decompile rows.
- Post exports: `10` metadata rows, `10` tag rows, `64` xref rows, `708` instruction rows, and `10` decompile rows.
- Queue refresh after the saved comment/tag correction: `6411` total functions, `6411` commented, `0` commentless, `0` exact-undefined signatures, `0` `param_N`, and no uncertain-owner/helper-address/wrapper-address names.
- Backup: `[maintainer-local-ghidra-backup-root]\BEA_20260605-182213_post_wave1147_frontend_game_shell_score20_current_risk_review_verified`; `19` files, `175967111` bytes, `DiffCount=0`, `HashDiffCount=0`.
- Previous completed backup: `[maintainer-local-ghidra-backup-root]\BEA_20260605-174520_post_wave1146_mixed_engine_score20_current_risk_review_verified`.
- Codex subagent usage: none for this slice; Codex root selected and audited the tranche locally against fresh exports.

## Progress

- Static Ghidra function-quality closure: `6411/6411 = 100.00%`.
- Static debt: `0 / 0 / 0` commentless / exact-undefined / `param_N`.
- Expanded post-100 static surface: `1560/1560 = 100.00%`.
- Wave911 focused historical residual: `812/1408 = 57.67%`.
- Wave911 top-500: `500/500 = 100.00%`.
- Wave1108 current focused accounting: `316/1179 = 26.80%`.
- Current risk candidates: 6166.
- Current focused candidates: 1178.
- Live regenerated current focused candidates: 1178.
- Remaining active focused work: 863.

## Boundary

Wave1147 is static Ghidra evidence only. It does not prove runtime frontend behavior, runtime video/fade/font output, runtime GameInterface pause/menu/input behavior, runtime CGame lifecycle behavior, exact layouts, exact source-body identity, BEA patching behavior, gameplay outcomes, visual QA, or rebuild parity.

Probe token anchor: Wave1147; wave1147-frontend-game-shell-score20-current-risk-review; 316/1179 = 26.80%; 10 current-risk rows; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 863; current risk candidates: 6166; frontend/game shell score20 current-risk review; fresh Ghidra export; one saved comment/tag correction; ParticleEffectLink__PushGlobalList; 0x004cb040; read-back verified; no rename; no signature change; no Codex subagent; 0 / 0 / 0; 6411/6411 = 100.00%; FEPBEConfig__FindSelectedEntryByGlobalId; CFrontEnd__RenderVideoQuadScaledToWindow; GlobalListNode__ClearField4AndPushGlobalList; CDXFont__DrawTextScaledWithShadow; CFrontEnd__Init; CFrontEnd__RenderPreCommonFade; CGame__ctor; CGame__dtor; CGameInterface__ResetMenuState; CGameInterface__AdvanceMenuSelectionWithWrap; [maintainer-local-ghidra-backup-root]\BEA_20260605-182213_post_wave1147_frontend_game_shell_score20_current_risk_review_verified; [maintainer-local-ghidra-backup-root]\BEA_20260605-174520_post_wave1146_mixed_engine_score20_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction.
