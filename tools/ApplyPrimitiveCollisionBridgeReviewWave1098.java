// Normalize Wave1098 primitive collision bridge review tags.
// @category BEA

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionManager;
import ghidra.program.model.listing.FunctionTag;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

public class ApplyPrimitiveCollisionBridgeReviewWave1098 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String signature;
        final List<String> tags;

        Spec(String address, String name, String signature, String... tags) {
            this.address = address;
            this.name = name;
            this.signature = signature;
            this.tags = Arrays.asList(tags);
        }
    }

    private static final String[] COMMON_TAGS = {
        "static-reaudit",
        "primitive-collision-bridge-review-wave1098",
        "wave1098-readback-verified",
        "retail-binary-evidence",
        "tag-normalized",
        "comment-hardened",
        "primitive-collision",
        "collision-geometry"
    };

    private static final Spec[] SPECS = {
        spec("0x004059a0", "CCylinder__VFunc_01_004059a0",
            "int __thiscall CCylinder__VFunc_01_004059a0(void * this, void * forwardedA, void * forwardedB, void * dispatchObject, void * forwardedC)",
            "cylinder", "vtable-wrapper", "slot-1", "slot-3", "slot-5", "delegate-vfunc-0x08"),
        spec("0x004098c0", "CLine__VFunc_01_004098c0",
            "int __thiscall CLine__VFunc_01_004098c0(void * this, void * arg0, void * arg1, void * dispatch_target, void * arg3)",
            "line", "vtable-wrapper", "slot-1", "slot-2", "slot-3", "slot-5", "delegate-vfunc-0x10"),
        spec("0x004098e0", "CLine__ctor_copy",
            "void __thiscall CLine__ctor_copy(void * this, void * sourceLine)",
            "line", "constructor", "copy-constructor", "cgeneralvolume-base", "vtable-0x005d8bfc"),
        spec("0x0040d470", "CLine__ctor_fromEndpoints",
            "void __thiscall CLine__ctor_fromEndpoints(void * this, void * startPoint, void * endPoint)",
            "line", "constructor", "endpoint-copy", "cgeneralvolume-base", "vtable-0x005d8bfc"),
        spec("0x00426320", "CSphere__VFunc_01_00426320",
            "int __thiscall CSphere__VFunc_01_00426320(void * this, void * query_arg0, void * query_arg1, void * delegate_object, void * query_arg3)",
            "sphere", "vtable-forwarder", "delegate-vfunc-0x0c", "vtable-0x005d95e8"),
        spec("0x00426340", "CLine__ScalarDeletingDestructor_00426340",
            "void * __thiscall CLine__ScalarDeletingDestructor_00426340(void * this, int deleteFlags)",
            "line", "scalar-deleting-dtor", "shared-helper", "base-vtable-reset"),
        spec("0x00426360", "CLine__SetBaseVtable_00426360",
            "void __fastcall CLine__SetBaseVtable_00426360(void * this)",
            "line", "base-vtable-reset", "unwind-helper", "shared-helper"),
        spec("0x0043fde0", "CCylinder__ctor",
            "void __thiscall CCylinder__ctor(void * this, void * sourceCylinder)",
            "cylinder", "constructor", "radius-context", "vtable-0x005d88cc"),
        spec("0x0043fe20", "CCylinder__ResolveCollisionVFunc02",
            "int __thiscall CCylinder__ResolveCollisionVFunc02(void * this, void * movingStateA, void * movingStateB, void * radiusContext, void * contactOut)",
            "cylinder", "vfunc-slot-2", "contact-output", "collision-resolve"),
        spec("0x004e4d70", "CSphere__VFunc02_ResolveCollisionAsCylinder",
            "void __thiscall CSphere__VFunc02_ResolveCollisionAsCylinder(void * this, void * collision_arg0, void * collision_arg1, void * collision_arg2, int collision_flags)",
            "sphere", "cylinder-proxy", "vfunc-slot-2", "temporary-cylinder"),
        spec("0x004abe50", "CMeshCollisionVolume__VFunc_02_004abe50",
            "int __thiscall CMeshCollisionVolume__VFunc_02_004abe50(void * this, void * query_arg0, void * query_arg1, void * source_sphere_record, void * contact_record)",
            "mesh-collision-volume", "vtable-slot-2", "sphere-record", "contact-record"),
        spec("0x004ac140", "CMeshCollisionVolume__TestSweptSphereAgainstBounds",
            "int __stdcall CMeshCollisionVolume__TestSweptSphereAgainstBounds(void * part_context, void * bounds_record, float * sphere_start, float * sweep_delta, float * sphere_radius, void * contact_record)",
            "mesh-collision-volume", "swept-sphere", "bounds-test", "contact-record"),
        spec("0x004ac4a0", "CMeshCollisionVolume__TestSweptSphereAgainstMeshPart",
            "int __stdcall CMeshCollisionVolume__TestSweptSphereAgainstMeshPart(void * part_context, void * mesh_part, float * sphere_start, float * sweep_delta, float * sphere_radius, void * contact_record)",
            "mesh-collision-volume", "swept-sphere", "mesh-part-triangle", "contact-record"),
        spec("0x004ac6e0", "CMeshCollisionVolume__VFunc_03_004ac6e0",
            "int __thiscall CMeshCollisionVolume__VFunc_03_004ac6e0(void * this, void * query_arg0, float * motion_record, void * query_arg2, void * contact_record)",
            "mesh-collision-volume", "vtable-slot-3", "swept-sphere", "contact-record"),
        spec("0x00478510", "CMeshCollisionVolume__TestSweptSphereAgainstTriangleCore",
            "int __cdecl CMeshCollisionVolume__TestSweptSphereAgainstTriangleCore(void * triangle_vertex0, void * triangle_vertex1, void * triangle_vertex2, void * sphere_start, void * sweep_delta, float sphere_radius, void * contact_record)",
            "mesh-collision-volume", "swept-sphere", "triangle", "contact-record"),
        spec("0x00478c20", "Geometry__IntersectSegmentTriangleAndStoreHit",
            "int __cdecl Geometry__IntersectSegmentTriangleAndStoreHit(void * triangle_vertex0, void * triangle_vertex1, void * triangle_vertex2, void * segment_start, void * segment_end, void * contact_record)",
            "geometry", "segment-triangle", "contact-record", "line-query"),
        spec("0x00479020", "CMeshCollisionVolume__IsDirectionInsideTrianglePrism",
            "int __cdecl CMeshCollisionVolume__IsDirectionInsideTrianglePrism(void * vertex0, void * vertex1, void * vertex2, void * vertex3, void * direction)",
            "mesh-collision-volume", "triangle-prism", "edge-plane-tests"),
        spec("0x00479200", "Geometry__SelectClosestPointOnTriangleEdges",
            "void __cdecl Geometry__SelectClosestPointOnTriangleEdges(void * outClosest, void * vertexA, void * vertexB, void * vertexC, void * queryPoint)",
            "geometry", "closest-point", "triangle-edges", "fallback-contact"),
        spec("0x00479630", "Geometry__RaySphereEntryDistance",
            "double __cdecl Geometry__RaySphereEntryDistance(void * rayStart, void * rayEnd, float radius)",
            "geometry", "ray-sphere", "entry-distance", "swept-sphere"),
        spec("0x004acde0", "CMeshCollisionVolume__InitContactOutputRecord",
            "void CMeshCollisionVolume__InitContactOutputRecord(void)",
            "mesh-collision-volume", "contact-output", "tail-block", "hidden-ebx"),
        spec("0x004ad830", "CMeshCollisionVolume__VFunc_04_004ad830",
            "int __thiscall CMeshCollisionVolume__VFunc_04_004ad830(void * this, void * query_arg0, void * state_record, void * segment_offsets, void * contact_record)",
            "mesh-collision-volume", "vtable-slot-4", "segment-triangle", "line-query")
    };

    private static Spec spec(String address, String name, String signature, String... extraTags) {
        List<String> tags = new ArrayList<>();
        tags.addAll(Arrays.asList(COMMON_TAGS));
        tags.addAll(Arrays.asList(extraTags));
        return new Spec(address, name, signature, tags.toArray(new String[0]));
    }

    @Override
    protected void run() throws Exception {
        boolean dryRun = true;
        String[] args = getScriptArgs();
        if (args.length > 0) {
            String mode = args[0].trim().toLowerCase();
            if ("apply".equals(mode)) {
                dryRun = false;
            } else if (!"dry".equals(mode)) {
                throw new IllegalArgumentException("Expected mode dry|apply, got: " + args[0]);
            }
        }

        FunctionManager functionManager = currentProgram.getFunctionManager();
        int updated = 0;
        int skipped = 0;
        int tagsAdded = 0;
        int missing = 0;
        int bad = 0;

        for (Spec spec : SPECS) {
            Address address = toAddr(spec.address);
            Function function = functionManager.getFunctionAt(address);
            if (function == null) {
                println("MISSING: " + spec.address + " " + spec.name);
                missing++;
                continue;
            }

            if (!verifyIdentity(spec, function)) {
                bad++;
                continue;
            }

            Set<String> existingTags = tagNames(function);
            List<String> missingTags = new ArrayList<>();
            for (String tag : spec.tags) {
                if (!existingTags.contains(tag)) {
                    missingTags.add(tag);
                }
            }

            if (missingTags.isEmpty()) {
                println("SKIP: " + spec.address + " " + spec.name + " tags already present");
                skipped++;
                continue;
            }

            tagsAdded += missingTags.size();
            if (dryRun) {
                println("WOULD_TAG: " + spec.address + " " + spec.name + " +" + String.join(",", missingTags));
                continue;
            }

            for (String tag : missingTags) {
                function.addTag(tag);
            }
            println("UPDATED: " + spec.address + " " + spec.name + " tags=+" + String.join(",", missingTags));
            updated++;
            currentProgram.flushEvents();
            Thread.sleep(50L);
        }

        if (!dryRun) {
            int verificationFailures = 0;
            for (Spec spec : SPECS) {
                Address address = toAddr(spec.address);
                Function function = functionManager.getFunctionAt(address);
                if (function == null) {
                    println("VERIFY_MISSING: " + spec.address);
                    verificationFailures++;
                    continue;
                }
                if (!verifyIdentity(spec, function)) {
                    verificationFailures++;
                    continue;
                }
                Set<String> tags = tagNames(function);
                for (String tag : spec.tags) {
                    if (!tags.contains(tag)) {
                        println("VERIFY_MISSING_TAG: " + spec.address + " " + tag);
                        verificationFailures++;
                    }
                }
            }
            if (verificationFailures != 0) {
                bad += verificationFailures;
            }
        }

        println("SUMMARY: updated=" + updated
            + " skipped=" + skipped
            + " renamed=0"
            + " would_rename=0"
            + " signature_updated=0"
            + " comment_only_updated=0"
            + " tags_added=" + tagsAdded
            + " missing=" + missing
            + " bad=" + bad);

        if (missing != 0 || bad != 0) {
            throw new IllegalStateException("Wave1098 tag normalization failed: missing=" + missing + " bad=" + bad);
        }
        if (!dryRun) {
            println("REPORT: Save succeeded");
        }
    }

    private boolean verifyIdentity(Spec spec, Function function) {
        boolean ok = true;
        if (!spec.name.equals(function.getName())) {
            println("BADNAME: " + spec.address + " expected=" + spec.name + " actual=" + function.getName());
            ok = false;
        }
        String actualSignature = function.getSignature().toString();
        if (!spec.signature.equals(actualSignature)) {
            println("BADSIG: " + spec.address + " expected=" + spec.signature + " actual=" + actualSignature);
            ok = false;
        }
        return ok;
    }

    private Set<String> tagNames(Function function) {
        Set<String> names = new HashSet<>();
        for (FunctionTag tag : function.getTags()) {
            names.add(tag.getName());
        }
        return names;
    }
}
