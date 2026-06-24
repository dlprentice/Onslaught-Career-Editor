# Original Binary Second-Host Command-Source Security Hardening

Status: validator and harness hardened, not live runtime proof
Date: 2026-06-20
Updated: 2026-06-21 computed source-safety preflight, invitation lifecycle receipt, and strict schema mismatch rejection
Scope: `second-host-command-source-proof-gate-not-live-runtime-proof`

This slice tightens the second-host command-source proof gate before any live runtime promotion. It does not add a playable online proof.

Hardened evidence requirements:

| Item | Value |
| --- | --- |
| Required rejected reasons | `16` |
| Live hardening evidence mode | `live-server-client-transcript` |
| Runtime-promotion fixture hardening accepted | `false` |
| Signed request/response payload hashes required | `true` |
| Accepted P2 command transcript binding required | `true` |
| Invitation path confinement | OS temp outside repo |
| Invitation exclusive create | `true` |
| Invitation expiry validation | Client rejects expired/not-yet-valid invitations before connect |
| Invitation cleanup | Deleted after server completion |
| Invitation lifecycle receipt | Accepted proof carries sanitized descriptor hash, exclusive-create success, deletion success, and post-delete absence |
| Machine identity preflight | Host/client machine fingerprints must be computed or fixture-labeled with redacted hostname/platform fingerprints |
| Source-safety preflight | Live proof requires local preflight-computed source evidence; hash-only operator input is not enough for promotion |
| Credential transport boundary | Transient OS-temp invitation only; credential hash is recorded in accepted proof, raw credential is not artifact-serialized |
| Timestamp window enforcement | Message timestamps are checked against server-observed time plus the configured nonce window, not the whole session expiry |
| VM/physical proof separation | VM-labeled proof must keep `samePhysicalMachineOnly=true`; physical proof must keep `samePhysicalMachineOnly=false` |
| Level854 aggregate flake handling | `tools/build_winui_original_binary_level854_fire_handoff_bundle.py` retries only exact pre-promotion foreground-focus loss or a basic-fire-handoff run that missed the required fire-burst pointer-chain promotion token; final accepted artifacts still require every input row `status=sent` and `sameWindowFireBurstPointerChainObserved=true` |
| Secure N-slot runtime executor warmup handling | `tools/winui_safe_copy_online_host_authority_secure_n_slot_runtime_executor_check.py` retries only the exact first-baseline CDB render-warmup miss; final accepted artifacts still require the unchanged secure N-slot movement-state proof |
| Base online readiness | `baseOnlineMultiplayerReady=false` |
| Live second-host runtime delivery | `acceptedLiveSecondHostRuntimeDeliveryProof=false` |
| BEA launch/CDB attach added | `0 / 0` |

Required live negative cases before runtime promotion:

- Bad session HMAC and bad command HMAC.
- Wrong pinned server identity and wrong pinned client identity.
- Pre-session command rejection before a valid session is established.
- P3/P4 metadata-slot gameplay rejection.
- Stale and future timestamp rejection relative to server-observed time and the configured nonce window.
- Sequence regression rejection.
- Compatibility-key mismatch rejection.
- Replay nonce rejection.
- Rate-limit rejection after the accepted P2 command.
- Signed unknown-field/schema mismatch rejection before acceptance.
- Direct-input/host-helper bypass rejection after session establishment.
- Accepted P2 command request/response hash binding: `client_command_p2_forward` and `server_command_accepted`.

Validation:

```powershell
npm run test:winui-original-binary-second-host-command-source
npm run test:winui-original-binary-second-host-command-source-builder
npm run test:winui-original-binary-second-host-runtime-executor
npm run test:winui-copied-profile-runtime
```

Non-claims:

- No accepted live second-host command-source artifact is created by this note.
- No copied BEA runtime delivery from a distinct host is proven.
- No Host/Join/Matchmaking control is enabled.
- No public matchmaking, public endpoint, native BEA netcode, active P3/P4 gameplay, deterministic sync, rollback, anti-cheat, rebuild parity, or no-noticeable-difference online parity is proven.
