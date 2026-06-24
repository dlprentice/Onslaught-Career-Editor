//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.DataType;
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

public class ApplyCDXTextureJpegSegmentParsersWave691 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] parameters;
        final boolean updateSignature;
        final String comment;
        final String[] tags;

        Spec(String address, String name, String callingConvention, DataType returnType,
                ParameterImpl[] parameters, boolean updateSignature, String comment, String[] tags) {
            this.address = address;
            this.name = name;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.parameters = parameters;
            this.updateSignature = updateSignature;
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
            "cdxtexture-jpeg-segment-parsers-wave691",
            "wave691-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "signature-hardened"
        }, extras);
    }

    private String[] commentOnlyTags(String... extras) {
        return concat(new String[] {
            "static-reaudit",
            "cdxtexture-jpeg-segment-parsers-wave691",
            "wave691-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "comment-only"
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
        if (!spec.updateSignature) {
            return true;
        }
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
        if (!spec.updateSignature) {
            return "<comment/tag-only; saved signature intentionally unchanged>";
        }
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
            boolean needsSignature = spec.updateSignature && !signatureMatches(fn, spec);
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
                if (!spec.updateSignature) {
                    stats.commentOnlyUpdated++;
                }
                println("DRY: " + spec.address + " actual=" + fn.getSignature() + " expected=" + expectedSignature(spec));
                return;
            }

            if (spec.updateSignature) {
                fn.setCallingConvention(spec.callingConvention);
                fn.setReturnType(spec.returnType, SourceType.USER_DEFINED);
                fn.replaceParameters(
                    FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS,
                    true,
                    SourceType.USER_DEFINED,
                    spec.parameters
                );
            }
            fn.setComment(spec.comment);
            for (String tag : spec.tags) {
                fn.addTag(tag);
            }
            verifyReadBack(spec);

            stats.updated++;
            if (needsSignature) {
                stats.signatureUpdated++;
            }
            if (!spec.updateSignature) {
                stats.commentOnlyUpdated++;
            }
            println("OK: " + spec.address + " " + expectedSignature(spec));
        } catch (Exception ex) {
            stats.bad++;
            println("BAD: " + spec.address + " " + spec.name + " " + ex.getClass().getSimpleName() + ": " + ex.getMessage());
        }
    }

    private Spec[] specs() throws Exception {
        DataType intType = IntegerDataType.dataType;
        DataType uintType = UnsignedIntegerDataType.dataType;
        DataType voidPtr = new PointerDataType(VoidDataType.dataType);
        DataType voidType = VoidDataType.dataType;

        return new Spec[] {
            new Spec(
                "0x00591460",
                "CDXTexture__DecodeJpegSegment_StartOfFrame",
                "__fastcall",
                intType,
                new ParameterImpl[] { param("param_1", intType) },
                false,
                "Wave691 static read-back: parses a JPEG start-of-frame segment, records marker/context fields into the decode state, reads sample precision, image width/height, and component count, validates nonzero dimensions and component triplets, allocates or uses the component descriptor table, records component id, horizontal/vertical sampling factors, and quant table selector, and emits diagnostics 0x3a/0x20/0x0b/0x65. Signature intentionally left unchanged because Ghidra exposes register-context inputs through EAX/ESI/EBX around the fastcall parameter; exact SOF marker enum, frame-header layout, component descriptor layout, and runtime decode fidelity remain unproven.",
                commentOnlyTags("jpeg", "start-of-frame", "component-descriptors", "sampling-factors", "quant-table-selector", "tranche-head")
            ),
            new Spec(
                "0x005919e0",
                "CDXTexture__DecodeJpegSegment_HuffmanTables",
                "",
                intType,
                new ParameterImpl[] {},
                false,
                "Wave691 static read-back: parses a JPEG DHT/Huffman-table segment, reads the segment length, table class/id byte, sixteen code-length counts, validates symbol budget and remaining segment bytes, allocates a table descriptor when needed, copies the code-length counts and symbol bytes, and emits diagnostics 0x50/0x56/0x08/0x1e. Signature intentionally left unchanged because Ghidra reports an unknown calling convention with locked parameter storage; exact Huffman descriptor layout, table class enum, entropy decoder ABI, and runtime decode fidelity remain unproven.",
                commentOnlyTags("jpeg", "huffman-table", "dht", "code-length-counts", "symbol-budget", "locked-storage")
            ),
            new Spec(
                "0x00591cb0",
                "CDXTexture__DecodeJpegSegment_QuantizationTables",
                "__stdcall",
                intType,
                new ParameterImpl[] { param("jpeg_decode_state", voidPtr) },
                true,
                "Wave691 static read-back: parses a JPEG DQT/quantization-table segment, reads the 16-bit segment length, precision/table-id byte, validates table id <= 3, allocates a quant table descriptor when missing, fills 64 coefficients through the observed zigzag table at DAT_005f37f8, supports 8-bit and 16-bit coefficient forms, and emits diagnostics 0x51/0x1f/0x5d. Static metadata only; exact quant descriptor layout, zigzag table contract, precision scaling, and runtime decode fidelity remain unproven.",
                signatureTags("jpeg", "quantization-table", "dqt", "zigzag-table", "coefficient-reader", "descriptor-allocation")
            ),
            new Spec(
                "0x00591ef0",
                "CDXTexture__DecodeJpegSegment_RestartInterval",
                "__stdcall",
                intType,
                new ParameterImpl[] { param("jpeg_decode_state", voidPtr) },
                true,
                "Wave691 static read-back: parses a JPEG DRI/restart-interval segment, requires the observed 16-bit length field to equal 4, reads the restart interval value, emits diagnostic 0x52, stores the interval at the observed +0x118 slot, advances buffered input state, and reports malformed length through diagnostic 0x0b. Static metadata only; exact restart interval field name, restart-marker reset behavior, marker reader ABI, and runtime decode fidelity remain unproven.",
                signatureTags("jpeg", "restart-interval", "dri", "marker-reader", "restart-marker", "interval-field")
            ),
            new Spec(
                "0x00591fc0",
                "CDXTexture__ParseJfifApp0Header",
                "__fastcall",
                voidType,
                new ParameterImpl[] { param("param_1", intType) },
                false,
                "Wave691 static read-back: parses a JPEG APP0 JFIF/JFXX header from register-held payload pointer and length/start context, validates the JFIF signature, records version, density units, x/y density, and thumbnail dimensions, emits diagnostics 0x4d/0x57/0x58/0x5a/0x77, and handles JFXX extension diagnostics 0x6c/0x6d/0x6e/0x59. Signature intentionally left unchanged because Ghidra exposes payload length/start through register context around the fastcall parameter; exact APP0 offset contract, density enum, thumbnail policy, and runtime decode fidelity remain unproven.",
                commentOnlyTags("jpeg", "app0", "jfif", "jfxx", "density-fields", "thumbnail-dimensions")
            ),
            new Spec(
                "0x005921a0",
                "CDXTexture__ParseAdobeApp14Header",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("param_1", uintType),
                    param("param_2", intType)
                },
                false,
                "Wave691 static read-back: parses a JPEG APP14 Adobe header from register-held payload pointer and Ghidra-labelled length/start fields, validates the Adobe signature, records version/flags/transform byte diagnostics, stores the transform byte at the observed +0x12c slot, sets the APP14-present flag at +0x128, and emits diagnostics 0x4c/0x4e. Signature intentionally left unchanged because Ghidra's thiscall shape treats a length as this and leaves the register-held payload pointer outside formal parameters; exact APP14 transform enum, offset contract, color-transform policy, and runtime decode fidelity remain unproven.",
                commentOnlyTags("jpeg", "app14", "adobe", "transform-byte", "color-transform", "register-context", "tranche-tail")
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

        println("ApplyCDXTextureJpegSegmentParsersWave691 mode=" + (dryRun ? "dry" : "apply"));
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
