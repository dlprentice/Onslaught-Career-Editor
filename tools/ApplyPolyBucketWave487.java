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

public class ApplyPolyBucketWave487 extends GhidraScript {
    private static class Spec {
        final String address;
        final String oldName;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] parameters;
        final String comment;
        final String[] tags;

        Spec(
                String address,
                String oldName,
                String name,
                String callingConvention,
                DataType returnType,
                ParameterImpl[] parameters,
                String comment,
                String[] tags) {
            this.address = address;
            this.oldName = oldName;
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
            "polybucket-wave487",
            "retail-binary-evidence",
            "polybucket"
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
            if (!fn.getName().equals(spec.oldName) && !fn.getName().equals(spec.name)) {
                throw new IllegalStateException("Unexpected function name at " + spec.address + ": " + fn.getName());
            }

            boolean needsRename = !fn.getName().equals(spec.name);
            if (dryRun) {
                println("DRY: " + spec.address + " " + fn.getName() + " -> " + expectedSignature(spec));
                if (needsRename) {
                    stats.wouldRename++;
                }
                stats.skipped++;
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

            Function readBack = functionAtEntry(spec.address);
            if (readBack == null) {
                throw new IllegalStateException("Read-back missing at " + spec.address);
            }
            if (!readBack.getName().equals(spec.name)) {
                throw new IllegalStateException("Read-back name mismatch at " + spec.address + ": " + readBack.getName());
            }
            String actualSignature = readBack.getSignature().toString();
            String expectedSignature = expectedSignature(spec);
            if (!actualSignature.equals(expectedSignature)) {
                throw new IllegalStateException(
                    "Read-back signature mismatch at " + spec.address + ": " + actualSignature + " != " + expectedSignature
                );
            }
            if (!spec.comment.equals(readBack.getComment())) {
                throw new IllegalStateException("Read-back comment mismatch at " + spec.address);
            }
            Set<String> actualTags = tagNames(readBack);
            for (String tag : spec.tags) {
                if (!actualTags.contains(tag)) {
                    throw new IllegalStateException("Read-back missing tag at " + spec.address + ": " + tag);
                }
            }

            stats.updated++;
            println("OK: " + spec.address + " " + readBack.getName() + " -> " + actualSignature);
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
        DataType intPtr = new PointerDataType(intType);
        DataType floatType = FloatDataType.dataType;
        DataType floatPtr = new PointerDataType(floatType);
        Spec[] specs = new Spec[] {
            new Spec(
                "0x004d3b10",
                "CPolyBucket__AABBIntersectsSegment2D",
                "CPolyBucket__AABBIntersectsSegment2D",
                "__cdecl",
                intType,
                new ParameterImpl[] {
                    param("rect_x", floatType),
                    param("rect_y", floatType),
                    param("rect_w", floatType),
                    param("rect_h", floatType),
                    param("seg_p0", floatPtr),
                    param("seg_p1", floatPtr)
                },
                "Wave487 comment/tag hardening: this preserved-signature helper rejects a 2D segment against an AABB using endpoint bounds and slope/intersection checks, returns 1 for intersection candidate and 0 for rejection, and is called by CPolyBucket__AdvanceLineSearch when a line step crosses both X and Y cells. Static retail evidence only; exact geometry tolerance, runtime collision behavior, and rebuild parity remain unproven.",
                tags("aabb", "line-search", "comment-hardened", "signature-preserved")
            ),
            new Spec(
                "0x004d3ce0",
                "CPolyBucket__TriangleInBucket",
                "CPolyBucket__TriangleInBucket",
                "__thiscall",
                intType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("triangle_vertices", floatPtr),
                    param("bucket_x", intType),
                    param("bucket_y", intType)
                },
                "Wave487 signature/comment hardening: read-back decompile shows ECX as the CPolyBucket-like object, a triangle vertex float block, and bucket X/Y coordinates. The helper tests whether a triangle overlaps the bucket cell by orienting the triangle consistently and checking the cell corners against the triangle edges. Returns 1 when the cell is accepted and 0 when rejected. Static retail evidence only; exact triangle record layout, winding tolerance, runtime collision behavior, and rebuild parity remain unproven.",
                tags("triangle-placement", "bucket-overlap", "signature-corrected", "comment-hardened")
            ),
            new Spec(
                "0x004d40d0",
                "CPolyBucket__Build",
                "CPolyBucket__Build",
                "__thiscall",
                intType,
                new ParameterImpl[] {param("this", voidPtr), param("mesh_part", voidPtr)},
                "Wave487 signature/comment hardening: CMeshPart__CreatePolyBucket and CStaticShadows__BuildShadowMaps call this builder. It derives bounds and grid dimensions from the mesh-part context, allocates the bucket grid, triangle records, and compressed vertex storage, deduplicates/decompresses vertices, computes per-triangle height masks, places triangles into overlapping cells through CPolyBucket__TriangleInBucket, warns if a triangle is not placed, and shrinks vertex storage at the end. Static retail evidence only; concrete CPolyBucket/CMeshPart layouts, runtime collision/render behavior, and rebuild parity remain unproven.",
                tags("builder", "mesh-part", "static-shadows", "signature-corrected", "comment-hardened")
            ),
            new Spec(
                "0x004d4aa0",
                "CPolyBucket__VertexToCompressed",
                "CPolyBucket__VertexToCompressed",
                "__thiscall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr), param("world_vertex", floatPtr), param("bucket_context", floatPtr)},
                "Wave487 signature/comment hardening: saved this/ECX is the output compressed vertex, not a proven C++ object pointer. The body subtracts bucket origin/base values from the world vertex, divides by the bucket scale, multiplies by the signed-short scale, and writes three compressed coordinates. Static retail evidence only; exact owner/source identity, compression rounding behavior, concrete context layout, and rebuild parity remain unproven.",
                tags("vertex-compression", "helper-ecx", "signature-corrected", "comment-hardened")
            ),
            new Spec(
                "0x004d4b30",
                "CPolyBucket__CompressedToVertex",
                "CPolyBucket__CompressedToVertex",
                "__thiscall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr), param("out_world_vertex", floatPtr), param("bucket_context", floatPtr)},
                "Wave487 signature/comment hardening: saved this/ECX is the compressed vertex pointer, not a proven C++ object pointer. The body expands three signed-short coordinates using the reciprocal short scale and the bucket scale/origin context, then writes the world-space vertex to the output vector. Static retail evidence only; exact owner/source identity, decompression precision, concrete context layout, and rebuild parity remain unproven.",
                tags("vertex-compression", "helper-ecx", "signature-corrected", "comment-hardened")
            ),
            new Spec(
                "0x004d4b90",
                "CPolyBucket__NormalizeVector",
                "CPolyBucket__NormalizeVector",
                "__thiscall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr), param("out_vec3", floatPtr), param("scale", floatType)},
                "Wave487 signature/comment hardening: saved this/ECX is the input vector, not a proven C++ object pointer. The helper divides the input xyz vector by the supplied scale and writes the normalized xyz result to the output vector; CPolyBucket__Build uses it before vertex compression. Static retail evidence only; exact source identity, scale semantics, runtime collision behavior, and rebuild parity remain unproven.",
                tags("vector-normalize", "helper-ecx", "signature-corrected", "comment-hardened")
            ),
            new Spec(
                "0x004d4bc0",
                "CPolyBucket__VertexEquals",
                "CPolyBucket__VertexEquals",
                "__thiscall",
                intType,
                new ParameterImpl[] {param("this", voidPtr), param("vec_b", floatPtr)},
                "Wave487 signature/comment hardening: saved this/ECX is the first vec3 pointer, not a proven C++ object pointer. The body compares xyz floats for exact equality and returns 1 when all three components match, otherwise 0; CPolyBucket__Build uses it during compressed-vertex deduplication. Static retail evidence only; exact equality policy in higher-level collision behavior and rebuild parity remain unproven.",
                tags("vertex-dedup", "helper-ecx", "signature-corrected", "comment-hardened")
            ),
            new Spec(
                "0x004d4c00",
                "CPolyBucket__StartSearch",
                "CPolyBucket__StartSearch",
                "__thiscall",
                voidPtr,
                new ParameterImpl[] {param("this", voidPtr), param("position", floatPtr), param("radius", floatType)},
                "Wave487 signature/comment hardening: CMeshPart__StartTriangleBucketSearch calls this point/radius query initializer. The body validates grid and height scale fields, increments the search generation, stores radius and local query position, computes a Z-height mask and clamped cell range, seeds current cell/list state, and returns the first matching triangle record via CPolyBucket__GetNextTriangle or 0. Static retail evidence only; exact search-state layout, caller contract, runtime collision behavior, and rebuild parity remain unproven.",
                tags("point-search", "query-state", "signature-corrected", "comment-hardened")
            ),
            new Spec(
                "0x004d4f00",
                "CPolyBucket__GetNextTriangle",
                "CPolyBucket__GetNextTriangle",
                "__fastcall",
                voidPtr,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave487 signature/comment hardening: this point-query iterator walks the current bucket list and clamped cell range, skips already-visited triangle records by generation and rejects records whose height mask misses the active query mask, marks accepted records with the current generation, and returns a triangle record pointer or 0. Static retail evidence only; exact triangle record layout, search-state layout, runtime collision behavior, and rebuild parity remain unproven.",
                tags("point-search", "iterator", "signature-corrected", "comment-hardened")
            ),
            new Spec(
                "0x004d50d0",
                "CPolyBucket__StartLineSearch",
                "CPolyBucket__StartLineSearch",
                "__thiscall",
                voidPtr,
                new ParameterImpl[] {param("this", voidPtr), param("start", floatPtr), param("end", floatPtr)},
                "Wave487 signature/comment hardening: CMeshPart__StartLineTriangleBucketSearch calls this segment-query initializer. The body validates grid/height scale fields, converts start/end points into bucket-local coordinates, clips the segment against the polybucket AABB, computes height mask and line stepping globals, seeds current cell/list state, warns on invalid searches or out-of-bucket diffs, and returns the first line-search triangle record via CPolyBucket__GetNextLineTriangle or 0. Static retail evidence only; exact global stepping contract, runtime collision behavior, and rebuild parity remain unproven.",
                tags("line-search", "query-state", "signature-corrected", "comment-hardened")
            ),
            new Spec(
                "0x004d5650",
                "CPolyBucket__AdvanceLineSearch",
                "CPolyBucket__AdvanceLineSearch",
                "__fastcall",
                intType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave487 signature/comment hardening: this line-search stepper advances the global line-search cursor, rounds to bucket cells, handles diagonal moves by consulting CPolyBucket__AABBIntersectsSegment2D, updates current cell fields, and returns 1 while another cell remains or 0 at the end. Static retail evidence only; exact global stepping contract, edge-case clipping behavior, runtime collision behavior, and rebuild parity remain unproven.",
                tags("line-search", "iterator", "aabb", "signature-corrected", "comment-hardened")
            ),
            new Spec(
                "0x004d57c0",
                "CPolyBucket__GetNextLineTriangle",
                "CPolyBucket__GetNextLineTriangle",
                "__thiscall",
                voidPtr,
                new ParameterImpl[] {param("this", voidPtr), param("stop_after_current_cell", intType)},
                "Wave487 signature/comment hardening: this line-query iterator scans the current cell list, applies generation and height-mask filters like the point iterator, returns an accepted triangle record pointer, and otherwise advances through cells with CPolyBucket__AdvanceLineSearch unless the stop_after_current_cell flag halts iteration. Static retail evidence only; exact flag semantics, triangle record layout, runtime collision behavior, and rebuild parity remain unproven.",
                tags("line-search", "iterator", "signature-corrected", "comment-hardened")
            ),
            new Spec(
                "0x004d5930",
                "CPolyBucket__GetRandomTriangle",
                "CPolyBucket__GetRandomTriangle",
                "__thiscall",
                intType,
                new ParameterImpl[] {param("this", voidPtr), param("out_vertex_triplet", intPtr)},
                "Wave487 signature/comment hardening: CMesh__GetRandomVertexFromPolyBucket calls this sampler. The body tries up to 1000 random bucket selections through Random__NextLCGAbs(DAT_008a9d9c), chooses a triangle from a nonempty cell, writes three compressed-vertex pointers through the output triplet, and returns 1 on success or 0 on failure. Static retail evidence only; exact random distribution, particle/effect caller behavior, runtime behavior, and rebuild parity remain unproven.",
                tags("random-triangle", "effects-adjacent", "signature-corrected", "comment-hardened")
            ),
            new Spec(
                "0x004d59f0",
                "CPolyBucket__Load",
                "CPolyBucket__Load",
                "__cdecl",
                voidPtr,
                new ParameterImpl[] {param("chunk_reader", intPtr)},
                "Wave487 signature/comment hardening: CMeshPart__LoadFromStream calls this deserializer. The body allocates a 0xb8-byte CPolyBucket-like object, initializes fields, validates a serialized size of 0xb8, reads grid dimensions and per-cell serialized lists, rebuilds callback/owner arrays and triangle records, reads compressed 6-byte vertices, and returns the loaded object or 0 on failure. Static retail evidence only; exact stream/chunk contract, callback ownership, concrete layout, runtime behavior, and rebuild parity remain unproven.",
                tags("deserialize", "mesh-part", "signature-corrected", "comment-hardened")
            ),
            new Spec(
                "0x004d5e30",
                "CPolyBucket__DebugRender",
                "CPolyBucket__DebugRender",
                "__fastcall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave487 signature/comment hardening: CMeshRenderer__RenderMesh calls this debug renderer. The body sets render states, lazily loads meshtex_default.tga through the global debug texture handle, walks bucket cells and triangle records, decompresses vertices using bucket origin/scale fields, emits debug geometry through vertex/index buffers, renders it, then restores render-state expectations. Static retail evidence only; exact debug toggle path, render resource lifetime, runtime visual behavior, and rebuild parity remain unproven.",
                tags("debug-render", "rendering", "signature-corrected", "comment-hardened")
            ),
            new Spec(
                "0x004d61b0",
                "CPolyBucket__AddVertex",
                "CPolyBucket__AddVertex",
                "__thiscall",
                intType,
                new ParameterImpl[] {param("this", voidPtr), param("compressed_vertex", voidPtr)},
                "Wave487 signature/comment hardening: saved this/ECX is the vertex-store record, not a proven CPolyBucket object pointer. The helper increments the stored count, grows backing storage through CPolyBucket__ReallocFromPool when count reaches capacity, copies one 6-byte compressed vertex into the store, and returns the inserted index. Static retail evidence only; exact store layout, allocator ownership, runtime behavior, and rebuild parity remain unproven.",
                tags("vertex-store", "helper-ecx", "signature-corrected", "comment-hardened")
            ),
            new Spec(
                "0x004d6210",
                "CPolyBucket__ResizeVertexBuffer",
                "CPolyBucket__ResizeVertexBuffer",
                "__thiscall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr), param("new_capacity", intType)},
                "Wave487 signature/comment hardening: saved this/ECX is the vertex-store record, not a proven CPolyBucket object pointer. The helper reallocates backing storage through CPolyBucket__ReallocFromPool for new_capacity * 6 bytes, updates the capacity field and backing pointer when allocation succeeds, and returns without a status value. Static retail evidence only; exact store layout, allocator ownership, failure semantics, runtime behavior, and rebuild parity remain unproven.",
                tags("vertex-store", "helper-ecx", "signature-corrected", "comment-hardened")
            )
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }

        println("--- SUMMARY ---");
        println(
            "updated=" + stats.updated +
            " skipped=" + stats.skipped +
            " created=0 would_create=0 renamed=" + stats.renamed +
            " would_rename=" + stats.wouldRename +
            " missing=" + stats.missing +
            " bad=" + stats.bad
        );
        if (stats.bad > 0 || stats.missing > 0) {
            throw new IllegalStateException("ApplyPolyBucketWave487 failed; see log");
        }
    }
}
