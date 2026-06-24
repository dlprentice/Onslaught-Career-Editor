//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

public class ApplyGeneralVolumeChangeWeaponSignatureTranche extends GhidraScript {

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
        int updated = 0;
        int skipped = 0;

        applySignature(
            "0x00409e80",
            "CGeneralVolume__SetParam2CC_ToOne",
            "__fastcall",
            voidType,
            "Signature hardening: writes float 1.0 to generalVolume +0x2cc. Current callers include CCockpit__CycleToNextUsableWeapon and CGeneralVolume__SelectNextEnabledEntry; exact CGeneralVolume layout, source identity, runtime behavior, tags, and rebuild parity remain unproven.",
            dryRun,
            param("generalVolume", voidPtr));
        if (dryRun) { skipped++; } else { updated++; }

        applySignature(
            "0x00409e90",
            "CGeneralVolume__SetParam2CC_ToOne_IfCurrentState1",
            "__fastcall",
            voidType,
            "Signature hardening: resolves a related state through the +0x1d4 vcall and writes float 1.0 to generalVolume +0x2cc only when nested state +0x34 equals 1. Exact layout, source identity, runtime behavior, tags, and rebuild parity remain unproven.",
            dryRun,
            param("generalVolume", voidPtr));
        if (dryRun) { skipped++; } else { updated++; }

        applySignature(
            "0x00409ec0",
            "CGeneralVolume__SetParam2CC_ToPoint4_IfCurrentState1",
            "__fastcall",
            voidType,
            "Signature hardening: resolves a related state through the +0x1d4 vcall and writes float 0.4 to generalVolume +0x2cc only when nested state +0x34 equals 1. Exact layout, source identity, runtime behavior, tags, and rebuild parity remain unproven.",
            dryRun,
            param("generalVolume", voidPtr));
        if (dryRun) { skipped++; } else { updated++; }

        applySignature(
            "0x00409ef0",
            "CGeneralVolume__DispatchModeSpecificReset_13CF0_or_11BF0",
            "__fastcall",
            voidType,
            "Signature hardening: dispatches by generalVolume mode +0x260 to the mode-2 current-entry progress refresh at +0x578 or the mode-3 burst-progress/spawn path at +0x57c. Exact layout, source identity, runtime behavior, tags, and rebuild parity remain unproven.",
            dryRun,
            param("generalVolume", voidPtr));
        if (dryRun) { skipped++; } else { updated++; }

        applySignature(
            "0x00409f20",
            "CGeneralVolume__Reset588AndDispatchModeSpecific_13CC0_or_11B90",
            "__fastcall",
            voidType,
            "Signature hardening: clears generalVolume +0x588, seeds +0x2b4 from +0x2a0 or +0x2b0, then dispatches mode +0x260 to mode-2 refresh or mode-3 selected-burst preset paths. Exact layout, source identity, runtime behavior, tags, and rebuild parity remain unproven.",
            dryRun,
            param("generalVolume", voidPtr));
        if (dryRun) { skipped++; } else { updated++; }

        applySignature(
            "0x00409f70",
            "CBattleEngine__ChangeWeapon",
            "__fastcall",
            voidType,
            "Signature hardening/source bridge: retail body counts active weapons by mode +0x260, clears +0x588, cycles the selected walker/jet weapon helper, timestamps +0x584, then plays HUD weapon samples matching Stuart CBattleEngine::ChangeWeapon string flow. Exact layout, runtime behavior, tags, and rebuild parity remain unproven.",
            dryRun,
            param("battleEngine", voidPtr));
        if (dryRun) { skipped++; } else { updated++; }

        println("--- SUMMARY ---");
        println("updated=" + updated + " skipped=" + skipped + " missing=0 bad=0");
    }
}
