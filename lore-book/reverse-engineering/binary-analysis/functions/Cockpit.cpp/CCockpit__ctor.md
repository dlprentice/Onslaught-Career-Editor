# CCockpit__ctor

> Address: `0x004244b0` | Source family: `CCockpit`

## Status

- Saved Ghidra name/signature/comment: yes, Wave 321
- Saved signature: `void * __thiscall CCockpit__ctor(void * this, void * battleEngine)`
- Runtime cockpit proof: not yet
- Exact Stuart-source method identity: not yet

## Summary

Constructor-like body reached from `CBattleEngine__Init` after cockpit object allocation. The callsite shows `ECX` as the destination object and one explicit stack argument for the owning BattleEngine pointer, so the older saved signature with a phantom extra parameter was corrected.

The body stores the owner at `this + 0x110`, initializes cockpit matrix/state fields, resolves animation/resource context, schedules event `0x7d1`, and returns `this`.

## Wave988 Read-Only Check

Wave988 (`cockpit-lifecycle-review-wave988`) re-reviewed `0x004244b0 CCockpit__ctor` with the adjacent lifecycle rows `0x00405970 CDXCockpit__scalar_deleting_dtor`, `0x00405990 CDXCockpit__dtor_base_thunk`, `0x00424710 CCockpit__scalar_deleting_dtor`, and `0x00424730 CCockpit__dtor_base`. Fresh metadata/tag/xref/instruction/decompile/vtable exports kept the saved constructor name/signature coherent and tied the callsite to `0x00404dd0 CBattleEngine__Init` at `0x004055dc`.

Queue closure remains `6222/6222 = 100.00%`. Wave911 focused re-audit progress is `436/1408 = 30.97%`; expanded static surface progress is `502/1478 = 33.96%`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260531-031646_post_wave988_cockpit_lifecycle_review_verified`.

## Boundaries

- This is saved static Ghidra metadata and read-back evidence only.
- It does not prove exact `CCockpit` layout, local names, tags, runtime HUD/cockpit behavior, or rebuild parity.
- It does not launch, patch, or mutate `BEA.exe`.
