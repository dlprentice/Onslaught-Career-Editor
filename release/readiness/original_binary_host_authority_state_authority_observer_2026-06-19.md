# Original Binary Host Authority State-Authority Observer Readiness Note

Status: accepted public-safe summary over private copied-runtime proof
Date: 2026-06-19
Scope: WinUI/AppCore safe-copy runtime proof, original-binary online feasibility

This slice adds one host-authority state-authority observer proof over the accepted N-slot runtime bridge. The checker consumes the accepted N-slot concurrent relay-derived runtime bridge proof, validates the referenced copied level-850/config-1 runtime artifact, and verifies that exact-PID CDB rows form a consistent P1/P2 host-owned state graph from render state through controller dispatch, player receive, BattleEngine part, WalkerPart, and movement-state store.

The raw proof remains private/ignored because it contains runtime pointers and private artifact references. This readiness note publishes only hashes, counters, booleans, and inherited public-safe boundary tokens from the already validated N-slot bridge and slot-ceiling guard.

Accepted private evidence:

- Evidence id: `online-host-authority-state-authority-observer-20260619-focus1`
- State-authority proof schema: `winui-original-binary-host-authority-state-authority-observer.v1`
- Protocol: `host-authority-state-authority-observer.v1`
- State-authority proof SHA-256: `ac1cd32281e354b5ae37a0aa8c17b1ab883bc9dd863c2ae5e2ffe7bde62c0416`
- Source N-slot runtime bridge proof SHA-256: `ee9aee859c40db44978664cfa11d1a668ec4fb9bade08a18ddfadcaa7847221f`
- Live runtime artifact SHA-256: `7b6118b783e82d13f20ed9e09fc593b920793e90f09a48ffc698750e56c940ae`
- N-slot concurrent process proof SHA-256: `7458bbafcca8fbb60f0b7750fac068b7a6dcdfe59b13980f54da081832f95896`

Evidence summary:

| Field | Value |
| --- | --- |
| Host authority model | `hostAuthorityModel=single-host-authoritative-copied-session` |
| Runtime profile | `runtimeProfile=original-binary-copied-local-splitscreen` |
| Host authority scope | `single-copied-host-exact-pid-state-graph` |
| slot capacity | `4` |
| Accepted session participants | `4` |
| Original-binary gameplay slots | `acceptedOriginalBinaryGameplaySlots=P1,P2` |
| Metadata-only slots | `metadataOnlySlots=P3,P4` |
| Unsupported runtime route | `unsupported-original-binary-active-slot`; `required-for-unproven-original-binary-slots` |
| Max original-binary active slots proven | `maxOriginalBinaryActiveSlotsProven=2` |
| Process concurrency model | `barrier-concurrent-client-processes` |
| Simultaneous client processes proven | `4` |
| Max simultaneous socket connections proven | `4` |
| Derived input sequence | `wait:300`, `down:Q,wait:500,up:Q`, `wait:300`, `down:E,wait:500,up:E` |
| Host graph | `players=2`; `level=850`; `horizSplit=1`; `distinctPlayers=true`; `distinctBattleEngines=true`; `distinctWalkers=true`; `distinctControllers=true` |
| State-authority graph | `stateAuthorityGraphProven=true` |
| P1/Q route authority | `inputDevice=0`; `routeType=walker-forward`; `state260=00000002`; `button31ReceiveRows=12`; `forwardEntryRows=12`; `forwardStateStoreRows=12`; `observedVectorDelta=true` |
| P2/E route authority | `inputDevice=1`; `routeType=walker-forward`; `state260=00000002`; `button31ReceiveRows=11`; `forwardEntryRows=11`; `forwardStateStoreRows=11`; `observedVectorDelta=true` |
| Clean baseline windows | `waitWindowsClean=true` |
| Visual captures | `7` |
| Host helper input sent | `hostHelperInputSent=true` |
| Scheduler direct game input | `gameInputSentByNSlotScheduler=false` |

Claim boundary:

- This proves that the accepted N-slot concurrent relay plan drove one copied host whose exact-PID CDB rows form a consistent P1/P2 host-owned state graph.
- This proves P1/Q and P2/E route authority through distinct controller, player, BattleEngine, and WalkerPart paths for this copied level-850/config-1 run.
- This keeps `nPlayerOriginalBinaryRuntimeProof=0`, `activeP3P4OriginalBinaryGameplayProof=false`, `beyondTwoPlayersRequiresNewProofClass=true`, and `permanentImpossibilityClaim=false`.
- This keeps `securityProofScope=minimal-smoke-hmac-envelope-not-full-session-security-proof` and `publicBind=false`.
- This is not active P3/P4 original-binary gameplay, not more-than-two original-binary runtime players, not multi-host LAN play, not public matchmaking, not native BEA netcode, not full session-security proof, not deterministic sync, not rollback, not anti-cheat, not physical gamepad proof, not rebuild parity, and not no-noticeable-difference online parity.
- `multiHostLanProof=false`; `publicMatchmakingProof=false`; `nativeBeaNetcodeProof=false`; `deterministicSyncProof=false`; `rollbackProof=false`; `antiCheatProof=false`; `rebuildParityProof=false`; `noNoticeableDifferenceProof=false`.
- `rawPrivateProofPathPublished=false`; `rawPrivateArtifactContentPublished=false`; `absolutePrivatePathPublished=false`; `privateRuntimePointerRows=0`; `releaseIncludedPrivateArtifact=false`.

Validation:

- `py -3 -m py_compile tools\winui_safe_copy_online_host_authority_state_authority_observer_check.py`
- `py -3 tools\winui_safe_copy_online_host_authority_state_authority_observer_check.py --self-test`
- `py -3 tools\winui_safe_copy_online_host_authority_state_authority_observer_check.py <private-proof-json>`

No installed Steam game mutation, no original BEA.exe mutation, no executable-byte mutation, no Ghidra mutation, and no Ghidra backup occurred in this proof slice.
