# BattleEngine Weapon Burst Comment Pass - 2026-05-09

Status: public-safe saved Ghidra comment pass, not rename/signature/runtime proof

## Objective

Continue the static re-audit campaign by writing proof-boundary comments into the saved Ghidra database for the current weapon/burst cluster.

The comment pass covers:

| Address | Current saved name | Comment intent |
| --- | --- | --- |
| `0x00506930` | `CWeapon__HandleFireBurstEvent` | Record event-handler evidence and the exact source/runtime claims it does not prove. |
| `0x00505f70` | `CWeapon__scalar_deleting_dtor` | Record destructor evidence and keep it separate from fire/stealth behavior. |
| `0x005069f0` | `CEngine__SpawnProjectileBurstFromCurrentPreset` | Record projectile-burst behavior while keeping owner/source identity provisional. |
| `0x00506010` | `CGeneralVolume__SpawnBurstFromPresetWithFallback` | Record shared fallback-dispatcher evidence while keeping the name provisional. |

## Inputs

- Address list: `subagents/ghidra-static-reaudit/weapon-burst-comment-pass/current/addresses.txt`
- Pre-comment decompile export: `subagents/ghidra-static-reaudit/weapon-burst-comment-pass/current/decompile_before/index.tsv`
- Pre-comment xref export: `subagents/ghidra-static-reaudit/weapon-burst-comment-pass/current/xrefs.tsv`
- Dry-run log: `subagents/ghidra-static-reaudit/weapon-burst-comment-pass/current/comments_dry.log`
- Apply log: `subagents/ghidra-static-reaudit/weapon-burst-comment-pass/current/comments_apply.log`
- Metadata read-back: `subagents/ghidra-static-reaudit/weapon-burst-comment-pass/current/metadata_after.tsv`
- Probe: `tools/battleengine_weapon_burst_comment_pass_probe.py`
- Probe test: `tools/battleengine_weapon_burst_comment_pass_probe_test.py`

## Commands

Read-only context exports:

```powershell
bash tools/run_ghidra_headless_postscript.sh ExportFunctionsByAddressDecompile.java subagents/ghidra-static-reaudit/weapon-burst-comment-pass/current/addresses.txt subagents/ghidra-static-reaudit/weapon-burst-comment-pass/current/decompile_before 80
bash tools/run_ghidra_headless_postscript.sh ExportXrefsForAddresses.java subagents/ghidra-static-reaudit/weapon-burst-comment-pass/current/addresses.txt subagents/ghidra-static-reaudit/weapon-burst-comment-pass/current/xrefs.tsv
```

Serialized headless comment pass and read-back:

```powershell
bash tools/run_ghidra_headless_postscript.sh ApplyWeaponBurstClusterComments.java dry
bash tools/run_ghidra_headless_postscript.sh ApplyWeaponBurstClusterComments.java apply
bash tools/run_ghidra_headless_postscript.sh ExportFunctionMetadataByAddress.java subagents/ghidra-static-reaudit/weapon-burst-comment-pass/current/addresses.txt subagents/ghidra-static-reaudit/weapon-burst-comment-pass/current/metadata_after.tsv
```

Probe validation:

```powershell
py -3 tools\battleengine_weapon_burst_comment_pass_probe_test.py
py -3 tools\battleengine_weapon_burst_comment_pass_probe.py --check
py -3 -m py_compile tools\battleengine_weapon_burst_comment_pass_probe.py tools\battleengine_weapon_burst_comment_pass_probe_test.py
cmd.exe /c npm run test:battleengine-weapon-burst-comment-pass
```

## Result

```text
BattleEngine weapon burst comment-pass probe
Status: PASS
Classification: weapon-burst-cluster-comments-applied
Dry summary: {'applied': 0, 'skipped': 4, 'missing': 0, 'bad': 0}
Apply summary: {'applied': 4, 'skipped': 0, 'missing': 0, 'bad': 0}
0x00506930 CWeapon__HandleFireBurstEvent comment present: True
0x00505f70 CWeapon__scalar_deleting_dtor comment present: True
0x005069f0 CEngine__SpawnProjectileBurstFromCurrentPreset comment present: True
0x00506010 CGeneralVolume__SpawnBurstFromPresetWithFallback comment present: True
```

## What This Proves

- The saved Ghidra database now has comments on the four checked weapon/burst-cluster functions.
- The dry-run verified all four target names before apply.
- The apply log reports four comments set with no missing or bad targets.
- The metadata read-back confirms expected function names and proof-boundary comment tokens after the saved headless pass.
- The comments put the current uncertainty directly beside the functions that future Ghidra work is likely to inspect.

## What This Does Not Prove

- This does not rename `0x005069f0` or `0x00506010`.
- This does not harden function signatures, parameter names, tags, or local variable names.
- This does not prove exact source `CWeapon::Fire` or `CBattleEngine::WeaponFired` identity.
- This does not prove retail weapon fire clears or preserves stealth.
- This does not prove runtime cloak activation, projectile behavior, or fire-while-cloaked behavior.
- This does not patch, launch, or mutate `BEA.exe` or the installed game.

## Outcome

This is a small saved-database quality pass, not a closure pass. It improves the network effects the user called out: the next static RE worker sees the current evidence and caveats in Ghidra itself, not only in external docs.

The remaining weapon-fire stealth gap stays open. Future static work should either refine signatures/owners for `0x005069f0` and `0x00506010` with stronger evidence or move to copied-profile runtime proof only after a verified cloak-active baseline exists.

## Privacy / Release Safety

This report stores repo-relative artifact paths, public addresses already present in repo evidence, function names, command summaries, counts, and proof boundaries only. It does not include binaries, private absolute asset paths, source excerpts, decompiled source excerpts, runtime captures, screenshots, frame data, copied executables, copied saves, debugger logs, raw private proof JSON, or private game payloads.
