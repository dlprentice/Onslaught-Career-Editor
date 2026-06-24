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

public class ApplyCDXTextureParserContextDiagnosticsWave693 extends GhidraScript {
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
            "cdxtexture-parser-context-diagnostics-wave693",
            "wave693-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "signature-hardened"
        }, extras);
    }

    private String[] commentOnlyTags(String... extras) {
        return concat(new String[] {
            "static-reaudit",
            "cdxtexture-parser-context-diagnostics-wave693",
            "wave693-readback-verified",
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
        DataType voidPtr = new PointerDataType(VoidDataType.dataType);
        DataType voidType = VoidDataType.dataType;

        return new Spec[] {
            new Spec(
                "0x00592b00",
                "CFastVB__ParserContext_Shutdown",
                "__stdcall",
                voidType,
                new ParameterImpl[] { param("parser_context", voidPtr) },
                true,
                "Wave693 static read-back: releases the parser-context owned object, calls the observed shutdown callback slots, invokes CRT__CExit(1), and dispatches the stack-held final callback record seeded by CFastVB__ParserContext_Init. Static metadata only; exact parser-context layout, callback-table ABI, shutdown ownership contract, and runtime JPEG/PNG decode behavior remain unproven.",
                signatureTags("parser-context", "shutdown", "callback-table", "owned-object-release", "tranche-head")
            ),
            new Spec(
                "0x00592c50",
                "CFastVB__ParserContext_Init",
                "__stdcall",
                voidType,
                new ParameterImpl[] { param("parser_context", voidPtr) },
                true,
                "Wave693 static read-back: seeds parser-context callback slots at the observed +0x00/+0x04/+0x08/+0x0c/+0x10 offsets, clears state fields at +0x14/+0x68/+0x6c/+0x78/+0x7c/+0x80, installs the default bogus-message-code diagnostic text pointer at +0x70, and records diagnostic id 0x7b at +0x74. Static metadata only; exact parser-context structure, callback ABI, diagnostic-table ownership, and runtime JPEG decode behavior remain unproven.",
                signatureTags("parser-context", "init", "callback-table", "diagnostic-default", "bogus-message-code")
            ),
            new Spec(
                "0x00592ca0",
                "CDXTexture__FormatChunkTagForDiagnostics",
                "__thiscall",
                voidType,
                new ParameterImpl[] {},
                false,
                "Wave693 static read-back: formats the four-byte PNG chunk tag from decode-state +0x10c into the ECX/output buffer, copies printable bytes directly, expands non-printable bytes as bracketed uppercase hex nibbles through the observed hex literal, and appends optional message text when present. Signature intentionally left unchanged because Ghidra's thiscall shape exposes the output buffer as this and the stack/register roles remain better documented by comments than by forcing a new ABI. Static metadata only; exact output-buffer capacity, chunk-state layout, and runtime PNG diagnostic fidelity remain unproven.",
                commentOnlyTags("png", "chunk-tag", "diagnostic-format", "hex-escape", "stack-message")
            ),
            new Spec(
                "0x00592d29",
                "CTexture__SetDecodeContextTriplet",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("decode_context", voidPtr),
                    param("callback_context", voidPtr),
                    param("error_callback", voidPtr),
                    param("warning_callback", voidPtr)
                },
                true,
                "Wave693 static read-back: writes the observed decode-context callback triplet, storing callback_context at +0x48, error_callback at +0x40, and warning_callback at +0x44 before returning. Static metadata only; exact callback prototypes, decode-context structure, ownership lifetime, and runtime JPEG/PNG decode behavior remain unproven.",
                signatureTags("decode-context", "callback-triplet", "error-callback", "warning-callback")
            ),
            new Spec(
                "0x00592d45",
                "CDXTexture__ThrowDecodeError",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("decode_context", voidPtr),
                    param("message_or_code", intType)
                },
                true,
                "Wave693 static read-back: if the decode-context error callback at +0x40 is present, invokes it with the decode context and message/code payload, then transfers control through _longjmp(decode_context, 1). Static metadata only; exact error-callback prototype, payload type, non-return contract, and runtime decode behavior remain unproven.",
                signatureTags("decode-context", "error-callback", "longjmp", "decode-error")
            ),
            new Spec(
                "0x00592d63",
                "CDXTexture__ReportDecodeWarning",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("decode_context", voidPtr),
                    param("message_or_code", intType)
                },
                true,
                "Wave693 static read-back: if the decode-context warning callback at +0x44 is present, invokes it with the decode context and message/code payload, then returns without a longjmp transfer. Static metadata only; exact warning-callback prototype, payload type, warning policy, and runtime decode behavior remain unproven.",
                signatureTags("decode-context", "warning-callback", "decode-warning")
            ),
            new Spec(
                "0x00592d7a",
                "CDXTexture__LogChunkTagDiagnostic",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("png_decode_state", voidPtr),
                    param("optional_message_text", voidPtr)
                },
                true,
                "Wave693 static read-back: builds a stack diagnostic string through CDXTexture__FormatChunkTagForDiagnostics for the current PNG chunk tag and optional message text, then routes the formatted stack buffer through CDXTexture__ThrowDecodeError. Static metadata only; exact stack-buffer size, chunk-state layout, callback payload type, and runtime PNG error behavior remain unproven.",
                signatureTags("png", "chunk-tag", "diagnostic-format", "decode-error", "stack-message")
            ),
            new Spec(
                "0x00592d9e",
                "CDXTexture__WarnPngChunkWithFormattedTag",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("png_decode_state", voidPtr),
                    param("optional_message_text", voidPtr)
                },
                true,
                "Wave693 static read-back: builds a stack diagnostic string through CDXTexture__FormatChunkTagForDiagnostics for the current PNG chunk tag and optional message text, then routes the formatted stack buffer through CDXTexture__ReportDecodeWarning. Static metadata only; exact stack-buffer size, chunk-state layout, callback payload type, and runtime PNG warning behavior remain unproven.",
                signatureTags("png", "chunk-tag", "diagnostic-format", "decode-warning", "stack-message", "tranche-tail")
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

        println("ApplyCDXTextureParserContextDiagnosticsWave693 mode=" + (dryRun ? "dry" : "apply"));
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
