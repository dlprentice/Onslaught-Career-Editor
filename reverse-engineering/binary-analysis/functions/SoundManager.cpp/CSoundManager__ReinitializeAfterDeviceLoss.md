# CSoundManager__ReinitializeAfterDeviceLoss

Status: independently rechecked instructions and bounded original execution
Last updated: 2026-09-20
Summary: sample deletion, music/device shutdown and conditional reinitialization; corrects stale stream-stop and voice-release identities.
Source File: no exact retained source body | Binary: pristine `BEA.exe.original.backup`.
Evidence: MEASURED — complete selected pristine bodies and original reset/shutdown execution; platform creation and real object lifetime remain intercepted.
Specimen: `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Address: `0x00517f10`

ECX is retained as the receiver. The body takes no stack argument, has no
success result and returns with `RET`. Its ordered calls are:

1. Trace at `00517f18`.
2. `004e06b0` at `00517f22` deletes the linked samples rooted at
   receiver `+0`. It is **DeleteAllSamples**, not StopAllStreams as the
   earlier note said. The independently inspected body follows sample `+0x74`,
   calls each nonnull object's vtable slot zero with argument 1, then clears
   the head; nested destructors remain owned hooks in the execution below.
3. Global music shutdown `004bb400`. Its body conditionally stops a playing
   stream, but invokes platform vtable slot `+4` unconditionally. A zeroed
   music object is therefore not a sufficient isolated-execution precondition.
4. If `008a9d84` is nonnull, call `004b8800` with that receiver.
5. DeviceShutdown `005171e0`, then device Init `005169b0` on the
   selected sound receiver. The earlier voice-release name at this call
   was misleading. The controls execute DeviceShutdown's two 64-slot arrays,
   release the 3D slot before its paired ordinary slot, clear each pointer, then
   release the device and destroy its wrapper. Init remains an explicit hook.
6. If Init's low return byte is zero, return immediately. Otherwise,
   music-enable global `00662dcc` conditionally admits `004bb380`.
7. Call compressed-bank helper `00517d00` with argument 1.
8. Only when `0066307c==0`, walk samples rooted at absolute global
   `00896988` and call `004e0a00` using each sample's name and
   `+0x6c` field with final argument 1. This last walk uses the canonical
   manager rather than an arbitrary selected receiver.

The [26 reset controls](../../../../VALIDATION.md#original-audio-reset-and-music-restoration--september-20)
match complete selected state and 625 ordered hook observations. They also retain
the original message helper: a nonzero cutscene word skips it; otherwise it
clears the message's voice byte and routes a retained voice event through
StopSound/deleting-destructor hooks before nulling the global event pointer.
The music Init body restores configured volume from the fixture and initializes
current/target fields; its platform hook supplies the owned new playlist.

The alternate receiver deliberately shares authored sample/device pointers with
the canonical manager. Its final refresh proves the absolute-list selection,
not valid lifetime after real destruction. Music Shutdown clears the list head
but leaves its old current-song pointer in the disabled/direct cases. Real
deallocation and subsequent pointer use remain untested.

These controls do not establish successful recovery, actual nested ownership,
filesystem effects or audible continuity. The compressed-bank hook is separate
from the [original bank admission/retry controls](../../../../VALIDATION.md#original-language-bank-admission-and-retry--september-20).
The caller [audio reset wrapper](Audio__ReinitializeSoundAndRestoreMusic.md)
continues after this function returns, including its early Init-failure return.

Private full-body disassemblies are `audio-00517f10.asm`,
`audio-004e06b0.asm` and `audio-004bb400.asm` under
`local-data/test-runs/save-startup-20260919/`. Original volume execution is
recorded separately in the [save/settings contract](../../save-options-static-review-2026-05-26.md#original-volume-application-and-save-composition).
