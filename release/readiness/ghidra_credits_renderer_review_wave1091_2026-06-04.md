# Ghidra Credits Renderer Review Wave1091

Status: complete static comment/tag normalization
Date: 2026-06-04
Scope: `credits-renderer-review-wave1091`

Wave1091 re-read and hardened the shared credits renderer plus its game-outro and frontend-page callers. The wave saved comment/tag normalization only for 11 already existing function objects: four `Credits.cpp` rows, two `CGame` outro/credits context rows, and five `CFEPCredits` vtable rows. It made no rename, no signature change, no function-boundary change, no executable-byte change, no BEA launch, and no installed-game or runtime-file mutation.

Reviewed and hardened rows:

| Address | Saved row | Fresh static evidence |
| --- | --- | --- |
| `0x00518bf0 CCredits__BuildDefaultEntries` | `void CCredits__BuildDefaultEntries(void)` | Startup thunk `0x00518be0` jumps to this body; decompile fills the hard-coded credits-entry table beginning at `DAT_00896ca8` with mixed localized text IDs and literal strings. |
| `0x00519ff0 CCredits__WriteEntry_TextId` | `void __thiscall CCredits__WriteEntry_TextId(void * this, int section, int text_id, int style)` | Writes one credits row as `{section,text_id,0,style}` at the ECX/`this` destination entry pointer. |
| `0x0051a010 CCredits__WriteEntry_String` | `void __thiscall CCredits__WriteEntry_String(void * this, int section, char * text, int style)` | Writes one credits row as `{section,-1,text_ptr,style}` at the ECX/`this` destination entry pointer. |
| `0x0051a030 CCredits__RenderCredits` | `bool __stdcall CCredits__RenderCredits(float elapsed, int alpha)` | Shared per-frame renderer called from `0x00472801 CGame__RollCredits` and `0x0051a92b CFEPCredits__Render`; resolves literal/localized rows, computes spacing/alpha, draws via `CDXFont__DrawTextDynamic`, and returns false when the scroll is complete. |
| `0x0046d9f0 CGame__RunOutroFMV` | `void __fastcall CGame__RunOutroFMV(void * this)` | Outro path calls `CGame__RollCredits` for final-level codes `0x2e5` and `800`. |
| `0x004726b0 CGame__RollCredits` | `void CGame__RollCredits(void)` | Main-game credits loop creates temporary controllers, plays credits music when enabled, calls `CCredits__RenderCredits(elapsed, 0xff)` at `0x00472801`, and exits on completion/skip before cleanup. |
| `0x0051a7f0 CFEPCredits__ButtonPressed` | `void __stdcall CFEPCredits__ButtonPressed(void * this, int button, float val)` | CFEPCredits vtable slot 3 (`0x005db88c`); button `0x2e` returns to page `0x11` and resumes frontend music. |
| `0x0051a820 CFEPCredits__Process` | `void __thiscall CFEPCredits__Process(void * this, int state)` | CFEPCredits vtable slot 2 (`0x005db888`); checks/clears completion flag `this+0x08`, returns to page `0x11`, resumes music, and draws prompt code `0x2e`. |
| `0x0051a880 CFEPCredits__RenderPreCommon` | `void __stdcall CFEPCredits__RenderPreCommon(void * this, float transition, int dest)` | CFEPCredits vtable slot 4 (`0x005db890`); dispatches the standard pre-common pass at full transition. |
| `0x0051a8b0 CFEPCredits__Render` | `void __thiscall CFEPCredits__Render(void * this, float transition, int dest)` | CFEPCredits vtable slot 5 (`0x005db894`); calls `CCredits__RenderCredits` at `0x0051a92b`, sets completion flag `this+0x08` when done, and triggers the full-transition helper path. |
| `0x0051a970 CFEPCredits__TransitionNotification` | `void __fastcall CFEPCredits__TransitionNotification(void * this, int from_page)` | CFEPCredits vtable slot 6 (`0x005db898`); rechecked prior Wave855 row, stores timer at `this+0x04`, calls `CMusic__PlaySelection(&DAT_00889a48,1,1)`, clears completion flag `this+0x08`, and returns with `RET 0x4`. |

Vtable evidence:

- `0x005db880` exported `9` CFEPCredits vtable slots, all `OK`.
- Key slots are slot `2` process, slot `3` button, slot `4` pre-common render, slot `5` render, and slot `6` transition notification.

Mutation and read-back:

- Dry run: `updated=0 skipped=11 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=11 missing=0 bad=0`.
- Apply: `updated=11 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=11 missing=0 bad=0`, with `REPORT: Save succeeded`.
- Final dry run: `updated=0 skipped=11 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`.
- Post tags include `credits-renderer-review-wave1091` and `wave1091-readback-verified` on all 11 rows.

Evidence counts:

- Pre primary exports: `4` metadata rows, `4` tag rows, `88` xref rows, `1135` function-body instruction rows, and `4` decompile rows.
- Pre context exports: `7` metadata rows, `7` tag rows, `7` xref rows, `381` function-body instruction rows, and `7` decompile rows.
- Pre around/vtable exports: `14` around-address targets, `546` around-instruction rows, and `9` CFEPCredits vtable rows.
- Post primary exports: `4` metadata rows, `4` tag rows, `88` xref rows, `1135` function-body instruction rows, and `4` decompile rows.
- Post context exports: `7` metadata rows, `7` tag rows, `7` xref rows, `381` function-body instruction rows, and `7` decompile rows.
- Post around/vtable exports: `14` around-address targets, `546` around-instruction rows, and `9` CFEPCredits vtable rows.
- Queue closure remains `6410/6410 = 100.00%`, with `0` commentless rows, `0` exact-undefined signatures, and `0` `param_N` signatures.
- Wave911 focused progress remains `812/1408 = 57.67%`; expanded static surface progress advances to `1545/1560 = 99.04%`; top-500 risk-ranked coverage remains `500/500 = 100.00%`.
- Verified backup: `G:\GhidraBackups\BEA_20260604-143442_post_wave1091_credits_renderer_review_verified`, 19 files, 175541127 bytes, `DiffCount=0`.

What this proves:

- The saved credits renderer and FE credits-page function objects exist in the loaded Ghidra database with coherent names, signatures, comments, tags, xrefs, instruction bodies, decompile output, vtable slots, and backup read-back.
- The shared credits renderer connects static game-outro and frontend-page credits presentation paths.
- The Wave1091 Ghidra mutation was limited to comment/tag normalization.

What remains separate proof:

- Runtime credits rendering or frontend navigation behavior.
- Concrete `CCredits` / `CFEPCredits` layout recovery beyond observed offsets.
- Exact source-body identity for absent full credits/frontend source files.
- BEA patching behavior, gameplay outcomes, and rebuild parity.

Probe token anchor: Wave1091; credits-renderer-review-wave1091; 0x00518bf0 CCredits__BuildDefaultEntries; 0x0051a030 CCredits__RenderCredits; 0x004726b0 CGame__RollCredits; 0x0051a8b0 CFEPCredits__Render; 0x0051a970 CFEPCredits__TransitionNotification; 0x005db880; 0x00472801; 0x0051a92b; DAT_00896ca8; CDXFont__DrawTextDynamic; CMusic__PlaySelection; 1545/1560 = 99.04%; 812/1408 = 57.67%; 500/500 = 100.00%; 6410/6410 = 100.00%; G:\GhidraBackups\BEA_20260604-143442_post_wave1091_credits_renderer_review_verified; comment/tag normalization.
