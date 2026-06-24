# Binary Patch Expansion Plan

## Stable Lane (Current)
- `resolution_gate` (stable)
- `force_windowed` (stable)
- `skip_auto_toggle` (experimental optional)

All three are now centralized in `patches/catalog/patches.v2.json` and consumed by both app stacks.

## Expansion Gate
New patches are eligible for catalog promotion only when all are true:
1. Deterministic byte location(s) with expected original/patched bytes.
2. Evidence references in canonical RE docs for behavior claims.
3. Rollback strategy and verification probe are specified.
4. Runtime matrix validation exists for at least one baseline hardware profile.

## Deferred Candidates (Bounded)
1. Additional feature-gate bypasses (for example extra-graphics pathways) pending byte-level confirmation and safety analysis.
2. Deeper startup/render call-flow interventions pending wrapper-first closure and compatibility matrix.
3. Legacy-to-modern call translation interventions remain experimental-only until staged runtime confidence is established.

## Catalog Process
- Add candidate in `patches/catalog/patches.v2.json`.
- Run verify/apply/restore tests on disposable executable copy.
- Update docs and app UI wording in same change window.
- Re-run C# + Python regression gates and policy gates before closing.
