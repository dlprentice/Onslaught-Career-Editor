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

public class ApplyCrtFdLocaleItoaWave648 extends GhidraScript {
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
            "crt-fd-locale-itoa-wave648",
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
                println("SKIP: " + spec.address + " " + spec.name);
                return;
            }
            if (dryRun) {
                stats.skipped++;
                if (needsRename) {
                    stats.wouldRename++;
                }
                println("DRY: " + spec.address + " " + fn.getName() + " -> " + spec.name + " sig=" + expectedSignature(spec));
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
            println("OK: " + spec.address + " " + spec.name + " sig=" + expectedSignature(spec));
        } catch (Exception ex) {
            stats.bad++;
            println("BAD: " + spec.address + " " + spec.name + " " + ex.getMessage());
        }
    }

    private Spec[] buildSpecs() throws Exception {
        DataType charPtr = new PointerDataType(CharDataType.dataType);
        DataType voidPtr = new PointerDataType(VoidDataType.dataType);
        DataType intType = IntegerDataType.dataType;
        DataType uintType = UnsignedIntegerDataType.dataType;

        return new Spec[] {
            new Spec(
                "0x0056db76",
                "CRT__ChangeFileSizeByFd_NoLock",
                new String[] {},
                "__cdecl",
                intType,
                new ParameterImpl[] {
                    param("fdIndex", uintType),
                    param("targetSize", intType)
                },
                "Wave648 CRT fd/locale/itoa hardening: unbuffered file-size adjustment helper reached from CRT__OpenFd. It saves the current fd position, compares the target size to file end, truncates through SetEndOfFile when shrinking, extends by writing zero-filled chunks after forcing binary mode when growing, restores the original file position, and maps access-denied failures through CRT errno/doserrno state. Static CRT fd resize evidence only; exact MSVC CRT version, full fd-table and text/binary mode layouts, large-file behavior, runtime file I/O behavior, BEA patching, and rebuild parity remain unproven.",
                tags("crt-runtime", "fd-table", "file-size", "SetEndOfFile", "file-write")
            ),
            new Spec(
                "0x0056dc9b",
                "CRT__WriteWideCharToStream",
                new String[] {},
                "__cdecl",
                uintType,
                new ParameterImpl[] {
                    param("wideChar", uintType),
                    param("stream", voidPtr)
                },
                "Wave648 CRT fd/locale/itoa hardening: writes one wide character to a CRT stream, preparing write mode and buffers, handling standard stream commit-mode exceptions, flushing pending buffer bytes when needed, appending in text mode, and returning the written low 16 bits or 0xffff on failure. Static CRT wide-stream evidence only; exact MSVC CRT version, full FILE/fd-table layout, text-mode append semantics, runtime stream behavior, BEA patching, and rebuild parity remain unproven.",
                tags("crt-runtime", "wide-char", "stream", "fd-write", "FILE")
            ),
            new Spec(
                "0x0056ddc2",
                "CRT__GetLocaleInfoCopyOrInt",
                new String[] {"CRT__GetLocaleInfoCopyOrInt_0056ddc2"},
                "__cdecl",
                intType,
                new ParameterImpl[] {
                    param("valueKind", intType),
                    param("localeId", intType),
                    param("localeInfoType", intType),
                    param("outValue", voidPtr)
                },
                "Wave648 CRT fd/locale/itoa hardening: shared locale-info extractor used by date/time and monetary locale loaders. Mode zero fetches locale text as wide data and parses ASCII digit characters into the caller output; mode one fetches multibyte locale text, retries after ERROR_INSUFFICIENT_BUFFER with heap storage, then copies an allocated string pointer to the caller. Static CRT locale-info evidence only; exact MSVC CRT version, full locale table/lconv/LC_TIME layouts, Windows NLS edge cases, allocation lifetime, runtime locale behavior, BEA patching, and rebuild parity remain unproven.",
                tags("crt-runtime", "locale", "GetLocaleInfo", "NLS", "allocation")
            ),
            new Spec(
                "0x0056e0bf",
                "CRT__IntToAsciiBase",
                new String[] {"CRT__IntToAsciiBase_0056e0bf"},
                "__cdecl",
                charPtr,
                new ParameterImpl[] {
                    param("value", intType),
                    param("outBuffer", charPtr),
                    param("base", intType)
                },
                "Wave648 CRT fd/locale/itoa hardening: signed integer-to-ASCII wrapper that emits a minus sign only for negative base-10 inputs, delegates digit generation to CRT__UIntToAsciiBase, and returns the caller output buffer. Static CRT numeric formatting evidence only; exact MSVC CRT version, signed overflow behavior, supported base contract, caller buffer size, runtime formatting behavior, BEA patching, and rebuild parity remain unproven.",
                tags("crt-runtime", "itoa", "numeric-format", "string")
            ),
            new Spec(
                "0x0056e0ec",
                "CRT__UIntToAsciiBase",
                new String[] {},
                "__cdecl",
                VoidDataType.dataType,
                new ParameterImpl[] {
                    param("value", uintType),
                    param("outBuffer", charPtr),
                    param("base", uintType),
                    param("emitMinusSign", intType)
                },
                "Wave648 CRT fd/locale/itoa hardening: unsigned integer-to-ASCII core that optionally writes a leading minus sign, emits base-N digits in reverse using 0-9 and lowercase a-z style offsets, terminates the buffer, then reverses the digit span in place. Static CRT numeric formatting evidence only; exact MSVC CRT version, supported base contract, caller buffer size, runtime formatting behavior, BEA patching, and rebuild parity remain unproven.",
                tags("crt-runtime", "itoa", "numeric-format", "string")
            ),
            new Spec(
                "0x0056e148",
                "CRT__UIntToAsciiBase_ReturnBuffer",
                new String[] {},
                "__cdecl",
                charPtr,
                new ParameterImpl[] {
                    param("value", uintType),
                    param("outBuffer", charPtr),
                    param("base", uintType)
                },
                "Wave648 CRT fd/locale/itoa hardening: convenience wrapper around CRT__UIntToAsciiBase that formats an unsigned value without a minus sign and returns the caller output buffer. Static CRT numeric formatting evidence only; exact MSVC CRT version, supported base contract, caller buffer size, runtime formatting behavior, BEA patching, and rebuild parity remain unproven.",
                tags("crt-runtime", "itoa", "numeric-format", "string", "wrapper")
            ),
            new Spec(
                "0x0056e170",
                "CRT__StrNICmpWithLocaleLock",
                new String[] {"CMCBuggy__StrnICmpWithLocaleLock"},
                "__cdecl",
                intType,
                new ParameterImpl[] {
                    param("leftText", charPtr),
                    param("rightText", charPtr),
                    param("maxChars", uintType)
                },
                "Wave648 CRT fd/locale/itoa hardening: corrected stale CMCBuggy owner label to a generic CRT case-insensitive bounded string compare helper. The single-byte fast path folds ASCII A-Z locally; the locale-aware path guards the active locale/codepage state and compares CRT__ToLowerWithLocale outputs until a mismatch, NUL, or maxChars exhaustion. Static CRT string-compare evidence only; exact MSVC CRT version, full locale/codepage behavior, signed-char behavior, runtime comparison behavior, BEA patching, and rebuild parity remain unproven.",
                tags("crt-runtime", "string-compare", "case-insensitive", "locale", "name-corrected")
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

        Stats stats = new Stats();
        println("MODE: " + (dryRun ? "dry" : "apply"));
        for (Spec spec : buildSpecs()) {
            applySpec(spec, dryRun, stats);
        }
        println(
            "SUMMARY: updated=" + stats.updated +
            " skipped=" + stats.skipped +
            " renamed=" + stats.renamed +
            " would_rename=" + stats.wouldRename +
            " signature_updated=" + stats.signatureUpdated +
            " missing=" + stats.missing +
            " bad=" + stats.bad
        );

        if (!dryRun && stats.bad == 0 && stats.missing == 0) {
            println("REPORT: Save succeeded");
        }
    }
}
