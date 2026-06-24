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

public class ApplyYccChromaConversionHeadWave727 extends GhidraScript {
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
            "ycc-chroma-conversion-head-wave727",
            "wave727-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "signature-hardened",
            "ycc-chroma-conversion"
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
                "0x005aeaf0",
                "CDXTexture__UpsampleChromaLinearHorizontal",
                true,
                "__fastcall",
                voidType,
                new ParameterImpl[] {
                    param("decode_context", voidPtr),
                    param("component_descriptor", voidPtr),
                    param("source_row_table", voidPtr)
                },
                "Wave727 static read-back: horizontally upsamples chroma/sample rows for a texture decode context. The decompile uses hidden EAX as the output row-pointer table, reads the active row count from decode_context +0x13c and the component width/sample count from component_descriptor +0x28, derives the source row table relative to the output row table, and writes first/interior/final linear interpolation samples with 3:1 weighted byte blends. Static retail Ghidra metadata/decompile/instruction/xref evidence only; exact decode context layout, component descriptor schema, row-pointer table layout, hidden EAX ABI, YCC/RGB coefficient identity, runtime JPEG/color conversion behavior, BEA patching, and rebuild parity remain unproven.",
                signatureTags("chroma-upsample", "hidden-eax-output-rows", "linear-horizontal", "tranche-head")
            ),
            new Spec(
                "0x005aebb0",
                "CDXTexture__UpsampleAndConvertYccToRgb_Mmx",
                true,
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("decode_context", voidPtr),
                    param("source_row_table", voidPtr),
                    param("hidden_edi_tail", intType)
                },
                "Wave727 static read-back: MMX-shaped YCC/chroma conversion helper selected by the adaptive scanline path. The this object supplies the component descriptor width/sample count at +0x28, decode_context +0x13c supplies the active row count, hidden EAX supplies the output row-pointer table, and source_row_table is consumed relative to that table while packed conversion constants around DAT_005f49d0/DAT_005f4a00/DAT_005f4a08/DAT_005f4a18 drive byte output. The trailing hidden_edi_tail is preserved because the caller forwards unaff_EDI. Static retail Ghidra metadata/decompile/instruction/xref evidence only; exact decode context layout, component descriptor schema, row-pointer table layout, hidden EAX/EDI ABI, YCC/RGB coefficient identity, runtime JPEG/color conversion behavior, BEA patching, and rebuild parity remain unproven.",
                signatureTags("mmx-ycc-rgb", "hidden-eax-output-rows", "hidden-edi-tail")
            ),
            new Spec(
                "0x005aee40",
                "CDXTexture__UpsampleAndConvertYccToRgb_Scalar",
                true,
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("decode_context", voidPtr),
                    param("component_descriptor", voidPtr),
                    param("source_row_table", voidPtr)
                },
                "Wave727 static read-back: scalar YCC/chroma conversion fallback over two-line source-row neighborhoods. The decompile uses hidden EAX as the output row-pointer table, reads the active row count from decode_context +0x13c and the component width/sample count from component_descriptor +0x28, walks source_row_table entries, and emits interpolated byte pairs with 3:1 weighted blends before advancing to the next row pair. Static retail Ghidra metadata/decompile/instruction/xref evidence only; exact decode context layout, component descriptor schema, row-pointer table layout, hidden EAX ABI, YCC/RGB coefficient identity, runtime JPEG/color conversion behavior, BEA patching, and rebuild parity remain unproven.",
                signatureTags("scalar-ycc-rgb", "hidden-eax-output-rows", "linear-chroma")
            ),
            new Spec(
                "0x005aefa0",
                "CDXTexture__ConvertYccBlocksToRgb_Sse",
                true,
                "__fastcall",
                voidType,
                new ParameterImpl[] {
                    param("color_context", voidPtr),
                    param("component_descriptor", voidPtr),
                    param("decode_context", voidPtr),
                    param("source_row_table", voidPtr)
                },
                "Wave727 static read-back: SSE-shaped YCC block-to-RGB conversion helper selected by the auto dispatch path. The visible color_context ECX argument is forwarded by the caller, component_descriptor +0x28 supplies the component width/sample count, decode_context +0x13c supplies the active row count, hidden EAX supplies the output row-pointer table, and source_row_table gives current/previous/next input rows while packed constants around DAT_005f4a20 drive byte output. Static retail Ghidra metadata/decompile/instruction/xref evidence only; exact decode context layout, component descriptor schema, row-pointer table layout, hidden EAX ABI, YCC/RGB coefficient identity, runtime JPEG/color conversion behavior, BEA patching, and rebuild parity remain unproven.",
                signatureTags("sse-ycc-rgb", "hidden-eax-output-rows", "color-conversion")
            ),
            new Spec(
                "0x005af570",
                "CDXTexture__UpsampleAndConvertScanlineAdaptive",
                true,
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("decode_context", voidPtr),
                    param("component_descriptor", voidPtr),
                    param("source_row_table", voidPtr)
                },
                "Wave727 static read-back: adaptive scanline color-conversion dispatcher for one source-row table. It checks component_descriptor +0x28, scans source_row_table row flags against the decode_context +0x13c row count, signals the decode context's error/progress callback when low flag bits are set, dispatches to the MMX-shaped helper for decode_context +0x48 values 5 or 6 when every row is clean, otherwise falls back to horizontal chroma upsample. The MMX call forwards a hidden EDI tail. Static retail Ghidra metadata/decompile/instruction/xref evidence only; exact decode context layout, component descriptor schema, row-pointer table layout, hidden EDI ABI, dispatch policy, runtime JPEG/color conversion behavior, BEA patching, and rebuild parity remain unproven.",
                signatureTags("adaptive-dispatch", "mmx-dispatch", "hidden-edi-tail")
            ),
            new Spec(
                "0x005af5f0",
                "CDXTexture__ConvertYccBlocksToRgb_Auto",
                true,
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("decode_context", voidPtr),
                    param("component_descriptor", voidPtr),
                    param("source_row_table", voidPtr),
                    param("dispatch_tail", voidPtr)
                },
                "Wave727 static read-back: automatic SSE/scalar YCC block conversion dispatcher. It checks component_descriptor +0x28, scans source_row_table row flags against decode_context +0x13c, signals the decode context's error/progress callback when low flag bits are set, dispatches to the SSE-shaped helper for decode_context +0x48 values 5 or 6 when every row is clean, otherwise falls back to the scalar helper. The decompile still shows an extraout_ECX gap and an unused dispatch_tail stack argument. Static retail Ghidra metadata/decompile/instruction/xref evidence only; exact decode context layout, component descriptor schema, row-pointer table layout, hidden EAX/ECX ABI, dispatch policy, runtime JPEG/color conversion behavior, BEA patching, and rebuild parity remain unproven.",
                signatureTags("auto-dispatch", "sse-dispatch", "scalar-fallback", "extraout-ecx-gap", "tranche-tail")
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

        println("ApplyYccChromaConversionHeadWave727 mode=" + (dryRun ? "dry" : "apply"));
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
