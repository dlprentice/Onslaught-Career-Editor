//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.CharDataType;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.UnsignedIntegerDataType;
import ghidra.program.model.data.UnsignedShortDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.FunctionTag;
import ghidra.program.model.listing.Parameter;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyDInputCrtTailWave740 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] parameters;
        final String comment;
        final String[] tags;

        Spec(String address, String name, String callingConvention, DataType returnType, ParameterImpl[] parameters,
                String comment, String[] tags) {
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

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "dinput-crt-tail-wave740",
            "wave740-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "signature-hardened",
            "dinput-crt-tail"
        };
        String[] result = new String[common.length + extras.length];
        System.arraycopy(common, 0, result, 0, common.length);
        System.arraycopy(extras, 0, result, common.length, extras.length);
        return result;
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
                println("MISSING: " + spec.address + " " + spec.name);
                stats.missing++;
                return;
            }
            if (!fn.getName().equals(spec.name)) {
                println("BADNAME: " + spec.address + " expected=" + spec.name + " actual=" + fn.getName());
                stats.bad++;
                return;
            }

            boolean signatureNeedsUpdate = !signatureMatches(fn, spec);
            boolean changed = needsUpdate(fn, spec);
            if (!changed) {
                println("SKIP: " + spec.address + " " + spec.name);
                stats.skipped++;
                return;
            }

            if (dryRun) {
                println("DRY: would update " + spec.address + " " + spec.name + " signature=" + expectedSignature(spec));
                if (signatureNeedsUpdate) {
                    stats.signatureUpdated++;
                } else {
                    stats.commentOnlyUpdated++;
                }
                stats.skipped++;
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
            println("OK: " + spec.address + " " + spec.name + " signature=" + expectedSignature(spec));
            if (signatureNeedsUpdate) {
                stats.signatureUpdated++;
            } else {
                stats.commentOnlyUpdated++;
            }
            stats.updated++;
        } catch (Exception ex) {
            println("FAIL: " + spec.address + " " + spec.name + " " + ex.getMessage());
            stats.bad++;
        }
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");
        DataType voidPtr = new PointerDataType(VoidDataType.dataType);
        DataType voidPtrPtr = new PointerDataType(voidPtr);
        DataType charPtr = new PointerDataType(CharDataType.dataType);
        DataType ushortPtr = new PointerDataType(UnsignedShortDataType.dataType);

        Spec[] specs = new Spec[] {
            new Spec(
                "0x005d04e0",
                "DirectInput8Create",
                "__stdcall",
                IntegerDataType.dataType,
                new ParameterImpl[] {
                    param("hinstance", voidPtr),
                    param("directinput_version", UnsignedIntegerDataType.dataType),
                    param("riid_directinput8", voidPtr),
                    param("directinput_out", voidPtrPtr),
                    param("outer_unknown", voidPtr)
                },
                "Wave740 static read-back: DINPUT8.DLL DirectInput8Create import thunk. Instruction export shows a six-byte JMP through IAT pointer 0x005d8020; PlatformInput__InitDirectInput callsite 0x00513178 pushes hinstance, version 0x800, IID pointer 0x0060c14c, interface output ESI, and null outer pointer, then checks returned EAX for failure. Static retail Ghidra metadata/instruction/xref evidence only; imported DirectInput runtime behavior, device enumeration behavior, BEA patching, and rebuild parity remain unproven.",
                tags("import-thunk", "directinput", "dinput8", "retail-import", "platform-input")
            ),
            new Spec(
                "0x005d04ec",
                "CFEPSaveGame__WideStrCaseInsensitiveCompare",
                "__cdecl",
                IntegerDataType.dataType,
                new ParameterImpl[] {
                    param("left_wide", ushortPtr),
                    param("right_wide", ushortPtr)
                },
                "Wave740 static read-back: frontend save-game wide-string case-insensitive compare helper. Xrefs from EnumerateSaveFiles_Main and CFEPSaveGame__CreateSave push two wide-string pointers; the body performs ASCII A-Z folding when locale globals are inactive and otherwise calls CFEPSaveGame__WideCharToLowerCompat for both strings before returning the character difference. Static retail Ghidra metadata/decompile/xref evidence only; exact locale model, save enumeration runtime behavior, BEA patching, and rebuild parity remain unproven.",
                tags("frontend-save", "wide-string", "case-insensitive-compare", "locale-compat")
            ),
            new Spec(
                "0x005d070f",
                "CRT__VsnprintfAndTerminate_005d070f",
                "__cdecl",
                IntegerDataType.dataType,
                new ParameterImpl[] {
                    param("out_buffer", charPtr),
                    param("out_buffer_size", IntegerDataType.dataType),
                    param("format", charPtr),
                    param("va_list_args", voidPtr)
                },
                "Wave740 static read-back: bounded CRT vsnprintf-style formatter. Texture and CFastVB diagnostic xrefs push output buffer, buffer size, format string, and va_list pointer; the body builds a local stream descriptor, calls CRT__FormatOutputToStream, then writes a terminating null or flushes a null byte when the remaining count is negative. Static retail Ghidra metadata/decompile/xref evidence only; exact CRT version, runtime diagnostic text behavior, BEA patching, and rebuild parity remain unproven.",
                tags("crt-format", "vsnprintf", "diagnostic-formatting", "texture-diagnostics")
            ),
            new Spec(
                "0x005d075f",
                "CRT__FormatToBufferAndTerminate",
                "__cdecl",
                IntegerDataType.dataType,
                new ParameterImpl[] {
                    param("out_buffer", charPtr),
                    param("out_buffer_size", IntegerDataType.dataType),
                    param("format", charPtr)
                },
                "Wave740 static read-back: bounded CRT sprintf-style formatter with caller varargs tail consumed from stack0x00000010. Texture diagnostic callsites push output buffer, size, and format before the variadic tail; the body builds a local stream descriptor, calls CRT__FormatOutputToStream, then writes a terminating null or flushes a null byte when the remaining count is negative. Static retail Ghidra metadata/decompile/xref evidence only; exact CRT version, runtime diagnostic text behavior, BEA patching, and rebuild parity remain unproven.",
                tags("crt-format", "sprintf", "hidden-varargs-tail", "texture-diagnostics")
            ),
            new Spec(
                "0x005d07f4",
                "CRT__FSeek_Locked",
                "__cdecl",
                IntegerDataType.dataType,
                new ParameterImpl[] {
                    param("stream", voidPtr),
                    param("offset", IntegerDataType.dataType),
                    param("origin", IntegerDataType.dataType)
                },
                "Wave740 static read-back: locked CRT fseek wrapper. Xref-site instruction evidence shows callers pushing stream, offset, and origin; the body locks by stream address, calls CRT__FSeek_UnlockedCore with the same three arguments, unlocks by stream address, and returns the core status. Static retail Ghidra metadata/decompile/xref evidence only; exact CRT FILE layout, runtime file positioning behavior, BEA patching, and rebuild parity remain unproven.",
                tags("crt-stdio", "fseek", "locked-wrapper", "file-positioning")
            ),
            new Spec(
                "0x005d0820",
                "CRT__FSeek_UnlockedCore",
                "__cdecl",
                IntegerDataType.dataType,
                new ParameterImpl[] {
                    param("stream", voidPtr),
                    param("offset", IntegerDataType.dataType),
                    param("origin", IntegerDataType.dataType)
                },
                "Wave740 static read-back: unlocked CRT fseek core. The body validates stream flags and origin 0/1/2, writes errno 0x16 on invalid input, converts origin 1 through CRT__FTellAdjusted, flushes write state, updates stream flags, calls CRT__LseekFd on stream+0x10, and returns 0 or -1. Static retail Ghidra metadata/decompile/xref evidence only; exact CRT FILE layout, runtime file positioning behavior, BEA patching, and rebuild parity remain unproven.",
                tags("crt-stdio", "fseek", "unlocked-core", "errno-0x16")
            ),
            new Spec(
                "0x005d09e4",
                "CRT__IncrementDotSuffixCounter",
                "__cdecl",
                IntegerDataType.dataType,
                new ParameterImpl[] {
                    param("path_buffer", charPtr)
                },
                "Wave740 static read-back: CRT temp-file suffix increment helper. Xrefs from CRT__TmpFile_OpenUniqueBinaryStream call it after candidate-name failures; the body finds the last dot, parses the suffix as base 0x20, increments it when below 0x7fff, writes the updated ASCII suffix back into the same buffer, and returns 0 or -1. Static retail Ghidra metadata/decompile/xref evidence only; exact CRT temp-file policy, runtime filesystem behavior, BEA patching, and rebuild parity remain unproven.",
                tags("crt-tempfile", "suffix-counter", "base-32", "path-buffer")
            ),
            new Spec(
                "0x005d0a2a",
                "CFEPSaveGame__WideCharToLowerCompat",
                "__cdecl",
                UnsignedIntegerDataType.dataType,
                new ParameterImpl[] {
                    param("wide_char", UnsignedIntegerDataType.dataType)
                },
                "Wave740 static read-back: frontend save-game wide-character lowercase compatibility helper. It preserves 0xffff, folds ASCII A-Z to lowercase when locale globals are inactive, and otherwise checks character type through CRT__GetCharTypeMaskCompat before calling CRT__LCMapStringW_AnsiCompat. Static retail Ghidra metadata/decompile/xref evidence only; exact locale model, save-name runtime behavior, BEA patching, and rebuild parity remain unproven.",
                tags("frontend-save", "wide-char", "tolower-compat", "locale-compat")
            ),
            new Spec(
                "0x005d0e88",
                "CRT__WcsNLen",
                "__cdecl",
                IntegerDataType.dataType,
                new ParameterImpl[] {
                    param("wide_string", ushortPtr),
                    param("max_chars", IntegerDataType.dataType)
                },
                "Wave740 static read-back: CRT bounded wide-string length helper. Xref from CRT__LCMapStringW_AnsiCompat pushes a wide string and maximum count; the body walks 16-bit characters until null or max count and returns either the measured character count or max_chars. Static retail Ghidra metadata/decompile/xref evidence only; exact CRT version, locale conversion runtime behavior, BEA patching, and rebuild parity remain unproven.",
                tags("crt-wide-string", "wcsnlen", "locale-compat", "bounded-length")
            ),
            new Spec(
                "0x005d0eb8",
                "CRT__GetCharTypeMaskCompat",
                "__cdecl",
                UnsignedIntegerDataType.dataType,
                new ParameterImpl[] {
                    param("wide_char", UnsignedIntegerDataType.dataType),
                    param("mask", UnsignedIntegerDataType.dataType)
                },
                "Wave740 static read-back: CRT character-type mask compatibility helper. CFEPSaveGame__WideCharToLowerCompat calls it with mask 1 for sub-0x100 characters; the body returns 0 for 0xffff, uses the byte-range type table at PTR_DAT_00653894 when possible, falls back to CRT__GetStringTypeWideOrAnsiCompat_0056defa, and returns the requested mask bits. Static retail Ghidra metadata/decompile/xref evidence only; exact CRT locale table identity, runtime locale behavior, BEA patching, and rebuild parity remain unproven.",
                tags("crt-wide-string", "char-type-mask", "locale-compat", "ctype-table")
            )
        };

        println("ApplyDInputCrtTailWave740 mode=" + (dryRun ? "dry" : "apply"));
        Stats stats = new Stats();
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }
        println("SUMMARY: updated=" + stats.updated
            + " skipped=" + stats.skipped
            + " renamed=0 would_rename=0"
            + " signature_updated=" + stats.signatureUpdated
            + " comment_only_updated=" + stats.commentOnlyUpdated
            + " missing=" + stats.missing
            + " bad=" + stats.bad);

        if (stats.missing > 0 || stats.bad > 0) {
            throw new IllegalStateException("Wave740 failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
