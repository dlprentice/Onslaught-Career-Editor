# Ghidra CPDSimpleSprite Distance Burst Tint Review Wave963

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 live correction closeout:** Historical record; `0x004c8060` comment correction. The original text below remains provenance rather than current semantic authority. It is superseded only where confirmed. Use the [closeout](../../reverse-engineering/binary-analysis/ghidra-full-reaudit-closeout-2026-07-13.md); final per-address decisions and exact before/after metadata are in `reverse-engineering/binary-analysis/ghidra-reviewed-correction-decisions-2026-07-13.jsonl` and `reverse-engineering/binary-analysis/ghidra-reviewed-correction-plan-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

Status: bounded static read-only review PASS
Date: 2026-05-28
Tag: `cpdsimplesprite-distance-burst-tint-review-wave963`

Wave963 re-reviewed the CPDSimpleSprite distance-derived burst-count and tint/fade bridge after the Wave462 particle sprite/render correction, Wave821 expression/noise hardening, and Wave867 CVBufTexture cursor hardening. The wave checked two primary Wave911 focused candidates plus adjacent sprite expression, render-list, atlas/noise, color, inverse-lerp, and vertex-cursor context with fresh serialized Ghidra exports. No mutation was needed: the saved names, signatures, comments, and tags remain consistent with the current static evidence. The pass made no rename, no signature change, no function-boundary change, no executable-byte change, and did not launch BEA.

## Scope

Primary Wave911 candidates:

| Address | Saved name | Result |
| --- | --- | --- |
| `0x004c35d0` | `CEngine__ConfigureParticleBurstForDistance` | Read-only PASS; still writes particle resource count at `particle+0x80`, optionally derives it from distance against parent transform fields, calls `CParticleManager__SetParticleResource(count * 0x28)`, and initializes resource records under `particle+0x88`. |
| `0x004c8060` | `CEngine__ComputeSpriteTintByDistance` | Read-only PASS; still computes packed sprite tint/alpha from expression color curves plus distance/age fade selectors and packed-channel output modes. |

Context anchors re-read: `0x004c0c70 CPDSimpleSprite__EvalExpressionNode`, `0x004c14f0 CPDSimpleSprite__VFunc_10_004c14f0`, `0x004c5c50 CPDSimpleSprite__BuildUvAtlasBuckets`, `0x004c5d50 CPDSimpleSprite__ProcessAndRenderSpriteList`, `0x004c7950 CPDSimpleSprite__EvaluateCurveDrivenScale`, `0x004c7db0 CPDSimpleSprite__InitNoiseTableOnce`, `0x004c8040 CPDSimpleSprite__VFunc_23_004c8040`, `0x004cab30 Color32__LerpArgb`, `0x004cac40 Math__InvLerpClamp01`, and `0x00550200 CVBufTexture__GetVertexPtrAt`.

## Evidence

Fresh serialized Ghidra exports under `subagents/ghidra-static-reaudit/wave963-cpdsimplesprite-distance-burst-tint-review`:

- `12` metadata rows, `12` tag rows, `30` xref rows, `1260` around-address instruction rows, `3407` function-body instruction rows, and `12` decompile-index rows.
- Xrefs tie `0x004c35d0` to the adjacent sprite/burst setup callsite at `0x004c36d5`, `0x004c8060` to two sprite-path callsites at `0x004c8a21` and `0x004c8b02`, `0x004c5d50` to `0x004c8056 CPDSimpleSprite__VFunc_23_004c8040`, `0x004c7950` to `0x004c74f0 CPDSimpleSprite__ProcessAndRenderSpriteList`, and `0x00550200` to CPDSimpleSprite vertex-cursor callsites `0x004c767b` and `0x004c8a09`.
- Instruction evidence for `0x004c35d0` includes `0x004c3645 MOV [ESI + 0x80], ECX`, `0x004c3665 CALL 0x004caed0`, `0x004c367c ADD EAX, 0x20`, `0x004c3686 MOV [EAX], 0x3e4ccccd`, and `0x004c369e RET 0x4`.
- Instruction evidence for `0x004c8060` includes `0x004c8088 FIDIV [EDI + 0x80]`, repeated expression evaluator calls through `0x004c10c0` from fields such as `+0x5c`, `+0x6c`, `+0x8c`, `+0x94`, and `+0x9c`, selector loads at `+0xa4` / `+0xa8`, and `RET 0xc` exits.
- `references/Onslaught` contains high-level `CParticleDescriptor` usage in `BattleEngine.cpp`, `BattleEngine.h`, `DXEngine.h`, and `PCEngine.cpp`, but no matching `CPDSimpleSprite` / `ParticleDescriptor.cpp` implementation body in the current source snapshot. The saved `CEngine__` owner-prefix labels therefore remain legacy static labels, not exact source-owner proof.

Verified Ghidra backup:

```text
[maintainer-local-ghidra-backup-root]\BEA_20260528-135208_post_wave963_cpdsimplesprite_distance_burst_tint_review_verified
```

Backup summary: `19` files, `173542279` bytes, `DiffCount=0`.

Wave911 focused re-audit progress after Wave963: `311/1408 = 22.09%`.
Static export-contract function-quality closure remains `6152/6152 = 100.00%`.

Probe anchor: Wave963; cpdsimplesprite-distance-burst-tint-review-wave963; 0x004c35d0 CEngine__ConfigureParticleBurstForDistance; 0x004c8060 CEngine__ComputeSpriteTintByDistance; 0x004c5d50 CPDSimpleSprite__ProcessAndRenderSpriteList; 0x004c8040 CPDSimpleSprite__VFunc_23_004c8040; 0x004c3645 MOV [ESI + 0x80], ECX; 0x004c3665 CALL 0x004caed0; 0x004c8088 FIDIV [EDI + 0x80]; 0x004c80e7 CALL 0x004c10c0; 0x004c767b CVBufTexture__GetVertexPtrAt; 311/1408 = 22.09%; 6152/6152 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260528-135208_post_wave963_cpdsimplesprite_distance_burst_tint_review_verified; no mutation.

## Boundary

This wave proves only saved static retail Ghidra evidence tying the cluster to CPDSimpleSprite resource-count, expression/noise, tint/fade, render-list, and CVBufTexture vertex-cursor paths. Runtime particle rendering behavior, concrete descriptor/particle/CVBufTexture layouts, exact source-owner or source-body identity, visual output, BEA patching, and rebuild parity remain separate proof.
