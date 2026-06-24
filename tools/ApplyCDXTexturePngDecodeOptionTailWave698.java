//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.DoubleDataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.UnsignedIntegerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.FunctionTag;
import ghidra.program.model.listing.Parameter;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyCDXTexturePngDecodeOptionTailWave698 extends GhidraScript {
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
            "cdxtexture-png-decode-option-tail-wave698",
            "wave698-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "signature-hardened"
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
                }
                else {
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
            }
            else {
                stats.commentOnlyUpdated++;
            }
            println("OK: " + spec.address + " " + expectedSignature(spec));
        } catch (Exception ex) {
            stats.bad++;
            println("BAD: " + spec.address + " " + spec.name + " " + ex.getClass().getSimpleName() + ": " + ex.getMessage());
        }
    }

    private Spec[] specs() throws Exception {
        DataType doubleType = DoubleDataType.dataType;
        DataType intType = IntegerDataType.dataType;
        DataType uintType = UnsignedIntegerDataType.dataType;
        DataType voidPtr = new PointerDataType(VoidDataType.dataType);
        DataType voidType = VoidDataType.dataType;

        return new Spec[] {
            new Spec(
                "0x00594ef8",
                "CDXTexture__SetDecodeOptionFloat",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("png_decode_state", voidPtr),
                    param("png_info_state", voidPtr),
                    param("option_value", doubleType)
                },
                "Wave698 static read-back: after null checks, ORs the observed info-state valid-option bitmask with 0x1 and stores option_value as a float at info_state +0x28; current xrefs include PNG gAMA parsing and the sRGB default-gamma helper. Static metadata only; exact info-state layout, option enum, gamma policy, and runtime PNG behavior remain unproven.",
                signatureTags("png", "decode-options", "info-state", "gamma", "tranche-head")
            ),
            new Spec(
                "0x00594fb6",
                "CTexture__SetDecodeScanParameters",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("png_decode_state", voidPtr),
                    param("png_info_state", voidPtr),
                    param("scan_parameter_table", voidPtr),
                    param("scan_parameter_count", intType)
                },
                "Wave698 static read-back: after null checks, ORs the observed info-state bitmask with 0x8, stores scan_parameter_table at +0x10, and stores the low word of scan_parameter_count at +0x14; current xref is PNG PLTE parsing. Static metadata only; exact table layout, field names, palette semantics, and runtime PNG behavior remain unproven.",
                signatureTags("png", "decode-options", "info-state", "plte", "palette")
            ),
            new Spec(
                "0x00594fdc",
                "CDXTexture__SetDecodeOptionByte",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("png_decode_state", voidPtr),
                    param("png_info_state", voidPtr),
                    param("option_byte_value", intType)
                },
                "Wave698 static read-back: after null checks, ORs info_state +0x9 with byte flag 0x8 and stores the low byte of option_byte_value at info_state +0x2c; current xrefs include PNG-from-memory setup and the sRGB byte-plus-default-gamma helper. Static metadata only; exact byte option identity, info-state layout, and runtime PNG behavior remain unproven.",
                signatureTags("png", "decode-options", "info-state", "byte-option")
            ),
            new Spec(
                "0x00594ff9",
                "CDXTexture__SetDecodeOptionByteWithDefaultFloat",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("png_decode_state", voidPtr),
                    param("png_info_state", voidPtr),
                    param("option_byte_value", intType)
                },
                "Wave698 static read-back: after null checks, calls the byte-option helper with option_byte_value, then calls the float-option helper with the static double at 0x005eeb30; current xref is PNG sRGB parsing. Static metadata only; exact default value meaning, sRGB/gamma policy, and runtime PNG behavior remain unproven.",
                signatureTags("png", "decode-options", "info-state", "srgb", "default-gamma")
            ),
            new Spec(
                "0x00595030",
                "CDXTexture__SetDecodeOptionParams",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("png_decode_state", voidPtr),
                    param("png_info_state", voidPtr),
                    param("parameter_table", voidPtr),
                    param("parameter_count", intType),
                    param("parameter_record", voidPtr)
                },
                "Wave698 static read-back: after null checks, stores parameter_table at info_state +0x30 when non-null, copies a 10-byte parameter_record into info_state +0x34 when supplied, defaults parameter_count to 1 for a copied record with zero count, ORs the observed bitmask with 0x10, and stores the low word count at +0x16. Static metadata only; exact tRNS/record layout, ownership, and runtime PNG behavior remain unproven.",
                signatureTags("png", "decode-options", "info-state", "trns", "record-copy")
            ),
            new Spec(
                "0x00595079",
                "CDXTexture__ReadFromSource",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("png_decode_state", voidPtr),
                    param("destination_buffer", voidPtr),
                    param("requested_byte_count", uintType)
                },
                "Wave698 static read-back: reads the source callback from png_decode_state +0x50, throws a decode error when it is null, otherwise calls it with the decode state, destination_buffer, and requested_byte_count. Static metadata only; exact callback ABI, source object layout, error string contract, and runtime stream behavior remain unproven.",
                signatureTags("png", "source-read", "read-callback", "decode-state")
            ),
            new Spec(
                "0x005950a2",
                "CDXTexture__SetReadFunction",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("png_decode_state", voidPtr),
                    param("read_context", voidPtr),
                    param("read_callback", voidPtr)
                },
                "Wave698 static read-back: stores read_context at decode_state +0x54 and read_callback at +0x50, clears +0x4c with two warnings if a buffered-read slot was already present, then clears +0x120. Static metadata only; exact read callback prototype, buffered-read state layout, warning semantics, and runtime stream behavior remain unproven.",
                signatureTags("png", "source-read", "read-callback", "decode-state")
            ),
            new Spec(
                "0x005950e0",
                "CDXTexture__ComparePngSignatureBytes",
                "__stdcall",
                intType,
                new ParameterImpl[] {
                    param("signature_buffer", voidPtr),
                    param("start_offset", uintType),
                    param("bytes_to_check", uintType)
                },
                "Wave698 static read-back: compares a caller-selected slice of signature_buffer against the 8-byte PNG signature literal at 0x005eebcc, clamps bytes_to_check to the remaining signature span, and returns zero for equality or a signed byte-order result for mismatch. Static metadata only; exact caller preconditions, error policy, and runtime PNG acceptance behavior remain unproven.",
                signatureTags("png", "signature-check", "png-signature", "tranche-tail")
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

        println("ApplyCDXTexturePngDecodeOptionTailWave698 mode=" + (dryRun ? "dry" : "apply"));
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
