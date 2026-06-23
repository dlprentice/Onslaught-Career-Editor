# CLI Goodie State Override Evidence - 2026-05-07

Status: public-safe implementation evidence, not runtime proof

## Objective

Expose AppCore's targeted copied-save Goodie state helper through the active C# CLI so the next Goodies 71-73 runtime wave can prepare copied saves repeatably without ad hoc byte edits.

## What Changed

- Added `--set-goodie-state INDEX:STATE` to the C# CLI.
- Accepted states are `0`, `1`, `2`, `3`, `locked`, `instructions`, `new`, and `old`.
- The command calls `BesFilePatcher.PatchGoodieStates`, which writes through the true-view Goodie table and preserves untouched slots.
- The command blocks in-place output through existing CLI path canonicalization.
- The command rejects broad patch, rank, kill, settings, options, or keybind overrides when `--set-goodie-state` is used, keeping this mode narrow for copied-save proof setup.

## Validation Summary

| Command | Result | What It Proves |
| --- | --- | --- |
| Pre-implementation CLI command with `--set-goodie-state 71:new 72:new 73:new` | Failed as expected | The option was not present before the patch. |
| `dotnet build OnslaughtCareerEditor.Cli\OnslaughtCareerEditor.Cli.csproj --nologo` | PASS | The active C# CLI builds after the new option and parser helpers. |
| `dotnet test OnslaughtCareerEditor.AppCore.Tests\OnslaughtCareerEditor.AppCore.Tests.csproj --nologo --filter PatchGoodieStates` | PASS, 2/2 | AppCore still proves the underlying targeted helper preserves neighboring slots and rejects invalid/reserved targets. |
| CLI command setting copied-save Goodies 71, 72, and 73 to `new` | PASS | The CLI can prepare a copied save through the AppCore helper. |
| CLI `--list-goodies` check of copied output | PASS | Slots 71, 72, and 73 changed to `NEW`; neighboring slots 70 and 74 remained `OLD`. |
| CLI command targeting reserved slot 233 | Failed as expected | Reserved/display-hidden Goodie slots are rejected by the helper. |
| CLI command combining `--set-goodie-state` with `--rank` | Failed as expected | The narrow proof setup mode does not silently combine with broad save patching. |
| CLI smoke command | PASS | The CLI help surface includes the new option and the command remains runnable. |
| Public release/docs/profile checks | PASS | The public-safe evidence note is included in release accounting and does not expose private assets or proof output. |

## Public-Safe Output Summary

The copied-output verification showed the intended five-slot neighborhood:

```text
70 OLD
71 NEW
72 NEW
73 NEW
74 OLD
```

Raw copied saves and full local paths stayed under ignored private `subagents/` output.

## Not Claimed

- This did not launch BEA.
- This did not mutate the installed game, installed save, or original executable.
- This does not prove Goodies 71-73 are visible or reachable at runtime.
- This does not prove hidden/non-grid Goodies behavior.
- This does not authorize broad save synthesis; all future runtime proof must still copy a valid baseline first.

## Next Step

Use this CLI helper in a copied-profile runtime proof wave to test whether forcing only Goodies 71-73 to visible save states changes normal Goodies wall behavior.
