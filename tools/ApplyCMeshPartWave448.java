//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.FloatDataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.FunctionTag;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyCMeshPartWave448 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final String comment;
        final String[] tags;
        final ParameterImpl[] parameters;

        Spec(
                String address,
                String name,
                String callingConvention,
                DataType returnType,
                String comment,
                String[] tags,
                ParameterImpl[] parameters) {
            this.address = address;
            this.name = name;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.comment = comment;
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
        Address address = toAddr(addressText);
        if (address == null) {
            throw new IllegalArgumentException("Bad address: " + addressText);
        }
        return address;
    }

    private Function functionAtEntry(String addressText) {
        Address entry = addr(addressText);
        Function fn = getFunctionAt(entry);
        if (fn == null) {
            Function containing = getFunctionContaining(entry);
            if (containing != null && containing.getEntryPoint().equals(entry)) {
                fn = containing;
            }
        }
        return fn;
    }

    private ParameterImpl param(String name, DataType dataType) throws Exception {
        return new ParameterImpl(name, dataType, currentProgram);
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
            "cmeshpart-wave448",
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
            Function fn = functionAtEntry(spec.address);
            if (fn == null) {
                stats.missing++;
                println("FAIL: " + spec.address + " " + spec.name + " Function not found");
                return;
            }

            if (!fn.getName().equals(spec.name)) {
                throw new IllegalStateException("Unexpected function name at " + spec.address + ": " + fn.getName());
            }

            if (dryRun) {
                println("DRY: " + spec.address + " " + fn.getName() + " -> " + expectedSignature(spec));
                stats.skipped++;
                return;
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

            Function readBack = functionAtEntry(spec.address);
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
        DataType intType = IntegerDataType.dataType;
        DataType floatType = FloatDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x004b0800",
                "CMeshPart__ApplyRootTransformRecursive",
                "__thiscall",
                voidType,
                "Wave448 signature/comment hardening: corrects the observed stack-cleanup shape for this recursive transform helper. The function returns with ret 0x44, consuming a 12-dword parent transform block, four origin/offset floats, and an optional frame-override part pointer; it recurses through child/material part pointers at +0x94/+0x90, translates +0x60/+0x64/+0x68/+0x6c, rebuilds basis rows via GetBasisX/GetBasisY/CopyPrimaryAxesToOutVec3Triplet, and updates cached frame transform/position blocks. Static retail decompile/instruction evidence only; exact transform field names, source-body identity, runtime mesh/render behavior, and rebuild parity remain unproven.",
                tags("meshpart", "transform", "recursive", "stack-block-signature", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("parent_transform_dword00", intType),
                    param("parent_transform_dword01", intType),
                    param("parent_transform_dword02", intType),
                    param("parent_transform_dword03", intType),
                    param("parent_transform_dword04", intType),
                    param("parent_transform_dword05", intType),
                    param("parent_transform_dword06", intType),
                    param("parent_transform_dword07", intType),
                    param("parent_transform_dword08", intType),
                    param("parent_transform_dword09", intType),
                    param("parent_transform_dword10", intType),
                    param("parent_transform_dword11", intType),
                    param("origin_x", floatType),
                    param("origin_y", floatType),
                    param("origin_z", floatType),
                    param("origin_w", floatType),
                    param("frame_override_part", voidPtr)
                }
            ),
            new Spec(
                "0x004b0c00",
                "CMeshPart__GetBasisX",
                "__thiscall",
                voidPtr,
                "Wave448 signature/comment hardening: writes the X-basis/vector components from part offsets +0x04, +0x14, and +0x24 into the caller output vec3 and returns that output pointer; instruction evidence ends with ret 0x4. Static retail evidence only; exact transform layout, source-body identity, runtime behavior, and rebuild parity remain unproven.",
                tags("meshpart", "basis-vector", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("out_vec3", voidPtr)
                }
            ),
            new Spec(
                "0x004b0c20",
                "CMeshPart__GetBasisY",
                "__thiscall",
                voidPtr,
                "Wave448 signature/comment hardening: writes the Y-basis/vector components from part offsets +0x08, +0x18, and +0x28 into the caller output vec3 and returns that output pointer; instruction evidence ends with ret 0x4. Static retail evidence only; exact transform layout, source-body identity, runtime behavior, and rebuild parity remain unproven.",
                tags("meshpart", "basis-vector", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("out_vec3", voidPtr)
                }
            ),
            new Spec(
                "0x004b0c40",
                "CMeshPart__FindNearestVertexIndex",
                "__thiscall",
                intType,
                "Wave448 signature/comment hardening: scans the first per-frame PVertex array through the pointer at +0x84, compares up to +0xac vertices against the supplied query position, and returns the nearest vertex index. The fourth stack float is retained to match the observed ret 0x10 cleanup but is not used in the distance calculation. Static retail evidence only; exact vertex layout, caller semantics, runtime behavior, and rebuild parity remain unproven.",
                tags("meshpart", "vertex-search", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("query_x", floatType),
                    param("query_y", floatType),
                    param("query_z", floatType),
                    param("query_w_unused", floatType)
                }
            ),
            new Spec(
                "0x004b1a40",
                "CMeshPart__CacheFrameData",
                "__fastcall",
                voidType,
                "Wave448 signature/comment hardening: chooses cached frame count at +0x118 from local/child frame counts, detects identity-transform and zero-position cache shortcuts at +0x120/+0x11c, allocates optional position cache at +0x104 and transform cache at +0x108, then calls CMCMech__BuildInterpolatedPoseAndAnchor for each cached frame before writing transform and position cache records. Static retail evidence only; exact cache layout, source-body identity, runtime animation behavior, and rebuild parity remain unproven.",
                tags("meshpart", "frame-cache", "allocation", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x004b1d30",
                "CMeshPart__LinkDamagedPartVariantsBySuffix",
                "__fastcall",
                voidType,
                "Wave448 signature/comment hardening: scans the parent mesh part table at +0x128/+0x15c/+0x160 for sibling part names that share this part's prefix and continue with the observed _damaged suffix, parses an optional decimal damage number, warns on duplicates, chains variant parts through +0x9c/+0xa0, and marks linked variants at +0xa4. Static retail evidence only; exact damaged-part state layout, source-body identity, runtime damage swap behavior, and rebuild parity remain unproven.",
                tags("meshpart", "damaged-variants", "suffix-scan", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x004b1eb0",
                "CMeshPart__RebuildPerVertexNormalsAndTangents",
                "__thiscall",
                voidType,
                "Wave448 signature/comment hardening: for parts below the observed 10001-DVertex guard, walks each DVertex and all triangles, accumulates normalized face vectors from the first PVertex frame, optionally updates the primary normal when the low byte of update_primary_normal is nonzero, and writes fallback axis vectors when no contributing faces are found. Static retail evidence only; exact normal/tangent field semantics, source-body identity, runtime render behavior, and rebuild parity remain unproven.",
                tags("meshpart", "normals", "tangents", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("update_primary_normal", intType)
                }
            ),
            new Spec(
                "0x004b24d0",
                "CMeshPart__ResolveWrappedFrameIndexAndLerp",
                "__thiscall",
                intType,
                "Wave448 signature/comment hardening: when the parent mesh frame table is present and this part has multiple frames, uses frame_table_index and frame_delta to compute an animation frame value, optionally lets frame_adjuster vfunc +0x14 mutate that value, stores the fractional lerp in out_lerp, and returns the rounded frame index wrapped by the part frame count. The fallback path runs the same adjuster/rounding flow around zero. Static retail evidence only; exact frame-table layout, adjuster owner, runtime animation behavior, and rebuild parity remain unproven.",
                tags("meshpart", "frame-resolve", "animation", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("frame_delta", floatType),
                    param("frame_table_index", intType),
                    param("out_lerp", voidPtr),
                    param("frame_adjuster", voidPtr)
                }
            )
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }

        println("SUMMARY updated=" + stats.updated
            + " skipped=" + stats.skipped
            + " created=0 would_create=0"
            + " renamed=" + stats.renamed
            + " would_rename=" + stats.wouldRename
            + " missing=" + stats.missing
            + " bad=" + stats.bad);
        if (stats.bad > 0 || stats.missing > 0) {
            throw new RuntimeException("ApplyCMeshPartWave448 failed: bad=" + stats.bad + " missing=" + stats.missing);
        }
    }
}
