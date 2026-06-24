# MSIX trust strategy — next steps (2026-05-27)

Status: public-safe operator decision guide (not install proof)
Date: 2026-05-27
Branch: `main` (post PR #1 lane promotion)

## What automated probes prove today

Revalidated on `main` era (2026-05-27):

| Probe | Status | Meaning |
| --- | --- | --- |
| `test:winui-msix-candidate-probe` | **pass** | Disposable MSIX can be built from publish output |
| `test:winui-msix-signing-probe` | **pass** | Local PFX + `signtool` can sign the package |
| `test:winui-msix-install-probe` | **install blocked** | `Add-AppxPackage` fails `0x800B0109` (untrusted root) |
| `test:winui-msix-trusted-install-probe` | **guarded-blocked** | Even CurrentUser `TrustedPeople` for probe cert does not install |

See also: `msix_trusted_install_revalidation_2026-05-27.md`, `winui_msix_trusted_install_guarded_blocker_2026-05-22.md`.

**Conclusion:** Engineering can **build and sign a disposable MSIX** in-repo; **Windows does not treat the probe certificate as an install-trusted root**. This is a **trust-chain / distribution policy** problem, not a WinUI compile problem.

## What remains unproven (installer-grade)

- Successful `Add-AppxPackage` with a **production** signing identity
- Launch from installed package identity
- Uninstall after real install
- SmartScreen / reputation / Store distribution posture
- Legal/compliance sign-off for public binary redistribution
- End-user installer UX

Disposable **ZIP** probes remain the proven non-installer distribution lane (`winui_zip_package_probe_2026-05-27.md`).

## Decision status (2026-05-27)

- **Formal selection:** No option **A–E** is recorded in repo state as of `main` **`1fca716b`**.
- **Probe-proven on `main`:** Disposable **ZIP** distribution lane (package + RC probes; see gate index).
- **Probe-blocked on `main`:** MSIX trusted install (`0x800B0109`; probe PFX + CurrentUser `TrustedPeople` insufficient).
- **Options B/C/D:** Require external trust infrastructure (CA cert, enterprise policy, or Store) not present in this repository.

This section records evidence only; it does **not** adopt Option **A** as formal product policy.

## Strategy options (operator decision)

| Option | Summary | Repo can automate | Needs human/org |
| --- | --- | --- | --- |
| **A. Stay on ZIP** | Ship documented disposable ZIP + README; no MSIX | ZIP/RC probes (done) | Release comms, support |
| **B. Commercial code signing** | OV/EV cert from a public CA; sign MSIX/AppX | Signing probe shape; new pipeline wiring | Purchase, identity verification, secure HSM/storage |
| **C. Enterprise/internal** | Distribute cert via IT (Trusted Publisher / policy) | Same as B for build | IT policy, not public Steam-style release |
| **D. Microsoft Store** | Store pipeline handles trust | Separate packaging work | Partner account, policy review |
| **E. Delay installer** | Keep `guarded-not-ready` until B/C/D decided | Preflight + blocker docs (done) | Product call |

**Probe-generated PFX + TrustedPeople alone is not sufficient** (proven blocked). Do not claim installer readiness without a new trust root strategy and a passing install probe using that identity.

## Suggested next engineering slice (when scope approved)

1. Choose option **A** (ZIP-only) or **B/C/D** (real trust path).
2. If B: integrate production cert into a **non-probe** signing script; add install probe gated on that cert (no `--allow-current-user-cert-trust` shortcut).
3. Update `winui_main_lane_gate_index_2026-05-27.md` and `CURRENT_CAPABILITIES.md` only after a **pass** install probe with the production identity.
4. Keep generated PFX/MSIX/certs under `subagents/` (R4 deny).

## Commands reference

```powershell
npm run test:winui-installer-preflight
npm run test:winui-msix-candidate-probe
npm run test:winui-msix-signing-probe
npm run test:winui-msix-install-probe
npm run test:winui-msix-trusted-install-probe
```
