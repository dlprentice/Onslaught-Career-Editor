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

public class ApplyMemoryManagerWave438 extends GhidraScript {
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
            "memorymanager-wave438",
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
        DataType voidPtrPtr = new PointerDataType(voidPtr);
        DataType charPtr = new PointerDataType(CharDataType.dataType);
        DataType intType = IntegerDataType.dataType;
        DataType uintType = UnsignedIntegerDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x004a13b0",
                "CMemoryHeap__Init",
                "__thiscall",
                intType,
                "Wave438 owner/signature correction: this source-adjacent body is CMemoryHeap::Init, not the global CMemoryManager. MEM_MANAGER__Init calls it four times to seed default, dump, sound, and thing heaps; the body clears heap stats/free lists, rounds heap_size, copies the heap name, links into DAT_009c3df0, mallocs/aligned the base block with a 0x4f69ea21 header, and optionally builds the 16-byte tiny heap free chain. Static retail plus Stuart source parity evidence only; exact CMemoryHeap field names/layout, runtime allocator behavior, and rebuild parity remain unproven.",
                new String[] { "CMemoryManager__Init" },
                tags("cmemoryheap", "allocator-init", "owner-corrected", "signature-corrected", "comment-hardened", "source-parity"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("heap_size", uintType),
                    param("tiny_heap_size", uintType),
                    param("name", charPtr),
                    param("support_small_allocs", intType)
                }
            ),
            new Spec(
                "0x004a15a0",
                "CMemoryHeap__ReallocTiny",
                "__thiscall",
                intType,
                "Wave438 owner/signature correction: matches CMemoryHeap::ReallocTiny and is reached from CPolyBucket__ReallocFromPool. The body checks mem against the tiny heap range at +0x8c0..+0x8c8, copies the 16-byte tiny payload to stack, returns the old tiny block to the +0x8c4 free chain, allocates replacement storage through CMemoryHeap__Alloc, copies min(new_size, 16), and stores the result through out_result. Static retail plus Stuart source parity evidence only; exact tiny-heap ownership, runtime allocation behavior, and rebuild parity remain unproven.",
                new String[] { "CMemoryManager__ReallocFromPool" },
                tags("cmemoryheap", "tiny-heap", "owner-corrected", "signature-corrected", "comment-hardened", "source-parity"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("mem", voidPtr),
                    param("new_size", uintType),
                    param("out_result", voidPtrPtr)
                }
            ),
            new Spec(
                "0x004a1640",
                "CMemoryHeap__Cleanup",
                "__thiscall",
                voidType,
                "Wave438 owner/signature correction: matches CMemoryHeap::Cleanup(bool needs_mutex). CMemoryHeap__Alloc, CMemoryHeap__SetMerge, and MEM_MANAGER__Cleanup call it; the body optionally waits on the heap mutex at +0x8bc, clears the 16 small-free buckets and main free list, walks heap blocks from mpMem, coalesces adjacent free blocks, and rebuilds small or size-sorted free lists before releasing the mutex. Static retail plus Stuart source parity evidence only; exact block-list invariants, runtime allocator behavior, and rebuild parity remain unproven.",
                new String[] { "CMemoryManager__Coalesce" },
                tags("cmemoryheap", "cleanup-coalesce", "owner-corrected", "signature-corrected", "comment-hardened", "source-parity"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("needs_mutex", intType)
                }
            ),
            new Spec(
                "0x004a17b0",
                "CMemoryHeap__Shutdown",
                "__fastcall",
                voidType,
                "Wave438 owner/signature correction: matches CMemoryHeap::Shutdown with Steam-retail mutex cleanup added. CDXEngine__ResetLandscapeCellManager calls it; the body unlinks this heap from the global DAT_009c3df0 heap list, frees the aligned base allocation, releases the mutex handle stored at +0x8bc, and zeros that field. Static retail plus Stuart source parity evidence only; exact mutex lifetime, heap-list ownership, runtime allocator behavior, and rebuild parity remain unproven.",
                new String[] { "CMemoryManager__UnlinkAndReleaseMutex" },
                tags("cmemoryheap", "shutdown", "owner-corrected", "signature-corrected", "comment-hardened", "source-parity"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x004a1810",
                "CMemoryHeap__Alloc",
                "__thiscall",
                voidPtr,
                "Wave438 owner/signature correction: matches CMemoryHeap::Alloc. The body guards with the heap mutex at +0x8bc, rounds size to 16 bytes, tries the tiny heap and small-block buckets, pulls from the main free list, retries after CMemoryHeap__Cleanup on pressure, emits Out of memory diagnostics on failure, then splits or consumes a free block and updates per-type usage counters. Static retail plus Stuart source parity evidence only; exact CMemoryBlock field names/layout, runtime allocator behavior, and rebuild parity remain unproven.",
                new String[] { "CMemoryManager__Alloc" },
                tags("cmemoryheap", "allocator", "owner-corrected", "signature-corrected", "comment-hardened", "source-parity"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("size", uintType),
                    param("memory_type", intType),
                    param("filename", charPtr),
                    param("line", uintType)
                }
            ),
            new Spec(
                "0x004a1c30",
                "CMemoryHeap__ReleaseMutexUnwindCleanup",
                "__fastcall",
                voidType,
                "Wave438 name/signature correction: this is the EH unwind cleanup helper referenced from the allocator/free unwind records at 0x005d3540 and 0x005d3560. The body releases the HANDLE stored through mutex_handle_ptr and is not a source-level CMemoryHeap method body. Static retail exception/unwind evidence only; exact compiler EH ownership, mutex lifetime, and runtime exception behavior remain unproven.",
                new String[] { "CMemoryManager__ReleaseMutexCallback" },
                tags("cmemoryheap", "eh-cleanup", "mutex-release", "renamed", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("mutex_handle_ptr", voidPtrPtr)
                }
            ),
            new Spec(
                "0x004a1c40",
                "CMemoryHeap__ReAlloc",
                "__thiscall",
                voidPtr,
                "Wave438 owner/signature correction: matches CMemoryHeap::ReAlloc. CPolyBucket__ReallocFromPool calls it; the body allocates a replacement block with the old block's memory type, copies min(old_size, new_size) bytes from block+0x10, frees the old block through CMemoryHeap__Free, and returns the new allocation. Static retail plus Stuart source parity evidence only; exact debug filename handling, runtime allocator behavior, and rebuild parity remain unproven.",
                new String[] { "CMemoryManager__Realloc" },
                tags("cmemoryheap", "realloc", "owner-corrected", "signature-corrected", "comment-hardened", "source-parity"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("block", voidPtr),
                    param("new_size", uintType)
                }
            ),
            new Spec(
                "0x004a1ca0",
                "CMemoryHeap__Free",
                "__thiscall",
                voidType,
                "Wave438 owner/signature correction: matches CMemoryHeap::Free. OID__FreeObject and CDXEngine landscape-cell cleanup call it; the body waits on the heap mutex, updates free/used/per-type counters from the CMemoryBlock header, clears the used/base-set flag bits, delegates reinsertion to CMemoryHeap__AddToFreeList, and releases the mutex. Static retail plus Stuart source parity evidence only; exact CMemoryBlock layout, runtime allocator behavior, and rebuild parity remain unproven.",
                new String[] { "CMemoryManager__Free" },
                tags("cmemoryheap", "free", "owner-corrected", "signature-corrected", "comment-hardened", "source-parity"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("block", voidPtr)
                }
            ),
            new Spec(
                "0x004a1d60",
                "CMemoryHeap__AddToFreeList",
                "__thiscall",
                voidType,
                "Wave438 owner/signature correction: matches CMemoryHeap::AddToFreeList. CMemoryHeap__Free and split-allocation paths call it; the body places small blocks under 0x100 bytes into the 16 bucket list when supported, otherwise optionally coalesces adjacent main-list blocks when mMerge is set, then reinserts by block size. Static retail plus Stuart source parity evidence only; exact free-list ordering invariants, runtime allocator behavior, and rebuild parity remain unproven.",
                new String[] { "CMemoryManager__AddToFreeList" },
                tags("cmemoryheap", "free-list", "owner-corrected", "signature-corrected", "comment-hardened", "source-parity"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("block", voidPtr)
                }
            ),
            new Spec(
                "0x004a1ea0",
                "CMemoryHeap__SetMerge",
                "__thiscall",
                voidType,
                "Wave438 owner/signature correction: matches CMemoryHeap::SetMerge, not a generic enable-coalescing helper. CLTShell shutdown and raw callsites reach it; when enabling merge from a disabled state, the body calls CMemoryHeap__Cleanup, then selection-sorts the main free list by block size before storing the merge flag at +0x874. Static retail plus Stuart source parity evidence only; exact shutdown caller ownership, free-list ordering behavior, and rebuild parity remain unproven.",
                new String[] { "CMemoryManager__EnableCoalescing" },
                tags("cmemoryheap", "set-merge", "owner-corrected", "signature-corrected", "comment-hardened", "source-parity"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("merge_enabled", intType)
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
            throw new IllegalStateException("Wave438 apply failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
