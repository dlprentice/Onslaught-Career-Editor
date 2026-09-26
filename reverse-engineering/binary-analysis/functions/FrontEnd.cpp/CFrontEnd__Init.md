# CFrontEnd__Init

Status: mixed — inherited function reference with scoped startup-selector corrections
Last updated: 2026-09-26 (0x00459810 renamed CFEPDevSelect__SetCurrentCard by the RE audit)
Summary: frontend initialization reference; distinguish developer selection and the separate startup selector from command-line level parsing.
Source File: `references/Onslaught/FrontEnd.cpp` at `5352a81cdb838b145a57f7febc5d9fc4b0129ebb` | Binary: pristine BEA.exe.original.backup, SHA-256 74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750

> Address: 0x004662a0 | Source: `references/Onslaught/FrontEnd.cpp` | Line: ~179 (0xb3)

## Selector correction — September 19

The read at `00466775` uses CLIParams `+18` (`00662dd0`), the cross-subsystem
developer selector. It is not frontend state or a demo/intro flag. Its
nonzero branch at `0046678b` changes first-run page selection; source
`FrontEnd.cpp`:188–203 names the corresponding developer-mode condition.
The [CLI owner](../CLIParams.cpp/CLIParams__ParseCommandLine.md#developer-selector-and-trace-consumers--september-19)
records the other consumers and evidence limits.

The separate reads at `004665e0/00466618` concern `0066304c` (CLIParams `+294`),
not the `-level` destination at `00662dc8` (`+10`). This branch sets active
page `0x17`, calls `00466ae0(0,0)`, and passes the separate selector to
`00459810`. Do not translate the old "direct level load via -level" label
into rebuild behavior. These corrections do not revalidate the other inherited
page names or the complete initialization routine. Complete body bytes and
disassembly are retained in the CLI private owner as `consumer-004662a0.*`.

## Name corrections — 2026-07-28

Superseded in place against `ghidra-function-name-table-2026-07-27.tsv`, the
2026-07-27 headless export of the live maintainer Ghidra project. The evidence
grade, and the limits of what a corrected name does and does not establish, are
stated once at [the area index](../_index.md#the-name-corrections-of-2026-07-28).
Old cell text is quoted below rather than deleted, so a reader who remembers the
withdrawn label can tell it was corrected and not lost.

| Address | Superseded label | Current name | Correction |
| --- | --- | --- | --- |
| `0x0044b060` | `FUN_0044b060` | `CEventManager__Init` | placeholder replaced; this address carries a name now |
| `0x0044d320` | `FUN_0044d320` | `CFrontEnd__InitPageStateDefaults` | placeholder replaced; this address carries a name now |
| `0x00459810` | `FUN_00459810` | `CFEPDevSelect__SetCurrentCard` | placeholder replaced; renamed by the 2026-09-26 RE audit |
| `0x004687e0` | `FUN_004687e0` | `CFrontEnd__LoadSharedResources` | placeholder replaced; this address carries a name now |
| `0x004bb8c0` | `FUN_004bb8c0` | `CMusic__PlaySelection` | placeholder replaced; this address carries a name now |
| `0x004f2150` | `FUN_004f2150` | `CText__Ctor` | placeholder replaced; this address carries a name now |
| `0x004f21f0` | `FUN_004f21f0` | `CText__Init` | placeholder replaced; this address carries a name now |
| `0x004fdc10` | `FUN_004fdc10` | `SharedVFunc__ReturnTrue_004fdc10` | placeholder replaced; the 2026-07-28 `CFrontEndPage__Init_ReturnTrue` reading was itself withdrawn on 2026-08-17 (see below) |
| `0x005145f0` | `FUN_005145f0` | `CController__ctor` | placeholder replaced; this address carries a name now |
| `0x005159b0` | `FUN_005159b0` | `PlatformInput__ResetKeyStateTables` | placeholder replaced; this address carries a name now |
| `0x00541240` | `FUN_00541240` | `CDXFrontEndVideo__SetDefaultSize` | placeholder replaced; this address carries a name now |
| `0x005490e0` | `OID__AllocObject` | `CDXMemoryManager__Alloc` | class prefix and suffix both moved |

Where a row's **suffix** moved rather than only its class prefix, the behavioural
text beside it in this note was written for the old name. This sweep corrected
names against the export and re-derived no behaviour, so read any such gloss as
unverified against the new name until it is re-measured.

## Name correction — 2026-08-17

One row above was corrected again. `0x004fdc10` had been read as
`CFrontEndPage__Init_ReturnTrue`, a FrontEnd-exclusive page initializer. The
2026-08-17 name cohort
([`name-cohort-promotion-manifest-2026-08-17.tsv`](../../name-cohort-promotion-manifest-2026-08-17.tsv))
counted the references and found **36 data references spread over 36 distinct
vtable classes** — the address is a shared `return 1` stub reused image-wide,
and FrontEnd exclusivity is refuted. It is now
`SharedVFunc__ReturnTrue_004fdc10`.

This matters beyond the name: the "Called Functions" table below listed this
address with the purpose `Resource loading`. That gloss is withdrawn, not
reworded. A stub that 35 other classes also point at cannot be doing
FrontEnd resource loading, and what `CFrontEnd__Init` gains by calling it is
no longer claimed here.

---

## Summary

Initializes the entire frontend menu system. This is a large function that:
1. Loads frontend resources with progress bar updates
2. Initializes all 24 frontend page (FEP) objects
3. Allocates player-specific frontend objects
4. Determines the initial page to display based on game state

## Signature

```c
// thiscall - ECX = CFrontEnd* this
int CFrontEnd__Init(CFrontEnd* this, int entry, int in_loaded_system);
// Returns: 1 on success, 0 on failure
```

## Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| this (ECX) | CFrontEnd* | The frontend object being initialized |
| entry | int | Source-bridged `EFrontEndEntry` value passed into `CFrontEnd::Init` |
| in_loaded_system | int | Source-bridged loaded-system/loading-range split flag |

Wave467 hardened this saved Ghidra signature/comment from retail stack use plus source `CFrontEnd::Init(EFrontEndEntry, BOOL)`. Runtime initial-page behavior, exact enum values, concrete layout, and rebuild parity remain unproven.

## Discovery

Found via xref to debug path string at 0x00629df0:
```
0x00466578: PUSH 0x629df0  ; "[maintainer-local-source-export-root]\FrontEnd.cpp"
```

The debug path is passed to a memory allocation function at line 179 (0xb3) for debug tracking.

## Key Operations

### 1. Progress Bar Initialization
```c
CConsole__SetLoading(1, 1, 0);  // Start loading-screen/progress tracking
if (in_loaded_system == 0) {
    CConsole__SetLoadingRange(0, 25.0f);   // Slow progress: 0% to 25%
} else {
    CConsole__SetLoadingRange(50.0f, 62.5f);  // Fast progress: 50% to 62.5%
}
```

### 2. Career Update
```c
CCareer__Update(&g_Career);  // Update career progress
```

### 3. Resource Loading (with failure checks)
```c
if (FUN_004687e0() == 0) return 0;  // Load resources
if (FUN_004fdc10() == 0) return 0;  // Load more resources
if (FUN_00541240() == 0) return 0;  // Load more resources
```

### 4. Page Pointer Initialization
The function initializes 24 page pointers, first setting all to a null page:
```c
// Initialize all 24 pointers to null page at this+0xbe04
for (int i = 0; i < 24; i++) {
    this->mPages[i] = this + 0xbe04;
}
// Then set specific page objects
this->mPages[0] = this + 0x278;   // FEPage 0
this->mPages[1] = this + 0x29c;   // FEPage 1
// ... etc for all 24 pages
```

### 5. Page Object Initialization Loop
```c
for (int i = 0; i < 24; i++) {
    sprintf(buffer, "FEP %d...", i);  // Debug: "FEP 0...", "FEP 1...", etc.
    DebugTrace(buffer);              // Log message
    result &= mPages[i]->vtable->Init();  // Call page's Init method
    DebugTrace("done.");             // Log completion
    CConsole__SetLoadingFraction(i * 0.041666668f);    // Update progress (i/24)
}
if (result == 0) return 0;
```

### 6. Player Object Allocation
```c
for (int i = 0; i < 2; i++) {  // Two players
    ptr = OID__AllocObject(0x178, 0x27, "[maintainer-local-source-export-root]\\FrontEnd.cpp", 0xb3);
    if (ptr != NULL) {
        this->field_0xbe0c[i] = FUN_005145f0(this, i, 1);
    } else {
        this->field_0xbe0c[i] = NULL;
    }
}
```

### 7. Initial Page Selection
Complex logic determines which page to show first:

| Condition | Page Set | Notes |
|-----------|----------|-------|
| DAT_0066304c != -1 | 0x17, then `SetPage(0,0)` | Separate startup selector; not the parser's `-level` field (September 19 correction above) |
| mFromOutro && no intro | 0x17 -> 0x0c | Return from victory |
| mFromOutro && intro | 0x17 -> 0x00 | Return to intro |
| entry == 2 | 0x17 -> 0x00 | From victory screen |
| entry == 1 | 0x17 -> varies | From intro |
| World 0x385-0x389 + dev/cheat | 0x08 | Special worlds with dev mode |
| World 0x385-0x389 no dev | timed to 0x08 | Timed transition |
| World 0x352-0x36f | 0x10 | Episode select range |
| Demo mode | 0x0c | Demo/intro start |
| Normal | 0x06 | Main menu |
| Normal + no dev/cheat | timed to 0x06 | Splash then main menu |

## Global Variables Used

| Address | Read/Write | Purpose |
|---------|------------|---------|
| CLIParams `+3c` (`00662df4`; legacy `g_bDevModeEnabled`) | R | Autoconfig-test flag; also bypasses cheat queries. Distinct from `+18` developer selection. |
| g_bAllCheatsEnabled | R | Check for all cheats |
| DAT_0066304c | R | Separate CLIParams `+294` startup selector; `-level` writes `+10` instead |
| DAT_00662f40 | R | Unknown init flag |
| DAT_00662dd0 | R | CLIParams `+18` developer selector; see September 19 correction |
| DAT_00662dcc | R | Unknown flag |
| DAT_0083d448 | R | Demo state |
| DAT_0083d454 | R | Playable demo flag |
| DAT_006630cc | R | Special mode flag |
| DAT_008a9ab4 | W | Set to 1 after init |
| DAT_008a9580 | W | Set during some transitions |
| DAT_008a9584 | W | Set during some transitions |
| DAT_008a9aac | W | Cleared to 0 |

## Called Functions

| Address | Name | Purpose |
|---------|------|---------|
| 0x0042bbc0 | CConsole__SetLoading | Loading-screen/progress enable-disable control |
| 0x0042cf40 | CConsole__SetLoadingRange | Progress bar range |
| 0x0042cf70 | CConsole__SetLoadingFraction | Progress bar value |
| 0x0044b060 | CEventManager__Init | Unknown init |
| 0x0041bd00 | CCareer__Update | Career update |
| 0x004687e0 | CFrontEnd__LoadSharedResources | Resource loading |
| 0x004fdc10 | SharedVFunc__ReturnTrue_004fdc10 | **`Resource loading` withdrawn.** Measured 2026-08-17: 36 data references from 36 distinct vtable classes. It is a shared `return 1` stub, not a FrontEnd-owned initializer, and no resource-loading purpose survives the measurement. |
| 0x00541240 | CDXFrontEndVideo__SetDefaultSize | Resource loading |
| 0x0040c640 | DebugTrace | Debug logging |
| 0x0044d320 | CFrontEnd__InitPageStateDefaults | Unknown |
| 0x0055de9b | sprintf (`FUN_0055de9b`) | sprintf equivalent |
| 0x005490e0 | CDXMemoryManager__Alloc | Memory allocation |
| 0x005145f0 | CController__ctor | Object constructor |
| 0x005159b0 | PlatformInput__ResetKeyStateTables | Unknown |
| 0x00466ae0 | CFrontEnd__SetPage | Page transition (`SetPage(page,time)`) |
| 0x00459810 | CFEPDevSelect__SetCurrentCard | Sets the device-select card when the CLI device-select field is not -1 (`FrontEnd.cpp:178-186`) |
| 0x004e2c50 | CSoundManager__ReloadLanguageSampleBank | Conditional language sound-bank reload |
| 0x004f2150 | CText__Ctor | Loop init |
| 0x004f21f0 | CText__Init | Loop body (5 iterations) |
| 0x004bb8c0 | CMusic__PlaySelection | Unknown (conditional) |

## Callers

| Address | Function | Context |
|---------|----------|---------|
| 0x004684ef | CFrontEnd__Run | Main frontend loop |

## Notes

1. **Two-Player Support**: Allocates objects for 2 players at offset 0xbe0c
2. **Exception Handling**: Uses SEH (Structured Exception Handling) with unwind at 0x005d2730
3. **Progress Bar**: Uses floating-point hex values (e.g., 0x41c80000 = 25.0f, 0x42c80000 = 100.0f)
4. **World ID Checks**: Special handling for ranges 0x352-0x36f and 0x385-0x389

## Hex Float Constants

| Hex | Float | Usage |
|-----|-------|-------|
| 0x41c80000 | 25.0 | Progress 25% |
| 0x42480000 | 50.0 | Progress 50% |
| 0x427a0000 | 62.5 | Progress 62.5% |
| 0x42a00000 | 80.0 | Progress 80% |
| 0x42b40000 | 90.0 | Progress 90% |
| 0x42be0000 | 95.0 | Progress 95% |
| 0x42c80000 | 100.0 | Progress 100% |
| 0xc2c80000 | -100.0 | Unknown (stored at 0xbe20) |
