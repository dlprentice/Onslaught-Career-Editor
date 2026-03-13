# DXTrees.cpp - Function Mappings

> DirectX-specific tree rendering system for environmental vegetation
> Source: `C:\dev\ONSLAUGHT2\DXTrees.cpp` (debug path at 0x006529b0)
> Last updated: 2025-12-16

## Overview

DXTrees.cpp implements the `CDXTrees` class which handles DirectX-specific rendering of environmental trees (vegetation billboards). The class manages two vertex/index buffers for rendering tree sprites as camera-facing quads.

**Key Features:**
- Billboard sprite rendering for distant trees
- Two separate vertex buffers (main + shadow/secondary)
- Quadtree-based spatial queries for visible trees
- Vertex buffer locking for dynamic hiding of destroyed trees

## Class Structure

### CDXTrees

**Size:** ~0x14 bytes (estimated)

| Offset | Type | Name | Notes |
|--------|------|------|-------|
| 0x00 | void* | vtable | Points to 0x005e59d8 |
| 0x04 | ??? | ??? | Inherited from base class |
| 0x08 | CVBufTexture* | m_pTreeBuffer1 | Main tree vertex buffer |
| 0x0C | CVBufTexture* | m_pTreeBuffer2 | Secondary tree vertex buffer |
| 0x10 | int | m_nTreeCount | Number of trees in buffers |

### Vtable (0x005e59d8)

| Index | Address | Function |
|-------|---------|----------|
| 0 | 0x0055a360 | CDXTrees__scalar_deleting_dtor |
| 1 | 0x00501930 | (inherited) |
| 2 | 0x00405930 | (inherited) |
| 3 | 0x00405930 | (inherited) |
| 4 | 0x0055a3b0 | CDXTrees__ReleaseBuffers |

## Functions

### CDXTrees__CDXTrees (0x0055a350)
**Constructor**

Sets up the vtable pointer.

```cpp
void CDXTrees::CDXTrees() {
    *(void**)this = &CDXTrees_vtable;
}
```

---

### CDXTrees__scalar_deleting_dtor (0x0055a360)
**Scalar Deleting Destructor**

MSVC-generated destructor that optionally frees memory.

```cpp
void CDXTrees::`scalar deleting destructor`(byte flags) {
    this->~CDXTrees();
    if (flags & 1) {
        operator delete(this);
    }
}
```

---

### CDXTrees__dtor (0x0055a380)
**Destructor**

Cleans up resources and calls base class destructor.

```cpp
CDXTrees::~CDXTrees() {
    *(void**)this = &CDXTrees_vtable;
    // Call base destructor at 0x00512d50
}
```

---

### CDXTrees__Init (0x0055a390)
**Initialize**

Initializes member variables, sets buffer pointers to NULL.

```cpp
void CDXTrees::Init() {
    BaseClass::Init();  // 0x00512ca0
    m_pTreeBuffer1 = NULL;  // this+0x08
    m_pTreeBuffer2 = NULL;  // this+0x0C
}
```

---

### CDXTrees__ReleaseBuffers (0x0055a3b0)
**Release Vertex Buffers**

Releases both CVBufTexture objects and frees memory.

```cpp
int CDXTrees::ReleaseBuffers() {
    if (m_pTreeBuffer1) {
        m_pTreeBuffer1->~CVBufTexture();
        operator delete(m_pTreeBuffer1);
        m_pTreeBuffer1 = NULL;
    }
    if (m_pTreeBuffer2) {
        m_pTreeBuffer2->~CVBufTexture();
        operator delete(m_pTreeBuffer2);
        m_pTreeBuffer2 = NULL;
    }
    return 0;
}
```

---

### CDXTrees__Reset (0x0055a400)
**Reset**

Calls virtual method then releases buffers.

```cpp
void CDXTrees::Reset() {
    // Call virtual method at vtable+0x10
    ReleaseBuffers();  // 0x00512cc0
}
```

---

### CDXTrees__BuildTreeGeometry (0x0055a420)
**Build Tree Geometry** - Main function

Iterates through the world quadtree to find all tree objects and builds vertex/index buffers for rendering them as billboards.

**Debug References:**
- Line 0x5E (94): First CVBufTexture allocation
- Line 0x6A (106): Second CVBufTexture allocation

**Algorithm:**
1. Release existing buffers if present
2. Allocate two new CVBufTexture objects (size 0x68 bytes each)
3. Configure vertex format: 0x152 (position + texture coords), 0x24 bytes per vertex
4. Configure index format: 0x65, 2 bytes per index
5. Iterate through quadtree levels (4 down to 0)
6. For each cell, query CMapWho for tree objects (flag 0x2000000)
7. For each tree, create a billboard quad (4 vertices, 6 indices)
8. Add vertices with UV coordinates from tree texture atlas

**Key Constants:**
- Vertex size: 0x24 (36 bytes)
- 4 vertices per tree billboard
- 6 indices per tree (2 triangles)
- Uses flag 0x2000000 to identify tree objects

```cpp
void CDXTrees::BuildTreeGeometry() {
    // Release existing buffers
    if (m_pTreeBuffer1) { /* cleanup */ }
    if (m_pTreeBuffer2) { /* cleanup */ }
    m_nTreeCount = 0;

    // Allocate buffer 1
    m_pTreeBuffer1 = new CVBufTexture();
    m_pTreeBuffer1->SetVBFormat(0x152, flags, 0x24, 4, 1);
    m_pTreeBuffer1->SetIBFormat(0x65, flags, 2, 1);
    m_pTreeBuffer1->SetPersist();

    // Allocate buffer 2
    m_pTreeBuffer2 = new CVBufTexture();
    // ... same setup

    // Iterate quadtree levels
    for (int level = 4; level >= 0; level--) {
        int gridSize = 64 / (1 << level);
        for (int x = 0; x < gridSize; x++) {
            for (int y = 0; y < gridSize; y++) {
                // Query mapwho for trees
                foreach (tree in cell) {
                    if (tree->flags & 0x2000000) {
                        // Build billboard quad
                        AddVertices(positions, 4);
                        AddIndices(indices, 6);
                        m_nTreeCount++;
                    }
                }
            }
        }
    }
}
```

---

### CDXTrees__Render (0x0055aa10)
**Render Trees**

Renders all tree billboards using the prepared vertex/index buffers.

**Algorithm:**
1. Check if tree count > 0
2. If buffers not built, call BuildTreeGeometry
3. Set up render states (blending, alpha test, etc.)
4. Bind texture
5. Render first buffer (main trees)
6. Optionally render second buffer based on distance check (> 20 units)
7. Restore render states

**Key Features:**
- Distance-based LOD (checks 20.0 unit threshold)
- Multiple render state changes for alpha blending
- Uses CVBufTexture::RenderIndexed and RenderIndexedNoValidate

```cpp
void CDXTrees::Render() {
    if (m_nTreeCount <= 0) return;

    if (m_pTreeBuffer1 == NULL) {
        BuildTreeGeometry();
    }

    // Setup render states
    SetRenderState(D3DRS_ALPHABLENDENABLE, TRUE);
    // ... more state setup

    // Render main buffer
    m_pTreeBuffer1->RenderIndexedNoValidate(0, 0, 0);

    // Distance check for secondary buffer
    float dist = GetCameraDistance();
    if (abs(currentDist - dist) > 20.0f) {
        m_pTreeBuffer2->RenderIndexed(0, 0, 0, 0);
    }

    // Restore states
}
```

---

### CDXTrees__HideTree (0x0055ae40)
**Hide Tree**

Hides a specific tree by zeroing out its vertex positions in both buffers.

**Parameters:**
- `param_1`: Pointer to tree object (contains vertex index at offset 0x30)

**Algorithm:**
1. Check if tree has valid vertex index (>= 0)
2. Lock vertex buffer range for tree's 4 vertices
3. Zero out position components for all 4 vertices
4. Unlock buffer
5. Repeat for second buffer

```cpp
void CDXTrees::HideTree(CTree* tree) {
    short vertexIndex = tree->m_nVertexIndex;  // offset 0x30
    if (vertexIndex < 0) return;
    if (m_pTreeBuffer1 == NULL || m_pTreeBuffer2 == NULL) return;

    // Hide in buffer 1
    void* vertices;
    if (m_pTreeBuffer1->LockRange(vertexIndex * 0x24, 0x90, &vertices, 0) >= 0) {
        // Zero positions for 4 vertices (offsets 3,4,5 / 12,13,14 / 21,22,23 / 30,31,32)
        memset(vertices + 0x0C, 0, 12);  // vertex 0 position
        memset(vertices + 0x30, 0, 12);  // vertex 1 position
        memset(vertices + 0x54, 0, 12);  // vertex 2 position
        memset(vertices + 0x78, 0, 12);  // vertex 3 position
        m_pTreeBuffer1->Unlock();
    }

    // Hide in buffer 2
    // ... same pattern
}
```

## Related Systems

### CVBufTexture
Vertex buffer wrapper class with texture support. Key methods used:
- `SetVBFormat(format, flags, stride, count, mode)`
- `SetIBFormat(format, flags, size, mode)`
- `SetPersist()`
- `AddVertices(data, count)`
- `AddIndices(data, count)`
- `RenderIndexed(start, count, base, flags)`
- `RenderIndexedNoValidate(start, count, flags)`
- `LockRange(offset, size, ppData, flags)`
- `Unlock()`

### CMapWho
Quadtree-based spatial partitioning system. Used to find tree objects in world cells.
- Entry flag 0x2000000 identifies tree objects
- GetOwner() returns CThing pointer

### tree.cpp
See [tree.cpp/_index.md](tree.cpp/_index.md) for the CTree class which manages individual tree objects (falling physics, destruction).

## Global References

| Address | Name | Usage |
|---------|------|-------|
| 0x00854e6c | DAT_00854e6c | Flag affecting vertex buffer format |
| 0x00704290 | DAT_00704290 | Quadtree level pointers |
| 0x009cc160 | DAT_009cc160 | Matrix data for rendering |
| 0x009cc190-19c | DAT_009cc190 | Render parameters |

## Callers

| Address | Function | Context |
|---------|----------|---------|
| 0x0046cfe2 | CGame__LoadLevel | Called during level load |
| 0x0055aa2e | CDXTrees__Render | Called if buffers not built |

## Notes

1. **Two-Buffer System**: The class maintains two separate vertex buffers. The first appears to be the main tree buffer, while the second may be for shadows or LOD purposes.

2. **Quadtree Integration**: Tree geometry is built by iterating through the CMapWho quadtree system, which provides efficient spatial queries.

3. **Dynamic Hiding**: Trees can be hidden at runtime (when destroyed) by zeroing their vertex positions, avoiding the need to rebuild the entire buffer.

4. **OID Allocation**: Both CVBufTexture objects are allocated via OID__AllocObject with type 0x1f and size 0x68 bytes.
