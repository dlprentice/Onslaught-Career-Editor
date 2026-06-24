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
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyCrtLocaleStringTailWave645 extends GhidraScript {
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
            "crt-locale-string-tail-wave645",
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

    private Spec[] buildSpecs() throws Exception {
        DataType charPtr = new PointerDataType(CharDataType.dataType);
        DataType charPtrPtr = new PointerDataType(charPtr);
        DataType ushortPtr = new PointerDataType(UnsignedShortDataType.dataType);
        DataType voidPtr = new PointerDataType(VoidDataType.dataType);
        DataType intType = IntegerDataType.dataType;
        DataType uintType = UnsignedIntegerDataType.dataType;

        return new Spec[] {
            new Spec(
                "0x0056b368",
                "CRT__WriteWideCharToStreamWithConversion",
                new String[] {},
                "__cdecl",
                uintType,
                new ParameterImpl[] {
                    param("wideChar", uintType),
                    param("stream", voidPtr)
                },
                "Wave645: writes a wide character to a CRT stream, routing text-mode multibyte conversion through the active locale/codepage path and falling back to the wide stream writer for wide-oriented streams.",
                tags("crt-runtime", "wide-char-output", "stream", "locale-codepage")
            ),
            new Spec(
                "0x0056b4f2",
                "CRT__LoadTimeLocaleInfoTable",
                new String[] {"CRT__LoadLocaleInfoTable"},
                "__cdecl",
                uintType,
                new ParameterImpl[] {
                    param("timeLocaleInfo", voidPtr)
                },
                "Wave645: loads date/time locale strings and integer fields with repeated GetLocaleInfo-backed helper calls, returning the OR of the per-field failure flags.",
                tags("crt-runtime", "locale", "time-locale", "GetLocaleInfoA")
            ),
            new Spec(
                "0x0056bba5",
                "CRT__NormalizeLocaleGroupingStringInPlace",
                new String[] {"CFastVB__NormalizeDigitStringInPlace"},
                "__cdecl",
                VoidDataType.dataType,
                new ParameterImpl[] {
                    param("groupingText", charPtr)
                },
                "Wave645: normalizes a locale grouping string in place by converting ASCII digits to numeric byte values and removing semicolon separators.",
                tags("crt-runtime", "locale", "grouping-string", "stale-owner-corrected")
            ),
            new Spec(
                "0x0056bca7",
                "CRT__LoadMonetaryLocaleInfoTable",
                new String[] {"CFastVB__LoadConfigFieldsBlock"},
                "__cdecl",
                uintType,
                new ParameterImpl[] {
                    param("monetaryLocaleInfo", voidPtr)
                },
                "Wave645: loads monetary locale strings, byte-sized sign/pattern fields, and grouping metadata through GetLocaleInfo-backed helper calls before normalizing the grouping string.",
                tags("crt-runtime", "locale", "monetary-locale", "stale-owner-corrected")
            ),
            new Spec(
                "0x0056bdc9",
                "CRT__FreeLocaleBufferSet",
                new String[] {},
                "__cdecl",
                VoidDataType.dataType,
                new ParameterImpl[] {
                    param("localeBufferSet", voidPtr)
                },
                "Wave645: frees the heap-backed string slots in a locale buffer set unless the record is null or still points at the static default buffer.",
                tags("crt-runtime", "locale", "heap-free", "buffer-set")
            ),
            new Spec(
                "0x0056c060",
                "CRT__StrCSpn",
                new String[] {"CRT__StrCSpn_0056c060"},
                "__cdecl",
                intType,
                new ParameterImpl[] {
                    param("text", charPtr),
                    param("rejectSet", charPtr)
                },
                "Wave645: strcspn-style helper that builds a 256-bit reject-set bitmap and returns the first input index whose byte is present in that set.",
                tags("crt-runtime", "string", "strcspn", "bitmap-search")
            ),
            new Spec(
                "0x0056c0a0",
                "CRT__StrPBrk",
                new String[] {"CRT__StrPBrk_0056c0a0"},
                "__cdecl",
                charPtr,
                new ParameterImpl[] {
                    param("text", charPtr),
                    param("acceptSet", charPtr)
                },
                "Wave645: strpbrk-style helper that builds a 256-bit accept-set bitmap and returns the first matching input pointer or null.",
                tags("crt-runtime", "string", "strpbrk", "bitmap-search")
            ),
            new Spec(
                "0x0056c0da",
                "CRT__ResolveLocaleNameAndMetadata_NlsCore",
                new String[] {"CRT__ResolveLocaleNameAndMetadata_0056c0da"},
                "__cdecl",
                intType,
                new ParameterImpl[] {
                    param("localeTriple", charPtr),
                    param("outLocaleIds", ushortPtr),
                    param("outResolvedTriple", charPtr)
                },
                "Wave645: NLS-backed locale resolver core that remaps language/country aliases, enumerates matching locales, resolves the codepage token, validates locale/codepage IDs, and optionally writes resolved language/country/codepage text.",
                tags("crt-runtime", "locale", "NLS", "GetLocaleInfoA")
            ),
            new Spec(
                "0x0056c257",
                "CRT__LocaleAliasBinarySearchRemap",
                new String[] {"CRT__LocaleAliasBinarySearchRemap_0056c257"},
                "__cdecl",
                VoidDataType.dataType,
                new ParameterImpl[] {
                    param("aliasTable", voidPtr),
                    param("highIndex", intType),
                    param("nameSlot", charPtrPtr)
                },
                "Wave645: binary-searches a sorted locale alias table with stricmp and rewrites the caller's name slot to the canonical alias payload on match.",
                tags("crt-runtime", "locale", "alias-table", "binary-search")
            ),
            new Spec(
                "0x0056c336",
                "CRT__EnumLocalesCallback_MatchLanguageCountry",
                new String[] {"CRT__EnumLocalesCallback_MatchLanguageCountry_0056c336"},
                "__stdcall",
                intType,
                new ParameterImpl[] {
                    param("localeIdText", charPtr)
                },
                "Wave645: EnumLocales callback that parses a hex LCID string, compares country and language names through the selected GetLocaleInfoA path, and records the best match flags.",
                tags("crt-runtime", "locale", "EnumLocalesA", "language-country")
            ),
            new Spec(
                "0x0056c590",
                "CRT__EnumLocalesCallback_MatchLanguageOnly",
                new String[] {"CRT__EnumLocalesCallback_MatchLanguageOnly_0056c590"},
                "__stdcall",
                intType,
                new ParameterImpl[] {
                    param("localeIdText", charPtr)
                },
                "Wave645: EnumLocales callback for language-only locale resolution that parses a hex LCID string, compares language names, validates partial matches, and records the selected LCID.",
                tags("crt-runtime", "locale", "EnumLocalesA", "language-only")
            ),
            new Spec(
                "0x0056c684",
                "CRT__ValidateCodePageAgainstLocale",
                new String[] {},
                "__stdcall",
                intType,
                new ParameterImpl[] {
                    param("localeIdText", charPtr)
                },
                "Wave645: EnumLocales-style callback that parses a hex LCID string, compares the locale country name, validates the codepage against the locale map, and records a matching LCID.",
                tags("crt-runtime", "locale", "codepage", "EnumLocalesA")
            ),
            new Spec(
                "0x0056c724",
                "CRT__ResolveLocaleCodePageToken",
                new String[] {},
                "__cdecl",
                intType,
                new ParameterImpl[] {
                    param("codePageToken", charPtr)
                },
                "Wave645: resolves an empty/ACP/OCP/numeric locale codepage token, using GetLocaleInfoA for ACP/OCP strings and returning the decimal parser result in EAX.",
                tags("crt-runtime", "locale", "codepage", "ACP-OCP")
            ),
            new Spec(
                "0x0056c78a",
                "CRT__IsCodePageSupportedByLocaleMap",
                new String[] {},
                "__cdecl",
                intType,
                new ParameterImpl[] {
                    param("localeId", intType)
                },
                "Wave645: checks a small locale-id exclusion table and returns zero for excluded locale ids, one otherwise.",
                tags("crt-runtime", "locale", "codepage", "locale-map")
            ),
            new Spec(
                "0x0056c7a9",
                "CRT__ValidateLocaleLanguageMatch",
                new String[] {"CRT__ValidateLocaleLanguageMatch_0056c7a9"},
                "__cdecl",
                intType,
                new ParameterImpl[] {
                    param("localeId", intType),
                    param("requireExactLanguage", intType)
                },
                "Wave645: validates that a candidate LCID maps back to the requested language, rejecting prefix-only matches when the requested language text is all alphabetic.",
                tags("crt-runtime", "locale", "language-match", "LCID")
            ),
            new Spec(
                "0x0056c841",
                "CRT__GetLocaleInfoACompatFallback",
                new String[] {},
                "__stdcall",
                intType,
                new ParameterImpl[] {
                    param("localeId", uintType),
                    param("localeInfoType", intType),
                    param("outBuffer", charPtr),
                    param("outChars", intType)
                },
                "Wave645: compatibility GetLocaleInfoA wrapper that first serves selected locale fields from an internal sorted table, then falls back to kernel32 GetLocaleInfoA.",
                tags("crt-runtime", "locale", "GetLocaleInfoA", "compatibility-table")
            ),
            new Spec(
                "0x0056c927",
                "CRT__ParseHexLocaleIdString",
                new String[] {"CRT__ParseHexLocaleIdString_0056c927"},
                "__cdecl",
                intType,
                new ParameterImpl[] {
                    param("localeIdText", charPtr)
                },
                "Wave645: parses a NUL-terminated hexadecimal locale-id string used by EnumLocales callbacks, accepting uppercase and lowercase A-F digits.",
                tags("crt-runtime", "locale", "hex-parser", "LCID")
            ),
            new Spec(
                "0x0056c960",
                "CRT__CountAlphaPrefix",
                new String[] {"CRT__CountAlphaPrefix_0056c960"},
                "__cdecl",
                intType,
                new ParameterImpl[] {
                    param("text", charPtr)
                },
                "Wave645: counts the initial ASCII alphabetic prefix length of a locale language string.",
                tags("crt-runtime", "locale", "string", "alpha-prefix")
            ),
            new Spec(
                "0x0056c981",
                "CRT__StrToLong",
                new String[] {},
                "__cdecl",
                intType,
                new ParameterImpl[] {
                    param("text", charPtr),
                    param("endPtr", charPtrPtr),
                    param("base", intType)
                },
                "Wave645: strtol-style wrapper that forwards text, end pointer, base, and mode flag zero into the shared CRT string-to-long core.",
                tags("crt-runtime", "string-to-long", "strtol", "numeric-parser")
            ),
            new Spec(
                "0x0056cb9d",
                "CRT__StrToLongWithBaseAndLocaleCType_Mode1Thunk",
                new String[] {"CRT__StrToLongWithBaseAndLocaleCType_Thunk"},
                "__cdecl",
                intType,
                new ParameterImpl[] {
                    param("text", charPtr),
                    param("endPtr", charPtrPtr),
                    param("base", intType)
                },
                "Wave645: string-to-long wrapper that forwards text, end pointer, base, and mode flag one into the shared CRT locale-aware string-to-long core.",
                tags("crt-runtime", "string-to-long", "mode-flag", "numeric-parser")
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
