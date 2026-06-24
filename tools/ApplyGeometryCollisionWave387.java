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
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

public class ApplyGeometryCollisionWave387 extends GhidraScript {
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
            fn = getFunctionContaining(entry);
            if (fn != null && !fn.getEntryPoint().equals(entry)) {
                fn = null;
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

    private void applySpec(Spec spec, boolean dryRun, Stats stats) {
        try {
            Function fn = functionAtEntry(spec.address);
            if (fn == null) {
                stats.missing++;
                println("FAIL: missing function at " + spec.address + " for " + spec.name);
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
            println("OK: " + spec.address + " " + spec.name + " -> " + readBack.getSignature().toString());
            stats.updated++;
            Thread.sleep(50);
        } catch (Exception ex) {
            stats.bad++;
            println("FAIL: " + spec.address + " " + spec.name + " " + ex.getMessage());
        }
    }

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "geometry-collision-wave387",
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
        DataType voidPtr = new PointerDataType(voidType);
        DataType floatType = FloatDataType.dataType;
        DataType intType = IntegerDataType.dataType;
        DataType doubleType = DoubleDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x00479020",
                "CMeshCollisionVolume__IsDirectionInsideTrianglePrism",
                "__cdecl",
                intType,
                "Wave387 geometry/collision correction: tests a candidate direction against three signed edge/plane dot tests and is called from CMeshCollisionVolume__TestSweptSphereAgainstTriangleCore. Concrete vector layout, exact source identity, runtime collision behavior, and rebuild parity remain unproven.",
                tags("mesh-collision", "triangle-prism", "comment-hardened", "signature-hardened"),
                new ParameterImpl[] {
                    param("vertex0", voidPtr),
                    param("vertex1", voidPtr),
                    param("vertex2", voidPtr),
                    param("vertex3", voidPtr),
                    param("direction", voidPtr)
                }
            ),
            new Spec(
                "0x00479200",
                "Geometry__SelectClosestPointOnTriangleEdges",
                "__cdecl",
                voidType,
                "Wave387 geometry/collision correction: computes clamped projections across all three triangle edges, then selects the nearest candidate point to queryPoint. Concrete vector layout, exact source identity, runtime collision behavior, and rebuild parity remain unproven.",
                tags("geometry", "closest-point", "comment-hardened", "signature-hardened"),
                new ParameterImpl[] {
                    param("outClosest", voidPtr),
                    param("vertexA", voidPtr),
                    param("vertexB", voidPtr),
                    param("vertexC", voidPtr),
                    param("queryPoint", voidPtr)
                }
            ),
            new Spec(
                "0x00479630",
                "Geometry__RaySphereEntryDistance",
                "__cdecl",
                doubleType,
                "Wave387 geometry/collision correction: normalizes rayEnd minus rayStart, solves origin-centered sphere entry distance, and returns the retail sentinel when no positive entry is observed. Concrete vector layout, exact source identity, runtime collision behavior, and rebuild parity remain unproven.",
                tags("geometry", "ray-sphere", "comment-hardened", "signature-hardened"),
                new ParameterImpl[] {
                    param("rayStart", voidPtr),
                    param("rayEnd", voidPtr),
                    param("radius", floatType)
                }
            ),
            new Spec(
                "0x00479770",
                "Geometry__DistanceOutsideAabb",
                "__cdecl",
                doubleType,
                "Wave387 geometry/collision correction: computes absolute centered AABB overhangs with single-axis and two-axis distance branches; the all-three-axis branch records the retail instruction sequence rather than an idealized formula. Concrete vector layout, exact source identity, runtime collision behavior, and rebuild parity remain unproven.",
                tags("geometry", "aabb-distance", "comment-hardened", "signature-hardened"),
                new ParameterImpl[] {
                    param("point", voidPtr),
                    param("halfExtents", voidPtr)
                }
            )
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }

        println("--- SUMMARY ---");
        println("updated=" + stats.updated + " skipped=" + stats.skipped + " missing=" + stats.missing + " bad=" + stats.bad);
    }
}
