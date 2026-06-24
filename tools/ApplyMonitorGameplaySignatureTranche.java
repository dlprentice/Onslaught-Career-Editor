//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.BooleanDataType;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.FloatDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

public class ApplyMonitorGameplaySignatureTranche extends GhidraScript {

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
        DataType boolType = BooleanDataType.dataType;
        int updated = 0;
        int skipped = 0;

        applySignature(
            "0x00407940",
            "CGeneralVolume__RandomizeOffsets4B8_4C0",
            "__thiscall",
            voidType,
            "Signature hardening: ret 0x4 shows one offsetRange stack argument; body randomizes +0x4b8/+0x4bc/+0x4c0 offsets, resets +0x4c4, and conditionally updates linked +0x528/front-end context. Exact volume layout, local names, tags, source identity, runtime behavior, and rebuild parity remain unproven.",
            dryRun,
            param("this", voidPtr),
            param("offsetRange", floatType));
        if (dryRun) { skipped++; } else { updated++; }

        applySignature(
            "0x00407a50",
            "CMonitor__UpdateCameraVectorsAndInput",
            "__fastcall",
            voidType,
            "Signature hardening: monitor camera/input update copies +0x114 angles to +0x590, gates on grounded/height checks, applies mouse-look, builds orientation, and decays camera-offset noise. Exact owner/layout, local names, tags, runtime behavior, and rebuild parity remain unproven.",
            dryRun,
            param("monitor", voidPtr));
        if (dryRun) { skipped++; } else { updated++; }

        applySignature(
            "0x004080f0",
            "CGame__IsWalkerGroundedOrCollision",
            "__fastcall",
            boolType,
            "Signature hardening: bool grounded/collision predicate checks mode +0x260 and returns true when the vtable collision/ground check or HeightDelta__Below015_D4 succeeds. Exact source identity, concrete layout, local names, tags, runtime behavior, and rebuild parity remain unproven.",
            dryRun,
            param("battleEngine", voidPtr));
        if (dryRun) { skipped++; } else { updated++; }

        applySignature(
            "0x00408120",
            "CUnitAI__IsState2AndBelowHeightDeltaThreshold_00408120",
            "__fastcall",
            boolType,
            "Signature hardening: bool state/timestamp predicate checks mode +0x260 and DAT_00672fd0 minus +0xcc against the threshold. Exact CUnitAI layout, source identity, local names, tags, runtime behavior, and rebuild parity remain unproven.",
            dryRun,
            param("unitAi", voidPtr));
        if (dryRun) { skipped++; } else { updated++; }

        applySignature(
            "0x00408150",
            "CUnit__ProcessStateSwapAndDeathChecks",
            "__fastcall",
            voidType,
            "Signature hardening: unit state/death helper swaps primary/secondary part readers, checks death flag +0x2c&4, dispatches pickup/death paths, and resets +0xd0. Exact unit layout, source identity, local names, tags, runtime behavior, and rebuild parity remain unproven.",
            dryRun,
            param("unit", voidPtr));
        if (dryRun) { skipped++; } else { updated++; }

        applySignature(
            "0x004081c0",
            "CMonitor__Process",
            "__fastcall",
            voidType,
            "Signature hardening: large monitor process body covers active-reader expiry, tracked-list update, 0x5d8/0x5dc interpolation, vibration, cloak/fade timer decay, actor move, CMonitor__UpdateCameraVectorsAndInput, and target/effect updates. Cloak activation, fire-while-cloaked behavior, exact layout, tags, runtime behavior, and rebuild parity remain unproven.",
            dryRun,
            param("monitor", voidPtr));
        if (dryRun) { skipped++; } else { updated++; }

        println("--- SUMMARY ---");
        println("updated=" + updated + " skipped=" + skipped + " missing=0 bad=0");
    }
}
