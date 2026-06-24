# Ghidra CDXFrontEndVideo Head Wave597 Readiness Note

Date: 2026-05-19
Status: static saved-Ghidra evidence only

Wave597 hardened the next queue head after Wave596: the CDXFrontEndVideo constructor/lifecycle/open/render/update cluster, plus the adjacent already-clean but commentless default-size helper.

Saved rows:

| Address | Function |
| --- | --- |
| `0x00541200` | `CDXFrontEndVideo__CDXFrontEndVideo` |
| `0x00541220` | `CDXFrontEndVideo__scalar_deleting_dtor` |
| `0x00541240` | `CDXFrontEndVideo__SetDefaultSize` |
| `0x00541260` | `CDXFrontEndVideo__Close` |
| `0x005412e0` | `CDXFrontEndVideo__Open` |
| `0x00541430` | `CDXFrontEndVideo__InitVideo` |
| `0x00541650` | `CDXFrontEndVideo__CloseVideo` |
| `0x00541770` | `CDXFrontEndVideo__GetWidth` |
| `0x00541780` | `CDXFrontEndVideo__GetHeight` |
| `0x00541790` | `CDXFrontEndVideo__Render` |
| `0x00541d30` | `CDXFrontEndVideo__Update` |

What is proven:

- Ghidra now records clean signatures, function comments, and `cdxfrontendvideo-head-wave597` tags for all eleven rows.
- `CDXFrontEndVideo__CDXFrontEndVideo` is called by `CFEPMultiplayerStart__ctor` and `CDXFMV__ctor_base`; it installs vtable `0x005e5084` and clears observed Bink handle, texture slots, frame flags, and fade state fields.
- `CDXFrontEndVideo__scalar_deleting_dtor` replaces the older generic `CDXFrontEndVideo__dtor` label. Vtable `0x005e5084` slot 0 points to it, `RET 0x4` proves one delete-flag stack parameter after `this`, and the body conditionally frees only when `delete_flags` bit 0 is set.
- `CDXFrontEndVideo__SetDefaultSize` stores fallback dimensions `0x200` by `0x200` at `this+0x20` and `this+0x24`, then returns 1.
- `CDXFrontEndVideo__Close` forwards to `CDXFrontEndVideo__CloseVideo` and clears the Bink handle at `this+0x08`.
- `CDXFrontEndVideo__Open` is reached by `CFEPCommon` video init/start paths, `CDXFrontEndVideo__Render` pending-open handling, and CDXFMV call sites. `RET 0x18` proves six stack parameters after `this`; the body configures RAD memory hooks, stores fallback dimensions, queues pending async opens through `DAT_008a97d0`, copies the filename into Bink-open buffers, runs or starts `CBinkOpenThread`, and calls `CDXFrontEndVideo__InitVideo` for synchronous opens.
- `CDXFrontEndVideo__InitVideo` consumes the open-thread Bink handle, prepares the first frame, allocates/configures two `CUMTexture` slots, computes power-of-two texture dimensions against device caps, and clears pending/fade state.
- `CDXFrontEndVideo__CloseVideo` waits for active async open work, releases two `CUMTexture` slots, logs Bink summary counters, closes the Bink handle, clears `this+0x08`, and unlocks the thread.
- `CDXFrontEndVideo__GetWidth` and `CDXFrontEndVideo__GetHeight` return cached fallback dimensions when no Bink handle exists, otherwise read the observed width/height fields at Bink handle offsets `0x00` and `0x04`.
- `CDXFrontEndVideo__Render` is reached by `CFrontEnd__RenderVideoQuadScaledToWindow` and CDXFMV render call sites. `RET 0x1c` proves seven stack parameters after `this`; the body services pending async opens, decodes/copies Bink frames into double-buffered `CUMTexture` surfaces, modulates `packed_argb` by fade alpha, falls back to `meshtex_default.tga`, builds a six-vertex quad from x/y/z scale values, and submits it through the Direct3D device.
- `CDXFrontEndVideo__Update` is reached by `CFrontEnd__Process` and CDXFMV update call sites. `RET 0x4` proves one stack parameter after `this`; the body returns 0 without a Bink handle, uses `BinkWait` to gate frame advancement, returns -1 when `wait_for_frame` requests a wait and the frame is not ready, advances frames through `BinkDoFrame`/`BinkNextFrame`, and returns 1 when the observed current-frame and total-frame fields match.
- Post-save read-back verified 11 metadata rows, 11 tag rows, 27 xref rows, 935 instruction rows, 11 decompile rows, and 48 vtable-slot rows.
- The queue refresh reports `6093` total functions, `3064` commented, `3029` commentless, `1333` exact-undefined signatures, and `1085` `param_N` signatures.
- Comment-backed proxy is `3064/6093 = 50.29%`; strict clean-signature proxy is `3019/6093 = 49.55%`.
- The next high-signal queue head is `0x00542740 CDXEngine__InitLandscapeTextureTables`.
- The live Ghidra project backup verified at `G:\GhidraBackups\BEA_20260519-162129_post_wave597_cdxfrontendvideo_head_verified` with 19 files, 161123207 bytes, `DiffCount=0`, and manifest hash `614df28fbf49231fd4d2bd359d833564e4f64678cb240bd8a5ed2c1ed82c1506`.

What is not proven:

- Runtime Bink playback, async scheduling, texture upload, frontend-video rendering, media timing, and game-visible FMV behavior remain unproven.
- Exact `CDXFrontEndVideo`, `CDXFMV`, `CFEPCommon`, `CFrontEnd`, `CBinkOpenThread`, `CUMTexture`, Direct3D surface, and Bink struct layouts remain unproven beyond observed fields documented in the read-back notes.
- Exact source identity remains unproven because the current tracked Stuart source snapshot does not include a byte/layout-matching retail `DXFrontEndVideo.cpp` body.
- BEA patching, gameplay behavior, packaged release behavior, and rebuild parity remain unproven.
