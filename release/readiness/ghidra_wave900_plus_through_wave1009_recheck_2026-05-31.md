# Ghidra Wave900+ Through Wave1009 Recheck Note

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 live correction closeout:** Historical record; `0x00534ac0` comment correction. The original text below remains provenance rather than current semantic authority. It is superseded only where confirmed. Use the [closeout](../../reverse-engineering/binary-analysis/ghidra-full-reaudit-closeout-2026-07-13.md); final per-address decisions and exact before/after metadata are in `reverse-engineering/binary-analysis/ghidra-reviewed-correction-decisions-2026-07-13.jsonl` and `reverse-engineering/binary-analysis/ghidra-reviewed-correction-plan-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

Status: PASS
Date: 2026-05-31
Scope: `ghidra-wave900-plus-through-wave1009-recheck`

Wave900-Wave1009 aggregate recheck extends the Wave900+ structural evidence gate after Wave1009 geometry / guide / heightfield spine boundary recovery. This is structural static evidence validation for the loaded Ghidra project and repo evidence surfaces, not runtime proof, exact source-layout proof, BEA patching proof, or rebuild parity.

Wave1009 anchor: `geometry-guide-heightfield-spine-review-wave1009`; `0x0047eb80 CStaticShadows__SampleShadowHeightBilinear`; `0x00448580 CDropshipAI__VFunc_09_00448580`; `0x00448930 CDropshipGuide__VFunc_03_00448930`; `0x004dfaa0 VFuncSlot_09_004dfaa0`; `0x004e9600 CSquadNormal__VFunc_20_004e9600`; `0x004e96f0 CSquadNormal__VFunc_21_004e96f0`; `0x004e9f00 CSquadNormal__VFunc_52_004e9f00`; `0x004eaae0 CRelaxedSquad__VFunc_07_004eaae0`; `0x004f0e40 CTentacle__VFunc_22_004f0e40`; `0x0050a3a0 CWingmanStart__VFunc_09_0050a3a0`; `0x00534ac0 ScriptCommand__SampleStaticShadowHeight_00534ac0`.

Verified recheck result:

- Readiness notes: `112`
- Covered waves: `110`
- Package probe scripts: `108`
- Evidence bases: `108`
- Backup references: `110`
- Apply scripts: `34`
- Wave982-Wave1009 direct probes: `28` total, `1` current pass, `27` classified stale-current failures, `0` disallowed evidence or unclassified failures
- Current queue closure: `6233/6233 = 100.00%`
- Wave911 focused re-audit progress: `499/1408 = 35.44%`
- Expanded static surface progress: `694/1488 = 46.64%`
- Wave911 top-500 risk-ranked coverage: `403/500 = 80.60%`
- Verified Wave1009 backup: `[maintainer-local-ghidra-backup-root]\BEA_20260531-155648_post_wave1009_geometry_guide_heightfield_spine_review_verified`

The direct-probe stale-current classifications are expected because older focused probes still assert historical baton/current-doc totals that have intentionally rolled forward. The aggregate gate treats those as stale-current only when the line-level classifier finds no metadata, signature, tag, decompile, log, backup, lock, or unclassified evidence mismatch.

Boundary note: Wave1009 confirms saved static boundary/name/signature/comment/tag coherence for the ten recovered DATA-backed static-shadow caller rows plus the carried-forward geometry / guide / heightfield anchors. Runtime dropship, squad, tentacle, wingman, MissionScript, terrain, or shadow behavior; exact source method identity; concrete layouts; BEA patching; and rebuild parity remain separate proof.
