//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.DoubleDataType;
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

public class ApplyCollisionGeometryWave446 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final String comment;
        final String[] allowedExistingNames;
        final String[] tags;
        final ParameterImpl[] parameters;

        Spec(
                String address,
                String name,
                String callingConvention,
                DataType returnType,
                String comment,
                String[] allowedExistingNames,
                String[] tags,
                ParameterImpl[] parameters) {
            this.address = address;
            this.name = name;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.comment = comment;
            this.allowedExistingNames = allowedExistingNames;
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

    private boolean allowedName(Spec spec, String actual) {
        if (actual.equals(spec.name)) {
            return true;
        }
        for (String allowed : spec.allowedExistingNames) {
            if (actual.equals(allowed)) {
                return true;
            }
        }
        return false;
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
            "collision-geometry-wave446",
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

            if (!allowedName(spec, fn.getName())) {
                throw new IllegalStateException("Unexpected function name at " + spec.address + ": " + fn.getName());
            }

            boolean needsRename = !fn.getName().equals(spec.name);
            if (dryRun) {
                if (needsRename) {
                    stats.wouldRename++;
                }
                println("DRY: " + spec.address + " " + fn.getName() + " -> " + expectedSignature(spec));
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
        DataType floatType = FloatDataType.dataType;
        DataType floatPtr = new PointerDataType(floatType);
        DataType intType = IntegerDataType.dataType;
        DataType doubleType = DoubleDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x004262e0",
                "CMeshCollisionVolume__VFunc_05_004262e0",
                "__thiscall",
                intType,
                "Wave446 signature/comment hardening: CMeshCollisionVolume vtable slot 5 at 0x005d95dc is a four-stack-argument forwarder that passes the current object plus stack arguments through to the delegate object's vtable slot +0x04 and returns with RET 0x10. Static retail vtable/instruction/decompile evidence only; delegate type, exact source identity, collision semantics, and rebuild parity remain unproven.",
                new String[] {},
                tags("mesh-collision-volume", "vtable-forwarder", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("query_arg0", voidPtr),
                    param("query_arg1", voidPtr),
                    param("delegate_object", voidPtr),
                    param("query_arg3", voidPtr)
                }
            ),
            new Spec(
                "0x00426320",
                "CSphere__VFunc_01_00426320",
                "__thiscall",
                intType,
                "Wave446 signature/comment hardening: CSphere-adjacent vtable slot forwarder reached from the 0x005d95e8/0x005d95fc table region; forwards four stack arguments plus the current object into the delegate object's vtable slot +0x0c and returns with RET 0x10. Static retail vtable/instruction/decompile evidence only; exact owner table split, delegate type, collision semantics, and rebuild parity remain unproven.",
                new String[] {},
                tags("sphere-collision", "vtable-forwarder", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("query_arg0", voidPtr),
                    param("query_arg1", voidPtr),
                    param("delegate_object", voidPtr),
                    param("query_arg3", voidPtr)
                }
            ),
            new Spec(
                "0x00477ba0",
                "Vec3__MagnitudeSquared",
                "__fastcall",
                doubleType,
                "Wave446 owner/name/signature correction: computes x*x + y*y + z*z from the three floats at ECX, ECX+4, and ECX+8 and returns the result through the x87 stack. This supersedes the stale Geometry__NoOpHook label that hid the return value in collision decompile. Static retail instruction/xref evidence only; concrete Vec3 layout, exact source method identity, runtime behavior, and rebuild parity remain unproven.",
                new String[] {"Geometry__NoOpHook"},
                tags("vector-math", "magnitude-squared", "owner-corrected", "renamed", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x00478160",
                "Geometry__ClipSegmentAgainstAABB3D",
                "__cdecl",
                intType,
                "Wave446 signature/comment hardening: clips a 3D segment represented by six scalar pointers against a six-float AABB ordered as minX, minY, maxX, maxY, minZ, maxZ, updating either endpoint until both are inside or rejecting when endpoint outcodes overlap. Static retail decompile/instruction evidence only; exact source identity, caller-owned scalar layout, runtime line-search behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("geometry", "aabb-clip", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("start_x", floatPtr),
                    param("start_y", floatPtr),
                    param("start_z", floatPtr),
                    param("end_x", floatPtr),
                    param("end_y", floatPtr),
                    param("end_z", floatPtr),
                    param("bounds_minmax", floatPtr)
                }
            ),
            new Spec(
                "0x00478510",
                "CMeshCollisionVolume__TestSweptSphereAgainstTriangleCore",
                "__cdecl",
                intType,
                "Wave446 signature/comment hardening: tests a swept sphere against one triangle by deriving a normalized triangle plane, rejecting back-facing or too-distant cases, using Vec3__MagnitudeSquared/Geometry__RaySphereEntryDistance and closest-edge fallback as needed, then writing contact point, normal, time, and status fields into the contact record. Static retail decompile/xref evidence only; exact contact-record layout, source identity, runtime collision behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("mesh-collision-volume", "swept-sphere", "triangle", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("triangle_vertex0", voidPtr),
                    param("triangle_vertex1", voidPtr),
                    param("triangle_vertex2", voidPtr),
                    param("sphere_start", voidPtr),
                    param("sweep_delta", voidPtr),
                    param("sphere_radius", floatType),
                    param("contact_record", voidPtr)
                }
            ),
            new Spec(
                "0x00478c20",
                "Geometry__IntersectSegmentTriangleAndStoreHit",
                "__cdecl",
                intType,
                "Wave446 signature/comment hardening: intersects a segment against a triangle plane, checks segment time in [0,1], rejects later hits when the contact record already has a nearer time, performs three edge-side tests, and writes hit point, normal, time, and status fields when an output record is supplied. Static retail decompile/xref evidence only; exact record layout, source identity, runtime collision behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("geometry", "segment-triangle", "contact-record", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("triangle_vertex0", voidPtr),
                    param("triangle_vertex1", voidPtr),
                    param("triangle_vertex2", voidPtr),
                    param("segment_start", voidPtr),
                    param("segment_end", voidPtr),
                    param("contact_record", voidPtr)
                }
            ),
            new Spec(
                "0x004ac6e0",
                "CMeshCollisionVolume__VFunc_03_004ac6e0",
                "__thiscall",
                intType,
                "Wave446 function-boundary recovery and signature/comment hardening: CMeshCollisionVolume vtable slot 3 body at 0x005d95d4 scans mode-specific mesh parts, refreshes per-part bounds with CMeshCollisionVolume__SetPartBounds, dispatches bounds or mesh-part swept-sphere tests, accumulates up to six contact candidates, resolves contact normal/plane data, and updates the caller motion/contact record. Static retail vtable/decompile evidence only; exact vfunc purpose, record layouts, source identity, runtime collision behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("mesh-collision-volume", "function-boundary-recovered", "vtable-slot", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("query_arg0", voidPtr),
                    param("motion_record", floatPtr),
                    param("query_arg2", voidPtr),
                    param("contact_record", voidPtr)
                }
            ),
            new Spec(
                "0x004ad830",
                "CMeshCollisionVolume__VFunc_04_004ad830",
                "__thiscall",
                intType,
                "Wave446 function-boundary recovery and signature/comment hardening: CMeshCollisionVolume vtable slot 4 body at 0x005d95d8 builds segment endpoints from caller records, scans mode-specific mesh parts through CMeshPart line-triangle bucket helpers, calls Geometry__IntersectSegmentTriangleAndStoreHit for each candidate triangle, transforms the winning hit/normal back through the part basis, and optionally writes the caller output vector. Static retail vtable/decompile evidence only; exact vfunc purpose, record layouts, source identity, runtime collision behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("mesh-collision-volume", "function-boundary-recovered", "vtable-slot", "segment-triangle", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("query_arg0", voidPtr),
                    param("state_record", voidPtr),
                    param("segment_offsets", voidPtr),
                    param("contact_record", voidPtr)
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
            throw new RuntimeException("ApplyCollisionGeometryWave446 failed: bad=" + stats.bad + " missing=" + stats.missing);
        }
    }
}
