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
import ghidra.program.model.listing.Parameter;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyCDXMemoryManagerCoreWave607 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] parameters;
        final String comment;
        final String[] allowedExistingNames;
        final String[] tags;

        Spec(
                String address,
                String name,
                String callingConvention,
                DataType returnType,
                ParameterImpl[] parameters,
                String comment,
                String[] allowedExistingNames,
                String[] tags) {
            this.address = address;
            this.name = name;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.parameters = parameters;
            this.comment = comment;
            this.allowedExistingNames = allowedExistingNames;
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
            "cdxmemorymanager-core-wave607",
            "retail-binary-evidence",
            "signature-corrected",
            "comment-hardened",
            "owner-corrected"
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

    private boolean sameDataType(DataType actual, DataType expected) {
        if (actual == null || expected == null) {
            return actual == expected;
        }
        return actual.isEquivalent(expected) || actual.getDisplayName().equals(expected.getDisplayName());
    }

    private boolean signatureMatches(Function fn, Spec spec) {
        if (!spec.callingConvention.equals(fn.getCallingConventionName())) {
            return false;
        }
        if (!sameDataType(fn.getReturnType(), spec.returnType)) {
            return false;
        }
        if (fn.getParameterCount() != spec.parameters.length) {
            return false;
        }
        for (int i = 0; i < spec.parameters.length; i++) {
            Parameter actual = fn.getParameter(i);
            ParameterImpl expected = spec.parameters[i];
            if (!actual.getName().equals(expected.getName())) {
                return false;
            }
            if (!sameDataType(actual.getDataType(), expected.getDataType())) {
                return false;
            }
        }
        return true;
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
        if (!signatureMatches(readBack, spec)) {
            throw new IllegalStateException("Read-back signature mismatch at " + spec.address + ": " + readBack.getSignature());
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
            if (!allowedName(spec, fn.getName())) {
                stats.bad++;
                println("BADNAME: " + spec.address + " actual=" + fn.getName() + " expected=" + spec.name);
                return;
            }
            boolean needsRename = !fn.getName().equals(spec.name);
            if (!needsUpdate(fn, spec)) {
                stats.skipped++;
                println("SKIP: " + spec.address + " " + expectedSignature(spec));
                return;
            }
            if (dryRun) {
                stats.skipped++;
                if (needsRename) {
                    stats.wouldRename++;
                }
                println("DRY: " + spec.address + " " + fn.getSignature() + " -> " + expectedSignature(spec));
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
            println("OK: " + spec.address + " " + expectedSignature(spec));
        } catch (Exception ex) {
            stats.bad++;
            println("BAD: " + spec.address + " " + spec.name + " " + ex.getClass().getSimpleName() + ": " + ex.getMessage());
        }
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = args == null || args.length == 0 || isDryRun(args[0]);

        DataType voidType = VoidDataType.dataType;
        DataType intType = IntegerDataType.dataType;
        DataType uintType = UnsignedIntegerDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);
        DataType charPtr = new PointerDataType(CharDataType.dataType);

        Spec[] specs = new Spec[] {
            new Spec(
                "0x00548ec0",
                "CMemoryManager__DeleteTagList_CtorUnwind",
                "__thiscall",
                voidType,
                new ParameterImpl[] { param("this", voidPtr) },
                "Wave607 memory-manager owner correction: this is not CDXEngine landscape-cell cleanup. It is the CDXMemoryManager constructor EH/unwind tag-list cleanup path: after heap-constructor cleanup stubs, the body walks CMemoryManager::mFirstTag at this+0x4, reads CMemoryTag::mNext at +0x208, frees each tag through the same default/thing tiny-free then type-selected heap-free path used by CDXMemoryManager__Free, and stores the next tag pointer. Static retail decompile/instruction evidence plus Stuart CMemoryManager destructor source parity only; exact compiler EH ownership, complete CMemoryTag layout, runtime tagging behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] { "CDXEngine__FreeLandscapeCellList_Debug" },
                tags("cmemorymanager", "tag-list", "ctor-unwind", "ret-c3")
            ),
            new Spec(
                "0x00548f90",
                "CDXMemoryManager__Init",
                "__thiscall",
                uintType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("heap_size", uintType)
                },
                "Wave607 CDXMemoryManager core hardening: RET 0x4 and CLTShell__WinMain prove ECX is global MEM_MANAGER and one stack heap_size argument. The body sets mInit, clears mDumpingMemory at this+0xc, initializes the default heap with heap_size and a 0x4b000 tiny heap, initializes dump/sound/thing heaps at offsets 0xae0/0x1c78/0x13ac, and remaps sound/sample and thing-family memory types to their specialized heaps. Static retail decompile/xref/instruction evidence plus Stuart DXMemoryManager.cpp source parity only; exact heap layouts, Xbox-only texture/VB heap paths, runtime allocation behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] { "MEM_MANAGER__Init" },
                tags("cdxmemorymanager", "init", "ret-0x4", "heap-bootstrap")
            ),
            new Spec(
                "0x005490c0",
                "CDXMemoryManager__Shutdown",
                "__thiscall",
                voidType,
                new ParameterImpl[] { param("this", voidPtr) },
                "Wave607 CDXMemoryManager core hardening: this is not CDXEngine landscape-cell manager reset. The PC retail body clears global mInit at 0x009c6334, then tail-jumps into CMemoryHeap__Shutdown for the default heap at this+0x214, matching the PC CDXMemoryManager::Shutdown source path with Xbox-only heap shutdowns absent. Static retail decompile/instruction evidence plus Stuart DXMemoryManager.cpp source parity only; exact heap teardown side effects, runtime shutdown behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] { "CDXEngine__ResetLandscapeCellManager" },
                tags("cdxmemorymanager", "shutdown", "tailcall", "default-heap")
            ),
            new Spec(
                "0x005490e0",
                "CDXMemoryManager__Alloc",
                "__thiscall",
                voidPtr,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("size", uintType),
                    param("mem_type", intType),
                    param("source_file", charPtr),
                    param("line", uintType)
                },
                "Wave607 CDXMemoryManager core hardening: this is not OID object allocation. RET 0x10 and 1384 xrefs identify the global allocation fan-out; the body dispatches size, mem_type, source_file, and line to the type-selected heap pointer at this+0x10 + mem_type*4. On allocation failure it maps default/dump/thing/sound heap pointers to FatalError_LocalizedStringId codes 0xcd, 0xce, 0xcf, and 0xd0. Static retail decompile/xref/instruction evidence plus Stuart DXMemoryManager.cpp source parity only; exact enum names, allocator statistics side effects, runtime OOM behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] { "OID__AllocObject" },
                tags("cdxmemorymanager", "alloc", "ret-0x10", "heap-dispatch", "oom-codes")
            ),
            new Spec(
                "0x005491b0",
                "CDXMemoryManager__ReAlloc",
                "__thiscall",
                voidPtr,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("mem", voidPtr),
                    param("new_size", uintType)
                },
                "Wave607 CDXMemoryManager core hardening: this is not a CPolyBucket-owned allocator. RET 0x8, CPolyBucket/FlexArray callsites, and the body match CDXMemoryManager::ReAlloc: try CMemoryHeap__ReallocTiny on default and thing heaps, otherwise derive the CMemoryBlock header at mem-0x10, read its memory type at mem-0x8, and dispatch CMemoryHeap__ReAlloc through the type heap table. Static retail decompile/xref/instruction evidence plus Stuart DXMemoryManager.cpp source parity only; exact block-header layout beyond observed offsets, runtime realloc behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] { "CPolyBucket__ReallocFromPool" },
                tags("cdxmemorymanager", "realloc", "ret-0x8", "heap-dispatch", "tiny-heap")
            ),
            new Spec(
                "0x005492d0",
                "CDXMemoryManager__CalcAndShowDeltas",
                "__thiscall",
                voidType,
                new ParameterImpl[] { param("this", voidPtr) },
                "Wave607 CDXMemoryManager core hardening: ECX-only method that emits debug-trace header/footer strings and calls CMemoryHeap__CalcAndShowDeltas on the default, dump, and thing heaps at this+0x214, this+0xae0, and this+0x13ac. The source has Xbox-only texture/VB heap delta calls that are absent from this PC retail body. Static retail decompile/xref/string evidence plus Stuart DXMemoryManager.cpp source parity only; exact trace output behavior, runtime memory-delta semantics, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("cdxmemorymanager", "memory-deltas", "ret-c3", "trace")
            ),
            new Spec(
                "0x00549400",
                "CMemoryManager__DeleteTagList",
                "__thiscall",
                voidType,
                new ParameterImpl[] { param("this", voidPtr) },
                "Wave607 memory-manager owner correction: this is not CDXEngine landscape-cell cleanup. The body is the simple CMemoryManager tag-list delete helper: walk CMemoryManager::mFirstTag at this+0x4, read CMemoryTag::mNext at +0x208, free each tag through default/thing tiny-free checks and type-selected heap free, then store the next tag pointer. Xrefs are unwind metadata for memory-manager cleanup paths. Static retail decompile/instruction evidence plus Stuart CMemoryManager destructor source parity only; exact compiler EH ownership, complete CMemoryTag layout, runtime tagging behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] { "CDXEngine__FreeLandscapeCellList" },
                tags("cmemorymanager", "tag-list", "ret-c3", "destructor-helper")
            )
        };

        Stats stats = new Stats();
        println("MODE: " + (dryRun ? "dry" : "apply"));
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }
        println(
            "SUMMARY: updated=" + stats.updated +
            " skipped=" + stats.skipped +
            " renamed=" + stats.renamed +
            " would_rename=" + stats.wouldRename +
            " missing=" + stats.missing +
            " bad=" + stats.bad);
        if (!dryRun) {
            if (stats.bad != 0 || stats.missing != 0) {
                throw new IllegalStateException("Apply completed with bad=" + stats.bad + " missing=" + stats.missing);
            }
        }
    }
}
