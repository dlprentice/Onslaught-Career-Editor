# Original Binary Host/Join Enablement Gate

Status: public-safe contract/checker accepted, no live Host/Join enablement
Date: 2026-06-21
Scope: `host-join-controls-composite-proof-gate-not-player-ready-online`

This slice closes a claim-boundary gap in the original-binary online ladder: Host/Join controls must not be enabled by second-host command-source proof alone.

Tracked artifacts:

| Artifact | Purpose |
| --- | --- |
| `roadmap/original-binary-online-host-join-enablement.v1.json` | Composite Host/Join enablement contract. |
| `tools/winui_safe_copy_online_host_join_enablement_check.py` | Validator for the composite contract plus related readiness/runtime gates. |
| `tools/winui_safe_copy_online_host_join_enablement_check_test.py` | Regression tests rejecting command-source-only enablement, missing runtime causality, and fixture/posthoc promotion. |
| `tools/winui_safe_copy_online_second_host_runtime_promotion_guard.py` | No-BEA promotion guard rejecting current compatibility executor artifacts as Host/Join-grade runtime causality. |

Required before Host/Join enablement:

- `distinct-private-host-command-source-proof`
- `host-runtime-delivery-from-source-bound-distinct-command-source`
- accepted-command payload hash binding
- invitation lifecycle hash binding
- runtime input derived from and driven by the second-host command source
- exact-PID CDB runtime input evidence
- accepted second-host payload hash in scheduler, bridge, runtime input-window, and exact-PID CDB receipts
- no fixture, self-test, or posthoc compatibility artifact as enablement proof
- no compatibility-executor promotion

Current truth remains:

- `hostJoinControlsMayBeEnabled=false`
- `baseOnlineMultiplayerReady=false`
- `multiHostLanPlayProof=false`
- `publicMatchmakingProof=false`
- `nativeBeaNetcodeProof=false`
- `activeP3P4OriginalBinaryGameplayProof=false`

Validation:

```powershell
npm run test:winui-original-binary-host-join-enablement
npm run test:winui-original-binary-second-host-runtime-promotion-guard
npm run test:winui-original-binary-second-host-readiness
```

This is not a BEA launch, CDB attach, new runtime artifact, Host/Join implementation, player-ready online multiplayer, public matchmaking, native BEA netcode, active P3/P4 original-binary gameplay, deterministic sync, rollback, anti-cheat, rebuild parity, or no-noticeable-difference proof.
