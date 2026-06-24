//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.ByteDataType;
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

public class ApplyBattleEngineHelperSignatureTranche extends GhidraScript {

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
        println("OK: " + addr + " " + expectedName + " -> " + fn.getSignature().toString());
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");
        println("Mode: " + (dryRun ? "dry" : "apply"));

        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);
        DataType intType = IntegerDataType.dataType;
        DataType floatType = FloatDataType.dataType;
        int updated = 0;
        int skipped = 0;

        applySignature("0x00405a40", "CBattleEngine__dtor_base", "__fastcall", voidType, dryRun,
            param("this", voidPtr));
        if (dryRun) { skipped++; } else { updated++; }

        applySignature("0x00405f60", "CBattleEngine__scalar_deleting_dtor", "__thiscall", voidPtr, dryRun,
            param("this", voidPtr),
            param("flags", ByteDataType.dataType));
        if (dryRun) { skipped++; } else { updated++; }

        applySignature("0x00405f80", "CBattleEngine__VFunc_02_00405f80", "__fastcall", voidType, dryRun,
            param("this", voidPtr));
        if (dryRun) { skipped++; } else { updated++; }

        applySignature("0x004063a0", "CBattleEngine__GetFloatAt0x118_AsDouble", "__fastcall", DoubleDataType.dataType, dryRun,
            param("this", voidPtr));
        if (dryRun) { skipped++; } else { updated++; }

        applySignature("0x004063b0", "CBattleEngine__UpdateWeaponEffect", "__fastcall", voidType, dryRun,
            param("this", voidPtr));
        if (dryRun) { skipped++; } else { updated++; }

        applySignature("0x00406460", "CBattleEngine__SwapPrimarySecondaryPartReadersForState", "__fastcall", voidType, dryRun,
            param("this", voidPtr));
        if (dryRun) { skipped++; } else { updated++; }

        applySignature("0x00406560", "CBattleEngine__UpdateAutoTargetSetAndFireProjectiles", "__fastcall", voidType, dryRun,
            param("this", voidPtr));
        if (dryRun) { skipped++; } else { updated++; }

        applySignature("0x00406fc0", "CBattleEngine__AddProjectile", "__thiscall", voidType, dryRun,
            param("this", voidPtr),
            param("target", voidPtr),
            param("lifetime", floatType),
            param("modeFlag", intType));
        if (dryRun) { skipped++; } else { updated++; }

        println("--- SUMMARY ---");
        println("updated=" + updated + " skipped=" + skipped + " missing=0 bad=0");
    }
}
