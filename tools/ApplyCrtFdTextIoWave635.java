//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
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

public class ApplyCrtFdTextIoWave635 extends GhidraScript {
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
            "crt-fd-text-io-wave635",
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

        DataType voidPtr = new PointerDataType(VoidDataType.dataType);
        DataType intType = IntegerDataType.dataType;
        DataType uintType = UnsignedIntegerDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x00567505",
                "CRT__WriteFdTextMode_Locked",
                new String[] {"CRT__WriteFdTextMode_Locking_00567505"},
                "__cdecl",
                intType,
                new ParameterImpl[] {param("fdIndex", uintType), param("buffer", voidPtr), param("byteCount", uintType)},
                false,
                "Wave635 CRT fd/text I/O hardening: locked fd write wrapper. It validates the fd-table index and active flag, locks the fd slot, delegates to CRT__WriteFdTextMode_NoLock, unlocks, and maps invalid fd input to errno 9/doserrno 0 with a -1 return. Static CRT wrapper evidence only; exact fd-table layout, lock ownership, runtime WriteFile behavior, BEA patching, and rebuild parity remain unproven.",
                tags("crt-runtime", "file-io", "text-mode", "write", "locked-wrapper", "name-corrected")
            ),
            new Spec(
                "0x0056756a",
                "CRT__WriteFdTextMode_NoLock",
                new String[] {},
                "__cdecl",
                intType,
                new ParameterImpl[] {param("fdIndex", uintType), param("buffer", voidPtr), param("byteCount", uintType)},
                false,
                "Wave635 CRT fd/text I/O hardening: unlocked fd write core. It honors append-seek state, writes binary-mode buffers directly through WriteFile, expands LF to CRLF into a bounded local text buffer for text-mode fds, returns the original byte count adjusted for inserted CR bytes, and maps Win32 write errors through errno/doserrno. Static CRT I/O evidence only; exact fd flag names, text-mode edge cases, runtime WriteFile behavior, BEA patching, and rebuild parity remain unproven.",
                tags("crt-runtime", "file-io", "text-mode", "write")
            ),
            new Spec(
                "0x00567700",
                "CRT__MemMove",
                new String[] {"CRT__MemMove_00567700"},
                "__cdecl",
                voidPtr,
                new ParameterImpl[] {param("dest", voidPtr), param("src", voidPtr), param("byteCount", uintType)},
                false,
                "Wave635 CRT fd/text I/O hardening: later CRT memmove helper. It returns the destination pointer, copies backward for overlapping ranges where src < dest < src + byteCount, otherwise copies forward, and uses alignment-aware dword loops with byte-tail handling. Static memory-helper evidence only; exact MSVC CRT identity, runtime aliasing behavior beyond the observed decompile, BEA patching, and rebuild parity remain unproven.",
                tags("crt-runtime", "memory", "memmove", "name-corrected")
            ),
            new Spec(
                "0x00567a35",
                "CRT__SetErrnoAndDosErrnoFromWinError",
                new String[] {"CRT__SetErrnoAndDosErrnoFromWinError_00567a35"},
                "__cdecl",
                VoidDataType.dataType,
                new ParameterImpl[] {param("winError", uintType)},
                false,
                "Wave635 CRT fd/text I/O hardening: maps a Win32 error into thread-local doserrno and errno. It stores winError into the doserrno slot, searches the observed 8-byte mapping table, and falls back to errno 0xd, 8, or 0x16 for the visible Win32 error ranges. Static CRT error-mapping evidence only; exact table identity, thread-local record layout, runtime error propagation, BEA patching, and rebuild parity remain unproven.",
                tags("crt-runtime", "errno", "win32-error", "name-corrected")
            ),
            new Spec(
                "0x00567aba",
                "CRT__ReadByteWithBufferRefill",
                new String[] {},
                "__cdecl",
                uintType,
                new ParameterImpl[] {param("stream", voidPtr)},
                false,
                "Wave635 CRT fd/text I/O hardening: FILE-like buffered-byte refill helper. It validates stream read/error state, initializes a buffer when needed, calls CRT__ReadFdTextMode_Locked with the stream fd and buffer span, updates count/cursor fields, returns the first buffered byte, and returns 0xffffffff on EOF/error. Static stream-buffer evidence only; exact FILE layout, stream flag names, runtime ReadFile behavior, BEA patching, and rebuild parity remain unproven.",
                tags("crt-runtime", "file-io", "stream-buffer", "read")
            ),
            new Spec(
                "0x00567b96",
                "CRT__ReadFdTextMode_Locked",
                new String[] {},
                "__cdecl",
                intType,
                new ParameterImpl[] {param("fdIndex", uintType), param("buffer", voidPtr), param("byteCount", uintType)},
                false,
                "Wave635 CRT fd/text I/O hardening: locked fd read wrapper. It validates the fd-table index and active flag, locks the fd slot, delegates to CRT__ReadFdTextMode_NoLock, unlocks, and maps invalid fd input to errno 9/doserrno 0 with a -1 return. Static CRT wrapper evidence only; exact fd-table layout, lock ownership, runtime ReadFile behavior, BEA patching, and rebuild parity remain unproven.",
                tags("crt-runtime", "file-io", "text-mode", "read", "locked-wrapper")
            ),
            new Spec(
                "0x00567bfb",
                "CRT__ReadFdTextMode_NoLock",
                new String[] {},
                "__cdecl",
                intType,
                new ParameterImpl[] {param("fdIndex", uintType), param("buffer", voidPtr), param("byteCount", uintType)},
                false,
                "Wave635 CRT fd/text I/O hardening: unlocked fd read core. It handles zero-length reads, pending lookahead bytes, binary-mode direct ReadFile results, text-mode CRLF-to-LF translation, Ctrl-Z EOF handling, final-CR lookahead or seek-back, and Win32 error mapping including access-denied and broken-pipe cases. Static CRT I/O evidence only; exact fd flag names, lookahead slot semantics, runtime ReadFile behavior, BEA patching, and rebuild parity remain unproven.",
                tags("crt-runtime", "file-io", "text-mode", "read")
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
            throw new IllegalStateException("Wave635 had missing/bad rows");
        }
    }
}
