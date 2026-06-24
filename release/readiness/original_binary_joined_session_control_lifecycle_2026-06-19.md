# Original Binary Joined-Session Control Lifecycle Readiness Note

Status: complete public-safe same-host session-control lifecycle proof
Date: 2026-06-19
Scope: `original-binary-online-joined-session-control-lifecycle`

This slice records a same-host control-plane lifecycle around the already accepted joined-session P1/P2 authority and runtime-causality path. It does not launch BEA, attach CDB, or send game input. It is a protocol/session-control proof for the online ladder, not base online multiplayer readiness.

Key tokens:

| Field | Value |
| --- | --- |
| `schemaVersion` | `winui-original-binary-joined-session-control-lifecycle.v1` |
| `sameHostSessionControlSchema` | `winui-original-binary-joined-session-same-host-session-control.v1` |
| `sessionControlScope` | `joined-session-control-lifecycle-same-host-not-online-play` |
| `sameHostSessionControlScope` | `joined-session-same-host-session-control-not-online-play` |
| `sessionControlLifecycleProven` | `sessionControlLifecycleProven=true` |
| `acceptedControlActionCount` | `acceptedControlActionCount=11` |
| `rejectedControlCaseCount` | `rejectedControlCaseCount=22` |
| `reconnectProofScope` | `metadata-reconnect-only-not-runtime-reconnect` |
| `sameHostOnly` | `sameHostOnly=true` |
| `samePhysicalMachineOnly` | `samePhysicalMachineOnly=true` |
| `newBeaLaunchCount` | `newBeaLaunchCount=0` |
| `cdbAttachCount` | `cdbAttachCount=0` |
| `gameInputSentBySessionControl` | `gameInputSentBySessionControl=false` |
| `baseOnlineMultiplayerReady` | `baseOnlineMultiplayerReady=false` |
| `activeP3P4OriginalBinaryGameplayProof` | `activeP3P4OriginalBinaryGameplayProof=false` |
| `publicMatchmakingProof` | `publicMatchmakingProof=false` |
| `multiHostLanProof` | `multiHostLanProof=false` |
| `nativeBeaNetcodeProof` | `nativeBeaNetcodeProof=false` |
| `publicBind` | `publicBind=false` |
| `publicNetworkSocketsOpened` | `publicNetworkSocketsOpened=false` |

Accepted lifecycle actions: register copied host session, list compatible session, issue P2 join ticket, activate P2 join ticket, heartbeat, pause command stream, resume command stream, soft-reconnect metadata, spectator metadata query, admin metadata query, and graceful P2 leave.

Rejected cases cover expired tickets, replayed tickets, wrong session/slot, P3/P4 gameplay activation, spectator/admin gameplay mutation, direct game input from control plane, public matchmaking, second-host claims, native-netcode claims, co-op/versus mode claims, unknown fields, oversized messages, stale heartbeat, bad sequence, missing or wrong runtime relay hash, secret-bearing messages, raw private paths, and reconnect-after-leave.

Boundary: this proves `joined-session-same-host-session-control-not-online-play` around an existing same-host P1/P2 path. It does not prove a second physical host, public matchmaking, native BEA netcode, active P3/P4 original-binary gameplay, co-op/versus runtime behavior, deterministic sync, rollback, anti-cheat, rebuild parity, or no-noticeable-difference parity.
