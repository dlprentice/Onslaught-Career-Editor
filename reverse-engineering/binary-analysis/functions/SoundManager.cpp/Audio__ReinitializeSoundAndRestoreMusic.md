# Audio__ReinitializeSoundAndRestoreMusic

Status: independently rechecked static ordering; controlled execution pending
Last updated: 2026-09-20
Summary: unconditional sound reinitialization followed by low-byte-selected music restoration, without a device-success gate.
Source File: no exact retained source body | Binary: pristine `BEA.exe.original.backup`.
Evidence: MEASURED — complete pristine wrapper and reinitializer instructions; restoration/playback remains unexecuted here.
Specimen: `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Address: `0x004cddf0`

The stack argument selects restoration context; caller cleanup is required.
The wrapper always first calls `00517f10` with sound receiver `00896988`.
It then tests only the argument's low byte at `004cddfa..004cddfe`:

- Nonzero: if `00662dcc` is nonzero, call `CMusic__PlaySelection` at
  `004bb8c0` with receiver `00889a48` and arguments `(0,0)`.
- Zero: tail-jump to `CGame__PlayMusicForCurrentLevel` at `0046dc00`
  with receiver `008a9a98`. The nested method's own admission remains
  separate from this wrapper.

There is no success check between reinitialization and restoration. In
particular, the reinitializer's early device-Init-failure return does not suppress
the wrapper's subsequent restoration attempt. This is static control-flow
evidence, not a reproduced device failure or successful playback.

OptionsTail_Read passes 1 when its audio-setting comparison selects reset;
the existing [loader controls](../../save-options-static-review-2026-05-26.md)
observe that call at an explicit boundary. They do not execute this wrapper.
Nearby options thunks and their saved boundaries are historical leads for later
inspection, not revalidated by this note.

See [reinitializer ordering](CSoundManager__ReinitializeAfterDeviceLoss.md).
Private selected instructions are `audio-004cddf0.asm` under
`local-data/test-runs/save-startup-20260919/`.
