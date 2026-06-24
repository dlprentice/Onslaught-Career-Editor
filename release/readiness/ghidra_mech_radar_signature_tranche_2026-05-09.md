# Ghidra Mech/Radar Signature Tranche - 2026-05-09

Status: public-safe saved-Ghidra signature/comment evidence, not final type/source/runtime proof

## Objective

Continue the post-name-confidence signature-debt phase with two low-risk lifecycle/destructor targets from the current undefined-signature queue. This pass hardens only the CMCMech destructor thunk and the CRadarWarningReceiver scalar deleting destructor, because their current retail instruction/decompile shapes are straightforward enough for a narrow saved signature claim.

## Inputs

- Targets:
  - `0x00405a10` `CMCMech__Destructor`
  - `0x00405a20` `CRadarWarningReceiver__scalar_deleting_dtor`
- Raw evidence root: `subagents/ghidra-static-reaudit/signature-debt-tranche2/current/`
- Signature script: `tools/ApplyMechRadarSignatureTranche.java`
- Probe: `tools/ghidra_mech_radar_signature_tranche_probe.py`
- Probe test: `tools/ghidra_mech_radar_signature_tranche_probe_test.py`

## Commands

Focused validation:

```powershell
py -3 tools\ghidra_mech_radar_signature_tranche_probe_test.py
py -3 tools\ghidra_mech_radar_signature_tranche_probe.py --check
py -3 -m py_compile tools\ghidra_mech_radar_signature_tranche_probe.py tools\ghidra_mech_radar_signature_tranche_probe_test.py
cmd.exe /c npm run test:ghidra-mech-radar-signature-tranche
cmd.exe /c npm run test:ghidra-static-reaudit-queue
```

Mutation/read-back summary:

- Read-only metadata/decompile/xref/instruction exports captured the two selected undefined-signature targets before mutation.
- Headless signature dry/apply updated both targets.
- Headless comment dry/apply saved proof-boundary comments for both targets.
- Metadata/decompile read-back verified the saved signatures/comments.
- The focused probe checked the signature/comment boundary plus xref and instruction evidence.

## Result

```text
Ghidra Mech/Radar signature tranche probe
Status: PASS
Targets: 2
Stale undefined signatures: 0
Xref rows: 2
Instruction rows: 66
```

Saved signatures:

| Address | Saved signature |
| --- | --- |
| `0x00405a10` | `void __fastcall CMCMech__Destructor(void * this)` |
| `0x00405a20` | `void * __thiscall CRadarWarningReceiver__scalar_deleting_dtor(void * this, byte flags)` |

Queue refresh after this pass:

- Total functions: `5866`
- Commented functions: `378`
- Commentless functions: `5488`
- Undefined signatures: `2083`
- `param_N` signatures: `2564`
- Uncertain owner names: `0`
- Address-suffixed helper names: `0`
- Address-suffixed wrapper names: `0`

## What This Proves

- The two selected targets no longer have stale `undefined ... (void)` signatures in the saved Ghidra project.
- The CMCMech target is now recorded as a destructor thunk with an explicit object-pointer parameter.
- The CRadarWarningReceiver target is now recorded as a scalar deleting destructor with an explicit object-pointer parameter, byte deletion flag, and object-pointer return.
- The saved comments preserve the proof boundary for future class-layout, source-identity, tag/local-name, and runtime work.

## What This Does Not Prove

- This does not prove concrete CMCMech or CRadarWarningReceiver class layout.
- This does not prove exact source method identity.
- This does not prove destructor side-effect completeness beyond the checked decompile/instruction evidence.
- This does not add Ghidra tags.
- This does not prove runtime mech or radar-warning behavior.
- This does not patch, launch, or mutate `BEA.exe` or the installed game.
- This does not close the broader signature/comment/type/tag/local/structure debt.

## Privacy / Release Safety

This report stores repo-relative artifact paths, public addresses, function names, signatures, command summaries, counts, and proof boundaries only. It does not include binaries, private absolute paths, source excerpts, decompiled source excerpts, runtime captures, screenshots, frame data, copied executables, copied saves, debugger logs, raw private proof JSON, or private game payloads.
