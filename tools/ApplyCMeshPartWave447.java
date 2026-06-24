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

public class ApplyCMeshPartWave447 extends GhidraScript {
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
            "cmeshpart-wave447",
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
                "0x004adff0",
                "CMeshPart__SetVertexCount",
                "__thiscall",
                voidType,
                "Wave447 signature/comment hardening: resets any existing five-pointer vertex channel block at offsets +0x0c..+0x1c, stores the requested count at +0x08, and allocates count*0x14 bytes with MeshPart.cpp line 0x6b before deriving the channel pointers. Static retail decompile/xref evidence only; exact channel names, source-body identity, runtime mesh behavior, and rebuild parity remain unproven.",
                tags("meshpart", "vertex-count", "allocation", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("vertex_count", intType)
                }
            ),
            new Spec(
                "0x004ae110",
                "CMeshPart__StartTriangleBucketSearch",
                "__thiscall",
                intType,
                "Wave447 signature/comment hardening: starts a polybucket triangle search through the part polybucket pointer at +0x100, calls CPolyBucket__StartSearch with two search coordinates/keys, and maps the first three 16-bit local triangle indices through the bucket owner table into the caller output triplet. Static retail decompile/xref evidence only; exact search-key semantics, output layout, runtime collision behavior, and rebuild parity remain unproven.",
                tags("meshpart", "polybucket", "triangle-search", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("search_key0", intType),
                    param("search_key1", intType),
                    param("out_triangle_vertices", voidPtr),
                    param("query_context", voidPtr)
                }
            ),
            new Spec(
                "0x004ae1a0",
                "CMeshPart__GetNextTriangleFromBucketSearch",
                "__thiscall",
                intType,
                "Wave447 signature/comment hardening: advances the active polybucket triangle search with CPolyBucket__GetNextTriangle and maps the returned three 16-bit local indices through the bucket owner table into the caller output triplet. Static retail decompile/xref evidence only; exact search context, output layout, runtime collision behavior, and rebuild parity remain unproven.",
                tags("meshpart", "polybucket", "triangle-search", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("out_triangle_vertices", voidPtr),
                    param("query_context", voidPtr)
                }
            ),
            new Spec(
                "0x004ae220",
                "CMeshPart__StartLineTriangleBucketSearch",
                "__thiscall",
                intType,
                "Wave447 signature/comment hardening: starts a line/polybucket triangle search through the part polybucket pointer at +0x100, calls CPolyBucket__StartLineSearch with two search arguments, and maps the first triangle's three 16-bit local indices into the caller output triplet. Static retail decompile/xref evidence only; exact line-search record layout, runtime collision/shadow behavior, and rebuild parity remain unproven.",
                tags("meshpart", "polybucket", "line-triangle-search", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("line_arg0", intType),
                    param("line_arg1", intType),
                    param("out_triangle_vertices", voidPtr),
                    param("query_context", voidPtr)
                }
            ),
            new Spec(
                "0x004ae2b0",
                "CMeshPart__CreatePolyBucket",
                "__fastcall",
                voidType,
                "Wave447 signature/comment hardening: lazily allocates a 0xb8-byte polybucket-style object at part offset +0x100 for mesh types 1 or 3, clones the mesh part, optionally optimizes the clone unless the current mesh name is on the observed boss_fenrir/tempbuilding3 exclusion path, builds the bucket, frees the bucket on build failure, clears clone material references, and releases the clone. Static retail decompile/xref evidence only; exact bucket type identity, mesh-name helper identity, runtime render/collision behavior, and rebuild parity remain unproven.",
                tags("meshpart", "polybucket", "allocation", "clone", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x004ae430",
                "CMeshPart__GetNextLineTriangleFromBucketSearch",
                "__thiscall",
                intType,
                "Wave447 signature/comment hardening: advances the active line/polybucket search with CPolyBucket__GetNextLineTriangle, then maps the returned three 16-bit local triangle indices through the bucket owner table into the caller output triplet. Static retail decompile/xref evidence only; exact line-search context, output layout, runtime collision/shadow behavior, and rebuild parity remain unproven.",
                tags("meshpart", "polybucket", "line-triangle-search", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("out_triangle_vertices", voidPtr),
                    param("line_search_context", voidPtr),
                    param("query_context", voidPtr)
                }
            ),
            new Spec(
                "0x004ae4b0",
                "CMeshPart__Init",
                "__fastcall",
                voidPtr,
                "Wave447 signature/comment hardening: initializes a CMeshPart-sized record by clearing observed pointer/count fields, copying the global 4x3 basis block into offsets +0x00..+0x2f, seeding defaults including +0x12c = 0.5f, allocating a 0x28-byte helper record at +0xfc and a 0x128-byte CDXMeshVB-style object at +0x138, then back-linking that object at +0x10c to the part. Static retail decompile/xref evidence only; concrete field names, exact source-body identity, runtime mesh behavior, and rebuild parity remain unproven.",
                tags("meshpart", "initializer", "allocation", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x004ae860",
                "CMeshPart__AllocateGeometry",
                "__thiscall",
                intType,
                "Wave447 signature/comment hardening: records DVertex/PVertex/triangle/texcoord/frame counts at +0xa8/+0xac/+0xb0/+0xb8/+0xb4, allocates DVertex storage as count*0x60 at +0x134, allocates per-frame PVertex pointer slots at +0x84, allocates each PVertex frame as pvertex_count*0x10, allocates triangles as triangle_count*0x0c at +0x80, and returns 1 only after all allocations succeed. Static retail decompile/xref evidence only; exact geometry layouts, runtime asset behavior, and rebuild parity remain unproven.",
                tags("meshpart", "geometry-allocation", "vertex-buffer", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("dvertex_count", intType),
                    param("pvertex_count", intType),
                    param("triangle_count", intType),
                    param("texcoord_count", intType),
                    param("frame_count", intType)
                }
            ),
            new Spec(
                "0x004aea50",
                "CMeshPart__ComputeLocalBoundsAndBoundingRadius",
                "__fastcall",
                voidType,
                "Wave447 signature/comment hardening: scans the first per-frame vertex array at +0x84 across +0xac vertices, computes min/max local bounds, writes center/extents/status into the helper record at +0xfc, stores the median extent at part +0x130, computes a bounding radius at +0x12c, clears bounds when helper status is zero, and writes extent magnitude at helper +0x24. Static retail decompile/xref evidence only; exact helper-record layout, source-body identity, runtime culling/collision behavior, and rebuild parity remain unproven.",
                tags("meshpart", "bounds", "bounding-radius", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
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
            throw new RuntimeException("ApplyCMeshPartWave447 failed: bad=" + stats.bad + " missing=" + stats.missing);
        }
    }
}
