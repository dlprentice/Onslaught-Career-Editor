# Ghidra Frontend Controls Signature Tranche - 2026-05-13

Status: GREEN public-safe static RE evidence.

## Summary

Serialized headless dry/apply/read-back hardened `13` frontend controls and control-binding targets in the saved Steam `BEA.exe` Ghidra project. The pass corrects one owner overclaim at `0x00453ac0`, hardens the `ControlsUI__RenderBindingsList` thiscall shape, records the remap list/capture/write helpers, and tags the tranche as `frontend-controls-wave370`.

## Saved Targets

| Address | Saved Ghidra state | Evidence summary |
| --- | --- | --- |
| `0x00453460` | `OptionsEntries__InitDefaultDualBindingsTable` | Initializes the default dual-binding options-entry table at `DAT_00677af0`, including `16` normal entries and sentinel entries. |
| `0x00453970` | `CControllerDefinition__InitDefaults` | Initializes control-definition defaults/vtable for the remap lifecycle helper object. |
| `0x004539b0` | `CControllerDefinition__scalar_deleting_dtor` | Scalar-deleting destructor wrapper with `flags` argument and optional free path. |
| `0x004539d0` | `CControllerDefinition__dtor` | Destructor body with key-sink reset gate and owned pointer cleanup. |
| `0x00453ac0` | `SharedVFunc__NoOp_Ret0C` | Corrects the older controller-specific label; instruction read-back is a zero-body `RET 0x0c`, and vtable/data refs include unrelated script/datatype tables. |
| `0x00453ad0` | `CControllerDefinition__RenderBindingsAndPollRemapInput` | Control-definition render/poll helper that calls the binding-list renderer. |
| `0x00455010` | `ControlsUI__RenderBindingsList` | Thiscall binding-list renderer with `columnIndex`, row/list coordinates, and interactive flag; evidence includes calls to dispatch, row lookup, and remap capture. |
| `0x00456080` | `Controls__BeginRemapCapture` | Begins remap capture by clearing remap-active globals and scheduling callback state. |
| `0x004565d0` | `OptionsEntries__SetBindingSlot` | Writes one binding slot `(field0, device_code, scan, vk)` into an options entry. |
| `0x00456610` | `CControllerDefinition__GetWidth` | Constant/control-definition getter with saved `this` signature. |
| `0x00456620` | `CControllerDefinition__GetRowHeight` | Constant/control-definition getter with saved `this` signature. |
| `0x00456630` | `CControllerDefinition__GetFlag1C` | Reads the control-definition byte flag at `this+0x1c`. |
| `0x00456640` | `CControllerDefinition__ClearFlag1C` | Clears the control-definition byte flag at `this+0x1c`. |

## Validation

| Check | Result |
| --- | --- |
| Focused probe tests | `py -3 tools\ghidra_frontend_controls_signature_probe_test.py` passed `2/2`. |
| Python compile | `py -3 -m py_compile tools\ghidra_frontend_controls_signature_probe.py tools\ghidra_frontend_controls_signature_probe_test.py` passed after serial rerun. |
| Headless apply | `ApplyFrontendControlsSignatureTranche.java` dry/apply both reported `targets=13 changed_or_would_change=13 failed=0`; apply printed `REPORT: Save succeeded`. |
| Read-back exports | Metadata `13`, decompile `13`, xrefs `26`, instruction rows `2145`, tags `13`, vtable slots `64`, callsite instructions `252`, and full `ControlsUI__RenderBindingsList` instructions `1251`. |
| Focused package probe | `cmd.exe /c npm run test:ghidra-frontend-controls-signature` passed with targets `13`, vtable evidence hits `10`, xref evidence hits `26`, instruction evidence hits `14`, stale token hits `0`, overclaim hits `0`. |
| Whole-database baseline | `cmd.exe /c npm run test:ghidra-static-reaudit-baseline` passed with `6020` total functions, `0` legacy weak names, `1980` `param_N` signatures, and `1939` undefined signatures. |
| Whole-database queue | `cmd.exe /c npm run test:ghidra-static-reaudit-queue` passed with `1324` commented functions and `4696` commentless functions. |
| Current proxies | Comment-backed `1324/6020 = 21.99%`; strict clean-signature `1262/6020 = 20.96%`. These are telemetry only, not milestones. |
| Ghidra backup | Live `BEA.gpr`/`BEA.rep` backup verified at `G:\GhidraBackups\BEA_20260513_100816_post_wave370_frontend_controls_verified` with `19` files, `153422727` bytes, and `HashDiffCount=0`. |

## Claim Boundary

This is saved static retail Ghidra name/signature/comment/tag refinement. It does not prove exact Stuart-source method identities, concrete controller/control-definition layouts, local variable or structure type recovery, runtime remap input behavior, frontend UI behavior, BEA launch behavior, game patching, or rebuild parity.
