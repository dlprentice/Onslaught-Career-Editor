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

public class ApplyBattleEngineDeathWeaponHudSignatureTranche extends GhidraScript {

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
        int updated = 0;
        int skipped = 0;

        applySignature(
            "0x0040bfd0",
            "CBattleEngine__StartDieProcess",
            null,
            "__thiscall",
            intType,
            "Signature/comment re-audit: source-aligned CBattleEngine::StartDieProcess. Retail body checks the dying flag, stops player vibration, sets the dying bit, notifies CGame__DeclarePlayerDead, tears down mission script state, calls the explode/pickup path, and starts the oily smoke effect. Static identity/read-back only; runtime death behavior is not re-proven.",
            dryRun,
            param("this", voidPtr));
        if (dryRun) { skipped++; } else { updated++; }

        applySignature(
            "0x0040c2e0",
            "CBattleEngine__CanSpawnBurstForResolvedEntry",
            "CEngine__CanSpawnBurstForResolvedEntry",
            "__thiscall",
            intType,
            "Owner/signature re-audit: BattleEngine-owned burst quota helper. Called by the current-preset projectile-burst body with a weapon/burst context, tries the +0x57c and +0x578 part paths, clears +0x5d8 on success, and returns a boolean-style result. Helper-level static evidence only; this does not prove exact CWeapon::Fire, CBattleEngine::WeaponFired, or stealth-reset runtime behavior.",
            dryRun,
            param("this", voidPtr),
            param("burstContext", voidPtr));
        if (dryRun) { skipped++; } else { updated++; }

        applySignature(
            "0x0040c340",
            "CBattleEngine__RandomizeBurstOffsetsAndAccumulateRange",
            "CEngine__RandomizeBurstOffsetsAndAccumulateRange",
            "__thiscall",
            voidType,
            "Owner/signature re-audit: BattleEngine-owned burst spread helper. The current-preset projectile-burst body calls it after projectile creation; it randomizes +0x4b8/+0x4c0 style offsets from the context range and accumulates twice that range into +0x604. Static helper evidence only; final source identity, tags, locals, and runtime projectile behavior remain unproven.",
            dryRun,
            param("this", voidPtr),
            param("burstContext", voidPtr));
        if (dryRun) { skipped++; } else { updated++; }

        applySignature(
            "0x0040c3a0",
            "CBattleEngine__IsEnergyWeapon",
            "CExplosionInitThing__GetCurrentEntrySlotFlag_544",
            "__thiscall",
            intType,
            "Owner/signature re-audit: source-aligned CBattleEngine::IsEnergyWeapon HUD helper. CExplosionInitThing HUD rendering calls it through the BattleEngine pointer; the body tail-dispatches to the walker or jet part current-entry energy/ammo-store flag based on state. Static source/caller evidence only; runtime HUD behavior remains unproven.",
            dryRun,
            param("this", voidPtr));
        if (dryRun) { skipped++; } else { updated++; }

        applySignature(
            "0x0040c3c0",
            "CBattleEngine__GetWeaponAmmoPercentage",
            "CExplosionInitThing__GetCurrentEntrySlotFillRatioOrRacerSpeed",
            "__thiscall",
            floatType,
            "Owner/signature re-audit: source-aligned CBattleEngine::GetWeaponAmmoPercentage. The HUD caller uses this value for the weapon meter; the body handles Racer by normalized velocity and otherwise dispatches to walker/jet ammo percentage helpers. Static source/caller evidence only; runtime HUD behavior remains unproven.",
            dryRun,
            param("this", voidPtr));
        if (dryRun) { skipped++; } else { updated++; }

        applySignature(
            "0x0040c460",
            "CBattleEngine__GetWeaponAmmoCount",
            "CExplosionInitThing__GetCurrentEntryRoundedSlotValue",
            "__thiscall",
            intType,
            "Owner/signature re-audit: source-aligned CBattleEngine::GetWeaponAmmoCount. The HUD caller formats this value for the non-meter weapon readout; the body tail-dispatches to walker or jet current-entry rounded ammo/count helpers based on state. Static source/caller evidence only; runtime HUD behavior remains unproven.",
            dryRun,
            param("this", voidPtr));
        if (dryRun) { skipped++; } else { updated++; }

        println("--- SUMMARY ---");
        println("updated=" + updated + " skipped=" + skipped + " missing=0 bad=0");
    }
}
