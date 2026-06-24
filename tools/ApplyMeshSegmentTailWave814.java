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
import ghidra.program.model.listing.Parameter;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyMeshSegmentTailWave814 extends GhidraScript {
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
            "mesh-segment-tail-wave814",
            "wave814-readback-verified",
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
        DataType charPtr = new PointerDataType(CharDataType.dataType);
        DataType intType = IntegerDataType.dataType;
        DataType intPtr = new PointerDataType(intType);

        Spec[] specs = new Spec[] {
            new Spec(
                "0x004aa4e0",
                "CMesh__SumChainedField1C",
                new String[] {"CRTMesh__SumSubtreeField1C"},
                "__thiscall",
                intType,
                new ParameterImpl[] {
                    param("this", voidPtr)
                },
                "Wave814 static read-back correction: recursively follows the mesh/resource chain pointer at this+0x08 and sums each node's field +0x1c. CRTMesh__Init calls this on its CMesh/resource pointer at this+0x14 to count chained records before scanning underscore-prefixed material/effect names. Static retail Ghidra evidence only; exact field +0x1c meaning, concrete mesh/resource layout, runtime RTMesh effect behavior, BEA patching, and rebuild parity remain deferred.",
                tags("cmesh", "rtmesh-caller", "owner-corrected", "signature-corrected", "mesh-chain")
            ),
            new Spec(
                "0x004aa500",
                "CMesh__GetChainedRecordNameAndIdByIndex",
                new String[] {"CRTMesh__GetMaterialNameAndIdByIndex"},
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("record_index", intType),
                    param("out_name", voidPtr),
                    param("out_record_id", intPtr)
                },
                "Wave814 static read-back correction: resolves a flat record_index across the same this+0x08 chained mesh/resource nodes, copies the selected 0x150-byte record's string at +0x4c into out_name, and writes record field +0x14c to out_record_id. If the chain is exhausted, it copies the empty string at 0x00662b2c and writes -1. CRTMesh__Init uses this after CMesh__SumChainedField1C while building underscore-prefixed effect/material arrays. RET 0xc proves three stack arguments after this and removes the stale unused_ctx parameter. Static retail Ghidra evidence only; exact record layout, id meaning, runtime effect behavior, BEA patching, and rebuild parity remain deferred.",
                tags("cmesh", "rtmesh-caller", "owner-corrected", "signature-corrected", "mesh-chain", "record-lookup")
            ),
            new Spec(
                "0x004aa6b0",
                "CMesh__GetNameOrUnknown",
                new String[] {"CDestructableSegmentsController__FindMeshNameByIdOrUnknown"},
                "__thiscall",
                voidPtr,
                new ParameterImpl[] {
                    param("this", voidPtr)
                },
                "Wave814 static read-back correction: scans global mesh list DAT_00704ad8 by following next-link +0x158 until it finds the CMesh pointer in ECX/this, returning the mesh name at +0x24; if not found, returns string 0x0062f8d4 (unknown mesh name). DestructableSegmentsController, CHud, and CMeshPart__CreatePolyBucket callers set ECX to a mesh/resource pointer and leave later printf/stricmp arguments on the stack, proving the old controller-specific one-stack-argument signature was stale. Static retail Ghidra evidence only; exact CMesh layout, caller source identity, runtime logging behavior, BEA patching, and rebuild parity remain deferred.",
                tags("cmesh", "mesh-name", "owner-corrected", "signature-corrected", "global-list")
            ),
            new Spec(
                "0x004aa8a0",
                "CMesh__FindPartByNameI",
                new String[] {"CDestroyableSegment__FindChildByNameI"},
                "__thiscall",
                voidPtr,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("part_name", charPtr)
                },
                "Wave814 static read-back correction: scans the CMesh part pointer table at this+0x160 for count this+0x15c, compares each part name at part+0xdc against part_name with stricmp, returns the matching part pointer, or returns null. DestructableSegmentsController name-dispatch helpers and shared grounded-unit init callers first obtain a mesh/resource pointer through vtable slot +0x24 before calling this helper. RET 0x4 proves one stack argument after this and removes the stale unused_ctx parameter. Static retail Ghidra evidence only; exact CMeshPart layout, source method name, runtime destruction/ground-unit behavior, BEA patching, and rebuild parity remain deferred.",
                tags("cmesh", "mesh-part-lookup", "owner-corrected", "signature-corrected", "case-insensitive-name")
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
            throw new IllegalStateException("Wave814 apply failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
