//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionTag;

import java.util.HashSet;
import java.util.Set;

public class ApplyTextureDispatchInterpolationTailWave887 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String signature;
        final String comment;
        final String[] tags;

        Spec(String address, String name, String signature, String comment, String[] tags) {
            this.address = address;
            this.name = name;
            this.signature = signature;
            this.comment = comment;
            this.tags = tags;
        }
    }

    private static class Stats {
        int updated = 0;
        int skipped = 0;
        int renamed = 0;
        int wouldRename = 0;
        int missing = 0;
        int bad = 0;
    }

    private boolean isDryRun(String mode) {
        if (mode == null || mode.trim().isEmpty()) {
            return true;
        }
        String normalized = mode.trim().toLowerCase();
        if (normalized.equals("dry") || normalized.equals("dry-run") || normalized.equals("true") || normalized.equals("1")) {
            return true;
        }
        if (normalized.equals("apply") || normalized.equals("no-dry") || normalized.equals("false") || normalized.equals("0")) {
            return false;
        }
        throw new IllegalArgumentException("Unrecognized mode: " + mode + " (use dry/apply)");
    }

    private Address addr(String addressText) {
        if (!addressText.startsWith("0x") && !addressText.startsWith("0X")) {
            addressText = "0x" + addressText;
        }
        Address address = toAddr(addressText);
        if (address == null) {
            throw new IllegalArgumentException("Bad address: " + addressText);
        }
        return address;
    }

    private Function functionAtEntry(String addressText) {
        Address address = addr(addressText);
        Function fn = getFunctionAt(address);
        if (fn == null) {
            Function containing = getFunctionContaining(address);
            if (containing != null && containing.getEntryPoint().equals(address)) {
                fn = containing;
            }
        }
        return fn;
    }

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "texture-dispatch-interpolation-tail-wave887",
            "wave887-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "signature-verified",
            "stack-locked-abi",
            "hidden-register-context",
            "texture-dispatch-interpolation-tail",
            "dispatch-table",
            "important-render-infrastructure",
            "raw-commentless-tail"
        };
        String[] result = new String[common.length + extras.length];
        System.arraycopy(common, 0, result, 0, common.length);
        System.arraycopy(extras, 0, result, common.length, extras.length);
        return result;
    }

    private Set<String> tagNames(Function fn) {
        Set<String> names = new HashSet<>();
        for (FunctionTag tag : fn.getTags()) {
            names.add(tag.getName());
        }
        return names;
    }

    private boolean hasAllTags(Function fn, String[] tags) {
        Set<String> existing = tagNames(fn);
        for (String tag : tags) {
            if (!existing.contains(tag)) {
                return false;
            }
        }
        return true;
    }

    private boolean needsUpdate(Function fn, Spec spec) {
        if (!fn.getName().equals(spec.name)) {
            return true;
        }
        if (!fn.getSignature().toString().equals(spec.signature)) {
            return true;
        }
        String existingComment = fn.getComment();
        if (existingComment == null || !existingComment.equals(spec.comment)) {
            return true;
        }
        return !hasAllTags(fn, spec.tags);
    }

    private void verifyReadBack(Spec spec) throws Exception {
        Function readBack = functionAtEntry(spec.address);
        if (readBack == null) {
            throw new IllegalStateException("Read-back missing at " + spec.address);
        }
        if (!readBack.getName().equals(spec.name)) {
            throw new IllegalStateException("Read-back name mismatch at " + spec.address + ": " + readBack.getName());
        }
        String actualSignature = readBack.getSignature().toString();
        if (!actualSignature.equals(spec.signature)) {
            throw new IllegalStateException("Read-back signature mismatch at " + spec.address + ": " + actualSignature);
        }
        String readComment = readBack.getComment();
        if (readComment == null || !readComment.equals(spec.comment)) {
            throw new IllegalStateException("Read-back comment mismatch at " + spec.address);
        }
        if (!hasAllTags(readBack, spec.tags)) {
            throw new IllegalStateException("Read-back tag mismatch at " + spec.address);
        }
    }

    private void applySpec(Spec spec, boolean dryRun, Stats stats) {
        try {
            Function fn = functionAtEntry(spec.address);
            if (fn == null) {
                stats.missing++;
                println("MISSING: " + spec.address + " " + spec.name);
                return;
            }
            if (!fn.getName().equals(spec.name)) {
                stats.bad++;
                println("BADNAME: " + spec.address + " actual=" + fn.getName() + " expected=" + spec.name);
                return;
            }
            if (!needsUpdate(fn, spec)) {
                stats.skipped++;
                println("SKIP: " + spec.address + " " + fn.getSignature());
                return;
            }
            if (dryRun) {
                stats.skipped++;
                println("DRY: " + spec.address + " " + spec.signature);
                return;
            }

            fn.setComment(spec.comment);
            for (String tag : spec.tags) {
                fn.addTag(tag);
            }
            verifyReadBack(spec);
            stats.updated++;
            println("OK: " + spec.address + " " + spec.signature);
            Thread.sleep(50);
        } catch (Exception ex) {
            stats.bad++;
            println("BAD: " + spec.address + " " + spec.name + " " + ex.getMessage());
        }
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");

        Spec[] specs = new Spec[] {
            new Spec(
                "0x005759b6",
                "CFastVB__DispatchIndirect_00657014",
                "void CFastVB__DispatchIndirect_00657014(void)",
                "Wave887 static read-back: CPU-feature dispatch-table initializer thunk for global pointer DAT_00657014. The body calls CFastVB__InitDispatchTableByCpuFeature(1) and then tail-jumps through dword ptr [0x00657014]; companion no-init thunk CDXTexture__PackTexels_DispatchIndirect_005759c3 jumps through the same slot, and texture pack callbacks call that no-init thunk. Static retail Ghidra evidence only; exact table-slot target, CPU feature policy, runtime texel-pack behavior, BEA patching, and rebuild parity remain unproven.",
                tags("cpu-dispatch-init", "slot-00657014", "computed-jump", "pack-texel-dispatch")
            ),
            new Spec(
                "0x005759c3",
                "CDXTexture__PackTexels_DispatchIndirect_005759c3",
                "void CDXTexture__PackTexels_DispatchIndirect_005759c3(void)",
                "Wave887 static read-back: no-init texel-pack dispatch thunk. The body tail-jumps through dword ptr [0x00657014]; xrefs come from CDXTexture__PackTexels_CallbackPerTexel_RepeatA, CDXTexture__PackTexels_CallbackPerTexel_RepeatB, and CDXTexture__PackTexels_CallbackPerTexel_Once. Static retail Ghidra evidence only; exact table-slot target, pixel format semantics, runtime packing behavior, BEA patching, and rebuild parity remain unproven.",
                tags("slot-00657014", "computed-jump", "pack-texel-dispatch", "no-init-thunk")
            ),
            new Spec(
                "0x00575a58",
                "CFastVB__DispatchIndirect_00657018",
                "void CFastVB__DispatchIndirect_00657018(void)",
                "Wave887 static read-back: CPU-feature dispatch-table initializer thunk for global pointer DAT_00657018. The body calls CFastVB__InitDispatchTableByCpuFeature(1) and tail-jumps through dword ptr [0x00657018]; companion no-init thunk CDXTexture__UnpackTexels_DispatchIndirect_00575a65 jumps through the same slot. Static retail Ghidra evidence only; exact table-slot target, CPU feature policy, runtime texel-unpack behavior, BEA patching, and rebuild parity remain unproven.",
                tags("cpu-dispatch-init", "slot-00657018", "computed-jump", "unpack-texel-dispatch")
            ),
            new Spec(
                "0x00575a65",
                "CDXTexture__UnpackTexels_DispatchIndirect_00575a65",
                "void CDXTexture__UnpackTexels_DispatchIndirect_00575a65(void)",
                "Wave887 static read-back: no-init texel-unpack dispatch thunk. The body tail-jumps through dword ptr [0x00657018]; xrefs come from CDXTexture__UnpackTexels_CallbackPerTexel_Stride2_SetRGBAOne, CFastVB__UnpackTexels_CallbackPerTexel_Stride4_SetZAOne, and CDXTexture__UnpackTexels_CallbackSingleTexel. Static retail Ghidra evidence only; exact table-slot target, pixel format semantics, runtime unpack behavior, BEA patching, and rebuild parity remain unproven.",
                tags("slot-00657018", "computed-jump", "unpack-texel-dispatch", "no-init-thunk")
            ),
            new Spec(
                "0x00575b1d",
                "CTexture__InterpolateVec2Cubic_Dispatch",
                "int CTexture__InterpolateVec2Cubic_Dispatch(void)",
                "Wave887 static read-back: CPU-feature dispatch wrapper for six-argument vec2 cubic interpolation. The body calls CFastVB__InitDispatchTableByCpuFeature(1), forwards the visible stack block to the function pointer at 0x00656f74, and returns with RET 0x18. Static retail Ghidra evidence only; exact pointer target, stack ABI, runtime interpolation behavior, BEA patching, and rebuild parity remain unproven.",
                tags("cpu-dispatch-init", "slot-00656f74", "computed-call", "vec2-cubic", "ret-0x18")
            ),
            new Spec(
                "0x00575b47",
                "Math__InterpolateVec2Cubic",
                "int Math__InterpolateVec2Cubic(void)",
                "Wave887 static read-back: stack-locked scalar vec2 cubic interpolation body. The decompile forms t^2/t^3 basis weights, blends four vec2 control inputs into the output pointer, and returns the output pointer with RET 0x18; constants at 0x005e9318 and 0x005e6a34 provide the Hermite/cubic basis scale and unit term. Static retail Ghidra evidence only; exact source helper identity, floating-point edge behavior, runtime math parity, BEA patching, and rebuild parity remain unproven.",
                tags("vec2-cubic", "scalar-math", "hermite-basis", "ret-0x18")
            ),
            new Spec(
                "0x00575bd5",
                "CTexture__InterpolateVec2CubicNormalized_Dispatch",
                "int CTexture__InterpolateVec2CubicNormalized_Dispatch(void)",
                "Wave887 static read-back: CPU-feature dispatch wrapper for normalized vec2 cubic interpolation. The body calls CFastVB__InitDispatchTableByCpuFeature(1), forwards six stack arguments to function pointer 0x00656fec, and returns with RET 0x18. Static retail Ghidra evidence only; exact table-slot target, stack ABI, runtime normalized interpolation behavior, BEA patching, and rebuild parity remain unproven.",
                tags("cpu-dispatch-init", "slot-00656fec", "computed-call", "vec2-cubic-normalized", "ret-0x18")
            ),
            new Spec(
                "0x00575bff",
                "Math__InterpolateVec2CubicNormalized",
                "int Math__InterpolateVec2CubicNormalized(void)",
                "Wave887 static read-back: stack-locked scalar normalized vec2 cubic interpolation body. The body derives cubic basis weights from the t parameter, normalizes the blended vec2 result before storing it to the output pointer, and returns with RET 0x18. Static retail Ghidra evidence only; exact normalization policy, floating-point edge behavior, runtime math parity, BEA patching, and rebuild parity remain unproven.",
                tags("vec2-cubic-normalized", "scalar-math", "normalizes-result", "ret-0x18")
            ),
            new Spec(
                "0x00575cae",
                "CFastVB__DispatchIndirect_00656ff0_ReturnInt",
                "int CFastVB__DispatchIndirect_00656ff0_ReturnInt(void)",
                "Wave887 static read-back: CPU-feature dispatch wrapper for a six-argument return-int math/texture slot. The body calls CFastVB__InitDispatchTableByCpuFeature(1), forwards the visible stack block to function pointer 0x00656ff0, and returns with RET 0x18. Static retail Ghidra evidence only; exact table-slot target, ABI, runtime behavior, BEA patching, and rebuild parity remain unproven.",
                tags("cpu-dispatch-init", "slot-00656ff0", "computed-call", "return-int-dispatch", "ret-0x18")
            ),
            new Spec(
                "0x00575cdd",
                "Math__InterpolateVec2ByUV",
                "int Math__InterpolateVec2ByUV(void)",
                "Wave887 static read-back: stack-locked scalar vec2 bilinear/UV interpolation body. The body stores base + (u direction * u) + (v direction * v) into the output vec2 pointer and returns with RET 0x18. Static retail Ghidra evidence only; exact source helper identity, coordinate convention, runtime math parity, BEA patching, and rebuild parity remain unproven.",
                tags("vec2-uv-interpolate", "scalar-math", "ret-0x18")
            ),
            new Spec(
                "0x00575d20",
                "CDXTexture__DispatchPtr00656f30_WithInit",
                "void CDXTexture__DispatchPtr00656f30_WithInit(void)",
                "Wave887 static read-back: CPU-feature dispatch-table initializer thunk for slot 0x00656f30. The body calls CFastVB__InitDispatchTableByCpuFeature(1) and tail-jumps through dword ptr [0x00656f30]; companion CFastVB__DispatchIndirect_00656f30 is the no-init thunk. Static retail Ghidra evidence only; exact table-slot target, transform-batch ABI, runtime behavior, BEA patching, and rebuild parity remain unproven.",
                tags("cpu-dispatch-init", "slot-00656f30", "computed-jump", "transform-dispatch")
            ),
            new Spec(
                "0x00575d2d",
                "CFastVB__DispatchIndirect_00656f30",
                "void CFastVB__DispatchIndirect_00656f30(void)",
                "Wave887 static read-back: no-init dispatch thunk for slot 0x00656f30. The body tail-jumps through dword ptr [0x00656f30]; direct callers include CFastVB__DispatchOp_TransformVec4BatchW_0059fa5d and CFastVB__DispatchOp_TransformVec4BatchW_Alt_005a1e5b. Static retail Ghidra evidence only; exact table-slot target, transform-batch ABI, runtime behavior, BEA patching, and rebuild parity remain unproven.",
                tags("slot-00656f30", "computed-jump", "transform-dispatch", "no-init-thunk")
            ),
            new Spec(
                "0x00575d44",
                "CDXTexture__DispatchPtr00656f54_WithInit",
                "void CDXTexture__DispatchPtr00656f54_WithInit(void)",
                "Wave887 static read-back: CPU-feature dispatch-table initializer thunk for slot 0x00656f54. The body calls CFastVB__InitDispatchTableByCpuFeature(1) and tail-jumps through dword ptr [0x00656f54]; companion CFastVB__DispatchIndirect_00656f54 is the no-init thunk. Static retail Ghidra evidence only; exact table-slot target, projected transform ABI, runtime behavior, BEA patching, and rebuild parity remain unproven.",
                tags("cpu-dispatch-init", "slot-00656f54", "computed-jump", "projected-transform-dispatch")
            ),
            new Spec(
                "0x00575d51",
                "CFastVB__DispatchIndirect_00656f54",
                "void CFastVB__DispatchIndirect_00656f54(void)",
                "Wave887 static read-back: no-init dispatch thunk for slot 0x00656f54. The body tail-jumps through dword ptr [0x00656f54]; direct callers include CFastVB__DispatchOp_TransformProjectVec4Batch_0059fbeb and CFastVB__DispatchOp_TransformProjectVec4Batch_Alt_005a1fe9. Static retail Ghidra evidence only; exact table-slot target, projected transform ABI, runtime behavior, BEA patching, and rebuild parity remain unproven.",
                tags("slot-00656f54", "computed-jump", "projected-transform-dispatch", "no-init-thunk")
            ),
            new Spec(
                "0x00575d68",
                "CMeshCollisionVolume__DispatchPtr00656f44_WithInit",
                "void CMeshCollisionVolume__DispatchPtr00656f44_WithInit(void)",
                "Wave887 static read-back: CPU-feature dispatch-table initializer thunk for slot 0x00656f44. The body calls CFastVB__InitDispatchTableByCpuFeature(1) and tail-jumps through dword ptr [0x00656f44]; companion CFastVB__DispatchIndirect_00656f44 is the no-init thunk. Static retail Ghidra evidence only; exact owner provenance, no-offset transform ABI, runtime behavior, BEA patching, and rebuild parity remain unproven.",
                tags("cpu-dispatch-init", "slot-00656f44", "computed-jump", "mesh-collision-transform-dispatch")
            ),
            new Spec(
                "0x00575d75",
                "CFastVB__DispatchIndirect_00656f44",
                "void CFastVB__DispatchIndirect_00656f44(void)",
                "Wave887 static read-back: no-init dispatch thunk for slot 0x00656f44. The body tail-jumps through dword ptr [0x00656f44]; direct callers include CFastVB__DispatchOp_TransformVec4Batch_NoOffset_0059fd51 and CFastVB__DispatchOp_TransformVec4Batch_NoOffset_Alt_005a214f. Static retail Ghidra evidence only; exact table-slot target, no-offset transform ABI, runtime behavior, BEA patching, and rebuild parity remain unproven.",
                tags("slot-00656f44", "computed-jump", "no-offset-transform-dispatch", "no-init-thunk")
            ),
            new Spec(
                "0x00575d8c",
                "CDXTexture__DispatchPtr00656f4c_WithInit",
                "void CDXTexture__DispatchPtr00656f4c_WithInit(void)",
                "Wave887 static read-back: CPU-feature dispatch-table initializer thunk for slot 0x00656f4c. The body calls CFastVB__InitDispatchTableByCpuFeature(1) and tail-jumps through dword ptr [0x00656f4c]; companion Runtime__CallIndirectThunk_00575d99 is the no-init thunk. Static retail Ghidra evidence only; exact owner provenance, matrix/quaternion or texel-pack slot identity, runtime behavior, BEA patching, and rebuild parity remain unproven.",
                tags("cpu-dispatch-init", "slot-00656f4c", "computed-jump", "mixed-runtime-dispatch")
            ),
            new Spec(
                "0x00575d99",
                "Runtime__CallIndirectThunk_00575d99",
                "void Runtime__CallIndirectThunk_00575d99(void)",
                "Wave887 static read-back: no-init indirect thunk for slot 0x00656f4c. The body tail-jumps through dword ptr [0x00656f4c]; callers include Math__BuildAxisAngleRotationMatrix, CFastVB__BuildAxisAngleQuaternion, CTexture__PackTexels_Dither_Bits8_8_FromAuxLookup, and an interior call at 0x00578305. Static retail Ghidra evidence only; exact table-slot target, mixed math/texel-pack ABI, runtime behavior, BEA patching, and rebuild parity remain unproven.",
                tags("slot-00656f4c", "computed-jump", "mixed-runtime-dispatch", "no-init-thunk")
            ),
            new Spec(
                "0x00575dc9",
                "CFastVB__HermiteInterpolateVec3",
                "int CFastVB__HermiteInterpolateVec3(void)",
                "Wave887 static read-back: stack-locked scalar vec3 cubic/Hermite interpolation body. The decompile forms t^2/t^3 basis weights, blends four vec3 inputs into the output pointer, and returns that output pointer with RET 0x18; constants at 0x005e9318 and 0x005e6a34 match the vec2 cubic basis pattern. Static retail Ghidra evidence only; exact source helper identity, floating-point edge behavior, runtime math parity, BEA patching, and rebuild parity remain unproven.",
                tags("vec3-hermite", "vec3-cubic", "scalar-math", "ret-0x18")
            ),
            new Spec(
                "0x00575e77",
                "CTexture__InterpolateVec3CubicNormalized_Dispatch",
                "int CTexture__InterpolateVec3CubicNormalized_Dispatch(void)",
                "Wave887 static read-back: CPU-feature dispatch wrapper for normalized vec3 cubic interpolation. The body calls CFastVB__InitDispatchTableByCpuFeature(1), forwards six stack arguments to function pointer 0x00656ff8, and returns with RET 0x18. Static retail Ghidra evidence only; exact table-slot target, stack ABI, runtime normalized interpolation behavior, BEA patching, and rebuild parity remain unproven.",
                tags("cpu-dispatch-init", "slot-00656ff8", "computed-call", "vec3-cubic-normalized", "ret-0x18")
            ),
            new Spec(
                "0x00575ea1",
                "Math__InterpolateVec3CubicNormalized",
                "int Math__InterpolateVec3CubicNormalized(void)",
                "Wave887 static read-back: stack-locked scalar normalized vec3 cubic interpolation body. The body computes cubic basis weights over four vec3 inputs, normalizes the result vector, stores it through the output pointer, and returns with RET 0x18. Static retail Ghidra evidence only; exact normalization policy, floating-point edge behavior, runtime math parity, BEA patching, and rebuild parity remain unproven.",
                tags("vec3-cubic-normalized", "scalar-math", "normalizes-result", "ret-0x18")
            ),
            new Spec(
                "0x00575f72",
                "CTexture__InterpolateVec3ByUV_Dispatch",
                "int CTexture__InterpolateVec3ByUV_Dispatch(void)",
                "Wave887 static read-back: CPU-feature dispatch wrapper for vec3 interpolation by UV. The body calls CFastVB__InitDispatchTableByCpuFeature(1), forwards six stack arguments to function pointer 0x00656ffc, and returns with RET 0x18. Static retail Ghidra evidence only; exact table-slot target, stack ABI, runtime UV interpolation behavior, BEA patching, and rebuild parity remain unproven.",
                tags("cpu-dispatch-init", "slot-00656ffc", "computed-call", "vec3-uv-interpolate", "ret-0x18")
            ),
            new Spec(
                "0x00575fa1",
                "Math__InterpolateVec3ByUV",
                "int Math__InterpolateVec3ByUV(void)",
                "Wave887 static read-back: stack-locked scalar vec3 UV interpolation body. The body stores base + (u direction * u) + (v direction * v) into the output vec3 pointer and returns with RET 0x18. Static retail Ghidra evidence only; exact source helper identity, coordinate convention, runtime math parity, BEA patching, and rebuild parity remain unproven.",
                tags("vec3-uv-interpolate", "scalar-math", "ret-0x18")
            ),
            new Spec(
                "0x00575ffe",
                "CTexture__DispatchPtr00656f34_WithInit",
                "void CTexture__DispatchPtr00656f34_WithInit(void)",
                "Wave887 static read-back: CPU-feature dispatch-table initializer thunk for slot 0x00656f34. The body calls CFastVB__InitDispatchTableByCpuFeature(1) and tail-jumps through dword ptr [0x00656f34]; companion CVBufTexture__DispatchTextureTransformThunk is the no-init thunk. Static retail Ghidra evidence only; exact table-slot target, texture transform ABI, runtime behavior, BEA patching, and rebuild parity remain unproven.",
                tags("cpu-dispatch-init", "slot-00656f34", "computed-jump", "texture-transform-dispatch")
            ),
            new Spec(
                "0x0057600b",
                "CVBufTexture__DispatchTextureTransformThunk",
                "void CVBufTexture__DispatchTextureTransformThunk(void)",
                "Wave887 static read-back: no-init texture-transform dispatch thunk for slot 0x00656f34. The body tail-jumps through dword ptr [0x00656f34]; callers include CVBufTexture__RenderDynamicUnitPass, CVertexShader__ApplyRenderStateShaderConstants, CVertexShader__ApplyCustomRenderStateShaderConstants, and CVBufTexture__RenderModePass. Static retail Ghidra evidence only; exact table-slot target, render-state ABI, runtime behavior, BEA patching, and rebuild parity remain unproven.",
                tags("slot-00656f34", "computed-jump", "texture-transform-dispatch", "render-state-caller", "no-init-thunk")
            ),
            new Spec(
                "0x0057609c",
                "CFastVB__DispatchIndirect_00657028",
                "void CFastVB__DispatchIndirect_00657028(void)",
                "Wave887 static read-back: CPU-feature dispatch-table initializer thunk for slot 0x00657028. The body calls CFastVB__InitDispatchTableByCpuFeature(1) and tail-jumps through dword ptr [0x00657028]. Static retail Ghidra evidence only; exact table-slot target, ABI, runtime behavior, BEA patching, and rebuild parity remain unproven.",
                tags("cpu-dispatch-init", "slot-00657028", "computed-jump")
            ),
            new Spec(
                "0x00576154",
                "CFastVB__DispatchIndirect_00656f58",
                "void CFastVB__DispatchIndirect_00656f58(void)",
                "Wave887 static read-back: CPU-feature dispatch-table initializer thunk for slot 0x00656f58. The body calls CFastVB__InitDispatchTableByCpuFeature(1) and tail-jumps through dword ptr [0x00656f58]; companion CFastVB__DispatchIndirectByGlobalTable is the no-init thunk. Static retail Ghidra evidence only; exact table-slot target, mesh/texture transform ABI, runtime behavior, BEA patching, and rebuild parity remain unproven.",
                tags("cpu-dispatch-init", "slot-00656f58", "computed-jump", "mesh-texture-transform-dispatch")
            ),
            new Spec(
                "0x00576161",
                "CFastVB__DispatchIndirectByGlobalTable",
                "void CFastVB__DispatchIndirectByGlobalTable(void)",
                "Wave887 static read-back: no-init dispatch thunk for slot 0x00656f58. The body tail-jumps through dword ptr [0x00656f58]; callers include CMeshRenderer__RenderMeshCore, CTexture__MapNormalizedUvToVolumeCoords, CFastVB__InterpolateDualProfileStreams, and CFastVB__MapVolumeCoordsToNormalizedUv. Static retail Ghidra evidence only; exact table-slot target, mesh/texture transform ABI, runtime behavior, BEA patching, and rebuild parity remain unproven.",
                tags("slot-00656f58", "computed-jump", "mesh-texture-transform-dispatch", "no-init-thunk")
            ),
            new Spec(
                "0x00576167",
                "CTexture__DispatchPtr0065702c_WithInit",
                "void CTexture__DispatchPtr0065702c_WithInit(void)",
                "Wave887 static read-back: CPU-feature dispatch-table initializer thunk for slot 0x0065702c. The body calls CFastVB__InitDispatchTableByCpuFeature(1) and tail-jumps through dword ptr [0x0065702c]; companion CTexture__DispatchPtr0065702c_NoInit is the no-init thunk. Static retail Ghidra evidence only; exact table-slot target, optional transform-pass ABI, runtime behavior, BEA patching, and rebuild parity remain unproven.",
                tags("cpu-dispatch-init", "slot-0065702c", "computed-jump", "optional-transform-dispatch")
            ),
            new Spec(
                "0x00576178",
                "CTexture__DispatchPtr0065702c_NoInit",
                "void CTexture__DispatchPtr0065702c_NoInit(void)",
                "Wave887 static read-back: no-init dispatch thunk for slot 0x0065702c. The body tail-jumps through dword ptr [0x0065702c]; callers include CFastVB__ApplyOptionalTransformPasses_Minimal and CFastVB__ApplyOptionalTransformPasses. Static retail Ghidra evidence only; exact table-slot target, optional transform-pass ABI, runtime behavior, BEA patching, and rebuild parity remain unproven.",
                tags("slot-0065702c", "computed-jump", "optional-transform-dispatch", "no-init-thunk")
            )
        };

        Stats stats = new Stats();
        println("Wave887 texture dispatch/interpolation tail mode=" + (dryRun ? "dry" : "apply"));
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }
        println("SUMMARY: updated=" + stats.updated +
            " skipped=" + stats.skipped +
            " renamed=" + stats.renamed +
            " would_rename=" + stats.wouldRename +
            " missing=" + stats.missing +
            " bad=" + stats.bad);
        if (stats.missing != 0 || stats.bad != 0) {
            throw new IllegalStateException("Wave887 apply failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
        if (!dryRun) {
            println("REPORT: Save succeeded");
        }
    }
}
