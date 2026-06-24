//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionTag;

import java.util.HashSet;
import java.util.Set;

public class ApplyTextureTransformDispatchTailWave888 extends GhidraScript {
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
            "texture-transform-dispatch-tail-wave888",
            "wave888-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "signature-verified",
            "stack-locked-abi",
            "hidden-register-context",
            "texture-transform-dispatch-tail",
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
            if (!fn.getSignature().toString().equals(spec.signature)) {
                stats.bad++;
                println("BADSIG: " + spec.address + " actual=" + fn.getSignature() + " expected=" + spec.signature);
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
            new Spec("0x0057617e", "CDXTexture__DispatchPtr00656f48_WithInit", "void CDXTexture__DispatchPtr00656f48_WithInit(void)", "Wave888 static read-back: CPU-feature dispatch-table initializer thunk for slot 0x00656f48. The body pushes 1, calls CFastVB__InitDispatchTableByCpuFeature, then tail-jumps through dword ptr [0x00656f48]; companion CFastVB__DispatchIndirect_00656f48 is the no-init thunk. Static retail Ghidra evidence only; exact slot target, CPU feature policy, runtime texture-transform behavior, BEA patching, and rebuild parity remain unproven.", tags("cpu-dispatch-init", "slot-00656f48", "computed-jump")),
            new Spec("0x0057618b", "CFastVB__DispatchIndirect_00656f48", "void CFastVB__DispatchIndirect_00656f48(void)", "Wave888 static read-back: no-init dispatch thunk for slot 0x00656f48. The body tail-jumps through dword ptr [0x00656f48]; xrefs include calls from the later dual-profile/interpolation stream region. Static retail Ghidra evidence only; exact slot target, ABI, runtime texture-transform behavior, BEA patching, and rebuild parity remain unproven.", tags("slot-00656f48", "computed-jump", "no-init-thunk")),
            new Spec("0x005761f7", "CDXTexture__DispatchPtr00657030_WithInit", "void CDXTexture__DispatchPtr00657030_WithInit(void)", "Wave888 static read-back: CPU-feature dispatch-table initializer thunk for slot 0x00657030. The body calls CFastVB__InitDispatchTableByCpuFeature(1) and tail-jumps through dword ptr [0x00657030]. Static retail Ghidra evidence only; exact slot target, CPU feature policy, runtime behavior, BEA patching, and rebuild parity remain unproven.", tags("cpu-dispatch-init", "slot-00657030", "computed-jump")),
            new Spec("0x00576286", "CDXTexture__DispatchPtr00656f68_WithInit", "void CDXTexture__DispatchPtr00656f68_WithInit(void)", "Wave888 static read-back: CPU-feature dispatch-table initializer thunk for slot 0x00656f68. Xrefs include the DATA table slot at 0x00656f68 plus the companion no-init thunk at 0x00576297; the body calls CFastVB__InitDispatchTableByCpuFeature(1) and tail-jumps through the slot. Static retail Ghidra evidence only; exact slot target, runtime behavior, BEA patching, and rebuild parity remain unproven.", tags("cpu-dispatch-init", "slot-00656f68", "computed-jump")),
            new Spec("0x00576297", "CDXTexture__DispatchPtr00656f68_WithInit_Thunk", "void CDXTexture__DispatchPtr00656f68_WithInit_Thunk(void)", "Wave888 static read-back: no-init dispatch thunk for slot 0x00656f68. The body is a pure tail-jump through dword ptr [0x00656f68]; direct callers include retail code at 0x00442219, 0x0054a0c8, and 0x00551398. Static retail Ghidra evidence only; exact caller semantics, slot target, runtime behavior, BEA patching, and rebuild parity remain unproven.", tags("slot-00656f68", "computed-jump", "no-init-thunk")),
            new Spec("0x00576404", "Math__InterpolateVec4Cubic", "int Math__InterpolateVec4Cubic(void)", "Wave888 static read-back: stack-locked scalar vec4 cubic interpolation body. The decompile forms t^2/t^3 cubic basis weights, blends four vec4 inputs into the output pointer, and returns the output pointer with RET 0x18; data xref 0x00657120 points at this concrete implementation. Static retail Ghidra evidence only; exact source helper identity, floating-point edge behavior, runtime math parity, BEA patching, and rebuild parity remain unproven.", tags("vec4-cubic", "scalar-math", "ret-0x18", "slot-00657120")),
            new Spec("0x005764d5", "CTexture__InterpolateVec4CubicNormalized_Dispatch", "int CTexture__InterpolateVec4CubicNormalized_Dispatch(void)", "Wave888 static read-back: CPU-feature dispatch wrapper for normalized vec4 cubic interpolation. The body calls CFastVB__InitDispatchTableByCpuFeature(1), forwards six stack values through function pointer 0x00657004, and returns with RET 0x18. Static retail Ghidra evidence only; exact table-slot target, ABI, runtime interpolation behavior, BEA patching, and rebuild parity remain unproven.", tags("cpu-dispatch-init", "slot-00657004", "computed-call", "vec4-cubic-normalized", "ret-0x18")),
            new Spec("0x005764ff", "Math__InterpolateVec4CubicNormalized", "int Math__InterpolateVec4CubicNormalized(void)", "Wave888 static read-back: stack-locked scalar normalized vec4 cubic interpolation body. The decompile computes cubic basis weights, applies the 0.5 scale constant, stores four blended components, and returns the output pointer with RET 0x18; data xref 0x00657124 points at this concrete implementation. Static retail Ghidra evidence only; exact normalization convention, runtime math parity, BEA patching, and rebuild parity remain unproven.", tags("vec4-cubic-normalized", "scalar-math", "ret-0x18", "slot-00657124")),
            new Spec("0x005765f2", "CTexture__InterpolateVec4ByUV_Dispatch", "int CTexture__InterpolateVec4ByUV_Dispatch(void)", "Wave888 static read-back: CPU-feature dispatch wrapper for vec4 UV interpolation. The body calls CFastVB__InitDispatchTableByCpuFeature(1), forwards six stack values through function pointer 0x00657008, and returns with RET 0x18. Static retail Ghidra evidence only; exact table-slot target, coordinate convention, runtime behavior, BEA patching, and rebuild parity remain unproven.", tags("cpu-dispatch-init", "slot-00657008", "computed-call", "vec4-uv-interpolate", "ret-0x18")),
            new Spec("0x00576621", "Math__InterpolateVec4ByUV", "int Math__InterpolateVec4ByUV(void)", "Wave888 static read-back: stack-locked scalar vec4 UV/bilinear interpolation body. The body writes base + U delta + V delta for four float components and returns the output pointer with RET 0x18; data xref 0x00657128 points at this concrete implementation. Static retail Ghidra evidence only; exact source helper identity, coordinate convention, runtime math parity, BEA patching, and rebuild parity remain unproven.", tags("vec4-uv-interpolate", "scalar-math", "ret-0x18", "slot-00657128")),
            new Spec("0x00576698", "CFastVB__DispatchIndirect_00656f38", "void CFastVB__DispatchIndirect_00656f38(void)", "Wave888 static read-back: CPU-feature dispatch-table initializer thunk for slot 0x00656f38. The body calls CFastVB__InitDispatchTableByCpuFeature(1) and tail-jumps through dword ptr [0x00656f38]; companion CVertexShader__DispatchTableCall_656f38 is the no-init thunk. Static retail Ghidra evidence only; exact slot target, shader/transform ABI, runtime behavior, BEA patching, and rebuild parity remain unproven.", tags("cpu-dispatch-init", "slot-00656f38", "computed-jump", "vertex-shader-dispatch")),
            new Spec("0x005766a5", "CVertexShader__DispatchTableCall_656f38", "void CVertexShader__DispatchTableCall_656f38(void)", "Wave888 static read-back: no-init dispatch thunk for slot 0x00656f38. The body tail-jumps through dword ptr [0x00656f38]; direct call xrefs include CVertexShader-adjacent code at 0x00502ca0, 0x0050325e, 0x0050350a, and 0x00503602. Static retail Ghidra evidence only; exact caller semantics, slot target, runtime shader behavior, BEA patching, and rebuild parity remain unproven.", tags("slot-00656f38", "computed-jump", "no-init-thunk", "vertex-shader-dispatch")),
            new Spec("0x0057674a", "CFastVB__DispatchIndirect_00657034", "void CFastVB__DispatchIndirect_00657034(void)", "Wave888 static read-back: CPU-feature dispatch-table initializer thunk for slot 0x00657034. The body calls CFastVB__InitDispatchTableByCpuFeature(1) and tail-jumps through dword ptr [0x00657034]. Static retail Ghidra evidence only; exact slot target, CPU feature policy, runtime behavior, BEA patching, and rebuild parity remain unproven.", tags("cpu-dispatch-init", "slot-00657034", "computed-jump")),
            new Spec("0x005768f1", "CFastVB__DispatchIndirect_00656f3c", "void CFastVB__DispatchIndirect_00656f3c(void)", "Wave888 static read-back: CPU-feature dispatch-table initializer thunk for heavily reused transform/composition slot 0x00656f3c. The body calls CFastVB__InitDispatchTableByCpuFeature(1) and tail-jumps through the slot; companion 0x005768fe is the no-init thunk. Static retail Ghidra evidence only; exact slot target, matrix ABI, runtime behavior, BEA patching, and rebuild parity remain unproven.", tags("cpu-dispatch-init", "slot-00656f3c", "computed-jump", "matrix-transform-dispatch")),
            new Spec("0x005768fe", "CFastVB__DispatchIndirect_00656f3c", "void CFastVB__DispatchIndirect_00656f3c(void)", "Wave888 static read-back: no-init dispatch thunk for heavily reused transform/composition slot 0x00656f3c. The body tail-jumps through dword ptr [0x00656f3c]; xrefs include vertex-shader, transform-matrix, UV/volume mapping, and optional transform-pass bodies. Static retail Ghidra evidence only; exact table-slot target, matrix ABI, runtime behavior, BEA patching, and rebuild parity remain unproven.", tags("slot-00656f3c", "computed-jump", "no-init-thunk", "matrix-transform-dispatch")),
            new Spec("0x00576b3a", "CFastVB__DispatchIndirect_00656fc4", "void CFastVB__DispatchIndirect_00656fc4(void)", "Wave888 static read-back: CPU-feature dispatch-table initializer thunk for slot 0x00656fc4. The body calls CFastVB__InitDispatchTableByCpuFeature(1) and tail-jumps through dword ptr [0x00656fc4]; companion CVertexShader__DispatchTableCall_656fc4 is the no-init thunk. Static retail Ghidra evidence only; exact slot target, runtime shader/transform behavior, BEA patching, and rebuild parity remain unproven.", tags("cpu-dispatch-init", "slot-00656fc4", "computed-jump", "vertex-shader-dispatch")),
            new Spec("0x00576b47", "CVertexShader__DispatchTableCall_656fc4", "void CVertexShader__DispatchTableCall_656fc4(void)", "Wave888 static read-back: no-init dispatch thunk for slot 0x00656fc4. The body tail-jumps through dword ptr [0x00656fc4]; direct callers include CVertexShader-adjacent and texture-transform matrix builders. Static retail Ghidra evidence only; exact slot target, shader/transform semantics, runtime behavior, BEA patching, and rebuild parity remain unproven.", tags("slot-00656fc4", "computed-jump", "no-init-thunk", "vertex-shader-dispatch")),
            new Spec("0x00576dfd", "CFastVB__DispatchIndirect_00656f78", "void CFastVB__DispatchIndirect_00656f78(void)", "Wave888 static read-back: CPU-feature dispatch-table initializer thunk for slot 0x00656f78. The body calls CFastVB__InitDispatchTableByCpuFeature(1) and tail-jumps through dword ptr [0x00656f78]; companion CVertexShader__DispatchTableCall_656f78 is the no-init thunk. Static retail Ghidra evidence only; exact slot target, runtime shader/transform behavior, BEA patching, and rebuild parity remain unproven.", tags("cpu-dispatch-init", "slot-00656f78", "computed-jump", "vertex-shader-dispatch")),
            new Spec("0x00576e0a", "CVertexShader__DispatchTableCall_656f78", "void CVertexShader__DispatchTableCall_656f78(void)", "Wave888 static read-back: no-init dispatch thunk for slot 0x00656f78. The body tail-jumps through dword ptr [0x00656f78]; xrefs include CVertexShader-adjacent code and UV/volume mapping transform paths. Static retail Ghidra evidence only; exact slot target, shader/transform semantics, runtime behavior, BEA patching, and rebuild parity remain unproven.", tags("slot-00656f78", "computed-jump", "no-init-thunk", "vertex-shader-dispatch")),
            new Spec("0x005776d3", "CFastVB__DispatchIndirect_00656fcc", "void CFastVB__DispatchIndirect_00656fcc(void)", "Wave888 static read-back: CPU-feature dispatch-table initializer thunk for slot 0x00656fcc. Xrefs include the DATA table slot at 0x00656fcc; the body calls CFastVB__InitDispatchTableByCpuFeature(1) and tail-jumps through it. Static retail Ghidra evidence only; exact slot target, runtime behavior, BEA patching, and rebuild parity remain unproven.", tags("cpu-dispatch-init", "slot-00656fcc", "computed-jump")),
            new Spec("0x005776e4", "CFastVB__DispatchIndirect_00656fd4_ReturnInt", "int CFastVB__DispatchIndirect_00656fd4_ReturnInt(void)", "Wave888 static read-back: CPU-feature dispatch wrapper for return-int slot 0x00656fd4. The body calls CFastVB__InitDispatchTableByCpuFeature(1), calls the function pointer at 0x00656fd4, and returns with RET 0x14; data xref 0x00656fd4 points at this wrapper. Static retail Ghidra evidence only; exact slot target, ABI, runtime behavior, BEA patching, and rebuild parity remain unproven.", tags("cpu-dispatch-init", "slot-00656fd4", "computed-call", "ret-0x14")),
            new Spec("0x0057770b", "CFastVB__BuildTransformMatrixWithOffsets", "int CFastVB__BuildTransformMatrixWithOffsets(void)", "Wave888 static read-back: stack-locked transform-matrix builder. The body initializes an identity/scaled 4x4 matrix, optionally builds a quaternion rotation matrix through Math__BuildQuaternionRotationMatrix_Dispatch_Thunk, composes through CFastVB__DispatchIndirect_00656f3c, applies optional pivot subtraction/restoration, then adds optional translation; data xref 0x006570f4 points at this body. Static retail Ghidra evidence only; exact source identity, matrix convention, runtime behavior, BEA patching, and rebuild parity remain unproven.", tags("transform-matrix", "quaternion-rotation", "pivot-translation", "slot-006570f4", "ret-0x14")),
            new Spec("0x00577b17", "CTexture__DispatchPtr00656f7c_WithInit", "void CTexture__DispatchPtr00656f7c_WithInit(void)", "Wave888 static read-back: CPU-feature dispatch-table initializer thunk for slot 0x00656f7c. The body calls CFastVB__InitDispatchTableByCpuFeature(1) and tail-jumps through dword ptr [0x00656f7c]; companion 0x00577b24 is the no-init thunk. Static retail Ghidra evidence only; exact slot target, runtime texture parser/transform behavior, BEA patching, and rebuild parity remain unproven.", tags("cpu-dispatch-init", "slot-00656f7c", "computed-jump")),
            new Spec("0x00577b24", "CTexture__DispatchPtr00656f7c_NoInit", "void CTexture__DispatchPtr00656f7c_NoInit(void)", "Wave888 static read-back: no-init dispatch thunk for slot 0x00656f7c. The body tail-jumps through dword ptr [0x00656f7c]; xrefs cluster in the later texture directive/transform setup region around 0x00579900. Static retail Ghidra evidence only; exact slot target, parser/transform semantics, runtime behavior, BEA patching, and rebuild parity remain unproven.", tags("slot-00656f7c", "computed-jump", "no-init-thunk")),
            new Spec("0x00577c83", "CTexture__DispatchPtr00656fe0_WithInit", "void CTexture__DispatchPtr00656fe0_WithInit(void)", "Wave888 static read-back: CPU-feature dispatch-table initializer thunk for slot 0x00656fe0. The body calls CFastVB__InitDispatchTableByCpuFeature(1) and tail-jumps through dword ptr [0x00656fe0]; companion 0x00577c90 is the no-init thunk. Static retail Ghidra evidence only; exact slot target, runtime texture parser/transform behavior, BEA patching, and rebuild parity remain unproven.", tags("cpu-dispatch-init", "slot-00656fe0", "computed-jump")),
            new Spec("0x00577c90", "CTexture__DispatchPtr00656fe0_NoInit", "void CTexture__DispatchPtr00656fe0_NoInit(void)", "Wave888 static read-back: no-init dispatch thunk for slot 0x00656fe0. The body tail-jumps through dword ptr [0x00656fe0]; xrefs cluster in the texture directive/transform setup region. Static retail Ghidra evidence only; exact slot target, parser/transform semantics, runtime behavior, BEA patching, and rebuild parity remain unproven.", tags("slot-00656fe0", "computed-jump", "no-init-thunk")),
            new Spec("0x00577d47", "CTexture__DispatchPtr0065700c_WithInit", "void CTexture__DispatchPtr0065700c_WithInit(void)", "Wave888 static read-back: CPU-feature dispatch-table initializer thunk for slot 0x0065700c. The body calls CFastVB__InitDispatchTableByCpuFeature(1) and tail-jumps through dword ptr [0x0065700c]; companion 0x00577d54 is the no-init thunk. Static retail Ghidra evidence only; exact slot target, runtime texture parser/transform behavior, BEA patching, and rebuild parity remain unproven.", tags("cpu-dispatch-init", "slot-0065700c", "computed-jump")),
            new Spec("0x00577d54", "CTexture__DispatchPtr0065700c_NoInit", "void CTexture__DispatchPtr0065700c_NoInit(void)", "Wave888 static read-back: no-init dispatch thunk for slot 0x0065700c. The body tail-jumps through dword ptr [0x0065700c]; xrefs cluster in the texture directive/transform setup region. Static retail Ghidra evidence only; exact slot target, parser/transform semantics, runtime behavior, BEA patching, and rebuild parity remain unproven.", tags("slot-0065700c", "computed-jump", "no-init-thunk")),
            new Spec("0x00577dd5", "CDXTexture__DispatchPtr00657010_WithInit", "void CDXTexture__DispatchPtr00657010_WithInit(void)", "Wave888 static read-back: CPU-feature dispatch-table initializer thunk for slot 0x00657010. The body calls CFastVB__InitDispatchTableByCpuFeature(1) and tail-jumps through dword ptr [0x00657010]; companion 0x00577de2 is the no-init thunk. Static retail Ghidra evidence only; exact slot target, runtime texture/DX behavior, BEA patching, and rebuild parity remain unproven.", tags("cpu-dispatch-init", "slot-00657010", "computed-jump")),
            new Spec("0x00577de2", "CDXTexture__DispatchPtr00657010_NoInit", "void CDXTexture__DispatchPtr00657010_NoInit(void)", "Wave888 static read-back: no-init dispatch thunk for slot 0x00657010. The body tail-jumps through dword ptr [0x00657010]; xrefs cluster in the later texture directive/transform setup region. Static retail Ghidra evidence only; exact slot target, DX texture semantics, runtime behavior, BEA patching, and rebuild parity remain unproven.", tags("slot-00657010", "computed-jump", "no-init-thunk")),
            new Spec("0x0057800e", "CTexture__DispatchPtr00656fe4_WithInit", "void CTexture__DispatchPtr00656fe4_WithInit(void)", "Wave888 static read-back: CPU-feature dispatch-table initializer thunk for slot 0x00656fe4. The body calls CFastVB__InitDispatchTableByCpuFeature(1) and tail-jumps through dword ptr [0x00656fe4]. Static retail Ghidra evidence only; exact slot target, runtime texture-transform behavior, BEA patching, and rebuild parity remain unproven.", tags("cpu-dispatch-init", "slot-00656fe4", "computed-jump")),
            new Spec("0x005780d6", "CDXTexture__DispatchPtr00656f84_WithInit", "void CDXTexture__DispatchPtr00656f84_WithInit(void)", "Wave888 static read-back: CPU-feature dispatch-table initializer thunk for slot 0x00656f84. Xrefs include DATA slot 0x00656f84 and companion no-init thunk 0x005780e3; the body calls CFastVB__InitDispatchTableByCpuFeature(1) and tail-jumps through the slot. Static retail Ghidra evidence only; exact slot target, runtime texture/DX behavior, BEA patching, and rebuild parity remain unproven.", tags("cpu-dispatch-init", "slot-00656f84", "computed-jump")),
            new Spec("0x005780e3", "CDXTexture__DispatchPtr00656f84_WithInit_005780e3", "void CDXTexture__DispatchPtr00656f84_WithInit_005780e3(void)", "Wave888 static read-back: no-init dispatch thunk for slot 0x00656f84. The body tail-jumps through dword ptr [0x00656f84]; direct callers include later texture setup code at 0x00579534 and 0x0057960e. Static retail Ghidra evidence only; exact caller semantics, slot target, runtime texture/DX behavior, BEA patching, and rebuild parity remain unproven.", tags("slot-00656f84", "computed-jump", "no-init-thunk")),
            new Spec("0x005783d9", "CTexture__DispatchPtr00657040_WithInit", "void CTexture__DispatchPtr00657040_WithInit(void)", "Wave888 static read-back: CPU-feature dispatch-table initializer thunk for slot 0x00657040. The body calls CFastVB__InitDispatchTableByCpuFeature(1) and tail-jumps through dword ptr [0x00657040]. Static retail Ghidra evidence only; exact slot target, runtime texture-transform behavior, BEA patching, and rebuild parity remain unproven.", tags("cpu-dispatch-init", "slot-00657040", "computed-jump")),
            new Spec("0x005784a9", "CFastVB__DispatchIndirect_00657044", "void CFastVB__DispatchIndirect_00657044(void)", "Wave888 static read-back: CPU-feature dispatch-table initializer thunk for slot 0x00657044. The body calls CFastVB__InitDispatchTableByCpuFeature(1) and tail-jumps through dword ptr [0x00657044]. Static retail Ghidra evidence only; exact slot target, runtime transform behavior, BEA patching, and rebuild parity remain unproven.", tags("cpu-dispatch-init", "slot-00657044", "computed-jump")),
            new Spec("0x005785c0", "Math__TransformVec2ArrayToVec4Array", "int Math__TransformVec2ArrayToVec4Array(void)", "Wave888 static read-back: stack-locked array transform body. The decompile loops over a strided vec2 input array, applies a 4x4 matrix with translation terms, writes four floats per output element, and returns the output base pointer with RET 0x18; data xref 0x0065713c points at this implementation. Static retail Ghidra evidence only; exact stride contract, matrix convention, runtime math parity, BEA patching, and rebuild parity remain unproven.", tags("array-transform", "vec2-to-vec4", "matrix4x4", "ret-0x18", "slot-0065713c")),
            new Spec("0x005786c0", "Math__TransformVec2ArrayByMatrixPerspective", "int Math__TransformVec2ArrayByMatrixPerspective(void)", "Wave888 static read-back: stack-locked vec2 array perspective-transform body. The decompile loops over strided vec2 inputs, computes transformed XY and W, conditionally divides by W through Math__IsFloatDiffOutsideTolerance, and returns the output base pointer with RET 0x18; data xref 0x00657140 points at this implementation. Static retail Ghidra evidence only; exact tolerance semantics, matrix convention, runtime math parity, BEA patching, and rebuild parity remain unproven.", tags("array-transform", "vec2-perspective", "matrix4x4", "ret-0x18", "slot-00657140")),
            new Spec("0x00578794", "Math__TransformVec2ArrayByMatrixLinear", "int Math__TransformVec2ArrayByMatrixLinear(void)", "Wave888 static read-back: stack-locked vec2 array linear-transform body. The decompile loops over strided vec2 inputs, applies the top-left matrix rows without translation or perspective divide, writes two floats per output element, and returns the output base pointer with RET 0x18; data xref 0x00657144 points at this implementation. Static retail Ghidra evidence only; exact matrix convention, runtime math parity, BEA patching, and rebuild parity remain unproven.", tags("array-transform", "vec2-linear", "matrix4x4", "ret-0x18", "slot-00657144")),
            new Spec("0x00578941", "Math__TransformVec3ArrayByMatrixPerspective", "int Math__TransformVec3ArrayByMatrixPerspective(void)", "Wave888 static read-back: stack-locked vec3 array perspective-transform body. The decompile loops over strided vec3 inputs, computes transformed XYZ and W, conditionally divides by W through Math__IsFloatDiffOutsideTolerance, and returns the output base pointer with RET 0x18; data xref 0x0065714c points at this implementation. Static retail Ghidra evidence only; exact tolerance semantics, matrix convention, runtime math parity, BEA patching, and rebuild parity remain unproven.", tags("array-transform", "vec3-perspective", "matrix4x4", "ret-0x18", "slot-0065714c")),
            new Spec("0x00578a20", "CTexture__MapNormalizedUvToVolumeCoords", "int CTexture__MapNormalizedUvToVolumeCoords(void)", "Wave888 static read-back: stack-locked texture coordinate mapping helper. The decompile selects optional transform passes from three boolean stack flags, can call CFastVB__DispatchIndirect_00656f3c and CFastVB__DispatchIndirectByGlobalTable, then maps normalized UV/Z into volume/rectangle coordinates using bounds from the descriptor pointer; data xref 0x00657088 points at this implementation. Static retail Ghidra evidence only; exact descriptor layout, coordinate convention, runtime texture behavior, BEA patching, and rebuild parity remain unproven.", tags("uv-volume-map", "optional-transform-flags", "slot-00657088", "ret-0x18")),
            new Spec("0x00578bad", "CFastVB__ApplyOptionalTransformPasses_Minimal", "void CFastVB__ApplyOptionalTransformPasses_Minimal(void)", "Wave888 static read-back: stack-locked optional transform pass helper. The body switches on three boolean stack flags, conditionally calls CFastVB__DispatchIndirect_00656f3c, optionally applies a fourth transform, then calls CTexture__DispatchPtr0065702c_NoInit before RET 0x24; data xref 0x00657158 points at this implementation. Static retail Ghidra evidence only; exact flag semantics, matrix ABI, runtime texture behavior, BEA patching, and rebuild parity remain unproven.", tags("optional-transform-passes", "slot-00657158", "ret-0x24")),
            new Spec("0x00578dad", "CFastVB__MapVolumeCoordsToNormalizedUv", "int CFastVB__MapVolumeCoordsToNormalizedUv(void)", "Wave888 static read-back: inverse texture coordinate mapping helper. The decompile selects optional transform passes from three boolean stack flags, calls CVertexShader__DispatchTableCall_656f78 and CFastVB__DispatchIndirectByGlobalTable, then maps volume/rectangle coordinates back to normalized UV/Z using descriptor bounds; data xref 0x0065708c points at this implementation. Static retail Ghidra evidence only; exact descriptor layout, coordinate convention, runtime texture behavior, BEA patching, and rebuild parity remain unproven.", tags("volume-uv-map", "optional-transform-flags", "slot-0065708c", "ret-0x18")),
            new Spec("0x00578f53", "CFastVB__ApplyOptionalTransformPasses", "void CFastVB__ApplyOptionalTransformPasses(void)", "Wave888 static read-back: full optional transform pass helper. The body switches on three boolean stack flags, conditionally calls CFastVB__DispatchIndirect_00656f3c, calls CVertexShader__DispatchTableCall_656f78, optionally applies another transform, then calls CTexture__DispatchPtr0065702c_NoInit before RET 0x24; data xref 0x0065715c points at this implementation. Static retail Ghidra evidence only; exact flag semantics, matrix ABI, runtime texture behavior, BEA patching, and rebuild parity remain unproven.", tags("optional-transform-passes", "slot-0065715c", "ret-0x24")),
            new Spec("0x00579273", "CTexture__BuildTransformMatrixWithOptionalOffsets", "int CTexture__BuildTransformMatrixWithOptionalOffsets(void)", "Wave888 static read-back: stack-locked texture transform matrix builder. The body initializes identity/scale matrix state, optionally composes quaternion rotations through Math__BuildQuaternionRotationMatrix_Dispatch_Thunk, calls CVertexShader__DispatchTableCall_656fc4 and CFastVB__DispatchIndirect_00656f3c, applies optional pivot subtraction/restoration and translation offsets, and returns the output matrix pointer with RET 0x1c; data xref 0x006570ec points at this body. Static retail Ghidra evidence only; exact source identity, matrix convention, runtime texture transform behavior, BEA patching, and rebuild parity remain unproven.", tags("transform-matrix", "quaternion-rotation", "pivot-translation", "slot-006570ec", "ret-0x1c"))
        };

        println("MODE: " + (dryRun ? "dry" : "apply"));
        println("TARGETS: " + specs.length);
        Stats stats = new Stats();
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }
        println("SUMMARY: updated=" + stats.updated + " skipped=" + stats.skipped +
            " renamed=" + stats.renamed + " would_rename=" + stats.wouldRename +
            " missing=" + stats.missing + " bad=" + stats.bad);
        if (!dryRun && stats.bad == 0 && stats.missing == 0) {
            println("REPORT: Save succeeded");
        }
        if (stats.bad != 0 || stats.missing != 0) {
            throw new IllegalStateException("Wave888 apply failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
