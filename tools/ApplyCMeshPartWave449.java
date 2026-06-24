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
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyCMeshPartWave449 extends GhidraScript {
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
            "cmeshpart-wave449",
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

        Spec[] specs = new Spec[] {
            new Spec(
                "0x004af470",
                "CMeshPart__LoadVerticesAndTriangles",
                "__thiscall",
                voidType,
                "Wave449 signature/comment hardening: loads non-skinned DVertex/PVertex/triangle stream data from mem_buffer, negates loaded Z components, clamps material/part indices against part_index_limit, handles DVertex duplication when per-triangle position/normal data diverges, reallocates/remaps the DVertex and triangle arrays, and calls CMeshPart__RebuildPerVertexNormalsAndTangents. The observed caller at 0x004a8f5c plus ret 0x14 show five stack arguments after this; part_table_entry, first_part_record, and unused_legacy_arg are retained to match stack cleanup even though this body currently uses only mem_buffer and part_index_limit. Static retail evidence only; exact stream format names, concrete CMeshPart/DVertex layouts, source-body identity, runtime mesh loading/render behavior, and rebuild parity remain unproven.",
                tags("meshpart", "mesh-load", "vertices", "triangles", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("mem_buffer", voidPtr),
                    param("part_table_entry", voidPtr),
                    param("first_part_record", voidPtr),
                    param("part_index_limit", intType),
                    param("unused_legacy_arg", intType)
                }
            ),
            new Spec(
                "0x004afbb0",
                "CMeshPart__LoadVerticesWithBones",
                "__thiscall",
                voidType,
                "Wave449 signature/comment hardening: loads skinned DVertex/PVertex/triangle data from mem_buffer, uses parent_mesh tables while resolving indices, reads influence_count per-vertex influence records, normalizes/selects top bone weight slots, handles format_tag-specific extra fields, remaps split DVertices, and calls CMeshPart__RebuildPerVertexNormalsAndTangents. The observed caller at 0x004a841d pushes seven stack arguments and the body returns with ret 0x1c. Static retail evidence only; exact stream tag names, bone/influence layout, concrete CMeshPart/DVertex layouts, runtime skinning/render behavior, and rebuild parity remain unproven.",
                tags("meshpart", "mesh-load", "skinned", "bones", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("mem_buffer", voidPtr),
                    param("parent_mesh", voidPtr),
                    param("unused_arg3", intType),
                    param("part_index_limit", intType),
                    param("unused_arg5", intType),
                    param("influence_count", intType),
                    param("format_tag", intType)
                }
            ),
            new Spec(
                "0x004b25d0",
                "CMesh__GetRandomVertexFromPolyBucket",
                "__thiscall",
                voidType,
                "Wave449 signature/comment hardening: writes a random vertex from this mesh/part polybucket into out_vec4. If +0x100 polybucket is missing it logs the fatal warning and zeroes the output; otherwise it calls CPolyBucket__GetRandomTriangle, chooses one of the three short-coordinate vertices with Random__NextLCGAbs % 3, scales by the bucket scale at +0x50 and DAT_005d8618, and adds the bucket origin at +0x40/+0x44/+0x48. Ret 0x4 confirms a single stack output pointer after this and corrects the stale phantom third argument. Static retail evidence only; exact polybucket layout, random distribution semantics, runtime geometry behavior, and rebuild parity remain unproven.",
                tags("mesh", "meshpart", "polybucket", "random-vertex", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("out_vec4", voidPtr)
                }
            ),
            new Spec(
                "0x004b27a0",
                "CMeshPart__LoadFromStream",
                "__cdecl",
                voidPtr,
                "Wave449 signature/comment hardening: cdecl deserializes a 0x13c CMeshPart record from chunk_reader into mesh_part, back-links parent_mesh at +0x128, allocates geometry and optional keyframe/FOV/bone/cache structures, reads DVertices, triangle remaps, per-frame PVertices, material refs, calls CMeshPart__LoadMaterial for material data, reads texcoords, keyframes, bones/weights/slots, optional CPolyBucket__Load data, position/transform caches, and CDXMeshVB data before returning mesh_part. Static retail evidence only; exact chunk tags, concrete layouts, runtime asset loading behavior, and rebuild parity remain unproven.",
                tags("meshpart", "deserialize", "chunk-reader", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("chunk_reader", voidPtr),
                    param("mesh_part", voidPtr),
                    param("parent_mesh", voidPtr)
                }
            ),
            new Spec(
                "0x004b3180",
                "CMeshPart__LoadMaterial",
                "__cdecl",
                voidPtr,
                "Wave449 signature/comment hardening: cdecl material loader advances chunk_reader, allocates a 0x28-byte material record when existing_material is null, reads two 0x10-byte blocks and two trailing dwords into offsets +0x20/+0x24, and returns the material pointer. Static retail evidence only; exact material/shader layout, source identity, runtime render behavior, and rebuild parity remain unproven.",
                tags("meshpart", "material", "chunk-reader", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("chunk_reader", voidPtr),
                    param("existing_material", voidPtr)
                }
            ),
            new Spec(
                "0x004b31f0",
                "CMeshPart__OptimizePolygons",
                "__fastcall",
                voidType,
                "Wave449 signature/comment hardening: fastcall polygon optimizer runs only when the PVertex count at +0xac exceeds 31, allocates per-vertex/per-triangle scratch, uses a 0.2 threshold or 0.3 above 300 vertices, compares triangle neighborhoods and normals, rewrites triangle vertex indices for merge candidates, and reports removed vertices/polys. Static retail evidence only; exact optimization semantics, scratch layout, runtime render/collision effects, and rebuild parity remain unproven.",
                tags("meshpart", "optimize", "polygons", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x004b3b70",
                "CMeshPart__Clone",
                "__fastcall",
                voidPtr,
                "Wave449 signature/comment hardening: fastcall deep-clones a CMeshPart by allocating 0x13c bytes, calling CMeshPart__Init, copying transform/bounds/material/name/link metadata, duplicating child/material arrays and geometry counts, copying DVertices/per-frame PVertices, remapping triangle DVertex pointers, and cloning optional keyframe/FOV/texcoord/bone/weight/slot data. Static retail evidence only; exact ownership semantics, concrete layouts, runtime clone use, and rebuild parity remain unproven.",
                tags("meshpart", "clone", "deep-copy", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x004b4250",
                "CMeshPart__Merge",
                "__thiscall",
                voidType,
                "Wave449 signature/comment hardening: merges source_part into this part, logs the merge, allocates combined PVertex/DVertex/triangle arrays, copies existing geometry, builds/interpolates pose transforms with CMCMech__BuildInterpolatedPoseAndAnchor, transforms source vertices and DVertices through cofactor/determinant matrix math, remaps source triangle pointers by the destination DVertex base offset, and updates geometry counts/pointers. Ret 0x4 confirms one source_part stack argument after this. Static retail evidence only; exact transform semantics, ownership/freeing behavior, runtime render effects, and rebuild parity remain unproven.",
                tags("meshpart", "merge", "geometry", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("source_part", voidPtr)
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
            throw new RuntimeException("ApplyCMeshPartWave449 failed: bad=" + stats.bad + " missing=" + stats.missing);
        }
    }
}
