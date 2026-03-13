# DXMemBuffer.cpp Function Mappings

> Binary-to-source function mappings for DXMemBuffer.cpp
> Last updated: 2025-12-16

## Overview

DXMemBuffer is a buffered file I/O class for DirectX applications. It provides:
- Buffered reading and writing to files
- Optional zlib compression/decompression for data files
- Line-by-line text reading with CR/LF handling
- Memory allocation via OID system

**Debug Path:** `C:\dev\ONSLAUGHT2\DXMemBuffer.cpp` at 0x00650fd0

## Class Structure

```cpp
// Estimated CDXMemBuffer class layout (0x130 bytes / 76 DWORDs)
class CDXMemBuffer {
    /* 0x00 */ HANDLE  mFileHandle;      // Windows file handle
    /* 0x04 */ void*   mBuffer;          // Allocated memory buffer
    /* 0x08 */ void*   mCurrentPos;      // Current read/write position in buffer
    /* 0x0C */ void*   mChecksumTable;   // Checksum verification data (read mode)
    /* 0x10 */ int     mChecksumIndex;   // Current checksum position
    /* 0x14 */ int     mFlushCount;      // Bytes flushed to disk (write mode)
    /* 0x18 */ int     mBufferSize;      // Size of allocated buffer (from DAT_00650f6c)
    /* 0x1C */ int     mBytesInBuffer;   // Valid bytes in buffer
    /* 0x20 */ int     mIsReadMode;      // 1 = read mode, 0 = write mode
    /* 0x24 */ int     mIsEOF;           // End-of-file flag
    /* 0x28 */ int     mIsLastChunk;     // Last chunk flag for read mode
    /* 0x2C */ char    mFilename[256];   // Filename buffer (at offset 0xB * 4 = 0x2C)
    /* 0x12C */ int    mOIDParam;        // OID allocation parameter
    /* 0x130 */ int    mTotalBytesProcessed; // Running total (at offset 0x4B * 4)
};
```

## Global Variables

| Address | Name | Type | Purpose |
|---------|------|------|---------|
| 0x00650f6c | g_DXMemBufferSize | DWORD | Default buffer size (default: 0x100000 = 1MB) |
| 0x008c029c | g_CompressionBuffer | byte[0x102927] | Shared compression/decompression buffer |
| 0x006318a0 | g_CompressedExtension | char* | Extension check for compressed files |

## Function Mappings

### Static Functions

| Address | Name | Purpose | Line |
|---------|------|---------|------|
| 0x00547d40 | DXMemBuffer__SetBufferSize | Set default buffer size (rounded to 1MB boundary) | - |

### Instance Methods (thiscall)

| Address | Name | Purpose | Line |
|---------|------|---------|------|
| 0x00547dc0 | DXMemBuffer__OpenWrite | Open file for writing with buffer | 0xe3 (227) |
| 0x00547ec0 | DXMemBuffer__OpenRead | Open file for reading with decompression | 0x11f (287) |
| 0x005482c0 | DXMemBuffer__GetFileSize | Get underlying file size | - |
| 0x005482d0 | DXMemBuffer__Skip | Skip N bytes forward in read buffer | - |
| 0x00548570 | DXMemBuffer__ReadBytes | Read bytes into destination buffer | - |
| 0x00548820 | DXMemBuffer__ReadLine | Read text line (handles CR/LF -> LF) | - |
| 0x00548a70 | DXMemBuffer__WriteBytes | Write bytes from source buffer | - |
| 0x00548c00 | DXMemBuffer__Close | Flush buffer and close file | - |
| 0x00548d30 | DXMemBuffer__IsEOF | Return EOF flag (this[9]) | - |

**Total: 9 functions**

## Function Details

### DXMemBuffer__SetBufferSize (0x00547d40)

```cpp
void DXMemBuffer__SetBufferSize(int size)
{
    if (size == 0) {
        g_DXMemBufferSize = 0x100000;  // Default 1MB
    } else {
        // Round up to nearest 1MB boundary
        g_DXMemBufferSize = (size + 0xFFFFF) & 0xFFF00000;
    }
}
```

**Purpose:** Sets the global default buffer size used by all DXMemBuffer instances.

---

### DXMemBuffer__OpenWrite (0x00547dc0)

```cpp
bool CDXMemBuffer::OpenWrite(char* filename, int oidParam)
{
    // Allocate 1MB buffer via OID system
    mBuffer = OID__AllocObject(0x100000, oidParam, "DXMemBuffer.cpp", 227);
    if (!mBuffer) {
        Error("Could not allocate memory for writing\n");
        return false;
    }

    mCurrentPos = mBuffer;
    mBufferSize = 0x100000;
    mBytesInBuffer = 0;
    mIsEOF = 0;
    mFlushCount = 0;
    strncpy(mFilename, filename, 256);

    // Create file for writing (CREATE_ALWAYS)
    mFileHandle = CreateFileA(filename, GENERIC_WRITE, 0, NULL,
                              CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, NULL);
    if (mFileHandle == INVALID_HANDLE_VALUE) {
        Error("Membuffer could not open file for writing\n");
        FreeBuffer(mBuffer);
        return false;
    }

    // Generate CRC filename (filename.crc)
    sprintf(crcPath, "%s.crc", filename);
    return true;
}
```

**Key Points:**
- Creates file with `CREATE_ALWAYS` disposition (overwrites existing)
- Allocates 1MB buffer via OID system for memory tracking
- Stores filename for potential CRC generation

---

### DXMemBuffer__OpenRead (0x00547ec0)

```cpp
bool CDXMemBuffer::OpenRead(LPCSTR filename, int oidParam, int unknown, uint seekOffset)
{
    strncpy(mFilename, filename, 256);

    // Allocate buffer via OID system
    mBuffer = OID__AllocObject(g_DXMemBufferSize, oidParam, "DXMemBuffer.cpp", 287);
    if (!mBuffer) {
        Error("Could not allocate memory for reading\n");
        return false;
    }

    mCurrentPos = mBuffer;
    mBufferSize = g_DXMemBufferSize;
    mIsReadMode = 1;
    mIsEOF = 0;
    mIsLastChunk = 0;
    mBytesInBuffer = 0;

    // Open existing file for reading
    mFileHandle = CreateFileA(filename, GENERIC_READ, FILE_SHARE_READ, NULL,
                              OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, NULL);
    if (mFileHandle == INVALID_HANDLE_VALUE) {
        FreeBuffer(mBuffer);
        return false;
    }

    // Handle seek offset for compressed files
    if (seekOffset != 0) {
        // Check if file has compressed extension
        if (IsCompressedFile(mFilename)) {
            // Skip compressed chunks to reach offset
            SkipCompressedChunks(seekOffset);
        } else {
            SetFilePointer(mFileHandle, seekOffset, NULL, FILE_BEGIN);
        }
    }

    // Read first chunk (decompressing if needed)
    if (IsCompressedFile(mFilename)) {
        ReadCompressedChunk();
    } else {
        ReadFile(mFileHandle, mBuffer, mBufferSize, &mBytesInBuffer, NULL);
    }

    // Verify checksum if available
    if (mChecksumTable && mBytesInBuffer > 0) {
        VerifyChecksum();
    }

    return true;
}
```

**Key Points:**
- Opens file with `OPEN_EXISTING` disposition
- Supports zlib-compressed files (auto-detected by extension)
- Handles seeking in both raw and compressed files
- Optional checksum verification

---

### DXMemBuffer__ReadBytes (0x00548570)

```cpp
int CDXMemBuffer::ReadBytes(void* dest, uint count)
{
    int totalRead = 0;

    // Check for EOF in last chunk mode
    if (mIsLastChunk && mCurrentPos + count > mBuffer + mBytesInBuffer) {
        mIsEOF = 1;
        count = (mBuffer + mBytesInBuffer) - mCurrentPos;
    }

    while (count > 0) {
        // Copy available data from buffer
        int available = (mBuffer + mBytesInBuffer) - mCurrentPos;
        int toCopy = min(count, available);

        memcpy(dest, mCurrentPos, toCopy);
        dest += toCopy;
        mCurrentPos += toCopy;
        count -= toCopy;
        totalRead += toCopy;

        // Need more data?
        if (count > 0) {
            // Refill buffer (with decompression if needed)
            RefillBuffer();
        }
    }

    mTotalBytesProcessed += totalRead;
    return totalRead;
}
```

**Key Points:**
- Handles buffer boundary crossing transparently
- Auto-refills buffer when exhausted
- Supports zlib decompression via `uncompress()`
- Tracks total bytes processed

---

### DXMemBuffer__ReadLine (0x00548820)

```cpp
void CDXMemBuffer::ReadLine(char* dest, DWORD maxLen)
{
    int pos = 0;
    int limit = maxLen - 1;

    while (pos < limit) {
        // Check if buffer needs refill
        if (mCurrentPos >= mBuffer + mBytesInBuffer) {
            if (mIsLastChunk) {
                mIsEOF = 1;
                break;
            }
            RefillBuffer();
        }

        char c = *mCurrentPos++;
        dest[pos++] = c;

        if (c == '\n') break;
    }

    // Convert CR/LF to LF only
    if (pos >= 2 && dest[pos-2] == '\r') {
        dest[pos-2] = '\n';
        dest[pos-1] = '\0';
    }

    dest[pos] = '\0';
    mTotalBytesProcessed += pos;
}
```

**Key Points:**
- Reads until newline or buffer limit
- Handles Windows CR/LF -> Unix LF conversion
- Null-terminates result

---

### DXMemBuffer__WriteBytes (0x00548a70)

```cpp
void CDXMemBuffer::WriteBytes(void* src, uint count)
{
    while (count > 0) {
        int available = mBufferSize - (mCurrentPos - mBuffer);

        if (count > available) {
            // Buffer full - flush to disk
            memcpy(mCurrentPos, src, available);
            src += available;
            count -= available;

            // Write buffer to file (with compression if needed)
            if (IsCompressedFile(mFilename)) {
                WriteCompressedChunk();
            } else {
                WriteFile(mFileHandle, mBuffer, mBufferSize, &bytesWritten, NULL);
            }

            mCurrentPos = mBuffer;
            mBytesInBuffer = 0;
            mTotalBytesProcessed += available;
        } else {
            // Copy to buffer
            memcpy(mCurrentPos, src, count);
            mCurrentPos += count;
            mBytesInBuffer += count;
            mTotalBytesProcessed += count;
            break;
        }
    }
}
```

**Key Points:**
- Buffers writes until buffer is full
- Auto-flushes to disk when buffer fills
- Supports zlib compression via `compress()`

---

### DXMemBuffer__Close (0x00548c00)

```cpp
bool CDXMemBuffer::Close()
{
    if (!mBuffer) return false;

    if (mIsReadMode) {
        // Read mode - just cleanup
        CloseHandle(mFileHandle);
        FreeBuffer(mBuffer);
        mBuffer = NULL;
        FreeBuffer(mChecksumTable);
        mChecksumTable = NULL;
        return true;
    }

    // Write mode - flush remaining data
    if (IsCompressedFile(mFilename)) {
        WriteCompressedChunk();
    } else {
        if (!WriteFile(mFileHandle, mBuffer, mBytesInBuffer, &bytesWritten, NULL)) {
            Error("Write failed");
        }
    }

    CloseHandle(mFileHandle);
    FreeBuffer(mBuffer);
    mBuffer = NULL;
    return true;
}
```

**Key Points:**
- Flushes remaining buffer contents in write mode
- Frees allocated memory
- Closes file handle

## Compression Format

The DXMemBuffer uses a chunked compression format for files with certain extensions:

```
[Compressed File Format]
+----------------+----------------+----------------+
| ChunkSize (4B) | CompressedData | ChunkSize (4B) | ...
+----------------+----------------+----------------+

- ChunkSize: 32-bit little-endian size of following compressed data
- CompressedData: zlib-compressed chunk (decompresses to up to 0x102927 bytes)
- Files are processed chunk-by-chunk, with each chunk decompressed independently
```

**Decompression Buffer:** 0x102927 bytes (1,059,111 bytes) at 0x008c029c

## Notable Strings

| Address | String | Context |
|---------|--------|---------|
| 0x00650fa4 | "Could not allocate memory for writing\n" | OpenWrite failure |
| 0x00650f78 | "Membuffer could not open file for writing\n" | File creation failure |
| 0x00650ff4 | "Could not allocate memory for reading\n" | OpenRead failure |
| 0x00651020 | "Write failed\n" | WriteBytes failure |
| 0x00651030 | "Write failed" | Close flush failure |
| 0x00650f70 | "%s.crc" | CRC filename format |

## Related Functions

| Address | Name | Purpose |
|---------|------|---------|
| 0x00549220 | FreeBuffer | Free memory via CMemoryManager (wrapper) |
| 0x004a1570 | FUN_004a1570 | Memory reference count check |
| 0x00568390 | stricmp (`FUN_00568390`) | String comparison (extension check) |
| 0x0042c750 | FUN_0042c750 | Error reporting function |
| 0x0040c640 | DebugTrace | Debug trace output |

## Usage Pattern

```cpp
// Reading a file
CDXMemBuffer reader;
if (reader.OpenRead("data/level.dat", OID_LEVEL_DATA, 0, 0)) {
    char line[256];
    while (!reader.IsEOF()) {
        reader.ReadLine(line, sizeof(line));
        // Process line...
    }
    reader.Close();
}

// Writing a file
CDXMemBuffer writer;
if (writer.OpenWrite("data/save.dat", OID_SAVE_DATA)) {
    writer.WriteBytes(header, sizeof(header));
    writer.WriteBytes(data, dataSize);
    writer.Close();
}
```

## Cross-References

Functions that use DXMemBuffer:
- Level loading system (World.cpp)
- Save/load system (Career.cpp)
- Configuration loading (various FEP* classes)
- Resource loading (mesh, texture, particle systems)

## Notes

1. **Buffer Size:** Default 1MB, can be changed globally via `DXMemBuffer__SetBufferSize`
2. **Compression:** Uses zlib `compress()` and `uncompress()` functions
3. **Memory Management:** Allocates via OID system with debug tracking
4. **Thread Safety:** Not thread-safe - single-threaded access assumed
5. **Error Handling:** Logs errors but continues where possible
