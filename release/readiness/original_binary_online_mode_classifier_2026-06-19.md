# Original Binary Online Mode Classifier Readiness Note

Status: complete public-safe mode classifier, not runtime mode proof
Date: 2026-06-19
Scope: `original-binary-online-mode-classifier`

This slice records `winui-original-binary-online-mode-classifier.v1` as a public-safe taxonomy guard for the online multiplayer lane. It does not launch BEA, attach CDB, send game input, mutate any executable, mutate Ghidra, or touch the installed Steam folder.

## Accepted Contract

The public-safe contract is:

```text
roadmap\original-binary-online-mode-classifier.v1.json
```

Key accepted fields:

- `proofClass=static-source-session-taxonomy-not-runtime-mode-proof`
- `modeClassifierScope=original-binary-online-mode-classifier-not-runtime-mode-proof`
- `currentRuntimeModeClassification=unclassified-local-multiplayer`
- `runtime-observed-local-splitscreen-not-co-op-or-versus-proof`
- `coOpVersusModeRuntimeProofSlices=0`
- `modeRuntimeProofSlices=0`
- `coOpModeRuntimeProof=false`
- `versusModeRuntimeProof=false`
- `teamVersusRuntimeProof=false`
- `spectatorAdminRuntimeProof=false`
- `teamAssignmentAuthority=schema-only-not-runtime-proof`
- `nPlayerOriginalBinaryRuntimeProof=0`
- `activeP3P4OriginalBinaryGameplayProof=false`
- `baseOnlineMultiplayerReady=false`
- `secondPhysicalHostProof=false`
- `multiHostLanProof=false`
- `publicMatchmakingProof=false`
- `nativeBeaNetcodeProof=false`

The checker rejects runtime mode claims from `sessionType alone`, `modeFamily alone`, `schema-only teamAssignments`, metadata-only spectator/admin rows, `slotCapacity=4`, same-host/WSL/private-interface artifacts, local session-directory smoke, host-authority wrapper scaffolding, or joined-session same-host proofs.

## Commands

```powershell
py -3 tools\winui_safe_copy_online_mode_classifier_check_test.py
py -3 tools\winui_safe_copy_online_mode_classifier_check.py --self-test
py -3 tools\winui_safe_copy_online_mode_classifier_check.py --check
npm run test:winui-original-binary-online-mode-classifier
```

## Boundary

This is no BEA launch, no CDB attach, no game input, no Ghidra mutation, no second-host LAN proof, no public matchmaking proof, no native BEA netcode proof, no runtime co-op proof, no runtime versus proof, no runtime team-versus proof, no spectator/admin runtime proof, no active P3/P4 gameplay proof, no deterministic sync proof, no rollback proof, no anti-cheat proof, no rebuild parity proof, and no no-noticeable-difference online parity proof.

No Ghidra backup was created because no Ghidra mutation occurred. The latest verified Ghidra review backup remains Wave1219 backup id `BEA_20260607-230027_post_wave1219_final_score16_current_risk_review_verified`; exact local backup roots stay in private state/evidence.
