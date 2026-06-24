//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.BooleanDataType;
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

public class ApplyNodePayloadHeadWave703 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] parameters;
        final boolean updateSignature;
        final String comment;
        final String[] tags;

        Spec(String address, String name, String callingConvention, DataType returnType,
                ParameterImpl[] parameters, boolean updateSignature, String comment, String[] tags) {
            this.address = address;
            this.name = name;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.parameters = parameters;
            this.updateSignature = updateSignature;
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
        int commentOnlyUpdated = 0;
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
            "ctexture-node-payload-head-wave703",
            "wave703-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "signature-hardened"
        }, extras);
    }

    private String[] commentOnlyTags(String... extras) {
        return concat(new String[] {
            "static-reaudit",
            "ctexture-node-payload-head-wave703",
            "wave703-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "comment-only"
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
        if (!spec.updateSignature) {
            return true;
        }
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
        if (!spec.updateSignature) {
            return "<comment/tag-only; saved signature intentionally unchanged>";
        }
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
            boolean needsSignature = spec.updateSignature && !signatureMatches(fn, spec);
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
                if (!spec.updateSignature) {
                    stats.commentOnlyUpdated++;
                }
                println("DRY: " + spec.address + " actual=" + fn.getSignature() + " expected=" + expectedSignature(spec));
                return;
            }

            if (spec.updateSignature) {
                fn.setCallingConvention(spec.callingConvention);
                fn.setReturnType(spec.returnType, SourceType.USER_DEFINED);
                fn.replaceParameters(
                    FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS,
                    true,
                    SourceType.USER_DEFINED,
                    spec.parameters
                );
            }
            fn.setComment(spec.comment);
            for (String tag : spec.tags) {
                fn.addTag(tag);
            }
            verifyReadBack(spec);

            stats.updated++;
            if (needsSignature) {
                stats.signatureUpdated++;
            }
            if (!spec.updateSignature) {
                stats.commentOnlyUpdated++;
            }
            println("OK: " + spec.address + " " + expectedSignature(spec));
        } catch (Exception ex) {
            stats.bad++;
            println("BAD: " + spec.address + " " + spec.name + " " + ex.getClass().getSimpleName() + ": " + ex.getMessage());
        }
    }

    private Spec[] specs() throws Exception {
        DataType boolType = BooleanDataType.dataType;
        DataType intType = IntegerDataType.dataType;
        DataType uintType = UnsignedIntegerDataType.dataType;
        DataType voidPtr = new PointerDataType(VoidDataType.dataType);
        DataType voidType = VoidDataType.dataType;

        return new Spec[] {
            new Spec(
                "0x00598702",
                "CTexture__NodePayloadBaseCtor",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("format_class_id_or_kind", intType)
                },
                true,
                "Wave703 static read-back: initializes the node-payload header, clears child and next links at +0x8/+0xc, installs the base release-node vtable, stores the observed format class/kind field at +0x4, and ends with RET 0x4. Static metadata only; exact payload class enum, owning allocator, concrete struct layout, and runtime texture behavior remain unproven.",
                signatureTags("node-payload", "constructor", "format-class", "tranche-head", "phantom-param-removed")
            ),
            new Spec(
                "0x0059871c",
                "CDXTexture__ReleaseNodePayloadChain",
                "__fastcall",
                voidType,
                new ParameterImpl[] { param("node_payload", voidPtr) },
                true,
                "Wave703 static read-back: resets the node to the base release vtable, destroys the child chain at +0x8 through vslot 0 with delete flag 1, then drains and unlinks the sibling chain at +0xc while invoking each node destructor with delete flag 1. Static metadata only; exact destructor ownership, payload layout, allocator behavior, and runtime texture lifetime remain unproven.",
                signatureTags("node-payload", "release-chain", "vtable-dispatch", "destructor")
            ),
            new Spec(
                "0x00598749",
                "CTexture__HasSameFormatClassId",
                "__thiscall",
                boolType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("candidate_node", voidPtr)
                },
                true,
                "Wave703 static read-back: returns false for a null candidate and otherwise compares candidate_node+0x4 with this+0x4 before returning via RET 0x4. Static metadata only; exact class-id enum, node layout, and runtime compatibility policy remain unproven.",
                signatureTags("node-payload", "format-class", "compatibility", "phantom-param-removed")
            ),
            new Spec(
                "0x0059877e",
                "CTexture__NodePayloadNoOp",
                "",
                voidType,
                new ParameterImpl[] {},
                false,
                "Wave703 static read-back: single RET no-op used as a node-payload/vtable slot and parser cleanup helper. Signature intentionally left unchanged because Ghidra reports an unknown calling convention with locked storage. Static metadata only; exact slot identity, caller ABI, and runtime parser behavior remain unproven.",
                commentOnlyTags("node-payload", "no-op", "vtable-slot", "locked-storage")
            ),
            new Spec(
                "0x0059877f",
                "CTexture__NodePayloadMatchesTypeOrNullIsZero",
                "__stdcall",
                uintType,
                new ParameterImpl[] {
                    param("node_or_null", voidPtr),
                    param("expected_type", intType)
                },
                true,
                "Wave703 static read-back: returns expected_type == 0 when node_or_null is null, otherwise dispatches node_or_null vslot +0x4 with expected_type and returns the boolean-style result through RET 0x8. Static metadata only; exact type enum, vtable contract, and runtime texture compatibility behavior remain unproven.",
                signatureTags("node-payload", "vtable-dispatch", "type-match", "null-sentinel")
            ),
            new Spec(
                "0x0059879e",
                "CDXTexture__InvokeNodeScoreOrZero",
                "__stdcall",
                intType,
                new ParameterImpl[] { param("node_or_null", voidPtr) },
                true,
                "Wave703 static read-back: returns zero for a null node and otherwise dispatches node_or_null vslot +0x8, preserving the node-provided score/result, then returns through RET 0x4. Static metadata only; exact score meaning, vtable ABI, and runtime selection behavior remain unproven.",
                signatureTags("node-payload", "vtable-dispatch", "score", "null-sentinel")
            ),
            new Spec(
                "0x005987b2",
                "CTexture__AppendNodeAtTail_Link0c",
                "__stdcall",
                voidPtr,
                new ParameterImpl[] {
                    param("chain_head", voidPtr),
                    param("node_to_append", voidPtr)
                },
                true,
                "Wave703 static read-back: appends node_to_append at the first null +0xc link of chain_head and returns the resulting chain head, or returns node_to_append when the input chain is empty. Static metadata only; exact chain ownership, node lifetime, parser reduction policy, and runtime texture behavior remain unproven.",
                signatureTags("node-payload", "linked-list", "append-tail", "parser-reduction")
            ),
            new Spec(
                "0x005987d9",
                "CDXTexture__NodePayload__ctor",
                "__fastcall",
                voidType,
                new ParameterImpl[] { param("node_payload", voidPtr) },
                true,
                "Wave703 static read-back: initializes a 0x14-byte node payload with kind/class field 1, null child and sibling links, the CDXTexture node-payload vtable, and a zeroed +0x10 value field. Static metadata only; exact derived payload type, allocator ownership, vtable slot names, and runtime texture behavior remain unproven.",
                signatureTags("node-payload", "constructor", "derived-node", "vtable")
            ),
            new Spec(
                "0x005987f4",
                "CTexture__NodePayloadRecordCtor",
                "",
                intType,
                new ParameterImpl[] {},
                false,
                "Wave703 static read-back: hidden-ECX constructor stores stack values into +0x8, +0xc, and +0x10, sets the kind/class field to 1, installs the CDXTexture node-payload vtable, returns ECX, and ends with RET 0xc. Signature intentionally left unchanged because Ghidra reports an unknown calling convention with locked storage. Static metadata only; exact hidden-register ABI, record-field meaning, and runtime parser behavior remain unproven.",
                commentOnlyTags("node-payload", "constructor", "hidden-ecx", "locked-storage")
            ),
            new Spec(
                "0x0059881b",
                "CTexture__IsFormatChainCompatible",
                "__thiscall",
                intType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("candidate_chain", voidPtr)
                },
                true,
                "Wave703 static read-back: first checks that candidate_chain shares this+0x4 through CTexture__HasSameFormatClassId, then walks node links at +0xc and validates kind-1 child chains or non-kind payloads through CTexture__NodePayloadMatchesTypeOrNullIsZero before returning a boolean-style result through RET 0x4. Static metadata only; exact chain schema, payload type enum, and runtime texture compatibility behavior remain unproven.",
                signatureTags("node-payload", "compatibility", "linked-list", "child-chain", "phantom-param-removed")
            ),
            new Spec(
                "0x00598873",
                "CFastVB__CloneNodeChainWithAddRef",
                "__fastcall",
                voidPtr,
                new ParameterImpl[] { param("source_chain", voidPtr) },
                true,
                "Wave703 static read-back: clones a node chain by allocating 0x14-byte kind-1 wrappers, copying +0x10, recursively cloning child payloads through vslot +0x8, rolling back failed child clones with delete flag 1, and linking cloned siblings through +0xc; non-kind-1 nodes are cloned through their vslot +0x8. Static metadata only; exact AddRef semantics, allocator ownership, payload layout, and runtime vertex-buffer behavior remain unproven.",
                signatureTags("node-payload", "clone-chain", "vtable-dispatch", "allocator", "fastcall-param-named")
            ),
            new Spec(
                "0x005988f5",
                "CFastVB__CompareNodeValuesByTagAndPayload",
                "__fastcall",
                intType,
                new ParameterImpl[] { param("left_payload", voidPtr) },
                true,
                "Wave703 static read-back: compares the ECX-held left_payload with a hidden EAX-held right payload by tag, handling observed scalar/pointer, inline-string, indirect-string, and double-like cases before returning a boolean-style match result. Static metadata only; hidden EAX comparator ABI, tag enum, string encoding, and runtime vertex-buffer selection behavior remain unproven.",
                signatureTags("node-payload", "comparator", "hidden-eax", "tag-dispatch", "fastcall-param-named")
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

        println("ApplyNodePayloadHeadWave703 mode=" + (dryRun ? "dry" : "apply"));
        Stats stats = new Stats();
        for (Spec spec : specs()) {
            applySpec(spec, dryRun, stats);
        }
        println("SUMMARY: updated=" + stats.updated
            + " skipped=" + stats.skipped
            + " renamed=" + stats.renamed
            + " would_rename=" + stats.wouldRename
            + " signature_updated=" + stats.signatureUpdated
            + " comment_only_updated=" + stats.commentOnlyUpdated
            + " missing=" + stats.missing
            + " bad=" + stats.bad);
    }
}
