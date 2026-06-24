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
import ghidra.program.model.listing.Parameter;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyNodeTreeCompatibilityWave709 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] parameters;
        final String comment;
        final String[] tags;

        Spec(String address, String name, String callingConvention, DataType returnType,
                ParameterImpl[] parameters, String comment, String[] tags) {
            this.address = address;
            this.name = name;
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

    private String[] concat(String[] common, String... extras) {
        String[] result = new String[common.length + extras.length];
        System.arraycopy(common, 0, result, 0, common.length);
        System.arraycopy(extras, 0, result, common.length, extras.length);
        return result;
    }

    private String[] signatureTags(String... extras) {
        return concat(new String[] {
            "static-reaudit",
            "node-tree-compatibility-wave709",
            "wave709-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "signature-hardened",
            "node-tree-compatibility"
        }, extras);
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
            if (!fn.getName().equals(spec.name)) {
                stats.bad++;
                println("BADNAME: " + spec.address + " actual=" + fn.getName() + " expected=" + spec.name);
                return;
            }
            boolean needsSignature = !signatureMatches(fn, spec);
            if (!needsUpdate(fn, spec)) {
                stats.skipped++;
                println("SKIP: " + spec.address + " " + expectedSignature(spec));
                return;
            }
            if (dryRun) {
                stats.skipped++;
                if (needsSignature) {
                    stats.signatureUpdated++;
                }
                println("DRY: " + spec.address + " " + expectedSignature(spec));
                return;
            }
            fn.setCallingConvention(spec.callingConvention);
            fn.setReturnType(spec.returnType, SourceType.USER_DEFINED);
            fn.replaceParameters(FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS, true,
                SourceType.USER_DEFINED, spec.parameters);
            if (needsSignature) {
                stats.signatureUpdated++;
            }
            fn.setComment(spec.comment);
            for (String tag : spec.tags) {
                fn.addTag(tag);
            }
            verifyReadBack(spec);
            stats.updated++;
            println("OK: " + spec.address + " " + expectedSignature(spec));
            Thread.sleep(75);
        }
        catch (Exception ex) {
            stats.bad++;
            println("FAIL: " + spec.address + " " + spec.name + " :: " + ex.getMessage());
        }
    }

    private Spec[] specs() throws Exception {
        DataType intType = IntegerDataType.dataType;
        DataType uintType = UnsignedIntegerDataType.dataType;
        DataType voidPtr = new PointerDataType(VoidDataType.dataType);

        return new Spec[] {
            new Spec(
                "0x00599d80",
                "CFastVB__FlattenNodeTreeLeafByLinearIndex",
                "__thiscall",
                intType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("node_tree", voidPtr),
                    param("linear_leaf_index", uintType),
                    param("out_leaf_scratch", voidPtr)
                },
                "Wave709 static read-back: RET 0xc and six caller sites show the CFastVB parser context in ECX plus three stack arguments: node tree, linear leaf index, and output leaf scratch. The helper walks wrapper kinds 1, 5, 7, and 10, descends to leaf kind 8, writes normalized leaf fields at output +0x10/+0x14/+0x18/+0x1c plus flag mask +0x20 & 0x200, and returns 0 or 0x80004005 on null/unknown paths. Static metadata only; exact node layout, field semantics, source identity, runtime parser behavior, and rebuild parity remain unproven.",
                signatureTags("flatten-leaf-by-index", "phantom-param-removed", "ret-0xc", "tranche-head")
            ),
            new Spec(
                "0x00599e48",
                "CFastVB__ResolveCommonLeafFormat",
                "__stdcall",
                intType,
                new ParameterImpl[] {
                    param("left_leaf_scratch", voidPtr),
                    param("right_leaf_scratch", voidPtr),
                    param("out_common_format", voidPtr)
                },
                "Wave709 static read-back: RET 0xc and the caller at 0x0059a19d show three stack arguments: two leaf scratch records and an output common-format slot. Both inputs must be leaf kind 8; matching formats are copied directly, otherwise the helper reads compatibility tables at 0x005f2908/0x005f290c and writes observed common format ids 0..0xc or returns -1. Static metadata only; exact format enum names, table semantics, source identity, runtime parser behavior, and rebuild parity remain unproven.",
                signatureTags("common-leaf-format", "format-compatibility-table", "ret-0xc")
            ),
            new Spec(
                "0x00599ffd",
                "CFastVB__CompareNodePayloadBindingChain",
                "__thiscall",
                intType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("left_payload", voidPtr),
                    param("right_payload", voidPtr),
                    param("right_binding_chain", voidPtr),
                    param("compare_flags", intType)
                },
                "Wave709 static read-back: RET 0x10 shows four cleaned stack arguments after the ECX parser context; the fourth cleaned argument is not read by the current decompile and is retained as ABI context. The helper compares the left payload +0x1c descriptor against the right payload descriptor/name, then walks the left payload +0x24 chain and the right binding chain through +0xc links, comparing kind-5 payload records and nested node trees with CFastVB__AreNodeTreesStructurallyEqual. Static metadata only; exact payload/binding layout, compare flag semantics, source identity, runtime parser behavior, and rebuild parity remain unproven.",
                signatureTags("payload-binding-chain", "ret-0x10", "unused-cleaned-arg")
            ),
            new Spec(
                "0x0059a10a",
                "CFastVB__ScoreNodeTreePairMismatchBits",
                "__thiscall",
                intType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("left_node_tree", voidPtr),
                    param("right_node_tree", voidPtr)
                },
                "Wave709 static read-back: RET 0x8 removes the prior phantom third stack argument; callers push only the two node-tree pointers after loading the parser context in ECX. The helper counts expanded leaves on both trees, exits with zero for structurally equal trees, flattens paired leaves with CFastVB__FlattenNodeTreeLeafByLinearIndex, resolves common leaf formats, and accumulates mismatch bits for count/format/flatten differences before returning the score. Static metadata only; exact score-bit meanings, node/leaf layout, source identity, runtime parser behavior, and rebuild parity remain unproven.",
                signatureTags("pair-mismatch-score", "phantom-param-removed", "ret-0x8")
            ),
            new Spec(
                "0x0059a21f",
                "CFastVB__AreNodeTreesCompatible",
                "__thiscall",
                intType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("left_node_tree", voidPtr),
                    param("right_node_tree", voidPtr),
                    param("relaxed_match", intType)
                },
                "Wave709 static read-back: RET 0xc plus ECX use correct the prior stdcall signature to thiscall with parser context in ECX and three stack arguments. The helper handles null-tree cases, expands non-leaf trees into node-type-9 scratch records, compares leaf shape/count/type constraints, optionally uses the relaxed leaf-type path, flattens leaves, and falls back to structural equality for nested node trees. Static metadata only; exact compatibility rules, relaxed-match semantics, node layout, source identity, runtime parser behavior, and rebuild parity remain unproven.",
                signatureTags("node-tree-compatible", "thiscall-correction", "ret-0xc", "relaxed-match")
            ),
            new Spec(
                "0x0059a54d",
                "CFastVB__ScoreNodeTreeMatch",
                "__thiscall",
                intType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("source_payload", voidPtr),
                    param("candidate_payload", voidPtr),
                    param("candidate_binding_chain", voidPtr),
                    param("match_flags", intType)
                },
                "Wave709 static read-back: RET 0x10 removes the prior phantom fifth stack argument; callers pass source payload, candidate payload, candidate binding chain, and match flags after loading parser context in ECX. The helper compares payload descriptor/name context, walks source payload +0x24 binding records, applies match flag 0x10 filtering, calls CFastVB__AreNodeTreesCompatible and CFastVB__ScoreNodeTreePairMismatchBits for nested node-tree candidates, and returns -1 or an accumulated match score. Static metadata only; exact payload/binding layout, score semantics, flag meanings, source identity, runtime parser behavior, and rebuild parity remain unproven.",
                signatureTags("node-tree-match-score", "phantom-param-removed", "ret-0x10", "tranche-tail")
            )
        };
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = true;
        if (args != null && args.length > 0) {
            dryRun = isDryRun(args[0]);
        }

        println("ApplyNodeTreeCompatibilityWave709 mode=" + (dryRun ? "dry" : "apply"));
        Stats stats = new Stats();
        for (Spec spec : specs()) {
            applySpec(spec, dryRun, stats);
        }
        println("SUMMARY: updated=" + stats.updated
            + " skipped=" + stats.skipped
            + " renamed=" + stats.renamed
            + " would_rename=" + stats.wouldRename
            + " signature_updated=" + stats.signatureUpdated
            + " missing=" + stats.missing
            + " bad=" + stats.bad);
    }
}
