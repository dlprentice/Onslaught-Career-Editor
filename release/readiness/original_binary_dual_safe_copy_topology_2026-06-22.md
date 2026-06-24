# Original Binary Dual Safe-Copy Topology Readiness Note

Status: complete public-safe topology contract
Date: 2026-06-22
Scope: `dual-safe-copy-same-workstation-topology-not-online-play`

This slice records the near-term companion-app topology needed before a future Host/Join flow: one host safe copy and one joiner safe copy, each app-owned and separate. It is a contract/checker slice only. It does not launch BEA, attach CDB, open a listener, create an invitation, send input, enable Host/Join, or prove player-ready netplay.

Accepted topology evidence:

| Field | Evidence |
| --- | --- |
| Contract | `roadmap/original-binary-online-dual-safe-copy-topology.v1.json` |
| Schema | `winui-original-binary-online-dual-safe-copy-topology.v1` |
| Scope | `dual-safe-copy-same-workstation-topology-not-online-play` |
| Safe copies | `safeCopyCount=2`; `roles=host,joiner`; root labels are `host-safe-copy-root` and `joiner-safe-copy-root`. |
| Descriptor counters | `safeCopyRootDescriptorCount=2`; `safeCopyExecutableDescriptorCount=2`; `distinctSafeCopyRootPairCount=1`; descriptor fingerprints are public-safe labels, not published paths. |
| Workstation boundary | `sameWorkstationOnly=true`; `samePhysicalMachineOnly=true`; distinct endpoint proof remains false. |
| Safety boundary | Both rows require app-owned separate roots and keep installed-game/original-executable/Steam writes false. |
| Host/Join boundary | `hostJoinControlsMayBeEnabled=false`; `baseOnlineMultiplayerReady=false`; future Host/Join still requires distinct endpoint command-source proof plus source-bound copied-runtime causality. |
| Runtime side effects | BEA launch count: 0; CDB attach count: 0; listener opened: false; invitation created: false; input sent: false. |

Validation:

```powershell
py -3 tools\winui_safe_copy_online_dual_safe_copy_topology_check_test.py
py -3 tools\winui_safe_copy_online_dual_safe_copy_topology_check.py --self-test
py -3 tools\winui_safe_copy_online_dual_safe_copy_topology_check.py --check
npm run test:winui-original-binary-dual-safe-copy-topology
```

Non-claims: this is not player-ready netplay, not multi-host LAN play, not public matchmaking, not native BEA netcode, not separate-screen gameplay, not active P3/P4 original-binary gameplay, not deterministic sync, not rollback, not anti-cheat, not rebuild parity, and not no-noticeable-difference online parity.
