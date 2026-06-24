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

public class ApplyCVBufTextureRenderWave531 extends GhidraScript {
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
            "cvbuftexture-render-wave531",
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

        Spec[] specs = new Spec[] {
            new Spec(
                "0x00500d10",
                "CVBufTexture__RenderBatchList",
                "__cdecl",
                voidType,
                new ParameterImpl[] {param("batch_list", voidPtr)},
                "Wave531 CVBufTexture render-tail signature/comment hardening: caller-cleaned RET C3 plus CMeshRenderer callsites prove one batch-list pointer argument. The helper walks 0x24-byte batch records for priority values 0..5, filters each record through texture priority field +0x88 and non-null CVBufTexture pointer, then calls CVBufTexture__Render(reset_after_render=1). Static retail evidence only; exact batch-record layout, runtime render ordering, and rebuild parity remain unproven.",
                tags("cvbuftexture", "rendering", "batch-list", "direct3d")
            ),
            new Spec(
                "0x00500d60",
                "CVBufTexture__ReleaseAllUnlocked",
                "__cdecl",
                voidType,
                new ParameterImpl[] {},
                "Wave531 CVBufTexture render-tail signature/comment hardening: global no-argument RET C3 helper called from CDXEngine__PostRender. The body walks CVBufTexture global list head 0x00854e00, skips persistent entries via byte +0x5c, unlocks active CIBuffer/CVBuffer state, emits leftover index/vertex warnings, preserves last vertex byte count at +0x64, and clears current byte cursors. Static retail evidence only; exact list layout, warning text semantics, runtime device-loss behavior, and rebuild parity remain unproven.",
                tags("cvbuftexture", "resource-lifetime", "lock-unlock", "rendering")
            ),
            new Spec(
                "0x00500e70",
                "CVBufTexture__Render",
                "__thiscall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr), param("reset_after_render", intType)},
                "Wave531 CVBufTexture render-tail signature/comment hardening: RET 0x4 proves one reset_after_render stack argument after ECX. The helper requires nonzero vertex and index byte cursors, unlocks active buffers, invokes texture pre/post render hooks, sets FVF globals, applies pending render state, binds stream/index buffers, draws indexed primitives, and optionally clears cursors/toggles double-buffer state. Static retail evidence only; exact texture interface, Direct3D state semantics, runtime rendering behavior, and rebuild parity remain unproven.",
                tags("cvbuftexture", "rendering", "direct3d", "indexed-render")
            ),
            new Spec(
                "0x00500f80",
                "CVBufTexture__Reset",
                "__thiscall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave531 CVBufTexture render-tail signature/comment hardening: ECX-only reset helper records the last nonzero vertex byte count at +0x64, clears vertex/index byte cursors +0x1c/+0x34, and toggles active vertex-buffer slot +0x48 when global double-buffering byte 0x00854e04 is enabled. Static retail evidence only; exact field names, runtime frame cadence, and rebuild parity remain unproven.",
                tags("cvbuftexture", "reset", "double-buffering", "rendering")
            ),
            new Spec(
                "0x00500fa0",
                "CVBufTexture__RenderIndexed",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("reset_after_render", intType),
                    param("vertex_count_override", intType),
                    param("primitive_count_override", intType)
                },
                "Wave531 CVBufTexture render-tail signature/comment hardening: RET 0x0c proves reset_after_render, vertex_count_override, and primitive_count_override stack arguments after ECX. The helper unlocks active VB/IB state, derives zero overrides from cursor/stride and CVBufTexture__GetIndexPrimitiveCount, sets FVF globals, optionally validates the device through DAT_00854dd9, calls DrawIndexedPrimitive, reports ValidateDevice failure text, and optionally resets cursors/double-buffer state. Static retail evidence only; exact D3D validation semantics, runtime render behavior, and rebuild parity remain unproven.",
                tags("cvbuftexture", "rendering", "direct3d", "indexed-render", "validate-device")
            ),
            new Spec(
                "0x005010e0",
                "CVBufTexture__RenderIndexedNoValidate",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("reset_after_render", intType),
                    param("vertex_count_override", intType),
                    param("primitive_count_override", intType)
                },
                "Wave531 CVBufTexture render-tail signature/comment hardening: RET 0x0c proves reset_after_render, vertex_count_override, and primitive_count_override stack arguments after ECX. The helper shares the indexed-render bind/draw/reset path but skips the ValidateDevice branch and render-state/FVF setup seen in CVBufTexture__RenderIndexed, matching particle/tree/water callsites that choose this direct path. Static retail evidence only; exact caller intent, runtime render behavior, and rebuild parity remain unproven.",
                tags("cvbuftexture", "rendering", "direct3d", "indexed-render", "no-validate")
            ),
            new Spec(
                "0x005011c0",
                "CVBufTexture__RenderNonIndexed",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("reset_after_render", intType),
                    param("primitive_count_override", intType)
                },
                "Wave531 CVBufTexture render-tail signature/comment hardening: RET 0x8 proves reset_after_render and primitive_count_override stack arguments after ECX. The helper unlocks active vertex-buffer state, derives zero primitive overrides from CVBufTexture__GetVertexPrimitiveCount, sets FVF globals, applies pending render state, binds the stream source, calls Direct3D DrawPrimitive, and optionally clears the vertex cursor/toggles double-buffer state. Static retail evidence only; exact non-indexed render semantics, runtime render behavior, and rebuild parity remain unproven.",
                tags("cvbuftexture", "rendering", "direct3d", "non-indexed-render")
            ),
            new Spec(
                "0x00501280",
                "CVBufTexture__GetOrCreate",
                "__cdecl",
                voidPtr,
                new ParameterImpl[] {param("texture", voidPtr), param("force_new", intType)},
                "Wave531 CVBufTexture render-tail signature/comment hardening: caller-cleaned RET C3 plus GetOrCreate callsites prove texture and force_new stack arguments. When force_new is zero, the helper reuses texture field +0x140 or a matching entry from global list 0x00854e00 and increments the CVBufTexture reference count at +0x60; otherwise it allocates 0x68 bytes through OID__AllocObject and calls CVBufTexture__CVBufTexture. Static retail evidence only; exact texture layout, ownership policy, runtime lifetime behavior, and rebuild parity remain unproven.",
                tags("cvbuftexture", "factory", "resource-lifetime", "texture-reference")
            )
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }
        println("SUMMARY updated=" + stats.updated + " skipped=" + stats.skipped + " missing=" + stats.missing + " bad=" + stats.bad);
    }
}
