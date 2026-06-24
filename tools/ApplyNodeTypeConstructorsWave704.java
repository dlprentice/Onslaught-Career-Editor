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

public class ApplyNodeTypeConstructorsWave704 extends GhidraScript {
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
            "node-type-constructors-wave704",
            "wave704-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "signature-hardened"
        }, extras);
    }

    private String[] commentOnlyTags(String... extras) {
        return concat(new String[] {
            "static-reaudit",
            "node-type-constructors-wave704",
            "wave704-readback-verified",
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
        DataType intType = IntegerDataType.dataType;
        DataType uintType = UnsignedIntegerDataType.dataType;
        DataType voidPtr = new PointerDataType(VoidDataType.dataType);
        DataType voidType = VoidDataType.dataType;

        return new Spec[] {
            new Spec(
                "0x005989c3",
                "CTexture__NodeType8_InitDefaults",
                "__fastcall",
                voidType,
                new ParameterImpl[] { param("node_type8", voidPtr) },
                true,
                "Wave704 static read-back: initializes a node-type-8 payload by clearing child/sibling links at +0x8/+0xc, setting kind/class field +0x4 to 2, and binding vtable 0x005ef240. Static metadata only; exact node-type enum, struct layout, parser source identity, runtime texture behavior, and rebuild parity remain unproven.",
                signatureTags("node-type", "node-type-8", "constructor", "vtable", "fastcall-param-named", "tranche-head")
            ),
            new Spec(
                "0x005989db",
                "CTexture__NodeType8_InitFromDescriptor",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("descriptor_words32", voidPtr)
                },
                true,
                "Wave704 static read-back: initializes the same node-type-8 header as CTexture__NodeType8_InitDefaults, then copies eight dwords from descriptor_words32 into storage at +0x10 and returns through RET 0x4. Static metadata only; exact descriptor schema, field meanings, parser ownership, runtime texture behavior, and rebuild parity remain unproven.",
                signatureTags("node-type", "node-type-8", "descriptor-copy", "vtable", "phantom-param-removed")
            ),
            new Spec(
                "0x00598a56",
                "CFastVB__InitNodeType9",
                "__fastcall",
                voidType,
                new ParameterImpl[] { param("node_type9", voidPtr) },
                true,
                "Wave704 static read-back: initializes a node-type-9 payload with kind/class field 8, vtable 0x005ef250, null child/sibling links, zeroed payload fields, and observed default tag/value field +0x14 set to 9. Static metadata only; exact node-type enum, field meanings, parser ownership, runtime vertex-buffer behavior, and rebuild parity remain unproven.",
                signatureTags("node-type", "node-type-9", "constructor", "vtable", "fastcall-param-named")
            ),
            new Spec(
                "0x00598a81",
                "CFastVB__NodeType9__ctor",
                "",
                intType,
                new ParameterImpl[] {},
                false,
                "Wave704 static read-back: hidden-ECX constructor for node-type 9 clears child/sibling links, copies five stack values into +0x10..+0x20, sets kind/class field 8, binds vtable 0x005ef250, returns ECX, and leaves the saved signature unchanged because Ghidra reports unknown calling convention with locked storage. Static metadata only; exact hidden ABI, field meanings, and runtime parser behavior remain unproven.",
                commentOnlyTags("node-type", "node-type-9", "constructor", "hidden-ecx", "locked-storage")
            ),
            new Spec(
                "0x00598abd",
                "CFastVB__NodeType9__dtor",
                "__fastcall",
                voidType,
                new ParameterImpl[] { param("node_type9", voidPtr) },
                true,
                "Wave704 static read-back: restores the node-type-9 vtable 0x005ef250 and releases the node-payload child/sibling chain through CDXTexture__ReleaseNodePayloadChain. Static metadata only; exact destructor ownership, payload layout, runtime vertex-buffer behavior, and rebuild parity remain unproven.",
                signatureTags("node-type", "node-type-9", "destructor", "release-chain", "fastcall-param-named")
            ),
            new Spec(
                "0x00598b48",
                "CFastVB__InitNodeType10",
                "__fastcall",
                voidType,
                new ParameterImpl[] { param("node_type10", voidPtr) },
                true,
                "Wave704 static read-back: initializes a node-type-10 payload with kind/class field 10, vtable 0x005ef260, null child/sibling links, and zeroed owned-child/resource pointer slots through +0x38. Static metadata only; exact node-type enum, owned-slot layout, runtime vertex-buffer behavior, and rebuild parity remain unproven.",
                signatureTags("node-type", "node-type-10", "constructor", "vtable", "owned-resource-slots", "fastcall-param-named")
            ),
            new Spec(
                "0x00598b81",
                "CFastVB__NodeType10_dtor",
                "__fastcall",
                voidType,
                new ParameterImpl[] { param("node_type10", voidPtr) },
                true,
                "Wave704 static read-back: restores vtable 0x005ef260, releases non-null owned child/interface pointers at +0x20/+0x24/+0x28/+0x2c/+0x30 through vslot 0 with delete flag 1, frees the +0x38 resource pointer, and then releases the base node-payload chain. Static metadata only; exact slot types, ownership policy, runtime vertex-buffer behavior, and rebuild parity remain unproven.",
                signatureTags("node-type", "node-type-10", "destructor", "owned-resource-slots", "release-chain", "fastcall-param-named")
            ),
            new Spec(
                "0x00598d6b",
                "CFastVB__InitNodeType13",
                "__fastcall",
                voidPtr,
                new ParameterImpl[] { param("node_type13", voidPtr) },
                true,
                "Wave704 static read-back: initializes a node-type-13 payload with kind/class field 0xd, vtable 0x005ef270, null child/sibling links, zeroed storage through +0x3c, +0x10 set to 3, and returns the initialized node pointer. Static metadata only; exact node-type enum, field schema, runtime texture behavior, and rebuild parity remain unproven.",
                signatureTags("node-type", "node-type-13", "constructor", "vtable", "fastcall-param-named", "return-this")
            ),
            new Spec(
                "0x00598da4",
                "CDXTexture__NodeType13__ctor",
                "",
                intType,
                new ParameterImpl[] {},
                false,
                "Wave704 static read-back: hidden-ECX constructor for node-type 13 clears child/sibling links, sets kind/class field 0xd, binds vtable 0x005ef270, copies stack-provided scalar fields and eight descriptor dwords into storage at +0x20, returns ECX, and leaves the saved signature unchanged because Ghidra reports unknown calling convention with locked storage. Static metadata only; exact hidden ABI, descriptor schema, runtime texture behavior, and rebuild parity remain unproven.",
                commentOnlyTags("node-type", "node-type-13", "constructor", "descriptor-copy", "hidden-ecx", "locked-storage")
            ),
            new Spec(
                "0x00598ddc",
                "CDXTexture__NodeType13__ctorWithRefBump",
                "",
                intType,
                new ParameterImpl[] {},
                false,
                "Wave704 static read-back: hidden-ECX constructor for node-type 13 mirrors the descriptor-copy setup, stores a stack-provided referenced object at +0x18, copies eight descriptor dwords into +0x20, and calls referenced vslot +4 when non-null. Signature intentionally left unchanged because Ghidra reports unknown calling convention with locked storage. Static metadata only; exact reference-count ABI, field layout, runtime texture behavior, and rebuild parity remain unproven.",
                commentOnlyTags("node-type", "node-type-13", "constructor", "ref-bump", "hidden-ecx", "locked-storage")
            ),
            new Spec(
                "0x00598e22",
                "CTexture__Dtor_ReleaseNodePayloadByKind",
                "__fastcall",
                voidType,
                new ParameterImpl[] { param("node_payload", voidPtr) },
                true,
                "Wave704 static read-back: restores vtable 0x005ef270, releases the optional +0x18 child/reference through vslot +8 when +0x10 == 5, releases the +0x18 owned child through vslot 0 with delete flag 1 when +0x10 == 4, then releases the base node-payload chain. Static metadata only; exact kind values, slot ownership, runtime texture behavior, and rebuild parity remain unproven.",
                signatureTags("node-type", "node-type-13", "destructor", "kind-dispatch", "release-chain", "fastcall-param-named")
            ),
            new Spec(
                "0x00598e5d",
                "CDXTexture__CompareNodePayloadWithOptionalChild",
                "__thiscall",
                intType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("candidate_payload", voidPtr)
                },
                true,
                "Wave704 static read-back: compares format/class id with CTexture__HasSameFormatClassId, compares four dwords at +0x10, and accepts a type-4 optional child path when CTexture__NodePayloadMatchesTypeOrNullIsZero succeeds for the +0x18 child/payload field. Static metadata only; exact type enum, optional-child ABI, runtime texture behavior, and rebuild parity remain unproven.",
                signatureTags("node-type", "node-type-13", "comparator", "optional-child", "phantom-param-removed")
            ),
            new Spec(
                "0x00598f22",
                "CDXTexture__Dtor_ReleaseNodePayload_DeleteOnFlag",
                "__thiscall",
                voidPtr,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("delete_flags", uintType)
                },
                true,
                "Wave704 static read-back: scalar-deleting-style wrapper releases the node-payload chain, frees this through OID__FreeObject_Callback when delete_flags bit 0 is set, returns this, and ends with RET 0x4. Static metadata only; exact vtable slot, allocator ownership, runtime texture behavior, and rebuild parity remain unproven.",
                signatureTags("node-type", "scalar-deleting-dtor", "delete-flag", "release-chain", "phantom-param-removed")
            ),
            new Spec(
                "0x00598f3e",
                "CDXTexture__Dtor_NodePayload_DeleteOnFlag",
                "__thiscall",
                voidPtr,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("delete_flags", uintType)
                },
                true,
                "Wave704 static read-back: resets the node payload to vtable 0x005ef230, releases the node-payload chain, frees this when delete_flags bit 0 is set, returns this, and ends with RET 0x4. Static metadata only; exact vtable slot, allocator ownership, runtime texture behavior, and rebuild parity remain unproven.",
                signatureTags("node-type", "scalar-deleting-dtor", "delete-flag", "release-chain", "phantom-param-removed")
            ),
            new Spec(
                "0x00598f60",
                "CFastVB__NodeType8_scalar_deleting_dtor",
                "__thiscall",
                voidPtr,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("delete_flags", uintType)
                },
                true,
                "Wave704 static read-back: resets the node-type-8 vtable 0x005ef240, releases the node-payload chain, frees this when delete_flags bit 0 is set, returns this, and ends with RET 0x4. Static metadata only; exact vtable slot, allocator ownership, runtime vertex-buffer behavior, and rebuild parity remain unproven.",
                signatureTags("node-type", "node-type-8", "scalar-deleting-dtor", "delete-flag", "release-chain", "phantom-param-removed")
            ),
            new Spec(
                "0x00598f82",
                "CFastVB__NodeType9_scalar_deleting_dtor",
                "__thiscall",
                voidPtr,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("delete_flags", uintType)
                },
                true,
                "Wave704 static read-back: resets the node-type-9 vtable 0x005ef250, releases the node-payload chain, frees this when delete_flags bit 0 is set, returns this, and ends with RET 0x4. Static metadata only; exact vtable slot, allocator ownership, runtime vertex-buffer behavior, and rebuild parity remain unproven.",
                signatureTags("node-type", "node-type-9", "scalar-deleting-dtor", "delete-flag", "release-chain", "phantom-param-removed")
            ),
            new Spec(
                "0x00598fa4",
                "CFastVB__NodeType10_scalar_deleting_dtor",
                "__thiscall",
                voidPtr,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("delete_flags", uintType)
                },
                true,
                "Wave704 static read-back: calls CFastVB__NodeType10_dtor, frees this when delete_flags bit 0 is set, returns this, and ends with RET 0x4. Static metadata only; exact vtable slot, allocator ownership, runtime vertex-buffer behavior, and rebuild parity remain unproven.",
                signatureTags("node-type", "node-type-10", "scalar-deleting-dtor", "delete-flag", "phantom-param-removed")
            ),
            new Spec(
                "0x00598fc0",
                "CTexture__Dtor_ReleaseNodePayload_DeleteOnFlag",
                "__thiscall",
                voidPtr,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("delete_flags", uintType)
                },
                true,
                "Wave704 static read-back: calls CTexture__Dtor_ReleaseNodePayloadByKind, frees this when delete_flags bit 0 is set, returns this, and ends with RET 0x4. Static metadata only; exact vtable slot, allocator ownership, runtime texture behavior, and rebuild parity remain unproven.",
                signatureTags("node-type", "node-type-13", "scalar-deleting-dtor", "delete-flag", "phantom-param-removed")
            ),
            new Spec(
                "0x00598fdc",
                "CTexture__InitOwnedNodeList",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("owner_context", voidPtr)
                },
                true,
                "Wave704 static read-back: initializes an owned-node list header by storing owner_context at +0x0, clearing +0x4 and head pointer +0x8, and setting the tail-link pointer at +0xc to the head slot; returns through RET 0x4. Static metadata only; exact list-owner schema, node record layout, runtime texture behavior, and rebuild parity remain unproven.",
                signatureTags("owned-node-list", "constructor", "tail-link", "phantom-param-removed")
            ),
            new Spec(
                "0x00598ff4",
                "CTexture__FreeOwnedNodeListAndPayloads",
                "__fastcall",
                voidType,
                new ParameterImpl[] { param("owned_node_list", voidPtr) },
                true,
                "Wave704 static read-back: drains the owned-node list at +0x8, advances through each node's +0x10 next link, conditionally frees node payloads based on flag bits +0x8 bit 3 or bit 0 clear, and always frees the node record. Static metadata only; exact node flags, ownership policy, runtime texture behavior, and rebuild parity remain unproven.",
                signatureTags("owned-node-list", "destructor", "payload-free", "fastcall-param-named")
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

        println("ApplyNodeTypeConstructorsWave704 mode=" + (dryRun ? "dry" : "apply"));
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
