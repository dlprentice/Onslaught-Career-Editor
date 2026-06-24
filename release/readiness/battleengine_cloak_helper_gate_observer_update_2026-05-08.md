# BattleEngine Cloak Helper Gate Observer Update - 2026-05-08

Status: public-safe observer hardening, not runtime proof

## Objective

Prepare the next copied-profile cloak proof to explain why decoded `Special function` inputs reached `CGeneralVolume__Update4ACLatchFromHeightAndA0` but did not activate the candidate latch.

The prior observer logged entry/exit latch fields. Fresh decompile inspection shows the candidate activation path also depends on two linked-object gate inputs:

- linked object `+0x2c` must be less than or equal to the candidate `this+0xfc` value
- linked object `+0xa0` must be greater than the threshold constant at `0x005d856c`

## What Changed

`tools/runtime-probes/cloak-latch-observer.cdb.txt` now logs these extra read-only fields at helper entry and both known return paths:

- linked object pointer from `this+0x4b0`
- linked object `+0x2c`
- linked object `+0xa0`
- threshold raw value at `0x005d856c`

`tools/cloak_runtime_observer_log_probe.py` now accepts both the old compact log shape and the new gate-aware shape. For gate-aware events it decodes the raw float fields and reports whether the two candidate activation gate inputs passed or which gate blocked the pair.

## Validation

Commands:

```powershell
py -3 -m py_compile tools\cloak_runtime_observer_log_probe.py
npm run test:cloak-runtime-observer-log
powershell -ExecutionPolicy Bypass -File .\tools\start_cdb_server.ps1 -CommandFile .\tools\runtime-probes\cloak-latch-observer.cdb.txt -PrintOnly
```

Expected result:

- parser self-test passes for activation, noisy same-line events, no-event logs, and gate-blocked pairs
- print-only CDB command generation passes without attaching to a process
- no `BEA.exe` launch, CDB attach, executable patch, Ghidra mutation, or runtime proof is performed in this update

## What This Enables

The next copied-profile observer can distinguish:

- wrong key or no helper reachability
- helper reached but linked/energy gate blocked activation
- helper reached and gate inputs passed but latch still did not activate
- helper reached and candidate activation was observed

That distinction is required before sending any weapon-fire input for the remaining fire-while-cloaked question.

## Not Proven

- Runtime cloak activation.
- Exact source-to-retail identity for `CBattleEngine::HandleCloak`, `Cloak`, `Decloak`, `Render`, or `WeaponFired`.
- Retail `RF_CLOAKED` render-flag identity.
- Weapon-fired stealth reset identity.
- Runtime fire-while-cloaked behavior.
- Ghidra rename-map mutation or project semantic promotion.

## Privacy / Release Safety

This report is public-safe. It includes only repo-relative command/script names, public addresses already present in project evidence, candidate offset names, and proof boundaries. Future raw CDB logs and runtime proof JSON must remain ignored under `subagents/`.
