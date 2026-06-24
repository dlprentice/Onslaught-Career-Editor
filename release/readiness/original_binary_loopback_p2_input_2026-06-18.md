# Original Binary Loopback P2 Input Proof

Status: accepted local loopback command-envelope proof
Date: 2026-06-18
Scope: WinUI/AppCore safe copied original-binary runtime proof

This slice adds the first original-binary-online-shaped proof without claiming real online play. A clean retail `BEA.exe` backup with SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750` was copied into an app-owned safe profile, patched only with the copied windowed pair, launched as `-skipfmv -level 850 -configuration 1`, observed by exact-PID CDB, and stopped through the managed copied-profile path.

The loopback proof bundle uses schema `winui-original-binary-loopback-p2-input.v1` with helper version `loopback-helper.v1` and protocol version `loopback-input.v1`. It records one accepted mock remote command, `loopback-p2-forward-0001`, with `remoteSlot=P2`, `command=movement-forward`, and mapped focused input sequence `down:E,wait:500,up:E`. It also records rejected malformed and P1-targeted command rows with `inputSent=false`.

Accepted checker result:

| Field | Value |
| --- | --- |
| Transport | `local-loopback-mock` |
| Launch args | `-skipfmv -level 850 -configuration 1` |
| CDB command | `local-multiplayer-level850-input-state-delta-observer.cdb.txt` |
| P2 receive rows | `11` button-31 receive rows |
| P2 movement rows | `11` Walker forward entry rows and `11` Walker forward state-store rows |
| P2 route | `inputDevice=1`, `routeType=walker-forward`, nonzero stored move value `bf800000` |
| Visual evidence | `4` foreground/occlusion-free captures in the private local artifact |
| Source safety | Installed executable, clean override executable, and source save/options hashes unchanged |

Validation:

```powershell
py -3 tools\build_winui_original_binary_loopback_p2_input_bundle.py <private-live-runtime-artifact>
py -3 tools\winui_safe_copy_online_loopback_p2_input_check.py <private-loopback-proof-bundle> --expected-controller-configuration 1
npm run test:winui-original-binary-loopback-p2-input
```

Claim boundary:

- This proves a local mock remote-intent command envelope can be mapped into the P2/bottom-player route of one safe copied original-binary split-screen session.
- This is not online play, matchmaking, public relay/server behavior, native BEA netcode, NAT traversal, anti-cheat, deterministic sync, rollback, two-client parity, physical gamepad behavior, rebuild parity, or no-noticeable-difference online parity.
- Raw runtime artifacts, captures, CDB logs, copied profile roots, process identifiers, and local proof paths remain private and release-excluded.

Next proof class:

Use the same command envelope to build a local relay/session descriptor proof, then a private LAN/direct relay proof. Public matchmaking and native BEA networking stay separate future lanes.
