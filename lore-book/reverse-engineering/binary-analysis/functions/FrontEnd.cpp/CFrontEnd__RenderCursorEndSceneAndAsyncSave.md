# CFrontEnd__RenderCursorEndSceneAndAsyncSave

- Address: 0x00468700
- Status: Renamed (headless batch, Wave 377 read-back verified)
- Current saved signature: `void __stdcall CFrontEnd__RenderCursorEndSceneAndAsyncSave(int end_scene)`

## Purpose

Renders the frontend mouse cursor path, optionally ends the scene, and schedules asynchronous career-save work.

## Notes

Wave 377 corrected the older generic `CFrontEnd__VFunc_07_00468700` label. The saved comment records cursor rendering, optional end-scene behavior when `end_scene` is nonzero, and async career-save scheduling.

This is static decompile/vtable evidence only. Runtime frame presentation or save behavior remains unproven by this page.
