//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
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

public class ApplySortMemoryCrtWave623 extends GhidraScript {
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
            "sort-memory-crt-wave623",
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
        DataType shortPtr = new PointerDataType(ShortDataType.dataType);
        DataType intType = IntegerDataType.dataType;
        DataType uintType = UnsignedIntegerDataType.dataType;
        DataType doubleType = DoubleDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x0055e7ae",
                "Sort__QuickSortGeneric",
                new String[] {},
                "__cdecl",
                voidType,
                new ParameterImpl[] {param("base", voidPtr), param("count", uintType), param("elemSize", uintType), param("compareFn", voidPtr)},
                "Wave623 sort/memory/CRT hardening: qsort-style generic sorter over base/count/elemSize using compareFn, stack worklists for deferred partitions, median-ish pivot swap, and Sort__ShortSortGeneric for partitions of eight or fewer elements. Xrefs include display-device sorting, render overlay candidates, texture symbol-table finalization, and world-file enumeration. Static helper evidence only; exact CRT version, comparator contract, runtime ordering behavior, and rebuild parity remain unproven.",
                tags("sort-generic", "crt-runtime")
            ),
            new Spec(
                "0x0055e902",
                "Sort__ShortSortGeneric",
                new String[] {"CDXEngine__InsertionSortGeneric"},
                "__cdecl",
                voidType,
                new ParameterImpl[] {param("lo", voidPtr), param("hi", voidPtr), param("elemSize", uintType), param("compareFn", voidPtr)},
                "Wave623 sort/memory/CRT hardening: small-partition qsort helper called by Sort__QuickSortGeneric; scans from lo through hi, selects the compareFn-greater element, swaps it to hi with Memory__SwapByteRange, then shrinks hi by elemSize. The old CDXEngine owner/insertion wording was too narrow and algorithmically misleading. Static helper evidence only; exact CRT version, comparator ordering contract, runtime ordering behavior, and rebuild parity remain unproven.",
                tags("sort-generic", "name-corrected", "crt-runtime")
            ),
            new Spec(
                "0x0055e950",
                "Memory__SwapByteRange",
                new String[] {},
                "__cdecl",
                voidType,
                new ParameterImpl[] {param("lhs", voidPtr), param("rhs", voidPtr), param("byteCount", intType)},
                "Wave623 sort/memory/CRT hardening: byte-swap helper exchanges byteCount bytes between lhs and rhs when the pointers differ. Current xrefs are the generic qsort and short-sort helpers. Static helper evidence only; aliasing edge cases, runtime sorter behavior, exact CRT identity, and rebuild parity remain unproven.",
                tags("sort-generic", "byte-swap")
            ),
            new Spec(
                "0x0055eb00",
                "CRT__WcsNcpyZeroPad",
                new String[] {},
                "__cdecl",
                shortPtr,
                new ParameterImpl[] {param("destWide", shortPtr), param("srcWide", shortPtr), param("maxWideChars", intType)},
                "Wave623 sort/memory/CRT hardening: wide strncpy-style helper copies up to maxWideChars 16-bit units from srcWide to destWide, stops at the first terminator, then zero-pads the remaining destination units in word-pair and tail loops. Xrefs include text wrapping, save-list rendering, and virtual keyboard rendering. Static wide-string evidence only; exact CRT identity, buffer safety, runtime UI text behavior, and rebuild parity remain unproven.",
                tags("crt-runtime", "wide-string")
            ),
            new Spec(
                "0x0055eb3d",
                "CRT__RoundToIntegerRespectingControlWord",
                new String[] {},
                "__cdecl",
                doubleType,
                new ParameterImpl[] {param("value", doubleType)},
                "Wave623 sort/memory/CRT hardening: rounds value through the current FPU control-word path, checks non-finite classifications, uses FRNDINT for finite inputs, and routes inexact/domain cases through CRT floating-point handlers. Xrefs include world occupancy, shadow-volume, squad, and billboard-strip coordinate rounding. Static math-helper evidence only; exact CRT identity, full exception semantics, runtime math behavior, and rebuild parity remain unproven.",
                tags("crt-runtime", "fpu-control", "math-helper")
            ),
            new Spec(
                "0x0055ec4a",
                "CRT__HeapAllocBase",
                new String[] {},
                "__cdecl",
                voidPtr,
                new ParameterImpl[] {param("byteCount", uintType)},
                "Wave623 sort/memory/CRT hardening: CRT allocation base helper routes through small-block heap modes under lock 9 when eligible, normalizes zero/aligned sizes, and falls back to HeapAlloc from DAT_009d35e4. Direct caller is __nh_malloc. Static heap-helper evidence only; allocator provenance, failure policy, runtime heap state, and rebuild parity remain unproven.",
                tags("crt-runtime", "heap-helper")
            ),
            new Spec(
                "0x0055ed50",
                "CRT__MemMoveOverlapSafe",
                new String[] {},
                "__cdecl",
                voidPtr,
                new ParameterImpl[] {param("dest", voidPtr), param("src", voidPtr), param("byteCount", uintType)},
                "Wave623 sort/memory/CRT hardening: memmove-style copy helper detects overlapping src-before-dest ranges and copies backward; otherwise it copies forward with alignment-aware dword loops and byte tails, returning dest. Xrefs span CRT heap/object construction, texture parsing, string shifting, and Ogg PCM reads. Static memory-helper evidence only; exact CRT identity, all alignment edge cases, runtime behavior, and rebuild parity remain unproven.",
                tags("crt-runtime", "memory-copy")
            ),
            new Spec(
                "0x0055f085",
                "CRT__FreeBase",
                new String[] {},
                "__cdecl",
                voidType,
                new ParameterImpl[] {param("ptr", voidPtr)},
                "Wave623 sort/memory/CRT hardening: CRT free base helper ignores null, attempts small-block heap release paths under lock 9 for heap modes 2/3, then falls back to HeapFree from DAT_009d35e4 when no small-block owner is found. Xrefs span type_info cleanup, locale/environment buffers, CDXTexture decode state, and memory-manager shutdown. Static heap-helper evidence only; allocator provenance, runtime heap state, ownership safety, and rebuild parity remain unproven.",
                tags("crt-runtime", "heap-helper")
            ),
            new Spec(
                "0x0055f19d",
                "CRT__FWriteCore",
                new String[] {},
                "__cdecl",
                uintType,
                new ParameterImpl[] {param("buffer", voidPtr), param("elemSize", uintType), param("elemCount", uintType), param("stream", voidPtr)},
                "Wave623 sort/memory/CRT hardening: core fwrite helper computes elemSize*elemCount, writes through stream buffer space when available, flushes pending write segments, falls back to fd text-mode writes, sets error flags on short/failed writes, and returns completed element count. Static stream-helper evidence only; exact CRT identity, text-mode translation details, runtime file I/O behavior, and rebuild parity remain unproven.",
                tags("crt-runtime", "stream-io")
            ),
            new Spec(
                "0x0055f2e8",
                "CRT__WcsCmp",
                new String[] {},
                "__cdecl",
                intType,
                new ParameterImpl[] {param("lhsWide", shortPtr), param("rhsWide", shortPtr)},
                "Wave623 sort/memory/CRT hardening: wide strcmp-style helper compares 16-bit code units until a mismatch or terminator, then returns -1, 0, or 1 for lexical ordering. Xrefs include message-box portrait selection, save-file enumeration, and virtual-keyboard transition handling. Static wide-string evidence only; exact CRT identity, locale/collation behavior, runtime UI text behavior, and rebuild parity remain unproven.",
                tags("crt-runtime", "wide-string")
            ),
            new Spec(
                "0x0055f39d",
                "CRT__AcosCoreWithFpuGuards",
                new String[] {},
                "__cdecl",
                doubleType,
                new ParameterImpl[] {param("lowWord", intType), param("highWord", uintType)},
                "Wave623 sort/memory/CRT hardening: acos core receives split double words from CRT__AcosClassifyAndDispatch, handles FPU-control adjustment, in-range fpatan/sqrt evaluation, +/-1 boundary cases, and CRT math error/exit paths. Static math-helper evidence only; exact CRT identity, all domain/exception semantics, runtime math behavior, and rebuild parity remain unproven.",
                tags("crt-runtime", "math-helper", "fpu-control")
            ),
            new Spec(
                "0x0055f506",
                "CRT__FReadCore",
                new String[] {},
                "__cdecl",
                uintType,
                new ParameterImpl[] {param("buffer", voidPtr), param("elemSize", uintType), param("elemCount", uintType), param("stream", voidPtr)},
                "Wave623 sort/memory/CRT hardening: core fread helper computes elemSize*elemCount, drains buffered bytes when present, uses byte-at-a-time refill for small requests, otherwise reads larger aligned chunks through the locked fd text-mode path, and sets EOF/error stream flags. Static stream-helper evidence only; exact CRT identity, text-mode translation details, runtime file I/O behavior, and rebuild parity remain unproven.",
                tags("crt-runtime", "stream-io")
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
