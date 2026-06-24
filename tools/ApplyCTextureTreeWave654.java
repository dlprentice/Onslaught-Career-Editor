//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
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

public class ApplyCTextureTreeWave654 extends GhidraScript {
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
            "ctexture-rbtree-wave654",
            "retail-binary-evidence",
            "signature-hardened",
            "comment-hardened"
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
            boolean needsSignature = !signatureMatches(fn, spec);
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
                if (needsSignature) {
                    stats.signatureUpdated++;
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
            if (needsSignature) {
                stats.signatureUpdated++;
            }
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
        DataType voidPtr = new PointerDataType(voidType);
        DataType intType = IntegerDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x00572e40",
                "CTexture__DestroyNodeTreeAndStorage",
                "__fastcall",
                voidType,
                new ParameterImpl[] {
                    param("tree_state", voidPtr)
                },
                "Wave654 CTexture/RB-tree helper hardening: fastcall destroy path tears down a sentinel-backed tree/list state, either erasing nodes one by one or recursively freeing the root subtree, then frees the tree header and decrements the shared sentinel DAT_009d0c44 refcount. Static retail decompile/xref evidence only; exact owner/template identity, concrete node layout, runtime texture behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("ctexture", "red-black-tree", "tree-destruction", "shared-sentinel")
            ),
            new Spec(
                "0x005738e0",
                "CTexture__EraseNodeFromTree",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("unused_out_slot", voidPtr),
                    param("node", voidPtr),
                    param("unused_context", voidPtr)
                },
                "Wave654 CTexture/RB-tree helper hardening: thiscall erase helper removes node from the sentinel-backed tree, updates header min/max/root links, and runs red-black delete fixup rotations/recolors against DAT_009d0c44. Also reached from adjacent CFastVB tree range erase code, so the owner label is treated as static Ghidra naming evidence rather than a concrete class layout. Runtime behavior and rebuild parity remain unproven.",
                new String[] {},
                tags("ctexture", "red-black-tree", "erase-node", "delete-fixup", "shared-sentinel", "ret-0xc")
            ),
            new Spec(
                "0x00573cc0",
                "CTexture__DestroySubtreeRecursive",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("node", voidPtr)
                },
                "Wave654 CTexture/RB-tree helper hardening: stdcall recursive subtree destructor walks right children first, frees each node, then advances through left links until the shared sentinel DAT_009d0c44 is reached. Static retail decompile/xref evidence only; exact node payload ownership, runtime texture behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("ctexture", "red-black-tree", "subtree-destruction", "shared-sentinel", "ret-0x4")
            ),
            new Spec(
                "0x00574080",
                "CTexture__WalkNodeListUntilSentinel",
                "__cdecl",
                voidType,
                new ParameterImpl[] {
                    param("node_slot", voidPtr)
                },
                "Wave654 CTexture/RB-tree helper hardening: cdecl sentinel walk helper follows first-child/next links from node_slot until DAT_009d0c44 is reached. Current decompile has no visible side effect, so this comment preserves the narrow static observation only and does not claim concrete iterator semantics, runtime behavior, or rebuild parity.",
                new String[] {},
                tags("ctexture", "red-black-tree", "sentinel-walk", "shared-sentinel", "narrow-static-claim")
            ),
            new Spec(
                "0x005740a0",
                "CTexture__RotateTreeLeft",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("pivot_node", voidPtr)
                },
                "Wave654 CTexture/RB-tree helper hardening: thiscall left-rotation helper pivots pivot_node's right child up, updates parent/root/header links, and preserves DAT_009d0c44 child checks. Xrefs are from adjacent tree insert fixup code, so this remains static helper evidence and not a concrete CTexture layout or runtime-rendering proof.",
                new String[] {},
                tags("ctexture", "red-black-tree", "left-rotate", "insert-delete-fixup", "shared-sentinel", "ret-0x4")
            ),
            new Spec(
                "0x00574100",
                "CTexture__InitTreeNodeParentAndKey",
                "__stdcall",
                voidPtr,
                new ParameterImpl[] {
                    param("parent_node", voidPtr),
                    param("node_color", intType)
                },
                "Wave654 CTexture/RB-tree helper hardening: stdcall allocator/init helper requests a 0x14-byte node, stores parent_node at +0x04 and node_color at +0x10, then returns the new node in EAX. Name retained from existing Ghidra state; exact field names, allocator provenance, owner/template identity, and runtime behavior remain unproven.",
                new String[] {},
                tags("ctexture", "red-black-tree", "node-allocation", "parent-link", "node-color", "ret-0x8")
            ),
            new Spec(
                "0x00574120",
                "CTexture__TreeIteratorNext",
                "__fastcall",
                voidType,
                new ParameterImpl[] {
                    param("iterator_slot", voidPtr)
                },
                "Wave654 CTexture/RB-tree helper hardening: fastcall iterator helper advances iterator_slot to the in-order successor using left/right/parent links and the shared sentinel DAT_009d0c44. Static retail decompile evidence only; exact iterator type, concrete node layout, runtime texture behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("ctexture", "red-black-tree", "iterator-next", "shared-sentinel")
            ),
            new Spec(
                "0x00574180",
                "CTexture__TreeIteratorPrev",
                "__fastcall",
                voidType,
                new ParameterImpl[] {
                    param("iterator_slot", voidPtr)
                },
                "Wave654 CTexture/RB-tree helper hardening: fastcall iterator helper retreats iterator_slot to the in-order predecessor using right/left/parent links and the shared sentinel DAT_009d0c44. Static retail decompile evidence only; exact iterator type, concrete node layout, runtime texture behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("ctexture", "red-black-tree", "iterator-prev", "shared-sentinel")
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
            " signature_updated=" + stats.signatureUpdated +
            " missing=" + stats.missing +
            " bad=" + stats.bad);
        if (!dryRun && (stats.bad != 0 || stats.missing != 0)) {
            throw new IllegalStateException("Apply completed with bad=" + stats.bad + " missing=" + stats.missing);
        }
    }
}
