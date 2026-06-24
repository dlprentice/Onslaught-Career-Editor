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

public class ApplyCrtPathMbsSpawnFdWave644 extends GhidraScript {
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
            "crt-path-mbs-spawn-fd-wave644",
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

        DataType charPtr = new PointerDataType(CharDataType.dataType);
        DataType charPtrPtr = new PointerDataType(charPtr);
        DataType intType = IntegerDataType.dataType;
        DataType uintType = UnsignedIntegerDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x0056a7e7",
                "CRT__ValidatePathAttributesForOpen",
                new String[] {},
                "__cdecl",
                intType,
                new ParameterImpl[] {param("path", charPtr), param("openFlags", uintType)},
                "Wave644 CRT path/MBCS/spawn/fd hardening: checks GetFileAttributesA for a candidate open/spawn path, maps Win32 lookup failures through CRT errno state, and rejects read-only files when the open flags request writable access. Static CRT path/open evidence only; exact MSVC CRT version, full open-flag mapping, Windows filesystem edge cases, runtime CreateProcess/file I/O behavior, BEA patching, and rebuild parity remain unproven.",
                tags("crt-runtime", "path-validation", "file-open", "errno")
            ),
            new Spec(
                "0x0056a82d",
                "CRT__MbsChr",
                new String[] {},
                "__cdecl",
                charPtr,
                new ParameterImpl[] {param("text", charPtr), param("charValue", uintType)},
                "Wave644 CRT path/MBCS/spawn/fd hardening: multibyte-aware strchr-style helper used by spawn/path and environment update code, falling back to _strchr in single-byte mode and otherwise walking lead-byte pairs under CRT lock 0x19. Static CRT MBCS evidence only; exact MSVC CRT version, locale/codepage table layout, signed-char behavior, runtime string equivalence, BEA patching, and rebuild parity remain unproven.",
                tags("crt-runtime", "mbcs", "string-search", "spawn-path")
            ),
            new Spec(
                "0x0056a8c4",
                "CRT__MbsRChr",
                new String[] {},
                "__cdecl",
                charPtr,
                new ParameterImpl[] {param("text", charPtr), param("charValue", uintType)},
                "Wave644 CRT path/MBCS/spawn/fd hardening: multibyte-aware strrchr-style helper used by spawn/path suffix and dot-counter code, falling back to _strrchr in single-byte mode and otherwise tracking the last matching byte or lead-byte pair under CRT lock 0x19. Static CRT MBCS evidence only; exact MSVC CRT version, locale/codepage table layout, signed-char behavior, runtime string equivalence, BEA patching, and rebuild parity remain unproven.",
                tags("crt-runtime", "mbcs", "string-search", "spawn-path")
            ),
            new Spec(
                "0x0056a936",
                "CRT__SpawnVe",
                new String[] {"CRT__SpawnVe_0056a936"},
                "__cdecl",
                intType,
                new ParameterImpl[] {param("spawnMode", intType), param("resolvedPath", charPtr), param("commandLineBlock", charPtr), param("environmentBlock", charPtr)},
                "Wave644 CRT path/MBCS/spawn/fd hardening: CreateProcessA-backed spawn helper reached from CRT__SpawnResolvedPathWithBuiltCommandEnv. It validates spawn mode, normalizes the built command-line block, builds inherited fd startup data, optionally masks std handles for detached mode, waits/returns exit code for wait mode, returns the process handle for async modes, and maps Win32 failures through CRT errno state. Static CRT spawn evidence only; exact MSVC CRT API identity, handle/exit-code ABI, command-line quoting equivalence, inherited-fd layout, runtime CreateProcess behavior, BEA patching, and rebuild parity remain unproven.",
                tags("crt-runtime", "spawn", "CreateProcessA", "fd-inheritance")
            ),
            new Spec(
                "0x0056ab1f",
                "CRT__BuildSpawnCommandAndEnv",
                new String[] {"CRT__BuildSpawnCommandAndEnv_0056ab1f"},
                "__cdecl",
                intType,
                new ParameterImpl[] {param("argvVector", charPtrPtr), param("envVector", charPtrPtr), param("commandLineOut", charPtrPtr), param("environmentBlockOut", charPtrPtr)},
                "Wave644 CRT path/MBCS/spawn/fd hardening: allocates and fills the command-line and optional environment blocks consumed by CRT__SpawnVe, concatenating argv strings with spaces, preserving drive-current-directory environment entries from the process environment, appending caller envp entries, and reporting allocation failures through CRT errno state. Static CRT spawn/environment evidence only; exact MSVC CRT API identity, command-line quoting equivalence, environment-block layout/lifetime, runtime CreateProcess behavior, BEA patching, and rebuild parity remain unproven.",
                tags("crt-runtime", "spawn", "environment", "command-line")
            ),
            new Spec(
                "0x0056ad25",
                "CRT__OpenFd",
                new String[] {},
                "__cdecl",
                uintType,
                new ParameterImpl[] {param("path", charPtr), param("openFlags", uintType), param("shareMode", uintType), param("permissionFlags", uintType)},
                "Wave644 CRT path/MBCS/spawn/fd hardening: open()-style fd allocator that maps CRT open/share/cache/text flags to CreateFileA access/share/creation/attribute values, allocates an fd-table slot, records file-type and inheritance flags, handles append/text EOF adjustment, and returns the fd index or 0xffffffff on error. Static CRT file-I/O evidence only; exact MSVC CRT version, full flag mapping, fd-table layout, text-mode EOF semantics, runtime file I/O behavior, BEA patching, and rebuild parity remain unproven.",
                tags("crt-runtime", "file-open", "fd-table", "CreateFileA")
            ),
            new Spec(
                "0x0056b117",
                "CRT__SetOsHandle",
                new String[] {},
                "__cdecl",
                intType,
                new ParameterImpl[] {param("fdIndex", uintType), param("osHandle", intType)},
                "Wave644 CRT path/MBCS/spawn/fd hardening: stores a Win32 OS handle in an unused fd-table slot and mirrors fd 0/1/2 into the process standard handles when the runtime standard-handle mode is active; invalid or already-populated slots set EBADF-style CRT errno state. Static CRT fd-table evidence only; exact MSVC CRT version, full fd-table layout, standard-handle policy, runtime handle ownership, BEA patching, and rebuild parity remain unproven.",
                tags("crt-runtime", "fd-table", "handle", "stdio")
            ),
            new Spec(
                "0x0056b193",
                "CRT__FreeOsHandle",
                new String[] {},
                "__cdecl",
                intType,
                new ParameterImpl[] {param("fdIndex", uintType)},
                "Wave644 CRT path/MBCS/spawn/fd hardening: clears a populated fd-table OS-handle slot, mirrors fd 0/1/2 to null standard handles when the runtime standard-handle mode is active, and reports invalid or already-free slots through EBADF-style CRT errno state. Static CRT fd-table evidence only; exact MSVC CRT version, full fd-table layout, standard-handle policy, runtime handle ownership, BEA patching, and rebuild parity remain unproven.",
                tags("crt-runtime", "fd-table", "handle", "stdio")
            ),
            new Spec(
                "0x0056b212",
                "CRT__GetOsFileHandleByIndex",
                new String[] {},
                "__cdecl",
                intType,
                new ParameterImpl[] {param("fdIndex", uintType)},
                "Wave644 CRT path/MBCS/spawn/fd hardening: validates an fd-table index and in-use flag before returning the stored OS handle, otherwise setting EBADF-style CRT errno state and returning -1. Static CRT fd-table evidence only; exact MSVC CRT version, full fd-table layout, runtime handle ownership, BEA patching, and rebuild parity remain unproven.",
                tags("crt-runtime", "fd-table", "handle")
            ),
            new Spec(
                "0x0056b254",
                "CRT__LockFileHandleByIndex",
                new String[] {},
                "__cdecl",
                VoidDataType.dataType,
                new ParameterImpl[] {param("fdIndex", uintType)},
                "Wave644 CRT path/MBCS/spawn/fd hardening: lazily initializes the per-fd critical section under global lock 0x11, marks the fd-table lock as initialized, and enters the per-handle critical section for synchronized file-handle operations. Static CRT fd-lock evidence only; exact MSVC CRT version, full fd-table layout, lock lifetime/destruction policy, runtime synchronization behavior, BEA patching, and rebuild parity remain unproven.",
                tags("crt-runtime", "fd-table", "locking", "critical-section")
            ),
            new Spec(
                "0x0056b2b3",
                "CRT__UnlockFileHandleByIndex",
                new String[] {},
                "__cdecl",
                VoidDataType.dataType,
                new ParameterImpl[] {param("fdIndex", uintType)},
                "Wave644 CRT path/MBCS/spawn/fd hardening: leaves the per-fd critical section selected from the fd-table slot index after synchronized close/read/write/seek/commit operations. Static CRT fd-lock evidence only; exact MSVC CRT version, full fd-table layout, lock lifetime/destruction policy, runtime synchronization behavior, BEA patching, and rebuild parity remain unproven.",
                tags("crt-runtime", "fd-table", "locking", "critical-section")
            ),
            new Spec(
                "0x0056b2d5",
                "CRT__CommitFileHandle",
                new String[] {},
                "__cdecl",
                intType,
                new ParameterImpl[] {param("fdIndex", uintType)},
                "Wave644 CRT path/MBCS/spawn/fd hardening: validates and locks an fd-table entry, resolves its OS handle, calls FlushFileBuffers, stores the Win32 error in CRT doserrno on failure, unlocks the entry, and returns 0 or -1. Static CRT fd-commit evidence only; exact MSVC CRT version, full fd-table layout, flush semantics, runtime file I/O behavior, BEA patching, and rebuild parity remain unproven.",
                tags("crt-runtime", "fd-table", "file-commit", "FlushFileBuffers")
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
            throw new IllegalStateException("Wave644 had missing/bad rows");
        }
    }
}
