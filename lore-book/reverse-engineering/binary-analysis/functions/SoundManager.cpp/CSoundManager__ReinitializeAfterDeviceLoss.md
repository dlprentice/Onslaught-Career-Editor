# CSoundManager__ReinitializeAfterDeviceLoss

> Address: `0x00517f10`

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** Yes (`void __thiscall CSoundManager__ReinitializeAfterDeviceLoss(void * this)`)
- **Verified vs Source:** Partial only. `references/Onslaught/SoundManager.cpp` confirms `CSoundManager::Reset` calls the platform sound reset path, but this retail helper performs a broader shutdown/reinit/reload sequence.

## Purpose
Reinitializes the `CSoundManager` instance and associated music/sample resources after sound-device loss or settings changes.

## Behavior Summary
- Traces DirectSound-buffer teardown and stops active sound streams.
- Shuts down global `MUSIC`.
- Stops message-box voice playback when a message box is active.
- Releases voice buffers through the `CSoundManager` instance.
- Reinitializes the PC sound device.
- Reinitializes `MUSIC` when global music is enabled.
- Reloads the compressed sample bank and refreshes existing sample definitions unless the reload-suppression flag is set.

## Evidence
- Callers load `ECX = 0x00896988` before entry, including `Audio__ReinitializeSoundAndRestoreMusic` and nearby raw config-change thunks.
- `0x00517f11` saves `ECX` into `ESI`; later calls reuse `ESI` as the sound-manager instance.
- Calls include `CSoundManager__StopAllStreams`, `CMusic__Shutdown`, `CMessageBox__StopVoicePlaybackIfNotInCutscene`, `CSoundManager__ReleaseAllVoiceBuffers`, `CPCSoundManager__Init`, `CMusic__Init`, `CSoundManager__LoadCompressedSampleBank`, and `CSoundManager__GetOrCreateSample`.

## Limits
Static retail-binary evidence only. Runtime audio behavior, exact source identity, concrete sound-manager/sample layouts, and rebuild parity remain unproven.
