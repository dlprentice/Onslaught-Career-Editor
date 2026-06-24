//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.CharDataType;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.DoubleDataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.ShortDataType;
import ghidra.program.model.data.UnsignedIntegerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.FunctionTag;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyWin32CrtStreamTailWave624 extends GhidraScript {
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
            "win32-crt-stream-tail-wave624",
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

        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(VoidDataType.dataType);
        DataType charPtr = new PointerDataType(CharDataType.dataType);
        DataType shortPtr = new PointerDataType(ShortDataType.dataType);
        DataType intType = IntegerDataType.dataType;
        DataType uintType = UnsignedIntegerDataType.dataType;
        DataType doubleType = DoubleDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x0055f5ee",
                "Win32__FindFirstFileWithMeta",
                new String[] {},
                "__cdecl",
                intType,
                new ParameterImpl[] {param("pattern", charPtr), param("outFindMeta", voidPtr)},
                "Wave624 Win32/CRT stream-tail hardening: FindFirstFileA wrapper used by save-file enumeration. On success it copies non-normal attributes, converted creation/access/write times, file size, and filename into outFindMeta; on failure it maps selected Win32 errors into CRT errno values and returns -1. Static Win32-wrapper evidence only; exact metadata struct layout, runtime save enumeration behavior, and rebuild parity remain unproven.",
                tags("win32-find", "crt-errno", "save-enumeration")
            ),
            new Spec(
                "0x0055f6bb",
                "Win32__FindNextFileWithMeta",
                new String[] {},
                "__cdecl",
                intType,
                new ParameterImpl[] {param("findHandle", intType), param("outFindMeta", voidPtr)},
                "Wave624 Win32/CRT stream-tail hardening: FindNextFileA wrapper used by save-file enumeration. On success it refreshes the same file metadata buffer as Win32__FindFirstFileWithMeta and returns 0; on failure it maps selected Win32 errors into CRT errno values and returns -1. Static Win32-wrapper evidence only; exact metadata struct layout, runtime save enumeration behavior, and rebuild parity remain unproven.",
                tags("win32-find", "crt-errno", "save-enumeration")
            ),
            new Spec(
                "0x0055f783",
                "Win32__FindCloseWithErrno",
                new String[] {},
                "__cdecl",
                intType,
                new ParameterImpl[] {param("findHandle", intType)},
                "Wave624 Win32/CRT stream-tail hardening: FindClose wrapper returning 0 on success, or setting CRT errno 0x16 and returning -1 if FindClose fails. Xrefs are save-file enumeration cleanup paths. Static Win32-wrapper evidence only; runtime handle ownership and rebuild parity remain unproven.",
                tags("win32-find", "crt-errno", "save-enumeration")
            ),
            new Spec(
                "0x0055f807",
                "CRT__MbsNcpy_LocaleLock",
                new String[] {},
                "__cdecl",
                charPtr,
                new ParameterImpl[] {param("dest", charPtr), param("src", charPtr), param("maxBytes", uintType)},
                "Wave624 Win32/CRT stream-tail hardening: multibyte strncpy-style helper. It falls back to strncpy when the multibyte locale table is inactive; otherwise it locks locale route 0x19, preserves lead/trail byte pairs, stops on terminator or byte limit, zero-pads remaining bytes, and unlocks. Current xref is PCPlatform async music stream setup. Static locale/string evidence only; exact CRT identity, locale table semantics, runtime audio path behavior, and rebuild parity remain unproven.",
                tags("crt-runtime", "multibyte-string", "locale-lock")
            ),
            new Spec(
                "0x0055f8a1",
                "CRT__MbsIcmp_LocaleLock",
                new String[] {},
                "__cdecl",
                intType,
                new ParameterImpl[] {param("lhs", charPtr), param("rhs", charPtr)},
                "Wave624 Win32/CRT stream-tail hardening: multibyte case-insensitive compare helper. It falls back to stricmp without active multibyte locale data; otherwise it locks locale route 0x19, folds single-byte uppercase via the locale table, maps lead-byte pairs with CRT__LCMapStringA_Compat, returns lexical -1/0/1 results, and returns 0x7fffffff on mapping failure. Current xref is PCPlatform async music stream setup. Static locale/string evidence only; exact CRT identity, collation semantics, runtime audio path behavior, and rebuild parity remain unproven.",
                tags("crt-runtime", "multibyte-string", "locale-lock")
            ),
            new Spec(
                "0x0055fa62",
                "CRT__PowCoreWithFpuGuards",
                new String[] {"CRT__PowCore_0055fa62"},
                "__cdecl",
                doubleType,
                new ParameterImpl[] {param("baseLowWord", intType), param("baseHighWord", uintType), param("exponentLowWord", intType), param("exponentHighWord", uintType)},
                "Wave624 Win32/CRT stream-tail hardening: pow core called by CRT__PowDispatch_ST0_ST1 after that wrapper spills two x87 doubles to stack and passes the exponent high word in EAX. Instruction evidence shows FPU-control checks, non-finite classification, sqrt/fyl2x/f2xm1/fscale-style x87 paths, integral-exponent handling, and CRT math-error exits. The decompiler currently reports overlapping input varnodes for this body, so this comment is instruction-backed rather than clean-decompile-backed. Static math-helper evidence only; exact CRT identity, all pow domain/exception semantics, runtime math behavior, and rebuild parity remain unproven.",
                tags("crt-runtime", "math-helper", "fpu-control", "name-corrected", "decompile-limited")
            ),
            new Spec(
                "0x0055fc5d",
                "CD3DApplication__ReadLineFromStreamLocked",
                new String[] {},
                "__cdecl",
                charPtr,
                new ParameterImpl[] {param("buffer", charPtr), param("maxChars", intType), param("stream", voidPtr)},
                "Wave624 Win32/CRT stream-tail hardening: fgets-style locked stream line reader used by CD3DApplication cardid/vendor-tweak loading. It route-locks the stream, copies bytes until newline, EOF/error, or maxChars-1, terminates the destination buffer, returns null only for empty EOF/error, and unlocks on exit. Static stream-helper evidence only; cardid runtime behavior, buffer lifetime, external file contents, and rebuild parity remain unproven.",
                tags("crt-runtime", "stream-io", "cd3dapplication")
            ),
            new Spec(
                "0x0055fe26",
                "CRT__LockRouteByAddress",
                new String[] {},
                "__cdecl",
                voidType,
                new ParameterImpl[] {param("streamOrLockAddress", voidPtr)},
                "Wave624 Win32/CRT stream-tail hardening: routes a stream-like address to either the indexed CRT lock table when it falls inside the known DAT_006533c0 range, or to the object's embedded critical section at +0x20 otherwise. Used by locked stream read/tell/seek helpers. Static lock-routing evidence only; exact CRT stream layout, thread behavior, and rebuild parity remain unproven.",
                tags("crt-runtime", "stream-lock", "lock-route")
            ),
            new Spec(
                "0x0055fe55",
                "CRT__LockRouteByIndex",
                new String[] {},
                "__cdecl",
                voidType,
                new ParameterImpl[] {param("streamIndex", intType), param("stream", voidPtr)},
                "Wave624 Win32/CRT stream-tail hardening: routes a small CRT stream index to lock table index streamIndex+0x1c, otherwise locks the stream/object critical section at +0x20. Static lock-routing evidence only; exact CRT stream layout, thread behavior, and rebuild parity remain unproven.",
                tags("crt-runtime", "stream-lock", "lock-route")
            ),
            new Spec(
                "0x0055fe78",
                "CRT__UnlockRouteByAddress",
                new String[] {},
                "__cdecl",
                voidType,
                new ParameterImpl[] {param("streamOrLockAddress", voidPtr)},
                "Wave624 Win32/CRT stream-tail hardening: unlock companion for CRT__LockRouteByAddress. It releases the indexed CRT lock table for addresses inside the DAT_006533c0 range, or the embedded critical section at +0x20 otherwise. Used by locked stream read/tell/seek helpers. Static lock-routing evidence only; exact CRT stream layout, thread behavior, and rebuild parity remain unproven.",
                tags("crt-runtime", "stream-lock", "lock-route")
            ),
            new Spec(
                "0x0055fea7",
                "CRT__UnlockRouteByIndex",
                new String[] {},
                "__cdecl",
                voidType,
                new ParameterImpl[] {param("streamIndex", intType), param("stream", voidPtr)},
                "Wave624 Win32/CRT stream-tail hardening: unlock companion for CRT__LockRouteByIndex. It releases lock table index streamIndex+0x1c for small CRT stream indexes, otherwise releases the stream/object critical section at +0x20. Static lock-routing evidence only; exact CRT stream layout, thread behavior, and rebuild parity remain unproven.",
                tags("crt-runtime", "stream-lock", "lock-route")
            ),
            new Spec(
                "0x0055feca",
                "CRT__FTellWithRouteLock",
                new String[] {},
                "__cdecl",
                intType,
                new ParameterImpl[] {param("stream", voidPtr)},
                "Wave624 Win32/CRT stream-tail hardening: locked ftell wrapper. It route-locks the stream, calls CRT__FTellAdjusted, unlocks the same stream route, and returns the adjusted file position. Current xref is CDXEngine landscape texture cache building. Static stream-helper evidence only; runtime file-position behavior, cache-file contents, and rebuild parity remain unproven.",
                tags("crt-runtime", "stream-io", "stream-lock")
            ),
            new Spec(
                "0x0055feec",
                "CRT__FTellAdjusted",
                new String[] {},
                "__cdecl",
                intType,
                new ParameterImpl[] {param("stream", voidPtr)},
                "Wave624 Win32/CRT stream-tail hardening: ftell core that lseeks the backing fd, subtracts unread buffered bytes, accounts for read/write mode flags, text-mode newline expansion, EOF/end positioning, and returns -1 with errno for invalid stream state. Xrefs include CRT__FTellWithRouteLock and CRT__FSeek_UnlockedCore. Static stream-helper evidence only; exact CRT stream layout, text translation edge cases, runtime file-position behavior, and rebuild parity remain unproven.",
                tags("crt-runtime", "stream-io")
            ),
            new Spec(
                "0x0056004d",
                "CDXTexture__AsciiToLowerInPlace",
                new String[] {},
                "__cdecl",
                charPtr,
                new ParameterImpl[] {param("pathText", charPtr)},
                "Wave624 Win32/CRT stream-tail hardening: in-place path/text lowercase helper used by CDXTexture file loading. It uses ASCII A-Z folding when locale mapping is inactive; otherwise it enters locale lock route 0x13, maps through CRT__LCMapStringA_Compat into a temporary buffer, copies the mapped text back, unlocks, frees the temporary buffer, and returns pathText. Static texture/string evidence only; exact locale behavior, runtime texture-path behavior, and rebuild parity remain unproven.",
                tags("cdxtexture", "ascii-lowercase", "locale-lock")
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
                + " missing=" + stats.missing
                + " bad=" + stats.bad
        );
    }
}
