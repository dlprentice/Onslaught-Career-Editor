# Wave1135 GroundAttack/GillMHead Current-Risk Review Readiness

Status: complete static read-only evidence
Date: 2026-06-05
Scope: `wave1135-groundattack-gillmhead-current-risk-review`

Wave1135 re-read ten GroundAttack/GillMHead guide lifecycle current-risk rows with fresh Ghidra metadata, tag, xref, instruction, and decompile exports.

Probe anchor: Wave1135; `wave1135-groundattack-gillmhead-current-risk-review`; `10 rows`; `196/1179 = 16.62%`; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 983; GroundAttack/GillMHead guide lifecycle cluster; fresh Ghidra export; read-only review; no mutation; static debt `0 / 0 / 0`; verified backup `[maintainer-local-ghidra-backup-root]\BEA_20260605-111213_post_wave1135_groundattack_gillmhead_current_risk_review_verified`; previous completed backup `[maintainer-local-ghidra-backup-root]\BEA_20260605-104845_post_wave1134_console_current_risk_review_verified`.

Read-back evidence:

- Primary exports: `10` metadata rows, `10` tag rows, `22` xref rows, `443` instruction rows, and `10` decompile rows.
- Context exports: `13` metadata rows, `13` tag rows, `15` xref rows, `546` instruction rows, and `13` decompile rows.
- Primary rows: `0x0047a760 CGillMHead__CreateGillMHeadAIComponent`, `0x0047a810 CGillMHeadAI__Destructor`, `0x0047a8b0 CGillMHeadAI__TryTransitionIdleToOpen`, `0x0047bab0 CGroundAttackAI__InitState`, `0x0047bbf0 CGroundAttackAircraft__Init`, `0x0047bd90 CGroundAttackAI__Destructor`, `0x0047be50 CGroundAttackGuide__Destructor`, `0x0047c040 CGroundAttackAircraft__AdvanceCloseShootAnimationState`, `0x0047e290 CGuide__ctor_base`, and `0x004964d0 CMCGroundAttack__Constructor`.
- Context rows include the adjacent scalar-deleting destructor wrappers, bay open/close helpers, CMCGroundAttack destructor/slot-4 helper, and Wave1118-covered `0x0047afc0 CGillMHeadAI__UpdateAimTransformAndTargetReader` plus `0x0047b090 CGillMHeadAI__UpdateTargetBallisticArcFlags`.
- Current focused accounting: `196/1179 = 16.62%`; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 983.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260605-111213_post_wave1135_groundattack_gillmhead_current_risk_review_verified`, `19` files, `175967111` bytes, `DiffCount=0`, `HashDiffCount=0`.

Mutation status:

- No Ghidra mutation.
- No rename.
- No signature change.
- No comment change.
- No tag change.
- No function-boundary change.
- No executable-byte change.
- No BEA launch, installed-game mutation, or runtime-file mutation.

What this proves:

- The ten target rows still exist in the saved Ghidra project with expected saved names and signatures.
- Fresh xrefs, instruction windows, decompile rows, and existing owner docs still support the static GroundAttack/GillMHead/guide lifecycle contracts.
- The project backup was verified after the read-only evidence wave.

What remains separate:

- Runtime GroundAttack/GillMHead AI behavior.
- Runtime guide/bay-animation/motion-controller behavior.
- Exact source-body identity and concrete `CGillMHeadAI`, `CGroundAttackAircraft`, `CGroundAttackAI`, `CGroundAttackGuide`, `CGuide`, and `CMCGroundAttack` layouts.
- BEA patching behavior, gameplay outcomes, visual QA, and rebuild parity.
