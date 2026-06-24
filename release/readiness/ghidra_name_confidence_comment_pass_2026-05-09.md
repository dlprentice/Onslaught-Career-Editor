# Ghidra Name-Confidence Comment Pass - 2026-05-09

Status: public-safe saved Ghidra comment evidence

## Objective

Consume the six comment-only candidates from the first Ghidra name-confidence queue tranche without overstating them as final names, signatures, source identities, tags, or runtime behavior.

## Inputs

- Comment map: `subagents/ghidra-static-reaudit/name-confidence-comment-pass1/current/comments.tsv`
- Address list: `subagents/ghidra-static-reaudit/name-confidence-comment-pass1/current/addresses.txt`
- Dry/apply logs: `subagents/ghidra-static-reaudit/name-confidence-comment-pass1/current/comments_*.log`
- Metadata read-back: `subagents/ghidra-static-reaudit/name-confidence-comment-pass1/current/metadata_after.tsv`
- Probe report: `subagents/ghidra-static-reaudit/name-confidence-comment-pass1/current/name-confidence-comment-pass1.json`
- Apply script: `tools/GhidraApplyFunctionCommentsFromTsv.java`
- Probe: `tools/ghidra_name_confidence_comment_pass_probe.py`
- Probe test: `tools/ghidra_name_confidence_comment_pass_probe_test.py`

Raw logs, metadata exports, and reports remain ignored under `subagents/`.

## Commands

```powershell
bash tools/run_ghidra_headless_postscript.sh GhidraApplyFunctionCommentsFromTsv.java subagents/ghidra-static-reaudit/name-confidence-comment-pass1/current/comments.tsv dry
bash tools/run_ghidra_headless_postscript.sh GhidraApplyFunctionCommentsFromTsv.java subagents/ghidra-static-reaudit/name-confidence-comment-pass1/current/comments.tsv apply
bash tools/run_ghidra_headless_postscript.sh ExportFunctionMetadataByAddress.java subagents/ghidra-static-reaudit/name-confidence-comment-pass1/current/addresses.txt subagents/ghidra-static-reaudit/name-confidence-comment-pass1/current/metadata_after.tsv
py -3 tools\ghidra_name_confidence_comment_pass_probe_test.py
py -3 tools\ghidra_name_confidence_comment_pass_probe.py --check
py -3 -m py_compile tools\ghidra_name_confidence_comment_pass_probe.py tools\ghidra_name_confidence_comment_pass_probe_test.py
cmd.exe /c npm run test:ghidra-name-confidence-comment-pass
bash tools/run_ghidra_headless_postscript.sh ExportFunctionQualitySnapshot.java subagents/ghidra-static-reaudit/queue/current/functions_quality.tsv
cmd.exe /c npm run test:ghidra-static-reaudit-queue
```

## Result

```text
Ghidra name-confidence comment-pass probe
Status: PASS
Classification: name-confidence-comment-candidates-commented
Targets: 6
Dry summary: {'applied': 0, 'skipped': 6, 'missing': 0, 'bad': 0}
Apply summary: {'applied': 6, 'skipped': 0, 'missing': 0, 'bad': 0}
All comments present: True
```

The refreshed queue reports:

```text
Total functions: 5863
Commentless functions: 5520
Undefined signatures: 2087
Param signatures: 2563
Uncertain owner names: 12
Address-suffixed helpers: 4
Address-suffixed wrappers: 24
```

## Commented Functions

| Address | Current saved name | Comment scope |
| --- | --- | --- |
| `0x00402dd0` | `CHeightField_Unk_0047eb80__Wrapper_00402dd0` | Heightfield/static-shadow corner test evidence and owner/signature caveat. |
| `0x00403ff0` | `CFastVB_Unk_0055db0a__Wrapper_00403ff0` | Resource-descriptor array destruction wrapper evidence and owner caveat. |
| `0x0040dcc0` | `CGeneralVolume_Unk_0040a580__Wrapper_0040dcc0` | Transition-state wrapper evidence and source-identity caveat. |
| `0x0040dda0` | `CUnitAI_Unk_0044c720__Wrapper_0040dda0` | UnitAI grid cooldown/stamp wrapper evidence and runtime/source caveat. |
| `0x00410670` | `CGeneralVolume_Unk_00409e60__Wrapper_00410670` | Linked-object drain/update wrapper evidence and owner/runtime caveat. |
| `0x00411b90` | `CEngine_Unk_00506010__Wrapper_00411b90` | Burst-dispatch list wrapper evidence and weapon-fire/stealth caveat. |

## What This Proves

- A reusable headless comment tool can apply exact-name-guarded function comments from a TSV map.
- The saved Ghidra database now has proof-boundary comments for the six checked name-confidence comment candidates.
- Metadata read-back confirms the expected current names and comment tokens after apply.
- The whole-database queue commentless count dropped from `5526` to `5520`.

## What This Does Not Prove

- This does not rename any of the six functions.
- This does not harden signatures, parameters, locals, tags, structures, or data types.
- This does not prove exact source-to-retail identity for any provisional owner label.
- This does not prove runtime behavior.
- This does not complete the broader Ghidra static re-audit queue.

## Privacy / Release Safety

This note stores repo-relative paths, public addresses, current function names, aggregate counts, command summaries, and proof boundaries only. It does not include binaries, private absolute paths, decompile excerpts, screenshots, runtime captures, copied executables, copied saves, raw private proof JSON, or private game payloads.
