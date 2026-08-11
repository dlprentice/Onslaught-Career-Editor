# `CPCController` platform-interface semantic crosswalk

Status: active, bounded semantic recovery
Last updated: 2026-08-11
Evidence: MEASURED — strict retail/demo RTTI, paired vtables, gapless bodies,
calls, globals, and constants; SOURCE — pinned `Controller.h`,
`PCController.h`, `PCController.cpp`, and `ltshell.h`; UNKNOWN — historical
names for three retail slots absent from the retained source revision.
Verdict: all 15 uniquely `CPCController`-owned targets have exact behavior;
12 retain source/ABI names and three are bounded retail interface extensions.

Specimen: pristine PC retail `BEA.exe`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`;
PC demo `BEA.exe`, SHA-256
`d8637dd755b21c720c0cb8f71923f94d2a04a184d90f5343c2e868ce8606e5c2`.

## Result

Strict RTTI pairs the 18-slot retail table at `0x005E48E0` with the demo table
at `0x005E58E0`; their structural key is
`57fcbb3e37307db044a499ef0d1fe2b32271f0948690fb669a0857459db62240`.
The 15 uniquely PC-owned targets contain 679 retail bytes and 199 decoded
instructions. Forty-five instructions differ in 74 raw bytes between the
builds, while all 15 pairs have zero normalized differences.

The machine-readable result is
[`cpccontroller-vtable-semantics-2026-08-11.tsv`](cpccontroller-vtable-semantics-2026-08-11.tsv).
That 3,375-byte table has SHA-256
`7a7e74803b48071d874ef99de3b582997e0e40be717ce2cf10709071b29485a2`.
The broader independent comparison is
[`pc-demo-retail-virtual-target-map-2026-08-11.tsv`](pc-demo-retail-virtual-target-map-2026-08-11.tsv).

## Recovered platform boundary

This table is a literal instance of the shared/platform split documented in
Lost Toys' 2002 GDC presentation. Shared `CController` owns mapping, repeat,
record/playback orchestration, and delivery to `IController`; `CPCController`
adapts PC input primitives into that interface:

- DirectInput joystick X/Y/Z axes are normalized into the shared `[-1, 1]`
  convention, with right Y using the released `32768` centre/range law;
- button once/on/release wrappers delegate to the current/old DirectInput
  button-state helpers;
- keyboard once/on wrappers delegate to the global platform object;
- record/read serialize the three digital words and four analogue floats in
  source order, with read closing playback at end-of-file;
- the two retail-only POV slots return `sin(angle)` and `-cos(angle)` from the
  DirectInput hundredths-of-a-degree value, or zero for the `0xFFFF` neutral
  sentinel;
- the remaining retail-only key slot returns one byte from the platform's
  third per-key state table. Its state transition meaning and historical name
  remain open because the retained header declares only key-once and key-on.

The complete table also contains three inherited/shared targets—no-op device
vibration, `Flush`, and `DoMappings`—which are not duplicated in the 15-row
unique-owner result. This distinction prevents platform-neutral controller
logic from being mislabeled as PC implementation code.
