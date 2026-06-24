# SoundManager.cpp Functions

> Source File: SoundManager.cpp | Binary: BEA.exe
> Debug Path: 0x00632428

## Overview
> **Queue status (2026-05-26):** Ghidra export-contract closure **6113/6113** (Wave900: every function commented; clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

Audio system implementation. CSoundManager handles sound playback, event allocation/lifetime, 3D audio positioning, streaming, pitch, pause state, and volume control with a DirectSound backend.

Wave995 early high-signal residual review (`early-high-signal-residual-review-wave995`) re-read the sound-debug-marker caller context and corrected `0x00441e50 CDebugMarkers__Shutdown` stale Wave364 allocator/free wording. `0x004422d0 CDebugMarker__ctor` is called by `CSoundManager__UpdateStatus`, and `0x00442380 CDebugMarker__UnlinkFromGlobalList` is called by both `CSoundManager__UpdateStatus` and `CSoundEvent__DestructorBody`; the shutdown helper itself now documents direct `CDXMemoryManager__Free` at `0x00549220` with context `0x009c3df0`. Wave911 focused re-audit progress is `464/1408 = 32.95%`; expanded static surface progress is `569/1478 = 38.50%`; queue closure remains `6222/6222 = 100.00%`. Verified backup: `G:\GhidraBackups\BEA_20260531-073718_post_wave995_early_high_signal_residual_review_verified`. Runtime sound debug-marker behavior, exact debug-marker manager layout, exact source-body identity, BEA patching, and rebuild parity remain separate proof.

Wave562 PC backend note: the adjacent CPCSoundManager backend functions are now saved in Ghidra with bounded signatures/comments/tags, including `CPCSoundManager__CreateSampleFromFile`, `CPCSoundManager__CreateSampleFromData`, `CPCSoundManager__CreateSoundBuffer`, `CPCSoundManager__ConvertAudioFormat`, and `CPCSoundManager__DecodeADPCM`. This strengthens the static bridge from `CSoundManager__CreateSample` and `CGame__PumpBinkVoiceSampleQueue` into the PC sound backend; runtime DirectSound playback and exact backend/sample layouts remain unproven.

Wave818 message voice pump (`message-voice-pump-wave818`, `wave818-readback-verified`) completed the saved static bridge from `0x004b7d90 CGame__PumpBinkVoiceSampleQueue` into the Bink-thread and sound playback helpers. The row is saved as `void __thiscall CGame__PumpBinkVoiceSampleQueue(void * this)` and ties `CGame__Update` callsite `0x0046ea77` to `CBinkOpenThread__IsRunning`, `CPCSoundManager__CreateSampleFromData`, `CSoundManager__PlaySample`, queue globals `DAT_008073d0`/`DAT_0080738c`/`DAT_00704e74`, and active-reader cleanup. Post-Wave818 queue telemetry is `5606/6098 = 91.93%`, with next raw commentless row `0x004bc2d0 CWorld__ClearDynamicOccupancySet`; verified backup `G:\GhidraBackups\BEA_20260524-161634_post_wave818_message_voice_pump_verified`. Runtime Bink/voice playback behavior, exact global names/layouts, BEA patching, and rebuild parity remain unproven.

Wave827 actor/SoundManager raw head (`actor-soundmanager-raw-head-wave827`, `wave827-readback-verified`) saved comments/tags and bounded name/signature corrections for the adjacent raw-head rows `0x004df520 CActor__dtor_base_Thunk`, `0x004e0300 CSoundManager__UpdateVolumeForAllSoundEvents`, `0x004e04c0 CSoundManager__SetMasterVolume`, `0x004e06b0 CSoundManager__DeleteAllSamples`, `0x004e06e0 CSoundManager__Shutdown`, and `0x004e0820 CEffect__scalar_deleting_dtor`. The pass corrected `CSoundManager__UpdateAllSoundVolumes` to the source-backed `UpdateVolumeForAllSoundEvents`, corrected `CSoundManager__StopAllStreams` to `DeleteAllSamples`, corrected `CSoundDefinition__Destructor` to `CEffect__scalar_deleting_dtor`, and separated the actor thunk from the already-commented `CActor__dtor_base` body. Post-Wave827 queue telemetry is `6098` total, `5640` commented, `458` commentless, and strict proxy `5640/6098 = 92.49%`; next raw commentless row is `0x004e1260 CMonitor__UpdateTrackedValueAndDirection`. Verified backup: `G:\GhidraBackups\BEA_20260524-203238_post_wave827_actor_soundmanager_raw_head_verified`. Exact `CSoundManager`, `CSoundEvent`, `CSample`, and `CEffect` field schemas, runtime audio behavior, runtime lifetime behavior, BEA patching, and rebuild parity remain deferred.

Wave828 SoundManager FadeTo (`soundmanager-fadeto-wave828`, `wave828-readback-verified`) corrected `0x004e1260 CMonitor__UpdateTrackedValueAndDirection` to `0x004e1260 CSoundManager__FadeTo`, with saved signature `void __thiscall CSoundManager__FadeTo(void * this, void * sample, float fade_value, float speed, void * owner)`. Static evidence ties the row to source `CSoundManager::FadeTo`, `this+0x0c` active sound-event list traversal, sample compare at `event+0x0c`, owner compare at `event+0x00`, fade destination write at `event+0x28`, fade speed write at `event+0x24`, and callers `0x004081c0 CMonitor__Process`, `0x00409950 CMonitor__UpdateSoundEventPlaybackForReader`, `0x0040a580 CBattleEngine__Morph`, and `0x0040eb50 CMonitor__FlushTrackedList_1D4`. Post-Wave828 queue telemetry is `6098` total, `5641` commented, `457` commentless, and strict proxy `5641/6098 = 92.51%`; next raw commentless row is `0x004eb1e0 CGame__ResetRenderStateForWorldRender`. Verified backup: `G:\GhidraBackups\BEA_20260524-210153_post_wave828_soundmanager_fadeto_verified`. Exact `CSoundManager`, `CSoundEvent`, `CSample`, and active-reader field schemas, runtime audio fade behavior, BEA patching, and rebuild parity remain deferred.

Wave853 SoundManager backend tail (`soundmanager-backend-tail-wave853`, `wave853-readback-verified`) completed an important static DirectSound backend connector pass at the later PC backend cluster. The pass corrected CPCSample lifetime rows at `0x005168d0 CPCSample__dtor` and `0x00516960 CPCSample__scalar_deleting_dtor`, corrected source-backed CPCSoundManager backend labels including `CPCSoundManager__DeviceShutdown`, `CPCSoundManager__DeviceReset`, `CPCSoundManager__LoadSampleFromBuffer_StubFail`, `CPCSoundManager__PlaySound`, `CPCSoundManager__PauseSound`, `CPCSoundManager__UnPauseSound`, `CPCSoundManager__StopSound`, `CPCSoundManager__UpdateGlobals`, `CPCSoundManager__UpdateSound`, `CPCSoundManager__UpdatesDone`, `CPCSoundManager__GetSampleLength`, and `CPCSoundManager__FindFreeChannel`, and kept the global/audio-manager rows `0x00517ad0 CSoundManager__GetOutputEnabledFlag` and `0x00517d00 CSoundManager__LoadCompressedSampleBank` with bounded comments. The sample-bank row opens the cached XAP path at `this+0x88`, logs PC XAP/cache diagnostics, and calls `CSoundManager__CreateSample`; the output-enabled helper gates `CSoundManager__PlayEffect`. Post-Wave853 queue telemetry is `6098` total, `5754` commented, `344` commentless, and strict proxy `5754/6098 = 94.36%`; next raw commentless row is `0x0051a6a0 CFastVB__RenderIndexedImmediate`. Verified backup: `G:\GhidraBackups\BEA_20260525-101054_post_wave853_soundmanager_backend_tail_verified`. Runtime DirectSound playback, pause/unpause, shutdown/reset, sample-bank loading, exact backend/event/sample schemas, BEA patching, and rebuild parity remain deferred.

Wave908 audio/media/cutscene static review (`audio-media-cutscene-static-review-wave908`) records the audio-manager side of a static-coherent audio/media/cutscene/camera core. The read-only slice covers `171` selected rows across `26` families, including `CSoundManager 34`, `CPCSoundManager 20`, `CMusic 11`, `CWaveSoundRead 11`, `COggFileRead 9`, `CBinkOpenThread 9`, and the cutscene/camera partners. SoundManager anchors include `CSoundManager__Init`, `CSoundManager__CreateSample`, `CSoundManager__PlaySample`, `CSoundManager__FadeTo`, and `CSoundManager__LoadCompressedSampleBank`; backend/audio-reader anchors include `CPCSoundManager__CreateSampleFromData`, `CPCSoundManager__CreateSoundBuffer`, `CPCSoundManager__DecodeADPCM`, `CMusic__Init`, `CMusic__UpdateStatus`, and `CWaveSoundRead__Open`. Verified backup: `G:\GhidraBackups\BEA_20260526-113941_post_wave908_audio_media_cutscene_static_review_verified`. Stuart source and AYAResourceExtractor are reference/tooling aids here; loaded Steam Ghidra rows and extracted retail resource proof remain the authorities. Runtime DirectSound playback, Ogg/WAV decode behavior, Bink voice/FMVs, music switching, exact layouts, patch behavior, and clean-room rebuild parity remain separate proof.

Wave1023 (`frontend-options-pause-menu-review-wave1023`) re-read the adjacent audio reset wrapper `0x004cddf0 Audio__ReinitializeSoundAndRestoreMusic` with no mutation. Fresh metadata confirmed the saved `void __cdecl Audio__ReinitializeSoundAndRestoreMusic(int frontend_music_after_reset)` signature and the bounded static bridge into `CSoundManager__ReinitializeAfterDeviceLoss`, `CMusic__PlaySelection`, and `CGame__PlayMusicForCurrentLevel` depending on the frontend/current-level music branch. Verified backup: `G:\GhidraBackups\BEA_20260531-233831_post_wave1023_frontend_options_pause_menu_review_verified`. Runtime audio/music reset behavior, exact source-body identity, concrete audio-manager layouts, BEA patching, and rebuild parity remain separate proof.

Wave1179 (`wave1179-input-audio-support-current-risk-review`) re-read and tag-normalized the audio support anchors `Audio__ReinitializeSoundAndRestoreMusic`, `CWaveSoundRead__ScalarDeletingDestructor`, and `CPCSoundManager__LoadSampleFromBuffer_StubFail` inside a `6 input/controller/audio support current-risk rows` slice. Fresh Ghidra export evidence verified `13 xref rows` and `152 instruction rows`; the audio row xrefs are `OptionsTail_Read`, DATA `0x005dfc4c`, and `CSoundManager__CreateSample`. The same slice also covers `Input__UpdateCursorCenterWithWindowScale`, `Input__ResetMouseTransientState`, and `GameControllers__RelinquishControlForTarget`. Apply/read-back used `ApplyInputAudioSupportCurrentRiskWave1179.java`: `updated=6 skipped=0`, `tags_added=56`, no rename, no signature change, no comment change, no function-boundary change, and no executable-byte change. Codex read-only consults used; one consult recommended four-row split, while Codex root final judgment kept the six-row input/audio support slice. No Cursor/Composer was used. Static closure remains `6411/6411 = 100.00%` with `0 / 0 / 0` debt; Wave1108 current focused accounting is `721/1179 = 61.15%`; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 458; current risk candidates: 6166; current-risk denominator; focused threshold `15`; not Wave911 reconstruction. Verified backup: `G:\GhidraBackups\BEA_20260606-101513_post_wave1179_input_audio_support_current_risk_review_verified`. Runtime input behavior, runtime controller/menu behavior, runtime audio/device-loss/sample-reader behavior, exact concrete input/controller/audio layouts, exact source-body identity, BEA patching behavior, visual/audio QA, gameplay outcomes, and rebuild parity remain separate proof. Static clean-room target: preserve rebuild-grade static contracts for a future clean-room implementation aiming at no noticeable difference. Probe token anchor: Wave1179; wave1179-input-audio-support-current-risk-review; 721/1179 = 61.15%; 6 input/controller/audio support current-risk rows; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 458; current risk candidates: 6166; fresh Ghidra export; tag-only normalization; updated=6 skipped=0; tags_added=56; no rename; no signature change; no comment change; no function-boundary change; no executable-byte change; Codex read-only consults used; Codex root final judgment; consult recommended four-row split; root kept six-row input/audio support slice; no Cursor/Composer; 0 / 0 / 0; 6411/6411 = 100.00%; 13 xref rows; 152 instruction rows; Input__UpdateCursorCenterWithWindowScale; Input__ResetMouseTransientState; GameControllers__RelinquishControlForTarget; Audio__ReinitializeSoundAndRestoreMusic; CWaveSoundRead__ScalarDeletingDestructor; CPCSoundManager__LoadSampleFromBuffer_StubFail; G:\GhidraBackups\BEA_20260606-101513_post_wave1179_input_audio_support_current_risk_review_verified; wave1108-current-risk-rank.

Wave766 static read-back (`unwind-continuation-wave766`, `wave766-readback-verified`) saved comments/tags/signatures for the SoundManager.cpp-adjacent compiler-generated unwind callbacks from `0x005d4bf0 Unwind@005d4bf0` through `0x005d4c30 Unwind@005d4c30`. Evidence includes SoundManager.cpp debug path `0x00632428`, DATA scope-table xrefs `0x0061d45c` through `0x0061d4ac`, two `OID__FreeObject_Callback` rows, and `CDXMemBuffer__dtor_base(EBP-0x140)`. Verified backup: `G:\GhidraBackups\BEA_20260523-161835_post_wave766_unwind_continuation_verified`. Exact parent source-body identity, runtime exception behavior, runtime cleanup behavior, BEA patching, and rebuild parity remain deferred.

## Functions

| Address | Name | Purpose | Size |
|---------|------|---------|------|
| 0x004e00d0 | CSoundManager__Init | Wave502 saved bool-returning initializer; event pool, SFX load, debug/menu commands, PC sound init | ~500 bytes |
| 0x004e2530 | CEffect__LoadSFXFile | Wave502 corrected static effect-definition parser for sounds.sfx / supplied SFX file | ~600 bytes |

## Related Functions (No Debug Ref)

| Address | Name | Purpose |
|---------|------|---------|
| 0x004e0300 | CSoundManager__UpdateVolumeForAllSoundEvents | Wave827 source-backed correction; distance/fade/master-volume recompute for active sound events |
| 0x004e04c0 | CSoundManager__SetMasterVolume | Set master volume |
| 0x004e06b0 | CSoundManager__DeleteAllSamples | Wave827 source-backed correction; delete every linked sample and clear the sample list head |
| 0x004e06e0 | CSoundManager__Shutdown | Full cleanup |
| 0x004e0820 | CEffect__scalar_deleting_dtor | Wave827 source-backed correction; chained-effect delete, global effect-list unlink, optional free |
| 0x004dff30 | CSample__DestructorBody | Wave501 corrected stale constructor-like label; clears active events referencing this sample and unlinks sample list node |
| 0x004dffc0 | CSample__DeletingDestructor | Wave501 corrected CSample vtable slot-0 wrapper; stops referencing events and conditionally frees this sample |
| 0x004e0890 | CSoundManager__CreateSample | Wave501 saved sample creation signature; PC backend create/link/name/stereo-side handling |
| 0x004e0a00 | CSoundManager__GetOrCreateSample | Wave501 saved find-or-create signature; case-insensitive lookup with optional reload/create |
| 0x004e0a90 | CSoundManager__PlayNamedSample | Wave501 saved full named-sample playback wrapper signature (`RET 0x34`) |
| 0x004e0b30 | CSoundManager__PlaySample | Wave501 saved full sample playback wrapper signature (`RET 0x34`) with once/pre-running gates |
| 0x004e0bd0 | CSoundManager__StartSoundEvent | Wave501 corrected stale `PlaySound` label; allocates/initializes event, computes position/volume, starts channel |
| 0x004e0f70 | CSoundManager__StopSoundEvent | Wave500 saved `void __stdcall ... (void * sound_event, int block_until_stopped)`; callback + channel release + reader clear |
| 0x004e0fb0 | CSoundManager__AllocateSoundEvent | Wave500 saved source-parity `GetSoundEvent` signature; get free event from pool and link into active list |
| 0x004e1040 | CSoundManager__SortEventList | Wave500 saved source-parity sort signature; priority sort + channel allocation/release pass |
| 0x004e1130 | CSoundManager__KillSamplesForThing | Wave500 saved owner-filter signature; stop active events owned by one thing |
| 0x004e1190 | CSoundManager__KillSample | Wave500 saved owner+sample-filter signature; stop active events matching owner + sample pair |
| 0x004e1200 | CSoundManager__KillAllInstancesOfSample | Wave503 corrected stale CMessageBox ownership; stop every active event whose sample pointer matches the supplied sample |
| 0x004e1260 | CSoundManager__FadeTo | Wave828 corrected stale CMonitor label; source-backed fade helper writes event fade destination/speed for a matching sample and owner |
| 0x004e12b0 | CSoundManager__KillAllSamples | Wave500 saved kill-all signature; stop all active events |
| 0x004e1300 | CSoundManager__PauseAllSamples | Wave500 saved pause signature; stop assigned channels and set paused flag |
| 0x004e1330 | CSoundManager__UnPauseAllSamples | Wave500 saved unpause signature; refresh channel looping and clear paused flag |
| 0x004e1360 | CSoundManager__UpdateSoundPosition | Wave500 saved stack-only `void __stdcall ... (void * sound_event, int first_time)`; recompute event position/pan/attenuation from camera/tracking mode |
| 0x004e1800 | CSoundManager__StopSample | Wave502 corrected stale CMonitor label; stop active events matching owner reader and sample name |
| 0x004e1880 | CSoundManager__GetSoundEventForThing | Wave502 corrected stale CMonitor label; return first playing event matching owner/name |
| 0x004e18d0 | CSoundManager__SetPitch | Wave500 saved source-parity pitch signature; set desired pitch multiplier + fade-time ticks on an event |
| 0x004e1910 | CSoundManager__GetEffectByName | Wave502 corrected stale BattleEngine label; initialized wrapper around static CEffect lookup |
| 0x004e1940 | CSoundManager__PlayEffect | Wave502 saved full effect playback signature (`RET 0x30`) and chained-effect/random-selection evidence |
| 0x004e1ab0 | CSoundManager__IsEffectPlaying | Wave502 corrected stale CMonitor label; chained effect plus active-event owner/sample scan |
| 0x004e1b20 | [CSoundManager__UpdateStatus](./CSoundManager__UpdateStatus.md) | Per-frame sound-event update (camera state, attenuation, fades, cleanup) |
| 0x004e2360 | CSoundManager__GetDebugMenuText | Wave502 saved debug-menu text signature/comment for nth active sound event |
| 0x004e2a90 | CEffect__GetEffectByName | Wave502 corrected static effect name/ordinal lookup |
| 0x004e2b30 | CSoundEvent__DestructorBody | Wave502 corrected stale sound-manager release helper; debug-marker/free-reader cleanup |
| 0x004e2bb0 | CSoundManager__BuildLanguageSampleBankPathIfChanged | Wave503 corrected stale CUnit voice label; build/compare the current language sample-bank XAP path |
| 0x004e2c50 | CSoundManager__ReloadLanguageSampleBank | Wave502 saved PC language sample-bank reload helper |
| 0x004e2e60 | CUnit__PlayImpactSoundForMaterials | Wave503 hardened impact-material effect selection/playback helper using CSoundManager |
| 0x004cddf0 | [Audio__ReinitializeSoundAndRestoreMusic](./Audio__ReinitializeSoundAndRestoreMusic.md) | Wave480 corrected stale CEngine ownership; reinitializes sound and restores frontend/current-level music. |
| 0x00517f10 | [CSoundManager__ReinitializeAfterDeviceLoss](./CSoundManager__ReinitializeAfterDeviceLoss.md) | Wave480 hardened ECX/this signature and shutdown/reinit/reload comment. |

## Exception Handlers

| Address | Name | Line | Purpose |
|---------|------|------|---------|
| 0x005d4bf0 | Unwind@005d4bf0 | 90 | Wave766 saved allocation cleanup: `OID__FreeObject_Callback(*(EBP-0x10))` with line token `0x5a` and allocation/type value `0x4a` |
| 0x005d4c10 | Unwind@005d4c10 | n/a | Wave766 saved adjacent allocation cleanup: `OID__FreeObject_Callback(*(EBP-0x98))` |
| 0x005d4c30 | Unwind@005d4c30 | n/a | Wave766 saved adjacent stack-local buffer cleanup: `CDXMemBuffer__dtor_base(EBP-0x140)` |

## Key Observations

- **256 sound event slots** - Pre-allocated pool
- **Wave503 audio-tail evidence** - `KillAllInstancesOfSample`, the retail PC language sample-bank path change helper, and the impact-material sound dispatcher are saved in Ghidra with bounded static comments and corrected owner/signature evidence
- **Wave502 effect-definition/playback evidence** - Init, StopSample, GetSoundEventForThing, GetEffectByName, PlayEffect, IsEffectPlaying, debug text, CEffect SFX parsing/lookup, CSoundEvent destructor body, and language-bank reload are saved in Ghidra with bounded static comments and source-parity signatures
- **Wave501 sample playback evidence** - Sample destructor/deleting-destructor, sample create/lookup, named playback, sample playback, and `StartSoundEvent` are saved in Ghidra with bounded static comments and source-parity signatures
- **Wave500 event lifecycle evidence** - Stop/allocate/sort/kill/pause/unpause/position/pitch helpers are saved in Ghidra with bounded static comments and source-parity signatures
- **3D attenuation** - 50-meter max range
- **Console variables** - Debug controls
- **Dual path system** - "sounds\\" and "music\\" directories
- **DirectSound units** - Volume in hundredths of dB

## Console Variables

| CVar | Description | Default |
|------|-------------|---------|
| snd_frozen | Are sounds frozen? | 0 |
| snd_visible | Are sounds visible? | 0 |
| snd_radiomessagevolume | Radio message volume | 0.42 |
| snd_hudmessagevolume | HUD message volume | 0.45 |

## Console Commands

| Command | Description |
|---------|-------------|
| playsound | Play the named sample or stream |

## Wave 503 Audio Tail Signature Note (2026-05-17)

Wave503 hardened three adjacent audio-tail functions after serialized headless dry/apply/read-back:

| Address | Current saved Ghidra state | Notes |
| --- | --- | --- |
| `0x004e1200` | `void __thiscall CSoundManager__KillAllInstancesOfSample(void * this, void * sample)` | Corrects stale `CMessageBox` ownership; source-aligns to `CSoundManager::KillAllInstancesOfSample`, walking active sound events and stopping each entry whose sample pointer matches the supplied sample. |
| `0x004e2bb0` | `bool __thiscall CSoundManager__BuildLanguageSampleBankPathIfChanged(void * this, char * out_path)` | Corrects stale `CUnit` voice ownership; retail PC helper builds `<root>/data/sounds/sounds_<language>_pc.xap`, compares it with the cached path at `this+0x88`, optionally writes `out_path`, and returns true only when changed. |
| `0x004e2e60` | `void __cdecl CUnit__PlayImpactSoundForMaterials(void * primary_unit, void * secondary_unit)` | Hardened impact-material dispatcher signature/comment; reads material ids through vtable slot `+0xac`, chooses `impact_Wood` or `hit_%d`, resolves the effect, and plays it through `CSoundManager__PlayEffect`. |

Artifacts live under `subagents/ghidra-static-reaudit/wave503-audio-tail-004e1200/`. `ApplyAudioTailWave503.java` dry/apply/final-verify reported `updated=0/3/0`, `skipped=3/0/3`, `renamed=0/2/0`, no creates, no missing, no bad rows, and `REPORT: Save succeeded`. Read-back verified `3` metadata rows, `3` tag rows, `6` xref rows, `111` instruction rows, `3` decompile exports, focused probe PASS, queue refresh PASS, and backup `G:\GhidraBackups\BEA_20260517-142753_post_wave503_audio_tail_verified` with `19` files, `157944711` bytes, `MissingCount=0`, `ExtraCount=0`, and `HashDiffCount=0`.

Runtime sample shutdown, language switching, collision/impact sound behavior, exact `CSoundManager`/`CSoundEvent`/sample/sample-bank/material/effect/backend layouts, BEA launch behavior, game patching, and rebuild parity remain unproven.

## Sound Event Structure (136 bytes / 0x88)

| Offset | Field | Notes |
|--------|-------|-------|
| 0x04 | mSoundHandle | Handle |
| 0x08 | mIsPlaying | Playing flag |
| 0x10 | mIs3D | 3D positioning |
| 0x14 | mChannelType | 1=sound, else=music |
| 0x18 | mIsLooping | Loop flag |
| 0x1C | mBaseVolume | Base volume |
| 0x44-0x4C | mPosition | x,y,z position |
| 0x74 | mNext | Linked list |
| 0x78 | mPrev | Linked list |

## Sound Definition Structure (220 bytes / 0xDC)

| Offset | Size | Field |
|--------|------|-------|
| 0x00 | 64 | mName |
| 0x40 | 64 | mFilePath |
| 0x80 | 64 | mAltPath |
| 0xD4 | 4 | mDuplicateNext |
| 0xD8 | 4 | mNext |

## Key Globals

| Address | Name | Purpose |
|---------|------|---------|
| 0x0083cfe8 | g_pSoundDefinitionListHead | Head of linked list of sound definitions (0xDC-byte nodes) |

## Wave 502 Effect Definition / Playback Signature Note (2026-05-17)

Wave502 hardened eleven adjacent effect-definition, lookup, playback, debug-text, event-destruction, and language-bank helpers after serialized headless dry/apply/read-back:

| Address | Current saved Ghidra state | Notes |
| --- | --- | --- |
| `0x004e00d0` | `bool __thiscall CSoundManager__Init(void * this)` | Source-aligns to `CSoundManager::Init` with retail PC differences; clears lists/volumes, loads `data\\sounds\\sounds.sfx`, allocates 256 pooled events, registers the sound debug menu/cvars/`playsound`, seeds message volumes, and calls the PC sound manager init path. |
| `0x004e1800` | `void __thiscall CSoundManager__StopSample(void * this, char * sample_name, void * owner)` | Corrects stale `CMonitor` ownership; walks active events and stops entries matching owner reader plus sample-name string. |
| `0x004e1880` | `void * __thiscall CSoundManager__GetSoundEventForThing(void * this, char * sample_name, void * owner)` | Corrects stale `CMonitor` ownership; returns the first playing event matching owner/name. |
| `0x004e1910` | `void * __thiscall CSoundManager__GetEffectByName(void * this, char * name, int ordinal)` | Corrects stale `CBattleEngine` ownership; initialized manager wrapper around static `CEffect__GetEffectByName`. |
| `0x004e1940` | `void __thiscall CSoundManager__PlayEffect(void * this, void * effect, void * owner, float volume, int tracking_type, int once, float fade_seconds, float from_point_seconds, float to_point_seconds, int repeat, float pitch, int sound_type, int ignore_owner_pos)` | Retail `RET 0x30` proves twelve stack arguments after `this`; selects a chained effect, applies volume/pitch/language flags, resolves the sample, and forwards to `CSoundManager__PlaySample`. |
| `0x004e1ab0` | `bool __thiscall CSoundManager__IsEffectPlaying(void * this, void * effect, void * owner)` | Corrects stale `CMonitor` ownership; scans chained effects and active events for a playing owner/sample match. |
| `0x004e2360` | `void __thiscall CSoundManager__GetDebugMenuText(void * this, int entry_index, char * text)` | Builds the nth active-event debug text line, including no-sound, sample/channel, volume/current attenuated volume, and tracking-mode text. |
| `0x004e2530` | `void __cdecl CEffect__LoadSFXFile(char * filename)` | Corrects stale `CSoundManager` ownership; static SFX parser opens the supplied file, allocates `0xDC`-byte `CEffect` records, parses names/scalars/flags, and chains duplicate effect names. |
| `0x004e2a90` | `void * __cdecl CEffect__GetEffectByName(char * name, int ordinal)` | Corrects stale `CSoundManager` ownership; static lookup normalizes repeated backslashes, walks the CEffect main list, and returns the nth case-insensitive match. |
| `0x004e2b30` | `void __thiscall CSoundEvent__DestructorBody(void * this)` | Corrects stale sound-manager release-helper ownership; unlinks/frees the debug marker and removes this active reader from its owner deletion-event set. |
| `0x004e2c50` | `void __thiscall CSoundManager__ReloadLanguageSampleBank(void * this)` | Retail PC language sample-bank reload helper; updates cached XAP path, moves active events back to the pool, stops voices, deletes samples, runs memory cleanup, and reloads the compressed sample bank. |

Artifacts live under `subagents/ghidra-static-reaudit/wave502-soundmanager-effects-scout-004e1800/`. `ApplyCSoundManagerEffectsWave502.java` dry/apply/final-verify reported `updated=0/11/0`, `skipped=11/0/11`, `renamed=0/8/0`, no creates, no missing, no bad rows, and `REPORT: Save succeeded`. Read-back verified `13` metadata rows, `13` tag rows, `117` xref rows, `481` instruction rows, `13` decompile exports, focused probe PASS, npm probe PASS, queue refresh PASS, and backup `G:\GhidraBackups\BEA_20260517-140251_post_wave502_csoundmanager_effects_verified` with `19` files, `157944711` bytes, `MissingCount=0`, `ExtraCount=0`, and `HashDiffCount=0`.

Runtime effect parsing, random selection/playback/mixing, language-bank reload behavior, exact `CSoundManager`/`CEffect`/`CSoundEvent`/backend/channel/owner-reader layouts, BEA launch behavior, game patching, and rebuild parity remain unproven. The former scout-only `0x004e2bb0` and `0x004e2e60` follow-ups were closed by Wave503.

## Wave 501 Sample Playback Signature Note (2026-05-17)

Wave501 hardened seven adjacent sample lifecycle/playback functions after serialized headless dry/apply/read-back:

| Address | Current saved Ghidra state | Notes |
| --- | --- | --- |
| `0x004dff30` | `void __fastcall CSample__DestructorBody(void * this)` | Corrects the stale constructor-like label; body installs the CSample vtable, stops/clears active events whose sample pointer equals this, and unlinks from the global sample list. |
| `0x004dffc0` | `void * __thiscall CSample__DeletingDestructor(void * this, int delete_flags, int unused)` | CSample vtable `0x005dee6c` slot 0 points here; wrapper duplicates cleanup, stops referencing events with `block_until_stopped=1`, conditionally frees on `delete_flags & 1`, and returns `this`. |
| `0x004e0890` | `void * __thiscall CSoundManager__CreateSample(void * this, char * name, int channel_type, void * sample_source, int reuse_existing)` | Source-aligns to sample creation with retail PC backend differences; chooses sound/music path context, optionally reuses existing samples, calls `CPCSoundManager__CreateSampleFromFile`, links the sample list, and marks `_L`/`_R` stereo side variants. |
| `0x004e0a00` | `void * __thiscall CSoundManager__GetOrCreateSample(void * this, char * name, int channel_type, int reload_if_exists)` | Source-aligns to `GetSample`; checks initialized/non-empty name state, scans by case-insensitive name, returns existing samples unless reload is requested, otherwise gates creation through retail load-allowed globals. |
| `0x004e0a90` | `void __thiscall CSoundManager__PlayNamedSample(void * this, char * sample_name, void * owner, float volume, int tracking_type, int once, float fade_seconds, float from_point_seconds, float to_point_seconds, int repeat, float pitch, int inform_owner_when_complete, int ignore_owner_pos, int sound_type)` | Retail `RET 0x34` proves the full playback stack payload after `this`; resolves the named sample and forwards to `CSoundManager__PlaySample`. |
| `0x004e0b30` | `void __thiscall CSoundManager__PlaySample(void * this, void * sample, void * owner, float volume, int tracking_type, int once, float fade_seconds, float from_point_seconds, float to_point_seconds, int repeat, float pitch, int inform_owner_when_complete, int ignore_owner_pos, int sound_type)` | Retail `RET 0x34` proves the full playback stack payload after `this`; applies initialization, pre-running, and once-only duplicate gates before forwarding to `StartSoundEvent`. |
| `0x004e0bd0` | `void * __thiscall CSoundManager__StartSoundEvent(void * this, void * owner, void * sample, int tracking_type, float volume, float fade_seconds, float from_point_seconds, float to_point_seconds, int loop, float pitch, int inform_owner_when_complete, int ignore_owner_pos, int sound_type)` | Corrects stale `PlaySound` label; allocates and initializes a sound event, computes pan/position/volume, handles too-distant non-looping events, starts a channel, and returns event/null. |

Artifacts live under `subagents/ghidra-static-reaudit/wave501-csoundmanager-sample-playback-004dff30/`. `ApplyCSoundManagerSamplePlaybackWave501.java` dry/apply/final-verify reported `updated=0/7/0`, `skipped=7/0/7`, `renamed=0/3/0`, no creates, no missing, no bad rows, and `REPORT: Save succeeded`. Read-back verified `7` metadata rows, `7` tag rows, `20` xref rows, `847` instruction rows, `7` decompile exports, focused probe PASS, npm probe PASS, queue refresh PASS, and backup `G:\GhidraBackups\BEA_20260517-132737_post_wave501_csoundmanager_sample_playback_verified` with `19` files, `157846407` bytes, `MissingCount=0`, `ExtraCount=0`, and `HashDiffCount=0`.

Runtime sample unload/loading/playback/mixing behavior, exact `CSample`/`CSoundManager`/`CSoundEvent`/backend/channel/active-reader layouts, BEA launch behavior, game patching, and rebuild parity remain unproven.

## Wave 500 Event Lifecycle Signature Note (2026-05-17)

Wave500 hardened ten adjacent event-lifecycle functions after serialized headless dry/apply/read-back:

| Address | Current saved Ghidra state | Notes |
| --- | --- | --- |
| `0x004e0f70` | `void __stdcall CSoundManager__StopSoundEvent(void * sound_event, int block_until_stopped)` | Retail `RET 0x8` proves stack event/flag arguments rather than hidden manager `this`; body handles owner callback, channel release, playing-state clear, and active-reader clear. |
| `0x004e0fb0` | `void * __thiscall CSoundManager__AllocateSoundEvent(void * this, int insert_at_top)` | Source-aligns to `GetSoundEvent`; pops an event from `this+0x34`, links it into `this+0x0c`, and increments the active-event count. |
| `0x004e1040` | `void __thiscall CSoundManager__SortEventList(void * this)` | Source-aligns to `SortEventList`; sorts by current attenuated volume, enforces the channel budget, and assigns/releases channels. |
| `0x004e1130` | `void __thiscall CSoundManager__KillSamplesForThing(void * this, void * owner)` | Stops active events whose active-reader owner matches the supplied owner. |
| `0x004e1190` | `void __thiscall CSoundManager__KillSample(void * this, void * owner, void * sample)` | Stops active events matching both owner reader and sample pointer. |
| `0x004e12b0` | `void __thiscall CSoundManager__KillAllSamples(void * this)` | Walks and stops the active event list; xrefs include game restart and cutscene update contexts. |
| `0x004e1300` | `void __thiscall CSoundManager__PauseAllSamples(void * this)` | Stops assigned channels and sets the event paused flag at `+0x84`. |
| `0x004e1330` | `void __thiscall CSoundManager__UnPauseAllSamples(void * this)` | Refreshes channel looping for assigned channels and clears the paused flag at `+0x84`. |
| `0x004e1360` | `void __stdcall CSoundManager__UpdateSoundPosition(void * sound_event, int first_time)` | Retail `RET 0x8` proves stack event/flag arguments; body handles camera selection, tracking modes, camera-local transforms, pan offsets, and `g_InvertXAxisFlag`. |
| `0x004e18d0` | `void __thiscall CSoundManager__SetPitch(void * this, void * sound_event, float desired_pitch_factor, float fade_time_seconds)` | Stores desired pitch at `event+0x3c` and `round(fade_time_seconds * 20.0)` fade ticks at `event+0x40`. |

Artifacts live under `subagents/ghidra-static-reaudit/wave500-csoundmanager-events-004e0f70/`. `ApplyCSoundManagerEventsWave500.java` dry/apply/final-verify reported `updated=0/10/0`, `skipped=10/0/10`, no creates, no renames, no missing, no bad rows, and `REPORT: Save succeeded`. Read-back verified `10` metadata rows, `10` tag rows, `17` xref rows, instruction exports, `10` decompile exports, focused probe PASS, npm probe PASS, queue refresh PASS, and backup `G:\GhidraBackups\BEA_20260517-125819_post_wave500_csoundmanager_events_verified` with `19` files, `157780871` bytes, `MissingCount=0`, `ExtraCount=0`, and `HashDiffCount=0`.

Runtime audio behavior, exact `CSoundManager`/`CSoundEvent`/channel/active-reader layouts, BEA launch behavior, game patching, and rebuild parity remain unproven.

## Wave 364 Debug Marker Correction Note (2026-05-13)

Wave 364 corrected two saved labels that had been interpreted as sound-event-node helpers:

| Address | Current saved Ghidra state | Notes |
| --- | --- | --- |
| `0x004422d0` | `CDebugMarker__ctor` | Sound-manager visible-sound callsites construct a debug marker for visualization; this is not a `CSoundManager__SoundEventNode` constructor. |
| `0x00442380` | `CDebugMarker__UnlinkFromGlobalList` | Sound-manager cleanup callsites unlink the associated debug marker before free; this is not a sound-event-node list unlink helper. |

This note preserves the sound-manager caller context while moving ownership to the debug-marker helpers. Runtime visible-sound/debug-marker behavior, concrete debug-marker layout, local variables/types, BEA launch behavior, game patching, and rebuild parity remain unproven.

## Related Files

- Music.cpp - Music playback
- engine.cpp - Engine initialization

---
*Discovered via Phase 1 xref analysis (Dec 2025)*
