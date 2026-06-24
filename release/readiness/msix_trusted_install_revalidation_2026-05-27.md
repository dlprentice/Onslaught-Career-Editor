# MSIX trusted-install revalidation (2026-05-27)

Status: public-safe installer blocker evidence (unchanged boundary)
Date: 2026-05-27
Branch: `main` era (post PR #1 lane promotion)
Tree: post-publish tip (`ce292f7a` era)

## Purpose

Confirm whether WinUI lane promotion to `main` changed the trusted-install boundary documented in `winui_msix_trusted_install_guarded_blocker_2026-05-22.md`.

## Commands

```powershell
npm run test:winui-installer-preflight
npm run test:winui-msix-trusted-install-probe
```

## Result

| Probe | Status |
| --- | --- |
| `test:winui-installer-preflight` | **guarded-not-ready** (expected) |
| `test:winui-msix-trusted-install-probe` | **guarded-blocked** (expected) |

Build/sign/trust steps through **PASS**; `install_package` **FAIL**:

```text
HRESULT: 0x800B0109
The root certificate of the signature in the app package or bundle must be trusted.
```

Cleanup steps **PASS** (package removed, certificate removed from CurrentUser, no WinUI process remains).

## Conclusion

Lane promotion to `main` did **not** resolve trusted MSIX install. Disposable ZIP distribution remains the proven non-installer lane; installer-grade release still requires a separate signing/trust strategy (e.g. proper code-signing cert chain, not probe-generated PFX + TrustedPeople only).

## Related evidence

- `release/readiness/winui_msix_trusted_install_guarded_blocker_2026-05-22.md` (initial guarded-blocked proof)
- `release/readiness/winui_main_lane_gate_index_2026-05-27.md` (gate index)
