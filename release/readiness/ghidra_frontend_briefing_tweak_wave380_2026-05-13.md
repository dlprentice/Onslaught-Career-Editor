# Ghidra Frontend Briefing/Tweak Wave380 Readiness Note

Status: public-safe static RE evidence
Date: 2026-05-13

## Summary

Wave380 serialized a focused headless dry/apply/read-back pass over `5` saved Ghidra targets in the frontend briefing and CTweak helper area. The pass corrected one briefing vtable-slot label plus four CTweak helper labels/signatures/comments/tags. This is saved static retail Ghidra evidence only.

## Saved Targets

| Address | Saved signature | Evidence summary |
| --- | --- | --- |
| `0x00452430` | `void __thiscall CFEPBriefing__ResetTimerAndClearState(void * this, int reset_state)` | Refreshes a timer from system time plus a static constant, stores it at `this+0x04`, and clears `this+0x08`. |
| `0x004530a0` | `void __fastcall CTweak__dtor_base_thunk_004530a0(void * this)` | One-instruction jump thunk to `CTweak__dtor_base` at `0x005286b0`, reached from static cleanup stubs. |
| `0x00528690` | `void * __thiscall CTweak__ctor_base(void * this, void * callback_context)` | Installs the base purecall vtable, stores `callback_context` at `this+0x08`, and links the node into `DAT_0089c018`. |
| `0x005286b0` | `void __fastcall CTweak__dtor_base(void * this)` | Resets the base vtable and unlinks the receiver from the `DAT_0089c018` list. |
| `0x00528b20` | `void * __thiscall CTweakInt_SetNumViewpoints__ctor(void * this, void * callback_context, int initial_value)` | Derived int tweak constructor; installs `PTR_CEngine__SetNumViewpoints_005e4aa4` and stores `initial_value` at `this+0x0c`. |

## Validation

- `py -3 tools\ghidra_frontend_briefing_tweak_wave380_probe_test.py` initially failed red before implementation with `ModuleNotFoundError`.
- `py -3 tools\ghidra_frontend_briefing_tweak_wave380_probe_test.py` passed with `2/2` tests.
- `cmd.exe /c npm run test:ghidra-frontend-briefing-tweak-wave380` passed with status `PASS`, `5` targets, `6` xref evidence hits, and `18` instruction evidence hits.
- `py -3 -m py_compile tools\ghidra_frontend_briefing_tweak_wave380_probe.py tools\ghidra_frontend_briefing_tweak_wave380_probe_test.py` passed.
- Headless dry/apply reported dry `updated=0 skipped=5 renamed=0 would_rename=5 missing=0 bad=0` and apply `updated=5 skipped=0 renamed=5 would_rename=0 missing=0 bad=0`, with `REPORT: Save succeeded`.
- Read-back verified `5` metadata rows, `5` decompile exports, `53` xref rows, `185` instruction rows, and `5` tag rows.
- The refreshed live queue reports `6026` functions, `1393` commented functions, `4633` commentless functions, `1939` undefined signatures, and `1934` `param_N` signatures.
- Current confirmation proxies are telemetry only: comment-backed `1393/6026 = 23.12%`, strict clean-signature `1328/6026 = 22.04%`.
- The live Ghidra project backup was verified at `G:\GhidraBackups\BEA_20260513_152919_post_wave380_frontend_briefing_tweak_verified` with `19` files, `153652103` bytes, and `HashDiffCount=0`.

## Not Proven

- Runtime frontend briefing behavior is not proven by this static pass.
- Runtime tweak registration, cleanup, or viewpoint behavior is not proven.
- Exact Stuart-source identity for CTweak helpers is not proven.
- Concrete class layouts, local variable names, and structure types remain open.
- BEA launch behavior, executable patching, packaged-app behavior, and rebuild parity remain unproven.
