# Ghidra Weapon / Burst Signature Tranche - 2026-05-09

Status: public-safe saved-Ghidra signature/comment evidence

## Objective

Refine the current weapon/burst seed cluster without overclaiming source identity or runtime stealth behavior. This tranche hardens only the two entries whose calling convention and parameter shape were supported by read-back evidence, while keeping the inner projectile-burst body and shared fallback dispatcher explicitly provisional.

## Saved Ghidra Changes

| Address | Saved name | Result |
| --- | --- | --- |
| `0x00506930` | `CWeapon__HandleFireBurstEvent` | Hardened from `undefined` to `void __thiscall CWeapon__HandleFireBurstEvent(void * this, void * eventRecord)`. |
| `0x00505f70` | `CWeapon__scalar_deleting_dtor` | Hardened from stale `param_N` shape to `void * __thiscall CWeapon__scalar_deleting_dtor(void * this, byte flags)`. |
| `0x005069f0` | `CEngine__SpawnProjectileBurstFromCurrentPreset` | Left provisional; saved comment keeps owner/name and `param_N` signature debt explicit. |
| `0x00506010` | `CGeneralVolume__SpawnBurstFromPresetWithFallback` | Left provisional; saved comment keeps owner/name and `param_N` signature debt explicit. |

## Commands

Focused test/probe:

```powershell
py -3 tools\ghidra_weapon_burst_signature_tranche_probe_test.py
py -3 tools\ghidra_weapon_burst_signature_tranche_probe.py --check
py -3 -m py_compile tools\ghidra_weapon_burst_signature_tranche_probe.py tools\ghidra_weapon_burst_signature_tranche_probe_test.py
cmd.exe /c npm run test:ghidra-weapon-burst-signature-tranche
```

Serialized Ghidra read-back and mutation:

```powershell
bash tools/run_ghidra_headless_postscript.sh ExportFunctionMetadataByAddress.java subagents/ghidra-static-reaudit/signature-debt-tranche4/current/addresses.txt subagents/ghidra-static-reaudit/signature-debt-tranche4/current/metadata.tsv
bash tools/run_ghidra_headless_postscript.sh ExportFunctionsByAddressDecompile.java subagents/ghidra-static-reaudit/signature-debt-tranche4/current/addresses.txt subagents/ghidra-static-reaudit/signature-debt-tranche4/current/decompile 100
bash tools/run_ghidra_headless_postscript.sh ExportXrefsForAddresses.java subagents/ghidra-static-reaudit/signature-debt-tranche4/current/addresses.txt subagents/ghidra-static-reaudit/signature-debt-tranche4/current/xrefs.tsv
bash tools/run_ghidra_headless_postscript.sh ExportInstructionsAroundAddresses.java subagents/ghidra-static-reaudit/signature-debt-tranche4/current/addresses.txt subagents/ghidra-static-reaudit/signature-debt-tranche4/current/instructions.tsv 0 80
bash tools/run_ghidra_headless_postscript.sh ApplyWeaponBurstSignatureTranche.java dry
bash tools/run_ghidra_headless_postscript.sh GhidraApplyFunctionCommentsFromTsv.java subagents/ghidra-static-reaudit/signature-debt-tranche4/current/comments.tsv dry
bash tools/run_ghidra_headless_postscript.sh ApplyWeaponBurstSignatureTranche.java apply
bash tools/run_ghidra_headless_postscript.sh GhidraApplyFunctionCommentsFromTsv.java subagents/ghidra-static-reaudit/signature-debt-tranche4/current/comments.tsv apply
bash tools/run_ghidra_headless_postscript.sh ExportFunctionMetadataByAddress.java subagents/ghidra-static-reaudit/signature-debt-tranche4/current/addresses.txt subagents/ghidra-static-reaudit/signature-debt-tranche4/current/metadata_readback.tsv
bash tools/run_ghidra_headless_postscript.sh ExportFunctionsByAddressDecompile.java subagents/ghidra-static-reaudit/signature-debt-tranche4/current/addresses.txt subagents/ghidra-static-reaudit/signature-debt-tranche4/current/decompile_readback 100
bash tools/run_ghidra_headless_postscript.sh ExportFunctionQualitySnapshot.java subagents/ghidra-static-reaudit/queue/current/functions_quality.tsv
```

## Result

```text
Ghidra weapon/burst signature tranche probe
Status: PASS
Targets: 4; hardened: 2; provisional: 2; xref rows: 14; instruction rows: 324

Ghidra static re-audit queue probe
Status: PASS
Total functions: 5866
Commentless functions: 5482
Undefined signatures: 2078
Param signatures: 2563
Uncertain owner names: 0
Address-suffixed helpers: 0
Address-suffixed wrappers: 0
```

## Process Notes

- An initial instruction export was accidentally overlapped with the xref export and failed with a Ghidra project `LockException`; the export was rerun serially and passed with `324` instruction rows.
- An initial comment TSV dry-run used literal `t` separators and failed with bad rows before any apply; the TSV was corrected, the dry-run was repeated cleanly, and only then were comments applied.

## What This Proves

- The saved `0x00506930` signature now models the event-handler shape: `this` plus a pointer-like event/context record whose `+4` event id is checked against `0x1389`.
- The saved `0x00505f70` signature now models the scalar-deleting destructor shape: `this` plus byte deletion flags, with optional object free and this-pointer return.
- The current saved comments preserve that `0x005069f0` and `0x00506010` remain provisional and still carry `param_N` signature debt.
- The refreshed queue reduced undefined signatures from `2079` to `2078` and `param_N` signatures from `2564` to `2563`.

## What This Does Not Prove

- This does not identify exact source `CWeapon::Fire`.
- This does not identify exact source `CBattleEngine::WeaponFired`.
- This does not close `weapon_fire_breaks_stealth`.
- This does not prove runtime cloak activation, runtime fire-while-cloaked behavior, or any stealth reset behavior.
- This does not finalize owner/name/signature for the inner projectile-burst body or shared fallback dispatcher.
- This does not add tags, recover structures, recover local names, patch or launch `BEA.exe`, or mutate the installed game.

## Privacy / Release Safety

This note includes repo-relative paths, public addresses, function names, aggregate counts, command summaries, and proof boundaries only. Raw decompile output, runtime proof, screenshots, frame data, copied saves, copied executables, private install paths, and generated JSON remain under ignored `subagents/`.
