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

public class ApplyMeshPartTailWave815 extends GhidraScript {
    private static class Spec {
        final String address;
        final String expectedName;
        final String[] allowedExistingNames;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] parameters;
        final String comment;
        final String[] tags;

        Spec(String address, String expectedName, String[] allowedExistingNames,
                String callingConvention, DataType returnType, ParameterImpl[] parameters,
                String comment, String[] tags) {
            this.address = address;
            this.expectedName = expectedName;
            this.allowedExistingNames = allowedExistingNames;
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
            "meshpart-tail-wave815",
            "wave815-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "raw-commentless-tail"
        };
        String[] result = new String[common.length + extras.length];
        System.arraycopy(common, 0, result, 0, common.length);
        System.arraycopy(extras, 0, result, common.length, extras.length);
        return result;
    }

    private boolean allowedName(Spec spec, String actual) {
        if (actual.equals(spec.expectedName)) {
            return true;
        }
        for (String allowed : spec.allowedExistingNames) {
            if (actual.equals(allowed)) {
                return true;
            }
        }
        return false;
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

    private Set<String> tagNames(Function fn) {
        Set<String> names = new HashSet<>();
        for (FunctionTag tag : fn.getTags()) {
            names.add(tag.getName());
        }
        return names;
    }

    private boolean hasAllTags(Function fn, String[] tags) {
        Set<String> actual = tagNames(fn);
        for (String tag : tags) {
            if (!actual.contains(tag)) {
                return false;
            }
        }
        return true;
    }

    private String expectedSignature(Spec spec) {
        StringBuilder sb = new StringBuilder();
        sb.append(spec.returnType.getDisplayName()).append(" ")
            .append(spec.callingConvention).append(" ")
            .append(spec.expectedName).append("(");
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

    private void readBack(Spec spec, Function fn, Stats stats) {
        boolean ok = true;
        if (!fn.getName().equals(spec.expectedName)) {
            println("BADNAME: " + spec.address + " expected " + spec.expectedName + " got " + fn.getName());
            ok = false;
        }
        if (!signatureMatches(fn, spec)) {
            println("BADSIG: " + spec.address + " expected " + expectedSignature(spec) + " got " + fn.getSignature());
            ok = false;
        }
        if (!spec.comment.equals(fn.getComment())) {
            println("BADCOMMENT: " + spec.address);
            ok = false;
        }
        if (!hasAllTags(fn, spec.tags)) {
            println("BADTAGS: " + spec.address);
            ok = false;
        }
        if (!ok) {
            stats.bad++;
        }
    }

    private void applySpec(Spec spec, boolean dryRun, Stats stats) throws Exception {
        Function fn = functionAtEntry(spec.address);
        if (fn == null) {
            println("MISSING: " + spec.address);
            stats.missing++;
            return;
        }
        if (!allowedName(spec, fn.getName())) {
            println("BADNAME: " + spec.address + " unexpected " + fn.getName());
            stats.bad++;
            return;
        }

        boolean needsRename = !fn.getName().equals(spec.expectedName);
        boolean needsSignature = !signatureMatches(fn, spec);
        boolean needsCommentOrTags = !spec.comment.equals(fn.getComment()) || !hasAllTags(fn, spec.tags);
        if (needsRename) {
            if (dryRun) {
                stats.wouldRename++;
            } else {
                stats.renamed++;
            }
        }
        if (needsSignature) {
            stats.signatureUpdated++;
        }
        if (needsCommentOrTags) {
            stats.commentOnlyUpdated++;
        }

        if (!needsRename && !needsSignature && !needsCommentOrTags) {
            println((dryRun ? "DRY" : "SKIP") + ": " + spec.address + " " + fn.getName() + " already matched");
            stats.skipped++;
            return;
        }
        if (dryRun) {
            println("DRY: " + spec.address + " " + fn.getName() + " -> " + expectedSignature(spec));
            stats.skipped++;
            return;
        }

        if (needsRename) {
            fn.setName(spec.expectedName, SourceType.USER_DEFINED);
        }
        if (needsSignature) {
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

        Function readBack = functionAtEntry(spec.address);
        if (readBack == null) {
            println("MISSING-READBACK: " + spec.address);
            stats.missing++;
        } else {
            readBack(spec, readBack, stats);
            println("OK: " + spec.address + " " + readBack.getSignature());
        }
        stats.updated++;
        Thread.sleep(50);
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");

        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);
        DataType intType = IntegerDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x004adf80",
                "CMesh__ClearField08",
                new String[] {},
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr)
                },
                "Wave815 static read-back: clears field +0x08 on the 0x24-byte CMesh embedded resource/material record. Evidence: CMesh__InitStatic calls this immediately after allocating the default record, while CMesh__Load and CMesh__Deserialize pass it to eh_vector_constructor_iterator for 0x24-byte record arrays paired with CMesh__ReleaseEmbeddedResources. Static retail Ghidra evidence only; exact concrete record type, field +0x08 meaning, runtime mesh loading behavior, BEA patching, and rebuild parity remain deferred.",
                tags("cmesh", "mesh-resource-record", "constructor-helper")
            ),
            new Spec(
                "0x004ae640",
                "CMeshPart__FreeOwnedResourcePointers",
                new String[] {"CMeshPart__FreeOwnedResourcePointers_004ae640"},
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr)
                },
                "Wave815 static read-back correction: shared CMeshPart owned-resource free body reached by the 0x004a51f0 CMeshPart__FreeResources tail entry and by CMeshPart__CreatePolyBucket failure cleanup. It frees pointer fields and arrays at observed offsets including +0x104, +0x108, +0x94, +0x134, frame pointer table +0x84 for count +0xb4, triangle pointer +0x80, texcoord/material arrays +0xc4/+0xc8/+0xcc/+0xd0/+0xd4/+0xd8/+0x10c, polybucket +0x100 through CPolyBucket__FreeBuffers, helper +0xfc, and vtable-owned field +0x138. Static retail Ghidra evidence only; exact CMeshPart field names, destructor ownership, runtime render/collision behavior, BEA patching, and rebuild parity remain deferred.",
                tags("meshpart", "resource-free", "owner-corrected", "signature-corrected", "tail-entry-body")
            ),
            new Spec(
                "0x004aede0",
                "CMeshPart__LoadOldStyle_VersionA",
                new String[] {},
                "__thiscall",
                intType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("mem_buffer", voidPtr),
                    param("parent_mesh", voidPtr),
                    param("mesh_resource_records", voidPtr),
                    param("material_index_limit", intType),
                    param("legacy_flags_or_zero", intType)
                },
                "Wave815 static read-back correction: old-style CMeshPart loader for the earliest observed old-style version token. CMesh__Load calls this with ECX set to the part pointer, pushes mem_buffer, parent CMesh, parent resource/material records, a material-index limit, and a zero legacy/reserved argument; the epilogue RET 0x14 proves five stack arguments after this, replacing the stale locked no-argument signature. The body reads 0x60-byte vertex/material records, negates loaded Z, clamps material indices below -2 or at/above material_index_limit, initializes six material slots, deserializes per-frame vertex triplets, transforms vertices through the part matrix/origin fields, builds triangle vertex pointers, and calls CMeshPart__RebuildPerVertexNormalsAndTangents(this, 1). Static retail Ghidra evidence only; exact old mesh-format schema, exact source-body identity, unused/reserved argument semantics, runtime asset behavior, BEA patching, and rebuild parity remain deferred.",
                tags("meshpart", "old-style-loader", "signature-corrected", "ret-0x14", "abi-corrected")
            ),
            new Spec(
                "0x004af110",
                "CMeshPart__LoadOldStyle_VersionB_WithExtraBlock",
                new String[] {},
                "__thiscall",
                intType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("mem_buffer", voidPtr),
                    param("parent_mesh", voidPtr),
                    param("mesh_resource_records", voidPtr),
                    param("material_index_limit", intType),
                    param("legacy_flags_or_zero", intType)
                },
                "Wave815 static read-back correction: adjacent old-style CMeshPart loader for the next observed old-style version token. CMesh__Load calls this with the same ECX part pointer and five stack arguments as VersionA, and the epilogue RET 0x14 proves the same ABI rather than the stale locked no-argument signature. Relative to VersionA, this loader also consumes an extra 4-byte block for each count at part offset +0xb8 before the per-frame vertex triplet loop, then applies the same vertex transform, triangle pointer build, and CMeshPart__RebuildPerVertexNormalsAndTangents(this, 1) path. Static retail Ghidra evidence only; exact old mesh-format schema, extra-block field meaning, exact source-body identity, runtime asset behavior, BEA patching, and rebuild parity remain deferred.",
                tags("meshpart", "old-style-loader", "signature-corrected", "ret-0x14", "extra-block")
            )
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }

        println("SUMMARY: updated=" + stats.updated +
            " skipped=" + stats.skipped +
            " renamed=" + stats.renamed +
            " would_rename=" + stats.wouldRename +
            " signature_updated=" + stats.signatureUpdated +
            " comment_only_updated=" + stats.commentOnlyUpdated +
            " missing=" + stats.missing +
            " bad=" + stats.bad);
        if (stats.missing != 0 || stats.bad != 0) {
            throw new IllegalStateException("Wave815 apply failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
