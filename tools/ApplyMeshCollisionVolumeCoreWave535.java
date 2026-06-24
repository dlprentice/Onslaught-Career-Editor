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
import ghidra.program.model.listing.Parameter;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyMeshCollisionVolumeCoreWave535 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] parameters;
        final String comment;
        final String[] tags;

        Spec(String address, String name, String callingConvention, DataType returnType,
                ParameterImpl[] parameters, String comment, String[] tags) {
            this.address = address;
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
            "meshcollisionvolume-core-wave535",
            "retail-binary-evidence",
            "signature-corrected",
            "comment-hardened"
        };
        String[] result = new String[common.length + extras.length];
        System.arraycopy(common, 0, result, 0, common.length);
        System.arraycopy(extras, 0, result, common.length, extras.length);
        return result;
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
            println("BADNAME: " + spec.address + " " + fn.getName() + " expected " + spec.name);
            stats.bad++;
            return;
        }

        boolean update = needsUpdate(fn, spec);
        if (dryRun) {
            println((update ? "DRY: " : "SKIP: ") + spec.address + " " + expectedSignature(spec));
            stats.skipped++;
            return;
        }
        if (!update) {
            println("SKIP: " + spec.address + " already current");
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
        verifyReadBack(spec);
        println("OK: " + spec.address + " " + functionAtEntry(spec.address).getSignature());
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
        DataType floatType = FloatDataType.dataType;
        DataType floatPtr = new PointerDataType(floatType);
        DataType intType = IntegerDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x004abe50",
                "CMeshCollisionVolume__VFunc_02_004abe50",
                "__thiscall",
                intType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("query_arg0", voidPtr),
                    param("query_arg1", voidPtr),
                    param("source_sphere_record", voidPtr),
                    param("contact_record", voidPtr)
                },
                "Wave535 signature/comment hardening: CMeshCollisionVolume vtable slot 2 at 0x005d95d0 uses ECX as the current object, reads source_sphere_record fields to build a local 0x005d95e8-record, then dispatches through this object's vtable slot +0x0c with query_arg0/query_arg1/local-record/contact_record and returns with RET 0x10. Static retail vtable/instruction/decompile evidence only; exact vfunc purpose, record layouts, source identity, runtime collision behavior, and rebuild parity remain unproven.",
                tags("mesh-collision-volume", "vtable-slot", "signature-corrected", "comment-hardened")
            ),
            new Spec(
                "0x004ac000",
                "CMeshCollisionVolume__InitDirectionLookupTable",
                "__cdecl",
                voidType,
                new ParameterImpl[] {},
                "Wave535 signature/comment hardening: lazily populates the global MeshCollisionVolume direction lookup table at 0x00704bf8..0x00704c54 with static direction-vector pointers from 0x00704af8..0x00704b68, then sets initialization flag 0x00704cc8 to 1. Called from the bounds swept-sphere helper when the flag is clear. Static retail instruction/decompile evidence only; exact table semantics, vector layout, runtime collision behavior, and rebuild parity remain unproven.",
                tags("mesh-collision-volume", "lookup-table", "signature-corrected", "comment-hardened")
            ),
            new Spec(
                "0x004ac140",
                "CMeshCollisionVolume__TestSweptSphereAgainstBounds",
                "__stdcall",
                intType,
                new ParameterImpl[] {
                    param("part_context", voidPtr),
                    param("bounds_record", voidPtr),
                    param("sphere_start", floatPtr),
                    param("sweep_delta", floatPtr),
                    param("sphere_radius", floatPtr),
                    param("contact_record", voidPtr)
                },
                "Wave535 signature/comment hardening: RET 0x18 helper called from CMeshCollisionVolume vtable slot 3; lazily initializes the direction table, rejects sphere sweeps outside the bounds_record center/extent fields at +0xfc, tests the 24 direction-table triangle faces when contact_record+0xcc is set, otherwise uses Geometry__DistanceOutsideAabb, and records part_context plus hit/status fields in contact_record. Static retail decompile/xref/instruction evidence only; exact AABB/contact layouts, source identity, runtime collision behavior, and rebuild parity remain unproven.",
                tags("mesh-collision-volume", "swept-sphere", "bounds-test", "signature-corrected", "comment-hardened")
            ),
            new Spec(
                "0x004ac4a0",
                "CMeshCollisionVolume__TestSweptSphereAgainstMeshPart",
                "__stdcall",
                intType,
                new ParameterImpl[] {
                    param("part_context", voidPtr),
                    param("mesh_part", voidPtr),
                    param("sphere_start", floatPtr),
                    param("sweep_delta", floatPtr),
                    param("sphere_radius", floatPtr),
                    param("contact_record", voidPtr)
                },
                "Wave535 signature/comment hardening: RET 0x18 helper called from CMeshCollisionVolume vtable slot 3; starts a mesh-part triangle bucket search around the sweep midpoint/radius, expands quantized triangle vertices through mesh_part+0x100 scale/origin fields, calls CMeshCollisionVolume__TestSweptSphereAgainstTriangleCore for each candidate, and records part_context at contact_record+0xe4 on hits. Static retail decompile/xref/instruction evidence only; exact mesh-part/contact layouts, source identity, runtime collision behavior, and rebuild parity remain unproven.",
                tags("mesh-collision-volume", "swept-sphere", "mesh-part-triangle", "signature-corrected", "comment-hardened")
            ),
            new Spec(
                "0x004acf30",
                "CMeshCollisionVolume__ResolveContactNormalAndPlane",
                "__stdcall",
                intType,
                new ParameterImpl[] {
                    param("contact_record", floatPtr),
                    param("hit_x", floatType),
                    param("hit_y", floatType),
                    param("hit_z", floatType),
                    param("hit_w", floatType),
                    param("normal_x", floatType),
                    param("normal_y", floatType),
                    param("normal_z", floatType),
                    param("normal_w", floatType),
                    param("unused_source_w", floatType),
                    param("out_contact_point", floatPtr),
                    param("out_contact_normal", floatPtr)
                },
                "Wave535 signature/comment hardening: RET 0x30 helper called from CMeshCollisionVolume vtable slot 3 after a contact candidate is selected; normalizes input vectors, handles contact_record sentinel flags at indices 0x32/0x33, appends candidate normals into the contact_record plane list, resolves a separating/contact normal through dot/cross/normalize helpers, and writes out_contact_point/out_contact_normal when a consistent result is found. The tenth stack dword is carried as an observed but currently unused source value. Static retail decompile/xref/instruction evidence only; exact contact-record layout, source identity, runtime collision behavior, and rebuild parity remain unproven.",
                tags("mesh-collision-volume", "contact-resolution", "signature-corrected", "comment-hardened")
            )
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }
        println("SUMMARY updated=" + stats.updated + " skipped=" + stats.skipped +
            " missing=" + stats.missing + " bad=" + stats.bad);
    }
}
