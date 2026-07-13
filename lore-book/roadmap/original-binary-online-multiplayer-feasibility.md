# Original Binary Online Multiplayer Feasibility

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 live correction closeout:** `0x0042e4d0` comment correction. Current live Ghidra reflects confirmed rows only; older conflicting text below is superseded only where confirmed. Use the [closeout](../reverse-engineering/binary-analysis/ghidra-full-reaudit-closeout-2026-07-13.md); final per-address decisions and exact before/after metadata are in `reverse-engineering/binary-analysis/ghidra-reviewed-correction-decisions-2026-07-13.jsonl` and `reverse-engineering/binary-analysis/ghidra-reviewed-correction-plan-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

Deployment shape: near-term public UX should use a companion/launcher model. WinUI prepares an app-owned safe copied game folder, applies selected byte/config/resource changes to that copy, writes a manifest, launches the copied executable, and owns repair/restore/update flow. First-generation online multiplayer should assume WinUI or a packaged helper remains active during sessions for session discovery, invitation handling, identity pins, authentication, relay/host authority, input delivery, process cleanup, and rollback. A later mega patch or in-game menu can make proven features feel more native, but a static one-time byte patch is not the realistic first deployment target for matchmaking/netplay.

Companion target model: the user-facing aspiration is that the host runs a safe copied BEA session while a second player joins from a separate safe copy instead of seeing the host's split-screen view. Current WinUI copy presents that as `Future design sketch; Host/Join unavailable`; it is not an enabled Host/Join flow and it is blocked until distinct endpoint command-source proof and source-bound copied-runtime causality are accepted.

Dual-safe-copy topology rung: `roadmap/original-binary-online-dual-safe-copy-topology.v1.json` now records the public-safe dual-safe-copy same-workstation topology for the companion model. It declares `safeCopyCount=2`, `roles=host,joiner`, `safeCopyRootDescriptorCount=2`, `sameWorkstationOnly=true`, and separate app-owned copied executable descriptors for a future host and joiner. This is not player-ready netplay: it launches no BEA process, starts no listener, creates no invitation, sends no input, enables no Host/Join controls, and does not prove a distinct endpoint.

Second-host runtime-host-kind gate: the command-source contract, builder, client preflight, live-readiness templates, live-run kit, and validator now require runtime-host-kind evidence. Accepted runtime kinds are `windows-host`, `linux-host`, `macos-host`, and explicitly labeled `vm-guest`; `wsl-on-host`, `container-on-host`, and `unknown-host` are rejected. VM-labeled proof requires client `vm-guest`; physical second-host proof rejects client `vm-guest`; live physical second-host validation also rejects `operator-supplied-runtime-host-kind` for host and client identity evidence; live run-kit readiness rejects operator-supplied client identity fingerprints unless the client preflight computed them from local redacted identity evidence. This adds no BEA launch, no CDB attach, no accepted live command-source proof, no accepted runtime-delivery proof, and no Host/Join enablement.

Status: online ladder checker/contract coverage extends through the second-host live-readiness preflight, live-run kit, command-source, runtime-delivery bridge, runtime executor, raw-material-file-backed runtime-causality, raw-material intake plan/manifest, and Host/Join enablement gates, with same-host runtime proof rungs recorded below. These are contract/checker surfaces, not user Host/Join availability. Current hard truth remains `baseOnlineMultiplayerReady=false`, `hostJoinControlsMayBeEnabled=false`, `acceptedLiveSecondHostCommandSourceProof=false`, `acceptedLiveSecondHostRuntimeDeliveryProof=false`, `acceptedLiveSecondHostRuntimeCausalityProof=false`, `activeP3P4OriginalBinaryGameplayProof=false`, and no live second-host LAN/public/matchmaking/native-netcode/player-ready netplay proof yet.
Date: 2026-06-22

WinUI status surface: Windowed & Mods now promotes an `Online multiplayer is not ready` card above the deep technical controls. It keeps the only safe current action as local split-screen in a safe copy, states the future separate-safe-copy companion target, and keeps Host/Join unavailable until distinct endpoint command-source proof plus copied-runtime causality are both accepted. The technical online details expose a second-host live-attempt readiness summary sourced from AppCore: `readyToAttemptHarness=false`, `readyForLiveValidationCandidate=false`, `readyToRunLiveCommandSource=false`, `serverCommandInputsComplete=false`, `clientPreflightProvided=false`, `candidatePrivateBindAddressCount=1`, `wslOnHostInterfaceCount=1`, and `hostJoinControlsMayBeEnabled=false`. Windowed & Mods can now load a redacted second-host live-readiness/run-kit JSON artifact and render only sanitized `readyToRunLiveCommandSource`, `serverCommandInputsComplete`, `clientPreflightProvided`, private-bind, and WSL-interface counts. AppCore rejects unsupported schemas, missing proof booleans, Host/Join or online proof overclaims, invalid/unreadable files, and run-kit artifacts that report raw private paths serialized in public docs. This is visible readiness accounting/intake only; it is not a listener, invitation, BEA launch, CDB attach, input send, accepted live command-source proof, runtime-causality proof, Host/Join enablement, or player-ready online play.

This document records the current feasible path for pursuing true online multiplayer/matchmaking around the original retail BEA binary while preserving the copied-game safety model.

Hard current proof booleans: `baseOnlineMultiplayerReady=false`, `hostJoinControlsMayBeEnabled=false`, `acceptedLiveSecondHostCommandSourceProof=false`, `acceptedLiveSecondHostRuntimeDeliveryProof=false`, `acceptedLiveSecondHostRuntimeCausalityProof=false`, `multiHostLanPlayProof=false`, `publicMatchmakingProof=false`, `nativeBeaNetcodeProof=false`, `activeP3P4OriginalBinaryGameplayProof=false`, and `nPlayerOriginalBinaryRuntimeProof=0`.

## Contract/Self-Test And Private Candidate Gates

The package scripts below are intentionally separated so a green local aggregate cannot be mistaken for live netplay proof.

| Gate | Command | Meaning |
| --- | --- | --- |
| Contract/self-test | `npm run test:winui-original-binary-second-host-command-source` | Validates the command-source checker and public contract shape; not live second-host proof. |
| Contract/self-test | `npm run test:winui-original-binary-second-host-runtime-causality` | Validates runtime-causality checker behavior and self-test fixtures; not accepted runtime causality. |
| Contract/self-test | `npm run test:winui-original-binary-second-host-runtime-causality-builder` | Validates the candidate materializer can write file-backed self-test candidates, reject the current compatibility executor, emit the raw-material intake plan, and derive the raw-material manifest; not live source-bound runtime causality. |
| Contract/self-test | `npm run test:winui-original-binary-host-join-enablement` | Validates the composite Host/Join gate stays fail-closed; not Host/Join availability. |
| Contract/self-test | `npm run test:winui-original-binary-second-host-live-candidate-gate` | Validates the private candidate wrapper fails closed and rejects fixture/self-test artifacts. |
| Private candidate | `SECOND_HOST_COMMAND_SOURCE_BUNDLE=<private-bundle.json> npm run test:winui-original-binary-second-host-command-source-live` | Requires a private command-source bundle accepted by the command-source checker in `--live` mode. |
| Private candidate | `SECOND_HOST_RUNTIME_CAUSALITY_CANDIDATE=<private-candidate.json> npm run test:winui-original-binary-second-host-runtime-causality-candidate` | Requires a private runtime-causality candidate with file-backed same-run evidence. |
| Private candidate | `SECOND_HOST_COMMAND_SOURCE_BUNDLE=<private-bundle.json> SECOND_HOST_RUNTIME_CAUSALITY_CANDIDATE=<private-candidate.json> npm run test:winui-original-binary-host-join-candidate-gate` | Requires both private candidate inputs and matching accepted-command payload plus invitation lifecycle hashes; still does not enable Host/Join. |

Online readiness is not player-ready online play. Accepted private candidate summaries carry scope `private-candidate-validation-not-host-join-enablement`. No BEA launch/CDB attach is produced by the contract/self-test gates, no private proof paths or raw invitation data belong in public docs, and current hard truth remains no Host/Join enablement, no player-ready netplay, no public matchmaking, and no native BEA netcode.

## Netplay Proof Rung Matrix

This matrix is the canonical handoff surface for the original-binary online ladder. "Accepted" means accepted by that rung's checker/contract only; it does not imply player-ready netplay unless the player-ready rung is also green.

| Rung | Current state | What it proves | What it does not prove |
| --- | --- | --- | --- |
| Same-host / same-workstation proof | Accepted for many local-only P1/P2 host-authority, relay, scheduler, and runtime-observer slices | The copied host can be launched, observed, and driven locally through guarded proof tooling | Second physical host, public matchmaking, native BEA netcode, or player-ready online |
| WSL-on-host proof | Accepted only as same-physical-machine command-source smoke | A WSL client can exercise command-source protocol shape against the Windows host | Second-host LAN proof; WSL-on-host is explicitly not a distinct host |
| VM-labeled private-LAN command-source proof | Not yet live-accepted | A VM endpoint, explicitly labeled same-physical-machine-only, can supply a private-LAN command source | Physical second-host LAN proof, runtime causality, player-ready netplay |
| Distinct physical private-LAN command-source proof | Not yet live-accepted | A separate physical machine can supply a private-LAN command source | Runtime causality, matchmaking, native BEA netcode, public readiness |
| Live command-source proof | Not yet live-accepted | Signed request/response transcript, live listener lifecycle receipt, listener teardown/post-close rejection, two-phase local source-safety samples, identity pins, non-fixture host/client identity evidence with `machineFingerprintSource=local-hostname-platform-preflight` and `runtimeHostKindSource=auto-platform-preflight`, and per-event monotonic `serverObservedAtUnix` timestamps inside the invitation window pass `--live` | Runtime delivery into BEA; command-source proof has `newBeaLaunchCount=0` and `cdbAttachCount=0` |
| Source-bound runtime causality | Not yet accepted | The accepted second-host payload and invitation lifecycle hashes reach scheduler, bridge, runtime input-window, exact-PID CDB, mapped P2 sequence, host-helper delivery, copied-runtime artifact, copied executable hash, process identity, role-specific material descriptors, and recomputed private-root-contained raw-material file hashes in one same-run chain | Host/Join UI enablement unless the composite gate also passes |
| Runtime-causality candidate materializer | Self-test passed; raw-material plan and manifest emitted/validated | The materializer can create file-backed self-test candidates for checker coverage, rejects today's host-authority-derived compatibility executor including edited live-looking booleans, emits a private-root-contained raw-material intake plan for the 8 required source-bound roles, and derives a manifest from candidate-bundle-relative raw material with recomputed hashes and false live proof booleans | Live source-bound runtime causality, Host/Join enablement, player-ready netplay |
| Host/Join enablement | Blocked by composite gate | Future Host/Join controls remain hidden until both distinct command-source proof and source-bound runtime causality pass their separate acceptance gates | Player-ready public netplay, matchmaking, native BEA netcode, deterministic sync, rollback, anti-cheat |
| P3/P4 scalability | Schema/process/socket evidence only | Four-slot session descriptors, process/socket concurrency, and P3/P4 rejection/metadata policy are measurable | Active P3/P4 original-binary gameplay, more-than-two runtime players, co-op/versus mode behavior |
| Player-ready netplay | Not started as a release claim | A user-facing Host/Join flow is reliable, understandable, safe, repeatable, and release-tested | Nothing below this rung should be described as multiplayer being implemented |

## Current Evidence

The project has strong local-multiplayer groundwork, not online proof:

| Evidence class | Current status |
| --- | --- |
| Static/runtime local-multiplayer contract | `reverse-engineering/binary-analysis/local-multiplayer-static-runtime-contract.md` |
| Local multiplayer launch surface | WinUI safe-copy Local Multiplayer Probe uses `-skipfmv -level 850` |
| Runtime anchors | `0x004725d0 CGame__IsMultiplayer`, `0x0050d7d0 CWorld__IsMultiplayerMode`, `0x00528b50 CEngine__SetNumViewpoints`, `0x0044a020 CEngine__SetViewpoint` |
| Local input/state proof | Copied-profile keyboard Q/E routing and movement-state evidence across configs 1-4 |
| Local control telemetry bundle | `1` accepted level-850 `winui-control-feel-telemetry-bundle.v1` proof over five diagnostics scenarios, one distinct repeat baseline, and one wait-only no-input control; records `runtimeProfile=original-binary-copied-local-control-telemetry`, `slotCapacity=4`, `acceptedOriginalBinaryGameplaySlots=P1,P2`, `metadataOnlySlots=P3,P4`, `rejectedGameplayRouteSlots=P3,P4`, `gameInputSentByNSlotScheduler=false`, `hostHelperInputSent=false`, `nPlayerOriginalBinaryRuntimeProof=0`, and `activeP3P4OriginalBinaryGameplayProof=false` |
| Loopback command-envelope proof | `1` local mock remote P2 Movement/Forward command reached the copied original-binary P2 route |
| Local relay/session descriptor proof | `1` localhost TCP JSONL relay/session descriptor transcript chained to the loopback proof |
| Private relay-delivery proof | `1` local/private relay-delivery adapter proof with fresh host-helper CDB input evidence |
| Private-interface transport/auth smoke | `1` same-workstation private-interface TCP JSONL auth/nonce/replay/sequence/rate/smoke-identity proof chained to the private relay-delivery proof; no second-host LAN reachability proven |
| Process-separated private remote-client smoke | `1` same-workstation separate-client-process private-interface command-source smoke chained to the private LAN transport proof |
| Host-authority two-client scheduler smoke | `1` same-workstation two-client host-authority scheduler proof with distinct P1/P2 client processes and deterministic host relay plan |
| Host-authority runtime delivery proof | `2` same-workstation scheduler-to-host-helper runtime proofs: P1 `Q` and P2 `E` delivered into two distinct copied level-850/config-1 host sessions with exact-PID CDB state evidence; `visualCaptureCount=7` per proof; `nPlayerOriginalBinaryRuntimeProof=0` |
| Host-authority runtime executor proof | `1` relay-plan-driven executor proof: accepted scheduler relay plan derived the live safe-copy input plan, launched one copied level-850/config-1 host through the live harness, and built a fresh runtime-delivery bundle with `childEnvSensitiveKeyCount=0` and `executorRecordsFreshSameRootArtifacts=true` |
| Private remote-client runtime-causality wrapper | `1` private wrapper proof; `private-remote-client-to-runtime-executor-same-workstation-not-online-play`; `privateRemoteClientRuntimeCausalityProven=true`; `remoteClientAcceptedCommandId=private-remote-client-p2-forward-0001`; `remoteClientProcessSeparated=true`; `sameWorkstationOnly=true`; `remoteClientToHostRelayPathMatchCount=1`; `hostRelayToRuntimeExecutorPathMatchCount=1`; `newBeaLaunchCount=1`; `cdbAttachCount=1`; `visualCaptureCount=7`; `deliveredOriginalBinaryCommandCount=2`; `hostHelperInputSent=true`; `gameInputSentByRemoteClient=false`; `gameInputSentByHostAuthorityScheduler=false`; `bridgeSendsNewNetworkInput=false`; `acceptedOriginalBinaryGameplaySlots=P1,P2`; `metadataOnlySlots=P3,P4`; `baseOnlineMultiplayerReady=false`; `multiHostLanProof=false`; `nativeBeaNetcodeProof=false`; no new BEA launch beyond the existing executor proof |
| Host-authority runtime movement-state bridge proof | `1` relay-plan-driven executor movement-state bridge: accepted executor artifact revalidated with exact-PID CDB Q/P0 and E/P1 movement-state deltas; `visibleMovementDeltaClaim=false` |
| Host-authority N-slot process smoke | `1` same-workstation sequential four-client N-slot process smoke: `four-separate-python-client-processes`; `processConcurrencyModel=sequential-distinct-client-processes`; `simultaneousClientProcessesProven=1`; `clientProcessCount=4`; `arrivalOrder=P4,P2,P3,P1`; deterministic participant order `P1,P2,P3,P4`; deterministic original-binary relay order `P1,P2`; `acceptedOriginalBinaryGameplaySlots=P1,P2`; `P3/P4 metadata-only`; `gameInputSentByNSlotScheduler=false`; `hostHelperInputSent=false`; `nPlayerOriginalBinaryRuntimeProof=0` |
| Host-authority N-slot concurrent process smoke | `1` same-workstation-client/private-interface concurrent/barrier four-client N-slot process smoke: `four-separate-python-client-processes`; `processConcurrencyModel=barrier-concurrent-client-processes`; `simultaneousClientProcessesProven=4`; `clientReadyBeforeBarrierReleaseCount=4`; `barrierReleaseAfterAllClientsReady=true`; `maxSimultaneousSocketConnectionsProven=4`; `privateLanReachableDuringRun=true`; `foreignPeersRejectedAfterAccept=true`; `securityProofScope=minimal-smoke-hmac-envelope-not-full-session-security-proof`; P1/P2 relay only; P3/P4 metadata-only; `nPlayerOriginalBinaryRuntimeProof=0` |
| Host-authority N-slot session-security smoke | `1` same-workstation N-slot session-security message smoke: `securityProofScope=same-workstation-session-security-smoke-not-online-gameplay-proof`; `sessionScopedMacCoverageProof=true`; `sessionScopedMacCoverageMode=canonical-json-message-excluding-mac`; `sessionScopedMacFieldSensitivityProof=true`; `tickBoundMacFieldsProof=true`; `relayPlanHashMacBound=true`; `maxJsonLineBytesEnforced=true`; `rawJsonLineByteLimitRejected=true`; `unknownFieldRejectionProof=true`; `strictMessageSchemaProof=true`; `acceptedOriginalBinaryGameplayCommandCount=2`; `metadataGameplayRejectionCount=2`; `rejectedSecurityCaseCount=25`; `activeP3P4OriginalBinaryGameplayProof=false`; `newBeaLaunchCount=0`; `cdbAttachCount=0`; `nPlayerOriginalBinaryRuntimeProof=0` |
| Host-authority secure N-slot runtime bridge provenance proof | `1` public-safe provenance wrapper: accepted same-workstation N-slot session-security smoke feeds the same runtime-compatible P1/P2 relay hash used by the accepted copied-runtime bridge; `secureSessionAcceptedRelayFeedsRuntimeBridge=true`; `runtimeCompatibleP1P2RelayHashMatched=true`; `wrapperNewBeaLaunchCount=0`; `wrapperCdbAttachCount=0`; `P3/P4 metadata-only`; `rejectedGameplayRouteSlots=P3,P4`; `nPlayerOriginalBinaryRuntimeProof=0` |
| Host-authority secure N-slot runtime executor proof | `1` live executor proof: accepted same-workstation N-slot session-security smoke supplied the P1/P2 relay input sequence for one fresh copied level-850/config-1 BEA host-helper run; `securityProofScope=same-workstation-session-security-smoke-not-online-gameplay-proof`; `newBeaLaunchCount=1`; `cdbAttachCount=1`; `visualCaptureCount=7`; `deliveredOriginalBinaryCommandCount=2`; `visibleMovementDeltaClaim=false`; `P3/P4 metadata-only`; `nPlayerOriginalBinaryRuntimeProof=0` |
| Host-authority secure N-slot runtime executor replayability proof | `1` replayability proof over `2` secure executor artifacts: same session-security proof hash, same session relay plan hash, same runtime-compatible P1/P2 relay hash, distinct live runtime hashes, distinct process ids, distinct CDB logs, distinct runtime paths, and distinct runtime pointer tuples; `secureNSlotRuntimeExecutorReplayabilityProven=true`; `deliveredOriginalBinaryCommandCountPerProof=2`; `visibleMovementDeltaClaim=false`; `P3/P4 metadata-only`; `nPlayerOriginalBinaryRuntimeProof=0` |
| Host-authority N-slot runtime bridge proof | `2` fresh N-slot concurrent relay-derived copied-runtime proofs: accepted concurrent four-client N-slot process proof supplied the P1/P2 relay input sequence for copied level-850/config-1 host-helper runs; `visualCaptureCount=7` per proof; `hostHelperInputSent=true`; `gameInputSentByNSlotScheduler=false`; `P3/P4 metadata-only`; `nPlayerOriginalBinaryRuntimeProof=0` |
| Host-authority state-authority observer proof | `2` N-slot-derived P1/P2 copied-host state-authority graph proofs: `hostAuthorityScope=single-copied-host-exact-pid-state-graph`; `distinctPlayers=true`; `distinctBattleEngines=true`; `distinctWalkers=true`; `distinctControllers=true`; `waitWindowsClean=true`; Q/P1 `button31ReceiveRows=12` / `forwardStateStoreRows=12`; E/P2 `button31ReceiveRows=11` / `forwardStateStoreRows=11`; `hostHelperInputSent=true`; `gameInputSentByNSlotScheduler=false`; `P3/P4 metadata-only`; `nPlayerOriginalBinaryRuntimeProof=0` |
| Host-authority state-authority replayability proof | `1` repeated same-workstation single-copied-host exact-PID P1/P2 state-authority graph replayability proof: two distinct observer proofs, live runtime artifact hashes, source bridge proof hashes, process ids, CDB logs, and runtime player/controller/BattleEngine/Walker tuples; same N-slot concurrent process proof and runtime-compatible P1/P2 relay hash; `stateAuthorityReplayabilityProven=true`; `nPlayerOriginalBinaryRuntimeProof=0` |
| Original Binary Online Session Scalability Contract | `1` public-safe four-slot-capable design/process contract; `originalBinaryPlayerSlotsProven=2`; `maxRetailPlayersProven=2`; `nPlayerOriginalBinaryRuntimeProof=0`; `modeScalableArchitecturePlanned=true`; `coOpVersusModeRuntimeProofSlices=0`; `processConcurrencyModel=barrier-concurrent-client-processes`; `simultaneousClientProcessesProven=4`; `maxSimultaneousSocketConnectionsProven=4`; four-slot capability is session/schema/process/socket-layer only |
| Original Binary Online N-slot session schema proof | `1` public-safe four-slot session/schema proof; `slotCapacity=4`; `acceptedSessionParticipantCount=4`; `P3/P4 metadata-only`; `rejectedOriginalBinaryGameplayCommandCount=2`; `nPlayerOriginalBinaryRuntimeProof=0` |
| Original-binary online slot-ceiling guard | `1` public-safe current-profile guard; `maxOriginalBinaryActiveSlotsProven=2`; `P3/P4 metadata-only`; `beyondTwoPlayersRequiresNewProofClass=true`; `absenceOfCurrentProofIsNotProofOfPermanentAbsence=true`; `permanentImpossibilityClaim=false` |
| Original Binary Online P3/P4 Runtime Feasibility Map | `1` public-safe static blast-radius map; `original-binary-online-p3p4-runtime-feasibility-map.v1.json`; `mapProofClass=static-blast-radius-map-not-runtime-proof`; `p3p4FeasibilityScope=static-blast-radius-not-runtime-proof`; `nPlayerOriginalBinaryRuntimeProof=0`; `P3/P4 metadata-only`; `sourceOnlyMaxPlayersIsRuntimeProof=false`; `quadSplitBranchIsRuntimeProof=false`; `safeToPatchMPlayersAbove2=false`; `activeP3P4OriginalBinaryGameplayProof=false` |
| Local session-directory smoke | `1` same-workstation local session-directory smoke; `same-workstation-local-directory-smoke-not-public-matchmaking`; `registeredSessionCount=1`; `compatibleListingCount=1`; `acceptedJoinTicketCount=1`; `rejectedDirectoryCaseCount=14`; `publicMatchmakingProof=false`; `nPlayerOriginalBinaryRuntimeProof=0` |
| Second-host readiness contract | `1` public-safe planning guard; `original-binary-online-second-host-readiness.v1.json`; scope `second-host-command-source-readiness-not-runtime-proof`; requires distinct private host or VM-labeled-private-LAN evidence, non-loopback/private assigned-interface evidence, pinned host identity, session-scoped auth, two-sided copied-profile/source-hash safety, Program Files mutation rejection, and `host-join-enablement-composite-proof` before any Host/Join enablement; `secondHostProof=false`; `multiHostLanProof=false`; `publicMatchmakingProof=false`; `nativeBeaNetcodeProof=false`; `activeP3P4OriginalBinaryGameplayProof=false` |
| Second-host live-readiness preflight | `1` public-safe host preflight; `winui-original-binary-second-host-live-readiness.v1`; scope `host-live-run-readiness-preflight-not-command-source-proof`; current workstation result `candidatePrivateBindAddressCount=1`, `wslOnHostInterfaceCount=1`, and `serverCommandInputsComplete=false`; keeps `acceptedLiveSecondHostCommandSourceProof=false`, `acceptedLiveSecondHostRuntimeDeliveryProof=false`, `baseOnlineMultiplayerReady=false`, and `hostJoinControlsMayBeEnabled=false`; opens no listener, creates no invitation, launches no BEA, attaches no CDB, sends no input, and is not player-ready netplay |
| Second-host live-run kit | `1` public-safe checked command package; `winui-original-binary-second-host-live-run-kit.v1`; scope `second-host-live-run-kit-not-command-source-proof`; current workstation result `readyToRunLiveCommandSource=false`, `serverCommandInputsComplete=false`, `clientPreflightProvided=false`, `candidatePrivateBindAddressCount=1`, and `wslOnHostInterfaceCount=1`; emits redacted host/client command templates only; readiness now requires an eligible selected private non-WSL bind host, an upstream private-LAN proof that passes the private LAN checker, host copied/install roots that hash through local preflight, and a `.json` invitation path under OS temp and outside the repo; the paired `--live` command-source gate rejects synthetic live-labeled fixtures unless non-fixture host/client identity evidence, non-fixture auth/identity/source hash values, realistic live timestamps/addresses, and server-observed transcript timestamps inside the invitation window are present; hidden Host/Join-style overclaims are rejected even as string/numeric truthy values; opens no listener, creates no invitation, launches no BEA, attaches no CDB, sends no input, creates no command-source proof, does not enable Host/Join, and is not player-ready netplay |
| Second-host command-source proof gate | `1` public-safe validator gate; `original-binary-online-second-host-command-source.v1.json`; scope `second-host-command-source-proof-gate-not-live-runtime-proof`; accepts only distinct physical private-LAN or VM-labeled private-LAN command-source bundle shapes; rejects TEST-NET/documentation ranges; requires private-LAN proof hash linkage, RFC1918/ULA private non-loopback assigned host/client addresses, structured host/client identity and sanitized interface evidence, computed/redacted machine-fingerprint preflight, client-source-not-host-local evidence, HMAC-SHA256 session auth, pinned identities, exact transcript sequence/count with payload hashes, replay/sequence controls, two-sided copied-profile/source hashes, Program Files mutation rejection, local source-safety preflight for live proof, invitation lifecycle receipt, `maxJsonLineBytes=4096`, no raw preflight paths, no absolute private proof paths, no hidden truthy overclaim fields, exact accepted/rejected/transcript key sets, live negative-case session-security hardening before runtime promotion, live physical rejection of `operator-supplied-runtime-host-kind`, and 16 required rejection reasons including signed unknown-field/schema mismatch; `acceptedLiveSecondHostCommandSourceProof=false`; `acceptedLiveSecondHostRuntimeDeliveryProof=false`; `newBeaLaunchCount=0`; `cdbAttachCount=0`; `baseOnlineMultiplayerReady=false`; `multiHostLanPlayProof=false`; `publicMatchmakingProof=false`; `nativeBeaNetcodeProof=false` |
| Second-host command-source harness | `1` server/client harness; `tools/build_winui_original_binary_second_host_command_source_bundle.py` plus `tools/winui_original_binary_second_host_command_source_client.py`; `test:winui-original-binary-second-host-command-source-builder`; emits only a checker-accepted private proof bundle from a distinct private-LAN host or VM command source; computes or fixture-labels host/client machine fingerprints with redacted hostname/platform fingerprints, can hash copied-profile and installed-game roots locally for source safety, requires RFC1918/ULA source evidence, enforces `maxJsonLineBytes=4096` before JSON parse, confines HMAC invitation to OS temp outside the repo with exclusive-create/no-overwrite semantics, validates client/server expiry, deletes after server completion, records a sanitized invitation lifecycle receipt, keeps transient invitation credential transport out of artifacts, records exact transcript events with signed request/response payload hashes, live bad-HMAC/pre-session/replay/server-observed stale-future-timestamp/sequence/pinned-identity/compatibility-key/metadata-slot/unknown-field-schema/direct-input-bypass rejection, VM-labeled proof `samePhysicalMachineOnly=true`, physical second-host proof `samePhysicalMachineOnly=false`, live physical promotion rejecting operator-supplied runtime-host-kind evidence, and two-sided source-safety hashes; hash-only source evidence is not enough for future live promotion; `acceptedLiveSecondHostCommandSourceProof=false` until a real live private proof is run and accepted; `acceptedLiveSecondHostRuntimeDeliveryProof=false`; `newBeaLaunchCount=0`; `cdbAttachCount=0`; `hostHelperInputSent=false`; not Host/Join enablement or player-ready netplay |
| Second-host runtime-delivery bridge adapter | `1` public-safe adapter/provenance contract plus private release-denied helper tooling; `original-binary-online-second-host-runtime-delivery-bridge.v1.json`; scope `second-host-command-source-to-runtime-delivery-bridge-not-player-ready-online`; `secondHostRuntimeDeliveryBridgeAdapterReady=true`; `upstreamPrivateLanProofHashMatch=true`; `acceptedLiveSecondHostRuntimeDeliveryProof=false`; `runtimeDrivenBySecondHostCommandSource=false`; `baseOnlineMultiplayerReady=false`; `multiHostLanPlayProof=false`; `publicMatchmakingProof=false`; `nativeBeaNetcodeProof=false`; `hostJoinControlsMayBeEnabled=false`; maps the second-host command-source proof contract to the existing host-authority runtime-delivery proof class, but host-runtime-delivery-from-source-bound-distinct-command-source remains unproven |
| Second-host runtime executor builder | `1` public-safe contract plus private release-denied builder/checker tooling; `original-binary-online-second-host-runtime-executor.v1.json`; scope `second-host-command-source-to-fresh-copied-runtime-executor-not-player-ready-online`; `runtimeExecutorBuilderReady=true`; `upstreamPrivateLanProofHashMatch=true`; `bridgeProofSameBundleOwnership=true`; `sourceBinding.secondHostInvitationLifecycleSha256`; `sourceSafety.evidenceMode=local-preflight-computed` required for live runtime promotion; `acceptedLiveSecondHostRuntimeDeliveryProof=false`; `runtimeDrivenBySecondHostCommandSource=false`; `baseOnlineMultiplayerReady=false`; `hostJoinControlsMayBeEnabled=false`; live promotion is blocked until second-host command-source security hardening proves live transcript-derived negative cases and until source-bound command payload plus invitation-lifecycle receipt hashes reach scheduler, bridge, runtime input-window, exact-PID CDB, mapped P2 sequence, and host-helper delivery receipts with `hostHelperInputBoundToSecondHostCommandSource=true`, `hostHelperInputBoundToMappedP2Sequence=true`, mapped route `P2/inputDevice1/bottom-split-half`, and `gameInputSentBySecondHostClient=false`; runtime input-window and exact-PID CDB raw bodies must carry the same boundary; the secure N-slot runtime executor may retry only the exact first-baseline CDB render-warmup miss, while final accepted artifacts still require the unchanged movement-state validator |
| Second-host runtime promotion guard | `1` public-safe no-BEA shape preflight; `tools/winui_safe_copy_online_second_host_runtime_promotion_guard.py`; scope `source-bound-second-host-command-to-copied-runtime-causality-not-host-join-enable`; rejects the current compatibility runtime executor as Host/Join-grade runtime causality; future shape preflight requires a candidate to claim runtime input derived from and driven by the second-host command source, a candidate runtime-delivery acceptance field, one same-run artifact chain, no fixture/posthoc binding, accepted second-host request payload plus invitation-lifecycle hash receipts in scheduler, bridge, runtime input-window, exact-PID CDB, mapped P2 sequence, and host-helper delivery evidence; that delivery field is a future-candidate input only and current accepted delivery proof remains false; live acceptance still belongs to the file-backed runtime-causality gate |
| Second-host runtime causality gate | `1` public-safe validator/contract; `original-binary-online-second-host-runtime-causality.v1.json`; `tools/winui_safe_copy_online_second_host_runtime_causality_check.py`; scope `second-host-runtime-causality-proof-gate-not-host-join-enable`; requires candidate-bundle-relative artifacts contained under the private runtime proof root plus semantic raw-artifact receipt recomputation, role-specific raw-evidence bodies, role-specific material descriptors, and private-root-contained raw-material file hash recomputation across command-source, scheduler, bridge, runtime input-window, exact-PID CDB, mapped P2 sequence, host-helper delivery, copied-runtime artifact, copied-runtime executable hash, and process identity; rejects receipt-only, envelope-only or hash-only synthetic files, JSON-only forged artifacts, fixture/posthoc, swapped-run, stale-CDB, stale mapped-P2/host-helper aliases, PID-mismatched, host-authority-derived, operator-source-safety, unknown source-hash-mode, outside-private-root, self-test-only raw artifacts, hidden truthy Host/Join/direct-input overclaims, missing-boundary-key, and Host/Join-overclaim candidates; current truth remains `acceptedLiveSecondHostRuntimeCausalityProof=false`, `acceptedLiveSecondHostRuntimeDeliveryProof=false`, `runtimeInputDerivedFromSecondHostCommandSource=false`, `runtimeDrivenBySecondHostCommandSource=false`, `hostJoinControlsMayBeEnabled=false`, and `baseOnlineMultiplayerReady=false` |
| Second-host runtime-causality candidate materializer | `1` public-safe builder/preflight; `tools/build_winui_original_binary_second_host_runtime_causality_candidate.py`; focused package script `test:winui-original-binary-second-host-runtime-causality-builder`; self-test candidate scope `file-backed-self-test-only-not-live-second-host-runtime-causality`; raw-material plan schema `winui-original-binary-second-host-runtime-causality-raw-material-plan.v1`; raw-material manifest schema `winui-original-binary-second-host-runtime-causality-raw-material-manifest.v1`; raw-material plan scope `raw-material-intake-plan-not-live-runtime-causality-proof`; raw-material manifest scope `raw-material-manifest-preflight-not-live-runtime-causality-proof`; writes a checker-accepted self-test candidate only in explicit fixture mode, rejects the current compatibility executor and truthy-edited executor attempts without writing a candidate, emits a private-root-contained raw-material intake plan for the `8` source-bound roles, derives a candidate-bundle-relative raw-material manifest with recomputed artifact/raw-evidence hashes, and keeps `acceptedLiveSecondHostRuntimeCausalityProof=false`, `acceptedLiveSecondHostRuntimeDeliveryProof=false`, `hostJoinControlsMayBeEnabled=false`, and `baseOnlineMultiplayerReady=false`; live materialization still requires a future raw-evidence adapter fed by a real source-bound second-host command-source/runtime chain |
| Host/Join composite enablement gate | `1` public-safe contract/checker; `original-binary-online-host-join-enablement.v1.json`; scope `host-join-controls-composite-proof-gate-not-player-ready-online`; Host and Join require both `distinct-private-host-command-source-proof` and `host-runtime-delivery-from-source-bound-distinct-command-source`; command-source proof alone is rejected; fixture, self-test, and posthoc compatibility artifacts are rejected for enablement; `hostJoinControlsMayBeEnabled=false`; `baseOnlineMultiplayerReady=false`; `publicMatchmakingProof=false`; `nativeBeaNetcodeProof=false`; `activeP3P4OriginalBinaryGameplayProof=false` |
| WSL2 remote-client command-source smoke | `1` same-physical-machine WSL2 client proof; transport `wsl2-remote-client-tcp-jsonl-auth-smoke`; `acceptedCommandId=wsl-remote-client-p2-forward-0001`; `acceptedOriginalBinaryGameplaySlots=P1,P2`; `metadataOnlySlots=P3,P4`; `rejectedGameplayRouteSlots=P3,P4`; `gameInputSentByWslClient=false`; `hostHelperInputSent=false`; `multiHostLanProof=false`; `nPlayerOriginalBinaryRuntimeProof=0` |
| Joined-session same-host runtime-authority proof | `1` wrapper proof; `joined-session-same-host-runtime-authority-not-online-play`; `joinedSessionSameHostRuntimeAuthorityChainProven=true`; `acceptedJoinTicketSlot=P2`; `joinTicketRuntimeRelayHashMatched=true`; `samePhysicalMachineWslPredecessor=true`; `sameHostOnly=true`; `hostAuthorityModel=single-host-authoritative-copied-session`; `hostAuthorityScope=single-copied-host-exact-pid-state-graph`; `hostHelperInputSentByAcceptedRuntimeAuthority=true`; `wrapperNewBeaLaunchCount=0`; `wrapperCdbAttachCount=0`; `publicMatchmakingProof=false`; `multiHostLanProof=false`; `nativeBeaNetcodeProof=false`; `secondPhysicalHostProof=false`; `nPlayerOriginalBinaryRuntimeProof=0` |
| Joined-session runtime-causality proof | `1` fresh same-host copied-runtime proof; `joined-session-fresh-runtime-causality-same-host-not-online-play`; `joinedSessionRuntimeCausalityProven=true`; `joinTicketRuntimeRelayPathMatchCount=1`; `newBeaLaunchCount=1`; `cdbAttachCount=1`; `visualCaptureCount=7`; `deliveredOriginalBinaryCommandCount=2`; `hostHelperInputSent=true`; `exactPidCdbStateRowsProven=true`; `baseOnlineMultiplayerReady=false`; `publicMatchmakingProof=false`; `multiHostLanProof=false`; `nativeBeaNetcodeProof=false`; `nPlayerOriginalBinaryRuntimeProof=0`; `activeP3P4OriginalBinaryGameplayProof=false` |
| Joined-session control-lifecycle proof | `1` same-host session-control lifecycle proof; `joined-session-control-lifecycle-same-host-not-online-play`; `joined-session-same-host-session-control-not-online-play`; `sessionControlLifecycleProven=true`; `acceptedControlActionCount=11`; `rejectedControlCaseCount=22`; `metadata-reconnect-only-not-runtime-reconnect`; `sameHostOnly=true`; `samePhysicalMachineOnly=true`; `newBeaLaunchCount=0`; `cdbAttachCount=0`; `gameInputSentBySessionControl=false`; `baseOnlineMultiplayerReady=false`; `publicMatchmakingProof=false`; `multiHostLanProof=false`; `nativeBeaNetcodeProof=false`; `activeP3P4OriginalBinaryGameplayProof=false` |
| Original Binary Online Mode Classifier | `1` public-safe mode classifier; `original-binary-online-mode-classifier.v1.json`; `currentRuntimeModeClassification=unclassified-local-multiplayer`; `runtime-observed-local-splitscreen-not-co-op-or-versus-proof`; `modeRuntimeProofSlices=0`; `coOpVersusModeRuntimeProofSlices=0`; `teamAssignmentAuthority=schema-only-not-runtime-proof`; rejects runtime mode proof from `sessionType alone`, `modeFamily alone`, `schema-only teamAssignments`, and `slotCapacity=4` |
| Level-850 P1/P2 mode-semantics observer | `1` public-safe observer proof; `original-binary-online-level850-mode-semantics-observer.v1.json`; scope `level850-p1p2-mode-semantics-observer-not-coop-versus-proof`; `modeSemanticsObserverProven=true`; `hookTargetCount=21`; `newBeaLaunchCount=1`; `cdbAttachCount=1`; `boundedCaptureCount=2`; `visualCaptureCount=2`; `forcedWinDeathRespawn=false`; `modeRuntimeProofSlicesAdded=0`; `coOpVersusModeRuntimeProofSlicesAdded=0`; `currentRuntimeModeClassification=unclassified-local-multiplayer` |
| Multiplayer outcome-semantics matrix | `1` public-safe static candidate matrix; `original-binary-online-multiplayer-outcome-semantics-matrix.v1.json`; scope `original-binary-p1p2-multiplayer-outcome-semantics-matrix-not-runtime-proof`; candidate levels `851/854/855/860`; selected runtime candidate `854`; `requiredHookTargetCount=10`; `runtimeProofCreatedByThisMatrix=false`; `newBeaLaunchCount=0`; `cdbAttachCount=0`; `modeRuntimeProofSlicesAdded=0`; `coOpVersusModeRuntimeProofSlicesAdded=0`; `nPlayerOriginalBinaryRuntimeProof=0`; `baseOnlineMultiplayerReady=false`; `activeP3P4OriginalBinaryGameplayProof=false` |
| Level-854 P1/P2 outcome-semantics observer | `1` public-safe copied-runtime observer surface; `original-binary-online-level854-outcome-semantics-observer.v1.json`; scope `level854-p1p2-outcome-semantics-observer-not-coop-versus-proof`; `outcomeObserverSurfaceProven=true`; `outcomeHookSurfaceObserved=true`; `selectedRuntimeCandidate=854`; `outcomeHookTargetCount=10`; `hookTargetCount=21`; `newBeaLaunchCount=1`; `cdbAttachCount=1`; `boundedCaptureCount=2`; `visualCaptureCount=2`; `outcomeTransitionHitCount=0`; `naturalOutcomeTransitionObserved=false`; `runtimeOutcomeProof=false`; `forcedOutcomeTransition=false`; `forcedWinDeathRespawn=false`; `modeRuntimeProofSlicesAdded=0`; `coOpVersusModeRuntimeProofSlicesAdded=0`; `currentRuntimeModeClassification=unclassified-local-multiplayer` |
| Level-854 P1/P2 input-assisted outcome attempt | `1` public-safe copied-runtime stimulus-attempt diagnostic; `original-binary-online-level854-input-assisted-outcome.v1.json`; scope `level854-input-assisted-outcome-transition-attempt-not-online-proof`; `inputAssistedOutcomeAttempted=true`; `inputWindowCount=8`; `stimulusWindowCount=4`; `waitControlWindowCount=4`; `inputAssistHitCount=124`; `inputWindowOutcomeTransitionHitCount=0`; `waitWindowOutcomeTransitionHitCount=0`; `positiveStimulusWindowCount=0`; `runtimeOutcomeProof=false`; `stimulusAttemptOnly=true`; `newBeaLaunchCount=1`; `cdbAttachCount=1`; `boundedCaptureCount=10`; `visualCaptureCount=10`; `renderPlayers=2`; `renderLevel=854`; `activeP3P4OriginalBinaryGameplayProof=false` |
| Level-854 P1/P2 fire-handoff/projectile diagnostic | `1` public-safe copied-runtime fire-handoff/projectile diagnostic; `original-binary-online-level854-fire-handoff.v1.json`; scope `level854-fire-input-to-weapon-handoff-not-online-proof`; `copiedDefaultOptionsFireWeaponQe=true`; `button18RuntimeDispatchObserved=false`; `button19RuntimeDispatchObserved=true`; `button18DispatchCount=0`; `button19DispatchCount=3`; `sameWindowInputFireHandoffWindowCount=3`; `sameWindowInputFireHandoffObserved=true`; `sameWindowFireBurstPointerChainWindowCount=1`; `sameWindowFireBurstPointerChainObserved=true`; `sameWindowOrderedFireBurstPointerChainWindowCount=0`; `sameWindowOrderedFireBurstPointerChainObserved=false`; `waitWindowFireButtonDispatchCount=0`; `waitWindowCausalProof=false`; `battleEngineProjectileTotalHitCount=1200`; `projectileFactoryTotalHitCount=2045`; `roundProjectileTotalHitCount=2045`; `sameWindowProjectileFactoryObserved=true`; `roundProjectileSameWindowCoincidenceObserved=true`; `roundProjectileCausalityProof=false`; `runtimeOutcomeProof=false`; `newBeaLaunchCount=1`; `cdbAttachCount=1`; `boundedCaptureCount=10`; `visualCaptureCount=10`; `renderPlayers=2`; `renderLevel=854`; `activeP3P4OriginalBinaryGameplayProof=false` |
| Level-854 P1/P2 fire-to-damage/outcome observer diagnostic | `1` public-safe copied-runtime fire-to-damage/outcome observer diagnostic; `original-binary-online-level854-fire-damage-outcome.v1.json`; scope `level854-fire-to-damage-outcome-observer-not-online-proof`; `copiedDefaultOptionsFireWeaponQe=true`; `button18RuntimeDispatchObserved=false`; `button19RuntimeDispatchObserved=true`; `button18DispatchCount=0`; `button19DispatchCount=3`; `sameWindowFireHandoffWindowCount=3`; `sameWindowFireBurstPointerChainWindowCount=2`; `sameWindowDamageSurfaceWindowCount=1`; `sameWindowUnitApplyDamageWindowCount=1`; `sameWindowOutcomeSurfaceWindowCount=0`; `waitWindowFireButtonDispatchCount=0`; `waitWindowDamageHitCount=27`; `waitWindowOutcomeHitCount=0`; `damageHitCount=151`; `unitApplyDamageHitCount=61`; `roundCollisionHitCount=90`; `outcomeHitCount=0`; `damageProof=false`; `runtimeOutcomeProof=false`; `fireToDamageOutcomePromotion=false`; `newBeaLaunchCount=1`; `cdbAttachCount=1`; `boundedCaptureCount=10`; `visualCaptureCount=10`; `renderPlayers=2`; `renderLevel=854`; `baseOnlineMultiplayerReady=false`; `activeP3P4OriginalBinaryGameplayProof=false` |
| Multi-host LAN/public online proof | `0` second-host LAN/public matchmaking/native-BEA-netcode proof slices |
| Physical gamepad proof | `0 physical DirectInput/gamepad runtime proof artifacts`; current host readiness is `blocked_no_present_gamepad` |

## Scalability And Mode Contract

`roadmap/original-binary-online-session-scalability-contract.v1.json` is the public-safe design contract for the online lane. It records the current retail/runtime cap as `originalBinaryPlayerSlotsProven=2`, `maxRetailPlayersProven=2`, `retailSlotsProven=P1,P2`, `retailViewpointsProven=2`, and `nPlayerOriginalBinaryRuntimeProof=0`. The current original-binary runtime profile is still P1/P2 local split-screen only; any more-than-two original-binary runtime support has `beyondTwoPlayersRequiresNewProofClass=true`.

The scalable architecture is intentionally broader than the current runtime proof: `modeScalableArchitecturePlanned=true`, `modeScalableContractStatus=design-only-unproven`, and future session descriptors must not hardcode exactly two players. They must carry `sessionType`, `participants[]`, profile-declared indexed slots, `minimumArchitectureAcceptanceSlots=4`, explicit `unsupportedSlotsRejected` behavior, and per-slot proof status.

The mode taxonomy is now classified but not runtime-proven: `roadmap/original-binary-online-mode-classifier.v1.json` records `currentRuntimeModeClassification=unclassified-local-multiplayer`, `runtime-observed-local-splitscreen-not-co-op-or-versus-proof`, `modeRuntimeProofSlices=0`, and `coOpVersusModeRuntimeProofSlices=0`. `cooperative`, `versus-free-for-all`, `team-versus`, and `spectator-admin` remain design-mode families only; `teamAssignmentAuthority=schema-only-not-runtime-proof`. Do not describe co-op/versus online support until runtime objective, win/death/respawn, team/friendly-fire, and mode-authority evidence exists.

`roadmap/original-binary-online-level850-mode-semantics-observer.v1.json` records the Level-850 P1/P2 mode-semantics observer. It proves only `level850-p1p2-mode-semantics-observer-not-coop-versus-proof`: one copied level-850/config-1 launch attached exact-PID CDB, observed two-player render state, and installed/read 21 hook targets around multiplayer gates, objective surfaces, win/loss, death, lives, and respawn paths. It keeps `forcedWinDeathRespawn=false`, `modeRuntimeProofSlicesAdded=0`, `coOpVersusModeRuntimeProofSlicesAdded=0`, `baseOnlineMultiplayerReady=false`, `publicMatchmakingProof=false`, `nativeBeaNetcodeProof=false`, and `activeP3P4OriginalBinaryGameplayProof=false`.

`roadmap/original-binary-online-multiplayer-outcome-semantics-matrix.v1.json` records the next public-safe P1/P2 outcome-semantics selection matrix. It proves only `static-candidate-matrix-not-runtime-outcome-proof`: candidate levels `851/854/855/860` have zero loose `LevelWon`/`LevelLost` rows in the current mission-events index, level `854` is selected as the first copied-runtime candidate, and future runtime proof must watch `CGame__MPDeclarePlayerWon`, `CGame__MPDeclareGameDrawn`, `CGame__DeclarePlayerDead`, `CGame__RespawnPlayer`, `CGame__GetPlayerLives`, `CGame__DeclareLevelWon`, `CGame__DeclareLevelLost`, and the IScript outcome thunks. It keeps `runtimeProofCreatedByThisMatrix=false`, `newBeaLaunchCount=0`, `cdbAttachCount=0`, `modeRuntimeProofSlicesAdded=0`, `coOpVersusModeRuntimeProofSlicesAdded=0`, `baseOnlineMultiplayerReady=false`, `nativeBeaNetcodeProof=false`, and `activeP3P4OriginalBinaryGameplayProof=false`.

`roadmap/original-binary-online-level854-outcome-semantics-observer.v1.json` records the Level-854 P1/P2 outcome-semantics observer. It proves only `level854-p1p2-outcome-semantics-observer-not-coop-versus-proof`: one copied level-854/config-1 launch attached exact-PID CDB, observed the two-player render graph, armed the 10 required matrix outcome hooks plus 11 supplemental context hooks, and recorded `outcomeObserverSurfaceProven=true`, `outcomeHookSurfaceObserved=true`, `selectedRuntimeCandidate=854`, `outcomeHookTargetCount=10`, `hookTargetCount=21`, `boundedCaptureCount=2`, and `visualCaptureCount=2`. It also records `outcomeTransitionHitCount=0`, `naturalOutcomeTransitionObserved=false`, `runtimeOutcomeProof=false`, `forcedOutcomeTransition=false`, `forcedWinDeathRespawn=false`, `modeRuntimeProofSlicesAdded=0`, `coOpVersusModeRuntimeProofSlicesAdded=0`, `baseOnlineMultiplayerReady=false`, `nativeBeaNetcodeProof=false`, and `activeP3P4OriginalBinaryGameplayProof=false`.

The secure N-slot runtime executor now proves one accepted same-workstation session-security proof can directly drive fresh copied level-850/config-1 BEA host-helper runtime runs for P1/P2, and the replayability checker proves the path repeats across two distinct copied-runtime artifacts while keeping P3/P4 metadata-only and gameplay-rejected; it still does not prove second-host LAN, matchmaking, native BEA netcode, or active P3/P4 runtime play. The current process/scheduler cardinality is now bounded at four client processes: `schedulerCardinalityProven=4`, `maxClientProcessesProven=4`, `schedulePolicy=stable-slot-order`, arrival order may differ from schedule order, and rejected extra-slot handling is required for unproven original-binary slots. The process layer now also has same-workstation-client/private-interface concurrent/barrier proof with `processConcurrencyModel=barrier-concurrent-client-processes`, `simultaneousClientProcessesProven=4`, `clientReadyBeforeBarrierReleaseCount=4`, `barrierReleaseAfterAllClientsReady=true`, `maxSimultaneousSocketConnectionsProven=4`, `privateLanReachableDuringRun=true`, `foreignPeersRejectedAfterAccept=true`, and `securityProofScope=minimal-smoke-hmac-envelope-not-full-session-security-proof`; `privateLanReachableDuringRun` here means a same-workstation private non-loopback interface bind/listener smoke, not second-host LAN reachability or multi-host play. That older concurrent process smoke is still only a minimal HMAC envelope, not full session-security proof. A separate same-workstation N-slot session-security message smoke now proves session-scoped canonical-message HMAC coverage, raw JSON line size rejection, strict schema allowlists, unknown-field rejection, nonce/tick/sequence/relay-plan/admission rejections, and P3/P4 gameplay rejection in an in-memory harness. The host-helper runtime delivery path still has proof only for the two original-binary gameplay slots P1/P2; P3/P4 remain metadata-only until a new runtime proof class exists, and the session-security smoke does not launch BEA or prove online gameplay.

`roadmap/original-binary-online-n-slot-session-schema.v1.json` is the first N-slot session schema proof. It records `slotCapacity=4`, `acceptedSessionParticipantCount=4`, `sessionType`, `participants[]`, profile-declared indexed slots, `P1/P2` active original-binary routes, and `P3/P4 metadata-only` participants with runtime route `unsupported-original-binary-active-slot`. Gameplay commands for `P3/P4` are rejected with `required-for-unproven-original-binary-slots`; schema rejection cases include disabled slots, duplicate slot/client identity, participant-slot mismatch, active original-binary slot count above two, spectator game input, invalid session type/mode/team, unknown fields, oversized messages, stale ticks, queue overflow/backpressure, and missing relay-plan hash. This advances online multiplayer architecture to an exactly four-slot session/schema layer while preserving `nPlayerOriginalBinaryRuntimeProof=0`; active original-binary gameplay remains proven only for P1/P2, more-than-four-player scaling remains unproven future work, and co-op/versus runtime behavior remains unproven.

`roadmap/original-binary-online-slot-ceiling-guard.v1.json` is the original-binary online slot-ceiling guard. It records `maxOriginalBinaryActiveSlotsProven=2`, `activeOriginalBinarySlotsProven=P1,P2`, `slotCapacity=4`, `acceptedSessionParticipantCount=4`, `P3/P4 metadata-only`, `unsupported-original-binary-active-slot`, and `beyondTwoPlayersRequiresNewProofClass=true`. It also records `absenceOfCurrentProofIsNotProofOfPermanentAbsence=true` and `permanentImpossibilityClaim=false`: `MAX_PLAYERS 4` and the source 3/4-player render branch are useful future research anchors, but they are not active P3/P4 original-binary gameplay proof today.

`roadmap/original-binary-online-p3p4-runtime-feasibility-map.v1.json` is the Original Binary Online P3/P4 Runtime Feasibility Map. It records `mapProofClass=static-blast-radius-map-not-runtime-proof`, `p3p4FeasibilityScope=static-blast-radius-not-runtime-proof`, `nPlayerOriginalBinaryRuntimeProof=0`, `sourceOnlyMaxPlayersIsRuntimeProof=false`, `quadSplitBranchIsRuntimeProof=false`, `mapCompleteForRuntimeAttempt=false`, and `safeToPatchMPlayersAbove2=false`. The map names current blockers around `mPlayers`, controller assignment, `VIEWPOINTS 2`, reconnect UI, lives/respawn/results, and CPlayer dispatch. It advances the scalable-online plan without proving active P3/P4 runtime gameplay.

The Local session-directory smoke is recorded in `roadmap/original-binary-online-session-scalability-contract.v1.json` as `sessionDirectorySmokePolicy`. It proves only `same-workstation-local-directory-smoke-not-public-matchmaking`: `registeredSessionCount=1`, `compatibleListingCount=1`, `acceptedJoinTicketCount=1`, `rejectedDirectoryCaseCount=14`, and `publicMatchmakingProof=false`. It does not launch BEA, attach CDB, send game input, prove public matchmaking, prove multi-host LAN play, prove native BEA netcode, or prove active P3/P4 original-binary gameplay.

The WSL2 remote-client command-source smoke is recorded in `roadmap/original-binary-online-session-scalability-contract.v1.json` as `wslRemoteClientSmokePolicy`. It proves only a same physical machine cross-environment client path: a WSL2 Linux Python client connects to a Windows private-interface listener, verifies pinned server identity, authenticates with an ephemeral HMAC credential, rejects P3/P4 gameplay routing, and accepts `acceptedCommandId=wsl-remote-client-p2-forward-0001` as a P2 envelope that would forward to the already-proven private LAN transport command. It does not launch BEA, attach CDB, send game input, prove a second physical host, prove multi-host LAN play, prove public matchmaking, prove native BEA netcode, or prove active P3/P4 original-binary gameplay.

The joined-session same-host runtime-authority proof is recorded in `roadmap/original-binary-online-session-scalability-contract.v1.json` as `joinedSessionSameHostRuntimeAuthorityPolicy`. It proves only `joined-session-same-host-runtime-authority-not-online-play`: the accepted local directory P2 join-ticket selects the bounded P1/P2 relay path, and the same-physical-machine WSL command-source predecessor is linked to that accepted P2 route already replayed through secure N-slot runtime executor and exact-PID state-authority proofs. The WSL smoke is not itself a relay-hash carrier. It records `joinedSessionSameHostRuntimeAuthorityChainProven=true`, `acceptedJoinTicketSlot=P2`, `joinTicketRuntimeRelayHashMatched=true`, `samePhysicalMachineWslPredecessor=true`, `sameHostOnly=true`, `hostAuthorityModel=single-host-authoritative-copied-session`, `hostAuthorityScope=single-copied-host-exact-pid-state-graph`, `hostHelperInputSentByAcceptedRuntimeAuthority=true`, `wrapperNewBeaLaunchCount=0`, `wrapperCdbAttachCount=0`, `publicMatchmakingProof=false`, `multiHostLanProof=false`, `nativeBeaNetcodeProof=false`, `secondPhysicalHostProof=false`, `nPlayerOriginalBinaryRuntimeProof=0`, `activeP3P4OriginalBinaryGameplayProof=false`, `joinedSessionVisibleMovementCausalityProof=false`, and `privateProofReleaseExcludedByPolicy=true`. It does not prove a second physical host, public matchmaking, native BEA netcode, active P3/P4 original-binary gameplay, more-than-two original-binary runtime players, or co-op/versus online semantics.

The joined-session runtime-causality proof is recorded in `roadmap/original-binary-online-session-scalability-contract.v1.json` as `joinedSessionRuntimeCausalityPolicy`. It proves only `joined-session-fresh-runtime-causality-same-host-not-online-play`: the accepted joined-session P2 ticket/relay chain selects the same runtime-compatible P1/P2 relay hash and derived input sequence that drove one fresh copied BEA level-850/config-1 secure N-slot runtime executor run. It records `joinedSessionRuntimeCausalityProven=true`, `joinTicketRuntimeRelayPathMatchCount=1`, `joinTicketRuntimeRelayHashMatched=true`, `samePhysicalMachineWslPredecessor=true`, `newBeaLaunchCount=1`, `cdbAttachCount=1`, `visualCaptureCount=7`, `deliveredOriginalBinaryCommandCount=2`, `hostHelperInputSent=true`, `exactPidCdbStateRowsProven=true`, `baseOnlineMultiplayerReady=false`, `publicMatchmakingProof=false`, `multiHostLanProof=false`, `nativeBeaNetcodeProof=false`, `nPlayerOriginalBinaryRuntimeProof=0`, `activeP3P4OriginalBinaryGameplayProof=false`, and `joinedSessionVisibleMovementCausalityProof=false`. It does not prove a second physical host, public matchmaking, native BEA netcode, active P3/P4 original-binary gameplay, more-than-two original-binary runtime players, co-op/versus online semantics, deterministic sync, rollback, anti-cheat, or online parity.

The Joined-session control-lifecycle proof is recorded in `roadmap/original-binary-online-session-scalability-contract.v1.json` as `joinedSessionControlLifecyclePolicy`. It proves only `joined-session-control-lifecycle-same-host-not-online-play` / `joined-session-same-host-session-control-not-online-play`: session registration, compatible listing, P2 ticket issue/activation, heartbeat, pause/resume, metadata-only soft reconnect, spectator/admin metadata queries, and graceful leave are represented as a public-safe control lifecycle around the already accepted P1/P2 joined-session runtime path. It records `sessionControlLifecycleProven=true`, `acceptedControlActionCount=11`, `rejectedControlCaseCount=22`, `metadata-reconnect-only-not-runtime-reconnect`, `sameHostOnly=true`, `samePhysicalMachineOnly=true`, `newBeaLaunchCount=0`, `cdbAttachCount=0`, `gameInputSentBySessionControl=false`, `baseOnlineMultiplayerReady=false`, `publicMatchmakingProof=false`, `multiHostLanProof=false`, `nativeBeaNetcodeProof=false`, and `activeP3P4OriginalBinaryGameplayProof=false`. It does not prove BEA launch/runtime behavior, direct game input, a second physical host, public matchmaking, native BEA netcode, active P3/P4 original-binary gameplay, co-op/versus runtime semantics, deterministic sync, rollback, anti-cheat, or no-noticeable-difference parity.

The Original Binary Online Mode Classifier is recorded in `roadmap/original-binary-online-session-scalability-contract.v1.json` as `modeClassifierPolicy` and in `roadmap/original-binary-online-mode-classifier.v1.json`. It proves only `static-source-session-taxonomy-not-runtime-mode-proof` for `original-binary-online-mode-classifier-not-runtime-mode-proof`: the current copied level-850/runtime evidence classifies as `currentRuntimeModeClassification=unclassified-local-multiplayer` with status `runtime-observed-local-splitscreen-not-co-op-or-versus-proof`. It records `modeRuntimeProofSlices=0`, `coOpVersusModeRuntimeProofSlices=0`, `coOpModeRuntimeProof=false`, `versusModeRuntimeProof=false`, `teamVersusRuntimeProof=false`, `spectatorAdminRuntimeProof=false`, and `teamAssignmentAuthority=schema-only-not-runtime-proof`. It rejects runtime mode proof from `sessionType alone`, `modeFamily alone`, `schema-only teamAssignments`, metadata-only spectator/admin rows, `slotCapacity=4`, same-host/WSL/private-interface artifacts, local session-directory smoke, host-authority wrapper scaffolding, or joined-session same-host proofs.

## Preferred Ladder

1. **Host-authoritative copied-session proof**

   Run one safe copied `BEA.exe` in local split-screen mode. Treat the original binary as the simulation host. A helper receives a mock remote input command and feeds only the P2/bottom-player route.

   First acceptable claim: remote-command-shaped loopback input bridge into one copied original-binary session.

2. **Local relay and session descriptor**

   Add a local helper/relay contract that describes the host session without public networking: clean specimen hash, selected patch keys, copied profile manifest hash, launch arguments, level, player slot, compatibility key, and compatible helper/protocol version.

   First acceptable claim: local session metadata and relay contract are generated and validated.

3. **Private-interface relay prototype**

   Only after loopback P2 proof and localhost session metadata are reliable, allow a private relay mode that sends remote input to the host helper. Private session discovery/join metadata is not public matchmaking.

   First acceptable claims: private relay can deliver remote input to the same proven P2 route; private-interface transport can authenticate and bound a command envelope before it would hand off to that relay; a separate same-workstation client process can source the bounded command envelope without direct game input.

4. **Public matchmaking investigation**

   Public matchmaking requires server identity, versioned protocol, session listing, NAT/relay posture, abuse controls, and operator secrets outside git.

   First acceptable claim: design/spec and local server smoke only.

5. **Dual-binary sync research**

   Do not attempt lockstep/rollback/two-client parity until repeated deterministic replay/state-sync evidence exists. Retail local split-screen does not by itself answer this.

## First Proof Slice Completed

The first online-shaped proof is local and non-networked:

1. Prepare one app-owned copied game profile from a clean retail source.
2. Apply only proven copied-executable rows needed for windowed safe launch.
3. Launch `-skipfmv -level 850 -configuration 1`.
4. Build a local loopback proof bundle with helper version `loopback-helper.v1`, protocol version `loopback-input.v1`, clean specimen hash, copied profile manifest hash, patch keys, launch arguments, level, controller configuration, command id, rejected malformed/P1 command rows, and the CDB input-window index.
5. Accept a mock remote command `loopback-p2-forward-0001` with `remoteSlot=P2`, `command=movement-forward`, and mapped focused input sequence `down:E,wait:500,up:E`.
6. Prove with exact-PID CDB that the expected controller/player route and movement-state path fires for P2/bottom only.
7. Capture bounded visual evidence, but keep CDB state as the primary first proof.

Accepted result:

```powershell
py -3 tools\build_winui_original_binary_loopback_p2_input_bundle.py <private-live-runtime-artifact>
py -3 tools\winui_safe_copy_online_loopback_p2_input_check.py <private-loopback-proof-bundle> --expected-controller-configuration 1
```

The checker accepted `transport=local-loopback-mock`, launch args `-skipfmv -level 850 -configuration 1`, `4` visual captures, and P2 evidence with `11` button-31 receive rows plus `11` Walker forward entry/state-store rows. The installed executable, clean override executable, and source save/options hashes stayed unchanged. Raw artifact paths, screenshots, CDB logs, copied profile roots, and process identifiers stay private/release-excluded.

## Second Proof Slice Completed

The second online-shaped proof is localhost-only and does not launch BEA again:

1. Read the accepted loopback proof bundle.
2. Revalidate the referenced loopback bundle and its live runtime artifact.
3. Generate a session descriptor with helper version `local-relay-helper.v1`, protocol version `local-relay-input.v1`, clean specimen hash, copied profile manifest hash, exact patch keys, launch arguments, level, controller configuration, remote slot, upstream loopback proof hash, and compatibility key.
4. Open a localhost-only TCP JSONL relay bound to `127.0.0.1`.
5. Exchange a replayable nine-message transcript: session hello/accepted, malformed command/rejected, P1 wrong-slot command/rejected, P2 movement command/accepted, close, and server stopped.
6. Preserve explicit negative flags for public network sockets, LAN relay claim, matchmaking, public server claim, native BEA netcode, NAT traversal, anti-cheat, deterministic sync, two-client parity, physical gamepad behavior, and rebuild parity.

Accepted result:

```powershell
py -3 tools\build_winui_original_binary_local_relay_session_bundle.py <private-loopback-proof-bundle>
py -3 tools\winui_safe_copy_online_local_relay_session_check.py <private-local-relay-proof-bundle> --expected-controller-configuration 1
```

The checker accepted `transport=localhost-tcp-jsonl`, `bindHost=127.0.0.1`, helper version `local-relay-helper.v1`, protocol version `local-relay-input.v1`, command `local-relay-p2-forward-0001`, upstream command `loopback-p2-forward-0001`, and a nine-message transcript. This proves local relay/session compatibility metadata and command acceptance only; the relay proof does not itself send game input or prove LAN/public online behavior.

Suggested existing anchors and probes:

| Purpose | Existing anchor |
| --- | --- |
| Local-multiplayer runtime state | `tools/runtime-probes/local-multiplayer-level850-input-isolation-observer.cdb.txt` |
| Input-to-state handoff | `tools/runtime-probes/local-multiplayer-level850-input-state-delta-observer.cdb.txt` |
| Controller dispatch | `0x0042e4d0 CController__SendButtonAction` |
| Player receive/state | `0x004d3110 CPlayer__ReceiveButtonActionState` |

## Third Proof Slice Completed

The third online-shaped proof is local/private and launches BEA through the safe copied-profile harness:

1. Build a fresh level-850/config-1 copied BEA runtime artifact with `wait:300` followed by `down:E,wait:500,up:E`.
2. Attach exact-PID CDB with `tools/runtime-probes/local-multiplayer-level850-input-state-delta-observer.cdb.txt`.
3. Build a fresh loopback P2 proof bundle from that runtime artifact.
4. Build a fresh localhost relay/session proof bundle from that loopback proof.
5. Build a private relay-delivery bundle that verifies the relay command is accepted by the safe-copy host-helper delivery adapter.
6. Preserve separate truth fields: `relaySideGameInputSent=false`, `hostHelperInputSent=true`, and `gameInputDeliveryEvidence=fresh-host-helper-cdb-proof`.

Accepted result:

```powershell
py -3 tools\build_winui_original_binary_private_relay_delivery_bundle.py <private-local-relay-proof-bundle>
py -3 tools\winui_safe_copy_online_private_relay_delivery_check.py <private-relay-delivery-proof-bundle> --expected-controller-configuration 1
```

The checker accepted `transport=localhost-relay-host-helper-adapter`, command `private-relay-p2-forward-0001`, relay command `local-relay-p2-forward-0001`, upstream command `loopback-p2-forward-0001`, mapped input `down:E,wait:500,up:E`, `hostHelperInputSent=true`, and `relaySideGameInputSent=false`. The fresh runtime proof recorded `5` visual captures, distinct runtime player pointers `p0=0472b090` and `p1=04742890`, and P2 evidence with `12` button-31 receive rows, `12` Walker forward entry rows, and `12` Walker forward state-store rows.

This proves private/local relay-delivery adapter behavior into the host-helper path only. It is still not LAN transport, public matchmaking, public relay/server behavior, native BEA netcode, NAT traversal, deterministic sync, rollback, anti-cheat, two-client parity, physical gamepad behavior, rebuild parity, or no-noticeable-difference online parity.

## Fourth Proof Slice Completed

The fourth online-shaped proof is a same-workstation private-interface transport/auth smoke and does not launch BEA again:

1. Read the accepted private relay-delivery proof bundle.
2. Revalidate the referenced private relay, localhost relay/session, loopback P2, and fresh host-helper CDB evidence chain.
3. Bind a real TCP JSONL listener to private non-loopback host `<private-non-loopback-host>` for this workstation smoke.
4. Require protocol `private-lan-transport-input.v1`, ephemeral HMAC-SHA256 credentials, pinned server identity, nonce freshness, replay rejection, command sequencing, compatibility checks, P2-only slot acceptance, and a one-command rate limit. The protocol name is historical; this proof is a same-workstation private-interface smoke, not second-host LAN reachability.
5. Accept one signed command envelope `private-lan-p2-forward-0001` that would forward to already-proven `private-relay-p2-forward-0001`.
6. Reject missing auth, bad HMAC, replayed nonce, expired timestamp, sequence gap, wrong command id, wrong server identity, rate limit, compatibility mismatch, P1/wrong slot, loopback-positive claim, public-bind claim, and direct-input claim.
7. Preserve separate truth fields: `gameInputSentByTransport=false`, `hostHelperInputSent=false`, and upstream private-relay evidence `hostHelperInputSent=true`.

Accepted result:

```powershell
py -3 tools\build_winui_original_binary_private_lan_transport_smoke_bundle.py <private-relay-delivery-proof-bundle> --bind-host <private-non-loopback-host>
py -3 tools\winui_safe_copy_online_private_lan_transport_smoke_check.py <private-lan-transport-smoke-proof-bundle> --expected-controller-configuration 1
```

The checker accepted `transport=private-lan-tcp-jsonl-auth-smoke`, `bindHost=<private-non-loopback-host>`, command `private-lan-p2-forward-0001`, forward target `private-relay-p2-forward-0001`, `authorization.scheme=HMAC-SHA256`, `credentialStorage=ephemeral-not-serialized`, `serverIdentityMode=pinned-fingerprint`, `replayCacheEnabled=true`, `sequenceEnforced=true`, and a `25`-message / `27`-event transcript. Wave hardening on 2026-06-18 changed the host to require the exact allowlisted command id before accepting any signed command. This proves a same-workstation private-interface transport/auth envelope can be accepted and bounded before relay handoff only. It does not prove second-host LAN reachability, production-grade server identity, multi-host LAN play, public matchmaking, public relay/server behavior, native BEA netcode, NAT traversal, deterministic sync, rollback, anti-cheat, dual-client parity, physical gamepad behavior, rebuild parity, or no-noticeable-difference online parity.

## Fifth Proof Slice Completed

The fifth online-shaped proof is same-workstation process-separated and does not launch BEA again:

1. Read the accepted private LAN transport smoke proof bundle.
2. Revalidate the private LAN, private relay-delivery, localhost relay/session, loopback P2, and fresh host-helper CDB evidence chain.
3. Bind a private non-loopback TCP JSONL listener on `<private-non-loopback-host>`.
4. Spawn a separate Python client process with a distinct PID.
5. Pass ephemeral credentials to the client process through stdin only; do not serialize the raw credential into the artifact, command line, environment, stdout, or stderr.
6. Require protocol `private-remote-client-input.v1`, HMAC-SHA256 authorization, pinned smoke server/client fingerprints, nonce freshness, replay rejection, command sequencing, compatibility checks, P2-only slot acceptance, exact command-id allowlisting, and a one-command rate limit.
7. Accept one signed command envelope `private-remote-client-p2-forward-0001` that would forward to already-proven `private-lan-p2-forward-0001`.
8. Preserve separate truth fields: `sameWorkstationOnly=true`, `gameInputSentByRemoteClient=false`, `hostHelperInputSent=false`, and upstream private LAN transport evidence `gameInputSentByTransport=false`.

Accepted result:

```powershell
py -3 tools\build_winui_original_binary_private_remote_client_smoke_bundle.py <private-lan-transport-smoke-proof-bundle> --bind-host <private-non-loopback-host>
py -3 tools\winui_safe_copy_online_private_remote_client_smoke_check.py <private-remote-client-smoke-proof-bundle> --expected-controller-configuration 1
```

The checker accepted `transport=private-remote-client-tcp-jsonl-auth-smoke`, `bindHost=<private-non-loopback-host>`, process model `separate-python-process`, `clientProcessDifferentFromBuilder=true`, `clientVerifiedServerIdentity=true`, command `private-remote-client-p2-forward-0001`, forward target `private-lan-p2-forward-0001`, `authorization.scheme=HMAC-SHA256`, `credentialStorage=ephemeral-not-serialized`, `serverIdentityMode=pinned-fingerprint`, `clientIdentityMode=pinned-fingerprint`, `replayCacheEnabled=true`, `sequenceEnforced=true`, and an `11`-message / `15`-event transcript. This proves a same-workstation separate client process can source a bounded private-interface command envelope before LAN transport handoff only. It does not prove multi-host LAN play, public matchmaking, public relay/server behavior, native BEA netcode, NAT traversal, deterministic sync, rollback, anti-cheat, dual-client parity, physical gamepad behavior, rebuild parity, or no-noticeable-difference online parity.

## Sixth Proof Slice Completed

The sixth online-shaped proof is a same-workstation two-client host-authority scheduler smoke and does not launch BEA again:

1. Read the accepted private remote-client smoke proof bundle.
2. Revalidate the private remote-client, private LAN, private relay-delivery, localhost relay/session, loopback P2, and fresh host-helper CDB evidence chain.
3. Bind a private non-loopback TCP JSONL listener on `<private-non-loopback-host>`.
4. Spawn two separate Python client processes for `P1` and `P2`, each with a distinct PID and slot identity.
5. Pass slot-scoped ephemeral credentials to each client process through stdin only; do not serialize raw credentials into the artifact, command line, environment, stdout, or stderr.
6. Require protocol `host-authority-two-client-input.v1`, HMAC-SHA256 authorization, pinned smoke server fingerprint, pinned per-slot client fingerprints, nonce freshness, replay rejection, command sequencing, compatibility checks, exact command-id allowlisting, and per-slot rate limits.
7. Accept one P2 command `host-authority-p2-forward-0001` and one P1 command `host-authority-p1-forward-0001`.
8. Preserve arrival order `P2`, then `P1`, while emitting deterministic host schedule order `P1`, then `P2`.
9. Preserve separate truth fields: `sameWorkstationOnly=true`, `gameInputSentByScheduler=false`, `hostHelperInputSent=false`, and upstream private remote-client evidence `gameInputSentByRemoteClient=false`.

Accepted result:

```powershell
py -3 tools\build_winui_original_binary_host_authority_two_client_smoke_bundle.py <private-remote-client-smoke-proof-bundle> --bind-host <private-non-loopback-host>
py -3 tools\winui_safe_copy_online_host_authority_two_client_smoke_check.py <host-authority-two-client-smoke-proof-bundle> --expected-controller-configuration 1
```

The checker accepted `transport=host-authority-two-client-tcp-jsonl-smoke`, `bindHost=<private-non-loopback-host>`, process model `two-separate-python-client-processes`, `clientProcessIdsDistinctFromBuilder=true`, `clientProcessIdsDistinctFromEachOther=true`, `credentialTransportToClientProcesses=stdin-ephemeral-not-serialized-to-artifact`, `authorization.scheme=HMAC-SHA256`, `credentialStorage=ephemeral-not-serialized`, `serverIdentityMode=pinned-fingerprint`, `clientIdentityMode=pinned-slot-fingerprint`, `replayCacheEnabled=true`, `sequenceEnforced=true`, accepted commands `host-authority-p2-forward-0001` and `host-authority-p1-forward-0001`, deterministic schedule order `P1,P2`, relay plan hash `fbb60fd900e377251059d00553835e088e73b05278314d42aaf5f28bbb3bf376`, and a `22`-message / `26`-event transcript. This proves same-workstation two-client command-source scheduling into a deterministic host relay plan only. It does not prove multi-host LAN play, public matchmaking, public relay/server behavior, native BEA netcode, NAT traversal, deterministic simulation sync, rollback, anti-cheat, physical gamepad behavior, rebuild parity, or no-noticeable-difference online parity.

## Seventh Proof Slice Completed

The seventh online-shaped proof is same-workstation host-authority runtime delivery into one copied BEA host-helper run:

1. Read the accepted host-authority two-client scheduler proof.
2. Revalidate the deterministic relay plan hash `fbb60fd900e377251059d00553835e088e73b05278314d42aaf5f28bbb3bf376`.
3. Launch a fresh copied `BEA.exe` from the clean specimen backup with `-skipfmv -level 850 -configuration 1`.
4. Materialize copied `defaultoptions.bea` so Movement/Forward maps P1 to `Q` and P2 to `E`.
5. Attach exact-PID CDB with `tools/runtime-probes/local-multiplayer-level850-input-state-delta-observer.cdb.txt`.
6. Deliver the scheduled P1 command as `down:Q,wait:500,up:Q` and the scheduled P2 command as `down:E,wait:500,up:E` through the host-helper runtime path.
7. Preserve separate truth fields: `gameInputSentByScheduler=false`, `hostHelperInputSent=true`, `deliveredOriginalBinaryCommandCount=2`, and `nPlayerOriginalBinaryRuntimeProof=0`.
8. Keep the public-safe N-slot schema attached but unchanged: `slotCapacity=4`, `acceptedSessionParticipantCount=4`, `P3/P4 metadata-only`, and P3/P4 gameplay commands rejected with `required-for-unproven-original-binary-slots`.

Accepted result:

```powershell
py -3 tools\build_winui_original_binary_host_authority_runtime_delivery_bundle.py <host-authority-two-client-smoke-proof-bundle> <private-live-runtime-artifact> --output <host-authority-runtime-delivery-proof-bundle>
py -3 tools\winui_safe_copy_online_host_authority_runtime_delivery_check.py <host-authority-runtime-delivery-proof-bundle>
```

The checker accepted schema `winui-original-binary-host-authority-runtime-delivery.v1`, helper version `host-authority-runtime-delivery-helper.v1`, protocol `host-authority-runtime-delivery.v1`, delivery path `host-authority-deterministic-p1-p2-relay-plan-to-safe-copy-host-helper`, commands `host-authority-p1-forward-0001` and `host-authority-p2-forward-0001`, `visualCaptureCount=7`, and copied-runtime evidence with P1 `inputDevice0` rows (`button31ReceiveRows=10`, `forwardStateStoreRows=10`) plus P2 `inputDevice1` rows (`button31ReceiveRows=8`, `forwardStateStoreRows=7`). It also revalidated N-slot relay plan hash `ad62052bde6b6a1108f0e599d58fb89d9b8107d3667b1adca2a18b417a389002` while preserving `nPlayerOriginalBinaryRuntimeProof=0`.

This proves one same-workstation scheduler-to-host-helper delivery path for the two original-binary gameplay slots only. It does not prove more-than-two original-binary players, P3/P4 active gameplay, co-op/versus mode semantics, multi-host LAN play, public matchmaking, public relay/server behavior, native BEA netcode, NAT traversal, deterministic simulation sync, rollback, anti-cheat, physical gamepad behavior, rebuild parity, or no-noticeable-difference online parity.

## Eighth Proof Slice Completed

The eighth online-shaped proof repeats the host-authority runtime-delivery path across a second copied BEA host-helper run:

1. Reuse the same accepted host-authority two-client scheduler proof and deterministic relay plan hash `fbb60fd900e377251059d00553835e088e73b05278314d42aaf5f28bbb3bf376`.
2. Launch a second fresh copied `BEA.exe` from the clean specimen backup with `-skipfmv -level 850 -configuration 1`.
3. Validate both runtime-delivery bundles with `tools/winui_safe_copy_online_host_authority_runtime_delivery_replayability_check.py`.
4. Require distinct live runtime artifact hashes, process IDs, CDB log paths, and runtime player/controller/BattleEngine/Walker tuples.
5. Preserve per-proof truth fields: `gameInputSentByScheduler=false`, `hostHelperInputSent=true`, `deliveredOriginalBinaryCommandCount=2`, and `nPlayerOriginalBinaryRuntimeProof=0`.

Accepted replayability result:

The replayability checker was run locally against two private, release-excluded proof bundles. Public docs intentionally omit raw `subagents` artifact paths, copied-game roots, CDB logs, screenshots, and process identifiers.

The replayability checker accepted two distinct copied-runtime proof bundles with `visualCaptureCount=7` in each, `deliveredOriginalBinaryCommandCount=2` per proof, runtime players P1/P2 `04815090`/`0482c890` in the first artifact, runtime players P1/P2 `047fb090`/`04812890` in the second artifact, the same host relay plan hash, the same N-slot relay hash, and the role invariant P1 -> Q -> `inputDevice0`, P2 -> E -> `inputDevice1`.

This proves the same P1/P2 host-authority scheduler relay plan can be delivered through the safe-copy host-helper input path across two distinct copied original-BEA level-850/config-1 runtime artifacts. It does not prove more-than-two original-binary players, P3/P4 active gameplay, co-op/versus mode semantics, multi-host LAN play, public matchmaking, public relay/server behavior, native BEA netcode, NAT traversal, deterministic simulation sync, rollback, anti-cheat, physical gamepad behavior, improved control feel, rebuild parity, or no-noticeable-difference online parity.

## Ninth Proof Slice Completed

The ninth online-shaped proof hardens executor provenance for the scheduler-to-host-helper path:

1. Read the accepted host-authority two-client scheduler proof and revalidate relay plan hash `fbb60fd900e377251059d00553835e088e73b05278314d42aaf5f28bbb3bf376`.
2. Derive the live harness input sequence from `hostAuthorityScheduler.relayPlan`: `wait:300`, `down:Q,wait:500,up:Q`, `wait:300`, `down:E,wait:500,up:E`.
3. Launch one fresh copied level-850/config-1 `BEA.exe` from the clean specimen backup through a hardened subprocess executor with an allowlisted child environment.
4. Build and validate a runtime-delivery proof bundle from the newly created live runtime artifact.
5. Record `live-executor-subprocess`, `childEnvSensitiveKeyCount=0`, `executorRecordsFreshSameRootArtifacts=true`, clean override hash `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, `visualCaptureCount=7`, `deliveredOriginalBinaryCommandCount=2`, `hostHelperInputSent=true`, and `nPlayerOriginalBinaryRuntimeProof=0`.

Accepted executor result:

```powershell
py -3 tools\winui_safe_copy_online_host_authority_runtime_executor_check.py <private-executor-proof>
```

The executor checker accepted a fresh same-root proof with runtime players P1/P2 `<runtime-p1-pointer-redacted>`/`<runtime-p2-pointer-redacted>`, P1 and P2 `button31ReceiveRows=11`, P1 and P2 `forwardStateStoreRows=11`, runtime-delivery bundle hash `a79618c7ccdd8312c2da2af125f939451e62a8d3f1377b94c94cee84080400c3`, and no BEA/CDB process left running.

This proves the accepted scheduler relay plan can directly drive one live safe-copy host-helper runtime-delivery run through a bounded executor. It does not prove multi-host LAN play, public matchmaking, native BEA netcode, more-than-two original-binary players, co-op/versus runtime semantics, deterministic simulation sync, rollback, anti-cheat, physical gamepad behavior, rebuild parity, or no-noticeable-difference online parity.

## Tenth Proof Slice Completed

The tenth online-shaped proof is a public-safe original-binary online slot-ceiling guard:

1. Keep the online/session architecture scalable with `slotCapacity=4`, `acceptedSessionParticipantCount=4`, `minimumArchitectureAcceptanceSlots=4`, and `mustNotHardcodeExactlyTwoPlayers=true`.
2. Keep the current original-binary runtime proof ceiling explicit: `maxOriginalBinaryActiveSlotsProven=2`, `activeOriginalBinarySlotsProven=P1,P2`, `retailViewpointsProven=2`, and `nPlayerOriginalBinaryRuntimeProof=0`.
3. Keep `P3/P4 metadata-only` with runtime route `unsupported-original-binary-active-slot`; gameplay commands for those slots remain rejected with `required-for-unproven-original-binary-slots`.
4. Preserve future possibility without overclaiming: `beyondTwoPlayersRequiresNewProofClass=true`, `absenceOfCurrentProofIsNotProofOfPermanentAbsence=true`, and `permanentImpossibilityClaim=false`.

This guard does not add a BEA launch, CDB attach, network transport, patch row, or runtime proof. It prevents the existing P4-capable session schema from being mistaken for active P3/P4 original-binary gameplay, while also preventing the current P1/P2 proof ceiling from being framed as a permanent impossibility claim.

## Eleventh Proof Slice Completed

The eleventh online-shaped proof is a host-authority runtime movement-state bridge over the accepted executor artifact:

1. Revalidate the accepted executor proof and its relay plan hash `fbb60fd900e377251059d00553835e088e73b05278314d42aaf5f28bbb3bf376`.
2. Revalidate the live runtime artifact referenced by that executor proof.
3. Apply the stricter movement-state delta checker to the same copied level-850/config-1 runtime artifact with expected proof lever `input-isolation-forward-qe`.
4. Keep visible movement causality separate because the strict visible movement-delta checker rejected this artifact.

Accepted result:

```powershell
py -3 tools\winui_safe_copy_online_host_authority_runtime_movement_bridge_check.py <private-executor-proof>
```

The checker accepted Q/P0 `inputDevice0`, E/P1 `inputDevice1`, P1/P2 runtime players `<runtime-p1-pointer-redacted>`/`<runtime-p2-pointer-redacted>`, P1 and P2 `button31ReceiveRows=11`, P1 and P2 `forwardStateStoreRows=11`, Q/P0 render samples `181` baseline / `213` target, E/P1 render samples `104` baseline / `183` target, `targetPositionChanged=true`, `targetVelocityChanged=true`, and `targetDiffersFromAdjacentBaseline=true` for both routes. It also keeps `deliveredOriginalBinaryCommandCount=2`, `gameInputSentByScheduler=false`, `hostHelperInputSent=true`, `nPlayerOriginalBinaryRuntimeProof=0`, and `visibleMovementDeltaClaim=false`.

This proves the relay-plan-derived executor chain reaches matching exact-PID movement-state deltas in one copied BEA host. It does not prove visible movement causality, improved control feel, physical gamepad behavior, multi-host LAN play, public matchmaking, native BEA netcode, active P3/P4 gameplay, deterministic sync, rollback, anti-cheat, rebuild parity, or no-noticeable-difference online parity.

## Twelfth Proof Slice Completed

The twelfth online-shaped proof is a same-workstation sequential four-client N-slot process smoke:

1. Start one private-interface host-authority TCP JSONL process smoke with schema `winui-original-binary-host-authority-n-slot-process-smoke.v1`.
2. Spawn four separate Python client processes with `credentialTransportToClientProcesses=stdin-ephemeral-not-serialized-to-artifact`, `processConcurrencyModel=sequential-distinct-client-processes`, and `simultaneousClientProcessesProven=1`.
3. Admit P1/P2/P3/P4 as session participants while preserving `slotCapacity=4` and `acceptedSessionParticipantCount=4`.
4. Use non-sorted arrival order `P4,P2,P3,P1`, then schedule deterministic participant order `P1,P2,P3,P4` and deterministic original-binary relay order `P1,P2`.
5. Accept only P1/P2 original-binary gameplay commands and reject P3/P4 gameplay commands with `required-for-unproven-original-binary-slots`.
6. Preserve `gameInputSentByNSlotScheduler=false`, `hostHelperInputSent=false`, `newBeaLaunchCount=0`, `cdbAttachCount=0`, `nPlayerOriginalBinaryRuntimeProof=0`, `activeP3P4OriginalBinaryGameplayProof=false`, and `permanentImpossibilityClaim=false`.

Accepted result:

```text
clientProcessCount=4
clientProcessIdsDistinctFromBuilder=true
clientProcessIdsDistinctFromEachOther=true
acceptedOriginalBinaryGameplayCommandCount=2
rejectedOriginalBinaryGameplayCommandCount=2
acceptedOriginalBinaryGameplaySlots=P1,P2
metadataOnlySlots=P3,P4
rejectedGameplayRouteSlots=P3,P4
relayPlanSha256=ad62052bde6b6a1108f0e599d58fb89d9b8107d3667b1adca2a18b417a389002
runtimeCompatibleP1P2RelayHash=fbb60fd900e377251059d00553835e088e73b05278314d42aaf5f28bbb3bf376
```

This proves four separate slot-scoped client processes can participate in the host-authority scheduler/process layer while only P1/P2 enter the original-binary relay plan. It does not prove active P3/P4 original-binary gameplay, co-op/versus runtime semantics, multi-host LAN play, public matchmaking, native BEA netcode, deterministic sync, rollback, anti-cheat, physical gamepad behavior, rebuild parity, or no-noticeable-difference online parity.

## Thirteenth Proof Slice Completed

The thirteenth online-shaped proof is a same-workstation-client/private-interface concurrent/barrier four-client N-slot process smoke:

1. Start one private-interface host-authority TCP JSONL process smoke with schema `winui-original-binary-host-authority-n-slot-concurrent-process-smoke.v1`.
2. Spawn four separate Python client processes with `credentialTransportToClientProcesses=stdin-ephemeral-not-serialized-to-artifact`.
3. Hold all four child processes at a parent-observed ready barrier before release.
4. Release all four clients, observe four overlapping private-interface socket connections, then hold those sockets until a close barrier.
5. Preserve P1/P2 as the only original-binary relay slots; keep P3/P4 metadata-only and reject their gameplay commands with `required-for-unproven-original-binary-slots`.
6. Preserve `privateLanReachableDuringRun=true`, `foreignPeersRejectedAfterAccept=true`, `sameWorkstationClientProcessesOnly=true`, `sameWorkstationNetworkOnly=false`, and `securityProofScope=minimal-smoke-hmac-envelope-not-full-session-security-proof`.
7. Preserve `gameInputSentByNSlotScheduler=false`, `hostHelperInputSent=false`, `newBeaLaunchCount=0`, `cdbAttachCount=0`, `nPlayerOriginalBinaryRuntimeProof=0`, `activeP3P4OriginalBinaryGameplayProof=false`, and `permanentImpossibilityClaim=false`.

Accepted result:

The N-slot concurrent process-smoke checker was run locally against a private, release-excluded proof bundle. Public docs intentionally omit raw `subagents` artifact paths, copied-game roots, CDB logs, screenshots, and process identifiers.

The checker accepted `transport=host-authority-n-slot-tcp-jsonl-concurrent-process-smoke`, process model `four-separate-python-client-processes`, `processConcurrencyModel=barrier-concurrent-client-processes`, `simultaneousClientProcessesProven=4`, `clientReadyBeforeBarrierReleaseCount=4`, `barrierReleaseAfterAllClientsReady=true`, `maxSimultaneousSocketConnectionsProven=4`, `privateLanReachableDuringRun=true`, `foreignPeersRejectedAfterAccept=true`, `sameWorkstationClientProcessesOnly=true`, `sameWorkstationNetworkOnly=false`, `securityProofScope=minimal-smoke-hmac-envelope-not-full-session-security-proof`, `clientProcessIdsDistinctFromBuilder=true`, `clientProcessIdsDistinctFromEachOther=true`, `clientEnvSensitiveKeyCount=0`, `arrivalOrder=P4,P2,P3,P1`, deterministic original-binary relay order `P1,P2`, accepted P1/P2 command count `2`, rejected P3/P4 command count `2`, relay plan hash `ad62052bde6b6a1108f0e599d58fb89d9b8107d3667b1adca2a18b417a389002`, and runtime-compatible P1/P2 relay hash `fbb60fd900e377251059d00553835e088e73b05278314d42aaf5f28bbb3bf376`.

This proves four concurrent slot-scoped client processes and four overlapping private-interface socket connections in the host-authority process layer while only P1/P2 enter the original-binary relay plan. The listener is private-LAN reachable during the run and rejects foreign peers after accept, but the HMAC layer is only a minimal smoke envelope. It does not prove active P3/P4 original-binary gameplay, more than two original-binary runtime players, co-op/versus runtime semantics, multi-host LAN play, public matchmaking, native BEA netcode, full session-security proof, deterministic sync, rollback, anti-cheat, physical gamepad behavior, rebuild parity, or no-noticeable-difference online parity.

## Fourteenth Proof Slice Completed

The fourteenth online-shaped proof is a fresh N-slot concurrent relay-derived copied-runtime bridge:

1. Revalidate the accepted concurrent four-client N-slot process proof and its runtime-compatible P1/P2 relay hash `fbb60fd900e377251059d00553835e088e73b05278314d42aaf5f28bbb3bf376`.
2. Derive the live input sequence `wait:300`, `down:Q,wait:500,up:Q`, `wait:300`, and `down:E,wait:500,up:E` from the N-slot relay plan.
3. Launch one fresh copied level-850/config-1 `BEA.exe` from the clean specimen backup through the safe-copy live harness.
4. Attach exact-PID CDB movement-state observation and require Q/P1 plus E/P2 movement-state deltas.
5. Preserve `P3/P4 metadata-only`, `gameInputSentByNSlotScheduler=false`, and `nPlayerOriginalBinaryRuntimeProof=0`.

Accepted result:

The N-slot runtime bridge checker was run locally against a private, release-excluded proof bundle. Public docs intentionally omit raw `subagents` artifact paths, copied-game roots, CDB logs, screenshots, and process identifiers.

The checker accepted schema `winui-original-binary-host-authority-n-slot-runtime-bridge.v1`, protocol `host-authority-n-slot-runtime-bridge.v1`, proof hash `ee9aee859c40db44978664cfa11d1a668ec4fb9bade08a18ddfadcaa7847221f`, live runtime artifact hash `7b6118b783e82d13f20ed9e09fc593b920793e90f09a48ffc698750e56c940ae`, `slotCapacity=4`, `acceptedSessionParticipantCount=4`, `processConcurrencyModel=barrier-concurrent-client-processes`, `simultaneousClientProcessesProven=4`, `maxSimultaneousSocketConnectionsProven=4`, runtime players P1/P2 `<runtime-p1-pointer-redacted>`/`<runtime-p2-pointer-redacted>`, Q/P1 `button31ReceiveRows=12` and `forwardStateStoreRows=12`, E/P2 `button31ReceiveRows=11` and `forwardStateStoreRows=11`, `visualCaptureCount=7`, `hostHelperInputSent=true`, `gameInputSentByNSlotScheduler=false`, `P3/P4 metadata-only`, and `nPlayerOriginalBinaryRuntimeProof=0`.

This proves the accepted concurrent N-slot process proof can feed one fresh copied-runtime P1/P2 host-helper state observation. It does not prove active P3/P4 original-binary gameplay, more-than-two original-binary runtime players, multi-host LAN play, public matchmaking, native BEA netcode, full session-security proof, deterministic sync, rollback, anti-cheat, physical gamepad behavior, rebuild parity, or no-noticeable-difference online parity.

## Fifteenth Proof Slice Completed

The fifteenth online-shaped proof is a host-authority state-authority observer over the accepted N-slot runtime bridge:

1. Revalidate the accepted N-slot concurrent relay-derived runtime bridge proof and its copied level-850/config-1 runtime artifact.
2. Verify the host-side render state remains `players=2`, `level=850`, and `horizSplit=1`.
3. Verify P1/Q and P2/E route authority through distinct controller, player, BattleEngine, and WalkerPart identities.
4. Verify Q/P1 and E/P2 reach `walker-forward` state-store rows with clean wait windows.
5. Preserve `P3/P4 metadata-only`, `gameInputSentByNSlotScheduler=false`, `hostHelperInputSent=true`, and `nPlayerOriginalBinaryRuntimeProof=0`.

Accepted result:

```powershell
py -3 tools\winui_safe_copy_online_host_authority_state_authority_observer_check.py <private-proof-json>
```

The checker accepted schema `winui-original-binary-host-authority-state-authority-observer.v1`, protocol `host-authority-state-authority-observer.v1`, proof hash `ac1cd32281e354b5ae37a0aa8c17b1ab883bc9dd863c2ae5e2ffe7bde62c0416`, source N-slot runtime bridge proof hash `ee9aee859c40db44978664cfa11d1a668ec4fb9bade08a18ddfadcaa7847221f`, live runtime artifact hash `7b6118b783e82d13f20ed9e09fc593b920793e90f09a48ffc698750e56c940ae`, N-slot concurrent process proof hash `7458bbafcca8fbb60f0b7750fac068b7a6dcdfe59b13980f54da081832f95896`, `hostAuthorityScope=single-copied-host-exact-pid-state-graph`, `distinctPlayers=true`, `distinctBattleEngines=true`, `distinctWalkers=true`, `distinctControllers=true`, `waitWindowsClean=true`, Q/P1 `button31ReceiveRows=12` and `forwardStateStoreRows=12`, E/P2 `button31ReceiveRows=11` and `forwardStateStoreRows=11`, `visualCaptureCount=7`, `hostHelperInputSent=true`, `gameInputSentByNSlotScheduler=false`, `P3/P4 metadata-only`, and `nPlayerOriginalBinaryRuntimeProof=0`.

This proves the accepted N-slot concurrent relay plan drove one copied host whose exact-PID CDB rows form a consistent P1/P2 host-owned state graph. It does not prove active P3/P4 original-binary gameplay, more-than-two original-binary runtime players, multi-host LAN play, public matchmaking, native BEA netcode, full session-security proof, deterministic sync, rollback, anti-cheat, physical gamepad behavior, rebuild parity, or no-noticeable-difference online parity.

## Sixteenth Proof Slice Completed

The sixteenth online-shaped proof is host-authority state-authority replayability over two accepted observer proofs:

1. Revalidate two state-authority observer proofs with schema `winui-original-binary-host-authority-state-authority-observer.v1`.
2. Require the same N-slot concurrent process proof hash `7458bbafcca8fbb60f0b7750fac068b7a6dcdfe59b13980f54da081832f95896`.
3. Require the same runtime-compatible P1/P2 relay hash `fbb60fd900e377251059d00553835e088e73b05278314d42aaf5f28bbb3bf376`.
4. Require distinct observer proof hashes, source bridge proof hashes, live runtime artifact hashes, process ids, CDB logs, and runtime player/controller/BattleEngine/Walker tuples.
5. Preserve P1/Q/inputDevice0 and P2/E/inputDevice1 route authority, clean wait windows, `P3/P4 metadata-only`, `gameInputSentByNSlotScheduler=false`, and `nPlayerOriginalBinaryRuntimeProof=0`.

Accepted result:

```powershell
py -3 tools\winui_safe_copy_online_host_authority_state_authority_replayability_check.py <private-observer-proof-a> <private-observer-proof-b>
```

The checker accepted schema `winui-original-binary-host-authority-state-authority-replayability.v1`, protocol `host-authority-state-authority-replayability.v1`, replayability summary hash `a66e66dee6ff06bfab3a1cae234b86958bc8537712206d4db6605c898543ef7a`, observer proof hashes `ac1cd32281e354b5ae37a0aa8c17b1ab883bc9dd863c2ae5e2ffe7bde62c0416` and `e57516d1b306d0a8a37aa1be2103235f066d1d4e06d4b648a9b0c140dfafc017`, source bridge proof hashes `ee9aee859c40db44978664cfa11d1a668ec4fb9bade08a18ddfadcaa7847221f` and `6e6a8d68d1c4dea875b93e9dc74b63a6aeabc05b350a4e683bc17f0881176ba8`, live runtime artifact hashes `7b6118b783e82d13f20ed9e09fc593b920793e90f09a48ffc698750e56c940ae` and `f87e0e6b622e504733082a9b8aafb4ba8d4e254e7a93471b0eacb87d263f32a8`, `hostAuthorityScope=single-copied-host-exact-pid-state-graph`, `stateAuthorityGraphProven=true`, `stateAuthorityReplayabilityProven=true`, `distinctProcessIds=true`, `distinctCdbLogs=true`, `distinctRuntimePointerTuples=true`, `waitWindowsClean=true`, `hostHelperInputSent=true`, `gameInputSentByNSlotScheduler=false`, `activeP3P4OriginalBinaryGameplayProof=false`, and `nPlayerOriginalBinaryRuntimeProof=0`.

This proves replayability of the same-workstation single-copied-host exact-PID P1/P2 state-authority graph across distinct copied BEA level-850/config-1 runtime artifacts. It does not prove active P3/P4 original-binary gameplay, more-than-two original-binary runtime players, co-op/versus online semantics, multi-host LAN play, public matchmaking, native BEA netcode, full session-security proof, deterministic sync, rollback, anti-cheat, physical gamepad behavior, visible movement causality, rebuild parity, or no-noticeable-difference online parity.

## Seventeenth Proof Slice Completed

The seventeenth online-shaped proof is a same-workstation N-slot session-security message smoke over the host-authority protocol layer:

1. Build schema `winui-original-binary-host-authority-n-slot-session-security-smoke.v1` for protocol `host-authority-n-slot-input.v1`.
2. Use an in-memory same-workstation message harness; no BEA launch, no CDB attach, no host-helper input, and no public sockets.
3. Accept authenticated P1/P2 original-binary gameplay command envelopes only.
4. Reject P3/P4 gameplay commands as metadata-only with `required-for-unproven-original-binary-slots`.
5. Reject `25` security/admission cases including unknown fields, raw JSON line oversize, stale/future ticks, nonce replay, missing/wrong relay-plan hash, bad MAC, bad slot credentials, slot identity mismatch, slot change on connection, command before session, duplicate session, non-next sequence, slot/tick rate limits, missing/wrong typed fields, public-matchmaking/direct-input claims, server identity mismatch, unknown slot, invalid team assignment, and duplicate slot/client identity.
6. Record exact proof flags: `securityProofScope=same-workstation-session-security-smoke-not-online-gameplay-proof`, `sessionScopedMacCoverageProof=true`, `sessionScopedMacCoverageMode=canonical-json-message-excluding-mac`, `sessionScopedMacFieldSensitivityProof=true`, `tickBoundMacFieldsProof=true`, `relayPlanHashMacBound=true`, `maxJsonLineBytesEnforced=true`, `rawJsonLineByteLimitRejected=true`, `unknownFieldRejectionProof=true`, `strictMessageSchemaProof=true`, `rejectedSecurityCaseCount=25`, and `activeP3P4OriginalBinaryGameplayProof=false`.

Accepted result:

```powershell
py -3 tools\winui_safe_copy_online_host_authority_n_slot_session_security_smoke_check.py <private-proof-json>
```

The checker accepted the release-excluded proof bundle hash `4976d01e2bc6f0c4f7f7af58c0c6a9d68e7401c6319b0bbc9eb6b2c358d9c6be`, relay plan hash `ad62052bde6b6a1108f0e599d58fb89d9b8107d3667b1adca2a18b417a389002`, `acceptedOriginalBinaryGameplayCommandCount=2`, `metadataGameplayRejectionCount=2`, `rejectedSecurityCaseCount=25`, `tickBoundMacFieldsProof=true`, `relayPlanHashMacBound=true`, `newBeaLaunchCount=0`, `cdbAttachCount=0`, `nPlayerOriginalBinaryRuntimeProof=0`, and `activeP3P4OriginalBinaryGameplayProof=false`.

This proves message-layer/session-security behavior for the same-workstation host-authority protocol harness only. It does not prove active P3/P4 original-binary gameplay, more-than-two original-binary runtime players, co-op/versus online semantics, multi-host LAN play, public matchmaking, native BEA netcode, deterministic sync, rollback, anti-cheat, physical gamepad behavior, rebuild parity, or no-noticeable-difference online parity.

## Eighteenth Proof Slice Completed

The eighteenth online-shaped proof is a public-safe provenance wrapper that links the accepted N-slot session-security message smoke to the accepted copied-runtime P1/P2 bridge:

1. Validate schema `winui-original-binary-host-authority-secure-n-slot-runtime-bridge.v1` for protocol `host-authority-secure-n-slot-runtime-bridge.v1`.
2. Require the accepted secure session proof to carry `acceptedOriginalBinaryGameplaySlots=P1,P2`, `metadataOnlySlots=P3,P4`, `sessionScopedMacCoverageProof=true`, `tickBoundMacFieldsProof=true`, `relayPlanHashMacBound=true`, `strictMessageSchemaProof=true`, and `rejectedSecurityCaseCount=25`.
3. Require the secure accepted relay path to match the copied-runtime bridge through `runtimeCompatibleP1P2RelayHashMatched=true` and relay hash `fbb60fd900e377251059d00553835e088e73b05278314d42aaf5f28bbb3bf376`.
4. Require the copied-runtime bridge source to retain `hostHelperInputSent=true`, delivered P1/P2 command count `2`, visual capture count `7`, and `nPlayerOriginalBinaryRuntimeProof=0`.
5. Record wrapper-only counters `wrapperNewBeaLaunchCount=0` and `wrapperCdbAttachCount=0`.

Accepted result:

```powershell
py -3 tools\winui_safe_copy_online_host_authority_secure_n_slot_runtime_bridge_check.py <private-proof-json>
```

The checker accepted public-safe proof hash `bce12fdbb4c34892d04764edcf288bef600608881e764b600478a7e8f8aebbd1`, `secureSessionAcceptedRelayFeedsRuntimeBridge=true`, `runtimeCompatibleP1P2RelayHashMatched=true`, `acceptedOriginalBinaryGameplaySlots=P1,P2`, `metadataOnlySlots=P3,P4`, `rejectedGameplayRouteSlots=P3,P4`, `secureSessionAcceptedCommandCount=2`, `secureSessionMetadataRejectionCount=2`, `secureSessionSecurityRejectionCount=25`, `sourceRuntimeBridgeDeliveredCommandCount=2`, `sourceRuntimeBridgeVisualCaptureCount=7`, `wrapperNewBeaLaunchCount=0`, `wrapperCdbAttachCount=0`, `activeP3P4OriginalBinaryGameplayProof=false`, and `nPlayerOriginalBinaryRuntimeProof=0`.

This proves the accepted secure N-slot relay contract and the accepted copied-runtime P1/P2 bridge share the same bounded P1/P2 relay hash. It does not prove a new BEA launch, a new CDB attach, multi-host LAN play, public matchmaking, native BEA netcode, active P3/P4 original-binary gameplay, more than two original-binary runtime players, co-op/versus online semantics, deterministic sync, rollback, anti-cheat, production-grade server identity, rebuild parity, or no-noticeable-difference online parity.

## Nineteenth Proof Slice Completed

The nineteenth online-shaped proof is a secure N-slot runtime executor that turns the previous provenance wrapper into one fresh copied-runtime observation:

1. Validate schema `winui-original-binary-host-authority-secure-n-slot-runtime-executor.v1` for protocol `host-authority-secure-n-slot-runtime-executor.v1`.
2. Require an accepted same-workstation session-security smoke proof with relay plan hash `ad62052bde6b6a1108f0e599d58fb89d9b8107d3667b1adca2a18b417a389002`, `sessionScopedMacCoverageProof=true`, `tickBoundMacFieldsProof=true`, `relayPlanHashMacBound=true`, strict schema rejection, and `rejectedSecurityCaseCount=25`.
3. Derive the runtime input sequence `wait:300`, `down:Q,wait:500,up:Q`, `wait:300`, and `down:E,wait:500,up:E` from the accepted session relay plan.
4. Launch one copied level-850/config-1 BEA host through the safe-copy live harness, attach CDB to the exact managed process, capture seven bounded frames, and stop the managed copied process.
5. Record `newBeaLaunchCount=1`, `cdbAttachCount=1`, `visualCaptureCount=7`, `deliveredOriginalBinaryCommandCount=2`, `hostHelperInputSent=true`, `gameInputSentByNSlotScheduler=false`, `visibleMovementDeltaClaim=false`, `acceptedOriginalBinaryGameplaySlots=P1,P2`, `metadataOnlySlots=P3,P4`, `rejectedGameplayRouteSlots=P3,P4`, and `nPlayerOriginalBinaryRuntimeProof=0`.

Accepted result:

```powershell
py -3 tools\winui_safe_copy_online_host_authority_secure_n_slot_runtime_executor_check.py <private-proof-json>
```

The checker accepted public-safe proof hash `4a2b3814112931a60fb58ebfc424fe4382e19701c0f3a16200f3b4b4806b4df1`, session-security proof hash `3c0d0e15c23fa3644afcd937dc3c53df6d703301ec8ccffc9e665ea4f182711b`, live runtime artifact hash `cdfb399e3a058ad9b0f9080ff446c8887fdfe0b44c3ca52c32bd0497febaae3f`, runtime-compatible relay hash `fbb60fd900e377251059d00553835e088e73b05278314d42aaf5f28bbb3bf376`, `newBeaLaunchCount=1`, `cdbAttachCount=1`, `visualCaptureCount=7`, `secureSessionAcceptedCommandCount=2`, `secureSessionMetadataRejectionCount=2`, `secureSessionSecurityRejectionCount=25`, `deliveredOriginalBinaryCommandCount=2`, `hostHelperInputSent=true`, `gameInputSentByNSlotScheduler=false`, `visibleMovementDeltaClaim=false`, `activeP3P4OriginalBinaryGameplayProof=false`, and `nPlayerOriginalBinaryRuntimeProof=0`.

This proves only a same-workstation secure-session-derived P1/P2 copied-runtime executor path. It does not prove active P3/P4 original-binary gameplay, more-than-two original-binary runtime players, co-op/versus online semantics, multi-host LAN play, public matchmaking, native BEA netcode, deterministic sync, rollback, anti-cheat, physical gamepad behavior, production server identity, rebuild parity, or no-noticeable-difference online parity.

## Twentieth Proof Slice Completed

The twentieth online-shaped proof repeats the secure N-slot runtime executor path across two distinct copied BEA host-helper runs:

1. Revalidate two secure N-slot runtime executor proofs with schema `winui-original-binary-host-authority-secure-n-slot-runtime-executor.v1`.
2. Require the same session-security proof hash `3c0d0e15c23fa3644afcd937dc3c53df6d703301ec8ccffc9e665ea4f182711b`.
3. Require the same session relay plan hash `ad62052bde6b6a1108f0e599d58fb89d9b8107d3667b1adca2a18b417a389002` and runtime-compatible P1/P2 relay hash `fbb60fd900e377251059d00553835e088e73b05278314d42aaf5f28bbb3bf376`.
4. Require distinct secure executor proof hashes, live runtime artifact hashes, process ids, CDB logs, runtime paths, and runtime player tuples.
5. Preserve `acceptedOriginalBinaryGameplaySlots=P1,P2`, `metadataOnlySlots=P3,P4`, `rejectedGameplayRouteSlots=P3,P4`, `deliveredOriginalBinaryCommandCountPerProof=2`, `hostHelperInputSent=true`, `gameInputSentByNSlotScheduler=false`, `newBeaLaunchCountPerProof=1`, `cdbAttachCountPerProof=1`, `visibleMovementDeltaClaim=false`, `activeP3P4OriginalBinaryGameplayProof=false`, and `nPlayerOriginalBinaryRuntimeProof=0`.

The checker accepted public-safe proof hashes `4a2b3814112931a60fb58ebfc424fe4382e19701c0f3a16200f3b4b4806b4df1` and `8ef72707fd57a6c4ad9e65d3f03e1c21dd945e72bfbb3c3c87f5ddfd3c5d1e0d`, live runtime artifact hashes `cdfb399e3a058ad9b0f9080ff446c8887fdfe0b44c3ca52c32bd0497febaae3f` and `8db116a2b68c0100dc7a6bc49e29df9c9167aee2e6d41aa8a356e438bf9cb877`, `secureNSlotRuntimeExecutorReplayabilityProven=true`, `distinctLiveRuntimeArtifactHashes=true`, `distinctRuntimeArtifactPaths=true`, `distinctProcessIds=true`, `distinctCdbLogs=true`, and `distinctRuntimePointerTuples=true`.

This proves only repeated same-workstation secure-session-derived P1/P2 copied-runtime executor artifacts. It does not prove active P3/P4 original-binary gameplay, more-than-two original-binary runtime players, co-op/versus online semantics, multi-host LAN play, public matchmaking, native BEA netcode, deterministic sync, rollback, anti-cheat, physical gamepad behavior, visible movement causality, production server identity, rebuild parity, or no-noticeable-difference online parity.

## Twenty-First Proof Slice Completed

The twenty-first online-shaped proof is a Local session-directory smoke over public-safe copied-host metadata:

1. Build schema `winui-original-binary-online-session-directory-smoke.v1` for protocol `online-session-directory.v1`.
2. Use `same-workstation-local-directory-smoke-not-public-matchmaking`; no public bind, no public server, no BEA launch, no CDB attach, and no game input.
3. Register one copied level-850/config-1 host descriptor, list one compatible session, and issue one redacted P2 join-ticket fingerprint.
4. Reject `14` directory/admission cases, including public matchmaking, public bind, native-netcode, multi-host LAN, P3/P4 gameplay route, unknown-field, oversized-query, secret/path leakage, duplicate session id, and compatibility failures.
5. Record `registeredSessionCount=1`, `compatibleListingCount=1`, `acceptedJoinTicketCount=1`, `rejectedDirectoryCaseCount=14`, `publicMatchmakingProof=false`, `multiHostLanProof=false`, `nativeBeaNetcodeProof=false`, `activeP3P4OriginalBinaryGameplayProof=false`, and `nPlayerOriginalBinaryRuntimeProof=0`.

Accepted result:

```powershell
py -3 tools\winui_safe_copy_online_session_directory_smoke_check.py subagents\winui-original-binary-online\session-directory-smoke-20260619\online-session-directory-smoke-proof.json
```

This proves only local session-discovery metadata and join-ticket shaping for the original-binary online ladder. It does not prove active P3/P4 original-binary gameplay, more-than-two original-binary runtime players, co-op/versus online semantics, multi-host LAN play, public matchmaking, native BEA netcode, deterministic sync, rollback, anti-cheat, physical gamepad behavior, production server identity, rebuild parity, or no-noticeable-difference online parity.

## Twenty-Second Proof Slice Completed

The twenty-second online-shaped proof is a WSL2 same-physical-machine remote-client command-source smoke chained to the accepted private-LAN transport artifact:

1. Build schema `winui-original-binary-wsl-remote-client-smoke.v1` for protocol `wsl2-remote-client-input.v1`.
2. Bind a Windows private-interface listener and launch a WSL2 Linux Python client with sanitized environment and stdin-only ephemeral credential transport.
3. Verify pinned server/client identity and HMAC authorization, reject P3 gameplay routing with `metadata-slot-gameplay-not-allowed`, and accept one P2 command envelope.
4. Record transport `wsl2-remote-client-tcp-jsonl-auth-smoke`, `acceptedCommandId=wsl-remote-client-p2-forward-0001`, forward target `private-lan-p2-forward-0001`, `acceptedOriginalBinaryGameplaySlots=P1,P2`, `metadataOnlySlots=P3,P4`, `rejectedGameplayRouteSlots=P3,P4`, `gameInputSentByWslClient=false`, `hostHelperInputSent=false`, `newBeaLaunchCount=0`, `cdbAttachCount=0`, `nPlayerOriginalBinaryRuntimeProof=0`, and `activeP3P4OriginalBinaryGameplayProof=false`.
5. Preserve `publicMatchmakingProof=false`, `multiHostLanProof=false`, `nativeBeaNetcodeProof=false`, and `secondPhysicalHostProof=false`.

Accepted result:

```powershell
py -3 tools\winui_safe_copy_online_wsl_remote_client_smoke_check.py subagents\winui-original-binary-online\wsl-remote-client-smoke-20260619\wsl-remote-client-smoke-proof.json
```

This proves only a same-physical-machine WSL2 command-source step toward online infrastructure. It does not prove a second physical host, active P3/P4 original-binary gameplay, more-than-two original-binary runtime players, co-op/versus online semantics, multi-host LAN play, public matchmaking, native BEA netcode, deterministic sync, rollback, anti-cheat, physical gamepad behavior, production server identity, rebuild parity, or no-noticeable-difference online parity.

## Twenty-Third Proof Slice Completed

The twenty-third online-shaped proof is a joined-session same-host runtime-authority wrapper over accepted directory, WSL, secure executor, and state-authority evidence:

1. Build schema `winui-original-binary-joined-session-same-host-runtime-authority.v1` for protocol `joined-session-same-host-runtime-authority.v1`.
2. Revalidate the accepted local session-directory proof and WSL2 command-source proof, then bind the accepted P2 join-ticket to the same runtime-compatible P1/P2 relay path used by the secure N-slot executor replayability proof. The WSL smoke remains a same-physical-machine command-source predecessor, not a relay-hash carrier.
3. Link the joined-session metadata to the accepted state-authority replayability evidence: `hostAuthorityModel=single-host-authoritative-copied-session`, `hostAuthorityScope=single-copied-host-exact-pid-state-graph`, `stateAuthorityGraphProven=true`, and `stateAuthorityReplayabilityProven=true`.
4. Preserve `acceptedOriginalBinaryGameplaySlots=P1,P2`, `metadataOnlySlots=P3,P4`, `rejectedGameplayRouteSlots=P3,P4`, `hostHelperInputSentByAcceptedRuntimeAuthority=true`, `gameInputSentByDirectory=false`, `gameInputSentByWslClient=false`, `gameInputSentByNSlotScheduler=false`, `wrapperNewBeaLaunchCount=0`, `wrapperCdbAttachCount=0`, `nPlayerOriginalBinaryRuntimeProof=0`, and `activeP3P4OriginalBinaryGameplayProof=false`.
5. Keep `joinedSessionVisibleMovementCausalityProof=false`; existing config-1 visible movement replayability is referenced as supporting local split-screen evidence, not as same-run joined-session visual causality.

Accepted result:

```powershell
npm run test:winui-original-binary-online-session-directory-smoke
npm run test:winui-original-binary-wsl-remote-client-smoke
py -3 tools\build_winui_original_binary_joined_session_same_host_runtime_authority_bundle.py
py -3 tools\winui_safe_copy_online_joined_session_same_host_runtime_authority_check.py --check
npm run test:winui-original-binary-joined-session-same-host-runtime-authority
```

This proves only a same-host joined-session runtime-authority chain for the currently proven P1/P2 original-binary route. It does not prove a second physical host, active P3/P4 original-binary gameplay, more-than-two original-binary runtime players, co-op/versus online semantics, multi-host LAN play, public matchmaking, native BEA netcode, deterministic sync, rollback, anti-cheat, physical gamepad behavior, joined-session visible movement causality, production server identity, rebuild parity, or no-noticeable-difference online parity.

## Twenty-Fourth Proof Slice Completed

The twenty-fourth online-shaped proof is a fresh joined-session runtime-causality proof over the accepted P2 joined-session route:

1. Validate schema `winui-original-binary-joined-session-runtime-causality.v1` for protocol `joined-session-runtime-causality.v1`.
2. Revalidate the accepted joined-session same-host runtime-authority proof and its P2 ticket/relay chain.
3. Build a fresh N-slot session-security proof, then use the existing secure N-slot runtime executor to launch one copied BEA level-850/config-1 host.
4. Validate the fresh executor proof, live runtime artifact, CDB log hash, relay hash, derived input sequences, and public-safe runtime state summary digest.
5. Preserve `acceptedOriginalBinaryGameplaySlots=P1,P2`, `metadataOnlySlots=P3,P4`, `rejectedGameplayRouteSlots=P3,P4`, `gameInputSentByJoinedSessionClient=false`, `gameInputSentByNSlotScheduler=false`, `baseOnlineMultiplayerReady=false`, `nPlayerOriginalBinaryRuntimeProof=0`, and `activeP3P4OriginalBinaryGameplayProof=false`.

Accepted result:

```powershell
py -3 tools\build_winui_original_binary_joined_session_runtime_causality_bundle.py
py -3 tools\winui_safe_copy_online_joined_session_runtime_causality_check.py --check
npm run test:winui-original-binary-joined-session-runtime-causality
```

This proves only one same-host joined-session causality rung for the currently proven P1/P2 original-binary route. It does not prove base online multiplayer readiness, a second physical host, active P3/P4 original-binary gameplay, more-than-two original-binary runtime players, co-op/versus online semantics, multi-host LAN play, public matchmaking, native BEA netcode, deterministic sync, rollback, anti-cheat, physical gamepad behavior, joined-session visible movement causality, production server identity, rebuild parity, or no-noticeable-difference online parity.

## Twenty-Fifth Proof Slice Completed

The twenty-fifth online-shaped proof is a joined-session control-lifecycle proof around the accepted P1/P2 same-host path. It records `joined-session-control-lifecycle-same-host-not-online-play`, `joined-session-same-host-session-control-not-online-play`, `sessionControlLifecycleProven=true`, `acceptedControlActionCount=11`, `rejectedControlCaseCount=22`, `metadata-reconnect-only-not-runtime-reconnect`, `newBeaLaunchCount=0`, `cdbAttachCount=0`, `gameInputSentBySessionControl=false`, and `baseOnlineMultiplayerReady=false`.

This proves session-control lifecycle metadata only. It does not prove BEA launch/runtime behavior, direct game input, base online multiplayer readiness, second-host LAN, public matchmaking, native BEA netcode, active P3/P4 original-binary gameplay, co-op/versus runtime semantics, deterministic sync, rollback, anti-cheat, rebuild parity, or no-noticeable-difference online parity.

## Twenty-Sixth Proof Slice Completed

The twenty-sixth online-shaped proof is an Original Binary Online Mode Classifier:

1. Validate schema `winui-original-binary-online-mode-classifier.v1` for scope `original-binary-online-mode-classifier`.
2. Classify the current accepted original-binary copied runtime profile as `currentRuntimeModeClassification=unclassified-local-multiplayer`.
3. Preserve `runtime-observed-local-splitscreen-not-co-op-or-versus-proof`, `modeRuntimeProofSlices=0`, and `coOpVersusModeRuntimeProofSlices=0`.
4. Keep planned mode families `cooperative`, `versus-free-for-all`, `team-versus`, and `spectator-admin` as `schema-planned-not-runtime-proven`.
5. Reject runtime mode claims from `sessionType alone`, `modeFamily alone`, `schema-only teamAssignments`, metadata-only spectator/admin rows, `slotCapacity=4`, same-host/WSL/private-interface artifacts, local session-directory smoke, host-authority wrapper scaffolding, or joined-session same-host proofs.

Accepted result:

```powershell
py -3 tools\winui_safe_copy_online_mode_classifier_check_test.py
py -3 tools\winui_safe_copy_online_mode_classifier_check.py --self-test
py -3 tools\winui_safe_copy_online_mode_classifier_check.py --check
npm run test:winui-original-binary-online-mode-classifier
```

This proves only a public-safe classifier and anti-overclaim guard. It does not prove runtime co-op, runtime versus, runtime team-versus, spectator/admin runtime authority, base online multiplayer readiness, second-host LAN, active P3/P4 original-binary gameplay, more-than-two original-binary runtime players, public matchmaking, native BEA netcode, deterministic sync, rollback, anti-cheat, rebuild parity, or no-noticeable-difference online parity.

## Twenty-Seventh Proof Slice Completed

The twenty-seventh online-shaped proof is a level-850 P1/P2 mode-semantics observer:

1. Validate schema `winui-original-binary-level850-mode-semantics-observer.v1` for scope `level850-p1p2-mode-semantics-observer-not-coop-versus-proof`.
2. Launch one copied level-850/config-1 BEA host, attach CDB to the exact managed PID, and record `renderPlayers=2`, `boundedCaptureCount=2`, and `visualCaptureCount=2`.
3. Observe `hookTargetCount=21` across multiplayer gates, objective surfaces, win/loss, death, lives, and respawn paths.
4. Preserve `forcedWinDeathRespawn=false`, `modeRuntimeProofSlicesAdded=0`, `coOpVersusModeRuntimeProofSlicesAdded=0`, `currentRuntimeModeClassification=unclassified-local-multiplayer`, `baseOnlineMultiplayerReady=false`, and `activeP3P4OriginalBinaryGameplayProof=false`.

Accepted result:

```powershell
py -3 tools\build_winui_original_binary_level850_mode_semantics_observer_bundle.py
py -3 tools\winui_safe_copy_online_level850_mode_semantics_observer_check.py --check
npm run test:winui-original-binary-level850-mode-semantics-observer
```

This proves only copied-runtime observer coverage for P1/P2 local split-screen mode-semantics surfaces. It does not prove runtime co-op, runtime versus, team-versus, spectator/admin runtime behavior, base online multiplayer readiness, second-host LAN, active P3/P4 original-binary gameplay, more-than-two original-binary runtime players, public matchmaking, native BEA netcode, deterministic sync, rollback, anti-cheat, rebuild parity, or no-noticeable-difference online parity.

## Twenty-Eighth Proof Slice Completed

The twenty-eighth online-shaped proof is a public-safe multiplayer outcome-semantics matrix:

1. Validate schema `winui-original-binary-multiplayer-outcome-semantics-matrix.v1` for scope `original-binary-p1p2-multiplayer-outcome-semantics-matrix-not-runtime-proof`.
2. Select level `854` from candidate levels `851/854/855/860` as the first P1/P2 copied-runtime outcome observer target.
3. Record `requiredHookTargetCount=10` around `CGame__MPDeclarePlayerWon`, `CGame__MPDeclareGameDrawn`, `CGame__DeclarePlayerDead`, `CGame__RespawnPlayer`, `CGame__GetPlayerLives`, `CGame__DeclareLevelWon`, `CGame__DeclareLevelLost`, and script outcome thunks.
4. Preserve `runtimeProofCreatedByThisMatrix=false`, `newBeaLaunchCount=0`, `cdbAttachCount=0`, `modeRuntimeProofSlicesAdded=0`, `coOpVersusModeRuntimeProofSlicesAdded=0`, `baseOnlineMultiplayerReady=false`, `nPlayerOriginalBinaryRuntimeProof=0`, and `activeP3P4OriginalBinaryGameplayProof=false`.

Accepted result:

```powershell
py -3 tools\winui_safe_copy_online_multiplayer_outcome_semantics_matrix_check.py --check
npm run test:winui-original-binary-multiplayer-outcome-semantics-matrix
```

This proves only static candidate selection and hook-surface planning for a later runtime observer. It does not prove runtime outcome behavior, co-op/versus semantics, base online multiplayer readiness, second-host LAN, active P3/P4 original-binary gameplay, more-than-two original-binary runtime players, public matchmaking, native BEA netcode, deterministic sync, rollback, anti-cheat, rebuild parity, or no-noticeable-difference online parity.

## Twenty-Ninth Proof Slice Completed

The twenty-ninth online-shaped proof is a level-854 P1/P2 passive outcome-semantics observer:

1. Validate schema `winui-original-binary-level854-outcome-semantics-observer.v1` for scope `level854-p1p2-outcome-semantics-observer-not-coop-versus-proof`.
2. Launch one copied level-854/config-1 BEA host, attach CDB to the exact managed PID, and record `renderPlayers=2`, `renderLevel=854`, `boundedCaptureCount=2`, and `visualCaptureCount=2`.
3. Observe `outcomeHookTargetCount=10` inside the broader `hookTargetCount=21` surface, without forcing win/death/respawn paths.
4. Preserve `outcomeTransitionHitCount=0`, `naturalOutcomeTransitionObserved=false`, `runtimeOutcomeProof=false`, `forcedOutcomeTransition=false`, `forcedWinDeathRespawn=false`, `modeRuntimeProofSlicesAdded=0`, `coOpVersusModeRuntimeProofSlicesAdded=0`, `currentRuntimeModeClassification=unclassified-local-multiplayer`, `baseOnlineMultiplayerReady=false`, and `activeP3P4OriginalBinaryGameplayProof=false`.

Accepted result:

```powershell
py -3 tools\build_winui_original_binary_level854_outcome_semantics_observer_bundle.py
py -3 tools\winui_safe_copy_online_level854_outcome_semantics_observer_check.py --check
npm run test:winui-original-binary-level854-outcome-semantics-observer
```

This proves only passive copied-runtime observer coverage for level-854 P1/P2 outcome surfaces. It does not prove a natural death/respawn/win/loss transition, runtime outcome causality, co-op/versus semantics, base online multiplayer readiness, second-host LAN, active P3/P4 original-binary gameplay, more-than-two original-binary runtime players, public matchmaking, native BEA netcode, deterministic sync, rollback, anti-cheat, rebuild parity, or no-noticeable-difference online parity.

## Thirtieth Proof Slice Completed

The thirtieth online-shaped proof is a level-854 P1/P2 input-assisted outcome attempt:

1. Validate schema `winui-original-binary-level854-input-assisted-outcome.v1` for scope `level854-input-assisted-outcome-transition-attempt-not-online-proof`.
2. Launch one copied level-854/config-1 BEA host, attach CDB to the exact managed PID, and record `renderPlayers=2`, `renderLevel=854`, `boundedCaptureCount=10`, and `visualCaptureCount=10`.
3. Send eight bounded input windows: four wait/no-input controls and four stimulus windows (`Q`, `E`, and two clicks).
4. Record `inputAssistHitCount=124`, `inputWindowOutcomeTransitionHitCount=0`, `waitWindowOutcomeTransitionHitCount=0`, `positiveStimulusWindowCount=0`, `runtimeOutcomeProof=false`, and `stimulusAttemptOnly=true`.
5. Preserve `baseOnlineMultiplayerReady=false`, `nativeBeaNetcodeProof=false`, `publicMatchmakingProof=false`, `nPlayerOriginalBinaryRuntimeProof=0`, and `activeP3P4OriginalBinaryGameplayProof=false`.

Accepted result:

```powershell
py -3 tools\build_winui_original_binary_level854_input_assisted_outcome_bundle.py
py -3 tools\winui_safe_copy_online_level854_input_assisted_outcome_check.py --check
npm run test:winui-original-binary-level854-input-assisted-outcome
```

This proves scoped input reached the runtime input hooks while the level-854 outcome observer was armed. Positive outcome promotion requires an outcome-transition hit inside a stimulus window with same-window input-assist hits; wait-window or ambient transitions are rejected. This does not prove any natural death/respawn/win/loss transition, co-op/versus runtime semantics, base online multiplayer readiness, second-host LAN, active P3/P4 original-binary gameplay, more-than-two original-binary runtime players, public matchmaking, native BEA netcode, deterministic sync, rollback, anti-cheat, rebuild parity, or no-noticeable-difference online parity.

## Thirty-First Proof Slice Completed

The latest online-shaped proof is an expanded level-854 P1/P2 fire-input-to-weapon/projectile diagnostic:

1. Validate schema `winui-original-binary-level854-fire-handoff.v1` for scope `level854-fire-input-to-weapon-handoff-not-online-proof`.
2. Launch one copied level-854/config-1 BEA host, attach CDB to the exact managed PID, and record `renderPlayers=2`, `renderLevel=854`, `boundedCaptureCount=10`, and `visualCaptureCount=10`.
3. Materialize Fire weapon Q/E only in the copied `defaultoptions.bea`, send three repeated stimulus windows (`Q`, `Q`, and `E`) plus four wait/no-input controls, and record `copiedDefaultOptionsFireWeaponQe=true`.
4. Record `button18RuntimeDispatchObserved=false`, `button19RuntimeDispatchObserved=true`, `button18DispatchCount=0`, `button19DispatchCount=3`, `sameWindowInputFireHandoffWindowCount=3`, `sameWindowInputFireHandoffObserved=true`, `sameWindowProjectileFactoryObserved=true`, `roundProjectileSameWindowCoincidenceObserved=true`, `waitWindowFireButtonDispatchCount=0`, `waitWindowCausalProof=false`, `roundProjectileCausalityProof=false`, and `runtimeOutcomeProof=false`.
5. Preserve `baseOnlineMultiplayerReady=false`, `nativeBeaNetcodeProof=false`, `publicMatchmakingProof=false`, `nPlayerOriginalBinaryRuntimeProof=0`, and `activeP3P4OriginalBinaryGameplayProof=false`.

Accepted result:

```powershell
py -3 tools\build_winui_original_binary_level854_fire_handoff_bundle.py
py -3 tools\winui_safe_copy_online_level854_fire_handoff_check.py --check
npm run test:winui-original-binary-level854-fire-handoff
```

This proves copied Fire weapon Q/E materialization, same-window weapon/fire handoff anchors, one same-window fire-to-burst pointer chain, ordered fire/burst correlation still false, and same-window projectile-factory/CRound-side activity. The source-expected button 18 did not dispatch in this run; runtime button 19 did. Wait-window burst/handoff and projectile-side hits are ambient and prevent causality promotion. This does not prove any natural death/respawn/win/loss transition, damage, kill, visual projectile, round/projectile causality, co-op/versus runtime semantics, base online multiplayer readiness, second-host LAN, active P3/P4 original-binary gameplay, more-than-two original-binary runtime players, public matchmaking, native BEA netcode, deterministic sync, rollback, anti-cheat, rebuild parity, or no-noticeable-difference online parity.

## Thirty-Second Proof Slice Completed

The thirty-second online-shaped proof is a level-854 P1/P2 fire-to-damage/outcome observer diagnostic:

1. Validate schema `winui-original-binary-level854-fire-damage-outcome.v1` for scope `level854-fire-to-damage-outcome-observer-not-online-proof`.
2. Launch one copied level-854/config-1 BEA host, attach CDB to the exact managed PID, and record `renderPlayers=2`, `renderLevel=854`, `boundedCaptureCount=10`, and `visualCaptureCount=10`.
3. Materialize Fire weapon Q/E only in the copied `defaultoptions.bea`, send three stimulus windows plus four wait/no-input controls, and record `copiedDefaultOptionsFireWeaponQe=true`.
4. Record `button18RuntimeDispatchObserved=false`, `button19RuntimeDispatchObserved=true`, `sameWindowFireHandoffWindowCount=3`, `sameWindowFireBurstPointerChainWindowCount=2`, `sameWindowDamageSurfaceWindowCount=1`, `sameWindowUnitApplyDamageWindowCount=1`, `waitWindowDamageHitCount=27`, `damageProof=false`, `runtimeOutcomeProof=false`, and `fireToDamageOutcomePromotion=false`.
5. Preserve `baseOnlineMultiplayerReady=false`, `nativeBeaNetcodeProof=false`, `publicMatchmakingProof=false`, `nPlayerOriginalBinaryRuntimeProof=0`, and `activeP3P4OriginalBinaryGameplayProof=false`.

Accepted result:

```powershell
py -3 tools\build_winui_original_binary_level854_fire_damage_outcome_bundle.py
py -3 tools\winui_safe_copy_online_level854_fire_damage_outcome_check.py
py -3 tools\winui_safe_copy_online_level854_fire_damage_outcome_check_test.py
py -3 tools\winui_safe_copy_online_level854_fire_damage_outcome_check.py --self-test
```

This proves the observer can see same-window fire handoff, fire-to-burst pointer-chain, round-collision, and CUnit damage surfaces under scoped Q/E stimulus. It does not promote damage or outcome causality because wait/no-input windows also contain damage activity and no outcome transition fired. It does not prove any natural death/respawn/win/loss transition, damage causality, kill, visual projectile, round/projectile causality, co-op/versus runtime semantics, base online multiplayer readiness, second-host LAN, active P3/P4 original-binary gameplay, more-than-two original-binary runtime players, public matchmaking, native BEA netcode, deterministic sync, rollback, anti-cheat, rebuild parity, or no-noticeable-difference online parity.

## Earlier Proof Slice

An earlier online-shaped proof is a private remote-client runtime-causality wrapper over the already accepted relay-plan runtime executor path:

1. Validate schema `winui-original-binary-private-remote-client-runtime-causality.v1` for scope `private-remote-client-to-runtime-executor-same-workstation-not-online-play`.
2. Revalidate the process-separated private remote-client proof, the host-authority two-client scheduler proof, the relay-plan runtime executor proof, the runtime-delivery proof, and the live runtime artifact hashes.
3. Record that `private-remote-client-p2-forward-0001` reaches the same host relay hash `fbb60fd900e377251059d00553835e088e73b05278314d42aaf5f28bbb3bf376` used by the copied level-850/config-1 runtime executor.
4. Preserve `privateRemoteClientRuntimeCausalityProven=true`, `remoteClientProcessSeparated=true`, `sameWorkstationOnly=true`, `remoteClientToHostRelayPathMatchCount=1`, `hostRelayToRuntimeExecutorPathMatchCount=1`, `gameInputSentByRemoteClient=false`, `gameInputSentByHostAuthorityScheduler=false`, `bridgeSendsNewNetworkInput=false`, `baseOnlineMultiplayerReady=false`, `nPlayerOriginalBinaryRuntimeProof=0`, and `activeP3P4OriginalBinaryGameplayProof=false`.
5. Reuse the executor proof's existing `newBeaLaunchCount=1`, `cdbAttachCount=1`, `visualCaptureCount=7`, and `deliveredOriginalBinaryCommandCount=2`; this wrapper does not add another BEA launch.

Accepted result:

```powershell
npm run test:winui-original-binary-private-remote-client-runtime-causality
py -3 tools\winui_safe_copy_online_private_remote_client_runtime_causality_check.py --check
npm run test:winui-original-binary-private-remote-client-runtime-causality
```

This proves only same-workstation provenance from the process-separated private remote-client command source into one copied original-BEA host-authority runtime executor proof. It does not prove base online multiplayer readiness, a second physical host, multi-host LAN play, public matchmaking, native BEA netcode, a new network input bridge inside BEA, active P3/P4 original-binary gameplay, more-than-two original-binary runtime players, co-op/versus online semantics, deterministic sync, rollback, anti-cheat, physical gamepad behavior, rebuild parity, or no-noticeable-difference online parity.

## Product Surface Guard Added

The WinUI Windowed & Mods page now includes a passive online readiness/status panel backed by `OnlineMultiplayerReadinessService`. It records the current status as `Not player-ready online/netplay`, accepted original-binary gameplay slots `P1/P2`, metadata-only slots `P3/P4`, same-host/same-workstation proof scope, and next dependency `second-host command-source plus direct runtime causality`.

The product surface deliberately exposes no Host/Join/Matchmaking buttons yet. Online hosting unavailable, Online joining unavailable, Public matchmaking, and Native BEA netcode are blocked status rows until separate runtime evidence justifies enabling them. The only tryable action named by the service is the existing Local Multiplayer Probe (`-skipfmv -level 850`).

2026-06-21 UI hardening: the same panel now renders `OnlineMultiplayerReadinessService.ProofGateRows` and disabled-action reasons. It names that live command source is not accepted, command-source JSONL is capped at `4096` bytes, live physical proof rejects `operator-supplied-runtime-host-kind`, and Host/Join requires source-bound runtime causality with exact-PID CDB evidence, accepted payload hash binding, mapped P2 sequence, host-helper receipt, and invitation lifecycle hash binding. The AppCore companion-session readiness model also binds the online-adjacent status to the prepared safe-copy launch plan: missing, stale, or launch-plan-blocked safe copies expose no tryable online-adjacent action, while a ready safe copy exposes only the local multiplayer probe.

2026-06-21 live-run-kit hardening: the second-host live-run kit now validates provided run material instead of treating path presence as enough. It also separates `readyToAttemptHarness` from `readyForLiveValidationCandidate`/`readyToRunLiveCommandSource`. Attempt-shaped material requires the upstream private-LAN proof to pass the private LAN checker, host copied/install roots to hash through local preflight, and the invitation path to be a `.json` path under OS temp and outside the repo; repo/public invitation paths are rejected before attempt readiness. Live-ready material additionally rejects upstream fixture private-LAN proof such as TEST-NET/documentation `192.0.2.0/24` or fixture sentinel auth/server identity, and requires live-compatible client runtime-kind evidence. VM-labeled attempts still require client `runtimeHostKind=vm-guest`, but operator-supplied `vm-guest` remains manual-attempt evidence only until auto platform preflight detects it; physical second-host live readiness requires `runtimeHostKindSource=auto-platform-preflight` and rejects `vm-guest`. The command-source checker's `--live` mode also rejects synthetic live-labeled fixtures by requiring non-fixture host/client identity evidence, non-fixture auth/identity/source hash values, realistic live timestamps/addresses, and server-observed transcript timestamps inside the invitation window; hidden Host/Join-style overclaims are rejected even as string/numeric truthy values. This is still preparation for a later real VM/physical run, not proof that a second host has connected.

This is not an online proof slice. It does not add a new BEA launch, CDB attach, runtime artifact, second-host LAN proof, public matchmaking, native BEA netcode, active P3/P4 original-binary gameplay, deterministic sync, rollback, anti-cheat, rebuild parity, or no-noticeable-difference online parity.

## Second-Host Readiness Contract Added

`roadmap/original-binary-online-second-host-readiness.v1.json` and `tools/winui_safe_copy_online_second_host_readiness_check.py` now define the next second-host proof boundary before any Host/Join surface is enabled. The contract is deliberately not a runtime proof. It keeps `baseOnlineMultiplayerReady=false`, `secondHostProof=false`, `multiHostLanProof=false`, `publicMatchmakingProof=false`, `nativeBeaNetcodeProof=false`, `activeP3P4OriginalBinaryGameplayProof=false`, and `hostJoinControlsMayBeEnabled=false`.

The accepted next evidence must prove `distinct-private-host-command-source-proof` plus runtime delivery evidence, but Host/Join controls remain disabled until `host-join-enablement-composite-proof` proves both the accepted command-source proof and `host-runtime-delivery-from-source-bound-distinct-command-source`. The guard rejects loopback, same-workstation-process, WSL-on-host, public-internet-host, and unknown-peer command sources as second-host proof. It requires different host identity, non-loopback private address evidence assigned to an interface, sanitized host/client interface evidence, pinned host identity, session-scoped authentication, copied-profile hashes on both sides, installed-game pre/post hashes on both sides, and Program Files mutation rejection.

Accepted validation:

```powershell
npm run test:winui-original-binary-second-host-readiness
npm run test:winui-original-binary-host-join-enablement
```

This adds zero BEA launches, zero CDB attaches, zero public endpoints, zero Host/Join buttons, and zero runtime/player-readiness claims. VM evidence is allowed only as `distinct-vm-private-lan-labeled-vm-only`; it is not physical second-host proof.

## Host/Join Composite Enablement Gate Added

`roadmap/original-binary-online-host-join-enablement.v1.json` and `tools/winui_safe_copy_online_host_join_enablement_check.py` now define the public-safe Host/Join enablement gate. The scope is `host-join-controls-composite-proof-gate-not-player-ready-online`: Host and Join stay disabled until both `distinct-private-host-command-source-proof` and `host-runtime-delivery-from-source-bound-distinct-command-source` are accepted.

The gate requires direct runtime causality from the second-host command source, accepted-command payload hash binding, runtime input derived from and driven by that command source, exact-PID CDB evidence, and no fixture/self-test/posthoc compatibility mode. It keeps `hostJoinControlsMayBeEnabled=false`, `baseOnlineMultiplayerReady=false`, `multiHostLanPlayProof=false`, `publicMatchmakingProof=false`, `nativeBeaNetcodeProof=false`, and `activeP3P4OriginalBinaryGameplayProof=false`.

Accepted validation:

```powershell
npm run test:winui-original-binary-host-join-enablement
```

## Second-Host Command-Source Proof Gate Added

`roadmap/original-binary-online-second-host-command-source.v1.json` and `tools/winui_safe_copy_online_second_host_command_source_check.py` now define the private proof-bundle validator for the next distinct-host command-source rung. This is deliberately a proof gate, not accepted live evidence: it keeps `acceptedLiveSecondHostCommandSourceProof=false`, `acceptedLiveSecondHostRuntimeDeliveryProof=false`, `baseOnlineMultiplayerReady=false`, `multiHostLanPlayProof=false`, `publicMatchmakingProof=false`, `nativeBeaNetcodeProof=false`, `activeP3P4OriginalBinaryGameplayProof=false`, `newBeaLaunchCount=0`, and `cdbAttachCount=0`.

The gate only accepts `distinct-physical-host-private-lan` or `distinct-vm-private-lan-labeled-vm-only` command-source bundle shapes. It requires hash linkage to the existing private-LAN transport proof, RFC1918/ULA private non-loopback assigned host/client addresses, client-source-not-host-local evidence, structured host/client identity evidence, sanitized interface evidence, HMAC-SHA256 session-scoped auth, pinned server/client identities, exact transcript sequence/count with payload hashes, replay/sequence protection, two-sided copied-profile and installed-game hashes, Program Files/original-executable mutation rejection, no absolute private proof paths, no hidden truthy overclaim fields including string/numeric truthy Host/Join-style values, exact accepted/rejected/transcript key sets, live negative-case session-security hardening before runtime promotion, and 16 required rejection reasons: P3/P4 gameplay route, loopback, same-workstation process, WSL-on-host, public-internet host, unknown peer, bad HMAC, pre-session command, replay nonce, stale/future timestamp window, sequence regression, pinned identity mismatch, compatibility-key mismatch, rate limit, signed unknown-field/schema mismatch, and direct input. It explicitly rejects TEST-NET/documentation ranges (`192.0.2.0/24`, `198.51.100.0/24`, `203.0.113.0/24`) for accepted live bundles. The checker now has an explicit `--live` mode: fixture/shape validation may omit live hardening, but a live candidate must carry `sessionSecurityHardening.evidenceMode=live-server-client-transcript`, signed request/response payload hashes from the observed transcript, `listenerLifecycle.evidenceMode=live-server-socket-receipt` with private non-loopback bind, no wildcard/loopback/public bind, one accepted client, listener teardown, post-close connect rejection, non-fixture auth/identity/source hash values, realistic live timestamps/addresses, plus `sourceSafety.evidenceMode=local-preflight-computed` with host/client file-counted two-phase pre/post source hashes.

Accepted validation:

```powershell
npm run test:winui-original-binary-second-host-command-source
```

This does not prove player-ready online multiplayer, multi-host LAN play, native BEA netcode, Host/Join enablement, public matchmaking, active P3/P4 original-binary gameplay, or runtime delivery from a distinct host. The next runtime proof remains `host-runtime-delivery-from-source-bound-distinct-command-source`; Host/Join enablement additionally requires the composite source-bound runtime-causality gate.

## Second-Host Command-Source Harness Added

`tools/build_winui_original_binary_second_host_command_source_bundle.py` now provides the live server/client harness for producing the proof bundle described above, with `tools/winui_original_binary_second_host_command_source_client.py` as a small second-host client wrapper. The `server` mode binds a private non-loopback address, writes a private transient invitation only under OS temp outside the repo with exclusive-create/no-overwrite semantics, records only the credential fingerprint in accepted proof artifacts, enforces invitation expiry at receive time, deletes the invitation after server completion, waits for a distinct private-LAN client, records client-source and identity evidence, records a live listener lifecycle receipt, recomputes host/client source-safety after the session, and emits a private bundle only if it passes `tools/winui_safe_copy_online_second_host_command_source_check.py`. The `client` mode reads that private invitation on a second host or VM, rejects expired or not-yet-valid invitations before connecting, and sends bounded negative/positive HMAC-authenticated messages: bad session HMAC, wrong server pin, wrong client pin, pre-session command rejection, P3/P4 metadata-slot gameplay rejection, bad command HMAC, stale/future timestamp relative to server-observed time plus the configured nonce window, sequence regression, compatibility-key mismatch, valid P2 acceptance, replay nonce, rate-limit rejection, signed unknown-field/schema-mismatch rejection, direct-input/host-helper bypass rejection, and a signed source-safety postflight. VM-labeled proofs must remain `samePhysicalMachineOnly=true`; physical second-host proofs must remain `samePhysicalMachineOnly=false`. Live hardening cases reference the signed request/response payload hashes from the observed transcript. The builder/client live harness is release-denied private tooling, and the builder also has a self-test and focused regression tests under `tools/build_winui_original_binary_second_host_command_source_bundle_test.py`.

Accepted validation:

```powershell
npm run test:winui-original-binary-second-host-command-source-builder
```

This harness is the first executable path for a later distinct-host command-source proof, but the current tracked state still has no accepted live second-host artifact. It adds zero BEA launches, zero CDB attaches, and zero host-helper input. `acceptedLiveSecondHostCommandSourceProof=false`, `acceptedLiveSecondHostRuntimeDeliveryProof=false`, and `baseOnlineMultiplayerReady=false` remain the truth until a real private-LAN host/VM run is captured and then bound to copied-host runtime delivery.

## Second-Host Live Run Kit Added

`tools/winui_original_binary_second_host_live_run_kit.py` now packages the host live-readiness result, a computed client identity/source-safety preflight, required private live-run inputs, and redacted command templates into a public-safe run kit. The scope is `second-host-live-run-kit-not-command-source-proof`; the schema is `winui-original-binary-second-host-live-run-kit.v1`.

The current checked workstation output remains not ready for a live command-source run: `readyToAttemptHarness=false`, `readyForLiveValidationCandidate=false`, `readyToRunLiveCommandSource=false`, `serverCommandInputsComplete=false`, `clientPreflightProvided=false`, `candidatePrivateBindAddressCount=1`, and `wslOnHostInterfaceCount=1`. The paired readiness preflight now hardens bind-host selection: `serverCommandInputsComplete=true` requires an eligible selected private non-WSL bind host when `--bind-host` is supplied, so WSL, link-local, TEST-NET/documentation, public, or unassigned private addresses cannot make the host appear ready. The run kit now keeps fixture/private-smoke material separate from live-validation material: TEST-NET/documentation private-LAN proof and fixture sentinel auth/server identity can be attempt-shaped but cannot make `readyForLiveValidationCandidate=true`; VM-labeled `vm-guest` evidence must be auto-detected before it can be live-ready, while operator-supplied `vm-guest` remains manual-attempt-only.

Accepted validation:

```powershell
npm run test:winui-original-binary-second-host-live-readiness
npm run test:winui-original-binary-second-host-live-run-kit
```

This run kit opens no listener, creates no invitation, launches no BEA, attaches no CDB, sends no input, creates no command-source proof, enables no Host/Join controls, and proves no player-ready netplay. Its purpose is to make the next live VM-labeled or distinct-host command-source attempt reproducible without committing private paths, raw invitation data, private proof roots, or secrets.

## Second-Host Runtime Executor Builder Added

`roadmap/original-binary-online-second-host-runtime-executor.v1.json`, `tools/build_winui_original_binary_second_host_runtime_executor_bundle.py`, and `tools/winui_safe_copy_online_second_host_runtime_executor_check.py` define the next private runtime executor rung. The scope is `second-host-command-source-to-fresh-copied-runtime-executor-not-player-ready-online`, with `runtimeExecutorBuilderReady=true`, `upstreamPrivateLanProofHashMatch=true`, `bridgeProofSameBundleOwnership=true`, `acceptedLiveSecondHostRuntimeDeliveryProof=false`, `runtimeDrivenBySecondHostCommandSource=false`, `baseOnlineMultiplayerReady=false`, and `hostJoinControlsMayBeEnabled=false`.

The runner can bind a checker-accepted second-host P2 command-source proof to a matching host-authority P1/P2 proof and, in live mode, run the existing copied-BEA runtime executor. It is intentionally blocked from live promotion until the second-host command-source proof carries `evidenceMode=live-server-client-transcript` plus signed request/response payload hashes for bad HMAC, replayed nonce, stale/future timestamp window, sequence ordering, pinned server/client identity, compatibility-key, and metadata-slot gameplay rejection.

## Second-Host Runtime Causality Gate Added

`roadmap/original-binary-online-second-host-runtime-causality.v1.json` and `tools/winui_safe_copy_online_second_host_runtime_causality_check.py` now define the stricter source-bound second-host-to-copied-runtime causality gate. This gate is validator/contract readiness only; it adds zero BEA launches, zero CDB attaches, zero Host/Join controls, zero public endpoints, and no new runtime proof counters.

Future acceptance requires candidate-bundle-relative artifact references contained under the private runtime proof root, recomputed raw artifact receipts from disk, semantic receipt envelopes plus role-specific raw-evidence bodies on every raw artifact file, and one same-run chain binding the same accepted second-host command request payload hash plus the same second-host invitation lifecycle hash across command-source, scheduler, bridge, runtime input-window, exact-PID CDB, copied-runtime artifact, copied-runtime executable hash, and process identity evidence. The gate now rejects JSON-only forged live-looking artifacts by requiring concrete raw-evidence body fields for command-source transcript hardening, scheduler relay-plan evidence, bridge mapping, runtime input-window rows, exact-PID CDB log rows, copied-runtime artifact rows, copied-executable byte hash, and process identity. It also rejects receipt-only candidates, envelope-only or hash-only synthetic files, fixture/posthoc binding, swapped bridge or run ids, stale CDB/process identity, host-authority-derived runtime input, operator/fixture source safety, unknown source-hash modes, outside-private-root candidates, private-path-leaking artifacts, self-test-only raw artifacts, missing boundary keys, and Host/Join overclaims. Self-test fixtures require explicit fixture mode and cannot return live-delivery proof booleans. Current truth remains `acceptedLiveSecondHostRuntimeCausalityProof=false`, `acceptedLiveSecondHostRuntimeDeliveryProof=false`, `runtimeInputDerivedFromSecondHostCommandSource=false`, `runtimeDrivenBySecondHostCommandSource=false`, `hostJoinControlsMayBeEnabled=false`, and `baseOnlineMultiplayerReady=false`.

## Second-Host Runtime Causality Candidate Builder Added

`tools/build_winui_original_binary_second_host_runtime_causality_candidate.py` plus package script `test:winui-original-binary-second-host-runtime-causality-builder` define the materializer preflight for the strict runtime-causality gate. The helper can write a file-backed self-test candidate under the private proof root and prove the checker accepts it only when explicit fixture mode is enabled. It also rejects the current host-authority-derived compatibility runtime executor, including edited live-looking executor booleans, without writing a candidate.

The same helper can now emit a raw-material intake plan with scope `raw-material-intake-plan-not-live-runtime-causality-proof`. The plan is private-root-contained, records `requiredRoleCount=8`, and enumerates the required raw roles/body keys for command-source transcript hardening, scheduler relay-plan evidence, bridge mapping, runtime input-window rows, exact-PID CDB log rows, copied-runtime artifact rows, copied-executable byte hash, and process identity. The plan keeps `acceptedLiveSecondHostRuntimeCausalityProof=false`, `hostJoinControlsMayBeEnabled=false`, `baseOnlineMultiplayerReady=false`, and `privateProofRootPublished=false`.

It can also derive a raw-material manifest with scope `raw-material-manifest-preflight-not-live-runtime-causality-proof` from a file-backed candidate. The manifest is candidate-bundle-relative, recomputes the candidate/artifact/raw-evidence hashes, records each role's evidence mode and material counts, rejects fixture material unless explicit fixture mode is requested, and preserves the same false live/netplay proof booleans. This closes the gap between "required raw material is known" and "future private material can be inventoried before promotion" without accepting live causality.

This is not live source-bound runtime causality. It produces no BEA launch, no CDB attach, no accepted live second-host runtime delivery, no Host/Join enablement, no public endpoint, no public matchmaking, no native BEA netcode, and no player-ready netplay. A future live materializer must consume a real distinct-host or VM-labeled command-source proof plus raw runtime/CDB material in one same-run chain before the private candidate gates can promote anything.

## Next Proof Slice

Advance from the second-host live-run kit to a real private multi-host LAN or explicitly VM-labeled command-source candidate when a second machine/session is available. First produce a computed client preflight, then run the redacted host/client command-source flow from the kit, then bind that accepted distinct-host command source through scheduler, bridge, copied-runtime input-window, exact-PID CDB, mapped P2 sequence, and host-helper delivery receipts accepted by the second-host runtime causality gate. The next credible runtime slice should still be host-authoritative: one host-side copied BEA session, bounded command sources, no public matchmaking, and explicit state/authority accounting before any native BEA netcode, public server, co-op/versus mode, or P3/P4 gameplay claim.

## Non-Claims

- No native BEA online netcode is implemented.
- No matchmaking server is implemented.
- No multi-host LAN play is proven.
- No public server, NAT traversal, anti-cheat, or abuse-control posture is proven.
- No deterministic sync, rollback, two-client parity, or no-noticeable-difference online parity is proven.
- No physical DirectInput/gamepad runtime proof exists yet.
- No installed Steam executable mutation is permitted.

## Release Boundary

Public release material may describe the plan, public-safe contracts, and bounded local proof outcomes. It must not include private runtime artifacts, private game assets, secrets, operator server credentials, raw copied-game folders, or generated proof files excluded by the release profile.
