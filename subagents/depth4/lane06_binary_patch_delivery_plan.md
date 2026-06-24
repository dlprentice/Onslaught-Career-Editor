# Lane 06 - Binary Patch Delivery Plan (Final Synthesis)

Date: 2026-03-04
Scope: delivery sequencing for binary patching with explicit `Stable` vs `Experimental` tracks, rollback gates, byte-verification gates, and extra-graphics/cardid coverage.

## 1) Delivery Model

Two-track model:

| Track | Purpose | Default Exposure | Risk Profile |
|---|---|---|---|
| Stable | Ship/maintain low-regression, byte-verified patching and companion graphics workflows | Enabled in primary UX | Low to Medium |
| Experimental | Isolate high-regression or incomplete-mapping patch work | Explicit opt-in only | Medium to High |

Promotion rule: nothing moves from Experimental to Stable without passing the full byte-verification and rollback gates defined below.

## 2) Global Gates (Apply to All Tracks)

### Gate A - Target Profile Gate (Preflight)

1. Detect `BEA.exe` hash before any write.
2. Match against profile manifest:
3. `canonical` (Steam SHA256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`)
4. `approved variant` (explicit allowlist entry)
5. Unknown hash outcome:
6. Stable track: block writes (or require explicit override mode with warning banner).
7. Experimental track: block by default; allow only in isolated research mode with full backup required.

### Gate B - Byte Verification Gate (Before Write)

1. For each selected patch site, state must be exactly one of:
2. `original` bytes (ready to patch), or
3. `patched` bytes (already patched / no-op).
4. Any mismatch or out-of-range offset aborts the entire operation.

### Gate C - Atomic Write + Immediate Read-Back

1. Write only selected `original -> patched` sites.
2. Re-read file bytes immediately and verify every touched site equals `patched`.
3. If read-back fails, stop and trigger rollback gate.

### Gate D - Rollback Readiness Gate

1. Backup must exist before first write in session.
2. Stable display lane backup source: `BEA.exe.original.backup`.
3. On any post-write verification failure, restore from backup and re-verify bytes.

### Gate E - Post-Apply State Gate

1. Report per-site state for all selected patches (`original/patched/mismatch/out-of-range`).
2. Mark run successful only when all selected sites are in known state and intended target bytes are confirmed.

## 3) Stable Track Plan

## 3.1 Stable-S1: Taxonomy + UX Hardening

Deliverables:

1. Canonical `Stable`/`Experimental` labels across docs, script help, WPF/PyQt UI.
2. Stable preset naming for existing display flow patches.

Byte gate impact: none (docs/UX only).
Rollback gate: simple revert of labeling/content changes.

## 3.2 Stable-S2: Profile-Aware Targeting

Deliverables:

1. Executable hash/profile manifest support in patch surfaces.
2. Consistent unknown-hash policy in CLI/UI.

Byte gate impact: preflight only.
Rollback gate: feature-flag fallback to current offset-only verification path.

## 3.3 Stable-S3: Stable Display Patch Preset (A-minimal)

Patch set (existing low-risk lane):

| Key | File Offset | Original | Patched | Notes |
|---|---:|---|---|---|
| `resolution_gate` | `0x129696` | `CC` | `00` | non-4:3 reject bypass |
| `force_windowed` | `0x12A644` | `A1 F0 2D 66 00` | `B8 01 00 00 00` | force startup windowed decision |
| `skip_auto_toggle` (optional) | `0x12BB97` | `75 20` | `EB 20` | partial startup flow tweak |

Verification gate:

1. Must pass Gate B on all selected offsets.
2. Must pass Gate C read-back on all touched offsets.

Rollback gate:

1. Restore `BEA.exe` from `BEA.exe.original.backup`.
2. Re-run verify to prove original bytes restored.

## 3.4 Stable-S4: Compatibility Guard Micro-Patch

Patch:

| Key | File Offset | Original | Patched | Notes |
|---|---:|---|---|---|
| `forcewindowed_guard_normalize` | `0x262F3E` | `00` | `01` | variant compatibility only |

Rules:

1. Off by default; separate toggle.
2. No-op on binaries already at `01`.

Verification gate: same Gate B/C sequence per site.
Rollback gate: restore original recorded byte (`00` or `01`) and verify.

## 3.5 Stable-S5: Regression Coverage Expansion

Deliverables:

1. Add automated verify/apply/restore tests for WPF/PyQt and script mode flags.
2. Add fixture coverage for canonical and approved variant profiles.

Byte gate impact: test-only.
Rollback gate: disable failing tests without changing shipped patch bytes.

## 3.6 Stable-S6: Extra-Graphics/Cardid Companion Track (Non-binary)

Purpose: cover requested extra-graphics scope with low-risk file workflow before binary gate bypass work.

Deliverables:

1. Managed `cardid.txt` preset insertion/merge flow.
2. Backup/restore for `cardid.txt`.
3. Preserve unknown lines/comments wherever possible.

Baseline tweak preset examples:

1. `GEFORCE_FX_POWER 1`
2. `SRT_ENABLE 1`
3. `IMPOSTOR_ENABLE 1`
4. `LANDSCAPE_LIGHTING 1`

Verification gate:

1. Syntax integrity check (vendor/device/tweak block structure).
2. Idempotency check (re-apply should not duplicate entries).

Rollback gate:

1. Restore original `cardid.txt` from backup.
2. Confirm checksum/path and line-count parity (or exact byte parity when backup restore used).

## 4) Experimental Track Plan

## 4.1 Experimental-X1: 28-Region Widescreen Binary Lane

Scope: productize the mapped widescreen diff regions as an opt-in experimental profile.

Verification gate:

1. Per-region before/after byte manifests required.
2. Abort on first mismatch.

Rollback gate:

1. Mandatory full-file backup before region 1 write.
2. One-step full restore plus targeted byte spot-check at representative regions.

## 4.2 Experimental-X2: Additional Startup Fullscreen Gate Patches

Scope: patch sites beyond `0x12BB97` once branch ownership and behavior are proven.

Verification gate:

1. No write until each candidate site has mapped owner, expected byte pair, and runtime evidence.
2. Apply as independent micro-patches.

Rollback gate:

1. Per-micro-patch disable/revert support.
2. Full backup restore remains global fallback.

## 4.3 Experimental-X3: Force Default `ALLOW_WIDESCREEN_MODES`

Scope: binary-side default-on behavior for widescreen mode flag.

Verification gate:

1. Proof of initializer/write-site ownership and config load-order interactions before implementation.
2. Pre/post bytes documented for every touched site.

Rollback gate:

1. Single control to revert all touched defaults.
2. Backup restore required if any site fails post-apply read-back.

## 4.4 Experimental-X4: Binary Extra-Graphics/Cardid Gate Bypass

Scope: direct binary bypass path for cardid-driven graphics gating.

Verification gate:

1. Discovery-first: no writes until decision points and branch conditions are fully mapped.
2. Require at least two independent evidence signals per target site (decompile ownership + runtime observation).

Rollback gate:

1. Full-file backup mandatory.
2. Per-site reversible manifest mandatory.
3. Tooling kill switch to disable this lane instantly.

## 5) Rollout Sequence

1. Stable-S1 (taxonomy), Stable-S2 (profile gate), Stable-S3 (stable preset formalization).
2. Stable-S4 (guard micro-patch) after variant fixture validation.
3. Stable-S5 (regression coverage) in parallel with Stable-S4.
4. Stable-S6 (cardid companion) to close extra-graphics need without high-risk exe mutation.
5. Keep Experimental-X1..X4 opt-in only; no default exposure.

## 6) Promotion and Freeze Criteria

Stable promotion requires all of:

1. Byte-verification gates A-E passing on canonical profile.
2. Backup/restore proven in at least one failure-injection test.
3. No unresolved doc drift in patch defaults/guard semantics.
4. Explicit signoff that UX warnings and rollback behavior are understandable.

Freeze triggers (immediate halt on lane):

1. Unexpected byte mismatch on supported profile.
2. Restore failure or non-deterministic post-restore state.
3. Runtime regression without reproducible rollback-safe boundary.
