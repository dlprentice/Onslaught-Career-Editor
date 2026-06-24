//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.FloatDataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.UnsignedIntegerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.FunctionTag;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyWorldOccupancyWave457 extends GhidraScript {
    private static class Spec {
        final String address;
        final String expectedCurrentName;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final String comment;
        final String[] tags;
        final ParameterImpl[] parameters;

        Spec(
                String address,
                String expectedCurrentName,
                String name,
                String callingConvention,
                DataType returnType,
                String comment,
                String[] tags,
                ParameterImpl[] parameters) {
            this.address = address;
            this.expectedCurrentName = expectedCurrentName;
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
            "world-occupancy-wave457",
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
            String currentName = fn.getName();
            if (!currentName.equals(spec.expectedCurrentName) && !currentName.equals(spec.name)) {
                throw new IllegalStateException("Unexpected function name at " + spec.address + ": " + currentName);
            }

            boolean needsRename = !currentName.equals(spec.name);
            if (dryRun) {
                if (needsRename) {
                    stats.wouldRename++;
                }
                println("DRY: " + spec.address + " " + currentName + " -> " + expectedSignature(spec));
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
            if (!expectedSignature(spec).equals(readBack.getSignature().toString())) {
                throw new IllegalStateException("Read-back signature mismatch at " + spec.address + ": " + readBack.getSignature());
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
            Thread.sleep(5000);
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
        DataType uintType = UnsignedIntegerDataType.dataType;
        DataType floatType = FloatDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x004bc260",
                "CWorld__InitOccupancyBitplanes",
                "CWorld__InitOccupancyBitplanes",
                "__thiscall",
                voidPtr,
                "Wave457 signature/comment correction: CWorld occupancy bitplane initializer uses ECX as bitplane_base and the RET 0x4 stack argument as max_slope_degrees, stores the slope threshold at bitplane_base+0x2000, clears DAT_00809598, fills DAT_00809dc0 with 0xffffffff, seeds DAT_00829dc4/8 and DAT_00630ab4/8, and initializes the packed 0x100 x 0x20 byte rows to 0xff. Three CWorld__InitLODLists callers pass 35/45/60 degree thresholds. Static retail evidence only; runtime occupancy behavior remains unproven.",
                tags("world", "occupancy", "bitplane", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("max_slope_degrees", floatType)
                }
            ),
            new Spec(
                "0x004bc3e0",
                "CWorld__RemoveUnitFromOccupancyGrid",
                "CWorld__RemoveUnitFromOccupancyGrid",
                "__cdecl",
                voidType,
                "Wave457 signature/comment correction: CWorld remove helper calls CSPtrSet__Remove on DAT_00809588, then when occupancy is active uses the unit vfunc +0x40 radius plus unit+0x1c/+0x20 position and 0.5 padding to rerasterize a footprint with skip_shadow_rebuild=1. Static retail evidence only; runtime occupancy behavior remains unproven.",
                tags("world", "occupancy", "unit-set", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("unit", voidPtr)
                }
            ),
            new Spec(
                "0x004bc480",
                "CWorld__AddUnitToOccupancyGridAndRebuildShadows",
                "CWorld__AddUnitToOccupancyGridAndRebuildShadows",
                "__cdecl",
                voidType,
                "Wave457 signature/comment correction: CWorld add helper calls CSPtrSet__AddToHead on DAT_00809588, rerasterizes the unit footprint with skip_shadow_rebuild=1 when occupancy is active, then calls CEngine__BuildStaticShadowVolumesAroundUnit. Static retail evidence only; runtime static-shadow behavior remains unproven.",
                tags("world", "occupancy", "static-shadow", "unit-set", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("unit", voidPtr)
                }
            ),
            new Spec(
                "0x004bc510",
                "CExplosionInitThing__IsGridSegmentBlocked",
                "CExplosionInitThing__IsGridSegmentBlocked",
                "__thiscall",
                intType,
                "Wave457 signature/comment correction: CExplosionInitThing line-of-sight helper uses ECX as bitplane_base and RET 0x10 confirms four stack coordinates: start_grid_x/start_grid_y to end_grid_x/end_grid_y. The old phantom float parameter was a register artifact. The body bounds coordinates to 0..255, walks the dominant axis through packed occupancy bits, returns 1 for outside/blocked and 0 for clear. Static retail evidence only; runtime pathfinding behavior remains unproven.",
                tags("explosion-init", "pathfinding", "occupancy", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("start_grid_x", intType),
                    param("start_grid_y", uintType),
                    param("end_grid_x", intType),
                    param("end_grid_y", uintType)
                }
            ),
            new Spec(
                "0x004bc6d0",
                "CExplosionInitThing__FindNearestSetBitInOccupancyGrid",
                "CExplosionInitThing__FindNearestSetBitInOccupancyGrid",
                "__thiscall",
                intType,
                "Wave457 signature/comment correction: CExplosionInitThing nearest-occupancy helper uses ECX as bitplane_base and RET 0x8 confirms inout_grid_x/inout_grid_y only; the prior third pointer was a register artifact. The body searches an expanding square/ring around the coordinate, writes the nearest set bit back to the inout pointers, returns 1 on success and 0 after radius exceeds 0xff. Static retail evidence only; runtime pathfinding behavior remains unproven.",
                tags("explosion-init", "pathfinding", "occupancy", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("inout_grid_x", intPtr),
                    param("inout_grid_y", intPtr)
                }
            ),
            new Spec(
                "0x004bd440",
                "CWorld__ClearCrossNeighborsInBitplane",
                "CWorld__ClearCrossNeighborsInBitplane",
                "__thiscall",
                voidType,
                "Wave457 signature/comment correction: CWorld bitplane helper uses ECX as bitplane_base and RET 0x8 confirms world_x/world_y only. The body converts world coordinates to half-resolution packed-bit rows and clears the center/cross-neighbor bits around the sample. Static retail evidence only; runtime occupancy behavior remains unproven.",
                tags("world", "occupancy", "bitplane", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("world_x", intType),
                    param("world_y", intType)
                }
            ),
            new Spec(
                "0x004bd5c0",
                "CWorld__RasterizeFootprintIntoOccupancyBitplanes",
                "CWorld__RasterizeFootprintIntoOccupancyBitplanes",
                "__cdecl",
                voidType,
                "Wave457 signature/comment correction: CWorld footprint rasterizer clamps min/max world bounds to 0..511, sets candidate bits across DAT_00855290/DAT_00855294/DAT_00855298, samples height and normals through CHeightField__GetHeightSamplePacked16 and CMonitor__SampleHeightfieldNormalAtXY, clears unsafe slope/height cells through CWorld__SetOrClearOccupancyBit and CWorld__ClearCrossNeighborsInBitplane, and when skip_shadow_rebuild is 0 rebuilds tracked unit static shadows. Static retail evidence only; runtime occupancy behavior remains unproven.",
                tags("world", "occupancy", "heightfield", "static-shadow", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("min_world_x", intType),
                    param("min_world_y", intType),
                    param("max_world_x", intType),
                    param("max_world_y", intType),
                    param("skip_shadow_rebuild", intType)
                }
            ),
            new Spec(
                "0x004bd9e0",
                "CEngine__BuildStaticShadowVolumesAroundUnit",
                "CEngine__BuildStaticShadowVolumesAroundUnit",
                "__cdecl",
                voidType,
                "Wave457 signature/comment correction: static shadow occupancy helper uses a unit parameter, samples targeting position via CUnitAI__GetWorldPositionForTargeting, uses the unit vfunc +0x44 radius, samples terrain through CStaticShadows__SampleShadowHeightBilinear, constructs line volumes, tests the unit collision volume, and clears packed occupancy through CWorld__SetOrClearOccupancyBit plus CWorld__ClearCrossNeighborsInBitplane. Static retail evidence only; runtime static-shadow behavior remains unproven.",
                tags("engine", "world", "static-shadow", "occupancy", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("unit", voidPtr)
                }
            ),
            new Spec(
                "0x004bdf70",
                "CWorld__SetOrClearOccupancyBit",
                "CWorld__SetOrClearOccupancyBit",
                "__thiscall",
                voidType,
                "Wave457 signature/comment correction: CWorld packed-bit helper uses ECX as bitplane_base and RET 0xc confirms world_x/world_y/set_flag only. The body converts to half-resolution packed bit coordinates and sets or clears the bit based on set_flag. Static retail evidence only; runtime occupancy behavior remains unproven.",
                tags("world", "occupancy", "bitplane", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("world_x", intType),
                    param("world_y", intType),
                    param("set_flag", intType)
                }
            ),
            new Spec(
                "0x004be050",
                "CWorld__LoadOccupancyBitplaneChunk",
                "CWorld__LoadOccupancyBitplaneChunk",
                "__thiscall",
                voidType,
                "Wave457 signature/comment correction: CWorld occupancy loader uses ECX as bitplane_base and RET 0x4 stack argument mem_buffer, reads through CDXMemBuffer__Read, expands version 1 bit-by-bit over 0x200 x 0x200 source bits, and for version 2 reads packed direct rows into 0x100 columns x 0x20 byte rows. Static retail evidence only; runtime load behavior remains unproven.",
                tags("world", "occupancy", "bitplane", "load", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("mem_buffer", voidPtr)
                }
            ),
            new Spec(
                "0x004be970",
                "CExplosionInitThing__TestBitAtGridCoordPacked",
                "CExplosionInitThing__TestBitAtGridCoordPacked",
                "__thiscall",
                uintType,
                "Wave457 signature/comment correction: packed occupancy test helper uses ECX as bitplane_base and RET 0x8 confirms grid_x/grid_y only. It returns the packed bit mask result for grid_x at row grid_y. Static retail evidence only; runtime pathfinding behavior remains unproven.",
                tags("explosion-init", "pathfinding", "occupancy", "bitplane", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("grid_x", intType),
                    param("grid_y", uintType)
                }
            ),
            new Spec(
                "0x004bed30",
                "CExplosionInitThing__StepToLowestCostNeighbor8",
                "CExplosionInitThing__StepToLowestCostNeighbor8",
                "__cdecl",
                voidType,
                "Wave457 signature/comment correction: CExplosionInitThing path helper uses inout_grid_x/inout_grid_y pointers, reads the DAT_00809dc0 cost field and its eight neighbors, then writes the lowest-cost neighboring coordinate back to the inout pointers. Static retail evidence only; runtime pathfinding behavior remains unproven.",
                tags("explosion-init", "pathfinding", "occupancy", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("inout_grid_x", intPtr),
                    param("inout_grid_y", intPtr)
                }
            ),
            new Spec(
                "0x004beea0",
                "CExplosionInitThing__SimplifyGridPathByLineOfSight",
                "CExplosionInitThing__SimplifyGridPathByLineOfSight",
                "__thiscall",
                voidType,
                "Wave457 signature/comment correction: CExplosionInitThing path simplifier uses ECX as path and RET 0x4 confirms only bitplane_base on the stack; the prior phantom third parameter was a register artifact. The body uses path+0x0c count and path+0x10/+0x18 coordinate arrays, removing path points when CExplosionInitThing__IsGridSegmentBlocked reports line of sight. Static retail evidence only; runtime pathfinding behavior remains unproven.",
                tags("explosion-init", "pathfinding", "occupancy", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("bitplane_base", voidPtr)
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
        if (stats.missing != 0 || stats.bad != 0) {
            throw new RuntimeException("Wave457 apply had missing/bad entries");
        }
    }
}
