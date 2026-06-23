# Ghidra InitThing Load Wave424 Static Correction

Status: public-safe static Ghidra evidence note
Date: 2026-05-14
Scope: saved retail `BEA.exe` Ghidra signature/comment/tag correction

## Summary

Wave424 serialized headless dry/apply/read-back hardened the saved Ghidra metadata for `CInitThing__LoadFromMemBuffer` at `0x0040e280`. The pass keeps the existing function boundary and name, replaces generic `param_1` / `param_2` signature debt with evidence-backed `version` and `mem_buffer` parameters, refreshes the proof-boundary comment, and adds Wave424 tags.

This is public-safe static evidence only. It does not launch or patch `BEA.exe`, does not mutate the installed Steam game, and does not include raw decompile text or private runtime proof.

## Saved Ghidra Change

| Address | Previous saved state | Current saved state | Static evidence summary |
| --- | --- | --- | --- |
| `0x0040e280` | `void __thiscall CInitThing__LoadFromMemBuffer(void * this, int param_1, int param_2)` | `void __thiscall CInitThing__LoadFromMemBuffer(void * this, int version, void * mem_buffer)` | Retail instruction/decompile evidence reads the first stack argument as a 16-bit version, branches on the same version thresholds as Stuart-source `CInitThing::Load(short inVersion, CMEMBUFFER &inFile)`, reads through `CDXMemBuffer__Read`, and fills transform/orientation fields, script/name/spawn-script strings at `+0xac/+0x1ac/+0x2ac`, and active/attach flags at `+0x3ac/+0x3b0`. |

## Validation

| Command or check | Result | Important output |
| --- | --- | --- |
| `py -3 tools\ghidra_initthing_load_wave424_probe_test.py` | PASS | Focused tests passed `4/4`. |
| `py -3 -m py_compile tools\ghidra_initthing_load_wave424_probe.py tools\ghidra_initthing_load_wave424_probe_test.py` | PASS | Both focused Python files compile. |
| Pre-apply `cmd.exe /c npm run test:ghidra-initthing-load-wave424` | FAIL, expected red | Probe rejected the missing post-apply artifacts before saved Ghidra apply/read-back existed. |
| Headless `ApplyInitThingLoadWave424.java` dry run | PASS | `updated=0 skipped=1 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`, with `REPORT: Save succeeded`; dry logic made no metadata mutation. |
| Headless `ApplyInitThingLoadWave424.java` apply | PASS | `updated=1 skipped=0 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`, with `REPORT: Save succeeded`. |
| Post-apply metadata/tag/xref/instruction/decompile read-back | PASS | Verified `1` metadata row, `1` tag row, `1` xref row, `65` instruction rows, and `1` decompile export. |
| Post-apply `cmd.exe /c npm run test:ghidra-initthing-load-wave424` | PASS | Focused probe accepted the saved signature, comment, tags, read-back tokens, caller xref, and proof-boundary wording. |
| Headless whole-database quality snapshot | PASS | `total_functions=6043`; `commented_functions=1671`. |
| `cmd.exe /c npm run test:ghidra-static-reaudit-queue` | PASS | Queue reports `6043` functions, `4372` commentless functions, `1861` undefined signatures, `1808` `param_N` signatures, and zero broad uncertain/helper/wrapper debt. |
| Live Ghidra project backup | PASS | Private post-mutation backup verified `19` files, `155159431` bytes, `HashDiffCount=0`, `MissingCount=0`. |

## Current Queue Telemetry

The refreshed static re-audit queue now reports:

- Total function objects: `6043`
- Functions with non-empty function comments: `1671`
- Commentless function objects: `4372`
- `undefined` signatures: `1861`
- Signatures still using `param_N`: `1808`
- Comment-backed telemetry proxy: `1671/6043 = 27.65%`
- Strict clean-signature telemetry proxy: `1609/6043 = 26.63%`

These are triage proxies only. They are not certification and are not completion gates.

## Not Proven

This wave does not prove runtime level loading, runtime object spawning, exact `CMEMBUFFER` concrete type/layout, full `CInitThing` class layout, exact local variable names/types, source-to-retail rebuild parity, BEA launch behavior, game patching, or runtime gameplay behavior.
