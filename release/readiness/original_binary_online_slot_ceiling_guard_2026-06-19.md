# Original Binary Online Slot-Ceiling Guard Readiness Note

Status: complete public-safe slot-ceiling guard
Date: 2026-06-19
Scope: `original-binary-online-slot-ceiling-guard`

This slice records the current multiplayer scalability boundary in a machine-checkable way. It keeps the online/session architecture scalable while making the current original-binary runtime ceiling explicit: P1/P2 are the only active original-binary gameplay slots proven today, and P3/P4 remain metadata-only/rejected original-binary gameplay routes until a new proof class exists.

Accepted guard evidence:

| Field | Evidence |
| --- | --- |
| Guard contract | `roadmap/original-binary-online-slot-ceiling-guard.v1.json` |
| Source player-count anchor | `references/Onslaught/game.cpp:705 WORLD.IsMultiplayer() sets mPlayers=2` |
| Source viewpoint anchor | `references/Onslaught/engine.h:16 defines VIEWPOINTS 2` |
| Source capacity trap | `references/Onslaught/game.h:22 defines MAX_PLAYERS 4`, but this is not active P3/P4 runtime proof. |
| Source latent quad-split trap | `references/Onslaught/game.cpp:1793` has a 3/4-player quad-split render branch, but this is not proof that the current retail runtime reaches active P3/P4 gameplay. |
| Current runtime ceiling | `maxOriginalBinaryActiveSlotsProven=2`; `activeOriginalBinarySlotsProven=P1,P2`; `retailViewpointsProven=2`; `observedViewpoints=0,1`. |
| Scalable session boundary | `slotCapacity=4`; `acceptedSessionParticipantCount=4`; `minimumArchitectureAcceptanceSlots=4`; `mustNotHardcodeExactlyTwoPlayers=true`. |
| P3/P4 boundary | `P3/P4 metadata-only`; `unsupported-original-binary-active-slot`; `required-for-unproven-original-binary-slots`; `p3p4GameplayInputRejected=true`; `rejectedOriginalBinaryGameplayCommandCount=2`. |
| Latest runtime proof boundary | `winui-original-binary-host-authority-state-authority-replayability.v1`; `winui-original-binary-host-authority-state-authority-observer.v1`; `hostAuthorityScope=single-copied-host-exact-pid-state-graph`; `proofCount=2`; `deliveredOriginalBinaryCommandCount=2`; `deliveredSlots=P1,P2`; `hostHelperInputSent=true`; `gameInputSentByScheduler=false`; `stateAuthorityGraphProven=true`; `stateAuthorityReplayabilityProven=true`; `distinctPlayers=true`; `distinctProcessIds=true`; `distinctCdbLogs=true`; `distinctRuntimePointerTuples=true`; `waitWindowsClean=true`; `nPlayerOriginalBinaryRuntimeProof=0`. |
| Future proof boundary | `beyondTwoPlayersRequiresNewProofClass=true`; `absenceOfCurrentProofIsNotProofOfPermanentAbsence=true`; `permanentImpossibilityClaim=false`. |

Validation:

```powershell
py -3 tools\winui_safe_copy_online_slot_ceiling_guard_check.py --check
py -3 tools\winui_safe_copy_online_slot_ceiling_guard_check.py --self-test
py -3 tools\winui_safe_copy_online_slot_ceiling_guard_check.py --private-proof <private-executor-proof>
npm run test:winui-original-binary-online-slot-ceiling-guard
```

No BEA launch, executable mutation, Ghidra mutation, or Ghidra backup was required for this public-safe guard slice.

Non-claims: this does not prove more than two original-binary runtime players, active P3/P4 original-binary gameplay, co-op mode runtime behavior, versus mode runtime behavior, team-versus runtime behavior, multi-host LAN play, public matchmaking, public relay/server behavior, native BEA netcode, NAT traversal, deterministic sync, rollback, anti-cheat, physical gamepad behavior, rebuild parity, or no-noticeable-difference online parity. It also does not prove P3/P4 are impossible forever; it proves only that a new proof class is required before any P3/P4 original-binary gameplay claim.
