# Ghidra FEPMultiplayerStart Embedded Helper Tranche - 2026-05-14

Status: public-safe static evidence note

This note records a serialized static Ghidra correction wave for nine `CFEPMultiplayerStart` embedded-helper targets around the multiplayer start page. It documents saved Ghidra metadata only. It does not include private decompile excerpts, private screenshots, copied executables, copied saves, raw runtime evidence, or private asset payloads.

## What Changed

| Address | Saved state | Public-safe evidence summary |
| --- | --- | --- |
| `0x00459810` | `void __thiscall CFEPMultiplayerStart__SubObj39B8__QueuePageId(void * this, int page_id)` | Preserved the offset-stable helper name and saved a proof-boundary comment. Static read-back shows the helper queues the requested page id through `+0xc`, `+0x10`, and `+0x8` fields and is called from `CFrontEnd__Init`. |
| `0x00459920` | `void * __thiscall CFEPMultiplayerStart__SubObj8848__ctor(void * this)` | Corrected the saved calling convention from generic fastcall-style metadata to ECX-this constructor shape. Static read-back shows vtable `0x005db4fc`, seeded level-code constants, row count setup, and a cleared 300-entry highlight grid. |
| `0x004599a0` | `int __thiscall CFEPMultiplayerStart__SubObj8848__Init(void * this)` | Corrected the saved calling convention from generic fastcall-style metadata to ECX-this init shape. Static read-back shows current level-code matching, row/column selection state, scroll offset setup, and timestamp refresh. |
| `0x00459a60` | `void __thiscall CFEPMultiplayerStart__SubObj8848__ActiveNotification(void * this, int from_page)` | Added saved comment/tag evidence for the active-notification hook. Static read-back shows page 5/6 highlight restore and inactivity timer reset. |
| `0x00459aa0` | `void __thiscall CFEPMultiplayerStart__SubObj8848__TransitionNotification(void * this, int from_page)` | Added saved comment/tag evidence for the transition-notification hook. Static read-back shows timestamp update, 300-entry grid clear, and page 5/6 highlight restore. |
| `0x00459b00` | `void __thiscall CFEPMultiplayerStart__SubObj8848__Process(void * this, int menu_state)` | Added saved comment/tag evidence for the process hook. Static read-back shows scroll easing, selection highlight fade updates, inactivity counting, and fallback to page `0x0c`. |
| `0x00459c10` | `void __thiscall CFEPMultiplayerStart__SubObj8848__ButtonPressed(void * this, int button)` | Added saved comment/tag evidence for the button handler. Static read-back shows horizontal/vertical navigation, select/back transitions, sound feedback, selected-level update, and animation timestamp refresh. |
| `0x00459e50` | `void __stdcall CFEPMultiplayerStart__SubObj8848__RenderPreCommon(float transition, int dest)` | Corrected the saved signature from the stale `void * this, float transition` shape. Instruction read-back shows `RET 0x8`, transition stack-argument use, no saved `this` use, and the scaled video-quad backdrop path. |
| `0x00459ee0` | `void __thiscall CFEPMultiplayerStart__SubObj8848__Render(void * this, float transition, int dest)` | Added saved comment/tag evidence for the render hook. Static read-back shows selection-grid rendering, level and episode text resolution, the `E3 2002` build/progress string, help prompts, overlay effects, and title bar rendering. |

The `SubObjXXXX` labels remain intentional offset-stable names because `FEPMultiplayerStart.cpp` is absent from the current Stuart source snapshot. This wave did not force a friendlier class name without source parity or stronger RTTI evidence.

## Validation

- `ApplyFEPMultiplayerStartSubObjWave399.java` dry run: expected no mutation and reported nine skipped targets.
- `ApplyFEPMultiplayerStartSubObjWave399.java` apply run: saved the project and reported nine updated targets with no renames.
- Metadata/decompile/xref/tag/instruction/vtable read-back is stored under ignored `subagents/`.
- Focused probe: `tools/ghidra_fepmultiplayerstart_subobj_wave399_probe.py --check`.
- Self-test: `tools/ghidra_fepmultiplayerstart_subobj_wave399_probe_test.py`.
- Refreshed static queue: `6028` functions, `1529` commented functions, `4499` commentless functions, `1913` undefined signatures, and `1864` `param_N` signatures.
- Current confirmation proxies remain telemetry only: comment-backed `1529/6028 = 25.36%`, strict clean-signature `1464/6028 = 24.29%`.
- Live Ghidra backup verified at `[maintainer-local-ghidra-backup-root]\BEA_20260514_030115_post_wave399_fepmultiplayerstart_subobj_verified` with `19` files, `154766215` bytes, and `HashDiffCount=0`.

## Claim Boundary

This tranche improves saved static Ghidra comments, tags, and signatures for the multiplayer start embedded helper cluster. It does not prove runtime multiplayer behavior, does not prove exact source identity, does not recover concrete structure types/locals, does not launch or patch `BEA.exe`, and does not prove rebuild parity.
