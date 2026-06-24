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

public class ApplyYccLookupResourceHeadWave728 extends GhidraScript {
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
            "ycc-lookup-resource-head-wave728",
            "wave728-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "signature-hardened",
            "ycc-lookup-resource"
        }, extras);
    }

    private String[] commentTags(String... extras) {
        return concat(new String[] {
            "static-reaudit",
            "ycc-lookup-resource-head-wave728",
            "wave728-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "comment-only",
            "hidden-eax-context",
            "ycc-lookup-resource"
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
                "0x005af670",
                "CDXTexture__InitEntropyDecodeResources",
                true,
                "__stdcall",
                voidType,
                new ParameterImpl[] { param("decode_context", voidPtr) },
                "Wave728 static read-back: initializes entropy/decode resource dispatch state for a texture decode context. The function allocates a 0xa0-byte controller through the context allocator, stores it at decode_context +0x1c8, installs the refill callback, checks component sampling against decode_context +0x138/+0x13c, selects per-component resampler/conversion callbacks including the Wave727 adaptive YCC helpers, flags the two-row YCC path when needed, and allocates scanline/component row buffers through the context allocator. Static retail Ghidra metadata/decompile/instruction/xref evidence only; exact decode context layout, component descriptor schema, controller layout, allocator contract, callback table schema, sampling policy, runtime JPEG/color conversion behavior, BEA patching, and rebuild parity remain unproven.",
                signatureTags("entropy-decode-resources", "component-resampler", "callback-dispatch-table", "allocator", "tranche-head")
            ),
            new Spec(
                "0x005af860",
                "CDXTexture__BuildYccToRgbLookupTables",
                false,
                "__stdcall",
                voidType,
                new ParameterImpl[] {},
                "Wave728 static read-back: builds YCC-to-RGB lookup tables using hidden EAX as the texture decode context. The function reads the scanline/color controller at context +0x1cc, allocates four lookup buffers through the context allocator, stores them at controller +8 through +0x14, and fills 256-style coefficient tables using fixed increments and the LAB_005b6900 base pointer. Ghidra still exposes locked hidden EAX storage, so the current void(void) signature is intentionally retained. Static retail Ghidra metadata/decompile/instruction/xref evidence only; exact context layout, controller layout, hidden EAX ABI, allocator contract, coefficient identity, color-space math, runtime JPEG/color conversion behavior, BEA patching, and rebuild parity remain unproven.",
                commentTags("ycc-rgb-lut", "coefficient-table", "hidden-eax-context", "comment-only")
            ),
            new Spec(
                "0x005afbd0",
                "CDXTexture__InterleaveComponentRowsIntoScanline",
                true,
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("decode_context", voidPtr),
                    param("component_row_tables", voidPtr),
                    param("source_row_index", intType),
                    param("output_scanline_table", voidPtr),
                    param("scanline_count", intType)
                },
                "Wave728 static read-back: interleaves component row tables into output scanline rows. The function reads component count from decode_context +0x24 and output width from decode_context +0x70, uses component_row_tables plus source_row_index to select each component source row, walks output_scanline_table entries, and writes component bytes at component-count stride for scanline_count rows. Static retail Ghidra metadata/decompile/instruction/xref evidence only; exact decode context layout, component row-table schema, output scanline schema, component ordering, runtime texture/color conversion behavior, BEA patching, and rebuild parity remain unproven.",
                signatureTags("component-interleave", "scanline-output", "row-table-callback")
            ),
            new Spec(
                "0x005afcf0",
                "CDXTexture__ConvertYccToRgba_WithLookupTables",
                true,
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("decode_context", voidPtr),
                    param("source_component_row_table", voidPtr),
                    param("source_row_index", intType),
                    param("output_rgba_row_table", voidPtr),
                    param("scanline_count", intType)
                },
                "Wave728 static read-back: converts source component rows into RGBA output rows using the lookup tables attached to the decode context. The function reads output width from decode_context +0x70, reads lookup-table pointers from the controller at decode_context +0x1cc, uses decode_context +0x148 as a clamp/base table, selects Y/C/A rows from source_component_row_table plus source_row_index, writes four bytes per output pixel through output_rgba_row_table, and repeats for scanline_count rows. Static retail Ghidra metadata/decompile/instruction/xref evidence only; exact decode context layout, source row-table schema, RGBA byte order, lookup-table coefficient identity, alpha/component semantics, runtime JPEG/color conversion behavior, BEA patching, and rebuild parity remain unproven.",
                signatureTags("ycc-rgba-conversion", "lookup-table-conversion", "rgba-output", "row-table-callback")
            ),
            new Spec(
                "0x005afe60",
                "CDXTexture__InitYccLookupTables",
                false,
                "__stdcall",
                voidType,
                new ParameterImpl[] {},
                "Wave728 static read-back: initializes the extended YCC lookup-table bank using hidden EAX as the texture decode context. The function reads the scanline/color controller at context +0x1cc, allocates ten lookup buffers at controller +0x18 through +0x3c, then fills paired entries with fixed-point coefficient/clamp transforms over the byte domain. Ghidra still exposes locked hidden EAX storage, so the current void(void) signature is intentionally retained. Static retail Ghidra metadata/decompile/instruction/xref evidence only; exact context layout, controller layout, hidden EAX ABI, allocator contract, coefficient identity, clamp semantics, runtime JPEG/color conversion behavior, BEA patching, and rebuild parity remain unproven.",
                commentTags("extended-ycc-lut", "coefficient-table", "hidden-eax-context", "comment-only", "tranche-tail")
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

        println("ApplyYccLookupResourceHeadWave728 mode=" + (dryRun ? "dry" : "apply"));
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
