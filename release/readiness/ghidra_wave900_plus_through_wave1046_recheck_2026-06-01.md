# Ghidra Wave900+ Through Wave1046 Recheck

Status: structural static evidence recheck passed
Date: 2026-06-01
Scope: Wave900-Wave1046

This note extends the Wave900+ recheck gate after Wave1046. It is a structural evidence gate over saved readiness notes, focused probes, ignored evidence bases, backup references, apply-log coverage for mutation waves, direct focused-probe classifications for Wave982-Wave1046, and current queue closure.

Validation result: PASS. The gate covered 149 readiness notes across 147 waves, 145 package probe scripts, 145 evidence bases, 147 backup references, 43 apply scripts, and current queue closure at `6246/6246 = 100.00%`. Direct Wave982-Wave1046 probe classification recorded 65 results with 1 direct pass, 64 classified stale-current-state or rolled-current-doc failures, and 0 disallowed evidence/unclassified failures.

Fresh validation command:

```powershell
npm run test:ghidra-wave900-plus-through-wave1046-recheck
```

Expected scope:

- Wave900-Wave981 remain covered by the earlier focused-probe sweep and evidence audit.
- Wave982-Wave1046 focused probes are rerun or classified by the current recheck gate.
- Wave910 and Wave911 remain queue/planning waves without per-wave Ghidra backup notes.
- Current live queue closure remains `6246/6246 = 100.00%`.

Wave1046 extension:

- Focused probe: `npm run test:ghidra-renderthing-crttree-review-wave1046`
- Readiness note: `release/readiness/ghidra_renderthing_crttree_review_wave1046_2026-06-01.md`
- Evidence base: `subagents/ghidra-static-reaudit/wave1046-renderthing-crttree-review`
- Verified backup: `G:\GhidraBackups\BEA_20260601-120449_post_wave1046_renderthing_crttree_review_verified`
- Mutation status: no mutation. Fresh evidence reconfirmed the selected `CRenderThing` / `CRTTree` rows against metadata, tags, xrefs, instructions, decompile, vtable slots, and context exports without changing Ghidra state.
- Progress accounting: Wave1046 targets are not Wave911 focused TSV rows, so Wave911 focused progress remains `735/1408 = 52.20%`; expanded static surface progress advances to `993/1509 = 65.81%`; top-500 risk-ranked coverage remains `500/500 = 100.00%`.

Boundary note: this recheck validates static evidence structure, backups, probe wiring, direct-probe classifications, and current queue closure. It does not prove runtime cutscene/tree/render behavior, exact `CRenderThing`/`CRTCutscene`/`CRTTree`/`CRTMesh`/resource/output-record layouts, exact source virtual names, `CSphere__RenderAnimatedRecursive` signature/layout, BEA patching, gameplay outcomes, or rebuild parity.

Probe token anchor: Wave1046; renderthing-crttree-review-wave1046; 0x004db880 CRenderThing__ForwardSlot26ToChildSlot68; 0x004dbb80 CRenderThing__VFunc_07_ClearRenderOutputs; 0x004dbbe0 CRenderThing__VFunc_08_ClearVec3; 0x004dbd20 CRenderThing__dtor; 0x004dbd50 CRenderThing__scalar_deleting_dtor; 0x004dd960 CRTTree__VFuncSlot02_BuildRenderOutputs; 0x004de050 CRTTree__VFuncSlot06_GetResourceScalar164; 0x004de060 SharedVFunc__ReturnResourceField150_004de060; 0x005dea38; 0x005deaac; 0x005deb1c; 0x005deb9c; DAT_0083cd58; 0x0083ccd8; 0x004b6260 CSphere__RenderAnimatedRecursive; 735/1408 = 52.20%; 993/1509 = 65.81%; 500/500 = 100.00%; 6246/6246 = 100.00%; G:\GhidraBackups\BEA_20260601-120449_post_wave1046_renderthing_crttree_review_verified; no mutation.
