//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.UnsignedShortDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.FunctionTag;
import ghidra.program.model.listing.Parameter;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyCFastVBTailWave563 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] params;
        final String comment;
        final String[] tags;

        Spec(String address, String name, String callingConvention, DataType returnType,
                ParameterImpl[] params, String comment, String[] tags) {
            this.address = address;
            this.name = name;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.params = params;
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

    private DataType voidPtr() {
        return new PointerDataType(VoidDataType.dataType);
    }

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "cfastvb-tail-wave563",
            "retail-binary-evidence",
            "source-parity",
            "signature-corrected",
            "comment-hardened"
        };
        String[] result = new String[common.length + extras.length];
        System.arraycopy(common, 0, result, 0, common.length);
        System.arraycopy(extras, 0, result, common.length, extras.length);
        return result;
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
        if (fn.getParameterCount() != spec.params.length) {
            return false;
        }
        for (int i = 0; i < spec.params.length; i++) {
            Parameter actual = fn.getParameter(i);
            ParameterImpl expected = spec.params[i];
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
        if (!fn.getName().equals(spec.name)) {
            return true;
        }
        if (!signatureMatches(fn, spec)) {
            return true;
        }
        String existingComment = fn.getComment();
        if (existingComment == null || !existingComment.equals(spec.comment)) {
            return true;
        }
        return !hasAllTags(fn, spec.tags);
    }

    private String expectedSignature(Spec spec) {
        StringBuilder sb = new StringBuilder();
        sb.append(spec.returnType.getDisplayName()).append(" ")
            .append(spec.callingConvention).append(" ")
            .append(spec.name).append("(");
        if (spec.params.length == 0) {
            sb.append("void");
        }
        for (int i = 0; i < spec.params.length; i++) {
            if (i > 0) {
                sb.append(", ");
            }
            sb.append(spec.params[i].getDataType().getDisplayName())
                .append(" ")
                .append(spec.params[i].getName());
        }
        sb.append(")");
        return sb.toString();
    }

    private void verifyReadBack(Spec spec) throws Exception {
        Function fn = functionAtEntry(spec.address);
        if (fn == null) {
            throw new IllegalStateException("Readback missing function at " + spec.address);
        }
        if (!fn.getName().equals(spec.name)) {
            throw new IllegalStateException("Readback name mismatch at " + spec.address + ": " + fn.getName());
        }
        if (!signatureMatches(fn, spec)) {
            throw new IllegalStateException("Readback signature mismatch at " + spec.address +
                ": expected " + expectedSignature(spec) + " got " + fn.getSignature());
        }
        String existingComment = fn.getComment();
        if (existingComment == null || !existingComment.equals(spec.comment)) {
            throw new IllegalStateException("Readback comment mismatch at " + spec.address);
        }
        if (!hasAllTags(fn, spec.tags)) {
            throw new IllegalStateException("Readback missing tags at " + spec.address);
        }
    }

    private void applySpec(Spec spec, boolean dryRun, Stats stats) {
        try {
            Function fn = functionAtEntry(spec.address);
            if (fn == null) {
                stats.missing++;
                println("FAIL: " + spec.address + " " + spec.name + " Function not found");
                return;
            }
            if (!fn.getName().equals(spec.name)) {
                throw new IllegalStateException("Unexpected function name at " + spec.address + ": " + fn.getName());
            }

            boolean updateNeeded = needsUpdate(fn, spec);
            if (dryRun) {
                if (updateNeeded) {
                    println("DRY: " + spec.address + " " + spec.name + " -> " + expectedSignature(spec));
                } else {
                    println("SKIP: " + spec.address + " " + spec.name + " already matches");
                }
                stats.skipped++;
                return;
            }

            if (!updateNeeded) {
                stats.skipped++;
                println("SKIP: " + spec.address + " " + spec.name + " already matches");
                verifyReadBack(spec);
                return;
            }

            fn.setCallingConvention(spec.callingConvention);
            fn.setReturnType(spec.returnType, SourceType.USER_DEFINED);
            fn.replaceParameters(
                FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS,
                true,
                SourceType.USER_DEFINED,
                spec.params);
            fn.setComment(spec.comment);
            for (String tag : spec.tags) {
                fn.addTag(tag);
            }
            verifyReadBack(spec);
            stats.updated++;
            println("UPDATED: " + spec.address + " " + spec.name + " -> " + expectedSignature(spec));
        } catch (Exception ex) {
            stats.bad++;
            println("FAIL: " + spec.address + " " + spec.name + " " + ex.getClass().getSimpleName() + ": " + ex.getMessage());
        }
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = true;
        if (args != null && args.length > 0) {
            dryRun = isDryRun(args[0]);
        }

        DataType intType = IntegerDataType.dataType;
        DataType uint16Type = UnsignedShortDataType.dataType;
        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = voidPtr();
        DataType voidPtrPtr = new PointerDataType(voidPtr);

        Spec[] specs = new Spec[] {
            new Spec(
                "0x0051a270",
                "CFastVB__Create",
                "__thiscall",
                intType,
                new ParameterImpl[] { param("this", voidPtr) },
                "Wave563 signature/comment hardening: source-aligns to FastVB.cpp CFastVB::Create. The retail body returns 0 when this+0x00 already has a CVBuffer, allocates a 0x2c CVBuffer from the FastVB.cpp line-0x29 debug context, stores it at this+0x00, calls CVBuffer__CreateDynamic with vertex_count from this+0x0c, vertex_stride 0x1c, and FVF/format 0x144, releases and clears the buffer on negative create result, and registers successful buffers through D3DBufferRegistry__MoveToFreeList. Static retail/source evidence only; exact CFastVB/CVBuffer layout, D3D runtime behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("cfastvb", "dynamic-vbuffer", "create")
            ),
            new Spec(
                "0x0051a340",
                "CFastVB__Destroy",
                "__thiscall",
                voidType,
                new ParameterImpl[] { param("this", voidPtr) },
                "Wave563 signature/comment hardening: source-aligns to FastVB.cpp CFastVB::Destroy. The retail body releases the instance CVBuffer at this+0x00 through its vtable with flag 1, clears this+0x00, then releases the shared static index buffer DAT_00897a90 the same way and clears the global. Static retail/source evidence only; shared-buffer lifetime, exact CFastVB/CIBuffer layout, D3D runtime behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("cfastvb", "dynamic-vbuffer", "index-buffer", "destroy")
            ),
            new Spec(
                "0x0051a380",
                "CFastVB__LockAligned",
                "__thiscall",
                uint16Type,
                new ParameterImpl[] { param("this", voidPtr), param("out_vertex_data", voidPtrPtr), param("vertex_count", intType) },
                "Wave563 signature/comment hardening: RET 0x8 plus callers prove out_vertex_data and vertex_count stack arguments. The retail body returns 0xffff without a CVBuffer, aligns the write cursor at this+0x04 to the next 4-vertex boundary, compares against the max vertex count at this+0x0c, selects lock flag 0x2800 for discard/reset or 0x1800 for no-overwrite append, calls CVBuffer__LockRange using 0x1c-byte vertices, then updates this+0x04, this+0x06 start vertex, and this+0x08 batch vertex count. Static retail/source evidence only; exact CFastVB/CVBuffer layout, D3D lock behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("cfastvb", "lock-range", "dynamic-vbuffer", "quad-aligned")
            ),
            new Spec(
                "0x0051a430",
                "CFastVB__Lock",
                "__thiscall",
                uint16Type,
                new ParameterImpl[] { param("this", voidPtr), param("out_vertex_data", voidPtrPtr), param("vertex_count", intType) },
                "Wave563 signature/comment hardening: RET 0x8 plus callers prove out_vertex_data and vertex_count stack arguments. The retail body returns 0xffff without a CVBuffer, delegates to CFastVB__LockAligned when this+0x06 is 0xffff, flushes through CFastVB__Render and resets this+0x04/0x06/0x08 on overflow, otherwise unlocks the active CVBuffer and uses no-overwrite flag 0x1800 before calling CVBuffer__LockRange over 0x1c-byte vertices. Static retail/source evidence only; exact batch lifetime, CFastVB/CVBuffer layout, D3D lock behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("cfastvb", "lock-range", "dynamic-vbuffer", "render-batching")
            ),
            new Spec(
                "0x0051a510",
                "CFastVB__Render",
                "__thiscall",
                voidType,
                new ParameterImpl[] { param("this", voidPtr) },
                "Wave563 signature/comment hardening: source-aligns to FastVB.cpp CFastVB::Render. The retail body returns when this+0x06 is 0xffff, unlocks the vertex buffer, binds stream source stride 0x1c, lazily allocates shared CIBuffer DAT_00897a90 from the FastVB.cpp line-0xc3 debug context, calls CIBuffer__Create with index_count 0x1d4c, fills the [0,1,2,2,3,0] quad-index pattern up to this+0x0c vertices, registers the index buffer, binds it, sets raw vertex shader/FVF handle 0x144, draws indexed primitive type 4 from this+0x06/this+0x08, then resets this+0x06 to 0xffff and this+0x08 to 0. Static retail/source evidence only; exact render-state lifetime, CFastVB/CIBuffer layout, D3D runtime behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("cfastvb", "render-batching", "index-buffer", "quad-render")
            )
        };

        println("ApplyCFastVBTailWave563 mode=" + (dryRun ? "dry" : "apply"));
        Stats stats = new Stats();
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }

        println("SUMMARY: updated=" + stats.updated + " skipped=" + stats.skipped +
            " missing=" + stats.missing + " bad=" + stats.bad);
        if (stats.missing > 0 || stats.bad > 0) {
            throw new IllegalStateException("Wave563 CFastVB tail apply failed: missing=" +
                stats.missing + " bad=" + stats.bad);
        }
    }
}
