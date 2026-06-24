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
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

public class ApplyMeshGridSignatureTranche extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final String comment;
        final String[] allowedCurrentNames;
        final String[] tags;
        final ParameterImpl[] parameters;

        Spec(
                String address,
                String name,
                String callingConvention,
                DataType returnType,
                String comment,
                String[] allowedCurrentNames,
                String[] tags,
                ParameterImpl[] parameters) {
            this.address = address;
            this.name = name;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.comment = comment;
            this.allowedCurrentNames = allowedCurrentNames;
            this.tags = tags;
            this.parameters = parameters;
        }
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

    private Function getFunctionOrThrow(String addressText) throws Exception {
        Address address = addr(addressText);
        Function fn = getFunctionAt(address);
        if (fn == null) {
            Function containing = getFunctionContaining(address);
            if (containing != null && containing.getEntryPoint().equals(address)) {
                fn = containing;
            }
        }
        if (fn == null) {
            throw new IllegalStateException("Function not found at " + addressText);
        }
        return fn;
    }

    private ParameterImpl param(String name, DataType type) throws Exception {
        return new ParameterImpl(name, type, currentProgram);
    }

    private boolean allowedName(String currentName, Spec spec) {
        if (currentName.equals(spec.name)) {
            return true;
        }
        for (String allowed : spec.allowedCurrentNames) {
            if (currentName.equals(allowed)) {
                return true;
            }
        }
        return false;
    }

    private String signatureText(Spec spec) {
        StringBuilder sb = new StringBuilder();
        sb.append(spec.returnType.getDisplayName()).append(" ");
        sb.append(spec.callingConvention).append(" ");
        sb.append(spec.name).append("(");
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

    private void applySpec(Spec spec, boolean dryRun) throws Exception {
        Function fn = getFunctionOrThrow(spec.address);
        if (!allowedName(fn.getName(), spec)) {
            throw new IllegalStateException("Unexpected function name at " + spec.address + ": " + fn.getName());
        }

        if (dryRun) {
            println("DRY: " + spec.address + " " + fn.getName() + " -> " + signatureText(spec));
            return;
        }

        if (!fn.getName().equals(spec.name)) {
            fn.setName(spec.name, SourceType.USER_DEFINED);
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

        Function readBack = getFunctionOrThrow(spec.address);
        if (!readBack.getName().equals(spec.name)) {
            throw new IllegalStateException("Read-back name mismatch at " + spec.address);
        }
        println("OK: " + spec.address + " " + spec.name + " -> " + readBack.getSignature().toString());
        Thread.sleep(50);
    }

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "mesh-grid-wave366",
            "retail-binary-evidence"
        };
        String[] result = new String[common.length + extras.length];
        System.arraycopy(common, 0, result, 0, common.length);
        System.arraycopy(extras, 0, result, common.length, extras.length);
        return result;
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");
        println("Mode: " + (dryRun ? "dry" : "apply"));

        DataType voidType = VoidDataType.dataType;
        DataType intType = IntegerDataType.dataType;
        DataType floatType = FloatDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);

        Spec[] specs = new Spec[] {
            new Spec("0x0044c1c0", "CMesh__DeserializeTripletDwords", "__thiscall", voidType,
                "Wave366 signature/comment/tag hardening: mesh deserializer helper reads three dwords from mem_buffer through CDXMemBuffer__Read, writes them to this+0x00..this+0x08, and ends with ret 0x4. Static retail evidence only; exact mesh field type, source identity, runtime asset behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("mesh", "serializer", "signature-hardened"),
                new ParameterImpl[] {param("this", voidPtr), param("mem_buffer", voidPtr)}),
            new Spec("0x0044c210", "CMesh__DeserializeNineDwords", "__thiscall", voidType,
                "Wave366 signature/comment/tag hardening: mesh deserializer helper reads nine dwords from mem_buffer through CDXMemBuffer__Read, writes matrix-like slots through this+0x28, and ends with ret 0x4. Static retail evidence only; exact mesh field type, source identity, runtime asset behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("mesh", "serializer", "signature-hardened"),
                new ParameterImpl[] {param("this", voidPtr), param("mem_buffer", voidPtr)}),
            new Spec("0x0044c3d0", "CFearGrid__ctor_base", "__thiscall", voidPtr,
                "Wave366 owner/name/signature correction: constructor-style CFearGrid body installs vtable 0x005db2a4, stores grid_id at this+0x8008, calls CFearGrid__RebuildOccupancyAndScheduleTick, returns this, and ends with ret 0x4. Static retail evidence only; exact allocation owner, concrete CFearGrid layout, source identity, runtime AI behavior, and rebuild parity remain unproven.",
                new String[] {"CFearGrid__ctor_like_0044c3d0"},
                tags("fear-grid", "constructor", "owner-corrected"),
                new ParameterImpl[] {param("this", voidPtr), param("grid_id", intType)}),
            new Spec("0x0044c440", "CFearGrid__RebuildOccupancyAndScheduleTick", "__thiscall", voidType,
                "Wave366 comment/tag hardening: CFearGrid refresh clears the occupancy plane at this+0x08, sets the clearance plane at this+0x4008, filters tracked objects by grid_id at this+0x8008, calls CFearGrid__LookupFearWeightByArchetype for occupancy marks, clears nearby clearance cells for blocking actors, then schedules event 1000. Static retail evidence only; exact object-list ownership, concrete layout, runtime AI behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("fear-grid", "grid-refresh", "comment-hardened"),
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x0044c720", "CFearGrid__GetOccupancyAtWorldVector", "__thiscall", intType,
                "Wave366 owner/name/signature correction: CFearGrid occupancy sampler is called with a 16-byte by-value vector payload, rounds vector_x/vector_y into 8-unit 64x64 grid coordinates, reads the occupancy plane at this+0x08, and ends with ret 0x10. Represented as four float stack slots until a shared vector-by-value data type is recovered. Static retail evidence only; exact vector layout, source identity, runtime AI behavior, and rebuild parity remain unproven.",
                new String[] {"CSquadNormal__GetCellValueAtWorldXY"},
                tags("fear-grid", "occupancy", "owner-corrected", "signature-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("vector_x", floatType),
                    param("vector_y", floatType),
                    param("vector_z", floatType),
                    param("vector_w", floatType)
                }),
            new Spec("0x0044c780", "CFearGrid__ReadClearanceAtWorldVectorIfAboveTerrainDelta", "__thiscall", intType,
                "Wave366 owner/name/signature correction: CFearGrid clearance sampler is called with a 16-byte by-value vector payload, samples static-shadow height through CStaticShadows__SampleShadowHeightBilinear, gates on vector_z versus the threshold at 0x005db2b0, reads the clearance plane at this+0x4008 when in range, and ends with ret 0x10. Represented as four float stack slots until a shared vector-by-value data type is recovered. Static retail evidence only; exact vector layout, source identity, runtime firing behavior, and rebuild parity remain unproven.",
                new String[] {"OID__ReadHazardGridIfAboveTerrainDelta"},
                tags("fear-grid", "clearance", "owner-corrected", "signature-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("vector_x", floatType),
                    param("vector_y", floatType),
                    param("vector_z", floatType),
                    param("vector_w", floatType)
                }),
            new Spec("0x0044c810", "CFearGrid__FindNearestFreeCellSpiral", "__thiscall", voidType,
                "Wave366 owner/name/signature correction: CFearGrid free-cell search takes one inout_world_vector pointer, converts its first two float fields into 8-unit 64x64 grid coordinates, spirals through the occupancy plane at this+0x08 for a zero cell, snaps the vector fields back with scale 0x005d8c44 when a later-radius free cell is found, and ends with ret 0x4. Static retail evidence only; exact vector layout, source identity, runtime AI movement behavior, and rebuild parity remain unproven.",
                new String[] {"CSquadNormal__FindNearestFreeCellSpiral"},
                tags("fear-grid", "occupancy", "owner-corrected", "signature-hardened"),
                new ParameterImpl[] {param("this", voidPtr), param("inout_world_vector", voidPtr)}),
        };

        int updated = 0;
        int skipped = 0;
        int failed = 0;
        for (Spec spec : specs) {
            try {
                applySpec(spec, dryRun);
                if (dryRun) {
                    skipped++;
                }
                else {
                    updated++;
                }
            }
            catch (Exception ex) {
                failed++;
                println("FAIL: " + spec.address + " " + ex.getMessage());
            }
        }

        println("--- SUMMARY ---");
        println("targets=" + specs.length + " updated=" + updated + " skipped=" + skipped + " failed=" + failed + " dry=" + dryRun);
        if (failed != 0) {
            throw new IllegalStateException("Failed targets: " + failed);
        }
    }
}
