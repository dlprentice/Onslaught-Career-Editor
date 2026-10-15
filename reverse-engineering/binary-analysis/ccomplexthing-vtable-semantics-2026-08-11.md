# `CComplexThing` virtual-interface semantic crosswalk

Status: active, bounded semantic recovery
Last updated: 2026-08-11
Evidence: MEASURED — strict retail/demo RTTI, paired vtables, gapless bodies,
constants, and calls; SOURCE — pinned `thing.h` and `thing.cpp`; UNKNOWN — one
retail render-interface property absent from the retained source declaration.
Verdict: 21 of 22 uniquely owned targets now have exact source/ABI identities;
the last has an exact animation-field contract and an open historical name.

Specimen: pristine PC retail `BEA.exe`, SHA-256 `74154bfae14ddc8e…`;
PC demo `BEA.exe`, SHA-256 `d8637dd755b21c720…`. Full hashes are pinned in
[`DEMO_VS_RETAIL.md`](../DEMO_VS_RETAIL.md).

## Result

Strict RTTI pairs the 29-slot secondary table at retail `0x005DF70C` / demo
`0x005E070C` (structural key
`0744acaaea6e2c59e2e7239d132f5d6d3f8058c6470bb29d6279916d2ab3084d`)
and the 66-slot primary table at retail `0x005DF784` / demo `0x005E0784`
(key `5225498156d68dc6633cdbf451ce113461c23f9b44c88fe32edc0fdccf16d3d8`).

The owner cohort contains 22 targets, 1,300 retail body bytes, and 453 decoded
instructions. Twelve targets contain 44 raw-different instructions (85 bytes)
in the demo; every pair has zero normalized differences.

The machine-readable result is
[`ccomplexthing-vtable-semantics-2026-08-11.tsv`](ccomplexthing-vtable-semantics-2026-08-11.tsv).
That 4,369-byte table has SHA-256
`c77047776dea687cd57e69b2c92d64fa7f83acf9dd6bf9565573d0a35eafd0cb`.
The broader build comparison is
[`pc-demo-retail-virtual-target-map-2026-08-11.tsv`](pc-demo-retail-virtual-target-map-2026-08-11.tsv).

## Recovered layer

This pass identifies the layer `CComplexThing` adds over `CThing`:

- orientation is shared by render, sound, old-orientation, and teleport paths;
- animation supplies real index, render frame, mode changes, and completion;
- name ownership is a real allocation/registration path, not a field getter;
- mission-script integration extends initialization, variables, death,
  shutdown, and events;
- motion-controller and objective projections occupy their inherited slots;
- `GoToPoint` is the intentional base no-op with its full FVector/Boolean ABI.

Several old labels were only offset descriptions. `0x004014D0` is
`GetRealAnimIndex`; `0x00401510` is `GetName`; `0x004F45C0` is
`GetRenderFrame`. `0x0043EA20` is compiler-folded across
`GetSoundOrientation` and `GetOldOrientation`, while secondary target
`0x004040D0` is `GetRenderOrientation` with the adjusted `this` pointer.

## Deliberate open name

Secondary render slot 22 (`0x00401500`) reads the animation pointer and returns
its field `+0x14`, or zero when no animation exists. The retained GPL header
does not declare a matching override at that ABI position. The table therefore
records the exact behavior and leaves the historical name open instead of
forcing a nearby render-interface label from a different source revision.

With `CThing`, `CComplexThing`, `CUnit`, and `CBattleEngine` now aligned, the
next subclass passes can inherit typed slots rather than re-derive the base ABI
for every actor, squad, building, and projectile.
