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

public class ApplyCrtSmallBlockHeapWave634 extends GhidraScript {
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
            "crt-small-block-heap-wave634",
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
        DataType voidPtrPtr = new PointerDataType(voidPtr);
        DataType voidType = VoidDataType.dataType;
        DataType intType = IntegerDataType.dataType;
        DataType uintType = UnsignedIntegerDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x00566294",
                "CRT__InitializeHeapSubsystem",
                new String[] {},
                "__cdecl",
                intType,
                new ParameterImpl[] {param("useSerializedHeap", intType)},
                false,
                "Wave634 CRT small-block heap hardening: heap bootstrap called from entry. It creates the process CRT heap, records the strategy from CRT__SelectHeapStrategy, initializes strategy 3 through CRT__InitSmallBlockHeap or strategy 2 through CRT__SbHeapCreateRegionPool, and destroys the heap on initialization failure. Static heap bootstrap evidence only; exact MSVC CRT version, heap strategy enum names, runtime allocation behavior, and rebuild parity remain unproven.",
                tags("crt-runtime", "heap", "heap-bootstrap")
            ),
            new Spec(
                "0x005662f1",
                "CRT__InitSmallBlockHeap",
                new String[] {},
                "__cdecl",
                intType,
                new ParameterImpl[] {param("smallBlockByteLimit", intType)},
                false,
                "Wave634 CRT small-block heap hardening: initializes the strategy 3 small-block heap table. It allocates initial 0x140-byte region-table storage, resets the region count and scan cursor, stores the caller byte limit, and seeds region-table capacity 0x10. Static table-initialization evidence only; exact table layout, heap strategy identity, runtime allocation behavior, and rebuild parity remain unproven.",
                tags("crt-runtime", "heap", "small-block-heap", "heap-bootstrap")
            ),
            new Spec(
                "0x00566339",
                "CRT__FindSmallBlockHeapEntryForPtr",
                new String[] {},
                "__cdecl",
                voidPtr,
                new ParameterImpl[] {param("userPtr", voidPtr)},
                false,
                "Wave634 CRT small-block heap hardening: searches the strategy 3 region table for a user pointer. It walks 0x14-byte region entries and returns the first entry whose reserved 0x100000-byte address range contains userPtr, otherwise null. Static pointer-range evidence only; exact region-entry layout, ownership semantics, and runtime heap behavior remain unproven.",
                tags("crt-runtime", "heap", "small-block-heap", "region-table")
            ),
            new Spec(
                "0x00566364",
                "CRT__SmallBlockHeapFreeBlock",
                new String[] {},
                "__cdecl",
                voidType,
                new ParameterImpl[] {param("heapEntry", voidPtr), param("userPtr", voidPtr)},
                false,
                "Wave634 CRT small-block heap hardening: frees a strategy 3 small-block allocation. It reads the inline chunk header before userPtr, coalesces neighboring free chunks, updates per-page free-list links plus low/high bucket bitmaps and counters, and can decommit or release a fully empty cached region through VirtualFree/HeapFree. Static allocator evidence only; exact chunk/header layout, concurrency behavior, and rebuild parity remain unproven.",
                tags("crt-runtime", "heap", "small-block-heap", "free")
            ),
            new Spec(
                "0x0056668d",
                "CRT__SbHeapAllocBlock",
                new String[] {},
                "__cdecl",
                voidPtr,
                new ParameterImpl[] {param("byteCount", uintType)},
                false,
                "Wave634 CRT small-block heap hardening: allocates from the strategy 3 small-block heap. It aligns the requested size with allocator headers, scans low/high bucket bitmaps across region entries, grows the region table or commits a page when needed, splits the chosen free chunk, updates bitmaps and free-list links, and returns the user pointer. Static allocation evidence only; exact small-block layout, failure policy, and runtime heap behavior remain unproven.",
                tags("crt-runtime", "heap", "small-block-heap", "allocation")
            ),
            new Spec(
                "0x00566996",
                "CRT__SbHeapGrowRegionTable",
                new String[] {},
                "__cdecl",
                voidPtr,
                new ParameterImpl[] {},
                false,
                "Wave634 CRT small-block heap hardening: grows or appends a strategy 3 region-table entry. It reallocates the table when count equals capacity, allocates per-region metadata, reserves a 0x100000-byte virtual address range, initializes entry bitmaps/counters, records the metadata pointer, and returns the new entry pointer or null. Static region-table evidence only; exact entry layout, reservation policy, and runtime heap behavior remain unproven.",
                tags("crt-runtime", "heap", "small-block-heap", "region-table")
            ),
            new Spec(
                "0x00566a47",
                "CRT__SbHeapCommitRegion",
                new String[] {},
                "__cdecl",
                intType,
                new ParameterImpl[] {param("heapEntry", voidPtr)},
                false,
                "Wave634 CRT small-block heap hardening: commits a page inside a strategy 3 reserved region. It finds the first uncommitted page bit, initializes 64 bucket list heads, commits an 0x8000-byte page with VirtualAlloc, seeds 0xff0-byte free chunks, updates page bitmaps/counters, and returns the committed page index or -1. Static page-commit evidence only; exact page metadata layout and runtime heap behavior remain unproven.",
                tags("crt-runtime", "heap", "small-block-heap", "virtualalloc")
            ),
            new Spec(
                "0x00566b42",
                "CRT__SmallBlockHeapReallocInPlace",
                new String[] {},
                "__cdecl",
                intType,
                new ParameterImpl[] {param("heapEntry", voidPtr), param("userPtr", voidPtr), param("byteCount", uintType)},
                false,
                "Wave634 CRT small-block heap hardening: attempts an in-place strategy 3 small-block realloc. It expands by consuming the following free chunk when possible, shrinks by splitting a trailing free chunk, updates inline headers and free-list bucket bitmaps, and returns 1 only when the original pointer can remain valid. Static realloc evidence only; exact chunk layout, copy fallback behavior, and runtime heap behavior remain unproven.",
                tags("crt-runtime", "heap", "small-block-heap", "realloc")
            ),
            new Spec(
                "0x00566e38",
                "CRT__SbHeapCreateRegionPool",
                new String[] {},
                "__cdecl",
                voidPtr,
                new ParameterImpl[] {},
                false,
                "Wave634 CRT small-block heap hardening: creates or initializes a strategy 2 deferred small-block region pool. It uses the static sentinel region or heap-allocates a new 0x2020-byte header, reserves a 0x400000-byte address range, commits the first 0x10000 bytes, links the region list, initializes 0x400 page records, and returns the region header or null. Static region-pool evidence only; exact strategy 2 policy, list layout, and runtime heap behavior remain unproven.",
                tags("crt-runtime", "heap", "small-block-heap", "region-pool")
            ),
            new Spec(
                "0x00566f7c",
                "CRT__SmallBlockHeapReleaseRegion",
                new String[] {},
                "__cdecl",
                voidType,
                new ParameterImpl[] {param("regionHeader", voidPtr)},
                false,
                "Wave634 CRT small-block heap hardening: releases a strategy 2 region-pool header. It frees the reserved address range, updates the current-region cursor, unlinks and heap-frees non-sentinel region headers, or resets the static sentinel state when the sentinel is released. Static region-lifetime evidence only; exact list ownership, sentinel policy, and runtime heap behavior remain unproven.",
                tags("crt-runtime", "heap", "small-block-heap", "region-pool")
            ),
            new Spec(
                "0x00566fd2",
                "CRT__SmallBlockHeapDecommitPages",
                new String[] {},
                "__cdecl",
                voidType,
                new ParameterImpl[] {param("pageCount", intType)},
                false,
                "Wave634 CRT small-block heap hardening: decommits up to pageCount free pages from strategy 2 region pools. It walks region headers, finds page records with free count 0xf0, calls VirtualFree with MEM_DECOMMIT, updates the global decommit counter and free-page cursor, and releases a region when all page records are empty. Static page-decommit evidence only; exact page-record layout and runtime heap behavior remain unproven.",
                tags("crt-runtime", "heap", "small-block-heap", "virtualfree")
            ),
            new Spec(
                "0x00567094",
                "CRT__SmallBlockHeapLocateBlock",
                new String[] {},
                "__cdecl",
                voidPtr,
                new ParameterImpl[] {param("userPtr", voidPtr), param("outRegionHeader", voidPtrPtr), param("outPageBase", voidPtrPtr)},
                false,
                "Wave634 CRT small-block heap hardening: locates a strategy 2 deferred small-block allocation. It walks the region list, validates that userPtr falls inside a region, enforces 16-byte alignment and page-offset constraints, writes the owning region header and page base to caller outputs, and returns the page-local chunk header pointer or null. Static locator evidence only; exact chunk/page layout and runtime heap behavior remain unproven.",
                tags("crt-runtime", "heap", "small-block-heap", "region-pool")
            ),
            new Spec(
                "0x005670eb",
                "CRT__SbHeapReleasePageBlock",
                new String[] {},
                "__cdecl",
                voidType,
                new ParameterImpl[] {param("regionHeader", voidPtr), param("pageBase", voidPtr), param("chunkHeader", voidPtr)},
                false,
                "Wave634 CRT small-block heap hardening: releases a strategy 2 page-local small-block chunk. It restores the page free-unit count from the chunk size byte, clears that byte, marks the page record free, increments the global decommit threshold counter, and triggers a bounded decommit sweep when the threshold reaches 0x20. Static page-free evidence only; exact unit accounting and runtime heap behavior remain unproven.",
                tags("crt-runtime", "heap", "small-block-heap", "free")
            ),
            new Spec(
                "0x00567130",
                "CRT__SbHeapAllocDeferredBlock",
                new String[] {},
                "__cdecl",
                voidPtr,
                new ParameterImpl[] {param("requestedUnits", uintType)},
                false,
                "Wave634 CRT small-block heap hardening: allocates a strategy 2 deferred small-block chunk by unit count. It scans from the current region/page cursor and wraps the region list, allocates a new region pool or commits more pages when needed, delegates page-local chunk selection to CRT__SbHeapAllocChunkFromRegion, updates page free counters/cursors, and returns the user pointer or null. Static deferred-allocation evidence only; exact unit size and runtime heap behavior remain unproven.",
                tags("crt-runtime", "heap", "small-block-heap", "allocation")
            ),
            new Spec(
                "0x00567338",
                "CRT__SbHeapAllocChunkFromRegion",
                new String[] {"CRT__SbHeapAllocChunkFromRegion_00567338"},
                "__cdecl",
                voidPtr,
                new ParameterImpl[] {param("pageHeader", voidPtr), param("freeUnits", uintType), param("requestedUnits", uintType)},
                false,
                "Wave634 CRT small-block heap hardening: allocates a requested unit count from one page-local strategy 2 byte map. It uses the page search cursor and residual free count, scans byte-sized chunk markers for a contiguous free run, updates the cursor when residual free space remains, stores the requested unit byte, and returns the derived user pointer. Static page-local allocator evidence only; exact byte-map layout and runtime heap behavior remain unproven.",
                tags("crt-runtime", "heap", "small-block-heap", "allocation", "name-corrected")
            ),
            new Spec(
                "0x0056745c",
                "CRT__SbHeapResizeChunkInRegion",
                new String[] {"CRT__SbHeapResizeChunkInRegion_0056745c"},
                "__cdecl",
                intType,
                new ParameterImpl[] {param("regionHeader", voidPtr), param("pageBase", voidPtr), param("chunkHeader", voidPtr), param("requestedUnits", uintType)},
                false,
                "Wave634 CRT small-block heap hardening: resizes a page-local strategy 2 byte-map chunk in place. Shrinks reduce the stored chunk unit byte and add free units back to the page record; growth succeeds only when following bytes are free and inside the page-local limit, then updates the page cursor/free count as needed. Static page-local realloc evidence only; exact byte-map layout and runtime heap behavior remain unproven.",
                tags("crt-runtime", "heap", "small-block-heap", "realloc", "name-corrected")
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
            throw new IllegalStateException("Wave634 had missing/bad rows");
        }
    }
}
