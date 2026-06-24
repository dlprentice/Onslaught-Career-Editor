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

public class ApplyDecodeCallbackEntropyHeadWave726 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final boolean updateSignature;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] parameters;
        final String comment;
        final String[] tags;

        Spec(String address, String name, boolean updateSignature, String callingConvention, DataType returnType,
                ParameterImpl[] parameters, String comment, String[] tags) {
            this.address = address;
            this.name = name;
            this.updateSignature = updateSignature;
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
        int renamed = 0;
        int wouldRename = 0;
        int signatureUpdated = 0;
        int commentOnlyUpdated = 0;
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

    private ParameterImpl param(String name, DataType dataType) throws Exception {
        return new ParameterImpl(name, dataType, currentProgram);
    }

    private String[] concat(String[] common, String... extras) {
        String[] result = new String[common.length + extras.length];
        System.arraycopy(common, 0, result, 0, common.length);
        System.arraycopy(extras, 0, result, common.length, extras.length);
        return result;
    }

    private String[] signatureTags(String... extras) {
        return concat(new String[] {
            "static-reaudit",
            "decode-callback-entropy-head-wave726",
            "wave726-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "signature-hardened",
            "decode-callback-entropy"
        }, extras);
    }

    private String[] commentTags(String... extras) {
        return concat(new String[] {
            "static-reaudit",
            "decode-callback-entropy-head-wave726",
            "wave726-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "comment-only",
            "hidden-register-context",
            "decode-callback-entropy"
        }, extras);
    }

    private Set<String> tagNames(Function fn) {
        Set<String> names = new HashSet<>();
        for (FunctionTag tag : fn.getTags()) {
            names.add(tag.getName());
        }
        return names;
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
        if (spec.updateSignature && !signatureMatches(fn, spec)) {
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
        sb.append(spec.returnType.getDisplayName())
            .append(" ")
            .append(spec.callingConvention)
            .append(" ")
            .append(spec.name)
            .append("(");
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

    private void verifyReadBack(Spec spec) throws Exception {
        Function readBack = functionAtEntry(spec.address);
        if (readBack == null) {
            throw new IllegalStateException("Read-back missing at " + spec.address);
        }
        if (!readBack.getName().equals(spec.name)) {
            throw new IllegalStateException("Read-back name mismatch at " + spec.address + ": " + readBack.getName());
        }
        if (spec.updateSignature && !signatureMatches(readBack, spec)) {
            throw new IllegalStateException("Read-back signature mismatch at " + spec.address + ": " + readBack.getSignature());
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

            boolean needsSignature = spec.updateSignature && !signatureMatches(fn, spec);
            boolean needsAnyUpdate = needsUpdate(fn, spec);
            String signatureText = spec.updateSignature ? expectedSignature(spec) : fn.getSignature().toString();
            if (!needsAnyUpdate) {
                stats.skipped++;
                println("SKIP: " + spec.address + " " + signatureText);
                return;
            }
            if (dryRun) {
                stats.skipped++;
                if (needsSignature) {
                    stats.signatureUpdated++;
                }
                else {
                    stats.commentOnlyUpdated++;
                }
                println("DRY: " + spec.address + " " + signatureText);
                return;
            }
            if (spec.updateSignature) {
                fn.setCallingConvention(spec.callingConvention);
                fn.setReturnType(spec.returnType, SourceType.USER_DEFINED);
                fn.replaceParameters(FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS, true,
                    SourceType.USER_DEFINED, spec.parameters);
            }
            if (needsSignature) {
                stats.signatureUpdated++;
            }
            else {
                stats.commentOnlyUpdated++;
            }
            fn.setComment(spec.comment);
            for (String tag : spec.tags) {
                fn.addTag(tag);
            }
            verifyReadBack(spec);
            stats.updated++;
            println("OK: " + spec.address + " " + signatureText);
            Thread.sleep(75);
        }
        catch (Exception ex) {
            stats.bad++;
            println("FAIL: " + spec.address + " " + spec.name + " :: " + ex.getMessage());
        }
    }

    private Spec[] specs() throws Exception {
        DataType intType = IntegerDataType.dataType;
        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(VoidDataType.dataType);

        return new Spec[] {
            new Spec(
                "0x005ad550",
                "CTexture__InitDecodeCallbackTables",
                true,
                "__stdcall",
                voidType,
                new ParameterImpl[] { param("decode_context", voidPtr) },
                "Wave726 static read-back: initializes the texture decode callback table for a decode context. RET 0x4 evidence restores the single stack argument as decode_context; the function allocates a 0xe8-byte callback/controller table through the context allocator at decode_context +4, stores it at decode_context +0x1c0, seeds callback entries including LAB_005ad410 and LAB_005ad000, and clears four callback/data slots starting at table +0x28. Static retail Ghidra metadata/decompile/instruction/xref evidence only; exact decode context layout, callback table schema, allocator ownership, runtime JPEG/decode behavior, BEA patching, and rebuild parity remain unproven.",
                signatureTags("callback-table", "decode-pipeline", "ret-0x4", "tranche-head")
            ),
            new Spec(
                "0x005ad590",
                "CFastVB__JpegEntropy_CommitAndResetBlockState",
                false,
                "__stdcall",
                intType,
                new ParameterImpl[] {},
                "Wave726 static read-back: commits and resets JPEG entropy block state using the hidden EBX texture/decode context. It advances the source byte position by the buffered bit count rounded to bytes, clears the bit count, calls the source flush callback at source context +8, zeroes per-component block/restart history slots, stores restart interval/state from decode_context +0x118, and clears the marker flag when decode_context +0x1a4 is zero. Ghidra still exposes locked hidden EBX storage, so the current int(void) signature is intentionally retained. Static retail Ghidra metadata/decompile/instruction/xref evidence only; exact context layout, hidden EBX ABI, entropy state layout, callback contract, restart/marker policy, runtime JPEG decode behavior, BEA patching, and rebuild parity remain unproven.",
                commentTags("entropy", "commit-reset", "hidden-ebx-context", "comment-only")
            ),
            new Spec(
                "0x005ae190",
                "CDXTexture__InitBlockCoefficientHistory",
                true,
                "__stdcall",
                voidType,
                new ParameterImpl[] { param("decode_context", voidPtr) },
                "Wave726 static read-back: initializes block coefficient history resources for a texture decode context. RET 0x4 evidence restores the single stack argument as decode_context; the function allocates a 0x40-byte controller at decode_context +0x1c0, installs callback LAB_005adf50, clears controller slots at +0x2c through +0x38, allocates a component-count-scaled coefficient/history buffer at decode_context +0xa4, and fills the active dwords with 0xffffffff. Static retail Ghidra metadata/decompile/instruction/xref evidence only; exact decode context layout, coefficient history layout, component descriptor schema, allocator ownership, runtime JPEG decode behavior, BEA patching, and rebuild parity remain unproven.",
                signatureTags("coefficient-history", "allocator", "ret-0x4")
            ),
            new Spec(
                "0x005ae600",
                "CDXTexture__InitPerComponentCoefficientBuffers",
                true,
                "__stdcall",
                voidType,
                new ParameterImpl[] { param("decode_context", voidPtr) },
                "Wave726 static read-back: initializes per-component coefficient buffers for a texture decode context. RET 0x4 evidence restores the single stack argument as decode_context; the function allocates a 0x54-byte controller at decode_context +0x1c4, installs callback LAB_005ae1f0, allocates one 0x100-byte buffer per component, stores each pointer in the component descriptor at +0x50, zeroes 0x40 dwords per component buffer, and seeds controller per-component slots to 0xffffffff. Static retail Ghidra metadata/decompile/instruction/xref evidence only; exact decode context layout, component descriptor schema, coefficient buffer ownership, callback contract, runtime JPEG decode behavior, BEA patching, and rebuild parity remain unproven.",
                signatureTags("component-coefficients", "allocator", "ret-0x4")
            ),
            new Spec(
                "0x005ae780",
                "CDXTexture__InitScanlineOutputStage",
                true,
                "__stdcall",
                voidType,
                new ParameterImpl[] { param("decode_context", voidPtr) },
                "Wave726 static read-back: initializes the scanline output stage for a texture decode context. RET 0x4 evidence restores the single stack argument as decode_context; the function allocates a 0x1c-byte stage at decode_context +0x1b4, installs callback LAB_005ae700, clears stage slots, optionally stores decode_context +0x13c when decode_context +0x54 is nonzero, dispatches through the stage callback when hidden ESI mode is nonzero, or allocates a row buffer sized from decode_context +0x78 and +0x70 otherwise. Static retail Ghidra metadata/decompile/instruction/xref evidence only; exact decode context layout, hidden ESI mode ABI, scanline stage schema, allocator ownership, runtime JPEG decode behavior, BEA patching, and rebuild parity remain unproven.",
                signatureTags("scanline-output", "hidden-esi-mode", "allocator", "ret-0x4")
            ),
            new Spec(
                "0x005ae810",
                "CDXTexture__RefillEntropyInputWindow",
                false,
                "__stdcall",
                intType,
                new ParameterImpl[] {},
                "Wave726 static read-back: refills/copies from the entropy input window using locked stack parameters and hidden EBP progress state. The function uses the decode context's entropy/input window at +0x1c8, invokes per-component callbacks when the consumed row/span reaches the context span at +0x13c, clamps copy size by context span, window remaining count, and output cursor/end, dispatches the copy/fill callback at decode_context +0x1cc +4, advances output and window offsets, and increments the hidden progress counter at span boundaries. Ghidra still exposes locked ABI/storage, so the current int(void) signature is intentionally retained. Static retail Ghidra metadata/decompile/instruction/xref evidence only; exact decode context layout, stack argument ABI, hidden EBP ABI, entropy window schema, copy callback contract, runtime JPEG decode behavior, BEA patching, and rebuild parity remain unproven.",
                commentTags("entropy-input-window", "hidden-ebp-context", "stack-locked-abi", "comment-only", "tranche-tail")
            )
        };
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = true;
        if (args != null && args.length > 0) {
            dryRun = isDryRun(args[0]);
        }

        println("ApplyDecodeCallbackEntropyHeadWave726 mode=" + (dryRun ? "dry" : "apply"));
        Stats stats = new Stats();
        for (Spec spec : specs()) {
            applySpec(spec, dryRun, stats);
        }
        println("SUMMARY: updated=" + stats.updated
            + " skipped=" + stats.skipped
            + " renamed=" + stats.renamed
            + " would_rename=" + stats.wouldRename
            + " signature_updated=" + stats.signatureUpdated
            + " comment_only_updated=" + stats.commentOnlyUpdated
            + " missing=" + stats.missing
            + " bad=" + stats.bad);
    }
}
