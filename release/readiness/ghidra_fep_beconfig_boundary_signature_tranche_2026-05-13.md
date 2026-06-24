# Ghidra FEPBEConfig Boundary / Signature Tranche - 2026-05-13

Status: GREEN public-safe saved-Ghidra evidence

## Summary

Serialized headless dry/apply/read-back recovered and hardened `22` FrontEnd Battle Engine configuration targets around `FEPBEConfig.cpp` / `CFEPMultiplayerStart` helper context. This pass corrects the stale mid-prologue init note from `0x0044fa93` to the saved `0x0044fa90` function boundary, repairs the Ghidra function body for that init target, recovers four adjacent `CFEPBEConfig` vtable-slot function starts, and hardens the existing config/profile/weapon helper signatures and comments.

| Address | Saved name | Public-safe static evidence |
| --- | --- | --- |
| `0x0044eab0` | `CFEPMultiplayerStart__GetConfigIdByIndex` | Walks the selected config list and returns the config id at `config_index`. |
| `0x0044eb30` | `CFEPMultiplayerStart__SetConfigDescriptionByIndex` | Resolves config names, maps type ids to text strings, and has an `Unknown Configuration` fallback. |
| `0x0044ecf0` | `CFEPMultiplayerStart__GetConfigCount` | Returns the selected BattleEngine profile config count after matching the current selection global. |
| `0x0044ed40` | `CFEPMultiplayerStart__LookupProfileField5CBySelectionIndex` | Resolves a config name and returns the matched profile/config record field at `+0x5c`. |
| `0x0044eea0` | `CFEPMultiplayerStart__LookupProfileField4CPlusFlagBySelectionIndex` | Resolves a config name and returns field `+0x4c` adjusted by the flag at `+0x60`. |
| `0x0044f030` | `CFEPBEConfig__GetWeaponProperty` | Primary weapon-property lookup through the selected profile list and weapon record fields `+0x10/+0x11/+0x12`. |
| `0x0044f300` | `CFEPBEConfig__GetWeaponPropertyAlt` | Alternate weapon-property lookup through the matched config record alternate list at `+0x50/+0x58`. |
| `0x0044f530` | `CFEPBEConfig__PlayWeaponSound` | Primary weapon sound/text helper using weapon-record field `+0x0f`, with `Unknown Weapon` fallback. |
| `0x0044f830` | `CFEPBEConfig__PlayWeaponSoundAlt` | Alternate weapon sound/text helper using the alternate weapon list and the same fallback path. |
| `0x0044fa90` | `CFEPBEConfig__Init` | Corrected function boundary at the SEH prologue before the `beconf::init() 0-5` trace strings; saved body covers `0x0044fa90-0x0044fd9f`. |
| `0x0044fda0` | `CFEPBEConfig__Cleanup` | Frees owned frontend/config-entry storage and delegates per-entry cleanup. |
| `0x0044fdf0` | `CFEPBEConfig__CleanupSquads` | Clears a config entry's squad/name pointer set at `+0x14`. |
| `0x0044fe70` | `CFEPBEConfig__Load` | Corrected to `__thiscall` with `ECX=this` and one `mem_buffer` stack argument; loads one config entry. |
| `0x00450010` | `CFEPBEConfig__UpdateTransitionTimers` | Recovered vtable slot 1 boundary; updates transition/timer fields and returns with `RET 0x4`. |
| `0x00450090` | `CFEPBEConfig__ButtonPressed` | Recovered vtable slot 2 boundary; dispatches frontend button/action codes and updates selected config indices. |
| `0x00450390` | `CFEPBEConfig__RenderPreCommon` | Recovered vtable slot 3 boundary for common selection marker rendering. |
| `0x00450400` | `CFEPBEConfig__PushProjectionMatrixForRender` | Saves the active projection matrix and installs CFEPBEConfig render projection values. |
| `0x00450440` | `CFEPBEConfig__PopProjectionMatrixAfterRender` | Restores the saved projection matrix and marks projection state dirty. |
| `0x00450460` | `CFEPMultiplayerStart__RenderConfigPipRow` | Renders rating pips from a rounded `1-5` count, color bands, alpha, and surface calls. |
| `0x004505b0` | `CFEPBEConfig__Render` | Recovered vtable slot 4 boundary for the BattleEngine config page render body. |
| `0x00451930` | `CFEPBEConfig__FindEntryByName` | Linear lookup over the global config/profile list by record name at `+0xa8`. |
| `0x004519c0` | `CFEPBEConfig__ResetTimestampAndModeFlag` | Renamed from the generic vfunc label; stores platform time, clears a mode flag, and conditionally re-enables it. |

## Validation

- `RepairFepBeConfigInitListing.java` body repair verified `CFEPBEConfig__Init` has decoded instructions and body `[[0044fa90, 0044fd9f]]` after an intermediate empty-body Ghidra state was caught by decompile read-back.
- `ApplyFepBeConfigBoundarySignatureTranche.java` final dry/apply: `targets=22 changed_or_would_change=22 failed=0`, with `REPORT: Save succeeded`.
- Read-back exports verified `22` metadata rows, `22` decompile exports, `53` xref rows, `6534` instruction rows, `22` tag rows, and `12` vtable-slot rows.
- `py -3 tools\ghidra_fep_beconfig_boundary_signature_probe_test.py` passed with `2/2` tests.
- `py -3 -m py_compile tools\ghidra_fep_beconfig_boundary_signature_probe.py tools\ghidra_fep_beconfig_boundary_signature_probe_test.py` passed.
- `cmd.exe /c npm run test:ghidra-fep-beconfig-boundary-signature` passed with focused probe status `PASS` and `22` targets.
- Whole-database quality refresh reports `6013` functions, `1292` commented functions, `4721` commentless functions, `1948` undefined signatures, and `1992` `param_N` signatures.
- Current confirmation proxies are telemetry only: comment-backed `1292/6013 = 21.49%` and strict clean-signature `1230/6013 = 20.46%`. These values are not milestones or completion gates; the target remains as close to `100%` evidence-grade static RE as possible.
- The actual live Ghidra project backup was verified at `G:\GhidraBackups\BEA_20260513_080854_post_wave367_fep_beconfig_verified` with `19` files, `153357191` bytes, and `HashDiffCount=0`.

## Claim Boundary

This is saved static Ghidra boundary/name/signature/comment/tag evidence only. It does not prove exact Stuart-source method identity, concrete structure layouts, local variable/type recovery, runtime frontend/config/render/input behavior, BEA launch behavior, game patching, or rebuild parity. The `0x0044fa90` correction supersedes the old `0x0044fa93` mid-prologue note, but adjacent frontend classes and config records still need their own evidence-grade review.
