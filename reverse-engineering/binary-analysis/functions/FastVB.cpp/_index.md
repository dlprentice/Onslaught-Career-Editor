# FastVB.cpp - Fast Vertex Buffer System

**Source File:** `C:\dev\ONSLAUGHT2\FastVB.cpp`
**Debug String Address:** `0x0063fb24`
**Functions Found:** 5 (+ 2 exception unwind handlers)

## Overview

CFastVB is a fast vertex buffer class designed for rendering dynamic quads (sprites, particles, UI elements). It uses a dynamic vertex buffer with an associated index buffer for efficient batched quad rendering.

### Key Characteristics

- **Vertex Size:** 0x1c (28 bytes) - likely position (12) + color (4) + UV (8) + normal/padding (4)
- **Max Vertices:** 0x144 (324 vertices = 81 quads)
- **Index Buffer:** Shared static index buffer at `DAT_00897a90` (0x1d4c = 7500 bytes)
- **Quad Indexing:** Uses 6 indices per quad (two triangles): [0,1,2,2,3,0] pattern

## Class Structure (CFastVB)

```cpp
struct CFastVB {
    /* 0x00 */ CVBuffer* pVertexBuffer;    // Pointer to vertex buffer
    /* 0x04 */ ushort   nWriteOffset;      // Current write position (vertex count)
    /* 0x06 */ ushort   nStartVertex;      // Start vertex for current batch (-1 if none)
    /* 0x08 */ int      nVertexCount;      // Number of vertices in current batch
    /* 0x0C */ int      nMaxVertices;      // Maximum vertices (0x144 = 324)
};
```

## Functions

| Address | Name | Description |
|---------|------|-------------|
| `0x0051a270` | CFastVB__Create | Initialize fast vertex buffer |
| `0x0051a340` | CFastVB__Destroy | Release vertex buffer and static index buffer |
| `0x0051a380` | CFastVB__LockAligned | Lock vertex buffer (4-vertex aligned) |
| `0x0051a430` | CFastVB__Lock | Lock vertex buffer for writing |
| `0x0051a510` | CFastVB__Render | Flush pending vertices to GPU |
| `0x005d6820` | CFastVB__Create__Unwind | Exception handler for Create |
| `0x005d6840` | CFastVB__Render__Unwind | Exception handler for Render |

---

## Recent Headless Semantic Promotions (2026-02-26)

| Address | Symbol | Description |
|---------|--------|-------------|
| `0x00584144` | `CFastVB__PackTexels_NoDither_Bits16_16` | Non-dither packer writing two 16-bit channels per texel into packed 32-bit output |
| `0x0058423f` | `CFastVB__PackTexels_NoDither_Bits2_10_10_10` | Non-dither packer writing 2-10-10-10 packed output from float texel channels |
| `0x0058439e` | `CFastVB__PackTexels_NoDither_Bits16_16_16_16` | Non-dither packer writing 16-16-16-16 packed output (two dwords per texel) |
| `0x00584d78` | `CFastVB__UnpackTexels_Bits565ToFloat4` | Unpacks 16-bit RGB565 packed texels into normalized float4 channels |
| `0x00584e32` | `CFastVB__UnpackTexels_Bits555ToFloat4_AlphaOne` | Unpacks 5-5-5 packed texels into float4 with forced alpha lane |
| `0x00584ee9` | `CFastVB__UnpackTexels_Bits1555ToFloat4` | Unpacks 1-5-5-5 packed texels into float4 including alpha-bit expansion |
| `0x00584fae` | `CFastVB__UnpackTexels_Bits4444ToFloat4` | Unpacks 4-4-4-4 packed texels into normalized float4 RGBA channels |
| `0x00585072` | `CFastVB__UnpackTexels_Bits2_10_10_10_ToFloat4` | Unpacks 2-10-10-10 packed texels into float4 channels with component scaling |
| `0x00585161` | `CFastVB__UnpackTexels_Bits8888ToFloat4` | Unpacks 8-8-8-8 packed texels into float4 RGBA channels |
| `0x00585220` | `CFastVB__UnpackTexels_Bits888ToFloat4_AlphaOne` | Unpacks 8-8-8 packed texels into float4 RGB with forced alpha=1.0 |
| `0x005852d5` | `CFastVB__UnpackTexels_Bits16_16_ToFloat4_RG` | Unpacks dual 16-bit channels into float4 RG lanes with default BA handling |
| `0x00585380` | `CFastVB__UnpackTexels_Bits2_10_10_10_ToFloat4_Alt` | Alternate channel-order unpacker for 2-10-10-10 packed texels |
| `0x005859d8` | `CFastVB__UnpackTexels_L8ToFloat4` | Unpacks 8-bit luminance texels into float4 with replicated RGB and alpha=1.0 |
| `0x00585a7b` | `CFastVB__UnpackTexels_L8A8ToFloat4` | Unpacks paired luminance/alpha bytes into float4 channels |
| `0x00585b35` | `CFastVB__UnpackTexels_A4L4ToFloat4` | Unpacks A4L4 texels into float4 RGBA channels |
| `0x00585c0b` | `CFastVB__UnpackTexels_L16ToFloat4` | Unpacks 16-bit luminance texels into float4 with replicated RGB and alpha=1.0 |
| `0x00585fa3` | `CFastVB__UnpackTexels_Signed8_8_8_8_ToFloat4` | Unpacks signed 8-8-8-8 packed texels into float4 channels |
| `0x005868d1` | `CFastVB__UnpackTexels_L16A16_ToFloat4` | Unpacks L16/A16 texels to float4 with replicated luminance and explicit alpha |
| `0x00585908` | `CFastVB__InitTexelUnpackVTable_005e9f5c` | Initializes texel-unpack profile object and binds vtable 0x005e9f5c |
| `0x00585924` | `CFastVB__InitTexelUnpackVTable_005e9f6c` | Initializes texel-unpack profile object and binds vtable 0x005e9f6c |
| `0x005859bc` | `CFastVB__InitTexelUnpackVTable_005e9f7c` | Initializes texel-unpack profile object and binds vtable 0x005e9f7c |
| `0x00585bd3` | `CFastVB__TexelUnpackProfile_scalar_deleting_dtor` | Scalar-deleting destructor for texel-unpack profile objects |
| `0x00585bef` | `CFastVB__InitTexelUnpackVTable_005e9fac` | Initializes texel-unpack profile object and binds vtable 0x005e9fac |
| `0x00585c94` | `CFastVB__InitTexelUnpackVTable_005e9fbc` | Initializes texel-unpack profile object and binds vtable 0x005e9fbc |
| `0x0058617c` | `CFastVB__InitTexelUnpackVTable_005ea034` | Initializes texel-unpack profile object and binds vtable 0x005ea034 |
| `0x005862e9` | `CFastVB__InitTexelUnpackVTable_005ea068` | Initializes texel-unpack profile object and binds vtable 0x005ea068 |
| `0x0058669a` | `CFastVB__InitTexelUnpackVTable_005ea0c8` | Initializes texel-unpack profile object and binds vtable 0x005ea0c8 |
| `0x005866b6` | `CFastVB__InitTexelUnpackVTable_005ea0d8` | Initializes texel-unpack profile object and binds vtable 0x005ea0d8 |
| `0x0058675f` | `CFastVB__InitTexelUnpackVTable_005ea0e8` | Initializes texel-unpack profile object and binds vtable 0x005ea0e8 |
| `0x00586994` | `CFastVB__InitTexelUnpackVTable_005ea118` | Initializes texel-unpack profile object and binds vtable 0x005ea118 |
| `0x00586ec7` | `CFastVB__InitTexelUnpackVTable_005ea198` | Initializes texel-unpack profile object and binds vtable 0x005ea198 |
| `0x00586bb7` | `CFastVB__FlushPendingConvertedRows16` | Flushes pending converted rows from float scratch to 16-bit destination pairs |
| `0x0058735a` | `CFastVB__StoreDecodedBlockToScratch` | Stores decoded texel block into scratch buffer |
| `0x005873f8` | `CFastVB__LoadDecodedBlockFromScratch` | Loads decoded texel block from scratch buffer |
| `0x00587daf` | `CFastVB__TexelPackProfile_scalar_deleting_dtor` | Scalar-deleting destructor for texel pack profile |
| `0x00587dee` | `CFastVB__InitTexelUnpackVTable_005ea264` | Initializes texel-unpack profile and binds vtable 0x005ea264 |
| `0x00587e06` | `CFastVB__InitTexelUnpackVTable_005ea274` | Initializes texel-unpack profile and binds vtable 0x005ea274 |
| `0x00587e66` | `CFastVB__TexelCodecProfile_scalar_deleting_dtor` | Scalar-deleting destructor for texel codec profile objects |
| `0x00587e82` | `CFastVB__CreateTexelUnpackProfileByFormat` | Factory creating texel unpack profile object by format id |
| `0x00580120` | `CFastVB__RunDualProfileConversionStage` | Runs dual-profile conversion stage with staging allocation and compatibility checks |
| `0x0058070e` | `CFastVB__InitDualTexelConversionPipeline` | Initializes paired unpack profiles and full conversion pipeline stages |
| `0x005809de` | `CFastVB__ShutdownActiveProfile` | Releases active profile via vtable callbacks and clears pointer |
| `0x00580eef` | `CFastVB__ShutdownActiveProfile_Thunk` | Alias thunk to active-profile shutdown path |
| `0x005866d2` | `CFastVB__UnpackTexels_CallbackPerTexel_Stride4_SetZAOne` | Callback wrapper for stride-4 records with post-write Z/A one-fill |
| `0x00591050` | `CFastVB__ReleaseOwnedObjectAndReset` | Releases owned sub-object via vfunc(`+0x28`) and clears local state fields (`+0x04`, `+0x14`) |
| `0x00592b00` | `CFastVB__ParserContext_Shutdown` | Parser-context shutdown path performing virtual cleanup, release/reset helper, and terminal callback dispatch |
| `0x00592c50` | `CFastVB__ParserContext_Init` | Parser-context constructor/init path seeding callback slots and default `"Bogus message code"` diagnostic string |
| `0x00599258` | `CFastVB__ComputeNodeSpanAndStride` | Recursively computes node span/stride aggregates across node-kind tree branches |
| `0x00599878` | `CFastVB__CloneNodeTreeWithAddRef` | Allocates and clones node tree while AddRef-copying child/interface references with failure cleanup |
| `0x00598a56` | `CFastVB__InitNodeType9` | Initializes node-type 9 record fields and binds vtable `0x005ef250` |
| `0x00598f82` | `CFastVB__NodeType9_scalar_deleting_dtor` | Scalar-deleting destructor for node-type 9 object (`vtable 0x005ef250`) |
| `0x00598b48` | `CFastVB__InitNodeType10` | Initializes node-type 10 record fields and binds vtable `0x005ef260` |
| `0x00598b81` | `CFastVB__NodeType10_dtor` | Destructor body for node-type 10 releasing owned children/resources then base cleanup |
| `0x00598fa4` | `CFastVB__NodeType10_scalar_deleting_dtor` | Scalar-deleting wrapper for node-type 10 destructor with optional free flag |
| `0x005988f5` | `CFastVB__CompareNodeValuesByTagAndPayload` | Typed payload comparator handling scalar/string/pointer payload forms by node tag |
| `0x00598873` | `CFastVB__CloneNodeChainWithAddRef` | Clones linked node chain and AddRef-copies referenced payload objects with failure rollback |
| `0x00598d6b` | `CFastVB__InitNodeType13` | Initializes node-type 13 storage defaults and binds vtable `0x005ef270` |
| `0x00599b13` | `CFastVB__SetParseErrorAndMarkStateDirty` | Emits parse diagnostic message and marks parser state/error flags dirty |
| `0x00599b69` | `CFastVB__NodeTreeHasBitFlag0x200` | Recursively walks node tree and returns whether payload bit `0x200` is present |
| `0x00592530` | `CFastVB__JpegParser_ReadAndValidateSOI` | Validates JPEG SOI marker and parser preconditions before frame decode |
| `0x005913b0` | `CFastVB__JpegParser_ResetFrameState` | Clears parser/frame accumulators and resets component-state fields |
| `0x00591720` | `CFastVB__JpegParser_ParseSOFComponents` | Parses SOF component descriptors with sampling/table selector fields |
| `0x00596589` | `CFastVB__SolveScalarEndpointPairFromSamples` | Solves scalar endpoint pair from sample spans for compression fit |
| `0x005968a4` | `CFastVB__SolveVectorEndpointPairFromSamples` | Solves weighted vector endpoint pair from sample set for fit path |
| `0x00596e23` | `CFastVB__QuantizeScalarBlockIndices` | Quantizes scalar samples into selector indices with iterative residual distribution |
| `0x00597a61` | `CFastVB__PackScalarBlock_4BitEndpoints` | Packs 16 scalar samples into 4-bit endpoint/index representation |
| `0x00597b87` | `CFastVB__PackScalarBlock_InterpolatedEndpoints` | Computes/interpolates scalar endpoints and emits per-sample selector indices |
| `0x0059c610` | `CFastVB__ReleaseOwnedObjectAndReset_Core` | Core release/reset helper for owned object pointer and local state fields |
| `0x0059c700` | `CFastVB__CopyBlockRows128Bytes` | Copies `param_3` rows of 128-byte block data between buffers |
| `0x0059a21f` | `CFastVB__AreNodeTreesCompatible` | Recursively compares node trees/types with exact-vs-compatible mode support |
| `0x0059a54d` | `CFastVB__ScoreNodeTreeMatch` | Computes compatibility score between requested/candidate node trees |
| `0x0059a71a` | `CFastVB__SelectBestNodeTreeMatch` | Selects best candidate node-tree match from rule lists by minimal score |
| `0x00598f60` | `CFastVB__NodeType8_scalar_deleting_dtor` | Scalar-deleting destructor wrapper for node-type-8 object (`vtable 0x005ef240`) |
| `0x005997a5` | `CFastVB__InitNodeType17` | Initializes node-type-17 storage and binds node vtable `0x005ef374` |
| `0x00598474` | `CFastVB__InitDispatchOpsFromFeatureFlags` | Initializes dispatch-operation table entries from active runtime feature flags |
| `0x0059f6dd` | `CFastVB__BroadcastMatrix4x4ToSIMDLanes` | Broadcasts matrix components into SIMD lane layout for downstream dispatch ops |
| `0x005a2a61` | `CFastVB__DispatchOp_TransformVec2ByMatrix4` | Dispatch operation transforming Vec2 coordinates through matrix-form parameters |
| `0x005aa0cc` | `CFastVB__DispatchOp_ComposeTransformFromOptionalInputs_Scalar` | Scalar composition dispatch path combining optional transform inputs into output state |
| `0x005aa2f2` | `CFastVB__DispatchOp_ComposeTransformFromOptionalInputs_SIMD` | SIMD composition dispatch path combining optional transform inputs into output state |
| `0x005a38c0` | `CFastVB__DispatchOp_TransformVec4ArrayByMatrix4` | Iterates input vectors and applies 4x4 matrix multiplication with configurable src/dst strides |
| `0x005a47f2` | `CFastVB__DispatchOp_ExtractAxisAndOptionalAngle` | Copies axis-vector components and optionally emits an angle-like scalar metric |
| `0x005a7617` | `CFastVB__DispatchOp_BuildRotationMatrixFromEulerAngles` | Computes trigonometric terms and writes a 4x4 rotation matrix-style output block |
| `0x005a7cf0` | `CFastVB__DispatchOp_BuildRotationMatrixFromAxisAngleVector` | Normalizes axis-angle vector input then emits a 4x4 rotation matrix-style output block |
| `0x005b3440` | `CFastVB__JpegEntropy_EncodeBlockZigZagHuffman` | Zig-zag block entropy encoder that emits run-length/value bits through JPEG-style bitstream helper |
| `0x005b35b0` | `CFastVB__JpegEntropy_WriteMarkerAndResetDcPredictors` | Emits marker bytes and resets per-component DC predictor/accumulator state |
| `0x005b86c0` | `CFastVB__FastAcosApprox_Scalar` | Scalar arccos-approximation kernel used by axis/angle extraction dispatch paths |
| `0x005b8ca0` | `CFastVB__FastTrigPairApprox_Scalar` | Scalar trigonometric pair approximation kernel used by rotation-matrix dispatch builders |
| `0x005a7e09` | `CFastVB__DispatchOp_ComposeMatrixFromOptionalTransforms` | Multi-branch dispatch path composing output matrix from optional transform inputs and basis blocks |
| `0x005ad590` | `CFastVB__JpegEntropy_CommitAndResetBlockState` | Commits entropy progress counters and resets per-block working state before next encode step |
| `0x0055f506` | `CRT__FReadCore` | Core CRT `fread` helper dispatching buffered read logic with item-size/count parameters |
| `0x0055f5ee` | `Win32__FindFirstFileWithMeta` | Wrapper around `FindFirstFile` path with metadata copyout into caller struct |
| `0x0055f6bb` | `Win32__FindNextFileWithMeta` | Wrapper around `FindNextFile` path with metadata copyout into caller struct |
| `0x0055fe26` | `CRT__LockRouteByAddress` | Routes lock/unlock path by encoded address class in CRT lock table |
| `0x0055fe55` | `CRT__LockRouteByIndex` | Routes lock/unlock path by lock-index mode and updates CRT lock bookkeeping |
| `0x0055f2e8` | `CRT__WcsCmp` | UTF-16 lexical compare returning {-1,0,1} ordering |
| `0x0055f783` | `Win32__FindCloseWithErrno` | Calls `FindClose`; maps failure into CRT errno path |
| `0x0055fe78` | `CRT__UnlockRouteByAddress` | Address-routed unlock companion to `CRT__LockRouteByAddress` |
| `0x0055fea7` | `CRT__UnlockRouteByIndex` | Index-routed unlock companion to `CRT__LockRouteByIndex` |
| `0x0055feec` | `CRT__FTellAdjusted` | Stream position helper with text-mode newline adjustment path |
| `0x0055eb3d` | `CRT__RoundToIntegerRespectingControlWord` | FPU control-word aware double rounding helper |
| `0x0055ec4a` | `CRT__HeapAllocBase` | CRT heap allocation base helper with small-block/HeapAlloc routing |
| `0x0055f085` | `CRT__FreeBase` | CRT heap free base helper with small-block/HeapFree routing |
| `0x0055f0ef` | `CRT__UnlockHeapLock` | Heap lock unlock wrapper for lock id 9 |
| `0x0055f147` | `CRT__UnlockHeapLock_Alt` | Alternate heap lock unlock wrapper for lock id 9 |
| `0x0055da8d` | `CRT__InitFloatConversionDispatchTable` | Initializes CRT float-conversion callback dispatch pointers |
| `0x0055dccd` | `CRT__Acos` | CRT arccos helper with FPU-control and error-path handling |
| `0x0055df28` | `CRT__OnexitTablePush` | Pushes callback pointer into CRT onexit table with growth fallback |
| `0x0055dfa6` | `CRT__RegisterOnexitFunction` | Front-end wrapper for CRT onexit registration |
| `0x0055e42a` | `Win32__CaptureSystemTimeAsFileTimeTicks` | Captures current system FILETIME into 64-bit global tick value |
| `0x0055d6a0` | `CRT__SehPopExceptionFrameAndJump` | Pops one exception-registration frame and tail-jumps to callback target |
| `0x0055d6db` | `CRT__SehLockUnlockAndJump` | Emits lock/unlock pair then tail-jumps to callback target |
| `0x0055d6e2` | `CRT__SehRtlUnwindAndRestoreFrame` | Calls `RtlUnwind`, clears unwind-state bit, and restores exception-list linkage |
| `0x0055d767` | `CRT__SehInvokeCallSettingFrame12` | Builds temporary exception frame and dispatches through `__CallSettingFrame_12` |
| `0x0055d7bb` | `CRT__SehCallback_Call_005602d2` | SEH callback shim that forwards control to `CRT__SehDispatchWithScopeTable` |
| `0x0055da5e` | `CRT__SehStoreFrameGlobals` | Stores frame/EAX context into CRT globals used by downstream runtime bridge helpers |
| `0x0055da76` | `CRT__InitRuntimeFromStoredFrameGlobals` | Runtime bridge init helper that seeds setup paths from stored frame globals |
| `0x0055db72` | `CRT__EhVectorDestructorIterator_IfNoException` | Invokes `eh_vector_destructor_iterator` only on no-exception guard path |
| `0x0055e412` | `CRT__CallHelper_00564a0b_NoFlags` | Thin wrapper forwarding args to helper `0x00564a0b` with trailing flag `0` |
| `0x0055e45f` | `CRT__CallHelper_00564c09_WithAutoUnlock` | Dispatches helper `0x00564c09` and releases lock context via address-routed unlock |
| `0x005602d2` | `CRT__SehDispatchWithScopeTable` | Central SEH dispatch callback that validates scope table state before handler lookup/unwind routing |
| `0x0056036d` | `CRT__SehLookupAndInvokeScopeHandler` | Walks scope records, matches state windows, and invokes matching handler callback routes |
| `0x00560627` | `CRT__SehUnwindToTargetState` | Iteratively unwinds exception-state index toward target and executes cleanup callbacks |
| `0x005606c5` | `CRT__SehUnwindAndResumeSearch` | Performs unwind cleanup and resumes exception-search dispatch through continuation callback |
| `0x00560cb1` | `CRT__InitFpuControlWord_0x10000_0x30000` | Initializes runtime FPU control mask/value pair through helper `CTexture__Helper_0056947e` |
| `0x0055fc35` | `CRT__IsFloat10Integral_0055fc35` | Floating-point helper that gates integral-path handling by comparing rounded value against original input |
| `0x00561590` | `CRT__Exp2FromFpuCore_00561590` | FPU exponentiation core using `f2xm1` plus `fscale` sequence |
| `0x005615a5` | `CRT__SetFpuControlWordMasked_005615a5` | Applies masked FPU control-word update (`(arg & 0x300) | 0x7f`) and loads it via `FLDCW` |
| `0x005615bc` | `CRT__MapExponentFlagToClassCode_005615bc` | Maps exponent/status bit test (`0x80000`) into class code return values (`7` or `1`) |
| `0x00561618` | `CRT__ExtractFiniteExponentMaskOrPassThrough_00561618` | Returns finite exponent mask bits or pass-through bits for infinity/NaN patterns |
| `0x00560e28` | `CRT__FormatFloatScientificFromLongDouble` | Wrapper that converts long-double decomposition and dispatches to scientific-format core output builder |
| `0x00560e89` | `CRT__FormatFloatScientificCore` | Scientific float text emitter writing sign/mantissa plus exponent suffix (`e+000`) |
| `0x00560f4b` | `CRT__FormatFloatFixedFromLongDouble` | Wrapper that converts long-double decomposition and dispatches to fixed-format core output builder |
| `0x00560fa0` | `CRT__FormatFloatFixedCore` | Fixed float text emitter handling sign, decimal insertion, and precision/zero padding |
| `0x00561047` | `CRT__FormatFloatGeneral_SelectStyle` | `%g`-style selector that chooses scientific vs fixed emitter based on exponent range |
| `0x0055d731` | `CRT__SehDispatchWithScopeTable_Thunk_0055d731` | Thin thunk that directly forwards to `CRT__SehDispatchWithScopeTable` |
| `0x0055fa62` | `CRT__PowCore_0055fa62` | Disassembly-evidenced `pow` core path using `FYL2X` plus exp2 flow and extensive edge-case branches |
| `0x00561530` | `CRT__ReportMathErrorAndRestoreControlWord_00561530` | Calls math-error helper then restores saved control word before returning |
| `0x00560d2a` | `CRT__InsertDecimalSeparatorBeforeExponent_00560d2a` | Inserts locale decimal separator before exponent marker and shifts mantissa tail bytes |
| `0x0056004d` | `CDXTexture__AsciiToLowerInPlace` | Lowercases ASCII `A..Z` in-place on C-string buffers with lock-guarded fallback route |
| `0x00560b2c` | `CTexture__InitializeThreadLocalState` | Allocates/install TLS state record for texture runtime and seeds per-thread defaults |
| `0x00560b80` | `CTexture__InitializeThreadLocalRecordDefaults` | Initializes thread-local texture record defaults (`+0x50` dispatch pointer, `+0x14` flag) |
| `0x00561150` | `CTexture__InitializeGlobalCriticalSections` | Initializes four global texture/runtime critical sections used by lock routes |
| `0x005602ae` | `CDXTexture__ReportFatalAndExitProcess` | Runs fatal-report helper chain and terminates process via `ExitProcess(0xff)` |
| `0x00560bfa` | `CDXTexture__InvokeTlsCleanupCallbackAndFinalize` | Invokes optional TLS-context cleanup callback (`context+0x60`) then executes common finalize helper |
| `0x00560c5b` | `CDXTexture__InvokeGlobalCleanupCallbackAndFinalize` | Invokes global cleanup callback pointer when present, then executes shared finalize helper |
| `0x00560d01` | `CDXTexture__ProbeProcessorFeaturePresentOrFallback` | Dynamically probes `IsProcessorFeaturePresent`; falls back to helper gate when unavailable |
| `0x0055dd7b` | `CFastVB__RunStaticInitRangesWithOptionalCallback` | Runs optional callback then processes two static init-range tables through shared helper |
| `0x0055e183` | `CFastVB__DispatchLockedRoute_6533e0` | Locks route key `0x6533e0`, dispatches helper call, then unlocks |

---

## Function Details

### CFastVB__Create (0x0051a270)

**Purpose:** Creates and initializes a fast vertex buffer for dynamic quad rendering.

**Line Number:** 41 (0x29)

**Signature:**
```cpp
int __thiscall CFastVB::Create(CFastVB* this);
```

**Behavior:**
1. Early return if vertex buffer already exists (`*this != 0`)
2. Allocate CVBuffer object (0x2c bytes)
3. Call `CVBuffer::CreateDynamic(maxVertices=0x144, vertexSize=0x1c)`
4. On success, call `FUN_00513d20()` to register buffer
5. On failure, release buffer and return error code

**Returns:** HRESULT (0 = already exists, negative = error, positive = success)

---

### CFastVB__Destroy (0x0051a340)

**Purpose:** Releases the vertex buffer and the shared static index buffer.

**Signature:**
```cpp
void __thiscall CFastVB::Destroy(CFastVB* this);
```

**Behavior:**
1. If vertex buffer exists, call Release(1) via vtable and set to NULL
2. If static index buffer (`DAT_00897a90`) exists, release it and set to NULL

**Note:** The static index buffer is shared across all CFastVB instances - destroying one destroys for all.

---

### CFastVB__LockAligned (0x0051a380)

**Purpose:** Lock vertex buffer with 4-vertex alignment (for quad rendering).

**Signature:**
```cpp
ushort __thiscall CFastVB::LockAligned(CFastVB* this, void** ppData, int vertexCount);
```

**Behavior:**
1. Early return 0xFFFF if no vertex buffer
2. Align current write offset to multiple of 4: `offset = ((offset + 3) >> 2) << 2`
3. If buffer is empty or would overflow, reset to start with DISCARD flag (0x2800)
4. Otherwise use NOOVERWRITE flag (0x1800)
5. Call `CVBuffer::LockRange()` with calculated byte offsets
6. Update write offset and store start vertex

**Returns:** Start vertex index, or 0xFFFF on failure

---

### CFastVB__Lock (0x0051a430)

**Purpose:** Lock vertex buffer for writing (may flush if needed).

**Signature:**
```cpp
ushort __thiscall CFastVB::Lock(CFastVB* this, void** ppData, int vertexCount);
```

**Behavior:**
1. Return 0xFFFF if no vertex buffer
2. If start vertex is -1 (no current batch), delegate to LockAligned
3. If current batch is empty or would overflow:
   - Call `Render()` to flush pending vertices
   - Reset state and use DISCARD flag (0x2800)
4. Otherwise use NOOVERWRITE flag (0x1800) after unlocking
5. Lock the requested range and update vertex count

**Returns:** Start vertex index, or 0xFFFF on failure

---

### CFastVB__Render (0x0051a510)

**Purpose:** Flush all pending vertices to GPU as indexed triangles.

**Line Number:** 195 (0xC3)

**Signature:**
```cpp
void __thiscall CFastVB::Render(CFastVB* this);
```

**Behavior:**
1. Early return if no pending vertices (start vertex == -1)
2. Unlock vertex buffer
3. Set stream source to vertex buffer via D3D device vtable
4. Create static index buffer if not exists:
   - Allocate index buffer (0x1d4c = 7500 bytes)
   - Fill with quad indices: [0,1,2,2,3,0], [4,5,6,6,7,4], ...
5. Set indices via D3D device
6. Call draw primitives: `FUN_00513c70(4, startVertex, vertexCount, indexCount, primitiveCount)`
7. Reset start vertex to -1 and vertex count to 0

**Index Pattern (per quad):**
```
Triangle 1: [i+0, i+1, i+2]
Triangle 2: [i+2, i+3, i+0]
```

---

## Global Data

| Address | Name | Type | Description |
|---------|------|------|-------------|
| `0x00897a90` | DAT_00897a90 | CIBuffer* | Shared static index buffer for quad rendering |
| `0x00888a50` | DAT_00888a50 | IDirect3DDevice8* | Direct3D device pointer |

## Lock Flags

| Value | Name | Description |
|-------|------|-------------|
| `0x1800` | D3DLOCK_NOOVERWRITE | Lock without overwriting (append mode) |
| `0x2800` | D3DLOCK_DISCARD | Discard contents (start fresh) |

## Usage Pattern

```cpp
// Typical usage for rendering quads
CFastVB fastVB;
fastVB.Create();

// Lock buffer for N vertices (N/4 quads)
void* pData;
ushort startVertex = fastVB.Lock(&pData, numVertices);
if (startVertex != 0xFFFF) {
    // Fill vertex data
    memcpy(pData, vertices, numVertices * 0x1c);
}

// Flush to GPU when batch complete
fastVB.Render();

// Cleanup
fastVB.Destroy();
```

## Cross-References

### Callers of CFastVB__Create
- `FUN_00540010` at 0x00540057 (likely particle system init)
- `FUN_005528b0` at 0x0055294c
- `FUN_00555be0` at 0x00556296

### Callers of CFastVB__Render
- `FUN_00427210` (called 4 times) - main rendering function
- `CFastVB__Lock` at 0x0051a490, 0x0051a4e2 (buffer full flush)
- `FUN_00540010` at 0x00540613

## Related Systems

- **CVBuffer** - Underlying vertex buffer wrapper
- **CIBuffer** - Index buffer class (used for static quad indices)
- **Direct3D 8** - Native graphics API
