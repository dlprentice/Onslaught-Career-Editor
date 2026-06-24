# WinUI Original Binary Second-Host Runtime-Causality Raw-Material Plan And Manifest

Status: contract/self-test preflight added; raw-material manifest added; no live proof claimed
Date: 2026-06-22
Plan schema: `winui-original-binary-second-host-runtime-causality-raw-material-plan.v1`
Plan scope: `raw-material-intake-plan-not-live-runtime-causality-proof`
Manifest schema: `winui-original-binary-second-host-runtime-causality-raw-material-manifest.v1`
Manifest scope: `raw-material-manifest-preflight-not-live-runtime-causality-proof`

This slice extends the second-host runtime-causality candidate builder with a raw-material intake plan and a raw-material manifest preflight for the strict source-bound runtime-causality gate. The plan is a checklist artifact for future private live materialization. The manifest inventories candidate-bundle-relative raw material before promotion. Neither artifact is runtime proof.

Tracked surface:

| Item | Purpose |
| --- | --- |
| `tools/build_winui_original_binary_second_host_runtime_causality_candidate.py --raw-material-plan` | Writes and validates the raw-material plan under the private proof root. |
| `tools/build_winui_original_binary_second_host_runtime_causality_candidate.py --raw-material-manifest-from-candidate <candidate>` | Derives and validates the candidate-bundle-relative raw-material manifest. |
| `tools/build_winui_original_binary_second_host_runtime_causality_candidate_test.py` | Regression tests for required role coverage, fixture-mode separation, hash-drift rejection, and fail-closed overclaim rejection. |
| `test:winui-original-binary-second-host-runtime-causality-builder` | Public-safe self-test covering the builder, compatibility-executor rejection, raw-material plan path, and raw-material manifest path. |

Required hash-chain raw-material roles:

- `commandSourceProofSha256`
- `schedulerProofSha256`
- `bridgeProofSha256`
- `runtimeInputWindowArtifactSha256`
- `exactPidCdbLogSha256`
- `copiedRuntimeArtifactSha256`
- `copiedRuntimeExeSha256`
- `processIdentitySha256`

Required end-to-end bindings:

- `runId`
- `acceptedSecondHostCommandRequestPayloadSha256`
- `secondHostInvitationLifecycleSha256`
- `observedProcessIdentitySha256`
- `hostHelperMappedInputSequenceSha256`

Boundary:

- `requiredRoleCount=8` for the hash-chain roles, with accepted payload, invitation lifecycle, observed process identity, and mapped input sequence represented as required end-to-end binding material.
- The manifest records each role's candidate-bundle-relative artifact path, raw-evidence path, recomputed hashes, evidence mode, raw body key count, and material-unit count.
- The manifest rejects self-test raw material unless explicit fixture mode is requested.
- `acceptedLiveSecondHostRuntimeCausalityProof=false`.
- `hostJoinControlsMayBeEnabled=false`.
- `baseOnlineMultiplayerReady=false`.
- `privateProofRootPublished=false`.
- No listener.
- No invitation.
- No BEA launch.
- No CDB attach.
- No input send.
- No Ghidra mutation.
- No patch bytes applied.
- No Host/Join enablement.
- No player-ready netplay, public matchmaking, native BEA netcode, or P3/P4 original-binary gameplay.
- No private proof paths, raw runtime evidence, copied-game roots, screenshots, raw CDB logs, secrets, or invitation credentials are recorded in this public-safe note.

Future live promotion still requires a real distinct-host or VM-labeled command-source proof and a same-run chain binding the accepted command payload, invitation lifecycle, scheduler, bridge, runtime input-window, exact-PID CDB, copied-runtime artifact, copied executable hash, and process identity through private-root-contained raw material accepted by the runtime-causality checker.
