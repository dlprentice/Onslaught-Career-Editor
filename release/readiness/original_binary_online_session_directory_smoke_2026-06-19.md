# Original Binary Online Session Directory Smoke Readiness Note

Status: complete public-safe architecture smoke
Date: 2026-06-19
Scope: `original-binary-online-session-directory-smoke`

This slice adds a local session-directory smoke for the original-binary online ladder. It builds one public-safe proof bundle for `same-workstation-local-directory-smoke-not-public-matchmaking`: one compatible copied-host session is registered, one compatible listing is returned, and one redacted P2 join-ticket fingerprint is issued.

Measured evidence:

| Field | Value |
| --- | --- |
| `registeredSessionCount=1` | One copied-host level-850/config-1 session descriptor registered in the local directory. |
| `compatibleListingCount=1` | One compatibility-matched listing returned with private paths, secrets, and raw addresses withheld. |
| `acceptedJoinTicketCount=1` | One P2 join ticket fingerprint issued with `rawCredentialSerialized=false`. |
| `rejectedDirectoryCaseCount=14` | Public matchmaking, public bind, native-netcode, multi-host LAN, P3/P4 gameplay routes, unknown fields, oversized rows, secret/path leakage, duplicate ids, and incompatible proof cases are rejected. |

Non-claims:

- `publicMatchmakingProof=false`
- `multiHostLanProof=false`
- `nativeBeaNetcodeProof=false`
- `nPlayerOriginalBinaryRuntimeProof=0`
- `activeP3P4OriginalBinaryGameplayProof=false`

Validation:

```powershell
py -3 tools\build_winui_original_binary_online_session_directory_smoke_bundle.py --output subagents\winui-original-binary-online\session-directory-smoke-20260619\online-session-directory-smoke-proof.json
py -3 tools\winui_safe_copy_online_session_directory_smoke_check.py subagents\winui-original-binary-online\session-directory-smoke-20260619\online-session-directory-smoke-proof.json
npm run test:winui-original-binary-online-session-directory-smoke
```

This does not launch BEA, attach CDB, send game input, prove public matchmaking, prove multi-host LAN play, prove native BEA netcode, prove active P3/P4 original-binary gameplay, prove co-op/versus runtime semantics, or prove no-noticeable-difference online parity.
