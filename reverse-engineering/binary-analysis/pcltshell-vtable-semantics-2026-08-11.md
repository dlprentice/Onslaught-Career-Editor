# `PCLTShell` virtual-interface semantic crosswalk

Status: active, bounded semantic recovery
Last updated: 2026-08-11
Evidence: MEASURED — strict retail/demo RTTI, paired vtables, gapless bodies,
calls, state writes, message constants, and Direct3D dispatch; SOURCE — pinned
`ltshell.h`, `ltshell.cpp`, `d3dapp.h`, and `d3dapp.cpp`; UNKNOWN — exact
source-revision identity for the released Direct3D 9 shell.
Verdict: all eight uniquely `PCLTShell`-owned virtual targets have recovered
interface identities and bounded released behavior.

Specimen: pristine PC retail `BEA.exe`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`;
PC demo `BEA.exe`, SHA-256
`d8637dd755b21c720c0cb8f71923f94d2a04a184d90f5343c2e868ce8606e5c2`.

## Result

Strict RTTI pairs the 14-slot retail table at `0x005E488C` with the demo table
at `0x005E588C`; their structural key is
`103093405e2f2ca7b627909db5b2ac66da531165b8e3ae5b683dc444eb681ccd`.
The eight unique shell targets contain 1,751 retail bytes and 560 decoded
instructions. One hundred instructions differ in 192 raw bytes between the
builds, while all eight pairs have zero normalized differences.

The machine-readable result is
[`pcltshell-vtable-semantics-2026-08-11.tsv`](pcltshell-vtable-semantics-2026-08-11.tsv).
That 2,187-byte table has SHA-256
`c1510d9baa0d6a633bf0d9514b7fc9ce3a5eb32070e1643181467ae2cffe7d1b`.
The independent pairing source is
[`pc-demo-retail-virtual-target-map-2026-08-11.tsv`](pc-demo-retail-virtual-target-map-2026-08-11.tsv).

## Recovered application-shell boundary

The released vtable order plus retained base declarations resolve the generic
`VFunc` labels to `InitDeviceObjects`, `RestoreDeviceObjects`,
`InvalidateDeviceObjects`, `DeleteDeviceObjects`, `FinalCleanup`, `Pause`, and
`MsgProc`; `ConfirmDevice` was already named. Their bodies recover the PC side
of another GDC-deck boundary:

- device creation selects PC renderer formats, creates retained presentation
  resources, walks the device-object registries, and brings up DirectInput;
- restore, invalidate, and delete are separate lifecycle passes over the two
  released device-object lists rather than one undifferentiated reset routine;
- deletion also frees joystick state, input ownership, particle surfaces, and
  the active-device flag;
- final cleanup clears the shell's running state;
- the released `Pause` override preserves the PC renderer's cached
  surface/texture state around pause transitions;
- `MsgProc` owns the Windows command, key-down, key-up, character, and mouse
  bridge before delegating other messages to `CD3DApplication`;
- `ConfirmDevice` rejects unsupported Direct3D capability combinations before
  the generic application creates the device.

The retained source snapshot uses Direct3D 8 types and does not contain the
released `PCLTShell::Pause` override, while the pristine retail executable uses
the later Direct3D 9 application path. Accordingly, the source proves class and
interface intent; released bytes prove the shipped implementation. The PC demo
then supplies an independently linked second witness: every one of these eight
released instruction streams remains identical after relocation normalization.

The other six table entries are inherited/shared implementations: three
return-zero callbacks, `CD3DApplication::Create`, the base window-adjustment
path, and one base lifecycle callback. They are deliberately not relabeled as
PC-shell-owned code. Actual device-loss timing, driver behavior, fullscreen
transitions, DirectInput hardware results, and rendered parity remain runtime
questions.
