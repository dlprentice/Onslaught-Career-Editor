# MCTentacle.cpp Functions

> Source File: MCTentacle.cpp | Binary: BEA.exe
> Debug Path: `C:\dev\ONSLAUGHT2\MCTentacle.cpp` at 0x0062e06c

## Overview

Motion controller for the tentacle boss animation system. CMCTentacle is a specialized motion controller that animates multi-segment tentacle appendages using cubic Bezier splines. The system supports:

- Dynamic bone chain animation with position/orientation interpolation
- Bezier spline-based smooth motion between control points
- Special bone types: "tether" (anchor), "tethercp" (control point), "headcp" (head control), "tentacle" (segment)
- Hierarchical bone transform propagation

## Functions

| Address | Name | Size | Purpose |
|---------|------|------|---------|
| 0x0049cc40 | CMCTentacle__Init | ~1600 bytes | Initialize tentacle controller, allocate bone arrays |
| 0x0049d280 | CMCTentacle__UpdateBone | ~2576 bytes | Update individual bone transforms recursively |
| 0x0049dc90 | CMCTentacle__Factorial | ~32 bytes | Calculate factorial for Bezier coefficients |
| 0x0049dcb0 | CMCTentacle__Power | ~32 bytes | Calculate power function for Bezier math |
| 0x0049dcd0 | CMCTentacle__UpdateSpline | ~2016 bytes | Calculate Bezier spline positions for all bones |
| 0x0049e4b0 | CMCTentacle__BuildOrientationMatrix | ~496 bytes | Build 3x3 rotation matrix from direction vectors |
| 0x0049eca0 | CMCTentacle__ValidateBoneStructure | ~144 bytes | Validate required bone names exist |
| 0x0049ed30 | CMCTentacle__HasTentacleBone | ~80 bytes | Check if model has any "tentacle" bone |

**Total: 8 functions (~6976 bytes)**

## Function Details

### CMCTentacle__Init (0x0049cc40)

**Purpose:** Constructor/initializer for the tentacle motion controller.

**Key Operations:**
- Allocates arrays for bone positions (16 bytes each - vec4)
- Allocates arrays for bone matrices (48 bytes each - 3x4 matrix)
- Allocates arrays for bone timing data (4 bytes each - float)
- Searches for special bones by name: "tether", "tethercp", "headcp", "tentacle"
- Initializes bone timing values to -1.0f (0xbf800000)
- Sets `mInitialized` flag at offset 0x2c

**Member Offsets (this pointer in ECX):**
- 0x08: Skeleton/bone pointer
- 0x0c: Bone matrix array (48 bytes per bone)
- 0x10: Bone position array (16 bytes per bone)
- 0x14: Bone timing array (4 bytes per bone)
- 0x18: Previous bone matrix array
- 0x1c: Previous bone position array
- 0x20: Previous bone timing array
- 0x2c: mInitialized flag
- 0x30-0x3c: Tether position (vec4)
- 0xa0: Tether bone index
- 0xa4: TetherCP bone index
- 0xa8: Unknown bone index
- 0xac: Unknown bone index
- 0xb0: HeadCP bone index
- 0xb4-0xc0: HeadCP position (vec4)
- 0xdc: Spline positions array
- 0xe0: Spline matrices array
- 0xe4: Spline bone index array
- 0xe8: Spline bone count

### CMCTentacle__UpdateBone (0x0049d280)

**Purpose:** Main per-frame bone update function. Recursively processes bone hierarchy.

**Key Operations:**
- Lazy initialization check (calls Init if not initialized)
- Retrieves bone parent transform data
- Handles special bones (tether, tethercp, headcp) differently
- Applies sin/cos rotations for tentacle segments (-1.57 radians = -90 degrees)
- Matrix multiplication for bone-to-world transforms
- Stores current state to "previous" arrays for interpolation
- Recursively calls itself for child bones

**Parameters:** Takes 19 float/int parameters including position, rotation matrix columns, bone pointer, and flags.

### CMCTentacle__UpdateSpline (0x0049dcd0)

**Purpose:** Calculates cubic Bezier spline positions for smooth tentacle animation.

**Key Operations:**
- Computes control point deltas from bone movements
- Uses cubic Bezier formula: B(t) = sum(C(n,i) * (1-t)^(n-i) * t^i * P_i)
- Calls Factorial and Power helpers for Bernstein polynomial coefficients
- Iterates through all spline bones (count at offset 0xe8)
- Builds orientation matrices for each spline segment
- Stores results in spline position/matrix arrays

**Math Constants:**
- Degree n=3 (cubic Bezier)
- 4 control points per spline segment

### CMCTentacle__BuildOrientationMatrix (0x0049e4b0)

**Purpose:** Constructs a 3x3 rotation matrix from a direction vector and up vector.

**Key Operations:**
- Takes direction vector (negated) and up vector
- Cross product: right = up x direction
- Cross product: newUp = direction x right
- Normalizes all three axes (checks for zero length)
- Stores result in 3x4 matrix format (columns: right, newUp, direction)

**Output Matrix Layout (float array):**
```
[0]  = right.x     [4]  = right.y     [8]  = right.z
[1]  = newUp.x     [5]  = newUp.y     [9]  = newUp.z
[2]  = dir.x       [6]  = dir.y       [10] = dir.z
```

### CMCTentacle__ValidateBoneStructure (0x0049eca0)

**Purpose:** Validates that a model has all required bones for tentacle animation.

**Required Bones (checked at offset +0xdc of bone):**
1. "tether" - anchor point bone
2. (unknown string at 0x0062e038) - likely "head" or similar
3. "tethercp" - tether control point
4. "headcp" - head control point
5. "tentacle" - main tentacle segment

**Returns:** true if ALL bones found, false if ANY missing.

### CMCTentacle__HasTentacleBone (0x0049ed30)

**Purpose:** Quick check if any bone in the model contains "tentacle" in its name.

**Key Operations:**
- Iterates through all bones (count at param+0x15c, array at param+0x160)
- Calls string comparison function at each bone+0xdc
- Returns 1 (true) on first match, 0 (false) if none found

### CMCTentacle__Factorial (0x0049dc90)

**Purpose:** Simple factorial calculation for Bezier coefficients.

**Implementation:** Iterative loop: `result = 1; for(i=2; i<=n; i++) result *= i;`

### CMCTentacle__Power (0x0049dcb0)

**Purpose:** Float power calculation for Bezier polynomial terms.

**Implementation:** Iterative loop: `result = 1.0; for(i=0; i<n; i++) result *= base;`

## Key Observations

### Bezier Spline System
The tentacle uses **cubic Bezier splines** (degree 3, 4 control points) to create smooth curved motion. The Bernstein polynomial formula is implemented using:
- `C(n,i) = n! / (i! * (n-i)!)` - binomial coefficients
- `B_i,n(t) = C(n,i) * (1-t)^(n-i) * t^i` - Bernstein basis polynomials

### Bone Naming Convention
Special bones are identified by substring matching at offset +0xdc:
- `tether` - Fixed anchor point (base of tentacle)
- `tethercp` - Bezier control point near tether
- `headcp` - Bezier control point near head/tip
- `tentacle` - Individual segment bones

### Matrix Format
Uses 3x4 matrices (48 bytes) stored column-major:
- Columns 0-2: 3x3 rotation matrix
- Column 3: Translation vector (implicit or stored separately)

### Physics Constants
- Rotation offset: -1.57 radians (-90 degrees) - aligns bone orientation
- Initial timing value: -1.0f (0xbf800000) - indicates uninitialized state

## Class Structure (Estimated)

```cpp
class CMCTentacle : public CMotionController {
    // 0x00: vtable
    // 0x04: base class data
    void* mSkeleton;              // 0x08
    float* mBoneMatrices;         // 0x0c (48 bytes per bone)
    float* mBonePositions;        // 0x10 (16 bytes per bone)
    float* mBoneTiming;           // 0x14 (4 bytes per bone)
    float* mPrevBoneMatrices;     // 0x18
    float* mPrevBonePositions;    // 0x1c
    float* mPrevBoneTiming;       // 0x20
    // 0x24-0x28: unknown
    int mInitialized;             // 0x2c
    float mTetherPos[4];          // 0x30-0x3c
    float mTetherCPMatrix[12];    // 0x40-0x6c (for transform)
    // ... more control point data ...
    float mHeadPos[4];            // 0x80-0x8c
    float mSplinePos[4];          // 0x90-0x9c
    int mTetherBone;              // 0xa0
    int mTetherCPBone;            // 0xa4
    int mUnknownBone1;            // 0xa8
    int mUnknownBone2;            // 0xac
    int mHeadCPBone;              // 0xb0
    float mHeadCPPos[4];          // 0xb4-0xc0
    // ... gap ...
    float* mSplinePositions;      // 0xdc
    float* mSplineMatrices;       // 0xe0
    int* mSplineBoneIndices;      // 0xe4
    int mSplineBoneCount;         // 0xe8
};
```

## Related Components

- **CTentacle** - Entity class for tentacle boss (Tentacle.cpp)
- **CTentacleAI** - AI controller for tentacle behavior
- **CTentacleGuide** - Pathfinding/guidance system
- **CComponentTentacle** - Component attachment system

## String References

| Address | String | Usage |
|---------|--------|-------|
| 0x0062e02c | "tentacle" | Bone name search |
| 0x0062e040 | "tether" | Anchor bone search |
| 0x0062e00c | "tethercp" | Control point bone search |
| 0x0062e004 | "headcp" | Head control point search |
| 0x0062e048 | "Got %d bones in tentacle\n" | Debug output |
| 0x0062e018 | "TPos at %f %f %f" | Debug position output |

---
*Discovered via Phase 1 xref analysis (Dec 2025)*
*8 functions identified and renamed in Ghidra*
