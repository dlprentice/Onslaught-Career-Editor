//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.CharDataType;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.FloatDataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.ShortDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

public class ApplyBattleEngineHudProfileSignatureTranche extends GhidraScript {

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
            throw new IllegalStateException("Unexpected function name at " + addr + ": " + fn.getName() + " != " + expectedName + " or " + previousName);
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
        DataType intType = IntegerDataType.dataType;
        DataType floatType = FloatDataType.dataType;
        DataType wcharPtr = new PointerDataType(ShortDataType.dataType);
        DataType charPtr = new PointerDataType(CharDataType.dataType);
        int updated = 0;
        int skipped = 0;

        applySignature(
            "0x0040c480",
            "CBattleEngine__IsWeaponOverheated",
            "CExplosionInitThing__GetCurrentEntrySlotFlag_55C",
            "__thiscall",
            intType,
            "Owner/signature re-audit: source-aligned CBattleEngine::IsWeaponOverheated HUD helper. The body routes by BattleEngine state to walker +0x578 or jet +0x57c part paths and reaches current-entry +0x55c overheat-style flag helpers. Static source/caller evidence only; runtime HUD behavior remains unproven.",
            dryRun,
            param("this", voidPtr));
        if (dryRun) { skipped++; } else { updated++; }

        applySignature(
            "0x0040c4a0",
            "CBattleEngine__GetWeaponCharge",
            "CExplosionInitThing__GetCurrentEntryDistanceProgressRatioOrRacerDelta",
            "__thiscall",
            floatType,
            "Owner/signature re-audit: source-aligned CBattleEngine::GetWeaponCharge. Racer path samples render/world position against terrain/water-style height and clamps a delta ratio; other paths route to walker/jet current-entry charge/progress helpers. Static source/caller evidence only; runtime weapon charge behavior remains unproven.",
            dryRun,
            param("this", voidPtr));
        if (dryRun) { skipped++; } else { updated++; }

        applySignature(
            "0x0040c550",
            "CBattleEngine__GetWeaponName",
            "CExplosionInitThing__GetCurrentEntryDisplayString",
            "__thiscall",
            wcharPtr,
            "Owner/signature re-audit: source-aligned CBattleEngine::GetWeaponName HUD helper. The body routes by BattleEngine state to walker/jet display-string helpers and is called by the HUD status panel. Static source/caller evidence only; wide string layout and runtime HUD behavior remain unproven.",
            dryRun,
            param("this", voidPtr));
        if (dryRun) { skipped++; } else { updated++; }

        applySignature(
            "0x0040c570",
            "CBattleEngine__GetWeaponPhysicsName",
            "CGeneralVolume__DispatchModeSpecific_145D0_or_12480",
            "__thiscall",
            charPtr,
            "Owner/signature re-audit: source-aligned CBattleEngine::GetWeaponPhysicsName. IScript__GetThingName calls this path; the body routes to walker/jet current-entry payload/name helpers. Static source/caller evidence only; runtime script behavior remains unproven.",
            dryRun,
            param("this", voidPtr));
        if (dryRun) { skipped++; } else { updated++; }

        applySignature(
            "0x0040c590",
            "CBattleEngine__GetWeaponIconName",
            "CExplosionInitThing__GetCurrentEntryFieldA4_38",
            "__thiscall",
            charPtr,
            "Owner/signature re-audit: source-aligned CBattleEngine::GetWeaponIconName HUD helper. The HUD status panel calls this path; the body routes to walker/jet icon-name context helpers. Static source/caller evidence only; runtime HUD behavior remains unproven.",
            dryRun,
            param("this", voidPtr));
        if (dryRun) { skipped++; } else { updated++; }

        applySignature(
            "0x0040c650",
            "CBattleEngine__UpdateConfiguration",
            "CBattleEngine__ApplyWeaponProfileByIndex",
            "__thiscall",
            voidType,
            "Owner/signature re-audit: source-aligned CBattleEngine::UpdateConfiguration. The body resolves the configuration by id, updates energy/life, resets jet/walker part configuration when present, refreshes store overheat/heat/value arrays, and logs the configuration name. Static source/caller evidence only; concrete layouts and runtime configuration behavior remain unproven.",
            dryRun,
            param("this", voidPtr));
        if (dryRun) { skipped++; } else { updated++; }

        println("--- SUMMARY ---");
        println("updated=" + updated + " skipped=" + skipped + " missing=0 bad=0");
    }
}
