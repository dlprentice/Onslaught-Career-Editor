# Ghidra Frontend Core Wave377 Evidence - 2026-05-13

Status: public-safe saved Ghidra evidence note

## Summary

Wave 377 is a serialized static Ghidra correction tranche for thirteen frontend core/helper targets. It hardens source-parity signatures for `CFrontEnd` controller, language, transition, and title-bar helpers; corrects the source-static sliding-border page predicate away from a `CFrontEnd` instance-method label; corrects a generic vtable-slot label to cursor/end-scene/async-save behavior; and hardens frontend mouse-rectangle wrappers plus level-name text resolution.

This note is public-safe. It records addresses, names, signatures, counts, and proof boundaries only. Raw decompile/read-back exports and generated proof JSON remain under ignored private artifact roots.

## Saved Targets

| Address | Saved Ghidra state | Evidence boundary |
| --- | --- | --- |
| `0x00466980` | `int __thiscall CFrontEnd__GetPlayer0ControllerPort(void * this)` | Source/decompile parity: reads player-0 controller port and normalizes the unset sentinel to `0`. |
| `0x004669a0` | `void __thiscall CFrontEnd__ReceiveButtonAction(void * this, void * from_controller, int button, float action_value)` | Corrects old `VFuncSlot_03_004669a0`; source and retail body match frontend button dispatch, controller selection, cheat button, and modal/page routing. |
| `0x00466ab0` | `void __thiscall CFrontEnd__SetLanguage(void * this, int language_index)` | Hardens source-parity language-set copy helper and removes stale extra parameter debt. |
| `0x00467200` | `void __thiscall CFrontEnd__DrawSlidingTextBordersAndMask(void * this, float transition, int dest_page)` | Hardens transition/destination-page signature for shared frontend border/mask renderer. |
| `0x004679a0` | `int __cdecl FrontEnd__HasStandardSlidingTextBordersAndMaskPage(int dest_page)` | Corrects old `CFrontEnd__HasStandardSlidingTextBordersAndMask` owner wording to source-static page predicate. |
| `0x00467bd0` | `void __stdcall CFrontEnd__DrawTitleBar(short * title_text, float transition, int dest_page)` | Hardens title text, transition, and destination-page arguments. |
| `0x00468700` | `void __stdcall CFrontEnd__RenderCursorEndSceneAndAsyncSave(int end_scene)` | Corrects generic `CFrontEnd__VFunc_07_00468700`; decompile shows cursor render, optional end-scene, and async career save. |
| `0x004691c0` | `void __fastcall CFrontEnd__ReleaseParticleHudWaypointResources(void * frontend)` | Hardens frontend cleanup helper signature for particle, HUD handle, waypoint, mesh, and texture level-resource cleanup. |
| `0x00469390` | `uint __cdecl CFrontEnd__ProcessMouseReadyOrDispatchVBufTexture(float x, float y, float width, float height, int dispatch_context)` | Hardens modal mouse-input gate and click-dispatch rectangle signature. |
| `0x004693d0` | `uint __cdecl CFrontEnd__GetCursorStateInRect(float x, float y, float width, float height)` | Hardens cursor-state rectangle wrapper signature. |
| `0x00469400` | `uint __cdecl CFrontEnd__GetClickStateInRect(float x, float y, float width, float height)` | Hardens click-state rectangle wrapper signature. |
| `0x00469430` | `uint __cdecl CFEPDirectory__GetCursorStateInRectAndConsumeIfMouseReady(float x, float y, float width, float height)` | Corrects old `CFEPDirectory__CheckMouseInputReady` wording to the observed consume-wrapper behavior. |
| `0x00469550` | `short * __cdecl CFrontEnd__ResolveLevelNameTextByCode(int level_code)` | Hardens return type for localized level-name text resolution with `Unnamed Level` fallback. |

## Validation

Serialized dry/apply used `tools/ApplyFrontendCoreWave377.java`. The dry run reported `updated=0 skipped=13 renamed=0 would_rename=4 missing=0 bad=0`; the apply run reported `updated=13 skipped=0 renamed=4 would_rename=0 missing=0 bad=0` and `REPORT: Save succeeded`.

Read-back verified `13` metadata rows, `13` decompile exports, `68` xref rows, `4693` instruction rows, and `13` tag rows. The focused probe reports `PASS` for `13` targets, with `23` xref evidence hits and `12` instruction evidence hits.

The refreshed whole-database queue reports `6026` functions, `1371` commented functions, `4655` commentless functions, `1939` undefined signatures, and `1952` `param_N` signatures. Current confirmation proxies are telemetry only: comment-backed `1371/6026 = 22.75%`, strict clean-signature `1306/6026 = 21.67%`.

The actual live Ghidra project backup was verified at `G:\GhidraBackups\BEA_20260513_135259_post_wave377_frontend_core_verified` with `19` files, `153619335` bytes, and `HashDiffCount=0`.

## Not Proven

- Runtime frontend input, rendering, title-bar, cursor, save, or localization behavior.
- Exact class layouts, local variable types, structure recovery, or source method identity for every branch.
- BEA launch behavior, game patching, packaged WinUI behavior, or rebuild parity.
