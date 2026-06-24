//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.FloatDataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.ShortDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.FunctionTag;
import ghidra.program.model.listing.Parameter;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyBattleLineTriangulateWave521 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] parameters;
        final String comment;
        final String[] tags;
        final boolean renameAllowed;

        Spec(String address, String name, String callingConvention, DataType returnType,
                ParameterImpl[] parameters, String comment, String[] tags, boolean renameAllowed) {
            this.address = address;
            this.name = name;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.parameters = parameters;
            this.comment = comment;
            this.tags = tags;
            this.renameAllowed = renameAllowed;
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

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "battleline-triangulate-wave521",
            "retail-binary-evidence",
            "signature-corrected",
            "comment-hardened"
        };
        String[] result = new String[common.length + extras.length];
        System.arraycopy(common, 0, result, 0, common.length);
        System.arraycopy(extras, 0, result, common.length, extras.length);
        return result;
    }

    private String expectedSignature(Spec spec) {
        StringBuilder sb = new StringBuilder();
        sb.append(spec.returnType.getDisplayName()).append(" ")
            .append(spec.callingConvention).append(" ")
            .append(spec.name).append("(");
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
        Set<String> existing = new HashSet<>();
        for (FunctionTag tag : fn.getTags()) {
            existing.add(tag.getName());
        }
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
        if (!spec.comment.equals(readBack.getComment())) {
            throw new IllegalStateException("Read-back comment mismatch at " + spec.address);
        }
        if (!hasAllTags(readBack, spec.tags)) {
            throw new IllegalStateException("Read-back tag mismatch at " + spec.address);
        }
    }

    private void applySpec(Spec spec, boolean dryRun, Stats stats) throws Exception {
        Function fn = functionAtEntry(spec.address);
        if (fn == null) {
            println("MISSING: " + spec.address);
            stats.missing++;
            return;
        }
        if (!fn.getName().equals(spec.name)) {
            if (!spec.renameAllowed) {
                println("BADNAME: " + spec.address + " " + fn.getName() + " expected " + spec.name);
                stats.bad++;
                return;
            }
            if (dryRun) {
                println("DRYRENAME: " + spec.address + " " + fn.getName() + " -> " + spec.name);
                stats.wouldRename++;
                stats.skipped++;
                return;
            }
            fn.setName(spec.name, SourceType.USER_DEFINED);
            stats.renamed++;
        }
        if (!needsUpdate(fn, spec)) {
            println("SKIP: " + spec.address + " " + spec.name);
            stats.skipped++;
            return;
        }
        if (dryRun) {
            println("DRY: " + spec.address + " " + spec.name + " :: " + expectedSignature(spec));
            stats.skipped++;
            return;
        }

        fn.setCallingConvention(spec.callingConvention);
        fn.setReturnType(spec.returnType, SourceType.USER_DEFINED);
        fn.replaceParameters(FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS, true, SourceType.USER_DEFINED, spec.parameters);
        fn.setComment(spec.comment);
        for (String tag : spec.tags) {
            fn.addTag(tag);
        }
        verifyReadBack(spec);
        println("OK: " + spec.address + " " + spec.name + " :: " + expectedSignature(spec));
        stats.updated++;
        Thread.sleep(50);
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");
        println("Mode: " + (dryRun ? "dry" : "apply"));

        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);
        DataType shortPtr = new PointerDataType(ShortDataType.dataType);
        DataType intType = IntegerDataType.dataType;
        DataType floatType = FloatDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x004f7170",
                "Triangulate__CreateQuadMesh",
                "__thiscall",
                voidPtr,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("max_vertices", intType),
                    param("min_x", floatType),
                    param("min_y", floatType),
                    param("max_x", floatType),
                    param("max_y", floatType),
                    param("subdivision_mode", intType)
                },
                "Wave521 Triangulate signature/comment hardening: RET 0x18 and the CDXBattleLine__BuildMesh caller show an ECX Triangulate work object plus six stack arguments. The body allocates an XY vertex buffer at max_vertices*8 bytes and a ushort-triangle buffer at max_vertices*0x0c bytes, stores capacity at this+0x10, seeds the four bounds corners, emits 4 vertices/2 triangles for subdivision mode 0, and emits 8 vertices/6 triangles with midpoint vertices for subdivision mode 1. Static retail evidence only; exact source type/layout, runtime influence-map mesh behavior, BEA patching, and rebuild parity remain unproven.",
                tags("triangulate", "quad-mesh", "battleline-mesh", "allocator"),
                false
            ),
            new Spec(
                "0x004f7460",
                "Triangulate__InsertPointOrAppendVertex",
                "__thiscall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr), param("point_xy", voidPtr)},
                "Wave521 Triangulate owner/signature/comment correction: RET 0x4 shows one stack argument after ECX, and CDXBattleLine__BuildMesh passes the Triangulate work object returned by Triangulate__CreateQuadMesh rather than the outer CDXBattleLine object. The helper scans the triangle array at this+0x04 for the active triangle count at this+0x0c, calls Triangulate__SplitTriangleAtPointAndLegalizeEdges on each candidate, and appends the XY point to the vertex array at this+0x00/this+0x08 when no containing triangle accepts it. Static retail evidence only; exact source name, structure field names, runtime overlay mesh behavior, BEA patching, and rebuild parity remain unproven.",
                tags("triangulate", "battleline-mesh", "point-insertion", "topology", "owner-corrected"),
                true
            ),
            new Spec(
                "0x004f74b0",
                "Triangulate__SplitTriangleAtPointAndLegalizeEdges",
                "__thiscall",
                intType,
                new ParameterImpl[] {param("this", voidPtr), param("triangle_indices", voidPtr), param("point_xy", voidPtr)},
                "Wave521 Triangulate owner/signature/comment correction: RET 0x8 shows two stack arguments after ECX, and all observed callers pass the Triangulate work object. The body capacity-checks vertex_count against this+0x10, uses three oriented-area tests against epsilon 0x005d856c to decide whether point_xy lies inside the input ushort triangle, rewrites the hit triangle, appends two triangle triplets, writes the new point to the vertex buffer, increments vertex/triangle counts, and tries quality flips on the three new shared edges. Static retail evidence only; exact source name, winding convention, runtime triangulation result, BEA patching, and rebuild parity remain unproven.",
                tags("triangulate", "battleline-mesh", "triangle-split", "edge-flip", "owner-corrected"),
                true
            ),
            new Spec(
                "0x004f7660",
                "Triangulate__TryFlipSharedEdgeForQuality",
                "__thiscall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr), param("edge_start", intType), param("edge_end", intType)},
                "Wave521 Triangulate owner/signature/comment correction: RET 0x8 shows two stack arguments after ECX, and callers in the same topology helper island pass the Triangulate work object. The helper finds triangles on both sides of the directed edge, compares shared-edge length against the opposite diagonal, applies oriented-area quality gates using epsilon 0x005d856c and ratio threshold 0x005d85f8, flips the shared edge by swapping the third vertices when the quality test improves, and sets the dirty flag at this+0x14. Static retail evidence only; exact source name, geometric heuristic, runtime mesh quality behavior, BEA patching, and rebuild parity remain unproven.",
                tags("triangulate", "battleline-mesh", "edge-flip", "quality-gate", "owner-corrected"),
                true
            ),
            new Spec(
                "0x004f78c0",
                "Triangulate__FindTriangleByDirectedEdge",
                "__thiscall",
                shortPtr,
                new ParameterImpl[] {param("this", voidPtr), param("edge_start", intType), param("edge_end", intType)},
                "Wave521 Triangulate owner/signature/comment correction: RET 0x8 shows two stack arguments after ECX, and the edge-flip caller passes the Triangulate work object. The helper scans the ushort triangle triplets at this+0x04 for the active count at this+0x0c, returns a pointer when the requested directed edge is already the first two indices, or rotates a matching triangle in place so the requested edge becomes the first two indices before returning it; absent edges return null. Static retail evidence only; exact source name, triangle-record type, runtime topology behavior, BEA patching, and rebuild parity remain unproven.",
                tags("triangulate", "battleline-mesh", "directed-edge", "triangle-lookup", "owner-corrected"),
                true
            ),
            new Spec(
                "0x004f7940",
                "Triangulate__RelaxMeshByEdgeFlips",
                "__fastcall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave521 Triangulate owner/signature/comment correction: ECX carries the Triangulate work object and the body returns without stack cleanup. The helper sets the dirty flag at this+0x14, then performs up to ten passes over all active triangle triplets, clearing the flag each pass and calling Triangulate__TryFlipSharedEdgeForQuality for each of the three directed edges until no flip marks the mesh dirty. Static retail evidence only; exact source name, convergence contract, runtime overlay mesh behavior, BEA patching, and rebuild parity remain unproven.",
                tags("triangulate", "battleline-mesh", "edge-flip", "mesh-relaxation", "owner-corrected"),
                true
            )
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }

        println("SUMMARY updated=" + stats.updated +
            " skipped=" + stats.skipped +
            " renamed=" + stats.renamed +
            " would_rename=" + stats.wouldRename +
            " missing=" + stats.missing +
            " bad=" + stats.bad);
    }
}
