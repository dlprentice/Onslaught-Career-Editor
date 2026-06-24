//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.CharDataType;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.DoubleDataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.ShortDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.FunctionTag;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyCrtCliStringWave622 extends GhidraScript {
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
            "crt-cli-string-wave622",
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
        DataType shortPtr = new PointerDataType(ShortDataType.dataType);
        DataType intType = IntegerDataType.dataType;
        DataType doubleType = DoubleDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x0055e14f",
                "CRT__SscanfFromString",
                new String[] {"CLIParams__ScanFormatFromString"},
                "__cdecl",
                intType,
                new ParameterImpl[] {param("input", charPtr), param("format", charPtr)},
                true,
                "Wave622 CRT/CLI string hardening: string input scan wrapper builds a local input descriptor from input, records strlen(input), then calls CRT__InputFormatCore with the format pointer and varargs. Xrefs include CLIParams__ParseCommandLine, CTokenArchive__ReadNextToken, CD3DApplication card-id parsing, CConsole setters, and con_map. Static parser-helper evidence only; exact CRT version, complete format semantics, runtime command-line behavior, and rebuild parity remain unproven.",
                tags("crt-runtime", "string-scan", "varargs", "name-corrected", "cli-parser-xrefs")
            ),
            new Spec(
                "0x0055e183",
                "CRT__PrintfStdoutLocked",
                new String[] {"CFastVB__DispatchLockedRoute_6533e0"},
                "__cdecl",
                intType,
                new ParameterImpl[] {param("format", charPtr)},
                true,
                "Wave622 CRT/CLI string hardening: stdout-style formatted output wrapper locks route index 1 for stream key 0x6533e0, ensures the DAT_006533e0 stream buffer, formats through CRT__FormatOutputToStream, flushes pending writes, and unlocks. Xrefs span CLIParams, CGame pause, CWorldPhysicsManager, and CFastVB strip-building diagnostics. Static CRT output-helper evidence only; exact CRT identity, console visibility, runtime output behavior, and rebuild parity remain unproven.",
                tags("crt-runtime", "formatted-output", "stdout-stream", "varargs", "name-corrected")
            ),
            new Spec(
                "0x0055e1c4",
                "CRT__ParseDoubleSkippingWhitespace",
                new String[] {"CConsole__ParseFloatSkippingWhitespace"},
                "__cdecl",
                doubleType,
                new ParameterImpl[] {param("text", charPtr)},
                false,
                "Wave622 CRT/CLI string hardening: skips leading whitespace using the active ctype table or CRT__GetCharTypeMask_Compat, then parses a floating literal through CRT__ParseFloatTextToFloatAndStatus and returns the double result. Xrefs include CConsole__SetVariableByName and CTexture__ParseFloatingLiteral. Static parser-helper evidence only; exact CRT identity, locale edge cases, runtime console parsing behavior, and rebuild parity remain unproven.",
                tags("crt-runtime", "float-parser", "ctype-table", "name-corrected")
            ),
            new Spec(
                "0x0055e21b",
                "CRT__ParseDecimalIntA",
                new String[] {},
                "__cdecl",
                intType,
                new ParameterImpl[] {param("text", charPtr)},
                false,
                "Wave622 CRT/CLI string hardening: skips leading whitespace, accepts optional plus/minus, accumulates ASCII decimal digits with active ctype digit checks, and returns the signed int result. Xrefs include CRT__ParseDecimalIntA_Thunk, CRT locale codepage parsing, and CRT__Tzset. Static parser-helper evidence only; overflow behavior, exact CRT identity, locale edge cases, and rebuild parity remain unproven.",
                tags("crt-runtime", "decimal-parser", "ctype-table")
            ),
            new Spec(
                "0x0055e2a6",
                "CRT__ParseDecimalIntA_Thunk",
                new String[] {"CSoundManager__ParseDecimalToken"},
                "__cdecl",
                intType,
                new ParameterImpl[] {param("text", charPtr)},
                false,
                "Wave622 CRT/CLI string hardening: tail wrapper over CRT__ParseDecimalIntA; the old CSoundManager owner label was too narrow because xrefs span mesh suffix parsing, SFX files, texture/shader token parsing, mech setup, console mapping, and CDXTexture chunk processing. Static parser-helper evidence only; exact CRT identity, caller-specific token semantics, runtime parsing behavior, and rebuild parity remain unproven.",
                tags("crt-runtime", "decimal-parser", "thunk", "name-corrected")
            ),
            new Spec(
                "0x0055e598",
                "ControlsUI__FormatWideStringSafe",
                new String[] {},
                "__cdecl",
                intType,
                new ParameterImpl[] {param("outWide", shortPtr), param("format", shortPtr)},
                true,
                "Wave622 CRT/CLI string hardening: wide formatted-output wrapper seeds a wide-output descriptor, calls ControlsUI__FormatWideStringCore with format and varargs, then writes a double NUL terminator through the local output cursor. Known named xref is ControlsUI__RenderBindingsList. Static wide-format helper evidence only; exact CRT identity, buffer bounds beyond observed sentinel fields, runtime UI text behavior, and rebuild parity remain unproven.",
                tags("crt-runtime", "wide-format", "controls-ui", "varargs")
            ),
            new Spec(
                "0x0055e624",
                "CRT__WStrCat",
                new String[] {"ControlsUI__WideStrCat"},
                "__cdecl",
                intType,
                new ParameterImpl[] {param("destWide", shortPtr), param("srcWide", shortPtr)},
                false,
                "Wave622 CRT/CLI string hardening: scans destWide to its terminating 16-bit zero, then copies srcWide 16-bit units including the terminator. The old ControlsUI owner label was too narrow because xrefs span save/load frontend flows, virtual keyboard, menu text, FE options, and ControlsUI. Static wide-string helper evidence only; exact CRT identity, buffer safety, runtime UI text behavior, and rebuild parity remain unproven.",
                tags("crt-runtime", "wide-string", "name-corrected")
            ),
            new Spec(
                "0x0055e64e",
                "CRT__WStrCpy",
                new String[] {},
                "__cdecl",
                intType,
                new ParameterImpl[] {param("destWide", shortPtr), param("srcWide", shortPtr)},
                false,
                "Wave622 CRT/CLI string hardening: copies 16-bit units from srcWide to destWide including the terminating zero. Xrefs span game-interface rendering, localized frontend text, save/load directory flows, message wrapping, menu text, IScript sound, and controls UI. Static wide-string helper evidence only; exact CRT identity, buffer safety, runtime UI text behavior, and rebuild parity remain unproven.",
                tags("crt-runtime", "wide-string")
            ),
            new Spec(
                "0x0055e673",
                "CRT__ToUpperWithLocaleLock",
                new String[] {},
                "__cdecl",
                intType,
                new ParameterImpl[] {param("charValue", intType)},
                false,
                "Wave622 CRT/CLI string hardening: ASCII fast path uppercases a-z when locale state is inactive; otherwise it increments the locale lock counter, conditionally acquires CRT lock index 0x13, calls CRT__ToUpperWithLocale, then releases the lock/counter path. Xrefs include CRT__StrToLongWithBaseAndLocaleCType and texture semantic parsing. Static locale helper evidence only; exact CRT identity, full locale behavior, runtime parsing behavior, and rebuild parity remain unproven.",
                tags("crt-runtime", "locale", "ctype-table")
            ),
            new Spec(
                "0x0055e6e2",
                "CRT__ToUpperWithLocale",
                new String[] {},
                "__cdecl",
                intType,
                new ParameterImpl[] {param("charValue", intType)},
                false,
                "Wave622 CRT/CLI string hardening: ASCII fast path uppercases a-z when locale state is inactive; otherwise checks ctype uppercase state and routes through LCMapStringA-compatible conversion for single-byte or multibyte inputs. Direct caller is CRT__ToUpperWithLocaleLock. Static locale helper evidence only; exact CRT identity, full locale/codepage behavior, runtime parsing behavior, and rebuild parity remain unproven.",
                tags("crt-runtime", "locale", "ctype-table")
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
                + " varargs=" + stats.varArgs
                + " missing=" + stats.missing
                + " bad=" + stats.bad
        );
    }
}
