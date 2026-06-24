//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.BooleanDataType;
import ghidra.program.model.data.ByteDataType;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.FloatDataType;
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

public class ApplyStaticShadowsWave511 extends GhidraScript {
    private static class Spec {
        final String address;
        final String oldName;
        final String newName;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] parameters;
        final String comment;
        final String[] tags;

        Spec(String address, String oldName, String newName, String callingConvention,
                DataType returnType, ParameterImpl[] parameters, String comment, String[] tags) {
            this.address = address;
            this.oldName = oldName;
            this.newName = newName;
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

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "static-shadows-wave511",
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
            .append(spec.newName).append("(");
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
        if (!fn.getName().equals(spec.newName)) {
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

    private void applySpec(Spec spec, boolean dryRun, Stats stats) throws Exception {
        Function fn = functionAtEntry(spec.address);
        if (fn == null) {
            println("MISSING: " + spec.address);
            stats.missing++;
            return;
        }

        String currentName = fn.getName();
        if (!currentName.equals(spec.oldName) && !currentName.equals(spec.newName)) {
            println("BADNAME: " + spec.address + " " + currentName + " expected " + spec.oldName + " or " + spec.newName);
            stats.bad++;
            return;
        }

        boolean renameNeeded = !currentName.equals(spec.newName);
        boolean updateNeeded = needsUpdate(fn, spec);
        if (!updateNeeded) {
            println("SKIP: " + spec.address + " " + spec.newName);
            stats.skipped++;
            return;
        }

        if (dryRun) {
            println("DRY: " + spec.address + " " + currentName + " -> " + spec.newName + " :: " + expectedSignature(spec));
            stats.skipped++;
            if (renameNeeded) {
                stats.wouldRename++;
            }
            return;
        }

        if (renameNeeded) {
            fn.setName(spec.newName, SourceType.USER_DEFINED);
            stats.renamed++;
        }
        fn.setCallingConvention(spec.callingConvention);
        fn.setReturnType(spec.returnType, SourceType.USER_DEFINED);
        fn.replaceParameters(FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS, true, SourceType.USER_DEFINED, spec.parameters);
        fn.setComment(spec.comment);
        for (String tag : spec.tags) {
            fn.addTag(tag);
        }
        println("OK: " + spec.address + " " + spec.newName + " :: " + expectedSignature(spec));
        stats.updated++;
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");
        println("Mode: " + (dryRun ? "dry" : "apply"));

        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);
        DataType boolType = BooleanDataType.dataType;
        DataType intType = IntegerDataType.dataType;
        DataType byteType = ByteDataType.dataType;
        DataType floatType = FloatDataType.dataType;
        DataType floatPtr = new PointerDataType(floatType);

        Spec[] specs = new Spec[] {
            new Spec(
                "0x004eba30",
                "CEngine__SetVertexShaderPathEnabled",
                "CEngine__SetVertexShaderPathEnabled",
                "__stdcall",
                voidType,
                new ParameterImpl[] {param("enable_vertex_shader_path", intType)},
                "Wave511 signature/comment hardening: render-state helper used by world/cube/shader render paths to toggle the vertex-shader path. RET 0x4 proves one stack argument; the body gates on global shader support, updates object/light setup when enabled, and falls back to render-state dword 0x98 when disabled. Static retail evidence only; exact CDXEngine/CEngine state layout, runtime shader behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("engine", "render-state", "vertex-shader")
            ),
            new Spec(
                "0x004ebbc0",
                "CGame__InitStaticShadowBuildState",
                "CStaticShadows__Initialise",
                "__fastcall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave511 stale-owner/signature correction: CStaticShadows initialise body. CGame init calls this with ECX=0x009c8010, matching the source-level STATICSHADOWS.Initialise call; the body registers the BuildStaticShadows console command, clears the 64x64 global shadow-cell pointer grid at this+0x18, clears the list/tail fields at +0x4/+0x4018, and installs the command callback at 0x004ebbb0. Static retail evidence only; exact CStaticShadows layout, source-body parity, runtime command behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("static-shadows", "initialise", "build-command", "stale-owner-corrected")
            ),
            new Spec(
                "0x004ebd10",
                "CStaticShadows__ClearAllShadowEntries",
                "CStaticShadows__ClearAllShadowEntries",
                "__fastcall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave511 signature/comment hardening: CStaticShadows list/grid cleanup body. The ECX-only function walks the linked shadow-entry list, forces per-thing visibility removal, destroys each shadow-map entry array through the deleting-destructor helper, frees entry nodes, and clears the cached 64x64 grid cells. Static retail evidence only; exact entry/list/grid layout, shutdown naming, runtime detach behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("static-shadows", "cleanup", "shadow-grid", "linked-list")
            ),
            new Spec(
                "0x004ebdf0",
                "CStaticShadows__Destructor",
                "CStaticShadows__ShadowMapEntryDestructor",
                "__fastcall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave511 stale-purpose/signature correction: per-shadow-map-entry destructor callback, not the top-level CStaticShadows manager destructor. The ECX-only body frees each 0x200-byte bitmap cell pointer in the width*height array at entry+0x10, then frees the pointer array; it is passed to MSVC vector construction/destruction helpers for 0x1c-byte entries. Static retail evidence only; exact entry struct name/layout, ownership lifetime, runtime shadow-map behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("static-shadows", "shadow-map-entry", "destructor", "stale-purpose-corrected")
            ),
            new Spec(
                "0x004ebe40",
                "CStaticShadows__UpdateLightVectorAndRebuild",
                "CStaticShadows__UpdateLightVectorAndRebuild",
                "__fastcall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave511 signature/comment hardening: BuildStaticShadows command target and static-shadow rebuild entry point. The ECX-only body refreshes/normalizes light-vector fields from global light direction, enumerates eligible objects when the skip flag is clear, allocates 0x24-byte linked shadow entries, binds entries back to things, and calls CStaticShadows__BuildShadowMaps. Static retail evidence only; exact eligibility rules, source-body parity, runtime rebuild behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("static-shadows", "rebuild", "light-vector", "build-command")
            ),
            new Spec(
                "0x004ebfb0",
                "CStaticShadows__UpdateVisibility",
                "CStaticShadows__UpdateVisibility",
                "__stdcall",
                voidType,
                new ParameterImpl[] {param("thing", voidPtr), param("force_update", intType)},
                "Wave511 signature/comment hardening: static-shadow visibility refresher for a thing. RET 0x8 proves two stack arguments; the body rate-limits normal updates, queries the thing static-shadow payload and render mesh, compares per-submesh visibility, clears overlapped grid cells, reapplies intersecting shadow entries, invalidates landscape tiles, and clears the thing shadow pointer when forced. Static retail evidence only; exact CThing/static-shadow/render-mesh layouts, runtime visibility behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("static-shadows", "visibility", "shadow-grid", "thing")
            ),
            new Spec(
                "0x004ec250",
                "CStaticShadows__DestroyShadowMapNode",
                "CStaticShadows__ShadowMapEntryDeletingDestructor",
                "__thiscall",
                voidPtr,
                new ParameterImpl[] {param("this", voidPtr), param("flags", byteType)},
                "Wave511 stale-purpose/signature correction: scalar/vector deleting destructor wrapper for shadow-map entries. RET 0x4 proves one flags argument; flags&2 routes to the vector destructor helper with 0x1c-byte entries and CStaticShadows__ShadowMapEntryDestructor, while the scalar path frees the entry bitmap pointer array and optionally frees this on flags&1. Static retail evidence only; exact MSVC destructor ownership, entry layout, runtime lifetime behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("static-shadows", "shadow-map-entry", "deleting-destructor", "stale-purpose-corrected")
            ),
            new Spec(
                "0x004ec2f0",
                "CStaticShadows__BuildShadowMaps",
                "CStaticShadows__BuildShadowMaps",
                "__fastcall",
                voidType,
                new ParameterImpl[] {param("shadow_entry", voidPtr)},
                "Wave511 signature/comment hardening: main static-shadow map builder for one linked shadow entry. The ECX-only body allocates a 0x1c-byte entry array from the render mesh count, samples terrain height, traces against the heightfield, runs ray-triangle intersection tests for shadow casting, allocates 0x200-byte bitmap cells, records entry grid bounds, and finally applies the generated maps to the global grid. Static retail evidence only; exact mesh/terrain/light/data layouts, runtime shadow quality behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("static-shadows", "build", "heightfield", "ray-triangle", "shadow-grid")
            ),
            new Spec(
                "0x004ee0d0",
                "CStaticShadows__CleanupHelper",
                "CPolyBucket__ScalarDeletingDestructor",
                "__thiscall",
                voidPtr,
                new ParameterImpl[] {param("this", voidPtr), param("flags", byteType)},
                "Wave511 stale-owner/signature correction: CPolyBucket scalar-deleting destructor wrapper reached from static-shadow build cleanup. RET 0x4 proves one flags argument; the body calls CPolyBucket__FreeBuffers and optionally frees this through CDXMemoryManager__Free when flags&1 is set. Static retail evidence only; exact CPolyBucket layout/owner, cleanup callsite context, runtime render-buffer behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("polybucket", "scalar-deleting", "destructor", "stale-owner-corrected")
            ),
            new Spec(
                "0x004ee0f0",
                "CStaticShadows__ApplyShadowsToGrid",
                "CStaticShadows__ApplyShadowsToGrid",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("start_x", intType),
                    param("start_y", intType),
                    param("width", intType),
                    param("height", intType)
                },
                "Wave511 signature/comment hardening: applies one linked shadow entry into the global 64x64 shadow-cell grid. RET 0x10 proves four explicit rectangle arguments after ECX; -1 arguments fall back to the entry bounds, missing RTMesh is logged, destination cells allocate 0x200-byte bitmaps, and per-entry bitmaps are OR-composited into overlapped grid cells. Static retail evidence only; exact grid-cell bitmap semantics, render-mesh layout, runtime terrain invalidation, BEA launch, patching, and rebuild parity remain unproven.",
                tags("static-shadows", "apply-grid", "shadow-grid", "bitmap")
            ),
            new Spec(
                "0x004ee410",
                "CStaticShadows__RayTriangleIntersect",
                "CStaticShadows__RayTriangleIntersect",
                "__cdecl",
                boolType,
                new ParameterImpl[] {
                    param("triangle_a", floatPtr),
                    param("triangle_b", floatPtr),
                    param("triangle_c", floatPtr),
                    param("segment_start_x", floatType),
                    param("segment_start_y", floatType),
                    param("segment_start_z", floatType),
                    param("segment_padding_or_w", intType),
                    param("segment_end_x", floatType),
                    param("segment_end_y", floatType),
                    param("segment_end_z", floatType)
                },
                "Wave511 signature/comment hardening: cdecl ray/segment versus triangle predicate used by static-shadow casting. The body builds and normalizes the triangle normal, intersects the segment plane between start/end points, rejects out-of-range hits, then sums acos-based edge angles and returns 1 only when the hit is inside the triangle. Static retail evidence only; the unused seventh stack slot appears to be vector padding/W from the caller, and exact source signature, precision behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("static-shadows", "ray-triangle", "geometry", "predicate")
            ),
            new Spec(
                "0x004ee8a0",
                "CStaticShadows__LoadAll",
                "CStaticShadows__LoadAll",
                "__stdcall",
                voidType,
                new ParameterImpl[] {param("chunk_reader", voidPtr)},
                "Wave511 signature/comment hardening: static-shadow bulk deserializer over a chunk reader. RET 0x4 proves one stack argument; the body advances chunk records, reads a count, then loops that count and calls CStaticShadows__Load for each serialized shadow entry. Static retail evidence only; exact resource chunk tags/format, source-body parity, runtime resource-loading behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("static-shadows", "load", "resource", "chunk-reader")
            ),
            new Spec(
                "0x004ee8f0",
                "CStaticShadows__Load",
                "CStaticShadows__Load",
                "__cdecl",
                voidType,
                new ParameterImpl[] {param("chunk_reader", voidPtr)},
                "Wave511 signature/comment hardening: static-shadow single-entry deserializer. The cdecl caller cleans one argument; the body allocates a 0x24-byte linked shadow entry, links it into DAT_009c8010, reads bounds/count/owner data, allocates a 0x1c-byte shadow-map entry array, and loads optional 0x200-byte bitmap cells from the chunk stream. Static retail evidence only; exact resource format, entry ownership, runtime load/rebind behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("static-shadows", "load", "resource", "chunk-reader", "shadow-map-entry")
            )
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }
        println(
            "SUMMARY updated=" + stats.updated +
            " skipped=" + stats.skipped +
            " renamed=" + stats.renamed +
            " would_rename=" + stats.wouldRename +
            " missing=" + stats.missing +
            " bad=" + stats.bad
        );
    }
}
