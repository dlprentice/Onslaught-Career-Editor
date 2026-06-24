# Ghidra Atmospheric Signature Tranche - 2026-05-09

Status: public-safe saved-Ghidra signature/comment evidence, not final type/source/runtime proof

## Objective

Begin consuming the broad signature debt that remains after the name-confidence helper/wrapper tail reached zero. This pass originally hardened four then-current CAtmospheric lifecycle/list helper signatures whose decompile shapes exposed stable object-pointer parameters and simple list behavior. A later CAnimal owner correction superseded the `0x00404010` CAtmospheric attribution, so current Atmospheric tooling treats only the three remaining CAtmospheric targets as active.

## Inputs

- Original targets:
  - `0x00404010` `CAtmospheric__Destructor` (superseded on 2026-05-09 by `CAnimal__dtor_base`)
  - `0x004046d0` `CAtmospheric__Constructor`
  - `0x00404920` `CAtmospheric__Link`
  - `0x00404960` `CAtmospheric__Unlink`
- Raw evidence root: `subagents/ghidra-static-reaudit/signature-debt-tranche1/current/`
- Signature script: `tools/ApplyAtmosphericSignatureTranche.java`
- Probe: `tools/ghidra_atmospheric_signature_tranche_probe.py`
- Probe test: `tools/ghidra_atmospheric_signature_tranche_probe_test.py`

## Commands

Focused validation:

```powershell
py -3 tools\ghidra_atmospheric_signature_tranche_probe_test.py
py -3 tools\ghidra_atmospheric_signature_tranche_probe.py --check
py -3 -m py_compile tools\ghidra_atmospheric_signature_tranche_probe.py tools\ghidra_atmospheric_signature_tranche_probe_test.py
cmd.exe /c npm run test:ghidra-atmospheric-signature-tranche
cmd.exe /c npm run test:ghidra-static-reaudit-queue
```

Mutation/read-back summary:

- Read-only metadata/decompile/xref/instruction exports captured the first undefined-signature tranche.
- Headless signature dry/apply updated the then-current four-target tranche.
- Headless comment dry/apply saved proof-boundary comments for the same then-current four targets.
- Metadata/decompile/xref read-back verified the saved signatures/comments.
- Later Wave 284 CAnimal evidence superseded the `0x00404010` CAtmospheric owner attribution; `tools/ApplyAtmosphericSignatureTranche.java` and the Atmospheric probe now exclude that address from active Atmospheric validation.

## Result

```text
Original Wave 271 Ghidra Atmospheric signature tranche probe
Status: PASS
Targets: 4
Stale undefined signatures: 0
Xref rows: 59

Current Wave 284 adjusted probe
Status: PASS
Targets: 3
Stale undefined signatures: 0
Xref rows: 59
```

Saved signatures:

| Address | Saved signature |
| --- | --- |
| `0x00404010` | Superseded by `void __fastcall CAnimal__dtor_base(void * this)` |
| `0x004046d0` | `void * __thiscall CAtmospheric__Constructor(void * this, float param_1)` |
| `0x00404920` | `void __fastcall CAtmospheric__Link(void * this)` |
| `0x00404960` | `void __fastcall CAtmospheric__Unlink(void * this)` |

Queue refresh after this pass:

- Total functions: `5866`
- Commented functions: `376`
- Commentless functions: `5490`
- Undefined signatures: `2086`
- `param_N` signatures: `2564`
- Uncertain owner names: `0`
- Address-suffixed helper names: `0`
- Address-suffixed wrapper names: `0`

## What This Proves

- The active CAtmospheric functions selected by this tranche no longer have stale `undefined ... (void)` signatures in the saved Ghidra project.
- The comments record the proof boundary: object-pointer parameter shapes and global atmospheric-list behavior are visible in the decompile read-back.
- This is the first post-name-confidence signature-debt tranche, and it demonstrates the next static RE loop can shift from names to signatures/comments.
- The `0x00404010` row is historical evidence only and must not be used as a current CAtmospheric claim.

## What This Does Not Prove

- This does not prove the concrete CAtmospheric structure layout.
- This does not prove exact source method identity.
- This does not prove the constructor float parameter semantics beyond the current saved `float param_1` token.
- This does not add Ghidra tags.
- This does not prove runtime atmospheric behavior.
- This does not patch, launch, or mutate `BEA.exe` or the installed game.
- This does not close the broader signature/comment/type/tag/local/structure debt.

## Privacy / Release Safety

This report stores repo-relative artifact paths, public addresses, function names, signatures, command summaries, counts, and proof boundaries only. It does not include binaries, private absolute paths, source excerpts, decompiled source excerpts, runtime captures, screenshots, frame data, copied executables, copied saves, debugger logs, raw private proof JSON, or private game payloads.
