# CTree__UpdateFallingTree

| Property | Value |
| --- | --- |
| Address | `0x004f6b80` |
| Saved signature | `void __fastcall CTree__UpdateFallingTree(void * this)` |
| Wave | Wave520 CTree static re-audit |

Updates the falling-tree data at `this+0x48`. The body copies the current matrix to the previous-matrix slot, traces downward against the heightfield while velocity is positive, spawns the `"Tree Ground Hit Effect"` particle on sufficiently strong ground impact, damps/reverses velocity on contact, settles to `DAT_00672fd0` and schedules event `0x7d2` when motion falls below threshold, otherwise integrates angle/velocity, rebuilds the rotation matrix, writes the current matrix, and reschedules event `3000`.

Evidence: calls from `CTree__CreateFallingTree` and recovered `CTree__HandleEvent`, post decompile tokens `CHeightField__TraceLineAgainstHeightfield`, `s_Tree_Ground_Hit_Effect_00633aa0`, `0x7d2`, and `CEventManager__AddEvent_AtTime`, plus Wave520 probe coverage.

Claim boundary: static retail-binary evidence only. Exact source identity, concrete layouts, runtime particle/physics behavior, BEA patching, and rebuild parity remain unproven.
