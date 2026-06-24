//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.CharDataType;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.UnsignedIntegerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.FunctionTag;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyCrtBufferCodepageCtypeWave643 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String[] previousNames;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] parameters;
        final String comment;
        final String[] tags;

        Spec(
                String address,
                String name,
                String[] previousNames,
                String callingConvention,
                DataType returnType,
                ParameterImpl[] parameters,
                String comment,
                String[] tags) {
            this.address = address;
            this.name = name;
            this.previousNames = previousNames;
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

    private boolean nameAllowed(String currentName, Spec spec) {
        if (currentName.equals(spec.name)) {
            return true;
        }
        for (String previousName : spec.previousNames) {
            if (currentName.equals(previousName)) {
                return true;
            }
        }
        return false;
    }

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "crt-buffer-codepage-ctype-wave643",
            "retail-binary-evidence",
            "comment-hardened",
            "signature-hardened"
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

    private boolean hasAllTags(Function fn, String[] tags) {
        Set<String> existing = tagNames(fn);
        for (String tag : tags) {
            if (!existing.contains(tag)) {
                return false;
            }
        }
        return true;
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
        } else {
            for (int i = 0; i < spec.parameters.length; i++) {
                if (i > 0) {
                    sb.append(", ");
                }
                sb.append(spec.parameters[i].getDataType().getDisplayName())
                  .append(" ")
                  .append(spec.parameters[i].getName());
            }
        }
        sb.append(")");
        return sb.toString();
    }

    private boolean needsUpdate(Function fn, Spec spec) {
        if (!fn.getName().equals(spec.name)) {
            return true;
        }
        if (!fn.getSignature().toString().equals(expectedSignature(spec))) {
            return true;
        }
        String existingComment = fn.getComment();
        if (existingComment == null || !existingComment.equals(spec.comment)) {
            return true;
        }
        return !hasAllTags(fn, spec.tags);
    }

    private void verifyReadBack(Spec spec) throws Exception {
        Function readBack = functionAtEntry(spec.address);
        if (readBack == null) {
            throw new IllegalStateException("Read-back missing at " + spec.address);
        }
        if (!readBack.getName().equals(spec.name)) {
            throw new IllegalStateException("Read-back name mismatch at " + spec.address + ": " + readBack.getName());
        }
        String actualSignature = readBack.getSignature().toString();
        String expectedSignature = expectedSignature(spec);
        if (!actualSignature.equals(expectedSignature)) {
            throw new IllegalStateException("Read-back signature mismatch at " + spec.address + ": " + actualSignature + " != " + expectedSignature);
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
            if (!nameAllowed(fn.getName(), spec)) {
                stats.bad++;
                println("BADNAME: " + spec.address + " actual=" + fn.getName() + " expected=" + spec.name);
                return;
            }
            boolean needsRename = !fn.getName().equals(spec.name);
            if (!needsUpdate(fn, spec)) {
                stats.skipped++;
                println("SKIP: " + spec.address + " " + fn.getSignature());
                return;
            }
            if (dryRun) {
                stats.skipped++;
                if (needsRename) {
                    stats.wouldRename++;
                }
                println("DRY: " + spec.address + " " + fn.getName() + " -> " + expectedSignature(spec));
                return;
            }

            if (needsRename) {
                fn.setName(spec.name, SourceType.USER_DEFINED);
                stats.renamed++;
            }
            fn.setCallingConvention(spec.callingConvention);
            fn.setReturnType(spec.returnType, SourceType.USER_DEFINED);
            fn.replaceParameters(
                FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS,
                true,
                SourceType.USER_DEFINED,
                spec.parameters
            );
            stats.signatureUpdated++;
            fn.setComment(spec.comment);
            for (String tag : spec.tags) {
                fn.addTag(tag);
            }
            verifyReadBack(spec);
            stats.updated++;
            println("OK: " + spec.address + " " + spec.name + " -> " + functionAtEntry(spec.address).getSignature().toString());
            Thread.sleep(50);
        } catch (Exception ex) {
            stats.bad++;
            println("BAD: " + spec.address + " " + spec.name + " " + ex.getMessage());
        }
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");

        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);
        DataType charPtr = new PointerDataType(CharDataType.dataType);
        DataType intType = IntegerDataType.dataType;
        DataType uintType = UnsignedIntegerDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x00569d91",
                "CRT__InitFileBuffer",
                new String[] {},
                "__cdecl",
                voidType,
                new ParameterImpl[] {param("stream", voidPtr)},
                "Wave643 CRT buffer/codepage/ctype hardening: initializes a CRT stream buffer, increments the global allocation counter, attempts a 0x1000-byte heap buffer, falls back to the stream inline buffer on allocation failure, and resets cursor/count fields. Static CRT I/O evidence only; exact MSVC CRT version, full FILE layout, locale globals, runtime stream side effects, BEA patching, and rebuild parity remain unproven.",
                tags("crt-runtime", "stream-buffer", "stdio", "allocation")
            ),
            new Spec(
                "0x00569dd5",
                "CRT__IsFdCommitMode",
                new String[] {},
                "__cdecl",
                intType,
                new ParameterImpl[] {param("fdIndex", uintType)},
                "Wave643 CRT buffer/codepage/ctype hardening: bounds-checks the file-descriptor table index and returns the per-descriptor 0x40 commit/text flag used by flush/write helpers before buffer or wide-character stream work. Static CRT I/O evidence only; exact MSVC CRT version, full fd-table layout, locale globals, runtime stream side effects, BEA patching, and rebuild parity remain unproven.",
                tags("crt-runtime", "fd-table", "stdio", "commit-mode")
            ),
            new Spec(
                "0x00569dfe",
                "CRT__WideCharToCurrentCodePage_WithLocaleGuard",
                new String[] {},
                "__cdecl",
                intType,
                new ParameterImpl[] {param("outBytes", charPtr), param("wideChar", intType)},
                "Wave643 CRT buffer/codepage/ctype hardening: locale-guard wrapper around CRT__WideCharToCurrentCodePage that increments the locale refcount, takes lock 0x13 when the locale is mutable, delegates conversion, and releases the matching guard. Static CRT codepage evidence only; exact MSVC CRT version, locale/global layout, Windows API parity, runtime conversion side effects, BEA patching, and rebuild parity remain unproven.",
                tags("crt-runtime", "codepage", "wide-char", "locale-guard")
            ),
            new Spec(
                "0x00569e57",
                "CRT__WideCharToCurrentCodePage",
                new String[] {},
                "__cdecl",
                intType,
                new ParameterImpl[] {param("outBytes", charPtr), param("wideChar", intType)},
                "Wave643 CRT buffer/codepage/ctype hardening: converts one wide character into the active multibyte codepage, using a direct byte store for single-byte locale mode or WideCharToMultiByte for active MBCS codepages, and sets errno 0x2a on failure. Static CRT codepage evidence only; exact MSVC CRT version, locale/global layout, Windows API parity, runtime conversion side effects, BEA patching, and rebuild parity remain unproven.",
                tags("crt-runtime", "codepage", "wide-char", "errno")
            ),
            new Spec(
                "0x00569f35",
                "CRT__MultiByteToWideChar_ThreadSafe",
                new String[] {},
                "__cdecl",
                intType,
                new ParameterImpl[] {param("outWideChar", voidPtr), param("inputBytes", charPtr), param("inputByteCount", uintType)},
                "Wave643 CRT buffer/codepage/ctype hardening: locale-guard wrapper around CRT__MultiByteToWideChar_SingleToken that increments the locale refcount, takes lock 0x13 when required, converts one multibyte token, and releases the matching guard. Static CRT codepage evidence only; exact MSVC CRT version, locale/global layout, Windows API parity, runtime conversion side effects, BEA patching, and rebuild parity remain unproven.",
                tags("crt-runtime", "codepage", "multibyte", "wide-char", "locale-guard")
            ),
            new Spec(
                "0x00569f92",
                "CRT__MultiByteToWideChar_SingleToken",
                new String[] {},
                "__cdecl",
                uintType,
                new ParameterImpl[] {param("outWideChar", voidPtr), param("inputBytes", charPtr), param("inputByteCount", uintType)},
                "Wave643 CRT buffer/codepage/ctype hardening: converts a single multibyte input token to a wide character, handling null input, single-byte locales, MBCS lead-byte checks, MultiByteToWideChar calls, lead-byte length validation, and errno 0x2a on conversion failure. Static CRT codepage evidence only; exact MSVC CRT version, locale/global layout, Windows API parity, runtime conversion side effects, BEA patching, and rebuild parity remain unproven.",
                tags("crt-runtime", "codepage", "multibyte", "wide-char", "errno")
            ),
            new Spec(
                "0x0056a05b",
                "CRT__IsAlpha",
                new String[] {"CRT__IsAlpha_0056a05b"},
                "__cdecl",
                uintType,
                new ParameterImpl[] {param("charValue", intType)},
                "Wave643 CRT buffer/codepage/ctype hardening: one-argument ctype helper for alpha classification using mask 0x103, delegating to CRT__GetCharTypeMask_Compat when the active codepage is multibyte and otherwise reading the static ctype table. Static CRT ctype evidence only; exact MSVC CRT version, locale table layout, signed-char/EOF behavior, runtime conversion side effects, BEA patching, and rebuild parity remain unproven.",
                tags("crt-runtime", "ctype", "alpha", "codepage")
            ),
            new Spec(
                "0x0056a089",
                "CRT__IsDigit",
                new String[] {"CRT__IsDigit_0056a089"},
                "__cdecl",
                uintType,
                new ParameterImpl[] {param("charValue", intType)},
                "Wave643 CRT buffer/codepage/ctype hardening: one-argument ctype helper for digit classification using mask 0x04, delegating to CRT__GetCharTypeMask_Compat when the active codepage is multibyte and otherwise reading the static ctype table. Static CRT ctype evidence only; exact MSVC CRT version, locale table layout, signed-char/EOF behavior, runtime conversion side effects, BEA patching, and rebuild parity remain unproven.",
                tags("crt-runtime", "ctype", "digit", "codepage")
            ),
            new Spec(
                "0x0056a0b1",
                "CRT__IsCharTypeMask0x80",
                new String[] {},
                "__cdecl",
                uintType,
                new ParameterImpl[] {param("charValue", intType)},
                "Wave643 CRT buffer/codepage/ctype hardening: one-argument ctype helper for mask 0x80, delegating to CRT__GetCharTypeMask_Compat when the active codepage is multibyte and otherwise reading the static ctype table. Static CRT ctype evidence only; exact MSVC CRT version, locale table layout, signed-char/EOF behavior, runtime conversion side effects, BEA patching, and rebuild parity remain unproven.",
                tags("crt-runtime", "ctype", "mask-0x80", "codepage")
            ),
            new Spec(
                "0x0056a0de",
                "CRT__IsCharTypeMask0x08",
                new String[] {},
                "__cdecl",
                uintType,
                new ParameterImpl[] {param("charValue", intType)},
                "Wave643 CRT buffer/codepage/ctype hardening: one-argument ctype helper for whitespace/control-style mask 0x08, delegating to CRT__GetCharTypeMask_Compat when the active codepage is multibyte and otherwise reading the static ctype table. Static CRT ctype evidence only; exact MSVC CRT version, locale table layout, signed-char/EOF behavior, runtime conversion side effects, BEA patching, and rebuild parity remain unproven.",
                tags("crt-runtime", "ctype", "mask-0x08", "codepage")
            ),
            new Spec(
                "0x0056a106",
                "CRT__GetCharClassMask",
                new String[] {},
                "__cdecl",
                uintType,
                new ParameterImpl[] {param("charValue", intType)},
                "Wave643 CRT buffer/codepage/ctype hardening: one-argument helper returning the combined 0x107 ctype class mask, delegating to CRT__GetCharTypeMask_Compat when the active codepage is multibyte and otherwise reading the static ctype table. Static CRT ctype evidence only; exact MSVC CRT version, locale table layout, signed-char/EOF behavior, runtime conversion side effects, BEA patching, and rebuild parity remain unproven.",
                tags("crt-runtime", "ctype", "mask-0x107", "codepage")
            ),
            new Spec(
                "0x0056a15f",
                "CRT__UngetCharToStream",
                new String[] {},
                "__cdecl",
                uintType,
                new ParameterImpl[] {param("character", uintType), param("stream", voidPtr)},
                "Wave643 CRT buffer/codepage/ctype hardening: ungetc-style stream pushback helper that rejects EOF and invalid stream modes, initializes the stream buffer if absent, handles commit/text-mode byte agreement, stores the pushed byte, increments the buffered count, and restores read-state flags. Static CRT I/O evidence only; exact MSVC CRT version, full FILE layout, text/binary pushback semantics, runtime stream side effects, BEA patching, and rebuild parity remain unproven.",
                tags("crt-runtime", "stdio", "stream-buffer", "ungetc")
            )
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }
        println("SUMMARY: updated=" + stats.updated
            + " skipped=" + stats.skipped
            + " renamed=" + stats.renamed
            + " would_rename=" + stats.wouldRename
            + " signature_updated=" + stats.signatureUpdated
            + " missing=" + stats.missing
            + " bad=" + stats.bad);
        if (stats.missing != 0 || stats.bad != 0) {
            throw new IllegalStateException("Wave643 had missing/bad rows");
        }
    }
}
