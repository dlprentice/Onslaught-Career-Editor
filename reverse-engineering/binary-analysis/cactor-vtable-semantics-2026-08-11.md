# `CActor` virtual-interface semantic crosswalk

Status: active, bounded semantic recovery
Last updated: 2026-08-11
Evidence: MEASURED — strict retail/demo RTTI, paired vtables, gapless bodies,
constants, fields, and calls; SOURCE — pinned `actor.h` and `actor.cpp`.
Verdict: all 18 uniquely `CActor`-owned targets have exact source/ABI
identities, independently preserved in the PC demo build.

Specimen: pristine PC retail `BEA.exe`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`;
PC demo `BEA.exe`, SHA-256
`d8637dd755b21c720c0cb8f71923f94d2a04a184d90f5343c2e868ce8606e5c2`.

## Result

Strict RTTI pairs the 29-slot secondary/render table at retail `0x005D83D4`
and demo `0x005D93D4`, plus the 71-slot primary table at retail `0x005D844C`
and demo `0x005D944C`. The paired structures identify every override by slot while
the retained source supplies the historical method declarations and bodies.

The owner cohort contains 18 targets, 2,835 retail body bytes, and 867 decoded
instructions. Fifty-five instructions differ in 90 raw bytes between builds;
all differences normalize to relocated addresses or displacements. Every pair
has zero normalized instruction differences.

The machine-readable result is
[`cactor-vtable-semantics-2026-08-11.tsv`](cactor-vtable-semantics-2026-08-11.tsv).
That 3,694-byte table has SHA-256
`04bc840d8904c527d1c04ab278419cc4309f8a6cf368f63caddfdeba7ce4188e`.
The broader independent comparison is
[`pc-demo-retail-virtual-target-map-2026-08-11.tsv`](pc-demo-retail-virtual-target-map-2026-08-11.tsv).

## Recovered layer

`CActor` adds the moving-object contract over `CComplexThing`:

- `Move` saves the old pose, integrates velocity, resolves terrain and water,
  applies slide/bounce behavior, records contacts, and updates spatial sectors;
- `HandleEvent` owns the full/low-fidelity move schedule, while the source-only
  `AddMoveEvent` and `LowFidelityMove` helpers explain its two event branches;
- current and old position/orientation form the released interpolation state
  used by the two secondary render-interface overrides;
- ground, water, and standing-object declarations are timestamp writes, with
  `IsOnGround` using the exact `< 0.15f` freshness test;
- `Teleport` updates sector membership, while `MoveTo` deliberately preserves
  the actor's old-position policy and delegates to the base implementation;
- `Stop` is the formerly anonymous slot 64 and zeros the velocity vector;
- the inline actor type override writes the combined actor/thing class mask.

The source also declares inline velocity, old-pose, `IsInWater`, and
`IsOnObject` accessors whose bodies are shared or non-virtual in this retail
layout. They are not duplicated in the 18-row unique-owner table. Downstream
unit, vehicle, projectile, and squad passes can now inherit these slot meanings
without re-inferring the actor ABI.
