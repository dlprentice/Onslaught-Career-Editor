//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.CharDataType;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.UnsignedShortDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.FunctionTag;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyCrtLocaleHeadWave633 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String[] previousNames;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] parameters;
        final boolean varArgs;
        final String comment;
        final String[] tags;

        Spec(
                String address,
                String name,
                String[] previousNames,
                String callingConvention,
                DataType returnType,
                ParameterImpl[] parameters,
                boolean varArgs,
                String comment,
                String[] tags) {
            this.address = address;
            this.name = name;
            this.previousNames = previousNames;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.parameters = parameters;
            this.varArgs = varArgs;
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
        int varArgs = 0;
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
            "crt-locale-head-wave633",
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
        if (spec.parameters.length == 0 && !spec.varArgs) {
            sb.append("void");
        }
        else {
            for (int i = 0; i < spec.parameters.length; i++) {
                if (i > 0) {
                    sb.append(", ");
                }
                sb.append(spec.parameters[i].getDataType().getDisplayName())
                  .append(" ")
                  .append(spec.parameters[i].getName());
            }
            if (spec.varArgs) {
                if (spec.parameters.length > 0) {
                    sb.append(", ");
                }
                sb.append("...");
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
        if (fn.hasVarArgs() != spec.varArgs) {
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
        if (readBack.hasVarArgs() != spec.varArgs) {
            throw new IllegalStateException("Read-back varArgs mismatch at " + spec.address);
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
                println("SKIP: " + spec.address + " " + fn.getSignature() + " varArgs=" + fn.hasVarArgs());
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
            fn.setVarArgs(spec.varArgs);
            stats.signatureUpdated++;
            fn.setComment(spec.comment);
            for (String tag : spec.tags) {
                fn.addTag(tag);
            }
            verifyReadBack(spec);
            if (spec.varArgs) {
                stats.varArgs++;
            }
            stats.updated++;
            println("OK: " + spec.address + " " + spec.name + " -> " + functionAtEntry(spec.address).getSignature().toString()
                + " varArgs=" + functionAtEntry(spec.address).hasVarArgs());
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

        DataType charPtr = new PointerDataType(CharDataType.dataType);
        DataType intPtr = new PointerDataType(IntegerDataType.dataType);
        DataType ushortPtr = new PointerDataType(UnsignedShortDataType.dataType);
        DataType voidPtr = new PointerDataType(VoidDataType.dataType);
        DataType voidType = VoidDataType.dataType;
        DataType intType = IntegerDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x0056586a",
                "CRT__SetLocale",
                new String[] {},
                "__cdecl",
                charPtr,
                new ParameterImpl[] {param("category", intType), param("localeName", charPtr)},
                false,
                "Wave633 CRT locale hardening: setlocale-style dispatcher for categories 0..5. It locks CRT route 0x13, handles LC_* composite strings, resolves category names through the adjacent locale metadata helper, updates individual categories through CRT__SetLocaleCategory, and returns the active/composite locale string or null on failure. Static retail evidence only; exact MSVC CRT version, full locale table layout, runtime locale behavior, and rebuild parity remain unproven.",
                tags("crt-runtime", "locale", "setlocale", "signature-hardened")
            ),
            new Spec(
                "0x00565ab0",
                "CRT__SetLocaleCategory",
                new String[] {},
                "__cdecl",
                charPtr,
                new ParameterImpl[] {param("category", intType), param("localeName", charPtr)},
                false,
                "Wave633 CRT locale hardening: per-category locale setter called by CRT__SetLocale. It resolves locale metadata, allocates/copies the resolved name, snapshots previous category/codepage fields, dispatches the category callback, and rolls back on callback failure. Static locale-table evidence only; exact category globals, callback contracts, runtime locale behavior, and rebuild parity remain unproven.",
                tags("crt-runtime", "locale", "setlocale", "signature-hardened")
            ),
            new Spec(
                "0x00565bcb",
                "CRT__BuildCompositeLocaleString",
                new String[] {},
                "__cdecl",
                charPtr,
                new ParameterImpl[] {},
                false,
                "Wave633 CRT locale hardening: builds the global LC_* composite locale string from per-category entries. It lazily allocates the composite buffer, appends category names and separators through CRT__StrCatVarArgs/CRT__StrCatAligned, detects whether all categories match, and frees the composite when a single shared locale string is enough. Static string/global evidence only; exact buffer ownership, locale table layout, and rebuild parity remain unproven.",
                tags("crt-runtime", "locale", "composite-locale", "signature-hardened")
            ),
            new Spec(
                "0x00565c84",
                "CRT__ResolveLocaleNameAndMetadata",
                new String[] {},
                "__cdecl",
                charPtr,
                new ParameterImpl[] {param("localeName", charPtr), param("outResolvedName", charPtr), param("outLocaleTriple", ushortPtr), param("outLocaleMetadata", intPtr)},
                false,
                "Wave633 CRT locale hardening: resolves an input locale string into the cached resolved locale name and optional metadata outputs. It handles the literal C locale, cached current-locale aliases, parsed language/country/codepage triples, and helper resolution before copying the resolved name and metadata to caller-owned outputs. Static decompile/xref evidence only; exact locale triple structure, Windows locale mapping, and runtime behavior remain unproven.",
                tags("crt-runtime", "locale", "locale-resolver", "signature-hardened")
            ),
            new Spec(
                "0x00565d9c",
                "CRT__StrCatVarArgs",
                new String[] {},
                "__cdecl",
                voidType,
                new ParameterImpl[] {param("dest", charPtr), param("partCount", intType)},
                true,
                "Wave633 CRT locale hardening: small varargs strcat helper used by the locale composite and locale triple composer paths. It treats partCount as the number of following char* fragments and appends each fragment into dest through CRT__StrCatAligned. Static stack/vararg evidence only; exact caller buffer capacities and rebuild parity remain unproven.",
                tags("crt-runtime", "locale", "string-builder", "varargs", "signature-hardened")
            ),
            new Spec(
                "0x00565dc1",
                "CRT__ParseLocaleSpecifierTriple",
                new String[] {},
                "__cdecl",
                intType,
                new ParameterImpl[] {param("outLocaleTriple", voidPtr), param("localeSpecifier", charPtr)},
                false,
                "Wave633 CRT locale hardening: parses a locale specifier into a 0x88-byte language/country/codepage-style triple buffer. It splits on dot/underscore/comma delimiters, bounds language and country fragments to 0x40 bytes, accepts dotted codepage-only input, and returns -1 for malformed triples. Static parser evidence only; exact triple field names, Windows locale equivalence, and rebuild parity remain unproven.",
                tags("crt-runtime", "locale", "locale-parser", "signature-hardened")
            ),
            new Spec(
                "0x00565e8d",
                "CRT__ComposeLocaleSpecifierFromTriple",
                new String[] {},
                "__cdecl",
                voidType,
                new ParameterImpl[] {param("outLocaleName", charPtr), param("localeTriple", voidPtr)},
                false,
                "Wave633 CRT locale hardening: composes a locale specifier string from the parsed triple buffer. It copies the base language/name fragment, appends country and codepage fragments when present through CRT__StrCatVarArgs, and is called by CRT__ResolveLocaleNameAndMetadata. Static string-builder evidence only; exact delimiter strings, field semantics, and rebuild parity remain unproven.",
                tags("crt-runtime", "locale", "locale-parser", "signature-hardened")
            ),
            new Spec(
                "0x00566104",
                "CRT__InvokeNewHandler",
                new String[] {"CRT__InvokeLocaleValidationCallback"},
                "__cdecl",
                intType,
                new ParameterImpl[] {param("requestedBytes", intType)},
                false,
                "Wave633 CRT allocation hardening: corrected from the stale locale-validation label to the allocation new-handler callback shim. It calls the global callback at DAT_009d09b8 with requestedBytes when installed and returns 1 only when the callback reports success. Current xrefs are malloc/calloc/realloc retry paths. Static allocation-helper evidence only; exact CRT new-handler API identity, callback ownership, runtime OOM behavior, and rebuild parity remain unproven.",
                tags("crt-runtime", "allocation", "new-handler", "name-corrected", "signature-hardened")
            ),
            new Spec(
                "0x0056611f",
                "CRT__ReadMainModulePeVersionBytes",
                new String[] {},
                "__cdecl",
                voidType,
                new ParameterImpl[] {param("outVersionBytes", voidPtr)},
                false,
                "Wave633 CRT heap-selector hardening: reads two version bytes from the current process main module's PE header into outVersionBytes after an MZ/header-offset check, zeroing the output first. The current caller is CRT__SelectHeapStrategy. Static PE-header evidence only; exact optional-header field identity, malformed-header behavior, and rebuild parity remain unproven.",
                tags("crt-runtime", "heap-selector", "pe-header", "signature-hardened")
            ),
            new Spec(
                "0x0056614c",
                "CRT__SelectHeapStrategy",
                new String[] {},
                "__cdecl",
                intType,
                new ParameterImpl[] {},
                false,
                "Wave633 CRT heap-selector hardening: chooses the CRT heap strategy from OS version, __MSVCRT_HEAP_SELECT, module filename matching, and the main-module PE version-byte helper. It returns strategy ids used by CRT__InitializeHeapSubsystem to select ordinary heap, small-block heap, or region-pool paths. Static heap-selection evidence only; exact MSVC CRT version, environment-string grammar, OS/runtime behavior, and rebuild parity remain unproven.",
                tags("crt-runtime", "heap-selector", "environment", "signature-hardened")
            )
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }
        println(
            "SUMMARY: updated=" + stats.updated
                + " skipped=" + stats.skipped
                + " renamed=" + stats.renamed
                + " would_rename=" + stats.wouldRename
                + " signature_updated=" + stats.signatureUpdated
                + " varargs=" + stats.varArgs
                + " missing=" + stats.missing
                + " bad=" + stats.bad
        );
    }
}
