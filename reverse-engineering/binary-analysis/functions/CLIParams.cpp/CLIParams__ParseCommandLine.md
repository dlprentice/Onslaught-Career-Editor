# CLIParams__ParseCommandLine

> Address: 0x00423bc0 | Source: `references/Onslaught/CLIParams.cpp` (`CCLIParams::GetParams(int num_parms, char **parms)`)

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** No
- **Verified vs Source:** Partially (retail differs from source)

## Purpose

Parses command-line arguments passed to BEA.exe. The retail PC port has a different set of parameters than Stuart's internal source code shows.

## Signature
```c
// TODO: Add verified retail signature (calling convention + class name differ from Stuart source).
// Source reference signature:
void CCLIParams::GetParams(int num_parms, char **parms);
```

## Parameter Parsing Logic

The function iterates through argv and uses string comparison to match parameters:

```c
// Pseudocode
for (int i = 1; i < argc; i++) {
    if (strcmp(argv[i], "-level") == 0) {
        g_startLevel = atoi(argv[++i]);
    }
    else if (strcmp(argv[i], "-skipfmv") == 0) {
        g_skipFMV = 1;
    }
    else if (strcmp(argv[i], "-forcewindowed") == 0) {
        if (DAT_00662f3e != 0) {  // GUARDED!
            g_forceWindowed = 1;
        }
    }
    // ... more parameters
}
```

## -forcewindowed Guard Flag

The windowed mode parameter is guarded by a global flag:

| Address | Symbol | File Offset | Value |
|---------|--------|-------------|-------|
| 0x00662f3e | DAT_00662f3e | 0x262F3E | Canonical Steam hash `74154bfa...` = **0x01** (historical variants with `0x00` reported) |

```c
// Guard check
if (DAT_00662f3e != 0) {
    g_forceWindowed = 1;
}
```

`-forcewindowed` parsing is guard-gated by this byte. In the canonical Steam hash used in this repo (`74154bfa...`), the byte is `0x01`; historical variants with `0x00` explain reports where parser gating blocked the parameter.

### How to Enable

If a variant has `0x262F3E = 0x00`, patch to `0x01` to allow parser processing of `-forcewindowed`.

See [windowed-mode-analysis.md](../../windowed-mode-analysis.md) for the full investigation into windowed mode.

## Verified Working Parameters

| Parameter | Type | Effect |
|-----------|------|--------|
| `-level N` | int | Skip to level N |
| `-skipfmv` | flag | No cutscenes |
| `-nomusic` | flag | Silence music |
| `-nosound` | flag | Silence all audio |
| `-res W H` | int int | Set resolution |
| `-showdebugtrace` | flag | Debug output |
| `-traceconsole` | flag | Console logging |

## Additional Parameters (Discovered Dec 2025)

| Parameter | Type | Effect |
|-----------|------|--------|
| `-e3` | flag | E3 demo mode (trade show build) |
| `-cardid` | flag | Force card identification mode |
| `-backbuffer2` | flag | Double backbuffer for rendering |
| `-timeout N` | int | Set timeout value |
| `-soundbuffers N` | int | Set number of sound buffers |
| `-autoconfigtest [path]` | string (optional) | Run auto-config test |
| `-testeur` | flag | Test mode (European QA flag?) |

See [_index.md](./_index.md) for detailed descriptions of each parameter.

## Notes
- Migrated from ghidra-analysis.md (Dec 2025)
- Retail binary has fewer parameters than source code suggests
- No `-GOD` parameter exists - god mode relies on save-name checks (B4K42 in source/internal; Maladim in PC port, no visible effect observed)
- The `-forcewindowed` parser path is guard-gated; baseline value depends on binary variant (`74154bfa...` uses `0x01`)
