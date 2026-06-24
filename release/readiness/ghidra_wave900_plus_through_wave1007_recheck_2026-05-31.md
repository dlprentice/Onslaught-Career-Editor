# Ghidra Wave900+ Through Wave1007 Recheck Note

Status: PASS
Date: 2026-05-31
Scope: `ghidra-wave900-plus-through-wave1007-recheck`

Wave900-Wave1007 aggregate recheck extends the Wave900+ structural evidence gate after Wave1007 particle descriptor token-spine review. This is structural static evidence validation for the loaded Ghidra project and repo evidence surfaces, not runtime proof, exact source-layout proof, BEA patching proof, or rebuild parity.

Wave1007 anchor: `particle-descriptor-token-spine-review-wave1007`; `0x004c07f0 CPDSimpleSprite__WriteTokenFields`; `0x004c1970 CPDEmitter__WriteTokenFields`; `0x004c2220 CPDSelector__WriteTokenFields`; `0x004c2400 CPDColourRange__WriteTokenFields`; `0x004c2ca0 CPDShape__WriteTokenFields`; `0x004c3440 CPDTrail__WriteTokenFields`; `0x004c4920 CPDFunction__WriteTokenFields`; `0x004c49b0 CPDMesh__dtor_base`; `0x004c5410 CParticleDescriptor__Update`; `0x004c5730 CParticleDescriptor__Load`; `0x004c59e0 CPDPMesh__WriteTokenFields`.

Verified recheck result:

- Readiness notes: `110`
- Covered waves: `108`
- Package probe scripts: `106`
- Evidence bases: `106`
- Backup references: `108`
- Apply scripts: `33`
- Wave982-Wave1007 direct probes: `26` total, `1` current pass, `25` classified stale-current failures, `0` disallowed evidence or unclassified failures
- Current queue closure: `6223/6223 = 100.00%`
- Wave911 focused re-audit progress: `499/1408 = 35.44%`
- Expanded static surface progress: `676/1478 = 45.74%`
- Wave911 top-500 risk-ranked coverage: `398/500 = 79.60%`
- Verified Wave1007 backup: `G:\GhidraBackups\BEA_20260531-143106_post_wave1007_particle_descriptor_token_spine_review_verified`

The direct-probe stale-current classifications are expected because older focused probes still assert historical baton/current-doc totals that have intentionally rolled forward. The aggregate gate treats those as stale-current only when the line-level classifier finds no metadata, signature, tag, decompile, log, backup, lock, or unclassified evidence mismatch.

Boundary note: Wave1007 confirms static particle descriptor token-spine read-back coherence for the selected rows. Runtime particle loading/update/rendering behavior, exact source virtual names, concrete descriptor/token/particle/effect layouts, exact source-body identity, BEA patching, and rebuild parity remain separate proof.
