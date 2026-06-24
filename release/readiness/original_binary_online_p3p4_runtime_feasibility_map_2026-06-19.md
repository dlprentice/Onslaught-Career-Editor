# Original Binary Online P3/P4 Runtime Feasibility Map Readiness Note

Status: complete public-safe P3/P4 blast-radius map
Date: 2026-06-19
Scope: `original-binary-online-p3p4-runtime-feasibility-map`

This slice records the static/source blast radius for any future attempt to scale the original binary beyond the currently proven P1/P2 runtime path. It is deliberately not a runtime proof and not a patch proposal.

Accepted map evidence:

| Field | Evidence |
| --- | --- |
| Map contract | `roadmap/original-binary-online-p3p4-runtime-feasibility-map.v1.json` |
| Proof boundary | `mapProofClass=static-blast-radius-map-not-runtime-proof`; `p3p4FeasibilityScope=static-blast-radius-not-runtime-proof`; `newBeaLaunchCount=0`; `cdbAttachCount=0`; `ghidraMutationCount=0`. |
| Current runtime ceiling | `maxOriginalBinaryActiveSlotsProven=2`; `maxRuntimePlayerSlotsProven=2`; `nPlayerOriginalBinaryRuntimeProof=0`; `P3/P4 metadata-only`; `p3p4GameplayInputRejected=true`; `activeP3P4OriginalBinaryGameplayProof=false`. |
| Source capacity trap | `references/Onslaught/game.h:22` defines `MAX_PLAYERS 4`, but `sourceOnlyMaxPlayersIsRuntimeProof=false`. |
| Player-count gate | `references/Onslaught/game.cpp:705-708` sets `mPlayers=2` for multiplayer and `mPlayers=1` otherwise. |
| Controller trap | `references/Onslaught/game.cpp:723-728` assigns P1/P2 controller ownership and includes the source comment/assert against more than two players. |
| Viewpoint blocker | `references/Onslaught/engine.h:16` defines `VIEWPOINTS 2`; the latent quad-split branch at `references/Onslaught/game.cpp:1793-1816` remains `quadSplitBranchIsRuntimeProof=false`. |
| Runtime attempt gate | `mapCompleteForRuntimeAttempt=false`; `safeToPatchMPlayersAbove2=false`; `hardBlockersBeforeP3P4Runtime`; `beyondTwoPlayersRequiresNewProofClass=true`; `absenceOfCurrentProofIsNotProofOfPermanentAbsence=true`; `permanentImpossibilityClaim=false`; `publicMatchmakingProof=false`; `multiHostLanProof=false`; `nativeBeaNetcodeProof=false`. |
| Mapped rows | `source-max-players-capacity`; `current-mplayers-gate`; `controller-assignment-p1-p2-trap`; `engine-viewpoints-two`; `reconnect-interface-two`; `lives-respawn-results-two`; `input-flush-loop-by-mplayers`; `gameplay-systems-multiplayer-branches`. |

Validation:

```powershell
py -3 tools\winui_safe_copy_online_p3p4_runtime_feasibility_map_check.py --check
py -3 tools\winui_safe_copy_online_p3p4_runtime_feasibility_map_check.py --self-test
py -3 tools\winui_safe_copy_online_p3p4_runtime_feasibility_map_check_test.py
npm run test:winui-original-binary-online-p3p4-runtime-feasibility-map
```

Next useful rungs are same-host session-control, real second-host private command-source proof when a separate host exists, retail Ghidra P3/P4 deep dive for CGame/CEngine/controller/result paths, and only later copied-runtime P3/P4 allocation/input observation in an app-owned safe copy.

Non-claims: this does not prove more than two original-binary runtime players, active P3/P4 original-binary gameplay, co-op mode runtime behavior, versus mode runtime behavior, team-versus runtime behavior, multi-host LAN play, second-host command source, public matchmaking, native BEA netcode, deterministic sync, rollback, anti-cheat, rebuild parity, or no-noticeable-difference online parity. It also does not prove P3/P4 are impossible forever.
