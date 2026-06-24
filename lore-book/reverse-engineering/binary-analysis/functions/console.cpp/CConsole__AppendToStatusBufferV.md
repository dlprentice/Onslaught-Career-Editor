# CConsole__AppendToStatusBufferV

- **Address:** `0x00472240`
- **Saved signature:** `void __cdecl CConsole__AppendToStatusBufferV(void * console, char * format)`
- **Source context:** console/status overlay helper; reached by frontend cheat/status paths and other status-overlay callers

## Summary

Appends formatted status/debug overlay text through `vsprintf`, using the write cursor at `console+0x2710`.

## Notes

- Wave 381 supersedes the older `CGame__AppendToStatusBufferV` label and moves this helper under console/status ownership.
- Saved via serialized headless dry/apply/read-back on 2026-05-13.
- The exported instruction evidence includes the `console+0x2710` cursor load and the `vsprintf` call target.

## Not Proven

- Runtime console/status overlay rendering is not proven by this static pass.
- Exact console object layout and varargs typing remain open.
- BEA launch behavior, game patching, and rebuild parity are not proven.
