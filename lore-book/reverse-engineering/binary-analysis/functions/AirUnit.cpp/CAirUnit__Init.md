# CAirUnit__Init

> Address: 0x00402ad0 | Source: AirUnit.cpp (source file not present in `references/Onslaught/` snapshot)

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** Yes (headless postscript + read-back verified, 2026-03-01)
- **Verified vs Source:** Partial (behavior-level; source file is not present in current `references/Onslaught/` snapshot)

## Purpose

Initialize an air unit by calling the base CUnit constructor and creating aircraft-specific visual effects. Creates "Trail" effects (exhaust contrails) and "Engine" effects (thrust particles) in two separate loops.

Wave822 particle manager owner links (`particle-manager-owner-links-wave822`) corrected the shared registration helper from old `CWorldPhysicsManager__PushNodeGlobalList` to `0x004cb040 ParticleEffectLink__PushGlobalList`. The same static read-back wave also hardened `0x004caf30 CParticleManager__ClearParticleOwnerBacklinks`, `0x004cb080 CParticleManager__PruneDeadOwnerLinks`, and `0x004cbc60 CParticleManager__UpdateRenderNodesAndResetState`. Queue after Wave822 is `5626/6098 = 92.26%`; next raw commentless row is `0x004cd7a0 CWorldPhysicsManager__FindNodeByNameGE`; verified backup `[maintainer-local-ghidra-backup-root]\BEA_20260524-180249_post_wave822_particle_manager_owner_links_verified`. Exact effect-handle/link-node/render-node/owner layouts, exact source-body identity, runtime particle shutdown behavior, runtime particle/effect behavior, runtime render behavior, BEA patching, and rebuild parity remain deferred.

## Signature
```c
void __thiscall CAirUnit__Init(void * this, void * init);
```

Read-back verified in `scratch/program_2026-03-01/phase5_signature_readback/index.tsv` and refreshed by Wave1185 post exports (`status=OK`).

## Responsibilities

- **Base class init** - Calls `CUnit__Init(init)` first
- **Trail effects loop** - Creates visual trail effects (line 42)
- **Engine effects loop** - Creates engine glow/thrust effects (line 54)
- **Memory allocation** - Uses OID__AllocObject with debug info
- **Effect registration** - Calls `ParticleEffectLink__PushGlobalList` (`0x004cb040`), `CSPtrSet__AddToTail` (`0x004e5b20`), CSPtrSet__AddToHead

## Key Observations

- **Two effect types** - "Trail" and "Engine" strings at 0x00622d14 and 0x00622cec
- **Config at 0x3bc** - Reads effect data from configuration offset
- **Exception safe** - Unwind handlers for both effect loops
- **~600 bytes** - Moderately sized function

## Decompiled Pseudocode

```c
void CAirUnit::Init(void * init) {
    // Call base class constructor
    CUnit__Init(init);

    // Initialize air unit-specific properties from config
    void* config = this->config_3bc;

    // First loop: Create Trail effects (line 42)
    for each trail_effect in config->trails {
        void* effect = MemAlloc(size, type, "AirUnit.cpp", 42);
        ParticleEffectLink__PushGlobalList(effect);      // Register effect-owner link globally
        CSPtrSet__AddToTail(effect); // Register effect (set pointer is in ECX)
    }

    // Second loop: Create Engine effects (line 54)
    for each engine_effect in config->engines {
        void* effect = MemAlloc(size, type, "AirUnit.cpp", 54);
        ParticleEffectLink__PushGlobalList(effect);      // Register effect-owner link globally
        CSPtrSet__AddToHead(effect);      // Final setup
    }
}
```

## Notes

- Discovered via xref to debug path string at 0x00622cf4
- Trail effects create visible exhaust trails behind aircraft
- Engine effects create thrust glow and particle emissions
- Consider finding vtable xrefs to discover more CAirUnit methods

## Wave1185 Current-Risk Normalization

Wave1185 (`wave1185-airunit-init-current-risk-review`) accounts for `1 AirUnit init lifecycle current-risk row` with fresh Ghidra export evidence and saved comment/tag normalization. Static closure remains `6411/6411 = 100.00%` with `0 / 0 / 0` debt; Wave1108 current focused accounting is `783/1179 = 66.41%`; current focused candidates: 1177; live regenerated current focused candidates: 1177; remaining active focused work: 396; current risk candidates: 6166; fresh Ghidra export; comment/tag normalization; `updated=1 skipped=0`; `comment_only_updated=1`; `tags_added=13`; final dry updated=0 skipped=1; no rename; no signature change; no function-boundary change; no executable-byte change; Codex read-only consult used; no Cursor/Composer. Evidence anchors: `CAirUnit__Init`, `CUnit__Init`, `CCarrier__Init`, `CDropship__Init`, `CPlane__Init`, `CGroundAttackAircraft__Init`, aircraft vtable DATA refs 0x005e3548/0x005e379c, `Trail`, `Engine`, `0x00622d14`, and `0x00622cec`; `8 xref rows`; `165 instruction rows`; `1 decompile row`; backup `[maintainer-local-ghidra-backup-root]\BEA_20260606-134914_post_wave1185_airunit_init_current_risk_review_verified`; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction; rebuild-grade static contracts for a future clean-room implementation aiming at no noticeable difference remain the static target.

Probe token anchor: Wave1185; wave1185-airunit-init-current-risk-review; 783/1179 = 66.41%; 1 AirUnit init lifecycle current-risk row; current focused candidates: 1177; live regenerated current focused candidates: 1177; remaining active focused work: 396; current risk candidates: 6166; fresh Ghidra export; comment/tag normalization; updated=1 skipped=0; comment_only_updated=1; tags_added=13; final dry updated=0 skipped=1; no rename; no signature change; no function-boundary change; no executable-byte change; Codex read-only consult used; no Cursor/Composer; CAirUnit__Init; CUnit__Init; CCarrier__Init; CDropship__Init; CPlane__Init; CGroundAttackAircraft__Init; aircraft vtable DATA refs 0x005e3548/0x005e379c; Trail; Engine; 0x00622d14; 0x00622cec; 0 / 0 / 0; 6411/6411 = 100.00%; 8 xref rows; 165 instruction rows; 1 decompile row; [maintainer-local-ghidra-backup-root]\BEA_20260606-134914_post_wave1185_airunit_init_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction; rebuild-grade static contracts; no noticeable difference.

## Related Functions

- [CUnit__Init](../Unit.cpp/CUnit__Init.md) - Base class initialization
- ParticleEffectLink__PushGlobalList - Effect-owner link global registration
- CSPtrSet__AddToTail - Effect registration (set insert)
- CSPtrSet__AddToHead - Final effect setup
- OID__FreeObject_Callback - Exception cleanup/deallocation

---
*Discovered via Phase 1 xref analysis (Dec 2025)*
