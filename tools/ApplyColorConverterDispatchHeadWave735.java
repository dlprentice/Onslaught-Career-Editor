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

public class ApplyColorConverterDispatchHeadWave735 extends GhidraScript {
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
            "color-converter-dispatch-head-wave735",
            "wave735-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "signature-hardened",
            "color-converter-dispatch-head"
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
        if (!signatureMatches(readBack, spec)) {
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
            boolean needsSignature = !signatureMatches(fn, spec);
            if (!needsUpdate(fn, spec)) {
                stats.skipped++;
                println("SKIP: " + spec.address + " " + expectedSignature(spec));
                return;
            }
            if (dryRun) {
                stats.skipped++;
                if (needsSignature) {
                    stats.signatureUpdated++;
                } else {
                    stats.commentOnlyUpdated++;
                }
                println("DRY: " + spec.address + " actual=" + fn.getSignature() + " expected=" + expectedSignature(spec));
                return;
            }

            fn.setCallingConvention(spec.callingConvention);
            fn.setReturnType(spec.returnType, SourceType.USER_DEFINED);
            fn.replaceParameters(
                FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS,
                true,
                SourceType.USER_DEFINED,
                spec.parameters
            );
            fn.setComment(spec.comment);
            for (String tag : spec.tags) {
                fn.addTag(tag);
            }
            verifyReadBack(spec);

            stats.updated++;
            if (needsSignature) {
                stats.signatureUpdated++;
            } else {
                stats.commentOnlyUpdated++;
            }
            println("OK: " + spec.address + " " + expectedSignature(spec));
            Thread.sleep(75);
        } catch (Exception ex) {
            stats.bad++;
            println("FAIL: " + spec.address + " " + spec.name + " :: " + ex.getMessage());
        }
    }

    private Spec[] specs() throws Exception {
        DataType intType = IntegerDataType.dataType;
        DataType voidPtr = new PointerDataType(VoidDataType.dataType);
        DataType voidType = VoidDataType.dataType;

        return new Spec[] {
            new Spec(
                "0x005b71b0",
                "CDXTexture__ConvertRgbRowsToGrayscale",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("jpeg_codec_state", voidPtr),
                    param("source_row_table", voidPtr),
                    param("output_row_table", voidPtr),
                    param("output_start_row", intType),
                    param("row_count", intType)
                },
                "Wave735 static read-back: converts RGB source rows into grayscale/luma rows through the active color-converter controller. RET 0x14 callback slot is installed by CDXTexture__InitColorConverterDispatch when source color mode +0x28 selects RGB-family input and output mode +0x40 expects one channel; the helper reads pixel width from state +0x1c, dereferences source_row_table and output_row_table + output_start_row, uses the lookup table pointer stored at state +0x168/+8, combines the three RGB byte channels through 0x0/0x400/0x800 table bands, and writes one output byte per pixel per row. Static retail Ghidra metadata/decompile/instruction/xref evidence only; exact color-mode enum, lookup-table schema, channel order, row-table ownership, runtime JPEG output behavior, BEA patching, and rebuild parity remain unproven.",
                signatureTags("tranche-head", "grayscale-conversion", "jpeg-color-converter", "luma-lookup-table", "ret-0x14")
            ),
            new Spec(
                "0x005b7480",
                "CDXTexture__CopyInterleavedChannelRows",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("jpeg_codec_state", voidPtr),
                    param("source_row_table", voidPtr),
                    param("output_row_table", voidPtr),
                    param("output_start_row", intType),
                    param("row_count", intType)
                },
                "Wave735 static read-back: copies one selected channel from interleaved source rows into destination component rows. RET 0x14 callback slot is installed by CDXTexture__InitColorConverterDispatch for direct-compatible one/three-channel paths; the helper reads pixel width from state +0x1c, source channel stride from state +0x24, dereferences source_row_table and output_row_table + output_start_row, advances the source cursor by the stride per pixel, and writes one output byte per pixel per row. Static retail Ghidra metadata/decompile/instruction/xref evidence only; exact color-mode enum, channel order, row-table ownership, destination component semantics, runtime JPEG output behavior, BEA patching, and rebuild parity remain unproven.",
                signatureTags("channel-copy", "interleaved-channel-copy", "jpeg-color-converter", "row-table-helper", "ret-0x14")
            ),
            new Spec(
                "0x005b7580",
                "CDXTexture__InitColorConverterDispatch",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("jpeg_codec_state", voidPtr)
                },
                "Wave735 static read-back: allocates and initializes the JPEG color-converter dispatch/controller table. RET 0x4 caller CDXTexture__InitializeJpegEncoderPipeline reaches this helper when state +0xb0 is zero; the helper allocates a 0xc-byte controller at state +0x168, installs controller entry 0x005b0ed0, validates source mode fields +0x28/+0x24 and output mode fields +0x40/+0x3c, reports error ids 9, 10, or 0x1b through the codec error callback for incompatible modes, and installs callback slot +4 with CDXTexture__CopyInterleavedChannelRows, CDXTexture__ConvertRgbRowsToGrayscale, or local color-conversion labels at 0x005b6e70, 0x005b6f50, 0x005b7080, 0x005b7250, 0x005b7300, and 0x005b74e0. Static retail Ghidra metadata/decompile/instruction/xref evidence only; exact color-mode enum, controller schema, local helper boundaries, callback ABI, runtime JPEG output behavior, BEA patching, and rebuild parity remain unproven.",
                signatureTags("tranche-tail", "color-converter-dispatch", "controller-init", "jpeg-color-converter", "ret-0x4")
            )
        };
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = args == null || args.length == 0 || isDryRun(args[0]);
        Stats stats = new Stats();

        println("ApplyColorConverterDispatchHeadWave735 mode=" + (dryRun ? "dry" : "apply"));
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

        if (stats.bad > 0 || stats.missing > 0) {
            throw new IllegalStateException("Wave735 had bad=" + stats.bad + " missing=" + stats.missing);
        }
    }
}
