# Goodies 71-73 Hidden Runtime Proof Plan - 2026-05-07

Status: public-safe proof plan, not runtime proof

## Objective

Design the next copied-profile runtime wave for Goodies 71-73 without mutating the installed Steam game, original `BEA.exe`, original saves, or public release scope.

The question is now narrow:

- Static/source/catalog evidence proves Goodies 71-73 are real shipped texture-only rows with data-table, texture-helper, unlock, and instruction support.
- Normal copied-profile wall replay proves visible top-row navigation jumps from 70 to 74.
- Ghidra read-back proves selected-coordinate handlers still route through `get_goodie_number(mCX, mCY)` and currently contain no direct `0x47`/`0x48`/`0x49` selection constants.
- Remaining work is hidden/non-grid runtime reachability, packed/runtime script divergence, or a binary-only/developer direct-selection path.

## Non-Negotiable Safety

- Do not patch or mutate the installed/original Steam `BEA.exe`.
- Do not synthesize `.bes` or `defaultoptions.bea` files from scratch.
- Copy a valid profile/save/options baseline before writing.
- Use app-owned copied-profile and artifact roots only.
- Apply any windowed-mode executable patch only to the copied `BEA.exe`.
- Keep raw screenshots, captures, frame dumps, save copies, copied executables, logs with private paths, and proof JSON under ignored/private paths.
- Publish only sanitized summaries.
- Confirm no managed BEA process remains at the end.

## Proposed Runtime Matrix

| Step | Purpose | Expected Evidence | Public Claim If Green |
| --- | --- | --- | --- |
| Copied-profile prep | Create an isolated runtime profile and copied executable. | Private copied-profile manifest, copied `BEA.exe` hash, artifact root path. | Runtime proof used a copied profile only. |
| Windowed patch on copy | Keep the game controllable for capture/input. | Patch verification against copied executable only. | Windowed runtime used a copied executable. |
| Baseline all-visible wall replay | Reconfirm the known control path. | Private capture sequence showing 66-70 then 74-77. | Normal wall path still skips 71-73. |
| Copied save state forcing | Copy a valid save, then set only copied Goodies 71-73 to visible states through true-view offsets while preserving file size and unknown bytes. | Before/after byte-range diff for copied save only; AppCore `BesFilePatcher.PatchGoodieStates` can perform the targeted copied-save override without using the broad all-Goodies product patch. | State forcing alone does or does not reveal 71-73 through normal wall navigation. |
| Cheat/display override check | Test the known retail all-Goodies display override path if safe and already documented for the retail specimen. | Private capture and save-name evidence. | Display override does or does not expose skipped coordinates. |
| Selection-handler runtime logging | If practical, observe `get_goodie_number`, `StartLoadingGoody`, and selected-state update behavior while navigating/opening Goodies. | Private debugger/log trace with selected coordinates and returned ids. | Runtime selected ids match or diverge from static mapping. |
| Stop and cleanup | Stop managed process and verify no BEA process remains. | Process-list proof. | Runtime proof left no managed BEA process. |

Prepared observer: `tools/runtime-probes/goodies-selection-observer.cdb.txt` logs `get_goodie_number` coordinates/return values plus right-navigation and selected-load state. Use it only against a copied-profile, windowed runtime session, and keep raw CDB logs under ignored `subagents/`.

Focused navigation observer: `tools/runtime-probes/goodies-input-observer.cdb.txt` avoids the hot global mapper breakpoint and logs `CFEPGoodies__ButtonPressed` entry plus after-call return values for the navigation/selection call sites. Prefer this for the next normal-skip proof because the first CDB-attached run was dominated by render-loop mapper sampling.

Follow-up result: `release/readiness/goodies_input_observer_runtime_proof_2026-05-08.md` proves the normal copied-profile wall-navigation path skips from `70` to `74`. Hidden/non-grid reachability for `71`, `72`, and `73` remains open only for non-wall, cheat, developer, or other direct-selection paths.

Follow-up static refresh: `release/readiness/goodies_hidden_path_static_refresh_2026-05-08.md` reruns the source, script, packed-resource, xref, and existing Ghidra-export probes after the focused observer proof. It keeps the current static model intact: no direct source API access, no direct source array access, no known mapper return, no current `GetGoodiePtr` or direct data-xref selector, no direct `0x47`/`0x48`/`0x49` constants in the selected-coordinate handlers, and no literal installed loose-script or packed-resource Goodie state calls for script indices 72-74. It does not prove hidden runtime reachability impossible.

Follow-up scalar scan: `release/readiness/goodies_scalar_reference_scan_2026-05-08.md` broadens the binary search to all instruction scalar references for `0x47`, `0x48`, and `0x49`. The result is noisy but actionable: it does not reveal a self-evident selector, and it leaves a smaller focused candidate set for decompile/instruction-context classification before another runtime run.

Follow-up scalar classification: `release/readiness/goodies_scalar_candidate_classification_2026-05-08.md` classifies the focused scalar candidates as non-selector evidence: object-allocation/source-line constants, stack cleanup/stride offsets, frontend page/icon state, virtual-keyboard constants, script runtime offsets, CRT noise, or texture parser offsets.

Prepared log parser: `tools/goodies_selection_observer_log_probe.py` summarizes observer logs and can enforce the normal skip sequence with `--check-normal-skip`.

## Copied-Save Preparation Helper

AppCore now exposes `BesFilePatcher.PatchGoodieStates(inputPath, outputPath, statesByIndex)` for proof setup only. It:

- refuses in-place writes,
- validates fixed save size and version word,
- writes through the true-view Goodie base `0x1F46`,
- accepts only displayable save indices `0..232`,
- accepts only raw states `0..3`,
- preserves neighboring Goodies and reserved slots unless explicitly targeted.

The active C# CLI now exposes this helper as `--set-goodie-state INDEX:STATE` for copied-save proof setup. The CLI mode rejects broad patch, rank, kill, settings, options, and keybind overrides when this option is used, so a runtime wave can prepare a narrow copied save without accidentally mixing unrelated edits.

The focused AppCore tests prove Goodies 71-73 can be set in a copied save without touching neighboring slots 70/74 or reserved slot 233. This is setup evidence for the future runtime wave, not runtime reachability proof.

## Acceptance Language

If the wave proves normal wall navigation and copied-state forcing still skip 71-73:

```text
Copied-profile runtime proof did not find a normal wall or copied-state path to display Goodies 71-73. This narrows the remaining question to hidden/developer/direct-selection or packed/runtime script divergence. It does not prove the rows are unreachable in all runtime states.
```

If the wave finds a path:

```text
Copied-profile runtime proof found a hidden/non-grid path for Goodies 71-73. Raw captures and copied-profile proof remain private; public docs record only the path class, safety posture, and sanitized observations.
```

## Validation To Run After The Runtime Wave

- `tasklist.exe /FI "IMAGENAME eq BEA.exe"` after stop.
- Relevant copied-profile proof verifier if added.
- `dotnet test .\OnslaughtCareerEditor.AppCore.Tests\OnslaughtCareerEditor.AppCore.Tests.csproj --nologo` if save/Goodies AppCore code changes.
- `npm run test:md-links`
- `npm run test:doc-commands`
- `py -3 tools\docsync_check.py`
- `py -3 tools\release_profile_snapshot.py --check`
- `py -3 tools\release_curated_manifest.py --check`
- `npm run test:public-allowlist`
- `git diff --check`

## Not Claimed By This Plan

- This plan is not runtime proof.
- This plan does not launch BEA.
- This plan does not prove hidden/non-grid reachability or unreachability.
- This plan does not authorize mutation of the installed game or original save/profile files.
