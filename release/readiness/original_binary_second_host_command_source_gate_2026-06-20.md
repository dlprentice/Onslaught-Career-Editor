# Original Binary Second-Host Command-Source Gate

Status: public-safe proof gate, not live runtime proof
Date: 2026-06-20
Updated: 2026-06-21 source-safety preflight, live-validation hardening, strict schema mismatch rejection, fixture-sentinel rejection, and string/numeric overclaim rejection

This slice adds `roadmap/original-binary-online-second-host-command-source.v1.json` and `tools/winui_safe_copy_online_second_host_command_source_check.py` to define and validate the private proof-bundle shape required before a later distinct-host command-source artifact can be accepted.

Accepted gate tokens:

| Token | Value |
| --- | --- |
| `schemaVersion` | `winui-original-binary-second-host-command-source-gate.v1` |
| `gateScope` | `second-host-command-source-proof-gate-not-live-runtime-proof` |
| `acceptedLiveSecondHostCommandSourceProof` | `false` |
| `acceptedLiveSecondHostRuntimeDeliveryProof` | `false` |
| `baseOnlineMultiplayerReady` | `false` |
| `multiHostLanPlayProof` | `false` |
| `publicMatchmakingProof` | `false` |
| `nativeBeaNetcodeProof` | `false` |
| `activeP3P4OriginalBinaryGameplayProof` | `false` |
| `newBeaLaunchCount` | `0` |
| `cdbAttachCount` | `0` |
| `requiredRejectedCaseCount` | `16` |
| `requiresComputedMachineFingerprintPreflight` | `true` |
| `requiresInvitationLifecycleReceipt` | `true` |
| `requiresLocalSourceSafetyPreflightForLiveProof` | `true` |
| `requiresFixtureSentinelLiveProofRejection` | `true` |
| `requiresStringNumericTruthyOverclaimRejection` | `true` |
| `nextRequiredProof` | `host-runtime-delivery-from-source-bound-distinct-command-source` |

The gate accepts only `distinct-physical-host-private-lan` or `distinct-vm-private-lan-labeled-vm-only` command-source evidence. It rejects loopback, same-workstation process, WSL-on-host, public internet, unknown peer, bad HMAC, pre-session commands, replay nonce, stale/future timestamp window, sequence regression, pinned identity mismatch, compatibility-key mismatch, rate-limit, signed unknown-field/schema mismatch, direct-input, and P3/P4 gameplay-route cases. The live-bundle validator also rejects TEST-NET/documentation address ranges (`192.0.2.0/24`, `198.51.100.0/24`, `203.0.113.0/24`) instead of treating sample address ranges as private-host evidence.

The accepted private proof bundle must also hash-link to the existing private-LAN transport proof, prove RFC1918/ULA private non-loopback assigned host/client addresses, prove the client source address is not host-local, carry structured distinct host/client identity and sanitized interface evidence, use HMAC-SHA256 session-scoped auth with pinned server/client identities, preserve copied-profile hashes and installed-game pre/post hashes on both sides, reject Program Files/original executable mutation, enforce exact transcript event sequence/count with payload hashes, enforce exact accepted/rejected/transcript key sets, reject absolute private proof paths, reject hidden truthy overclaim fields such as Host/Join enablement including string/numeric truthy values, and provide live transcript-derived session-security hardening before runtime promotion.

The 2026-06-21 hardening requires the bundle to carry computed/redacted machine-fingerprint preflight fields, a durable invitation lifecycle receipt, and source-safety evidence labeled as either local preflight-computed or self-test fixture. Operator-supplied hash-only evidence is not enough for future live proof promotion. Future live command-source candidates must also pass `tools/winui_safe_copy_online_second_host_command_source_check.py <private-bundle> --live`, which requires `sessionSecurityHardening.evidenceMode=live-server-client-transcript`, signed request/response payload hashes for the negative cases, `sourceSafety.evidenceMode=local-preflight-computed` with host/client file-counted source hashes, realistic live timestamps, non-fixture private addresses, and non-fixture auth/identity/source hash values.

Validation:

```powershell
py -3 tools\winui_safe_copy_online_second_host_command_source_check_test.py
py -3 tools\winui_safe_copy_online_second_host_command_source_check.py --self-test
py -3 tools\winui_safe_copy_online_second_host_command_source_check.py --check
py -3 tools\winui_safe_copy_online_second_host_command_source_check.py <private-bundle> --live
npm run test:winui-original-binary-second-host-command-source
npm run test:winui-copied-profile-runtime
```

Non-claims:

- No live second-host command-source artifact is accepted by this slice.
- No BEA launch is added by this gate.
- No CDB attach is added by this gate.
- No second-host LAN play is proven.
- No public matchmaking or public endpoint is implemented.
- No native BEA netcode is proven or implemented.
- No Host/Join/Matchmaking WinUI button is enabled.
- No active P3/P4 original-binary gameplay is proven.
- No deterministic sync, rollback, anti-cheat, rebuild parity, or no-noticeable-difference online parity is proven.
