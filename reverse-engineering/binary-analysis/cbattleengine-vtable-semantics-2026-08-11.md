# `CBattleEngine` virtual-interface semantic crosswalk

Status: active, bounded semantic recovery  
Last updated: 2026-08-11  
Evidence: MEASURED — strict retail/demo RTTI, vtables, gapless decoded
function bodies, strings, constants, and direct calls; SOURCE — pinned
`BattleEngine.h` and `BattleEngine.cpp`; UNKNOWN — runtime path coverage and
the behavior explicitly left outside this owner pass.  
Verdict: all 37 targets owned uniquely by `CBattleEngine` have the same
instruction, branch, register, and literal shape in the independently linked
PC demo after address/displacement normalization. Every provisional owner name
in this cohort now has a source or compiler-ABI identity.

Specimen: pristine PC retail `BEA.exe`, SHA-256 `74154bfae14ddc8e…`;
PC demo `BEA.exe`, SHA-256 `d8637dd755b21c720…`. Full hashes are pinned in
[`DEMO_VS_RETAIL.md`](../DEMO_VS_RETAIL.md).

## Result

Strict RTTI pairs both Battle Engine tables without using addresses or names:

| Table | Retail | Demo | Slots | Structural key |
| --- | --- | --- | ---: | --- |
| Secondary render-facing table | `0x005D894C` | `0x005D994C` | 29 | `9d770f1e8c938ba5d305cfb43ee0151bfd5c8dbd8c57a6cd0908d1065faee7f6` |
| Primary `CBattleEngine` table | `0x005D89C4` | `0x005D99C4` | 118 | `b1305342f094ba6210e0d5f7da3b213eadd4424d1edcea08a4fea69b214e5cc7` |

The 37-target semantic-owner cohort contains 15,082 retail body bytes and
4,138 decoded instructions. Thirty-two bodies have 549 raw-different
instructions (782 bytes) in the demo, all caused by relocated calls, globals,
strings, or displacements. All 37 have zero normalized instruction differences.
This independently corroborates the released PC bodies; it does not claim that
either build executed every path.

The complete result is machine-readable in
[`cbattleengine-vtable-semantics-2026-08-11.tsv`](cbattleengine-vtable-semantics-2026-08-11.tsv).
That 7,602-byte table has SHA-256
`1bf959a26bc390b8b6d3dfb44eef543b64d2d93839dfc5efe2356314fc429e4e`.
The full 2,127-target comparison remains in
[`pc-demo-retail-virtual-target-map-2026-08-11.tsv`](pc-demo-retail-virtual-target-map-2026-08-11.tsv).

## Provisional names replaced

The most consequential corrections are:

| Retail target | Old current label | Source/ABI identity | Decisive join |
| --- | --- | --- | --- |
| `0x00406040` | `CBattleEngine__GetTrackedPositionX_00406040` | `GetMaxLife` / `GetInitialLife` | Both source methods return `mConfiguration->mLife`; MSVC folded the identical bodies. The compass calls are health/life consumers, not proof of compass ownership. |
| `0x00408150` | `ProcessStateSwapAndDeathChecks` | `DeclareInWater` | Mesh-state fixup, dying explode/shutdown path, and water-altitude death gate match the source body in order. |
| `0x00409DE0` | `VFunc_25` | `GetLocalLastFrameMovement` | Returns superclass movement minus `mStandingOnObjectMovement`. |
| `0x0040A560` | `VFunc_101` | `ConfirmedKill` | Requires the killed unit's Muspell allegiance, then calls the player's `KilledEnemyThing`. |
| `0x0040C380` | `VFunc_117` | `GetCurrentWeapon` | State 3 tail-dispatches to the jet part; all other states dispatch to the walker part. |
| `0x0040C720` | `ResetAndSetActiveReader` | `DeclareOnObject` | Mesh-state fixup, standing-object reader assignment, then superclass callback. |
| `0x0040C750` | `VFunc_68` | `DeclareOnGround` | Exact dash exemption, impact-damage projection, and jet damping body. |
| `0x0040D530` | `VFunc_36` | `Render` | Stealth alpha, cloaked flag, first-person visibility gate, superclass render, alpha reset. |
| `0x0040DF80` | `VFunc_16` | `GetRadius` | Exact multiplayer `1.0f` versus single-player `0.4f` law. |
| `0x0040E7D0` | `VFunc_104` | `CanBeLocked` | Exact stealth, jet special-move, and walker dash/special-move rejection gates. |
| `0x0040E8E0` | `IsNearGroundByTerrainProbe` | `GetThreat` | The source's terrain-height/`2.0f` gate and `5.0f` result. |
| `0x0040E910` | `GetGroundedControlFactor` | `GetImportance` | The source's on-ground and not-on-object predicate and `5.0f` result. |

The two Battle Engine-owned entries in the secondary table are also no longer
anonymous: slot 0 is `GetRenderPos` (`0x00406050`) and slot 1 is
`GetRenderOrientation` (`0x004060B0`). Their adjusted `this` pointer and their
walker/morph transforms match the source implementations.

## Shared and folded implementations

The 37-target count is an ownership partition, not the whole Battle Engine
interface. Some Battle Engine semantics use code folded with other classes.
For example, the secondary render-facing slot 25 points at `0x0040AC30` for
`GetRequiresPolyBucket`; the source and body reduce it to the multiplayer
predicate. Inline constant methods such as `IsAThreat` and `BounceFactor` can
likewise share compiler-folded targets.

Conversely, one address may represent more than one source method. Both
`CBattleEngine::GetMaxLife` and `CBattleEngine::GetInitialLife` compile to
`0x00406040`. A single global rename to only one of them would discard real
source identity. As in the `CUnit` pass, semantic truth belongs first to
`(class, vtable, slot)` and only secondarily to an address label.

## What this closes and what it does not

This pass closes the source identity of the owner block, including lifecycle,
movement, collision, target/weapon selection, launch placement, rendering,
damage, terminal events, and lockability. It also gives recursive discovery a
typed surface: callers of slots 25, 68–70, 75, 78–81, 101–104, and 117 can now
be reasoned about as methods instead of offsets.

It does not elevate static cross-build agreement to runtime coverage, prove
every structure field name, or claim that the Godot rebuild implements every
branch. Those questions should now be attacked at the subsystem boundary—one
movement, weapon, render, or terminal chain at a time—rather than repeatedly
re-auditing the 37 function envelopes.
