# Wave1135 GroundAttack/GillMHead Current-Risk Review

Status: complete static read-only evidence
Date: 2026-06-05
Scope: `wave1135-groundattack-gillmhead-current-risk-review`

Wave1135 accounts for `10 rows` from the Wave1108 current focused continuity denominator as a GroundAttack/GillMHead guide lifecycle cluster. This wave uses fresh Ghidra export evidence as a read-only review and makes no mutation. Current focused accounting moves to `196/1179 = 16.62%` of the continuity denominator. The current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 983. Static closure debt remains `0 / 0 / 0` for commentless / exact-undefined / `param_N`.

Covered anchors:

| Address | Static evidence |
| --- | --- |
| `0x0047a760 CGillMHead__CreateGillMHeadAIComponent` | DATA xref `0x005e43d4`; allocates and installs the `CGillMHeadAI` component vtable, clears `+0x60`, and stores the component at owner `+0x13c`. |
| `0x0047a810 CGillMHeadAI__Destructor` | Called by `0x0047a7f0 CGillMHeadAI__ScalarDeletingDestructor`; restores the `CUnitAI` base vtable, unlinks active-reader/resource handles, then calls `CMonitor__Shutdown`. |
| `0x0047a8b0 CGillMHeadAI__TryTransitionIdleToOpen` | DATA xref `0x005e4350`; checks the current animation against `idle`, gates through deploy-state/charge helper context, and requests the shared `open` animation path. |
| `0x0047bab0 CGroundAttackAI__InitState` | Called from `CGroundAttackAircraft__Init`; clears `+0x60`, seeds a randomized `+0x64` state/timer, and calls `CGroundAttackAircraft__CloseBay`. |
| `0x0047bbf0 CGroundAttackAircraft__Init` | DATA xref `0x005e2bf0`; delegates to `CAirUnit__Init`, allocates/installs `CMCGroundAttack`, `CGroundAttackAI`, and `CGroundAttackGuide`, and initializes bay/state fields. |
| `0x0047bd90 CGroundAttackAI__Destructor` | Called by `0x0047bd70 CGroundAttackAI__ScalarDeletingDestructor`; restores `CUnitAI` base vtable, unlinks tracked reader/set fields, then shuts down the monitor base. |
| `0x0047be50 CGroundAttackGuide__Destructor` | Called by `0x0047be30 CGroundAttackGuide__ScalarDeletingDestructor`; removes linked reader/set field `+0x2c`, then calls `CMonitor__Shutdown`. |
| `0x0047c040 CGroundAttackAircraft__AdvanceCloseShootAnimationState` | DATA xref `0x005e2cb8`; advances the bay animation state through open/shoot/close/idle tokens and writes bay state `+0x27c`. |
| `0x0047e290 CGuide__ctor_base` | Shared guide base constructor with broad guide-family xrefs; installs the base vtable, stores the owner at `+0x18`, copies owner position/orientation fields, clears `+0x1c`, and returns `this`. |
| `0x004964d0 CMCGroundAttack__Constructor` | Called from `CGroundAttackAircraft__Init`; installs vtable `0x005dc330`, stores owner aircraft at `+0x08`, and seeds cached sentinels at `+0x0c/+0x10`. |

Context rows re-read: `0x0047a730 CGillMHeadAIVFunc__ForwardArgAndSetIdleAnimation_0047a730`, `0x0047a7f0 CGillMHeadAI__ScalarDeletingDestructor`, `0x0047a900 CGillMHeadAI__AdvanceOpenAttackCloseState`, `0x0047a9c0 CGillMHeadAIVFunc__ForwardNonMode4ToEngagementSetter_0047a9c0`, `0x0047afc0 CGillMHeadAI__UpdateAimTransformAndTargetReader`, `0x0047b090 CGillMHeadAI__UpdateTargetBallisticArcFlags`, `0x0047bd70 CGroundAttackAI__ScalarDeletingDestructor`, `0x0047be30 CGroundAttackGuide__ScalarDeletingDestructor`, `0x0047bfa0 CGroundAttackAircraft__OpenBay`, `0x0047bff0 CGroundAttackAircraft__CloseBay`, `0x00496500 CMCGroundAttack__ScalarDeletingDestructor`, `0x00496520 CMCGroundAttack__Destructor`, and `0x00496540 CMCGroundAttack__VFunc_04_UpdateTurretTransform_00496540`.

Exact context anchors for probes: context 0x0047a730 CGillMHeadAIVFunc__ForwardArgAndSetIdleAnimation_0047a730; context 0x0047a7f0 CGillMHeadAI__ScalarDeletingDestructor; context 0x0047a900 CGillMHeadAI__AdvanceOpenAttackCloseState; context 0x0047a9c0 CGillMHeadAIVFunc__ForwardNonMode4ToEngagementSetter_0047a9c0; context 0x0047afc0 CGillMHeadAI__UpdateAimTransformAndTargetReader; context 0x0047b090 CGillMHeadAI__UpdateTargetBallisticArcFlags; context 0x0047bd70 CGroundAttackAI__ScalarDeletingDestructor; context 0x0047be30 CGroundAttackGuide__ScalarDeletingDestructor; context 0x0047bfa0 CGroundAttackAircraft__OpenBay; context 0x0047bff0 CGroundAttackAircraft__CloseBay; context 0x00496500 CMCGroundAttack__ScalarDeletingDestructor; context 0x00496520 CMCGroundAttack__Destructor; context 0x00496540 CMCGroundAttack__VFunc_04_UpdateTurretTransform_00496540.

Mutation status:

- Read-only review.
- No Ghidra mutation.
- No rename.
- No signature change.
- No comment change.
- No tag change.
- No function-boundary change.
- No executable-byte change.
- No BEA launch, installed-game mutation, or runtime-file mutation.

Evidence:

- Primary metadata/tag/xref/instruction/decompile exports: `10` / `10` / `22` / `443` / `10`.
- Context metadata/tag/xref/instruction/decompile exports: `13` / `13` / `15` / `546` / `13`.
- Primary logs report `targets=10 found=10 missing=0`, `rows=10 missing=0`, `Wrote 22 rows`, `Wrote 443 function-body instruction rows`, and `targets=10 dumped=10 missing=0 failed=0`.
- Context logs report `targets=13 found=13 missing=0`, `rows=13 missing=0`, `Wrote 15 rows`, `Wrote 546 function-body instruction rows`, and `targets=13 dumped=13 missing=0 failed=0`.
- Final backup after the read-only evidence wave: `[maintainer-local-ghidra-backup-root]\BEA_20260605-111213_post_wave1135_groundattack_gillmhead_current_risk_review_verified`, `19` files, `175967111` bytes, `DiffCount=0`, `HashDiffCount=0`.
- Previous completed Ghidra review backup: `[maintainer-local-ghidra-backup-root]\BEA_20260605-104845_post_wave1134_console_current_risk_review_verified`.

What this proves:

- The ten target rows still exist in the saved Ghidra project with expected names and signatures.
- Saved comments, tags, xrefs, instruction windows, and decompile rows remain coherent with the prior GillMHead, GroundAttackAircraft, Guide, and CMCGroundAttack owner docs.
- The wave narrows current-risk accounting for this lifecycle cluster without changing the saved Ghidra project.
- The Ghidra project was backed up and verified after the read-only evidence wave.

What remains separate:

- Runtime GroundAttack/GillMHead AI behavior.
- Runtime guide/bay-animation/motion-controller behavior.
- Exact source-body identity.
- Concrete `CGillMHeadAI`, `CGroundAttackAircraft`, `CGroundAttackAI`, `CGroundAttackGuide`, `CGuide`, and `CMCGroundAttack` layouts.
- BEA patching behavior.
- Gameplay outcomes.
- Visual QA.
- Rebuild parity.
