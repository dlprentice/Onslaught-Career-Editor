//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.CharDataType;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.FunctionTag;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyMemoryManagerWave439 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final String comment;
        final String[] allowedExistingNames;
        final String[] tags;
        final ParameterImpl[] parameters;

        Spec(
                String address,
                String name,
                String callingConvention,
                DataType returnType,
                String comment,
                String[] allowedExistingNames,
                String[] tags,
                ParameterImpl[] parameters) {
            this.address = address;
            this.name = name;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.comment = comment;
            this.allowedExistingNames = allowedExistingNames;
            this.tags = tags;
            this.parameters = parameters;
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
        return toAddr(addressText);
    }

    private Function functionAtEntry(Address address) {
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

    private boolean allowedName(Spec spec, String actual) {
        if (actual.equals(spec.name)) {
            return true;
        }
        for (String allowed : spec.allowedExistingNames) {
            if (actual.equals(allowed)) {
                return true;
            }
        }
        return false;
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

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "memorymanager-wave439",
            "retail-binary-evidence"
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

    private void applySpec(Spec spec, boolean dryRun, Stats stats) {
        try {
            Address address = addr(spec.address);
            Function fn = functionAtEntry(address);
            if (fn == null) {
                stats.missing++;
                println("FAIL: " + spec.address + " " + spec.name + " Function not found");
                return;
            }

            if (!allowedName(spec, fn.getName())) {
                throw new IllegalStateException("Unexpected function name at " + spec.address + ": " + fn.getName());
            }

            boolean needsRename = !fn.getName().equals(spec.name);
            if (dryRun) {
                if (needsRename) {
                    stats.wouldRename++;
                }
                println("DRY: " + spec.address + " " + fn.getName() + " -> " + expectedSignature(spec));
                stats.skipped++;
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

            Function readBack = functionAtEntry(address);
            if (readBack == null) {
                throw new IllegalStateException("Read-back missing at " + spec.address);
            }
            if (!readBack.getName().equals(spec.name)) {
                throw new IllegalStateException("Read-back name mismatch at " + spec.address + ": " + readBack.getName());
            }
            if (!spec.comment.equals(readBack.getComment())) {
                throw new IllegalStateException("Read-back comment mismatch at " + spec.address);
            }
            Set<String> readBackTags = tagNames(readBack);
            for (String tag : spec.tags) {
                if (!readBackTags.contains(tag)) {
                    throw new IllegalStateException("Read-back missing tag " + tag + " at " + spec.address);
                }
            }

            println("OK: " + spec.address + " " + readBack.getSignature());
            stats.updated++;
            Thread.sleep(50);
        } catch (Exception ex) {
            stats.bad++;
            println("FAIL: " + spec.address + " " + spec.name + " " + ex.getMessage());
        }
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");
        println("Mode: " + (dryRun ? "dry" : "apply"));

        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);
        DataType charPtr = new PointerDataType(CharDataType.dataType);
        DataType intType = IntegerDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x004a1390",
                "CMemoryHeap__ctor",
                "__thiscall",
                voidPtr,
                "Wave439 owner/name correction: this is the CMemoryHeap constructor helper emitted immediately before CMemoryHeap__Init, not a landscape/CDXEngine helper. CDXMemoryManager__ctor calls it for default, dump, thing, and sound heap members; the body creates the retail heap mutex/HANDLE and stores it at +0x8bc. Static retail xref/decompile plus Stuart MemoryManager.cpp/CDXMemoryManager.cpp source parity evidence only; exact constructor inlining, mutex lifetime, runtime allocation behavior, and rebuild parity remain unproven.",
                new String[] { "CDXEngine__InitLandscapeCellTypeMutex" },
                tags("cmemoryheap", "constructor", "mutex", "owner-corrected", "signature-corrected", "comment-hardened", "source-parity"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x004a1570",
                "CMemoryHeap__FreeTiny",
                "__thiscall",
                intType,
                "Wave439 owner/name correction: matches CMemoryHeap::FreeTiny, not a landscape-cell free-list helper. CDXMemoryManager__Free and tag-list cleanup paths call it before falling back to CMemoryHeap__Free; the body checks mem against the tiny heap range at +0x8c0..+0x8c8 and pushes the 16-byte block onto the +0x8c4 tiny free chain. Static retail xref/decompile plus Stuart source parity evidence only; exact bool type, tiny-heap runtime behavior, and rebuild parity remain unproven.",
                new String[] { "CDXEngine__PushLandscapeCellToFreeListIfInRange" },
                tags("cmemoryheap", "tiny-heap", "free", "owner-corrected", "signature-corrected", "comment-hardened", "source-parity"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("mem", voidPtr)
                }
            ),
            new Spec(
                "0x004a1f60",
                "CMemoryHeap__OutputStats",
                "__thiscall",
                voidType,
                "Wave439 owner/name correction: matches CMemoryHeap::OutputStats(char *filename), not a global CMemoryManager dump routine. The body formats used/free/total counts, sorts 129 memory categories by per-heap size, builds data\\Memory\\<filename>, opens a CDXMemBuffer, writes the accumulated report, and closes it. Static retail string/decompile plus Stuart source parity evidence only; exact local buffer layout, file I/O runtime behavior, and rebuild parity remain unproven.",
                new String[] { "CMemoryManager__DumpStatsToFile" },
                tags("cmemoryheap", "stats", "file-output", "owner-corrected", "signature-corrected", "comment-hardened", "source-parity"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("filename", charPtr)
                }
            ),
            new Spec(
                "0x004a2190",
                "CMemoryHeap__PrintStats",
                "__thiscall",
                voidType,
                "Wave439 owner/name correction: matches CMemoryHeap::PrintStats, not CDXEngine landscape rendering. CDXMemoryManager__PrintStats selects the default or thing heap and calls this body; it draws used/free/total counts, small-block bucket pairs, and sorted per-type heap statistics through the debug font path. Static retail font/string/decompile plus Stuart source parity evidence only; exact on-screen layout, runtime debug-overlay behavior, and rebuild parity remain unproven.",
                new String[] { "CDXEngine__RenderLandscapeAllocatorStats" },
                tags("cmemoryheap", "stats", "debug-font", "owner-corrected", "signature-corrected", "comment-hardened", "source-parity"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x004a2460",
                "CMemoryHeap__LogStats",
                "__thiscall",
                voidType,
                "Wave439 owner/name correction: matches CMemoryHeap::LogStats, not a global CMemoryManager dump routine. CMemoryHeap__Alloc calls it on out-of-memory diagnostics and CDXMemoryManager__LogDebugStats calls it for the default, dump, and thing heaps; the body logs used/free/total counts and nonzero per-type byte/block counts. Static retail xref/string/decompile plus Stuart source parity evidence only; exact log sink behavior and rebuild parity remain unproven.",
                new String[] { "CMemoryManager__DumpStats" },
                tags("cmemoryheap", "stats", "debug-log", "owner-corrected", "signature-corrected", "comment-hardened", "source-parity"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x004a2660",
                "CMemoryHeap__DumpMap",
                "__thiscall",
                voidType,
                "Wave439 owner/name correction: matches CMemoryHeap::DumpMap(CMEMBUFFER *mb, int heapno), not a generic heap-block dump. CMemoryManager__DumpMemory calls it for each heap; the body counts non-DUMPTEMP blocks, writes heap header/size/block count records, then emits block validity, size, address, type, free-state, and fallback filename/line fields. Static retail string/decompile plus Stuart source parity evidence only; exact CMEMBUFFER type, file format consumers, runtime dump behavior, and rebuild parity remain unproven.",
                new String[] { "CMemoryManager__DumpHeapBlocks" },
                tags("cmemoryheap", "dump-map", "memory-dump", "owner-corrected", "signature-corrected", "comment-hardened", "source-parity"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("mem_buffer", voidPtr),
                    param("heap_index", intType)
                }
            ),
            new Spec(
                "0x004a2a20",
                "CMemoryManager__FlagAsBaseSet",
                "__thiscall",
                voidType,
                "Wave439 name/signature correction: matches CMemoryManager::FlagAsBaseSet with CMemoryHeap::FlagAsBaseSet logic inlined. CLTShell initialization reaches this after core resources load; the body walks the manager heap list and sets the CMemoryBlock base-set bit on each currently allocated block. Static retail xref/decompile plus Stuart source parity evidence only; exact base-set debug workflow, runtime memory-leak behavior, and rebuild parity remain unproven.",
                new String[] { "CMemoryManager__MarkAllocatedBlocksDebug" },
                tags("cmemorymanager", "base-set", "debug-memory", "renamed", "signature-corrected", "comment-hardened", "source-parity"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x004a2a80",
                "CMemoryManager__DumpMemory",
                "__thiscall",
                voidType,
                "Wave439 name/signature correction: matches CMemoryManager::DumpMemory(char *trace_name). The body guards against recursive dumps, writes MemoryDumps\\dump<N>.mem through CDXMemBuffer, emits trace name, memory-type names, heap count, each heap map via CMemoryHeap__DumpMap, memory tags, then increments and persists trace.no. Static retail string/xref/decompile plus Stuart source parity evidence only; runtime dump files, exact tag structure, and rebuild parity remain unproven.",
                new String[] { "CMemoryManager__DumpMemoryReport" },
                tags("cmemorymanager", "memory-dump", "renamed", "signature-corrected", "comment-hardened", "source-parity"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("trace_name", charPtr)
                }
            ),
            new Spec(
                "0x004a2ff0",
                "CMemoryBlock__SetBaseSet",
                "__thiscall",
                voidType,
                "Wave439 owner/name correction: matches the CMemoryBlock::SetBaseSet(bool) header helper that toggles bit 1 in the block size/flags dword, not a CMemoryManager routine. CMemoryHeap__Alloc calls it while initializing allocated blocks. Static retail bit-mask/decompile plus Stuart MemoryManager.h source parity evidence only; exact CMemoryBlock type recovery and runtime debug-base-set behavior remain unproven.",
                new String[] { "CMemoryManager__SetBlockFlag" },
                tags("cmemoryblock", "base-set", "owner-corrected", "signature-corrected", "comment-hardened", "source-parity"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("base_set", intType)
                }
            ),
            new Spec(
                "0x00548d70",
                "CDXMemoryManager__ctor",
                "__thiscall",
                voidPtr,
                "Wave439 owner/name correction: matches CDXMemoryManager::CDXMemoryManager, not CDXEngine landscape setup. The body clears base CMemoryManager fields, constructs the four embedded CMemoryHeap members through CMemoryHeap__ctor, points all 129 type slots at the default heap, and copies memory-type names/limits from the source-parity gMemTypeData table. Static retail decompile plus Stuart CDXMemoryManager.cpp source parity evidence only; exact compiler constructor/EH layout and rebuild parity remain unproven.",
                new String[] { "CDXEngine__InitLandscapeCellTypeTables" },
                tags("cdxmemorymanager", "constructor", "owner-corrected", "signature-corrected", "comment-hardened", "source-parity"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x00549220",
                "CDXMemoryManager__Free",
                "__thiscall",
                voidType,
                "Wave439 owner/name correction: matches CDXMemoryManager::Free(void *mem), not OID object freeing. The body ignores null, tries tiny-free on the default and thing heaps, then derives the CMemoryBlock header from mem-0x10 and dispatches to the type-selected CMemoryHeap__Free. Static retail xref/decompile plus Stuart CDXMemoryManager.cpp source parity evidence only; exact object-delete callsite ownership, runtime free behavior, and rebuild parity remain unproven.",
                new String[] { "OID__FreeObject" },
                tags("cdxmemorymanager", "free", "owner-corrected", "signature-corrected", "comment-hardened", "source-parity"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("mem", voidPtr)
                }
            ),
            new Spec(
                "0x00549290",
                "CDXMemoryManager__PrintStats",
                "__thiscall",
                voidType,
                "Wave439 owner/name correction: matches the CDXMemoryManager::PrintStats heap selector, not CDXEngine active-cell processing. The body selects the default or thing heap based on the retail heapnr byte and forwards to CMemoryHeap__PrintStats. Static retail xref/decompile plus Stuart CDXMemoryManager.cpp source parity evidence only; exact heapnr coverage and runtime debug-overlay behavior remain unproven.",
                new String[] { "CDXEngine__ProcessActiveLandscapeCellBucket" },
                tags("cdxmemorymanager", "stats", "owner-corrected", "signature-corrected", "comment-hardened", "source-parity"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x005492b0",
                "CDXMemoryManager__OutputStats",
                "__thiscall",
                voidType,
                "Wave439 owner/name correction: matches CDXMemoryManager::OutputStats(char *filename), not CDXEngine memory stats dumping. The wrapper forwards the requested filename to the default heap CMemoryHeap__OutputStats body. Static retail xref/decompile plus Stuart CDXMemoryManager.cpp source parity evidence only; exact file output behavior and rebuild parity remain unproven.",
                new String[] { "CDXEngine__DumpMemoryStats" },
                tags("cdxmemorymanager", "stats", "file-output", "owner-corrected", "signature-corrected", "comment-hardened", "source-parity"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("filename", charPtr)
                }
            )
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }

        println("SUMMARY updated=" + stats.updated
            + " skipped=" + stats.skipped
            + " created=0"
            + " would_create=0"
            + " renamed=" + stats.renamed
            + " would_rename=" + stats.wouldRename
            + " missing=" + stats.missing
            + " bad=" + stats.bad);

        if (stats.missing != 0 || stats.bad != 0) {
            throw new IllegalStateException("Wave439 apply failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
