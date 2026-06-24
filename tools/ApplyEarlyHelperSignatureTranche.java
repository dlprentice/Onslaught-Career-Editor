//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.BooleanDataType;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.FloatDataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

public class ApplyEarlyHelperSignatureTranche extends GhidraScript {

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

    private void applySignature(
            String addr,
            String expectedName,
            String callingConvention,
            DataType returnType,
            String comment,
            boolean dryRun,
            ParameterImpl... params) throws Exception {
        Function fn = getFunctionOrThrow(addr);
        if (!fn.getName().equals(expectedName)) {
            throw new IllegalStateException("Unexpected function name at " + addr + ": " + fn.getName() + " != " + expectedName);
        }

        if (dryRun) {
            println("DRY: " + addr + " " + expectedName + " -> " + expectedSignature(expectedName, callingConvention, returnType, params));
            return;
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
        DataType intType = IntegerDataType.dataType;
        int updated = 0;
        int skipped = 0;

        applySignature(
            "0x004062d0",
            "CSquadNormal__BuildOrientationMatrixFromEuler",
            "__thiscall",
            voidType,
            "Signature hardening: instruction evidence shows ret 0xc and FPU trig writes matrix rows through this/outMatrix offsets through +0x28. Wide xrefs make exact source identity, owner layout, local names, tags, runtime behavior, and rebuild parity remain unproven.",
            dryRun,
            param("this", voidPtr),
            param("angle0", floatType),
            param("angle1", floatType),
            param("angle2", floatType));
        if (dryRun) { skipped++; } else { updated++; }

        applySignature(
            "0x00406d50",
            "Vec3__NormalizeInPlace",
            "__fastcall",
            voidType,
            "Signature hardening: decompile evidence normalizes a Vec3 in place across +0x0/+0x4/+0x8 using SQRT, reciprocal scale, and a zero-length guard. Exact Vec3 type, local names, tags, runtime behavior, and rebuild parity remain unproven.",
            dryRun,
            param("vec", voidPtr));
        if (dryRun) { skipped++; } else { updated++; }

        applySignature(
            "0x00407060",
            "CEngine__MoveBurstReaderToCooldownSet",
            "__thiscall",
            voidType,
            "Signature hardening: instruction evidence shows ret 0x4 and one stack readerId argument; body moves a matching active set +0x294 entry into cooldown set +0x2a4 or frees a duplicate with CGenericActiveReader__dtor/OID__FreeObject. Exact reader layout, target semantics, local names, tags, runtime behavior, and rebuild parity remain unproven.",
            dryRun,
            param("this", voidPtr),
            param("readerId", intType));
        if (dryRun) { skipped++; } else { updated++; }

        applySignature(
            "0x00407140",
            "CMonitor__RemoveActiveReaderById",
            "__thiscall",
            voidType,
            "Signature hardening: instruction evidence shows ret 0x4 and one stack readerId argument; body scans cooldown set +0x2a4, removes a matching entry, then calls CGenericActiveReader__dtor and OID__FreeObject. Exact reader layout, local names, tags, runtime behavior, and rebuild parity remain unproven.",
            dryRun,
            param("this", voidPtr),
            param("readerId", intType));
        if (dryRun) { skipped++; } else { updated++; }

        applySignature(
            "0x00407310",
            "CBattleEngine__IsCurrentResolvedEntry",
            "__thiscall",
            BooleanDataType.dataType,
            "Signature hardening: instruction evidence shows ret 0x4 and one expectedEntry argument; body checks the current resolved entry through +0x57c or +0x578 and compares it with expectedEntry. Exact entry type, owner layout, local names, tags, runtime behavior, and rebuild parity remain unproven.",
            dryRun,
            param("this", voidPtr),
            param("expectedEntry", voidPtr));
        if (dryRun) { skipped++; } else { updated++; }

        applySignature(
            "0x00407540",
            "CGame__UpdateMouseLookAngles",
            "__fastcall",
            voidType,
            "Signature hardening for historical behavior label: decompile/xref evidence shows a mouse-look update path using g_MouseSensitivity, platform window dimensions, invert-Y state, orientation matrix setup, Vec3 helpers, heightfield normal sampling, pitch clamp, and cursor recentering. Exact owner, concrete layout, local names, tags, runtime behavior, and rebuild parity remain unproven.",
            dryRun,
            param("battleEngine", voidPtr));
        if (dryRun) { skipped++; } else { updated++; }

        println("--- SUMMARY ---");
        println("updated=" + updated + " skipped=" + skipped + " missing=0 bad=0");
    }
}
