//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.BooleanDataType;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.FunctionTag;
import ghidra.program.model.listing.Parameter;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplySPtrSetHelpersWave506 extends GhidraScript {
    private static class Spec {
        final String address;
        final String oldName;
        final String newName;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] parameters;
        final String comment;
        final String[] tags;

        Spec(String address, String oldName, String newName, String callingConvention,
                DataType returnType, ParameterImpl[] parameters, String comment, String[] tags) {
            this.address = address;
            this.oldName = oldName;
            this.newName = newName;
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
        Address result = toAddr(addressText);
        if (result == null) {
            throw new IllegalArgumentException("Bad address: " + addressText);
        }
        return result;
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

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "sptrset-helpers-wave506",
            "retail-binary-evidence",
            "signature-corrected",
            "comment-hardened"
        };
        String[] result = new String[common.length + extras.length];
        System.arraycopy(common, 0, result, 0, common.length);
        System.arraycopy(extras, 0, result, common.length, extras.length);
        return result;
    }

    private String expectedSignature(Spec spec) {
        StringBuilder sb = new StringBuilder();
        sb.append(spec.returnType.getDisplayName()).append(" ")
            .append(spec.callingConvention).append(" ")
            .append(spec.newName).append("(");
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
        Set<String> existing = new HashSet<>();
        for (FunctionTag tag : fn.getTags()) {
            existing.add(tag.getName());
        }
        for (String tag : tags) {
            if (!existing.contains(tag)) {
                return false;
            }
        }
        return true;
    }

    private boolean needsUpdate(Function fn, Spec spec) {
        if (!fn.getName().equals(spec.newName)) {
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

    private void applySpec(Spec spec, boolean dryRun, Stats stats) throws Exception {
        Function fn = functionAtEntry(spec.address);
        if (fn == null) {
            println("MISSING: " + spec.address);
            stats.missing++;
            return;
        }

        String currentName = fn.getName();
        if (!currentName.equals(spec.oldName) && !currentName.equals(spec.newName)) {
            println("BADNAME: " + spec.address + " " + currentName + " expected " + spec.oldName + " or " + spec.newName);
            stats.bad++;
            return;
        }

        boolean renameNeeded = !currentName.equals(spec.newName);
        boolean updateNeeded = needsUpdate(fn, spec);
        if (!updateNeeded) {
            println("SKIP: " + spec.address + " " + spec.newName);
            stats.skipped++;
            return;
        }

        if (dryRun) {
            println("DRY: " + spec.address + " " + currentName + " -> " + spec.newName + " :: " + expectedSignature(spec));
            stats.skipped++;
            if (renameNeeded) {
                stats.wouldRename++;
            }
            return;
        }

        if (renameNeeded) {
            fn.setName(spec.newName, SourceType.USER_DEFINED);
            stats.renamed++;
        }
        fn.setCallingConvention(spec.callingConvention);
        fn.setReturnType(spec.returnType, SourceType.USER_DEFINED);
        fn.replaceParameters(FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS, true, SourceType.USER_DEFINED, spec.parameters);
        fn.setComment(spec.comment);
        for (String tag : spec.tags) {
            fn.addTag(tag);
        }
        println("OK: " + spec.address + " " + spec.newName + " :: " + expectedSignature(spec));
        stats.updated++;
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");
        println("Mode: " + (dryRun ? "dry" : "apply"));

        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);
        DataType intType = IntegerDataType.dataType;
        DataType boolType = BooleanDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x004e5850",
                "CCareerNode__ClonePtrSetFromSource",
                "CSPtrSet__CopyCtorFromSource",
                "__thiscall",
                voidPtr,
                new ParameterImpl[] {param("this", voidPtr), param("source_set", voidPtr)},
                "Wave506 stale-owner correction: GenericSPtrSet/SPtrSet copy-constructor helper, not CCareerNode-owned logic. RET 0x4 proves one explicit source_set argument after ECX; the body zeroes mFirst/mLast/mSize in this, walks source_set nodes, and appends each non-null item through CSPtrSet__AddToTail. Static retail/source SPtrSet evidence only; exact template instantiation ownership, caller return-value mechanics, runtime behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("sptrset", "copy-constructor", "append", "stale-owner-corrected", "rename-corrected")
            ),
            new Spec(
                "0x004e59f0",
                "CSPtrSet__Initialise",
                "CSPtrSet__Initialise",
                "__cdecl",
                voidType,
                new ParameterImpl[] {param("numNodes", intType)},
                "Wave506 signature/comment hardening: static GenericSPtrSet/SPtrSet free-list initializer. The body warns if g_SPtrSet_PoolBase is already set, allocates numNodes 8-byte nodes with SPtrSet.cpp allocation evidence, stores g_SPtrSet_PoolNodeCount and g_SPtrSet_PoolBase, links the nodes into g_SPtrSet_FreeListHead, and terminates the final node. Static retail/source evidence only; allocator category semantics, runtime pool sizing, BEA launch, patching, and rebuild parity remain unproven.",
                tags("sptrset", "free-list", "pool-init", "source-parity")
            ),
            new Spec(
                "0x004e5a80",
                "CSPtrSet__AddToHead",
                "CSPtrSet__AddToHead",
                "__thiscall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr), param("item", voidPtr)},
                "Wave506 signature/comment hardening: GenericSPtrSet/SPtrSet Add helper. The body warns/fatals if the pool is not initialized, pops an 8-byte node from g_SPtrSet_FreeListHead or allocates an overflow node with every-20 warning accounting, stores item, links it before mFirst, increments mSize, and seeds mLast when inserting the first item. Static retail/source evidence only; exact embedded-list owners, runtime pool exhaustion behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("sptrset", "add-head", "free-list", "source-parity")
            ),
            new Spec(
                "0x004e5b20",
                "CSPtrSet__AddToTail",
                "CSPtrSet__AddToTail",
                "__thiscall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr), param("item", voidPtr)},
                "Wave506 signature/comment hardening: GenericSPtrSet/SPtrSet Append helper. The body warns/fatals if the pool is not initialized, pops an 8-byte node from g_SPtrSet_FreeListHead or allocates an overflow node with every-20 warning accounting, stores item, links it after mLast, increments mSize, and seeds mFirst when inserting the first item. Static retail/source evidence only; exact embedded-list owners, runtime pool exhaustion behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("sptrset", "append", "free-list", "source-parity")
            ),
            new Spec(
                "0x004e5c30",
                "CSPtrSet__Contains",
                "CSPtrSet__Contains",
                "__thiscall",
                boolType,
                new ParameterImpl[] {param("this", voidPtr), param("item", voidPtr)},
                "Wave506 signature/comment hardening: GenericSPtrSet/SPtrSet Contains predicate. RET 0x4 proves one explicit item argument after ECX; the body walks mFirst via node->mNext, compares node->mItem against item, returns true on the first match and false when traversal ends. Static retail/source evidence only; exact embedded-list owners, BOOL-vs-bool ABI naming, runtime behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("sptrset", "contains", "iterator-walk", "signature-corrected", "source-parity")
            ),
            new Spec(
                "0x004e5c90",
                "LinkedPtrSet__GetValueAtIndex",
                "CSPtrSet__At",
                "__thiscall",
                voidPtr,
                new ParameterImpl[] {param("this", voidPtr), param("index", intType)},
                "Wave506 stale-name correction: GenericSPtrSet/SPtrSet At(index) helper, not a separate LinkedPtrSet owner. RET 0x4 proves one explicit index argument after ECX; the body walks mFirst by index node steps and returns node->mItem, matching GenericSPtrSet::At without bounds/null protection in the retail body. Static retail/source evidence only; exact caller preconditions, null behavior, runtime behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("sptrset", "at-index", "iterator-walk", "stale-owner-corrected", "rename-corrected", "source-parity")
            )
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
            if (!dryRun) {
                Thread.sleep(5L);
            }
        }

        println(String.format(
            "SUMMARY updated=%d skipped=%d renamed=%d would_rename=%d missing=%d bad=%d",
            stats.updated, stats.skipped, stats.renamed, stats.wouldRename, stats.missing, stats.bad));
    }
}
