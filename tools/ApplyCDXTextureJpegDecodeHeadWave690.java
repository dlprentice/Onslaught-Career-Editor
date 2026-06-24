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

public class ApplyCDXTextureJpegDecodeHeadWave690 extends GhidraScript {
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
            "cdxtexture-jpeg-decode-head-wave690",
            "wave690-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "signature-hardened"
        }, extras);
    }

    private String[] commentOnlyTags(String... extras) {
        return concat(new String[] {
            "static-reaudit",
            "cdxtexture-jpeg-decode-head-wave690",
            "wave690-readback-verified",
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
        DataType voidPtr = new PointerDataType(VoidDataType.dataType);
        DataType voidType = VoidDataType.dataType;

        return new Spec[] {
            new Spec(
                "0x00590e10",
                "CDXTexture__FillInputBufferFromSource",
                "__stdcall",
                intType,
                new ParameterImpl[] {
                    param("jpeg_decode_state", voidPtr),
                    param("destination_buffer", voidPtr),
                    param("requested_byte_count", intType)
                },
                true,
                "Wave690 static read-back: validates JPEG input state and source bounds, reports exhausted-source/state mismatches through the decoder error callback, invokes the source read callback at +0x1ac with destination_buffer/requested_byte_count, and advances the consumed-byte cursor by the returned byte count. Static metadata only; exact JPEG source-manager ABI, buffer ownership, and runtime decode fidelity remain unproven.",
                signatureTags("jpeg", "input-buffer", "source-callback", "byte-cursor", "tranche-head")
            ),
            new Spec(
                "0x00590ea0",
                "CDXTexture__ProcessInputControllerState",
                "__stdcall",
                intType,
                new ParameterImpl[] { param("jpeg_decode_state", voidPtr) },
                true,
                "Wave690 static read-back: handles 0xca/0xcb/0xcc JPEG state progression, creates the decode dispatch context when needed, pumps input-controller callbacks, updates input-progress counters, and drains the parser work queue. Static metadata only; exact state enum, callback ABI, dispatch-context layout, and runtime decode behavior remain unproven.",
                signatureTags("jpeg", "input-controller", "decode-dispatch", "parser-work-queue")
            ),
            new Spec(
                "0x00590f80",
                "CDXTexture__InitJpegDecodeState",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("jpeg_decode_state", voidPtr),
                    param("expected_header_size", intType),
                    param("expected_context_size", intType)
                },
                true,
                "Wave690 static read-back: checks the observed 0x3e/0x1d8 setup constants, clears the JPEG decode-state block while preserving saved header slots, initializes the decode allocator, marker reader, callback context, and starts the state machine at 0xc8. Static metadata only; exact state layout, constant names, allocator ABI, and runtime decode behavior remain unproven.",
                signatureTags("jpeg", "decode-state", "marker-reader", "allocator", "callback-context")
            ),
            new Spec(
                "0x00591050",
                "CFastVB__ReleaseOwnedObjectAndReset",
                "__stdcall",
                voidType,
                new ParameterImpl[] { param("decode_state_header", voidPtr) },
                true,
                "Wave690 static read-back: releases the owned object through vtable slot +0x28 when present, then clears the owner pointer and stage/status field. Static metadata only; exact owner type, release ABI, and whether this helper is shared beyond JPEG decode remain unproven.",
                signatureTags("jpeg", "owned-object-release", "vtable-release", "cleanup")
            ),
            new Spec(
                "0x00591060",
                "CDXTexture__SelectJpegOutputDefaults",
                "",
                voidType,
                new ParameterImpl[] {},
                false,
                "Wave690 static read-back: uses the ESI-held JPEG decode state to select output color/component defaults from component count, Adobe transform flag, and observed RGB/YCbCr component ids, emits error ids 0x6f/0x72 on unsupported combinations, and resets output counters/defaults. Signature intentionally left unchanged because Ghidra records this helper with locked register-context storage; exact output enum, color-transform semantics, and state layout remain unproven.",
                commentOnlyTags("jpeg", "output-defaults", "color-transform", "register-context")
            ),
            new Spec(
                "0x005911d0",
                "CDXTexture__AdvanceJpegDecodeState",
                "__stdcall",
                intType,
                new ParameterImpl[] { param("jpeg_decode_state", voidPtr) },
                true,
                "Wave690 static read-back: advances the JPEG state machine from 0xc8/0xc9 into 0xca and later decode states, primes marker/input callbacks, invokes output-default selection when the marker controller reports ready, and reports unexpected states through the decoder error callback. Static metadata only; exact state enum, marker-controller ABI, and runtime decode sequencing remain unproven.",
                signatureTags("jpeg", "state-machine", "output-defaults", "marker-reader")
            ),
            new Spec(
                "0x00591280",
                "CDXTexture__DecodeJpegStream_PumpUntilReady",
                "__stdcall",
                intType,
                new ParameterImpl[] { param("jpeg_decode_state", voidPtr) },
                true,
                "Wave690 static read-back: handles 0xcd/0xce/0xcf/0xd2 stream states, reports short-source conditions when buffered input remains, invokes the stream-finalization callback, pumps the marker controller until output is ready, then advances allocator/stage setup. Static metadata only; exact end-of-stream semantics, callback ABI, and runtime decode fidelity remain unproven.",
                signatureTags("jpeg", "pump-until-ready", "allocator-stage", "end-of-stream")
            ),
            new Spec(
                "0x00591340",
                "CDXTexture__PumpDecoderStreamAndFinalize",
                "__stdcall",
                intType,
                new ParameterImpl[] {
                    param("jpeg_decode_state", voidPtr),
                    param("require_end_of_image", intType)
                },
                true,
                "Wave690 static read-back: validates the initial JPEG state, advances the decode state machine, handles result 2 by optionally reporting strict end-of-image error 0x33, pumps allocator/stage setup, and returns the decoder status. Static metadata only; exact result enum, strict-Eoi contract, and runtime decode behavior remain unproven.",
                signatureTags("jpeg", "decoder-finalize", "strict-eoi", "pump-wrapper", "tranche-tail")
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

        println("ApplyCDXTextureJpegDecodeHeadWave690 mode=" + (dryRun ? "dry" : "apply"));
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
