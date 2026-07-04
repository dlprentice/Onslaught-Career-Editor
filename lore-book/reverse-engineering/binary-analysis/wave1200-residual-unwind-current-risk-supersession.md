# Wave1200 Residual Compiler-Unwind Current-Risk Supersession

Status: complete read-only static supersession
Date: 2026-06-06
Scope: `wave1200-residual-unwind-current-risk-supersession`

Wave1200 re-read `147 residual compiler-unwind current-risk rows` from the Wave1108 current-risk denominator. The targets are compiler-generated SEH cleanup callbacks named `Unwind@...`, spanning `0x005d1115 Unwind@005d1115` through `0x005d7f53 Unwind@005d7f53`. Representative anchors include `0x005d1115 Unwind@005d1115`, `0x005d3440 Unwind@005d3440`, and the CFastVB cleanup tail ending at `0x005d7f53 Unwind@005d7f53`.

The wave is a read-only supersession. It made no rename, no signature change, no comment change, no tag change, no function-boundary change, and no executable-byte change. The generic `Unwind@address` names remain intentional because the static evidence proves compiler cleanup callbacks and scope-table entries, not exact parent source-body identity.

Fresh Ghidra evidence:

| Export | Rows |
| --- | ---: |
| Metadata | `147` |
| Tags | `147` |
| Xrefs | `147 xref rows` |
| Instructions | `348 instruction rows` |
| Decompile index | `147 decompile rows` |

All `147` targets have `void __cdecl Unwind@...(void)` signatures, non-empty static read-back comments from Waves741-788, compiler-unwind/scope-table tags, DATA scope-table xrefs, and `OK` decompile rows. The evidence covers BattleEngine.cpp, CPhysicsScript.cpp, eventmanager.cpp, FrontEnd.cpp, game.cpp, GillM.cpp, GillMHead.cpp, GroundAttackAircraft.cpp, GroundVehicle.cpp, Infantry.cpp, UnitAI/monitor cleanup, MemoryManager, Player, RadarWarningReceiver, Sentinel, SphereTrigger, Submarine, Tentacle, texture, tree, Warspite, CFastVB, and related cleanup contexts.

Measured status:

| Track | Value |
| --- | ---: |
| Static Ghidra function-quality closure | `6411/6411 = 100.00%` |
| Commentless / exact-undefined / `param_N` debt | `0 / 0 / 0` |
| Corrected current-risk reviewed rows | `1017/1179 = 86.26%` |
| Remaining active focused work | `162` |
| Current risk candidates | `6166` |
| Current focused candidates | `1141` |
| Live regenerated current focused candidates | `1141` |

Accounting boundary: active progress is unique-address accounting from `static-reaudit-current-risk-ledger.json`. The legacy additive counter is deprecated (`1048/1179`) because it includes a 26 duplicate-address overcount and Wave1145 arithmetic overcount: 5. Wave911 is historical-retired/non-reconstructable at `812/1408 = 57.67%`; this is not Wave911 reconstruction. Active completion target: `1179/1179 current-risk focused rows reviewed or superseded with bounded static evidence`.

Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260606-231915_post_wave1200_residual_unwind_current_risk_verified`.

Boundary: this proves static compiler-unwind metadata/decompile/xref evidence only. Runtime cleanup behavior, runtime exception behavior, exact source-body identity, exact parent layouts, BEA patching behavior, rebuild parity, and no-noticeable-difference parity remain separate proof. Static target remains rebuild-grade static contracts and a rebuild-grade specification aiming at no noticeable difference.

Probe token anchor: Wave1200; wave1200-residual-unwind-current-risk-supersession; 1017/1179 = 86.26%; 147 residual compiler-unwind current-risk rows; current focused candidates: 1141; live regenerated current focused candidates: 1141; remaining active focused work: 162; current risk candidates: 6166; fresh Ghidra export; read-only supersession; no rename; no signature change; no comment change; no tag change; no function-boundary change; no executable-byte change; unique-address accounting; legacy additive counter is deprecated; 1048/1179; 26 duplicate-address overcount; Wave1145 arithmetic overcount: 5; Wave911 is historical-retired/non-reconstructable at 812/1408 = 57.67%; 0x005d1115 Unwind@005d1115; 0x005d3440 Unwind@005d3440; 0 / 0 / 0; 6411/6411 = 100.00%; 147 xref rows; 348 instruction rows; 147 decompile rows; [maintainer-local-ghidra-backup-root]\BEA_20260606-231915_post_wave1200_residual_unwind_current_risk_verified; static-reaudit-current-risk-ledger.json; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction; rebuild-grade static contracts; no noticeable difference; rebuild-grade specification; 1179/1179 current-risk focused rows reviewed or superseded with bounded static evidence.
