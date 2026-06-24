# Original Binary Host Authority N-Slot Runtime Bridge Readiness Note

Status: accepted live copied-runtime proof
Date: 2026-06-19
Scope: WinUI/AppCore safe-copy runtime proof, original-binary online feasibility

This slice adds one fresh N-slot concurrent relay-derived copied-runtime P1/P2 movement-state proof. The checker consumes the accepted four-client concurrent N-slot host-authority process proof, derives the runtime-compatible P1/P2 relay input sequence, launches one safe copied BEA level-850/config-1 host-helper run, attaches exact-PID CDB observation, and verifies Q/P1 and E/P2 movement-state deltas.

Accepted private artifact:

- Evidence id: `online-host-authority-n-slot-runtime-bridge-20260619-focus1`
- Proof SHA-256: `ee9aee859c40db44978664cfa11d1a668ec4fb9bade08a18ddfadcaa7847221f`
- Live runtime artifact SHA-256: `7b6118b783e82d13f20ed9e09fc593b920793e90f09a48ffc698750e56c940ae`

Evidence summary:

| Field | Value |
| --- | --- |
| Schema | `winui-original-binary-host-authority-n-slot-runtime-bridge.v1` |
| Protocol | `host-authority-n-slot-runtime-bridge.v1` |
| slot capacity | `4` |
| Accepted session participants | `4` |
| Original-binary gameplay slots | `P1,P2` |
| Metadata-only slots | `P3,P4` |
| Rejected gameplay route slots | `P3,P4` |
| Process concurrency model | `barrier-concurrent-client-processes` |
| Simultaneous client processes proven | `4` |
| Max simultaneous socket connections proven | `4` |
| Derived input sequence | `wait:300`, `down:Q,wait:500,up:Q`, `wait:300`, `down:E,wait:500,up:E` |
| Q/P1 state rows | `button31ReceiveRows=12`, `forwardStateStoreRows=12` |
| E/P2 state rows | `button31ReceiveRows=11`, `forwardStateStoreRows=11` |
| Host helper input sent | `hostHelperInputSent=true` |
| Visual captures | `7` |

Claim boundary:

- This proves that the accepted four-client N-slot process proof can supply the P1/P2 relay input sequence for a fresh copied BEA runtime host-helper run.
- This proves exact-PID CDB movement-state deltas for P1/P2 in that run.
- This keeps `nPlayerOriginalBinaryRuntimeProof=0` because P3/P4 are still metadata-only and gameplay-rejected in the original binary.
- This records `gameInputSentByNSlotScheduler=false`; the N-slot scheduler supplies the plan, and the host-helper runtime path injects the accepted P1/P2 inputs.
- This is not active P3/P4 original-binary gameplay, not more-than-two original-binary runtime players, not multi-host LAN play, not public matchmaking, not native BEA netcode, not full session-security proof, not deterministic sync, not rollback, not anti-cheat, not physical gamepad proof, not rebuild parity, and not no-noticeable-difference online parity.
- `rawPrivateProofPathPublished=false`; `rawPrivateArtifactContentPublished=false`; `absolutePrivatePathPublished=false`; `privateRuntimePointerRows=0`; `releaseIncludedPrivateArtifact=false`.

Validation:

- `py -3 -m py_compile tools\winui_safe_copy_online_host_authority_n_slot_runtime_bridge_check.py`
- `py -3 tools\winui_safe_copy_online_host_authority_n_slot_runtime_bridge_check.py --self-test`
- `py -3 tools\winui_safe_copy_online_host_authority_n_slot_runtime_bridge_check.py <private-proof-json>`

No installed Steam game mutation, no original BEA.exe mutation, no executable-byte mutation, no Ghidra mutation, and no Ghidra backup occurred in this runtime proof slice.
