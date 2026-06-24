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

public class ApplyBattleEngineVolumeAugmentPickupSignatureTranche extends GhidraScript {

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

    private boolean isAllowedCurrentName(String currentName, String expectedName, String previousName) {
        return currentName.equals(expectedName) || (previousName != null && currentName.equals(previousName));
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
            String previousName,
            String callingConvention,
            DataType returnType,
            String comment,
            boolean dryRun,
            ParameterImpl... params) throws Exception {
        Function fn = getFunctionOrThrow(addr);
        if (!isAllowedCurrentName(fn.getName(), expectedName, previousName)) {
            throw new IllegalStateException(
                "Unexpected function name at " + addr + ": " + fn.getName() + " != " + expectedName + " or " + previousName
            );
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
        int updated = 0;
        int skipped = 0;

        applySignature(
            "0x0040dc30",
            "CBattleEngine__EnableVolumeEntryGroupsByName",
            "CExplosionInitThing__EnableVolumeEntryGroupsByName",
            "__thiscall",
            voidType,
            "Owner/name correction: BattleEngine volume-entry group helper. The body takes an entry-name argument, dispatches the +0x578 general-volume group through CGeneralVolume__EnableEntriesByName, and dispatches the +0x57c linked group through CGeneralVolume__EnableLinkedEntriesByName. Static vtable/decompile evidence only; exact source identity, concrete layout, and runtime behavior remain unproven.",
            dryRun,
            param("this", voidPtr),
            param("entryName", voidPtr));
        if (dryRun) { skipped++; } else { updated++; }

        applySignature(
            "0x0040dc60",
            "CBattleEngine__DisableVolumeEntryGroupsByNameAndReselect",
            "CExplosionInitThing__DisableVolumeEntryGroupsByNameAndReselect",
            "__thiscall",
            voidType,
            "Owner/name correction: BattleEngine volume-entry group disable/reselect helper. The body takes an entry-name argument, dispatches the +0x578 group through CGeneralVolume__DisableEntriesByNameAndReselect, and dispatches the +0x57c linked group through CGeneralVolume__DisableLinkedEntriesByNameAndReselect. Static vtable/decompile evidence only; exact source identity, concrete layout, and runtime behavior remain unproven.",
            dryRun,
            param("this", voidPtr),
            param("entryName", voidPtr));
        if (dryRun) { skipped++; } else { updated++; }

        applySignature(
            "0x0040dcc0",
            "CBattleEngine__ClearFlag58CAndMorphIfState3",
            "CMonitor__ResetTransitionFlagAndUpdateIfState3_Thunk",
            "__thiscall",
            voidType,
            "Owner/name correction: tiny BattleEngine transition helper. The body clears +0x58c, checks state +0x260 for value 3, and tail-jumps to CBattleEngine__Morph only in that state. Static state-transition evidence only; exact source identity and runtime transform behavior remain unproven.",
            dryRun,
            param("this", voidPtr));
        if (dryRun) { skipped++; } else { updated++; }

        applySignature(
            "0x0040dda0",
            "CUnitAI__RefreshGridCooldownFromOccupiedCells",
            "CUnitAI__RefreshGridCooldownFromOccupiedCells",
            "__thiscall",
            voidType,
            "Signature hardening for the grid cooldown refresh helper. The body gates on DAT_00672fd0 minus a threshold, checks the object vfunc at +0x10c, samples two CSquadNormal grids at the current world XY, and refreshes +0x2e8 when either grid is active. Static objective-panel caller evidence only; owner, exact source identity, concrete layout, and runtime behavior remain provisional.",
            dryRun,
            param("this", voidPtr));
        if (dryRun) { skipped++; } else { updated++; }

        applySignature(
            "0x0040de40",
            "CBattleEngine__AugmentWeapon",
            "CMonitor__HandleTargetStateChangeAndHudPrompt",
            "__thiscall",
            voidType,
            "Owner/name correction from a strong static source bridge to Stuart CBattleEngine::AugmentWeapon(). The retail body checks primary/current weapon store availability, clears slow-movement/charge context through the selected weapon path, writes aug timestamps from DAT_00672fd0, writes MAX_AUG_VALUE as 10.0, sets the aug-active flag, and plays hud_weapon_augmented. Static source/decompile/caller evidence only; runtime augmented-weapon behavior, concrete layout, and rebuild parity remain unproven.",
            dryRun,
            param("this", voidPtr));
        if (dryRun) { skipped++; } else { updated++; }

        applySignature(
            "0x0040dfb0",
            "CGeneralVolume__SpawnPickupAndDispatch",
            "CGeneralVolume__SpawnPickupAndDispatch",
            "__thiscall",
            voidType,
            "Signature hardening for the pickup spawn/dispatch helper. The body resolves a pickup name from this+0x4b0/+0x68 against the global pickup list, calls CWorldPhysicsManager__CreatePickup, initializes an influence/launch stack object, copies position fields, and dispatches the created pickup through its vfunc when available. Static decompile/caller evidence only; exact owner/source identity, concrete layout, and runtime pickup behavior remain provisional.",
            dryRun,
            param("this", voidPtr));
        if (dryRun) { skipped++; } else { updated++; }

        println("--- SUMMARY ---");
        println("updated=" + updated + " skipped=" + skipped + " missing=0 bad=0");
    }
}
