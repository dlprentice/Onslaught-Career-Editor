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

public class ApplyJpegScanControllerHeadWave736 extends GhidraScript {
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
            "jpeg-scan-controller-head-wave736",
            "wave736-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "signature-hardened",
            "jpeg-scan-controller-head"
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
                "0x005b7ee0",
                "CDXTexture__ProcessJpegScanStateMachine",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("jpeg_codec_state", voidPtr)
                },
                "Wave736 static read-back: drives the active JPEG scan-controller state machine from the controller at state +0x154. RET 0x4 callback slot is installed by CDXTexture__InitJpegScanController at controller +0x00; phase 0 loads the current scan descriptor, builds the MCU layout, optionally invokes color-converter/upsampler/sample-buffer controllers for non-direct color paths, then runs DCT/quant, entropy/scan-script, output, and source/writer callbacks before setting controller +0xc. Phases 1 and 2 handle progressive/restart-style scan advancement, invoke writer callbacks at state +0x164 +4/+8, update controller +0x10 when the final scan is reached, and mirror scan progress into the optional status block at state +8; unexpected phase values report codec error id 0x30. Static retail Ghidra metadata/decompile/instruction/xref evidence only; exact controller struct, JPEG mode enums, callback ABI, runtime JPEG output behavior, BEA patching, and rebuild parity remain unproven.",
                signatureTags("tranche-head", "scan-state-machine", "jpeg-scan-controller", "ret-0x4")
            ),
            new Spec(
                "0x005b8060",
                "CDXTexture__AbortJpegScanStateMachine",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("jpeg_codec_state", voidPtr)
                },
                "Wave736 static read-back: aborts the active JPEG scan controller by clearing controller field +0xc and invoking writer/source callbacks at state +0x164 +4 and +8. RET 0x4 callback slot is installed by CDXTexture__InitJpegScanController at controller +0x04 next to the process callback and local callback label 0x005b8090. Static retail Ghidra metadata/decompile/instruction/xref evidence only; exact controller struct, callback ABI, abort ownership, runtime JPEG output behavior, BEA patching, and rebuild parity remain unproven.",
                signatureTags("abort-callback", "scan-controller-abort", "jpeg-scan-controller", "ret-0x4")
            ),
            new Spec(
                "0x005b8110",
                "CDXTexture__InitJpegScanController",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("jpeg_codec_state", voidPtr),
                    param("scan_controller_start_mode", intType)
                },
                "Wave736 static read-back: allocates and initializes the 0x24-byte JPEG scan-controller table at state +0x154. RET 0x8 caller evidence at CDXTexture__InitializeJpegEncoderPipeline pushes a mode flag then jpeg_codec_state before the call; the helper installs process/abort/local callback slots at controller +0x00/+0x04/+0x08, validates the frame MCU layout and optional scan script, sets state +0xec/+0xa8/+0xb8 for single-scan or script-driven paths, derives controller +0x14 from scan_controller_start_mode and state +0xb8, clears controller +0x18/+0x20, and stores the scan count at controller +0x1c as state +0xa8 or state +0xa8 << 1. Static retail Ghidra metadata/decompile/instruction/xref evidence only; exact controller struct, scan script semantics, local callback boundary at 0x005b8090, callback ABI, runtime JPEG output behavior, BEA patching, and rebuild parity remain unproven.",
                signatureTags("tranche-tail", "scan-controller-init", "controller-init", "callback-table", "ret-0x8")
            )
        };
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = args == null || args.length == 0 || isDryRun(args[0]);
        Stats stats = new Stats();

        println("ApplyJpegScanControllerHeadWave736 mode=" + (dryRun ? "dry" : "apply"));
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
            throw new IllegalStateException("Wave736 had bad=" + stats.bad + " missing=" + stats.missing);
        }
    }
}
