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

public class ApplyNodeTypeLifecycleWave706 extends GhidraScript {
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
            "node-type-lifecycle-wave706",
            "wave706-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "signature-hardened"
        }, extras);
    }

    private String[] commentOnlyTags(String... extras) {
        return concat(new String[] {
            "static-reaudit",
            "node-type-lifecycle-wave706",
            "wave706-readback-verified",
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
                println("DRY: " + spec.address + " " + expectedSignature(spec));
                return;
            }
            if (spec.updateSignature) {
                fn.setCallingConvention(spec.callingConvention);
                fn.setReturnType(spec.returnType, SourceType.USER_DEFINED);
                fn.replaceParameters(FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS, true,
                    SourceType.USER_DEFINED, spec.parameters);
                if (needsSignature) {
                    stats.signatureUpdated++;
                }
            }
            else {
                stats.commentOnlyUpdated++;
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
        DataType voidType = VoidDataType.dataType;

        return new Spec[] {
            new Spec(
                "0x005997a5",
                "CFastVB__InitNodeType17",
                "__fastcall",
                voidPtr,
                new ParameterImpl[] { param("node_type17", voidPtr) },
                true,
                "Wave706 static read-back: initializes a node-type 0x11 payload through CTexture__NodePayloadBaseCtor, zeroes descriptor/resource slots from +0x30 through +0x58, binds vtable 0x005ef374, clears eight dwords starting at +0x10, and returns the initialized node pointer. Static metadata only; exact node-type enum, field schema, runtime texture/vertex-buffer behavior, parser/source identity, and rebuild parity remain unproven.",
                signatureTags("node-type-0x11", "constructor", "vtable", "zero-init", "return-this", "tranche-head")
            ),
            new Spec(
                "0x005997e1",
                "CTexture__NodeType12_Ctor_DeleteOnFlag",
                "",
                intType,
                new ParameterImpl[] {},
                false,
                "Wave706 static read-back: hidden-ECX constructor for node-type 0x11 calls CTexture__NodePayloadBaseCtor, binds vtable 0x005ef374, copies eight descriptor dwords from the first stack pointer into +0x10, copies three following stack scalars into +0x30/+0x34/+0x38, and clears +0x3c through +0x58. Signature intentionally left unchanged because Ghidra reports unknown calling convention with locked storage. Static metadata only; exact hidden ABI, descriptor schema, runtime texture behavior, and rebuild parity remain unproven.",
                commentOnlyTags("node-type-0x11", "constructor", "descriptor-copy", "hidden-ecx", "locked-storage")
            ),
            new Spec(
                "0x00599831",
                "CTexture__NodeType12_Dtor_DeleteOnFlag_Body",
                "__fastcall",
                voidType,
                new ParameterImpl[] { param("node_type17", voidPtr) },
                true,
                "Wave706 static read-back: destructor body restores vtable 0x005ef374, releases optional owned interfaces at +0x3c and +0x40 through vslot 0 with delete flag 1, releases up to four +0x44..+0x50 entries through the same path, then releases the base node-payload chain. Static metadata only; exact slot ownership, interface types, runtime behavior, and rebuild parity remain unproven.",
                signatureTags("node-type-0x11", "destructor-body", "owned-resource-slots", "release-chain", "fastcall-param-named")
            ),
            new Spec(
                "0x00599878",
                "CFastVB__CloneNodeTreeWithAddRef",
                "__fastcall",
                voidPtr,
                new ParameterImpl[] { param("source_node_type17", voidPtr) },
                true,
                "Wave706 static read-back: allocates a 0x60 node-type 0x11 clone, initializes it through CFastVB__InitNodeType17, copies descriptor/scalar fields from the source node, invokes vslot +8 clone/add-ref hooks for optional +0x3c/+0x40/+0x44..+0x50 child resources, and destroys the partial clone if any child clone fails. Static metadata only; exact child-resource ABI, refcount semantics, runtime vertex-buffer behavior, and rebuild parity remain unproven.",
                signatureTags("node-type-0x11", "clone", "add-ref", "owned-resource-slots", "fastcall-param-named")
            ),
            new Spec(
                "0x0059993c",
                "CTexture__NodeType12_Ctor",
                "__fastcall",
                voidPtr,
                new ParameterImpl[] { param("node_type12", voidPtr) },
                true,
                "Wave706 static read-back: initializes a node-type 0x12 payload through CTexture__NodePayloadBaseCtor, clears +0x10/+0x14/+0x18/+0x1c/+0x28, binds vtable 0x005ef384, seeds fixed scalar defaults +0x20=0xf0000 and +0x24=0xe40000, and returns the initialized node pointer. Static metadata only; exact node-type enum, field schema, runtime texture behavior, and rebuild parity remain unproven.",
                signatureTags("node-type-0x12", "constructor", "vtable", "default-scalars", "return-this")
            ),
            new Spec(
                "0x0059996f",
                "CTexture__NodeType12_Ctor_ScalarDeletingDtor",
                "",
                intType,
                new ParameterImpl[] {},
                false,
                "Wave706 static read-back: hidden-ECX constructor for node-type 0x12 calls CTexture__NodePayloadBaseCtor, copies five stack-provided scalars into +0x10/+0x14/+0x18/+0x1c/+0x28, binds vtable 0x005ef384, and seeds fixed scalar defaults +0x20=0xf0000 and +0x24=0xe40000. Signature intentionally left unchanged because Ghidra reports unknown calling convention with locked storage. Static metadata only; exact hidden ABI, scalar semantics, runtime texture behavior, and rebuild parity remain unproven.",
                commentOnlyTags("node-type-0x12", "constructor", "stack-scalars", "hidden-ecx", "locked-storage")
            ),
            new Spec(
                "0x005999b5",
                "CTexture__NodeType12_ScalarDeletingDtor_Body",
                "__fastcall",
                voidType,
                new ParameterImpl[] { param("node_type12", voidPtr) },
                true,
                "Wave706 static read-back: destructor body restores vtable 0x005ef384, releases the optional owned pointer at +0x28 through vslot 0 with delete flag 1, then releases the base node-payload chain. Static metadata only; exact owned slot type, runtime texture behavior, and rebuild parity remain unproven.",
                signatureTags("node-type-0x12", "destructor-body", "owned-resource-slot", "release-chain", "fastcall-param-named")
            ),
            new Spec(
                "0x00599a3c",
                "CTexture__NodeType12_Dtor_DeleteOnFlag",
                "__thiscall",
                voidPtr,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("delete_flags", uintType)
                },
                true,
                "Wave706 static read-back: scalar-deleting-style wrapper calls CTexture__NodeType12_Dtor_DeleteOnFlag_Body, frees this through OID__FreeObject_Callback when delete_flags bit 0 is set, returns this, and ends with RET 0x4. Static metadata only; exact vtable slot, allocator ownership, runtime texture behavior, and rebuild parity remain unproven.",
                signatureTags("node-type-0x11", "scalar-deleting-dtor", "delete-flag", "phantom-param-removed")
            ),
            new Spec(
                "0x00599a58",
                "CTexture__NodeType12_ScalarDeletingDtor",
                "__thiscall",
                voidPtr,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("delete_flags", uintType)
                },
                true,
                "Wave706 static read-back: scalar-deleting-style wrapper calls CTexture__NodeType12_ScalarDeletingDtor_Body, frees this through OID__FreeObject_Callback when delete_flags bit 0 is set, returns this, and ends with RET 0x4. Static metadata only; exact vtable slot, allocator ownership, runtime texture behavior, and rebuild parity remain unproven.",
                signatureTags("node-type-0x12", "scalar-deleting-dtor", "delete-flag", "phantom-param-removed", "tranche-tail")
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

        println("ApplyNodeTypeLifecycleWave706 mode=" + (dryRun ? "dry" : "apply"));
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
