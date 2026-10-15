# Audio__ReinitializeSoundAndRestoreMusic

Status: independently rechecked instructions and bounded original execution
Last updated: 2026-09-20
Summary: unconditional sound reinitialization followed by low-byte-selected music restoration, without a device-success gate.
Source File: no exact retained source body | Binary: pristine `BEA.exe.original.backup`.
Evidence: MEASURED — complete pristine instructions and original reset/selection execution; device and playback services intercepted.
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

The [26 original reset controls](../../../../VALIDATION.md#original-audio-reset-and-music-restoration--september-20)
also execute the reinitializer, music shutdown/Init/selection and current-level
wrapper. A supplied device-Init return of 0 or `0x100` exits reinitialization
early but still permits enabled music selection. The original selection body
then writes mode 3, the requested category, null current song and configured
target volume; it makes no playback call with the empty playlist.
No actual device failure or successful recovery is claimed.

Wrapper argument `0x100` takes the level route, while `0x101` takes the
frontend route. The nested level helper independently checks the full
music-enable word, selects category 2 for level 100 and category 4 otherwise.
The tested Level 110 case uses the latter route. These categories select
playlist policy, not literal track numbers.

OptionsTail_Read passes 1 when its audio-setting comparison selects reset;
the existing [loader controls](../../save-options-static-review-2026-05-26.md)
observe that call at an explicit boundary. They do not yet compose this wrapper
inside Load; the new reset controls invoke it separately.
Nearby options thunks and their saved boundaries are historical leads for later
inspection, not revalidated by this note.

See [reinitializer ordering](CSoundManager__ReinitializeAfterDeviceLoss.md).
Private selected instructions are `audio-004cddf0.asm` under
`local-data/test-runs/save-startup-20260919/`.
