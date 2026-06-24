# Original Binary Second-Host Command-Source Harness

Status: private command-source harness implemented; no live second-host gameplay, Host/Join, or runtime proof
Date: 2026-06-20
Updated: 2026-06-21 computed source-safety preflight, invitation lifecycle receipt, 4096-byte JSONL boundary, and live physical runtime-host-kind provenance hardening

This slice adds `tools/build_winui_original_binary_second_host_command_source_bundle.py`, `tools/winui_original_binary_second_host_command_source_client.py`, and focused builder tests. The helper is private command-source proof tooling only: it can run a real server/client harness for a later distinct private-LAN host or VM to produce a `winui-original-binary-second-host-command-source.v1` private proof bundle that is accepted by `tools/winui_safe_copy_online_second_host_command_source_check.py`, but it is not online multiplayer, Host/Join enablement, or runtime delivery into BEA.

Accepted harness tokens:

| Token | Value |
| --- | --- |
| `builder` | `tools/build_winui_original_binary_second_host_command_source_bundle.py` |
| `clientRunner` | `tools/winui_original_binary_second_host_command_source_client.py` |
| `builderTest` | `tools/build_winui_original_binary_second_host_command_source_bundle_test.py` |
| `packageScript` | `test:winui-original-binary-second-host-command-source-builder` |
| `proofSchemaVersion` | `winui-original-binary-second-host-command-source.v1` |
| `acceptedLiveSecondHostCommandSourceProof` | `false` |
| `acceptedLiveSecondHostRuntimeDeliveryProof` | `false` |
| `baseOnlineMultiplayerReady` | `false` |
| `newBeaLaunchCount` | `0` |
| `cdbAttachCount` | `0` |
| `hostHelperInputSent` | `false` |
| `credentialInvitationLifecycle` | OS-temp only; exclusive-create; client rejects expired/not-yet-valid invitations; deleted by the server after the run succeeds or fails |
| `computedMachineFingerprintPreflight` | Host/client machine fingerprints can be computed from redacted local host/platform fingerprints when not explicitly supplied |
| `computedSourceSafetyPreflight` | Host/client copied-profile and installed-game roots can be hashed locally; accepted live proof must not rely on hash-only self-attestation |
| `invitationLifecycleReceipt` | Accepted bundles carry sanitized descriptor hash, exclusive-create success, deletion success, and post-delete absence without raw path/private material |
| `maxJsonLineBytes` | `4096` |
| `livePhysicalRuntimeHostKindSource` | Physical second-host `--live` validation rejects `operator-supplied-runtime-host-kind` for host and client identity evidence |

The harness has two live modes:

- `server`: binds a private non-loopback host interface, computes or records redacted host machine identity and source-safety preflight evidence, writes a private transient client invitation only under OS temp outside the repo using exclusive-create semantics, waits for a distinct private-LAN command source, records structured host/client identity and source-safety evidence, deletes the credential-bearing invitation after server completion, writes a sanitized invitation lifecycle receipt into the bundle, then emits a private proof bundle only if the resulting artifact validates against the second-host command-source checker. The invitation carries the ephemeral HMAC credential, must not be written inside the repo tree, must not overwrite an existing invitation, and must not remain as a durable artifact.
- `client`: reads the private invitation on the second host or VM, rejects expired or not-yet-valid invitations before connecting, computes or records redacted client machine identity and source-safety preflight evidence, connects to the server, authenticates with the ephemeral HMAC credential, sends the bounded bad-HMAC, wrong-server-pin, wrong-client-pin, pre-session command, P3 rejection, stale/future timestamp, sequence, compatibility-key, P2 acceptance, replay, rate-limit, and direct-input bypass sequence, and prints a redacted client summary.

For live proof promotion, source-safety evidence must come from `--host-copied-profile-root` / `--host-installed-game-root` and `--client-copied-profile-root` / `--client-installed-game-root`, or an equivalent computed preflight path. Hash-only arguments remain useful for fixtures and diagnostics but are rejected as the stronger live evidence class.

The command-source JSONL reader now enforces a 4096-byte maximum line before JSON parse, matching the session-security lane. Live physical second-host promotion also rejects operator-supplied runtime-host-kind evidence; explicitly VM-labeled proof remains VM-only and does not satisfy the physical-host claim.

The live transcript hashes the signed request envelopes and matching server responses for each hardening case. The accepted P2 command row must carry `requestEvent=client_command_p2_forward`, `requestPayloadSha256`, `responseEvent=server_command_accepted`, and `responsePayloadSha256` values that match the observed transcript. Synthetic hardening objects are not accepted for live runtime promotion.

VM-labeled command-source proofs are allowed only as an intermediate rung and must keep `samePhysicalMachineOnly=true`; physical second-host proofs must keep `samePhysicalMachineOnly=false` and must not rely on operator-supplied runtime-host-kind evidence in `--live` mode. Neither shape enables Host/Join until a later copied-runtime delivery proof passes.

The live server/client harness and focused harness tests are release-denied private tooling because they handle transient credentials and live socket proof machinery. Public release material may include this bounded readiness note and proof contract, not generated private invitations or live proof bundles.

Focused validation:

```powershell
py -3 tools\build_winui_original_binary_second_host_command_source_bundle_test.py
py -3 tools\build_winui_original_binary_second_host_command_source_bundle.py --self-test
npm run test:winui-original-binary-second-host-command-source-builder
```

Non-claims:

- No live second-host command-source artifact was accepted by this slice.
- No runtime delivery from a distinct host is proven.
- No BEA launch or CDB attach is added.
- No Host/Join/Matchmaking WinUI control is enabled.
- No public endpoint, public matchmaking, or native BEA netcode is implemented.
- No active P3/P4 original-binary gameplay is proven.
- No deterministic sync, rollback, anti-cheat, rebuild parity, or no-noticeable-difference online parity is proven.
