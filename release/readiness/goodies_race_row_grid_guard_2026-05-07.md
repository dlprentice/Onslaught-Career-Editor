# Goodies Race-Row Grid Guard - 2026-05-07

Status: public-safe static/AppCore guard

## Objective

Make the known Goodies top-row gap explicit in automated tests instead of relying on prose or broad mapping coverage.

## What Changed

Added an AppCore test named:

```text
GoodieWallGridMappingService_RaceRowSkipsHiddenGoodiesToDeveloperItems
```

It asserts the row-1 x-coordinate sequence from the race-level entries through the next developer item is:

```text
66, 67, 68, 69, 70, 74
```

and explicitly excludes 71, 72, and 73 from that normal coordinate path.

## Validation

Command:

```powershell
dotnet test OnslaughtCareerEditor.AppCore.Tests\OnslaughtCareerEditor.AppCore.Tests.csproj --nologo --filter GoodieWallGridMappingService_RaceRowSkipsHiddenGoodiesToDeveloperItems
```

Result: PASS, 1/1.

Follow-up gate summary:

- Full AppCore tests: PASS, 83/83.
- Release manifest/profile generation and checks: PASS.
- Markdown links, documented commands, docsync, public allowlist, and repo hygiene: PASS.
- State JSON parse and whitespace diff checks: PASS.
- `BEA.exe` process check: PASS, no matching process was running.

## Not Claimed

- This is not runtime proof.
- This does not prove hidden/non-grid Goodies 71-73 are unreachable.
- This does not prove the runtime input harness can always reproduce the edge-scroll sequence.
- This does not mutate any game file, save file, Ghidra project, or runtime process.
