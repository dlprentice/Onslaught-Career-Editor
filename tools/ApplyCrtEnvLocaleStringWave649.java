//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.CharDataType;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.UnsignedIntegerDataType;
import ghidra.program.model.data.UnsignedShortDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.FunctionTag;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyCrtEnvLocaleStringWave649 extends GhidraScript {
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
            "crt-env-locale-string-wave649",
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
                    spec.parameters);
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

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = true;
        if (args != null && args.length > 0) {
            dryRun = isDryRun(args[0]);
        }

        DataType intType = IntegerDataType.dataType;
        DataType uintType = UnsignedIntegerDataType.dataType;
        DataType charPtr = new PointerDataType(CharDataType.dataType);
        DataType charPtrPtr = new PointerDataType(charPtr);
        DataType ushortPtr = new PointerDataType(UnsignedShortDataType.dataType);

        Spec[] specs = new Spec[] {
            new Spec(
                "0x0056e271",
                "CRT__GetEnvVarValuePointerCaseInsensitive",
                new String[] { "CRT__GetEnvVarValuePointerCaseInsensitive_0056e271" },
                "__cdecl",
                charPtr,
                new ParameterImpl[] { param("variableName", charPtr) },
                "Wave649 CRT env/locale/string hardening: case-insensitive environment lookup helper reached from tzset. It ensures the multibyte environment table exists, scans NAME=value entries with __mbsnbicoll over the requested name length, requires an '=' after the matched name, and returns a pointer to the value text or null.",
                tags("crt-runtime", "environment", "case-insensitive", "string-compare", "name-corrected")
            ),
            new Spec(
                "0x0056e2ee",
                "CRT__SetFdTextBinaryModeFlag_NoLock",
                new String[] {},
                "__cdecl",
                intType,
                new ParameterImpl[] { param("fdIndex", uintType), param("modeFlag", intType) },
                "Wave649 CRT env/locale/string hardening: no-lock fd text/binary mode flag setter used by the Wave648 file-size helper. It toggles the observed fd-table text-mode bit for 0x8000/0x4000 requests, rejects other mode values with EINVAL, and returns the previous text/binary mode.",
                tags("crt-runtime", "fd-table", "text-mode", "binary-mode", "file-io")
            ),
            new Spec(
                "0x0056e34f",
                "CRT__GetLocaleInfoAsWide",
                new String[] {},
                "__cdecl",
                intType,
                new ParameterImpl[] {
                    param("localeId", uintType),
                    param("localeInfoType", intType),
                    param("outWideBuffer", ushortPtr),
                    param("outWideChars", intType),
                    param("codePage", uintType)
                },
                "Wave649 CRT env/locale/string hardening: locale-info wrapper that prefers GetLocaleInfoW when available, otherwise queries GetLocaleInfoA into stack scratch and converts the multibyte result to UTF-16-style output with MultiByteToWideChar using the requested or default CRT codepage.",
                tags("crt-runtime", "locale", "GetLocaleInfo", "wide-char", "NLS")
            ),
            new Spec(
                "0x0056e462",
                "CRT__GetLocaleInfoAsMultiByte",
                new String[] {},
                "__cdecl",
                intType,
                new ParameterImpl[] {
                    param("localeId", uintType),
                    param("localeInfoType", intType),
                    param("outBuffer", charPtr),
                    param("outChars", intType),
                    param("codePage", uintType)
                },
                "Wave649 CRT env/locale/string hardening: locale-info wrapper that prefers GetLocaleInfoA when available, otherwise queries GetLocaleInfoW into stack scratch and converts the wide result back to multibyte text with WideCharToMultiByte using the requested or default CRT codepage.",
                tags("crt-runtime", "locale", "GetLocaleInfo", "multibyte", "NLS")
            ),
            new Spec(
                "0x0056e5bf",
                "CRT__ProcessWideEnvTableToMultibyte",
                new String[] { "CRT__ProcessWideArgvTableToMultibyte" },
                "__cdecl",
                intType,
                new ParameterImpl[] {},
                "Wave649 CRT env/locale/string hardening: corrected stale Argv wording to environment-table behavior. It walks the CRT wide environment table, converts each wide NAME=value string to a multibyte allocation with WideCharToMultiByte, feeds the result through putenv table update, and returns -1 on allocation or conversion failure.",
                tags("crt-runtime", "environment", "wide-char", "multibyte", "name-corrected")
            ),
            new Spec(
                "0x0056e62d",
                "CRT__CompareLocaleStringsWithMBCSFallback",
                new String[] {},
                "__cdecl",
                intType,
                new ParameterImpl[] {
                    param("localeId", uintType),
                    param("compareFlags", uintType),
                    param("leftText", charPtr),
                    param("leftCount", intType),
                    param("rightText", charPtr),
                    param("rightCount", intType),
                    param("codePage", uintType)
                },
                "Wave649 CRT env/locale/string hardening: CompareString helper reached from __mbsnbicoll. It normalizes positive counts with CRT__StrNLen, uses CompareStringA when ANSI comparison is available, otherwise converts multibyte inputs to wide scratch buffers and compares with CompareStringW while preserving observed lead-byte edge handling.",
                tags("crt-runtime", "locale", "string-compare", "multibyte", "CompareString")
            ),
            new Spec(
                "0x0056e8aa",
                "CRT__StrNLen",
                new String[] {},
                "__cdecl",
                intType,
                new ParameterImpl[] { param("text", charPtr), param("maxChars", intType) },
                "Wave649 CRT env/locale/string hardening: bounded strlen helper that walks at most maxChars bytes and returns either the terminator distance or maxChars when no terminator is found.",
                tags("crt-runtime", "string", "bounded-length")
            ),
            new Spec(
                "0x0056e8d5",
                "CRT__PutEnvStringAndUpdateProcessEnv",
                new String[] {},
                "__cdecl",
                intType,
                new ParameterImpl[] { param("envAssignment", charPtr), param("updateProcessEnv", intType) },
                "Wave649 CRT env/locale/string hardening: putenv-style updater for the CRT environment table. It validates NAME=value text, clones the shared environment table when needed, inserts/replaces/removes entries by case-insensitive name match, and optionally mirrors the change through SetEnvironmentVariableA.",
                tags("crt-runtime", "environment", "putenv", "SetEnvironmentVariable", "allocation")
            ),
            new Spec(
                "0x0056ea5c",
                "CRT__FindEnvVarIndexOrInsertionPoint",
                new String[] {},
                "__cdecl",
                intType,
                new ParameterImpl[] { param("envAssignment", charPtr), param("nameLength", intType) },
                "Wave649 CRT env/locale/string hardening: scans the CRT environment pointer table for a case-insensitive name match of nameLength bytes and returns the matching index, or the negative insertion index when no matching NAME or NAME=value row exists.",
                tags("crt-runtime", "environment", "case-insensitive", "string-compare", "table-scan")
            ),
            new Spec(
                "0x0056eab4",
                "CRT__CloneEnvironmentTable",
                new String[] {},
                "__cdecl",
                charPtrPtr,
                new ParameterImpl[] { param("envTable", charPtrPtr) },
                "Wave649 CRT env/locale/string hardening: clones a null-terminated CRT environment pointer table by allocating a new pointer array, duplicating each NAME=value string with CRT__StrDup, preserving the final null slot, and routing allocation failure through __amsg_exit.",
                tags("crt-runtime", "environment", "allocation", "string-dup", "table-clone")
            ),
            new Spec(
                "0x0056eb1b",
                "CRT__StrDup",
                new String[] {},
                "__cdecl",
                charPtr,
                new ParameterImpl[] { param("sourceText", charPtr) },
                "Wave649 CRT env/locale/string hardening: strdup-style helper that allocates strlen(sourceText)+1 bytes, copies the source with CRT__StrCpyAligned, returns the duplicated string, and returns null for null input or allocation failure.",
                tags("crt-runtime", "string", "allocation", "string-dup")
            )
        };

        println("MODE: " + (dryRun ? "dry" : "apply"));
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
            throw new IllegalStateException("Wave649 CRT env/locale/string apply encountered missing/bad rows");
        }
    }
}
