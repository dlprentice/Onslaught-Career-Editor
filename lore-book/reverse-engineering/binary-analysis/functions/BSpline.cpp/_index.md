# BSpline.cpp Functions

> Source File: BSpline.cpp | Binary: BEA.exe
> Debug Path: 0x00623ab8 (`C:\dev\ONSLAUGHT2\BSpline.cpp`)

## Overview

CBSpline implements B-spline curve mathematics for smooth interpolation. Used by the camera system (CCamera) and player movement (CPlayer) for smooth trajectory calculations. B-splines provide C2 continuity (smooth position, velocity, and acceleration) which is essential for fluid camera movements and path following.

The implementation uses the Cox-de Boor recursion formula for computing basis functions, which is the standard algorithm for B-spline evaluation.

## Functions

| Address | Name | Purpose | Size |
|---------|------|---------|------|
| 0x00416d10 | CBSpline__ctor | Constructor - initializes spline with control points and order | ~0x86 bytes |
| 0x00416da0 | CBSpline__dtor | Destructor - frees knot vector and control point memory | ~0x8D bytes |
| 0x00416e30 | CBSpline__BasisFunction | Cox-de Boor recursion for basis function N(i,k,t) | ~0x102 bytes |
| 0x00416fc0 | CBSpline__GetPoint | Evaluate spline at parameter t, outputs 3D/4D point | ~0xD6 bytes |

**Total: 4 functions identified**

## Class Layout (CBSpline)

Based on decompilation analysis:

| Offset | Type | Field | Description |
|--------|------|-------|-------------|
| 0x00 | void** | vtable | Points to 0x005d8e00 |
| 0x04 | void* | mpControlPoints | Linked list of control points |
| 0x08 | int* | mpKnots | Knot vector array |
| 0x0C | int | mOrder | Spline order (degree + 1) |
| 0x10 | int | mNumControlPoints | Number of control points - 1 |

## Function Details

### CBSpline__ctor (0x00416d10)

**Signature:** `CBSpline* __thiscall CBSpline__ctor(void* controlPoints, int order)`

Constructor that initializes a B-spline:
1. Stores control points pointer and order
2. Sets vtable to 0x005d8e00
3. Calculates knot vector size: `(numControlPoints + order) * 4 + 4`
4. Allocates knot vector via memory manager (0x005490e0)
5. Initializes uniform knot vector with clamped ends

**Knot Vector Initialization:**
- First `order` knots are 0 (clamped start)
- Middle knots are sequential integers
- Last `order` knots are `numControlPoints - order + 2` (clamped end)

### CBSpline__dtor (0x00416da0)

**Signature:** `void __thiscall CBSpline__dtor(byte flags)`

Destructor that cleans up allocated memory:
1. Frees knot vector
2. Iterates through control points linked list, freeing each
3. If `flags & 1`, also frees the CBSpline object itself

### CBSpline__BasisFunction (0x00416e30)

**Signature:** `float __thiscall CBSpline__BasisFunction(int i, int k, float t)`

Implements the Cox-de Boor recursion formula for B-spline basis functions:

```
N(i,1,t) = 1 if knot[i] <= t < knot[i+1], else 0

N(i,k,t) = ((t - knot[i]) / (knot[i+k-1] - knot[i])) * N(i, k-1, t)
         + ((knot[i+k] - t) / (knot[i+k] - knot[i+1])) * N(i+1, k-1, t)
```

**Parameters:**
- `i` - Basis function index
- `k` - Order (recursion depth)
- `t` - Parameter value

**Returns:** Basis function value N(i,k,t) in range [0.0, 1.0]

Includes optimizations for zero-division cases (when knot intervals are equal).

### CBSpline__GetPoint (0x00416fc0)

**Signature:** `void __thiscall CBSpline__GetPoint(float* outPoint, float t)`

Evaluates the spline at parameter t:

```
P(t) = sum(i=0 to n) { N(i,k,t) * ControlPoint[i] }
```

**Parameters:**
- `outPoint` - Output 4D point (x, y, z, w)
- `t` - Parameter value in range [0.0, 1.0]

**Algorithm:**
1. Scale t by `(numControlPoints - order + 2)` to map to knot range
2. Iterate through all control points
3. For each, compute basis function N(i, order, scaled_t)
4. Accumulate weighted sum of control points
5. Store result in outPoint (x, y, z, w)

## Callers (Who Uses CBSpline)

| Address | Function | Context |
|---------|----------|---------|
| 0x00418ef0 | CThing3rdPersonCamera__ctor | 3rd-person camera spline construction (call @ `0x00419086`) |
| 0x004d2f19 | CPlayer__GotoPanView | Pan-view camera spline construction (`references/Onslaught/Player.cpp`: `CPlayer::GotoPanView`) |
| 0x00533e20 | IScript__Create3PointPanCamera | Script-created pan camera (3-point spline) |
| 0x0053421e | IScript__Create4PointPanCamera | Script-created pan camera (4-point spline) |

## VTable (0x005d8e00)

| Offset | Address | Method |
|--------|---------|--------|
| 0x00 | 0x00416da0 | CBSpline__dtor |
| 0x04 | 0x0060c9f8 | (Data, not code) |
| 0x08 | 0x004ff330 | (Unidentified) |
| 0x0C | 0x00417480 | (Destructor variant) |
| 0x10 | 0x004bacb0 | (Unidentified) |
| 0x14 | 0x004fef40 | CWarspite__Update (wrong class?) |
| 0x18 | 0x004ff4f0 | (Unidentified) |
| 0x1C | 0x004fea30 | (Unidentified) |

Note: VTable entries 0x04+ may be shared or misaligned - needs further investigation.

## Key Observations

1. **Uniform Clamped Knots**: The constructor creates a uniform knot vector with clamped endpoints, ensuring the curve passes through the first and last control points.

2. **Fixed-Point Influence**: The knot vector stores integers (not floats), and the basis function casts between int and float. This may be a performance/implementation choice (treat as raw ints unless proven fixed-point).

3. **Linked List Control Points**: Control points are stored in a linked list rather than an array, which is unusual for B-spline implementations. Each node contains the 3D point data and a pointer to the next node.

4. **Camera Integration**: The primary use case is camera path smoothing, evidenced by CCamera constructor calling CBSpline__ctor. This provides smooth camera transitions during cutscenes and gameplay.

5. **Memory Management**: Uses the engine's custom memory allocator at 0x005490e0 with source file tracking (debug path passed as parameter).

## Mathematical Background

B-splines (Basis splines) are piecewise polynomial curves defined by:
- **Control Points**: Define the shape (the spline approximates these)
- **Knot Vector**: Defines parameter intervals where basis functions are non-zero
- **Order k**: Degree + 1 (e.g., order 4 = cubic splines)

For a B-spline of order k with n+1 control points, you need n+k+1 knots.

The Cox-de Boor algorithm computes basis functions recursively, starting from piecewise constant functions (order 1) and building up to the desired order.

---
*Discovered via Phase 1 xref analysis (Dec 2025)*
