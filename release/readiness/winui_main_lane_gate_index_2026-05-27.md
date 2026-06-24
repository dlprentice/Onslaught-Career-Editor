# WinUI main-lane gate index (2026-05-27)

Status: public-safe operator index
Date: 2026-05-27
Default branch: `main`
Tip reference: Wave925 pushed (`e55b8e35` artifact, `75d29581` state; ZIP status unchanged; release accounting R0=4031; MSIX decision status unchanged)

Use this index to find the **main-lane promotion proof as of 2026-05-27** for the WinUI product on `main`. It is not the latest Windowed & Mods or runtime-proof index. Current patch/mod/runtime status is tracked in `roadmap/mod-patch-runtime-rebuild-register.md` and later `release/readiness/winui_*` notes. Private screenshot trees under `subagents/` are never release artifacts (R4 deny).

**Idle gate:** If the operator sends bare **"proceed"** without MSIX **A-E** or a named scope, read `idle_gate_2026-05-27.md` and stop repeating probes.

## Lane promotion

| Doc | Topic |
| --- | --- |
| `winui_primary_lane_on_main_2026-05-27.md` | What `main` is now; local gates |
| `pr1_merge_readiness_2026-05-27.md` | PR #1 merge scope (lane promotion, not narrow Home-only) |
| `post_merge_operator_sync_2026-05-27.md` | Publish/sync checklist (completed 2026-05-27) |

## Local Automated Gates

| Gate | Local command |
| --- | --- |
| Primary lane | `npm run test:winui-primary-lane` |

## Desktop proof (2026-05-27)

| Doc | Proves | Does not prove |
| --- | --- | --- |
| `winui_home_visual_smoke_2026-05-27.md` | Debug visual (11 primary + 7 scrolled PNGs) + Home UIA | Release ZIP layout |
| `winui_zip_package_probe_2026-05-27.md` | Extracted Release ZIP launch + Home nav UIA + media smoke (revalidated on `main` era 2026-05-27) | MSIX/trusted install |
| `winui_zip_release_candidate_probe_2026-05-27.md` | Named RC ZIP disposable probe (revalidated `main` era 2026-05-27) | Installer-grade release |

## Re-run rules

| Change type | Re-run |
| --- | --- |
| WinUI UI/routing/copy | `test:winui-primary-lane` + explicit Home/visual smokes |
| Publish output or ZIP probe scripts | `test:winui-zip-package-probe` (+ RC probe if claiming RC) |
| Ghidra program / mutation | Headless quality snapshot + wave docs (mutation needs approval) |

## Release policy (2026-05-27 closeout on `main`)

| Check | Result |
| --- | --- |
| `release_profile_snapshot.py --check` | **PASS** after regenerate (`R0=4031 R2=0 R3=2 R4=18188`; includes `idle_gate_2026-05-27.md`) |
| `release_curated_manifest.py --check` | **PASS** (`3456` selected) |
| `npm run test:public-allowlist` | **PASS** |
| `npm run test:winui-installer-preflight` | **guarded-not-ready** (expected; not a failure) |
| `bash tools/release_package.sh --dry-run` | **PASS** (docsync + profile + curated; R4 denylist excludes `game/`, `subagents/`, state files; no archive written) |

## MSIX / installer (2026-05-27 revalidation on `main`)

| Probe | Result |
| --- | --- |
| `test:winui-installer-preflight` | **guarded-not-ready** |
| `test:winui-msix-trusted-install-probe` | **guarded-blocked** (`0x800B0109`; see `msix_trusted_install_revalidation_2026-05-27.md`) |

Disposable ZIP probes remain the proven non-installer distribution path.

Operator decision guide: `msix_trust_strategy_next_steps_2026-05-27.md` (options A-E: ZIP-only vs commercial signing / enterprise / Store).

## Still guarded-not-ready

- Trusted MSIX install / installer-grade release (unchanged after revalidation)
- Ghidra 6113/6113 as runtime gameplay semantics
- Full manual review of every Home card workflow in retail BEA
