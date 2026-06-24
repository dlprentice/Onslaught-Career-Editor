//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.DoubleDataType;
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

public class ApplyCrtRuntimeMathFdWave637 extends GhidraScript {
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
            "crt-runtime-math-fd-wave637",
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
        DataType intType = IntegerDataType.dataType;
        DataType uintType = UnsignedIntegerDataType.dataType;
        DataType doubleType = DoubleDataType.dataType;
        DataType doublePtr = new PointerDataType(doubleType);

        Spec[] specs = new Spec[] {
            new Spec(
                "0x00568667",
                "CRT__PowSpecialCaseCore",
                new String[] {},
                "__cdecl",
                intType,
                new ParameterImpl[] {param("baseLowWord", uintType), param("baseHighWord", intType), param("exponentValue", doubleType), param("outResult", doublePtr)},
                false,
                "Wave637 CRT runtime/math/fd hardening: pow-family special-case helper reached from CRT__PowCoreWithFpuGuards. It treats baseLowWord/baseHighWord as a split double, handles +/-infinity and zero/exponent edge cases, calls CRT__PowClassifyIntegralExponent for negative-base exponent parity, writes the selected double to outResult, and returns a status flag. Static CRT pow evidence only; exact MSVC CRT version, complete pow edge-case equivalence, FPU status behavior, runtime math behavior, BEA patching, and rebuild parity remain unproven.",
                tags("crt-runtime", "math", "pow")
            ),
            new Spec(
                "0x00568797",
                "CRT__PowClassifyIntegralExponent",
                new String[] {},
                "__cdecl",
                intType,
                new ParameterImpl[] {param("exponentValue", doubleType)},
                false,
                "Wave637 CRT runtime/math/fd hardening: pow-family exponent classifier used by CRT__PowSpecialCaseCore. It classifies a finite double exponent by rounding, comparing the rounded value against the input, dividing by two, and returning 2 for even integral exponents, 1 for odd integral exponents, or 0 for non-integral/non-finite cases. Static CRT pow evidence only; exact MSVC CRT version, FPU rounding/control-word edge cases, runtime math behavior, BEA patching, and rebuild parity remain unproven.",
                tags("crt-runtime", "math", "pow", "calling-convention-corrected")
            ),
            new Spec(
                "0x005687fc",
                "CRT__InitializeFileDescriptorTable",
                new String[] {},
                "__cdecl",
                voidType,
                new ParameterImpl[] {},
                false,
                "Wave637 CRT runtime/math/fd hardening: process-entry fd-table initialization helper reached from entry. It allocates 0x20 fd slots, initializes inactive descriptors, imports inherited StartupInfoA fd metadata when present, seeds stdin/stdout/stderr from GetStdHandle/GetFileType, and calls SetHandleCount with the active capacity. Static CRT fd-table evidence only; exact descriptor layout, inherited-handle semantics, runtime process-start behavior, BEA patching, and rebuild parity remain unproven.",
                tags("crt-runtime", "fd-table", "startup")
            ),
            new Spec(
                "0x005689b8",
                "CRT__CallocWithRetry",
                new String[] {"CRT__CallocWithRetry_005689b8"},
                "__cdecl",
                voidPtr,
                new ParameterImpl[] {param("elementCount", uintType), param("elementSize", uintType)},
                false,
                "Wave637 CRT runtime/math/fd hardening: calloc-family allocation helper used by thread-local, spawn, and adjacent runtime allocation paths. It multiplies elementCount by elementSize, normalizes zero/aligned byte counts, tries strategy 3 or strategy 2 small-block heap paths under heap lock 9, zeroes successful small-block allocations, falls back to HeapAlloc, and retries through CRT__InvokeNewHandler when enabled. Static CRT allocation evidence only; overflow policy, exact heap layouts, runtime allocation behavior, BEA patching, and rebuild parity remain unproven.",
                tags("crt-runtime", "heap", "calloc", "name-corrected")
            ),
            new Spec(
                "0x00568a51",
                "CRT__UnlockHeap9_SbAllocPath",
                new String[] {},
                "__cdecl",
                voidType,
                new ParameterImpl[] {},
                false,
                "Wave637 CRT runtime/math/fd hardening: small-block allocation cleanup thunk that unlocks CRT lock index 9 through CRT__UnlockByIndex. Current xref is the strategy 3 path in CRT__CallocWithRetry. Static CRT heap-cleanup evidence only; exact exception-unwind role, runtime heap behavior, BEA patching, and rebuild parity remain unproven.",
                tags("crt-runtime", "heap", "cleanup")
            ),
            new Spec(
                "0x00568ada",
                "CRT__UnlockHeap9_DeferredAllocPath",
                new String[] {},
                "__cdecl",
                voidType,
                new ParameterImpl[] {},
                false,
                "Wave637 CRT runtime/math/fd hardening: deferred small-block allocation cleanup thunk that unlocks CRT lock index 9 through CRT__UnlockByIndex. Current xref is the strategy 2 path in CRT__CallocWithRetry. Static CRT heap-cleanup evidence only; exact exception-unwind role, runtime heap behavior, BEA patching, and rebuild parity remain unproven.",
                tags("crt-runtime", "heap", "cleanup")
            ),
            new Spec(
                "0x00568b76",
                "CRT__LseekFd",
                new String[] {},
                "__cdecl",
                intType,
                new ParameterImpl[] {param("fdIndex", uintType), param("offset", intType), param("origin", intType)},
                false,
                "Wave637 CRT runtime/math/fd hardening: locked fd seek wrapper reached from stream/tell/write-wide/fseek paths. It validates the fd-table index and active flag, locks the fd slot, calls CRT__LseekFd_NoLock, unlocks the slot, and maps invalid fd input to errno 9/doserrno 0. Static CRT fd evidence only; exact fd-table layout, 64-bit seek behavior, runtime file I/O behavior, BEA patching, and rebuild parity remain unproven.",
                tags("crt-runtime", "fd-table", "lseek")
            ),
            new Spec(
                "0x00568bdb",
                "CRT__LseekFd_NoLock",
                new String[] {},
                "__cdecl",
                intType,
                new ParameterImpl[] {param("fdIndex", uintType), param("offset", intType), param("origin", intType)},
                false,
                "Wave637 CRT runtime/math/fd hardening: unlocked fd seek core used by locked seek and fd text-mode read/write/open/truncate paths. It resolves the OS handle, calls SetFilePointer, clears the text-lookahead flag on success, maps Win32 errors through CRT__SetErrnoAndDosErrnoFromWinError, and returns -1 on failure. Static CRT fd evidence only; exact fd-table flag names, large-file behavior, runtime file I/O behavior, BEA patching, and rebuild parity remain unproven.",
                tags("crt-runtime", "fd-table", "lseek")
            ),
            new Spec(
                "0x00568c4e",
                "CRT__StructuredExceptionFilterDispatch",
                new String[] {},
                "__cdecl",
                intType,
                new ParameterImpl[] {param("exceptionCode", intType), param("exceptionPointers", voidPtr)},
                false,
                "Wave637 CRT runtime/math/fd hardening: structured-exception filter dispatcher reached from entry. It looks up exceptionCode in the thread-local exception-action table via CRT__FindExceptionActionEntry, falls back to UnhandledExceptionFilter when no action exists, handles sentinel actions 1 and 5, updates thread-local exception pointers/status around callback invocation, and returns the filter result. Static CRT SEH evidence only; exact exception-action table layout, callback ABI, runtime exception behavior, BEA patching, and rebuild parity remain unproven.",
                tags("crt-runtime", "seh", "exception")
            ),
            new Spec(
                "0x00568d8c",
                "CRT__FindExceptionActionEntry",
                new String[] {"CDXTexture__FindKeyedTripletEntry"},
                "__cdecl",
                voidPtr,
                new ParameterImpl[] {param("exceptionCode", intType), param("tableBase", voidPtr)},
                false,
                "Wave637 CRT runtime/math/fd hardening: exception-action table search helper used only by CRT__StructuredExceptionFilterDispatch in current xrefs. It walks DAT_0065612c 0x0c-byte records from tableBase, compares each first dword against exceptionCode, and returns the matching entry pointer or null. The previous CDXTexture owner label was stale for this CRT SEH table helper. Static CRT SEH evidence only; exact table layout, exception-code policy, runtime exception behavior, BEA patching, and rebuild parity remain unproven.",
                tags("crt-runtime", "seh", "exception", "name-corrected")
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
            throw new IllegalStateException("Wave637 had missing/bad rows");
        }
    }
}
