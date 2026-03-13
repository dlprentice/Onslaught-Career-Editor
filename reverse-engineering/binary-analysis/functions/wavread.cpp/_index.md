# wavread.cpp - WAV File Reader

**Source File:** `C:\dev\ONSLAUGHT2\wavread.cpp`
**Debug String Address:** `0x0063d1b0`
**Function Address Range:** `0x00505210` - `0x00505570`

## Overview

WAV file reader implementation for loading audio files. Parses RIFF WAVE format using Windows Multimedia I/O (mmio) functions. Part of the sound system for loading sound effects and music.

## Class: CWaveSoundRead

A class for reading WAV audio files. Uses Windows mmio API for buffered file I/O.

### Vtable Location

`0x005dfc4c` - CWaveSoundRead vtable

## Functions (7 total)

| Address | Name | Purpose |
|---------|------|---------|
| `0x00505210` | `WavRead__ReadMMIO` | Parse RIFF WAVE header and format chunk |
| `0x005053d0` | `WavRead__WaveReadFile` | Read PCM audio data from file |
| `0x005054a0` | `CWaveSoundRead__Constructor` | Initialize CWaveSoundRead instance |
| `0x005054e0` | `CWaveSoundRead__Destructor` | Destroy CWaveSoundRead and free resources |
| `0x00505500` | `CWaveSoundRead__Close` | Close mmio handle and free format buffer |
| `0x00505570` | `CWaveSoundRead__BaseConstructor` | Base class constructor (sets vtable) |
| `0x005055b0` | `CWaveSoundRead__Open` | Open WAV file and locate data chunk |

## Function Details

### WavRead__ReadMMIO (0x00505210)

Parses RIFF WAVE file header structure.

**Signature:** `HRESULT ReadMMIO(HMMIO hmmio, MMCKINFO* pckInfoRIFF, WAVEFORMATEX** ppwfxInfo)`

**Operations:**
1. Calls `mmioDescend()` to enter RIFF chunk
2. Validates RIFF header (`0x46464952` = "RIFF") and WAVE type (`0x45564157` = "WAVE")
3. Searches for "fmt " chunk (`0x20746d66`)
4. Reads WAVEFORMATEX structure (minimum 16 bytes)
5. Handles both PCM (format tag 1) and extended formats
6. Allocates memory for format structure via `OID__AllocObject` (memory allocator)

**Return Values:**
- `0` (S_OK) - Success
- `0x80004005` (E_FAIL) - Failure (invalid format, read error, etc.)

**RIFF Chunk IDs:**
- `0x46464952` = "RIFF"
- `0x45564157` = "WAVE"
- `0x20746d66` = "fmt "
- `0x61746164` = "data"

### WavRead__WaveReadFile (0x005053d0)

Reads raw PCM audio data from the WAV file.

**Signature:** `HRESULT WaveReadFile(HMMIO hmmio, UINT cbRead, BYTE* pbDest, MMCKINFO* pckInfo, UINT* pcbActualRead)`

**Operations:**
1. Gets mmio buffer info via `mmioGetInfo()`
2. Reads data byte-by-byte from mmio buffer
3. Calls `mmioAdvance()` when buffer exhausted
4. Updates bytes remaining in chunk
5. Restores mmio state via `mmioSetInfo()`

### CWaveSoundRead__Open (0x005055b0)

Opens a WAV file for reading.

**Signature:** `HRESULT Open(const char* filename)` (thiscall)

**Operations:**
1. Frees any existing format buffer
2. Converts filename (calls `FUN_004f7c70`)
3. Opens file with `mmioOpenA(filename, NULL, MMIO_READ)`
4. Calls `WavRead__ReadMMIO()` to parse format
5. Seeks to data chunk start
6. Descends into "data" chunk (`0x61746164`)

**Object Layout (ECX = this):**
- `+0x04` - WAVEFORMATEX* format pointer
- `+0x08` - HMMIO file handle
- `+0x0C` - MMCKINFO for data chunk
- `+0x20` - MMCKINFO for RIFF chunk
- `+0x2C` - Data offset

### CWaveSoundRead__Close (0x00505500)

Closes the WAV file and releases resources.

**Operations:**
1. Sets vtable pointer
2. Calls `mmioClose()` on file handle
3. Frees format buffer via `OID__FreeObject`
4. Clears format pointer

### CWaveSoundRead__Constructor (0x005054a0)

Initializes a new CWaveSoundRead instance.

**Operations:**
1. Sets vtable to `PTR_FUN_005dfc4c`
2. Clears format pointer to 0

### CWaveSoundRead__Destructor (0x005054e0)

Destroys CWaveSoundRead instance.

**Operations:**
1. Calls `CWaveSoundRead__Close()`
2. Optionally frees memory (if flag bit 0 set)

### CWaveSoundRead__BaseConstructor (0x00505570)

Base class constructor variant.

**Operations:**
1. Sets vtable to `PTR_LAB_005dfc6c` (base class vtable)

## Windows API Usage

| Function | Purpose |
|----------|---------|
| `mmioOpenA` | Open multimedia file |
| `mmioClose` | Close multimedia file |
| `mmioRead` | Read from multimedia file |
| `mmioDescend` | Descend into RIFF chunk |
| `mmioAscend` | Ascend from RIFF chunk |
| `mmioSeek` | Seek in multimedia file |
| `mmioGetInfo` | Get mmio buffer info |
| `mmioSetInfo` | Set mmio buffer info |
| `mmioAdvance` | Advance mmio buffer |

## WAV File Format Reference

```
RIFF chunk ('RIFF')
  |- Format type ('WAVE')
  |- Format chunk ('fmt ')
  |    |- WAVEFORMATEX structure
  |- Data chunk ('data')
       |- Raw PCM samples
```

## Related Systems

- **Sound System** - Uses CWaveSoundRead for loading sound effects
- **Music System** - May use for music playback (though OGG is more common)
- **Memory Manager** - `OID__AllocObject` / `OID__FreeObject` for allocation/free

## Discovery Notes

- Only 2 xrefs to debug path string, both within `WavRead__ReadMMIO`
- Functions contiguous in address space (0x00505210-0x00505570)
- Vtable at 0x005dfc4c contains 8 function pointers
- Standard DirectX SDK pattern for WAV reading (similar to DXUtil samples)
