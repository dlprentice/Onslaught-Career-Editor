# CFrontEnd__Init

> Address: 0x004662a0 | Source: `references/Onslaught/FrontEnd.cpp` | Line: ~179 (0xb3)

## Summary

Initializes the entire frontend menu system. This is a large function that:
1. Loads frontend resources with progress bar updates
2. Initializes all 24 frontend page (FEP) objects
3. Allocates player-specific frontend objects
4. Determines the initial page to display based on game state

## Signature

```c
// thiscall - ECX = CFrontEnd* this
int CFrontEnd__Init(CFrontEnd* this, int param_1, int param_2);
// Returns: 1 on success, 0 on failure
```

## Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| this (ECX) | CFrontEnd* | The frontend object being initialized |
| param_1 | int | Start mode (1 = from intro, 2 = from victory?) |
| param_2 | int | Progress bar mode (0 = slow, non-zero = fast) |

## Discovery

Found via xref to debug path string at 0x00629df0:
```
0x00466578: PUSH 0x629df0  ; "C:\dev\ONSLAUGHT2\FrontEnd.cpp"
```

The debug path is passed to a memory allocation function at line 179 (0xb3) for debug tracking.

## Key Operations

### 1. Progress Bar Initialization
```c
CConsole__SetLoading(1, 1, 0);  // Start loading-screen/progress tracking
if (param_2 == 0) {
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
    ptr = OID__AllocObject(0x178, 0x27, "C:\\dev\\ONSLAUGHT2\\FrontEnd.cpp", 0xb3);
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
| DAT_0066304c != -1 | 0x17 (23) | Direct level load via -level param |
| mFromOutro && no intro | 0x17 -> 0x0c | Return from victory |
| mFromOutro && intro | 0x17 -> 0x00 | Return to intro |
| param_1 == 2 | 0x17 -> 0x00 | From victory screen |
| param_1 == 1 | 0x17 -> varies | From intro |
| World 0x385-0x389 + dev/cheat | 0x08 | Special worlds with dev mode |
| World 0x385-0x389 no dev | timed to 0x08 | Timed transition |
| World 0x352-0x36f | 0x10 | Episode select range |
| Demo mode | 0x0c | Demo/intro start |
| Normal | 0x06 | Main menu |
| Normal + no dev/cheat | timed to 0x06 | Splash then main menu |

## Global Variables Used

| Address | Read/Write | Purpose |
|---------|------------|---------|
| g_bDevModeEnabled | R | Check for dev mode access |
| g_bAllCheatsEnabled | R | Check for all cheats |
| DAT_0066304c | R | Level override from -level param |
| DAT_00662f40 | R | Unknown init flag |
| DAT_00662dd0 | R | Demo/intro mode flag |
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
| 0x0044b060 | FUN_0044b060 | Unknown init |
| 0x0041bd00 | CCareer__Update | Career update |
| 0x004687e0 | FUN_004687e0 | Resource loading |
| 0x004fdc10 | FUN_004fdc10 | Resource loading |
| 0x00541240 | FUN_00541240 | Resource loading |
| 0x0040c640 | DebugTrace | Debug logging |
| 0x0044d320 | FUN_0044d320 | Unknown |
| 0x0055de9b | sprintf (`FUN_0055de9b`) | sprintf equivalent |
| 0x005490e0 | OID__AllocObject | Memory allocation |
| 0x005145f0 | FUN_005145f0 | Object constructor |
| 0x005159b0 | FUN_005159b0 | Unknown |
| 0x00466ae0 | CFrontEnd__SetPage | Page transition (`SetPage(page,time)`) |
| 0x00459810 | FUN_00459810 | Load level |
| 0x004e2c50 | CSoundManager__ReloadLanguageSampleBank | Conditional language sound-bank reload |
| 0x004f2150 | FUN_004f2150 | Loop init |
| 0x004f21f0 | FUN_004f21f0 | Loop body (5 iterations) |
| 0x004bb8c0 | FUN_004bb8c0 | Unknown (conditional) |

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
