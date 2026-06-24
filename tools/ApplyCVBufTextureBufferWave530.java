//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.FunctionTag;
import ghidra.program.model.listing.Parameter;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyCVBufTextureBufferWave530 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] parameters;
        final String comment;
        final String[] tags;

        Spec(String address, String name, String callingConvention, DataType returnType,
                ParameterImpl[] parameters, String comment, String[] tags) {
            this.address = address;
            this.name = name;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.parameters = parameters;
            this.comment = comment;
            this.tags = tags;
        }
    }

    private static class Stats {
        int updated = 0;
        int skipped = 0;
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
        Address result = toAddr(addressText);
        if (result == null) {
            throw new IllegalArgumentException("Bad address: " + addressText);
        }
        return result;
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

    private ParameterImpl param(String name, DataType dataType) throws Exception {
        return new ParameterImpl(name, dataType, currentProgram);
    }

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "cvbuftexture-buffer-wave530",
            "retail-binary-evidence",
            "signature-corrected",
            "comment-hardened"
        };
        String[] result = new String[common.length + extras.length];
        System.arraycopy(common, 0, result, 0, common.length);
        System.arraycopy(extras, 0, result, common.length, extras.length);
        return result;
    }

    private String expectedSignature(Spec spec) {
        StringBuilder sb = new StringBuilder();
        sb.append(spec.returnType.getDisplayName()).append(" ")
            .append(spec.callingConvention).append(" ")
            .append(spec.name).append("(");
        if (spec.parameters.length == 0) {
            sb.append("void");
        }
        for (int i = 0; i < spec.parameters.length; i++) {
            if (i > 0) {
                sb.append(", ");
            }
            sb.append(spec.parameters[i].getDataType().getDisplayName())
                .append(" ")
                .append(spec.parameters[i].getName());
        }
        sb.append(")");
        return sb.toString();
    }

    private boolean sameDataType(DataType actual, DataType expected) {
        if (actual == null || expected == null) {
            return actual == expected;
        }
        return actual.isEquivalent(expected) || actual.getDisplayName().equals(expected.getDisplayName());
    }

    private boolean signatureMatches(Function fn, Spec spec) {
        if (!spec.callingConvention.equals(fn.getCallingConventionName())) {
            return false;
        }
        if (!sameDataType(fn.getReturnType(), spec.returnType)) {
            return false;
        }
        if (fn.getParameterCount() != spec.parameters.length) {
            return false;
        }
        for (int i = 0; i < spec.parameters.length; i++) {
            Parameter actual = fn.getParameter(i);
            ParameterImpl expected = spec.parameters[i];
            if (!actual.getName().equals(expected.getName())) {
                return false;
            }
            if (!sameDataType(actual.getDataType(), expected.getDataType())) {
                return false;
            }
        }
        return true;
    }

    private boolean hasAllTags(Function fn, String[] tags) {
        Set<String> existing = new HashSet<>();
        for (FunctionTag tag : fn.getTags()) {
            existing.add(tag.getName());
        }
        for (String tag : tags) {
            if (!existing.contains(tag)) {
                return false;
            }
        }
        return true;
    }

    private boolean needsUpdate(Function fn, Spec spec) {
        if (!signatureMatches(fn, spec)) {
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
        if (!signatureMatches(readBack, spec)) {
            throw new IllegalStateException("Read-back signature mismatch at " + spec.address + ": " + readBack.getSignature());
        }
        if (!spec.comment.equals(readBack.getComment())) {
            throw new IllegalStateException("Read-back comment mismatch at " + spec.address);
        }
        if (!hasAllTags(readBack, spec.tags)) {
            throw new IllegalStateException("Read-back tag mismatch at " + spec.address);
        }
    }

    private void applySpec(Spec spec, boolean dryRun, Stats stats) throws Exception {
        Function fn = functionAtEntry(spec.address);
        if (fn == null) {
            println("MISSING: " + spec.address);
            stats.missing++;
            return;
        }
        if (!fn.getName().equals(spec.name)) {
            println("BADNAME: " + spec.address + " " + fn.getName() + " expected " + spec.name);
            stats.bad++;
            return;
        }
        if (!needsUpdate(fn, spec)) {
            println("SKIP: " + spec.address + " " + spec.name);
            stats.skipped++;
            return;
        }
        if (dryRun) {
            println("DRY: " + spec.address + " " + spec.name + " :: " + expectedSignature(spec));
            stats.skipped++;
            return;
        }

        fn.setCallingConvention(spec.callingConvention);
        fn.setReturnType(spec.returnType, SourceType.USER_DEFINED);
        fn.replaceParameters(FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS, true, SourceType.USER_DEFINED, spec.parameters);
        fn.setComment(spec.comment);
        for (String tag : spec.tags) {
            fn.addTag(tag);
        }
        verifyReadBack(spec);
        println("OK: " + spec.address + " " + spec.name + " :: " + expectedSignature(spec));
        stats.updated++;
        Thread.sleep(50);
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");
        println("Mode: " + (dryRun ? "dry" : "apply"));

        DataType intType = IntegerDataType.dataType;
        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);
        DataType voidPtrPtr = new PointerDataType(voidPtr);

        Spec[] specs = new Spec[] {
            new Spec(
                "0x005003f0",
                "CVBufTexture__CVBufTexture",
                "__thiscall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr), param("texture", voidPtr)},
                "Wave530 CVBufTexture buffer-management signature/comment hardening: RET 0x4 proves one explicit texture pointer after ECX. The constructor clears buffer, lock, format, cursor, list, persist, reference, and primitive fields, links this into global list head 0x00854e00, stores the texture pointer at +0x00, increments texture-side counters when non-null, and initializes the local reference count. Static retail evidence only; exact texture layout, constructor source identity, runtime rendering behavior, and rebuild parity remain unproven.",
                tags("cvbuftexture", "constructor", "buffer-management", "texture-reference")
            ),
            new Spec(
                "0x00500460",
                "CVBufTexture__dtor",
                "__thiscall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave530 CVBufTexture buffer-management signature/comment hardening: ECX-only destructor clears a texture back-pointer when it references this object, decrements the texture-side counter through CHud__DecrementCounter9C, unlocks any locked vertex/index buffers, releases the two CVBuffer slots and CIBuffer slot through their destructor wrappers, unlinks this from the global CVBufTexture list, and clears owned pointers. Static retail evidence only; exact texture/list layouts, destructor source identity, runtime device-loss behavior, and rebuild parity remain unproven.",
                tags("cvbuftexture", "destructor", "buffer-management", "texture-reference")
            ),
            new Spec(
                "0x00500540",
                "CVBufTexture__SetVBFormat",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("fvf_format", intType),
                    param("usage_flags", intType),
                    param("vertex_stride", intType),
                    param("primitive_type", intType),
                    param("pool_mode", intType)
                },
                "Wave530 CVBufTexture buffer-management signature/comment hardening: RET 0x14 proves five explicit stack arguments. The helper stores FVF at +0x04, usage flags at +0x08, pool mode at +0x0c, vertex stride at +0x54, and primitive type at +0x50; when hardware vertex processing global 0x00854dec is clear it masks usage with 0xfffffdf7 and forces pool mode 1. Static retail evidence only; exact D3D enum names, runtime render-state behavior, and rebuild parity remain unproven.",
                tags("cvbuftexture", "format", "vertex-buffer", "direct3d")
            ),
            new Spec(
                "0x00500590",
                "CVBufTexture__SetIBFormat",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("index_format", intType),
                    param("usage_flags", intType),
                    param("reserved", intType),
                    param("pool_mode", intType)
                },
                "Wave530 CVBufTexture buffer-management signature/comment hardening: RET 0x10 proves four explicit stack arguments. The body stores index format at +0x20, usage flags at +0x24, and pool mode at +0x28; the third stack argument is carried by callers but not consumed in the recovered body. When hardware vertex processing global 0x00854dec is clear it masks usage with 0xfffffdf7 and forces pool mode 1. Static retail evidence only; exact D3D enum names, reserved-argument meaning, runtime behavior, and rebuild parity remain unproven.",
                tags("cvbuftexture", "format", "index-buffer", "direct3d")
            ),
            new Spec(
                "0x005005d0",
                "CVBufTexture__SetPersist",
                "__thiscall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave530 CVBufTexture buffer-management signature/comment hardening: ECX-only helper sets persist byte +0x5c to 1 and returns. Static retail evidence only; exact lifetime contract, runtime resource-trimming behavior, and rebuild parity remain unproven.",
                tags("cvbuftexture", "persist", "resource-lifetime")
            ),
            new Spec(
                "0x005005e0",
                "CVBufTexture__ResizeVertexBuffer",
                "__thiscall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr), param("required_bytes", intType)},
                "Wave530 CVBufTexture buffer-management signature/comment hardening: RET 0x4 proves one required_bytes argument after ECX. The helper rounds nonzero requests up from 0x400 by powers of two, allocates a CVBuffer from vbuftexture.cpp line 0xb6 with pool token 0x2c, creates it with this object's VB usage/FVF/pool fields, copies existing vertex data through CVBuffer locks when present, unlocks the old buffer, releases the old current-buffer slot, installs the new CVBuffer in +0x40/+index*4, and stores the new capacity in +0x14/+index*4; required_bytes zero releases the current slot. Static retail evidence only; exact CVBufTexture layout, exception cleanup, runtime device behavior, and rebuild parity remain unproven.",
                tags("cvbuftexture", "resize", "vertex-buffer", "direct3d")
            ),
            new Spec(
                "0x005007f0",
                "CVBufTexture__ResizeIndexBuffer",
                "__thiscall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr), param("required_bytes", intType)},
                "Wave530 CVBufTexture buffer-management signature/comment hardening: RET 0x4 proves one required_bytes argument after ECX. The helper rounds nonzero requests up from 0x400 by powers of two, allocates a CIBuffer from vbuftexture.cpp line 0xfb with pool token 0x2f, creates it with this object's IB format/usage/pool fields, copies existing index bytes through CIBuffer direct locks when present, unlocks and releases the old CIBuffer slot at +0x4c, installs the new object, and stores capacity at +0x30; required_bytes zero releases the index buffer. Static retail evidence only; exact CVBufTexture layout, exception cleanup, runtime device behavior, and rebuild parity remain unproven.",
                tags("cvbuftexture", "resize", "index-buffer", "direct3d")
            ),
            new Spec(
                "0x005009c0",
                "CVBufTexture__UnlockVB",
                "__thiscall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave530 CVBufTexture buffer-management signature/comment hardening: ECX-only helper checks vertex-lock byte +0x10, unlocks the active CVBuffer slot selected by +0x48 when locked, clears vertex lock pointer +0x38, and clears +0x10. Static retail evidence only; exact lock ownership, runtime rendering behavior, and rebuild parity remain unproven.",
                tags("cvbuftexture", "lock-unlock", "vertex-buffer")
            ),
            new Spec(
                "0x005009f0",
                "CVBufTexture__UnlockIB",
                "__thiscall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave530 CVBufTexture buffer-management signature/comment hardening: ECX-only helper checks index-lock byte +0x2c, unlocks the CIBuffer at +0x4c when locked, clears index lock pointer +0x3c, and clears +0x2c. Static retail evidence only; exact lock ownership, runtime rendering behavior, and rebuild parity remain unproven.",
                tags("cvbuftexture", "lock-unlock", "index-buffer")
            ),
            new Spec(
                "0x00500a10",
                "CVBufTexture__AddVertices",
                "__thiscall",
                intType,
                new ParameterImpl[] {param("this", voidPtr), param("vertices", voidPtr), param("vertex_count", intType)},
                "Wave530 CVBufTexture buffer-management signature/comment hardening: RET 0x8 proves vertices and vertex_count stack arguments after ECX. The helper computes byte_count = vertex_count * stride +0x54, grows the active vertex buffer when needed, ensures the active CVBuffer is locked into +0x38, reports lock failure through HResultToString/CConsole__Printf/FatalError_LocalizedStringId, copies the vertex bytes into the current cursor +0x1c, advances +0x1c, and returns the starting vertex index. Static retail evidence only; exact vertex layout, caller ownership, runtime rendering behavior, and rebuild parity remain unproven.",
                tags("cvbuftexture", "append", "vertex-buffer", "lock-unlock")
            ),
            new Spec(
                "0x00500ac0",
                "CVBufTexture__AddIndices",
                "__thiscall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr), param("indices", voidPtr), param("index_count", intType)},
                "Wave530 CVBufTexture buffer-management signature/comment hardening: RET 0x8 proves indices and index_count stack arguments after ECX. The helper computes byte_count = index_count * 2, grows the index buffer when needed, locks the CIBuffer at +0x4c into +0x3c with FatalError_LocalizedStringId on failure, copies the index bytes into cursor +0x34, advances +0x34, and returns. Static retail evidence only; exact index format beyond 2-byte stride, caller ownership, runtime rendering behavior, and rebuild parity remain unproven.",
                tags("cvbuftexture", "append", "index-buffer", "lock-unlock")
            ),
            new Spec(
                "0x00500b40",
                "CVBufTexture__GetIndexPtr",
                "__thiscall",
                voidPtr,
                new ParameterImpl[] {param("this", voidPtr), param("index_count", intType)},
                "Wave530 CVBufTexture buffer-management signature/comment hardening: RET 0x4 proves one index_count argument after ECX. The helper reserves index_count * 2 bytes, grows and locks the index buffer when needed, advances cursor +0x34, and returns the pointer to the reserved index-byte range at lock pointer +0x3c plus the old cursor. Static retail evidence only; exact caller write contract, runtime rendering behavior, and rebuild parity remain unproven.",
                tags("cvbuftexture", "reserve", "index-buffer", "lock-unlock")
            ),
            new Spec(
                "0x00500bb0",
                "CVBufTexture__GetVertexPtr",
                "__thiscall",
                intType,
                new ParameterImpl[] {param("this", voidPtr), param("out_vertex_ptr", voidPtrPtr), param("vertex_count", intType)},
                "Wave530 CVBufTexture buffer-management signature/comment hardening: RET 0x8 proves out_vertex_ptr and vertex_count stack arguments after ECX. The helper reserves vertex_count * stride bytes, grows and locks the active vertex buffer when needed, writes the reserved vertex pointer through out_vertex_ptr, advances cursor +0x1c, and returns the starting vertex index. Static retail evidence only; exact vertex layout, caller write contract, runtime rendering behavior, and rebuild parity remain unproven.",
                tags("cvbuftexture", "reserve", "vertex-buffer", "lock-unlock")
            ),
            new Spec(
                "0x00500c50",
                "CVBufTexture__GetIndexPrimitiveCount",
                "__thiscall",
                intType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave530 CVBufTexture buffer-management signature/comment hardening: ECX-only primitive-count helper derives index_count from byte cursor +0x34 >> 1, reads primitive type +0x50, and returns D3D primitive counts for point list, line list, line strip, triangle list, triangle strip, and triangle fan, otherwise 0. Static retail evidence only; exact D3D enum names, validation behavior, runtime rendering behavior, and rebuild parity remain unproven.",
                tags("cvbuftexture", "primitive-count", "index-buffer", "rendering")
            ),
            new Spec(
                "0x00500cb0",
                "CVBufTexture__GetVertexPrimitiveCount",
                "__thiscall",
                intType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave530 CVBufTexture buffer-management signature/comment hardening: ECX-only primitive-count helper divides vertex byte cursor +0x1c by stride +0x54, reads primitive type +0x50, and returns D3D primitive counts for point list, line list, line strip, triangle list, triangle strip, and triangle fan, otherwise 0. Static retail evidence only; exact D3D enum names, validation behavior, runtime rendering behavior, and rebuild parity remain unproven.",
                tags("cvbuftexture", "primitive-count", "vertex-buffer", "rendering")
            )
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }

        println("SUMMARY updated=" + stats.updated + " skipped=" + stats.skipped +
            " missing=" + stats.missing + " bad=" + stats.bad);
        if (!dryRun && stats.missing == 0 && stats.bad == 0) {
            println("REPORT: Save succeeded");
        }
        if (stats.missing != 0 || stats.bad != 0) {
            throw new IllegalStateException("Wave530 apply failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
