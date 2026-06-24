//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.BooleanDataType;
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

public class ApplyCrtCommandlineRuntimeWave638 extends GhidraScript {
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
            "crt-commandline-runtime-wave638",
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

        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);
        DataType charType = CharDataType.dataType;
        DataType charPtr = new PointerDataType(charType);
        DataType charPtrPtr = new PointerDataType(charPtr);
        DataType intType = IntegerDataType.dataType;
        DataType intPtr = new PointerDataType(intType);
        DataType uintType = UnsignedIntegerDataType.dataType;
        DataType boolType = BooleanDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x00568dc6",
                "CRT__ParseCommandLineToken",
                new String[] {},
                "__cdecl",
                charPtr,
                new ParameterImpl[] {},
                false,
                "Wave638 CRT command-line/runtime hardening: command-line cursor helper reached from entry before argv/environment setup. It walks global command-line cursor DAT_009d35f4, honors quoted program-name text, skips multibyte lead-byte payloads through the active ctype table, skips trailing whitespace, and returns the next argument cursor. Static CRT command-line evidence only; exact MSVC CRT version, multibyte command-line equivalence, global startup-state layout, runtime process-start behavior, BEA patching, and rebuild parity remain unproven.",
                tags("crt-runtime", "command-line", "startup")
            ),
            new Spec(
                "0x00568e1e",
                "CRT__BuildEnvironTable",
                new String[] {},
                "__cdecl",
                voidType,
                new ParameterImpl[] {},
                false,
                "Wave638 CRT command-line/runtime hardening: process-start environment table builder reached from entry. It counts non-hidden entries in the duplicated environment block at DAT_009d090c, allocates a char** table, copies each non '=' entry with CRT__StrCpyAligned, frees the raw block, null-terminates the table, and marks environment setup complete. Static CRT environment evidence only; exact environment-table layout, hidden-entry policy, runtime process-start behavior, BEA patching, and rebuild parity remain unproven.",
                tags("crt-runtime", "environment", "startup")
            ),
            new Spec(
                "0x00568ed7",
                "CRT__BuildArgvTable",
                new String[] {},
                "__cdecl",
                voidType,
                new ParameterImpl[] {},
                false,
                "Wave638 CRT command-line/runtime hardening: process-start argv table builder reached from entry. It seeds the module filename fallback, chooses the raw command-line cursor when present, calls CRT__ParseCommandLineToArgv once for sizing, allocates the combined argv-pointer/text buffer, parses again into that buffer, stores the argv table, and records argc as slot count minus the null terminator. Static CRT argv evidence only; exact argv/global layout, command-line edge-case equivalence, runtime process-start behavior, BEA patching, and rebuild parity remain unproven.",
                tags("crt-runtime", "command-line", "argv", "startup")
            ),
            new Spec(
                "0x00568f70",
                "CRT__ParseCommandLineToArgv",
                new String[] {},
                "__cdecl",
                voidType,
                new ParameterImpl[] {param("commandLine", charPtr), param("argvTable", charPtrPtr), param("argTextBuffer", charPtr), param("outArgvSlotCount", intPtr), param("outArgTextBytes", intPtr)},
                false,
                "Wave638 CRT command-line/runtime hardening: two-pass command-line parser used by CRT__BuildArgvTable for sizing and filling argv storage. It handles the quoted program-name token, whitespace token boundaries, backslash/quote runs, multibyte lead-byte payloads through the active ctype table, optional argv pointer writes, optional text-buffer writes, null termination, and output counts for argv slots and argument text bytes. Static CRT argv parsing evidence only; exact MSVC CRT version, full command-line quoting equivalence, multibyte edge cases, runtime process-start behavior, BEA patching, and rebuild parity remain unproven.",
                tags("crt-runtime", "command-line", "argv", "parser")
            ),
            new Spec(
                "0x00569124",
                "CRT__GetEnvironmentStringsDupA",
                new String[] {"CRT__GetEnvironmentStringsDupA_00569124"},
                "__cdecl",
                charPtr,
                new ParameterImpl[] {},
                false,
                "Wave638 CRT command-line/runtime hardening: duplicated ANSI environment-block helper reached from entry and spawn environment-building code. It prefers GetEnvironmentStringsW when available, converts the double-null wide block to multibyte with WideCharToMultiByte, otherwise duplicates the ANSI block from GetEnvironmentStringsA with CRT__MemMove, frees the OS-owned environment strings, and returns a malloc-owned block or null. Static CRT environment evidence only; exact codepage policy, environment-block lifetime, runtime process-start/spawn behavior, BEA patching, and rebuild parity remain unproven.",
                tags("crt-runtime", "environment", "startup", "spawn", "name-corrected")
            ),
            new Spec(
                "0x00569256",
                "CRT__ReportRuntimeErrorIfCriticalMode",
                new String[] {},
                "__cdecl",
                voidType,
                new ParameterImpl[] {},
                false,
                "Wave638 CRT command-line/runtime hardening: critical-mode runtime-error reporter reached from __amsg_exit and fatal-exit reporting. When the critical-error mode is active it reports runtime code 0xfc, invokes the optional callback at DAT_009d0acc, then reports runtime code 0xff. Static CRT runtime-error evidence only; exact error-mode policy, callback ABI, UI/console behavior, BEA patching, and rebuild parity remain unproven.",
                tags("crt-runtime", "runtime-error", "startup")
            ),
            new Spec(
                "0x0056928f",
                "CRT__ReportRuntimeError",
                new String[] {},
                "__cdecl",
                voidType,
                new ParameterImpl[] {param("runtimeErrorCode", intType)},
                false,
                "Wave638 CRT command-line/runtime hardening: runtime-error message dispatcher used by __amsg_exit, fatal-exit, and the critical-mode reporter. It searches the observed runtime-error table at DAT_00656130, writes matching text to STDERR through WriteFile in critical mode, otherwise builds a program-name-prefixed Runtime Error message and routes it through CRT__MessageBoxA_WithActivePopupFallback. Static CRT runtime-error evidence only; exact runtime-error table identity, UI/console behavior, localization, BEA patching, and rebuild parity remain unproven.",
                tags("crt-runtime", "runtime-error", "message")
            ),
            new Spec(
                "0x005693e2",
                "CRT__IsReadablePtr",
                new String[] {},
                "__cdecl",
                boolType,
                new ParameterImpl[] {param("ptr", voidPtr), param("byteCount", uintType)},
                false,
                "Wave638 CRT command-line/runtime hardening: readable-pointer probe used by CRT C++ exception scope/catch helpers. It wraps IsBadReadPtr and returns true when the probed range is not rejected. Static CRT pointer-probe evidence only; Windows pointer-probe reliability, exception metadata layout, runtime exception behavior, BEA patching, and rebuild parity remain unproven.",
                tags("crt-runtime", "pointer-probe", "seh")
            ),
            new Spec(
                "0x005693fe",
                "CRT__IsWritablePtr",
                new String[] {},
                "__cdecl",
                boolType,
                new ParameterImpl[] {param("ptr", voidPtr), param("byteCount", uintType)},
                false,
                "Wave638 CRT command-line/runtime hardening: writable-pointer probe used by CRT C++ catch-object construction helpers. It wraps IsBadWritePtr and returns true when the probed range is not rejected. Static CRT pointer-probe evidence only; Windows pointer-probe reliability, catch-object layout, runtime exception behavior, BEA patching, and rebuild parity remain unproven.",
                tags("crt-runtime", "pointer-probe", "seh")
            ),
            new Spec(
                "0x0056941a",
                "CRT__IsExecutablePtr",
                new String[] {},
                "__cdecl",
                boolType,
                new ParameterImpl[] {param("codePtr", voidPtr)},
                false,
                "Wave638 CRT command-line/runtime hardening: executable-pointer probe used by the unhandled-exception and C++ catch-object paths. It wraps IsBadCodePtr and returns true when the target procedure pointer is not rejected. Static CRT pointer-probe evidence only; Windows pointer-probe reliability, callback ABI, runtime exception behavior, BEA patching, and rebuild parity remain unproven.",
                tags("crt-runtime", "pointer-probe", "seh")
            ),
            new Spec(
                "0x00569432",
                "CRT__FatalRuntimeErrorAndExit",
                new String[] {},
                "__cdecl",
                voidType,
                new ParameterImpl[] {},
                false,
                "Wave638 CRT command-line/runtime hardening: fatal runtime-error exit helper reached from TLS cleanup callback/finalizer paths. It reports runtime error code 10, raises signal 0x16, then exits with code 3 through __exit. Static CRT fatal-exit evidence only; exact signal/error policy, process-exit behavior, BEA patching, and rebuild parity remain unproven.",
                tags("crt-runtime", "runtime-error", "fatal-exit")
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
            + " varargs=" + stats.varArgs
            + " missing=" + stats.missing
            + " bad=" + stats.bad);
        if (stats.missing != 0 || stats.bad != 0) {
            throw new IllegalStateException("Wave638 had missing/bad rows");
        }
    }
}
