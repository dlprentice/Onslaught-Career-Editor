# Ghidra BattleEngineData / Config Signature Tranche - 2026-05-09

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 live correction closeout:** Historical record; `0x0040f890` comment correction. The original text below remains provenance rather than current semantic authority. It is superseded only where confirmed. Use the [closeout](../../reverse-engineering/binary-analysis/ghidra-full-reaudit-closeout-2026-07-13.md); final per-address decisions and exact before/after metadata are in `reverse-engineering/binary-analysis/ghidra-reviewed-correction-decisions-2026-07-13.jsonl` and `reverse-engineering/binary-analysis/ghidra-reviewed-correction-plan-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

## Summary

This wave reparsed seven already named functions in the BattleEngine configuration and `CBattleEngineData` load/default-data cluster. Fresh metadata, decompile, xref, instruction, callsite-instruction, and full-load-body exports showed the saved names were useful, but the signatures still carried stale or incomplete argument evidence.

A serial headless dry/apply pass saved signatures and proof-boundary comments for the configuration string table helpers and the `CBattleEngineData` constructor, initialise, shutdown, and `CMEMBUFFER` load path. Fresh read-back plus a focused probe then verified the saved signatures and the callsite/return-arity evidence.

## Corrected Targets

| Address | Saved signature after correction | Evidence boundary |
| --- | --- | --- |
| `0x0040f140` | `void __cdecl BattleEngineConfigurations__ShutDown(void)` | Clears the global configuration count/table and frees stored names. Runtime load behavior and concrete global type modeling remain unproven. |
| `0x0040f180` | `void __cdecl BattleEngineConfigurations__Load(void * memBuffer)` | `CWorld__LoadWorldHeader` pushes the `memBuffer` argument and caller-cleans with `ADD ESP, 0x4`; the body clears the table and reads length-prefixed names. Concrete `CMEMBUFFER` structure typing remains unproven. |
| `0x0040f260` | `void __cdecl BattleEngineConfigurations__Skip(void * memBuffer)` | Same caller-clean argument evidence as `Load`; the body reads and frees temporary length-prefixed names without storing them in the global table. |
| `0x0040f520` | `void * __thiscall CBattleEngineData__ctor(void * this)` | Constructor-style body initializes embedded pointer-set members and returns `this`. Concrete `CBattleEngineData` layout remains unproven. |
| `0x0040f590` | `void __fastcall CBattleEngineData__Initialise(void * battleEngineData)` | Default-data setup body copies source-aligned strings such as `Standard`, `Vulcan Cannon 1`, and `cockpit2.msh`, and initializes stealth/default profile fields. Runtime profile behavior remains unproven. |
| `0x0040f890` | `void __fastcall CBattleEngineData__Shutdown(void * battleEngineData)` | Cleanup body frees the configuration name, drains weapon pointer sets, and frees owned effect/cockpit strings. Destructor completeness and concrete layout remain unproven. |
| `0x0040f980` | `void __thiscall CBattleEngineData__LoadFromMemBuffer(void * this, void * memBuffer)` | Full instruction export shows two `RET 0x4` exits; the body calls shutdown before versioned `DXMemBuffer__ReadBytes` field and weapon-list loading. Concrete layout and runtime profile behavior remain unproven. |

## Validation

- Focused tests: `py -3 tools\ghidra_battleengine_data_config_signature_tranche_probe_test.py` passed `2/2`.
- Python compile: `py -3 -m py_compile tools\ghidra_battleengine_data_config_signature_tranche_probe.py tools\ghidra_battleengine_data_config_signature_tranche_probe_test.py` passed.
- Headless dry/apply: `updated=0 skipped=7 missing=0 bad=0`, then `updated=7 skipped=0 missing=0 bad=0`.
- Fresh metadata/decompile read-back: `7/7` targets.
- Fresh xref read-back: `12` rows.
- Fresh instruction read-back: `1827` rows across the seven targets.
- Fresh callsite-instruction read-back: `105` rows, including `CWorld__LoadWorldHeader` caller-clean evidence for `BattleEngineConfigurations__Load` and `BattleEngineConfigurations__Skip`.
- Fresh full-load instruction read-back: `1201` rows with two `RET 0x4` hits in `CBattleEngineData__LoadFromMemBuffer`.
- Focused probe: `cmd.exe /c npm run test:ghidra-battleengine-data-config-signature-tranche` passed with `7` targets, `0` `param_N` signature hits, `0` undefined signatures, and `2` load `RET 0x4` hits.
- Refreshed queue probe: `5866` functions, `503` commented functions, `5363` commentless functions, `2071` undefined signatures, and `2449` `param_N` signatures.

## Non-Claims

This is saved Ghidra signature/comment refinement only. It does not prove concrete `CBattleEngineData`, `BattleEngineConfigurations`, `CMEMBUFFER`, `CSPtrSet`, weapon-list, string-store, or global-table layouts; tag/local-name/type completeness; runtime profile loading; runtime Sniper/cloak behavior; BEA launch behavior; game patching; exhaustive source identity for every field; or rebuild parity.
