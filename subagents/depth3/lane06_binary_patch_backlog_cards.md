# Lane 06 - Binary Patch Backlog Cards (Stable vs Experimental)

Date: 2026-03-04
Source conversion: `subagents/depth2/lane06_binary_patch_gap_findings.md`

## Card Summary

| Card ID | Track | Confidence | Opportunity Theme | Primary Blocker |
|---|---|---|---|---|
| `BP-S-001` | Stable | High (0.93) | Explicit stable vs experimental taxonomy in docs/UI/script help | Needs owner signoff on labels/default visibility |
| `BP-S-002` | Stable | High (0.91) | Hash/profile-aware patch targeting (canonical + known variants) | Need governance for variant allowlist and override policy |
| `BP-S-003` | Stable | High (0.90) | Optional `-forcewindowed` guard normalization compatibility patch (`0x262F3E`) | Canonical binary already has `0x01`; requires variant fixtures |
| `BP-S-004` | Stable | High (0.89) | Formalize current 3-offset display lane as `Stable Track A-minimal` preset | Requires agreed behavior matrix and user-facing wording |
| `BP-S-005` | Stable | Medium-High (0.82) | Cross-stack regression coverage for verify/apply/restore and script mode flags | WPF/script test harness gaps |
| `BP-S-006` | Stable (Companion) | High (0.88) | `cardid.txt` managed preset/merge flow for extra-graphics unlock toggles | Safe merge rules for existing user/vendor lines |
| `BP-X-001` | Experimental | Medium (0.64) | 28-region widescreen code-cave track as an explicit patch lane | Regression risk across FOV/UI/render paths |
| `BP-X-002` | Experimental | Medium (0.58) | Expand startup fullscreen bypass beyond `0x12BB97` | Additional byte targets not fully mapped/validated |
| `BP-X-003` | Experimental | Low-Medium (0.47) | Force `ALLOW_WIDESCREEN_MODES` default-on behavior in binary | Initializer and side effects not fully proven |
| `BP-X-004` | Experimental | Low (0.31) | Binary `cardid`/extra-graphics gate bypass and forced unlock path | Retail gate decision points still unmapped |

## Stable Track Cards

### `BP-S-001` - Canonical Stable/Experimental Taxonomy

- Opportunity: Convert current mixed labels (`Supported`, `DEV MODE ONLY`, `Archived`) into explicit `Stable` and `Experimental` classes across script help, WPF/PyQt labels, and docs.
- Confidence: High (0.93).
- Primary blocker: Product/owner signoff on default visibility and warning verbosity for experimental cards.
- Rollback requirements:
- Keep this card implementation docs/UI-only (no binary delta).
- One-step rollback by reverting taxonomy strings and section headers.
- Preserve current default patch behavior exactly during taxonomy rollout.

### `BP-S-002` - Hash/Profile-Aware Targeting

- Opportunity: Add profile manifests keyed by executable hash (canonical Steam + approved variants) so verify/apply paths are explicit about supported targets.
- Confidence: High (0.91).
- Primary blocker: Need explicit policy for unknown hash handling (`block`, `warn`, `manual override`).
- Rollback requirements:
- Feature flag strict profile enforcement so fallback mode can be re-enabled immediately.
- Preserve existing offset byte-verification logic as fallback path.
- Revert manifest-only changes without modifying target binaries.

### `BP-S-003` - Compatibility Guard Patch for `-forcewindowed`

- Opportunity: Surface an optional compatibility patch for variant binaries where guard byte `0x262F3E` is `0x00` (`00 -> 01`), while no-op on canonical `0x01`.
- Confidence: High (0.90).
- Primary blocker: Need known-variant fixture binaries to test true-positive and no-op behavior.
- Rollback requirements:
- Record original byte value before apply and restore exactly that value.
- Keep this as separate toggle (never forced by default preset).
- Require preflight backup before first write.

### `BP-S-004` - Stable Track A-Minimal Preset Hardening

- Opportunity: Package the existing 3 offsets (`0x129696`, `0x12A644`, optional `0x12BB97`) into an explicit stable preset with documented expected outcomes and limits.
- Confidence: High (0.89).
- Primary blocker: Need signoff on expected-behavior matrix for startup/windowed outcomes across environments.
- Rollback requirements:
- Apply only byte-verified writes (abort on mismatch).
- Preserve single restore path using canonical backup (`BEA.exe.original.backup`).
- Keep optional patch 3 isolated so rollback can remove only that gate tweak.

### `BP-S-005` - Stable Regression Coverage Expansion

- Opportunity: Add automated coverage for WPF patch flows and script-mode flags (`--resolution-only`, `--windowed-only`, `--skip-auto-toggle`) to align with Python core depth.
- Confidence: Medium-High (0.82).
- Primary blocker: Existing WPF/UI automation depth and script harness setup are limited.
- Rollback requirements:
- Tests only; no production patch bytes changed.
- Gate new tests behind deterministic fixtures to avoid flaky CI regressions.
- If unstable, disable added tests without touching runtime patch logic.

### `BP-S-006` - `cardid.txt` Companion Unlock Lane (Non-Binary)

- Opportunity: Add managed `cardid.txt` preset generation/merge with backup/restore to expose extra-graphics unlock toggles (`GEFORCE_FX_POWER`, `SRT_ENABLE`, `IMPOSTOR_ENABLE`, `LANDSCAPE_LIGHTING`) without risky exe mutation.
- Confidence: High (0.88).
- Primary blocker: Merge precedence and duplicate-key behavior for existing user card profiles.
- Rollback requirements:
- Always write `cardid.txt` backup before merge.
- Provide one-click restore of original `cardid.txt`.
- Preserve unknown lines and comments byte-for-byte on merge where possible.

## Experimental Track Cards

### `BP-X-001` - Widescreen 28-Region Code-Cave Patch Lane

- Opportunity: Productize the mapped 28-region widescreen diff as an explicit experimental lane with deterministic apply/verify/restore.
- Confidence: Medium (0.64).
- Primary blocker: High runtime regression surface (render, HUD, FOV, cutscenes, and mission-specific camera behavior).
- Rollback requirements:
- Enforce full binary backup before first region write.
- Require per-region before/after byte checks and abort on first mismatch.
- Ship behind explicit experimental acknowledgement + tested-hash allowlist.

### `BP-X-002` - Additional Startup Fullscreen Gate Mapping

- Opportunity: Extend startup flow patching beyond `0x12BB97` by mapping and optionally patching additional fullscreen re-entry gates.
- Confidence: Medium (0.58).
- Primary blocker: Additional target offsets and branch semantics are not yet finalized with runtime proof.
- Rollback requirements:
- Stage as independent micro-patches (one gate per toggle).
- Require smoke test matrix before enabling any gate in presets.
- Support per-gate rollback without removing stable base patches.

### `BP-X-003` - Binary Default-On for `ALLOW_WIDESCREEN_MODES`

- Opportunity: Reduce config friction by forcing widescreen cvar default-on in executable startup path.
- Confidence: Low-Medium (0.47).
- Primary blocker: Incomplete evidence for initializer/write sites and interactions with existing config load order.
- Rollback requirements:
- Restrict to explicit experimental build profile.
- Snapshot and restore related config/cvar bytes touched by patch.
- Provide hard disable toggle that reverts to unpatched startup defaults.

### `BP-X-004` - Binary `cardid`/Extra-Graphics Gate Bypass

- Opportunity: Introduce direct binary unlock path for cardid-gated extra graphics features (beyond `cardid.txt` companion flow).
- Confidence: Low (0.31).
- Primary blocker: Retail gate decision points and safe patch targets are currently unmapped; side effects unknown.
- Rollback requirements:
- Discovery-first gate: no writes until all target sites have read-back evidence and branch ownership proof.
- Full-file backup plus per-site reversible byte manifests required.
- Runtime kill switch required in tooling to disable experimental cardid bypass immediately.

## Prioritization Cut

1. Execute stable cards first in this order: `BP-S-001`, `BP-S-002`, `BP-S-004`, `BP-S-003`, `BP-S-005`, `BP-S-006`.
2. Hold experimental cards behind explicit opt-in and separate QA budget.
3. Treat `BP-S-006` as the near-term `cardid`/extra-graphics unlock opportunity; treat `BP-X-004` as long-horizon research until gate mapping matures.
