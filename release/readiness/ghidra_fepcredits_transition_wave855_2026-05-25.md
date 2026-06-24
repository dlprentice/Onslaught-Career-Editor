# Ghidra FEPCredits Transition Wave855 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-25
Scope: `fepcredits-transition-wave855`

Wave855 FEPCredits transition saved a comment/tag treatment for `0x0051a970 CFEPCredits__TransitionNotification` after serialized headless dry/apply/read-back with the `fepcredits-transition-wave855` and `wave855-readback-verified` tags. The pass made no renames, no signature changes, no function-boundary changes, and no executable-byte changes.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x0051a970 CFEPCredits__TransitionNotification` | FE credits-page transition-notification vtable slot 6. DATA xref `0x005db898` in CFEPCredits vtable `0x005db880` points to the body. |
| Body behavior | Reads platform time through `PLATFORM__GetSysTimeFloat`, adds the `0x005d8ba0` float transition delay, stores the result at `this+0x04`, calls `CMusic__PlaySelection(&DAT_00889a48, 1, 1)`, clears the credits-complete flag at `this+0x08`, ignores `from_page`, and returns with `RET 0x4`. |
| Lifecycle context | Complements `CFEPCredits__Render`, which sets `this+0x08` when `CCredits__RenderCredits` finishes, plus `CFEPCredits__Process/ButtonPressed`, which return to page `0x11` and resume frontend music. |

Read-back evidence:

- `ApplyFEPCreditsTransitionWave855.java dry`: `updated=0 skipped=1 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=1 missing=0 bad=0`
- `ApplyFEPCreditsTransitionWave855.java apply`: `updated=1 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=1 missing=0 bad=0`
- `ApplyFEPCreditsTransitionWave855.java final dry`: `updated=0 skipped=1 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`
- Post exports: `1` metadata row, `1` tag row, `1` xref row, `81` instruction rows, `1` decompile row, `10` context metadata rows, `10` context decompile rows, and `9` vtable slot rows.
- Queue after Wave855: `6098` total functions, `5756` commented, `342` commentless, `0` exact-undefined signatures, `0` `param_N` signatures, comment-backed proxy `5756/6098 = 94.39%`, strict clean-signature proxy `5756/6098 = 94.39%`.
- Next raw commentless row: `0x0051aa90 CFEPDirectory__Init`.
- Commentless high-signal, signature, and name-confidence queues remain empty.
- Verified backup: `G:\GhidraBackups\BEA_20260525-110750_post_wave855_fepcredits_transition_verified`, `19` files, `172166023` bytes, `DiffCount=0`.

What this proves:

- The target function row exists in the saved Ghidra project.
- The saved signature remains `void __fastcall CFEPCredits__TransitionNotification(void * this, int from_page)`.
- The saved comment and tags include `fepcredits-transition-wave855` and `wave855-readback-verified`.
- The observed static behavior is a FE credits-page lifecycle transition hook: reset timing, start the credits music selection, and clear the completion flag.
- This is important connective/static frontend infrastructure even though source-file evidence is sparse.

What remains unproven:

- Exact `CFEPCredits` layout.
- Exact music-track semantics.
- Runtime frontend behavior.
- Source identity.
- BEA patching behavior.
- Rebuild parity.
