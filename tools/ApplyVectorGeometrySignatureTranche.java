//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.DoubleDataType;
import ghidra.program.model.data.FloatDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

public class ApplyVectorGeometrySignatureTranche extends GhidraScript {

    private static boolean isDryRun(String mode) {
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

    private Function getFunctionOrThrow(String addrText) throws Exception {
        if (!addrText.startsWith("0x") && !addrText.startsWith("0X")) {
            addrText = "0x" + addrText;
        }
        Address addr = toAddr(addrText);
        if (addr == null) {
            throw new IllegalArgumentException("Bad address: " + addrText);
        }
        Function fn = getFunctionAt(addr);
        if (fn == null) {
            Function containing = getFunctionContaining(addr);
            if (containing != null && containing.getEntryPoint().equals(addr)) {
                fn = containing;
            }
        }
        if (fn == null) {
            throw new IllegalStateException("Function not found at " + addrText);
        }
        return fn;
    }

    private ParameterImpl param(String name, DataType dataType) throws Exception {
        return new ParameterImpl(name, dataType, currentProgram);
    }

    private String expectedSignature(String name, String callingConvention, DataType returnType, ParameterImpl... params) {
        StringBuilder sb = new StringBuilder();
        sb.append(returnType.getDisplayName()).append(" ").append(callingConvention).append(" ").append(name).append("(");
        for (int i = 0; i < params.length; i++) {
            if (i > 0) {
                sb.append(", ");
            }
            sb.append(params[i].getDataType().getDisplayName()).append(" ").append(params[i].getName());
        }
        sb.append(")");
        return sb.toString();
    }

    private boolean isAllowedCurrentName(String currentName, String expectedName, String previousName) {
        return currentName.equals(expectedName) || (previousName != null && currentName.equals(previousName));
    }

    private void applySignature(
            String addr,
            String expectedName,
            String previousName,
            String callingConvention,
            DataType returnType,
            String comment,
            boolean dryRun,
            ParameterImpl... params) throws Exception {
        Function fn = getFunctionOrThrow(addr);
        if (!isAllowedCurrentName(fn.getName(), expectedName, previousName)) {
            throw new IllegalStateException("Unexpected function name at " + addr + ": " + fn.getName() + " != " + expectedName);
        }

        if (dryRun) {
            String renameNote = fn.getName().equals(expectedName) ? "" : " rename " + fn.getName() + " -> " + expectedName;
            println("DRY: " + addr + renameNote + " -> " + expectedSignature(expectedName, callingConvention, returnType, params));
            return;
        }

        if (!fn.getName().equals(expectedName)) {
            fn.setName(expectedName, SourceType.USER_DEFINED);
        }
        fn.setCallingConvention(callingConvention);
        fn.setReturnType(returnType, SourceType.USER_DEFINED);
        fn.replaceParameters(
            FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS,
            true,
            SourceType.USER_DEFINED,
            params
        );
        fn.setComment(comment);
        println("OK: " + addr + " " + expectedName + " -> " + fn.getSignature().toString());
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");
        println("Mode: " + (dryRun ? "dry" : "apply"));

        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);
        DataType floatType = FloatDataType.dataType;
        int updated = 0;
        int skipped = 0;

        applySignature(
            "0x0040d120",
            "Vec3__SubtractToOut",
            null,
            "__thiscall",
            voidType,
            "Signature hardening: Vec3 subtract helper reads ECX as lhs, stack arg1 as outVec, stack arg2 as rhs, writes three output lanes, and returns with ret 0x8. Not concrete Vec3 layout, exact source identity, runtime behavior, tags, locals, or rebuild parity proof.",
            dryRun,
            param("this", voidPtr),
            param("outVec", voidPtr),
            param("rhs", voidPtr));
        if (dryRun) { skipped++; } else { updated++; }

        applySignature(
            "0x0040d150",
            "Vec3__ScaleToOut",
            null,
            "__thiscall",
            voidType,
            "Signature hardening: Vec3 scale helper reads ECX as input vector, stack arg1 as outVec, stack arg2 as scale, writes three output lanes, and returns with ret 0x8. Not concrete Vec3 layout, exact source identity, runtime behavior, tags, locals, or rebuild parity proof.",
            dryRun,
            param("this", voidPtr),
            param("outVec", voidPtr),
            param("scale", floatType));
        if (dryRun) { skipped++; } else { updated++; }

        applySignature(
            "0x0040d180",
            "Vec3__Dot",
            null,
            "__thiscall",
            DoubleDataType.dataType,
            "Signature hardening: Vec3 dot helper reads ECX as lhs and stack arg1 as rhs, multiplies the three vector lanes into an FPU return, and returns with ret 0x4. Not concrete Vec3 layout, exact source identity, runtime behavior, tags, locals, or rebuild parity proof.",
            dryRun,
            param("this", voidPtr),
            param("rhs", voidPtr));
        if (dryRun) { skipped++; } else { updated++; }

        applySignature(
            "0x0040d1a0",
            "Vec3__ElevationOrZero",
            "CMonitor__ComputeVectorLengthOrZero",
            "__fastcall",
            DoubleDataType.dataType,
            "Owner/name correction: vector-angle helper computes vector length, guards near-zero input, divides z over length, and calls OID__AcosWrapper/CRT acos context. Source uses FVector::Elevation in auto-aim/camera orientation flows, but exact source identity, concrete Vec3 layout, runtime behavior, tags, locals, and rebuild parity remain unproven.",
            dryRun,
            param("vec", voidPtr));
        if (dryRun) { skipped++; } else { updated++; }

        applySignature(
            "0x0040d1f0",
            "Mat34__SetFromEulerAngles",
            "OID__BuildOrientationMatrixFromEuler",
            "__thiscall",
            voidType,
            "Owner/name correction: matrix builder evaluates cos/sin for three stack float angles, writes row/basis floats through matrix offsets +0x0..+0x28, and returns with ret 0xc. Broad xrefs keep exact source identity, angle order, concrete Mat34 layout, runtime behavior, tags, locals, and rebuild parity unproven.",
            dryRun,
            param("this", voidPtr),
            param("angle0", floatType),
            param("angle1", floatType),
            param("angle2", floatType));
        if (dryRun) { skipped++; } else { updated++; }

        applySignature(
            "0x0040d2c0",
            "Mat34__TransformVec3ByBasisToOut",
            "CSquadNormal__TransformVec3ByOrientationMatrix",
            "__thiscall",
            voidType,
            "Owner/name correction: basis-transform helper multiplies a vector by three matrix/basis rows at offsets +0x0/+0x10/+0x20, writes outVec lanes, and returns with ret 0x8. It does not prove translation, concrete Mat34/Vec3 layouts, exact source identity, runtime behavior, tags, locals, or rebuild parity.",
            dryRun,
            param("this", voidPtr),
            param("outVec", voidPtr),
            param("vec", voidPtr));
        if (dryRun) { skipped++; } else { updated++; }

        println("--- SUMMARY ---");
        println("updated=" + updated + " skipped=" + skipped + " missing=0 bad=0");
    }
}
