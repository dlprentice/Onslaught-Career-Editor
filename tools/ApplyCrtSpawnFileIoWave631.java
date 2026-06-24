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

public class ApplyCrtSpawnFileIoWave631 extends GhidraScript {
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
            "crt-spawn-file-io-wave631",
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
        }
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

    private boolean signatureMatches(Function fn, Spec spec) {
        return fn.getSignature().toString().equals(expectedSignature(spec));
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
                println("BADNAME: " + spec.address + " expected " + spec.name + " current " + fn.getName());
                return;
            }
            boolean renameNeeded = !fn.getName().equals(spec.name);
            boolean signatureNeeded = !signatureMatches(fn, spec);
            boolean updateNeeded = needsUpdate(fn, spec);
            if (!updateNeeded) {
                stats.skipped++;
                println("SKIP: " + spec.address + " " + fn.getSignature());
                return;
            }
            if (dryRun) {
                if (renameNeeded) {
                    stats.wouldRename++;
                    println("WOULD_RENAME: " + spec.address + " " + fn.getName() + " -> " + spec.name);
                } else {
                    println("WOULD_UPDATE: " + spec.address + " " + spec.name);
                }
                return;
            }
            if (renameNeeded) {
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
            fn.setComment(spec.comment);
            for (String tag : spec.tags) {
                fn.addTag(tag);
            }
            verifyReadBack(spec);
            if (signatureNeeded) {
                stats.signatureUpdated++;
            }
            stats.updated++;
            println("OK: " + spec.address + " " + spec.name + " -> " + functionAtEntry(spec.address).getSignature().toString());
            Thread.sleep(50);
        } catch (Exception ex) {
            stats.bad++;
            println("ERROR: " + spec.address + " " + spec.name + " " + ex.getClass().getSimpleName() + ": " + ex.getMessage());
        }
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");

        DataType intType = IntegerDataType.dataType;
        DataType uintType = UnsignedIntegerDataType.dataType;
        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(VoidDataType.dataType);
        DataType charPtr = new PointerDataType(CharDataType.dataType);

        Spec[] specs = new Spec[] {
            new Spec(
                "0x0055e412",
                "CRT__SpawnPathVarargsNoEnv_Thunk",
                new String[] {"CDXTexture__LoadPathFallbackNoFlags_Thunk"},
                "__cdecl",
                voidType,
                new ParameterImpl[] {param("spawnMode", intType), param("commandPath", charPtr)},
                "Wave631 CRT spawn/file-I/O correction: fixed stale CDXTexture owner label. This thunk takes spawn mode and command path, passes the first variadic stack argument as the argv vector, supplies a null environment pointer, and forwards to CRT__SpawnSearchPathWithFallbackExtensions. Static CRT spawn wrapper evidence only; exact exported CRT API identity, varargs contract, return-value use, runtime process behavior, and rebuild parity remain unproven.",
                tags("crt-runtime", "spawn", "stale-owner-corrected", "varargs-thunk")
            ),
            new Spec(
                "0x0055e45f",
                "CRT__OpenFileByModeString_AutoUnlock",
                new String[] {},
                "__cdecl",
                voidPtr,
                new ParameterImpl[] {param("path", charPtr), param("modeString", charPtr), param("shareFlags", intType)},
                "Wave631 CRT spawn/file-I/O hardening: fopen-facing wrapper acquires a CRT file-stream slot, calls CRT__OpenFileByModeString with the path, mode string, share flag, and locked stream descriptor, then unlocks through CRT__UnlockRouteByAddress before returning the FILE-like stream pointer or null. Static CRT file-open evidence only; exact CRT version, FILE layout, sharing semantics, runtime I/O behavior, and rebuild parity remain unproven.",
                tags("crt-runtime", "file-open", "stdio", "auto-unlock")
            ),
            new Spec(
                "0x005638a8",
                "CRT__FlushStreamIfWritePending",
                new String[] {},
                "__cdecl",
                voidType,
                new ParameterImpl[] {param("enabled", intType), param("stream", voidPtr)},
                "Wave631 CRT spawn/file-I/O correction: preserves the Wave629 stream-output behavior claim but fixes the stale callee owner. When enabled and the stream has pending write-buffer state, this helper flushes through CRT__FlushWriteStreamSegment, clears write/buffer flag bits, and zeroes stream cursor/count/base fields. Static CRT stream-output evidence only; exact FILE layout, runtime flush behavior, and rebuild parity remain unproven.",
                tags("crt-runtime", "stream-output", "stdio-buffer", "stale-callee-corrected")
            ),
            new Spec(
                "0x00564a0b",
                "CRT__SpawnSearchPathWithFallbackExtensions",
                new String[] {"CDXTexture__LoadFromPathWithFallbackExtensions"},
                "__cdecl",
                intType,
                new ParameterImpl[] {param("spawnMode", intType), param("commandPath", charPtr), param("argv", voidPtr), param("envp", voidPtr)},
                "Wave631 CRT spawn/file-I/O correction: fixed stale CDXTexture owner label. The body checks slash/backslash/drive-colon path markers, optionally builds a dot-backslash relative path, appends fallback extensions from the static extension table when the command has no suffix, validates candidates through CRT__ValidatePathAttributesForOpen, and dispatches the resolved candidate to CRT__SpawnResolvedPathWithBuiltCommandEnv. Static CRT spawn/path-probe evidence only; exact CRT API identity, extension-table contents, PATH-search equivalence, runtime CreateProcess behavior, and rebuild parity remain unproven.",
                tags("crt-runtime", "spawn", "path-probe", "stale-owner-corrected")
            ),
            new Spec(
                "0x00564b54",
                "CRT__SpawnResolvedPathWithBuiltCommandEnv",
                new String[] {"CDXTexture__LoadFromResolvedPathAndDecodedBuffer"},
                "__cdecl",
                intType,
                new ParameterImpl[] {param("spawnMode", intType), param("resolvedPath", charPtr), param("argv", voidPtr), param("envp", voidPtr)},
                "Wave631 CRT spawn/file-I/O correction: fixed stale CDXTexture owner label. The helper builds command-line and environment blocks with CRT__BuildSpawnCommandAndEnv_0056ab1f, calls CRT__SpawnVe_0056a936 for the resolved path, frees the allocated command/environment buffers, and returns the spawn result or -1. Static CRT spawn/CreateProcess evidence only; exact CRT API identity, environment block layout, process-handle/exit-code semantics, and rebuild parity remain unproven.",
                tags("crt-runtime", "spawn", "createprocess", "stale-owner-corrected")
            ),
            new Spec(
                "0x00564ba5",
                "CRT__UnhandledExceptionFilterDispatch",
                new String[] {},
                "__stdcall",
                intType,
                new ParameterImpl[] {param("exceptionPointers", voidPtr)},
                "Wave631 CRT spawn/file-I/O hardening: unhandled-exception filter dispatch checks the C++ exception code 0xe06d7363 and magic 0x19930520 before routing to CDXTexture__InvokeTlsCleanupCallbackAndFinalize; otherwise it validates the prior filter pointer through CRT__IsExecutablePtr and calls it when executable. Static CRT/SEH evidence only; exact CRT version, exception-object layout, prior-filter ownership, runtime exception behavior, and rebuild parity remain unproven.",
                tags("crt-runtime", "seh", "unhandled-exception-filter")
            ),
            new Spec(
                "0x00564c09",
                "CRT__OpenFileByModeString",
                new String[] {},
                "__cdecl",
                voidPtr,
                new ParameterImpl[] {param("path", charPtr), param("modeString", charPtr), param("shareFlags", intType), param("stream", voidPtr)},
                "Wave631 CRT spawn/file-I/O hardening: parses fopen-style mode strings for r/w/a, plus, text/binary, commit/no-commit, and sharing/cache flags; opens a file descriptor through CRT__OpenFd, increments the stream count, and initializes the FILE-like stream descriptor fields before returning the stream pointer or null. Static CRT file-open evidence only; exact mode-bit mapping, FILE/fd table layout, runtime I/O behavior, and rebuild parity remain unproven.",
                tags("crt-runtime", "file-open", "stdio", "mode-parser")
            ),
            new Spec(
                "0x00564d79",
                "CRT__AcquireFileStreamSlot",
                new String[] {},
                "__cdecl",
                voidPtr,
                new ParameterImpl[] {},
                "Wave631 CRT spawn/file-I/O hardening: locks the global stream table, finds an unused stream descriptor or allocates a new 0x38-byte descriptor, initializes its critical section when newly allocated, locks the selected stream, clears cursor/count/base/flag/fd-style fields, unlocks the global table, and returns the locked stream pointer or null. Static CRT stream-table evidence only; exact FILE layout, allocator failure behavior, runtime lock ordering, and rebuild parity remain unproven.",
                tags("crt-runtime", "stdio", "stream-table", "lock")
            ),
            new Spec(
                "0x00564e41",
                "CRT__CloseFd",
                new String[] {},
                "__cdecl",
                intType,
                new ParameterImpl[] {param("fdIndex", uintType)},
                "Wave631 CRT spawn/file-I/O hardening: validates an fd-table entry, locks it by index, calls CRT__CloseFd_NoLock, unlocks the entry, and returns the close result; invalid indices set errno to EBADF and doserrno to zero before returning -1. Static CRT fd-table evidence only; exact fd table layout, runtime locking behavior, and rebuild parity remain unproven.",
                tags("crt-runtime", "file-close", "fd-table", "lock")
            ),
            new Spec(
                "0x00564e9e",
                "CRT__CloseFd_NoLock",
                new String[] {},
                "__cdecl",
                intType,
                new ParameterImpl[] {param("fdIndex", uintType)},
                "Wave631 CRT spawn/file-I/O hardening: no-lock fd close helper gets the OS handle, avoids double-closing shared stdout/stderr handles, calls CloseHandle when needed, frees the fd-table handle slot, clears the in-use byte, and maps GetLastError through CRT__SetErrnoAndDosErrnoFromWinError_00567a35 on failure. Static CRT fd-table evidence only; exact standard-handle sharing semantics, runtime close behavior, and rebuild parity remain unproven.",
                tags("crt-runtime", "file-close", "fd-table", "win32-handle")
            ),
            new Spec(
                "0x00564f4c",
                "CRT__FlushAndCommitFileStream",
                new String[] {},
                "__cdecl",
                intType,
                new ParameterImpl[] {param("stream", voidPtr)},
                "Wave631 CRT spawn/file-I/O hardening: flushes pending stream output through CRT__FlushWriteStreamSegment and, when the stream commit flag is set, commits the underlying fd through CRT__CommitFileHandle; returns 0 on success and -1 on flush or commit failure. Static CRT stream-output evidence only; exact FILE flag meanings, runtime flush/commit behavior, and rebuild parity remain unproven.",
                tags("crt-runtime", "stream-output", "flush", "commit")
            ),
            new Spec(
                "0x00564f7a",
                "CRT__FlushWriteStreamSegment",
                new String[] {"CDXTexture__FlushWriteStreamSegment"},
                "__cdecl",
                intType,
                new ParameterImpl[] {param("stream", voidPtr)},
                "Wave631 CRT spawn/file-I/O correction: fixed stale CDXTexture owner label. The helper checks writable buffered stream flags, computes the pending byte count from cursor/base fields, writes through CRT__WriteFdTextMode_Locking_00567505, marks stream error on short write, clears the write/update flag when appropriate, then resets count and cursor back to the buffer base. Static CRT stream-output evidence only; exact FILE layout, text-mode translation behavior, runtime I/O behavior, and rebuild parity remain unproven.",
                tags("crt-runtime", "stream-output", "flush", "stale-owner-corrected")
            ),
            new Spec(
                "0x00564fdf",
                "CRT__FlushAllFileStreamsByMode",
                new String[] {"CRT__FlushOrCloseAllFileHandles"},
                "__cdecl",
                intType,
                new ParameterImpl[] {param("flushMode", intType)},
                "Wave631 CRT spawn/file-I/O hardening: locks the global stream table and walks active stream descriptors. Mode 1 flushes and commits active streams while counting successes; mode 0 flushes writable streams and returns -1 if any flush/commit fails. Static CRT stream-table evidence only; exact _flushall/_fcloseall API identity, close behavior outside this helper, runtime locking behavior, and rebuild parity remain unproven.",
                tags("crt-runtime", "stream-output", "flush-all", "stream-table")
            )
        };

        Stats stats = new Stats();
        println("MODE: " + (dryRun ? "dry" : "apply"));
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }
        println(
            "SUMMARY: updated=" + stats.updated
            + " skipped=" + stats.skipped
            + " renamed=" + stats.renamed
            + " would_rename=" + stats.wouldRename
            + " signature_updated=" + stats.signatureUpdated
            + " missing=" + stats.missing
            + " bad=" + stats.bad
        );
        if (stats.missing != 0 || stats.bad != 0) {
            throw new IllegalStateException("Wave631 apply encountered missing/bad rows");
        }
    }
}
