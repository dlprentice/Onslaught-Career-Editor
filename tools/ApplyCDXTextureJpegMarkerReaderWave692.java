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

public class ApplyCDXTextureJpegMarkerReaderWave692 extends GhidraScript {
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
            "cdxtexture-jpeg-marker-reader-wave692",
            "wave692-readback-verified",
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
            println("OK: " + spec.address + " " + expectedSignature(spec));
        } catch (Exception ex) {
            stats.bad++;
            println("BAD: " + spec.address + " " + spec.name + " " + ex.getClass().getSimpleName() + ": " + ex.getMessage());
        }
    }

    private Spec[] specs() throws Exception {
        DataType intType = IntegerDataType.dataType;
        DataType voidPtr = new PointerDataType(VoidDataType.dataType);
        DataType voidType = VoidDataType.dataType;

        return new Spec[] {
            new Spec(
                "0x00592380",
                "CTexture__ReadJpegSegmentLengthAndEmitMarker",
                "__stdcall",
                intType,
                new ParameterImpl[] { param("jpeg_decode_state", voidPtr) },
                "Wave692 static read-back: reads the two-byte JPEG segment length through the buffered input source at +0x18, refills through callback +0x0c when needed, stores diagnostic id 0x5b plus marker/length context through the error callback record, records the length minus the two length bytes, optionally skips remaining bytes through callback +0x10, and returns decoder status. Static metadata only; exact marker-reader object layout, segment-length contract, callback ABI, and runtime decode fidelity remain unproven.",
                signatureTags("jpeg", "marker-reader", "segment-length", "input-buffer", "diagnostic-0x5b", "tranche-head")
            ),
            new Spec(
                "0x00592420",
                "CTexture__SkipJpegFillBytesAndReadMarker",
                "__stdcall",
                intType,
                new ParameterImpl[] { param("jpeg_decode_state", voidPtr) },
                "Wave692 static read-back: scans the buffered JPEG input stream until a marker prefix is found, skips non-marker bytes and stuffed 0xff/0x00 fill sequences while accumulating skipped-byte count at marker-reader +0x18, emits diagnostic id 0x74 when bytes were skipped, writes the current marker byte to decode-state +0x1a4, and returns decoder status. Static metadata only; exact skipped-byte counter meaning, marker stuffing policy, callback ABI, and runtime decode fidelity remain unproven.",
                signatureTags("jpeg", "marker-reader", "fill-byte-skip", "stuffed-marker", "diagnostic-0x74", "current-marker")
            ),
            new Spec(
                "0x00592530",
                "CFastVB__JpegParser_ReadAndValidateSOI",
                "__stdcall",
                intType,
                new ParameterImpl[] { param("jpeg_decode_state", voidPtr) },
                "Wave692 static read-back: reads the first two buffered JPEG bytes, refills through callback +0x0c when needed, validates the SOI marker bytes 0xff/0xd8, emits diagnostic id 0x35 with the observed bytes on mismatch, advances the buffer cursor, records the marker byte at decode-state +0x1a4, and returns decoder status. Static metadata only; exact parser owner identity, SOI precondition contract, callback ABI, and runtime decode fidelity remain unproven.",
                signatureTags("jpeg", "marker-reader", "start-of-image", "soi", "diagnostic-0x35", "input-buffer")
            ),
            new Spec(
                "0x005928d0",
                "CDXTexture__ConsumeExpectedRestartMarker",
                "__stdcall",
                intType,
                new ParameterImpl[] { param("jpeg_decode_state", voidPtr) },
                "Wave692 static read-back: consumes or fetches the current JPEG marker, compares it with the expected restart marker computed from marker-reader +0x14 plus 0xd0, emits diagnostic id 0x62 for the matched restart marker, clears decode-state +0x1a4 after a match, falls back to the marker-reader +0x14 resync callback when mismatched, advances the expected restart index modulo 8, and returns decoder status. Static metadata only; exact restart-index field name, restart recovery policy, marker-reader callback ABI, and runtime decode fidelity remain unproven.",
                signatureTags("jpeg", "marker-reader", "restart-marker", "restart-index", "diagnostic-0x62", "resync-callback")
            ),
            new Spec(
                "0x00592950",
                "CDXTexture__ClassifyRestartMarkerResync",
                "__stdcall",
                intType,
                new ParameterImpl[] {
                    param("jpeg_decode_state", voidPtr),
                    param("expected_restart_index", intType)
                },
                "Wave692 static read-back: logs diagnostic id 0x79 for a restart-marker resync attempt, classifies the current marker relative to the expected restart index into observed result classes 1/2/3, emits diagnostic id 0x61 with the marker and class, clears decode-state +0x1a4 for class 1, loops through CTexture__SkipJpegFillBytesAndReadMarker for class 2, and returns decoder status for class 3. Static metadata only; exact resync-class enum, recovery policy, restart-marker sequence semantics, and runtime decode fidelity remain unproven.",
                signatureTags("jpeg", "marker-reader", "restart-resync", "restart-index", "diagnostic-0x79", "diagnostic-0x61")
            ),
            new Spec(
                "0x00592a80",
                "CDXTexture__InitJpegMarkerReader",
                "__stdcall",
                voidType,
                new ParameterImpl[] { param("jpeg_decode_state", voidPtr) },
                "Wave692 static read-back: allocates the observed 0xac-byte marker-reader context through the decode-state allocator at +0x04, stores it at decode-state +0x1bc, seeds callback slots for reset, frame/SOI handling, restart consumption, segment-length readers, and APP parser defaults, clears sixteen segment callback counters, installs default APP handlers at slots +0x20/+0x58, and clears decode-state marker fields at +0xdc/+0x94/+0x1a4. Static metadata only; exact marker-reader structure, callback-table ABI, APP slot ownership, and runtime decode fidelity remain unproven.",
                signatureTags("jpeg", "marker-reader", "callback-table", "allocator", "app-handler", "tranche-tail")
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

        println("ApplyCDXTextureJpegMarkerReaderWave692 mode=" + (dryRun ? "dry" : "apply"));
        Stats stats = new Stats();
        for (Spec spec : specs()) {
            applySpec(spec, dryRun, stats);
        }
        println("SUMMARY: updated=" + stats.updated
            + " skipped=" + stats.skipped
            + " renamed=" + stats.renamed
            + " would_rename=" + stats.wouldRename
            + " signature_updated=" + stats.signatureUpdated
            + " missing=" + stats.missing
            + " bad=" + stats.bad);
    }
}
