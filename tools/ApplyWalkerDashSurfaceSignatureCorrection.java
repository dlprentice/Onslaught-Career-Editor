//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.CharDataType;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.FloatDataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

public class ApplyWalkerDashSurfaceSignatureCorrection extends GhidraScript {
    private static class ApplyResult {
        final boolean renamed;

        ApplyResult(boolean renamed) {
            this.renamed = renamed;
        }
    }

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

    private boolean nameAllowed(String currentName, String targetName, String... priorNames) {
        if (currentName.equals(targetName)) {
            return true;
        }
        for (String priorName : priorNames) {
            if (currentName.equals(priorName)) {
                return true;
            }
        }
        return false;
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

    private ApplyResult applySignature(
            String addr,
            String targetName,
            String callingConvention,
            DataType returnType,
            String comment,
            boolean dryRun,
            String[] priorNames,
            ParameterImpl... params) throws Exception {
        Function fn = getFunctionOrThrow(addr);
        if (!nameAllowed(fn.getName(), targetName, priorNames)) {
            throw new IllegalStateException("Unexpected function name at " + addr + ": " + fn.getName() + " != " + targetName);
        }

        boolean needsRename = !fn.getName().equals(targetName);
        if (dryRun) {
            println("DRY: " + addr + " " + fn.getName() + " -> " + expectedSignature(targetName, callingConvention, returnType, params));
            return new ApplyResult(false);
        }

        if (needsRename) {
            fn.setName(targetName, SourceType.USER_DEFINED);
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
        println("OK: " + addr + " " + targetName + " -> " + fn.getSignature().toString());
        return new ApplyResult(needsRename);
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");
        println("Mode: " + (dryRun ? "dry" : "apply"));

        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);
        DataType charPtr = new PointerDataType(CharDataType.dataType);
        DataType floatType = FloatDataType.dataType;
        DataType intType = IntegerDataType.dataType;
        int updated = 0;
        int skipped = 0;
        int renamed = 0;
        ApplyResult result;

        result = applySignature(
            "0x004127a0",
            "CGeneralVolume__EnableLinkedEntriesByName",
            "__thiscall",
            voidType,
            "Correction: linked-entry group helper walks the current list, compares each entry name with entryName, and sets the entry +0x9c enabled flag on matches. Corrects a stale JetPart weapon label; static decompile/xref evidence only, and concrete entry layout, tags, runtime availability, and rebuild parity remain unproven.",
            dryRun,
            new String[] {"CBattleEngineJetPart__EnableWeapon"},
            param("this", voidPtr),
            param("entryName", charPtr));
        if (dryRun) { skipped++; } else { updated++; if (result.renamed) { renamed++; } }

        result = applySignature(
            "0x00412900",
            "CMonitor__CanUseTrackingUpdate",
            "__thiscall",
            intType,
            "Correction: monitor predicate checks attached movement state, velocity magnitude, main-part energy, and a local timer before allowing tracking/camera update behavior. Corrects a stale JetPart AutoLevel label; static decompile/xref evidence only, and runtime flight/camera behavior remains unproven.",
            dryRun,
            new String[] {"CBattleEngineJetPart__AutoLevel"},
            param("this", voidPtr));
        if (dryRun) { skipped++; } else { updated++; if (result.renamed) { renamed++; } }

        result = applySignature(
            "0x004129a0",
            "LinkedObjectList__CountFlag9C",
            "__thiscall",
            intType,
            "Correction: linked-object-list helper walks entries and counts objects whose +0x9c flag is set. Corrects a stale JetPart active-weapon label; static decompile/xref evidence only, and concrete list/object layout remains unproven.",
            dryRun,
            new String[] {"CBattleEngineJetPart__CountActiveWeapons"},
            param("this", voidPtr));
        if (dryRun) { skipped++; } else { updated++; if (result.renamed) { renamed++; } }

        result = applySignature(
            "0x00412bc0",
            "CBattleEngineWalkerPart__ctor",
            "__thiscall",
            voidPtr,
            "Owner/signature correction: CBattleEngineWalkerPart constructor stores mainPart, initializes weapon/dash fields, calls CBattleEngineWalkerPart__ResetConfiguration, and registers g_dash_* console variables. Static source/caller evidence only; concrete layout, runtime dash behavior, and rebuild parity remain unproven.",
            dryRun,
            new String[] {"CBattleEngine__InitDashMoveParams"},
            param("this", voidPtr),
            param("mainPart", voidPtr));
        if (dryRun) { skipped++; } else { updated++; if (result.renamed) { renamed++; } }

        result = applySignature(
            "0x00412cf0",
            "CBattleEngineWalkerPart__dtor_base",
            "__thiscall",
            voidType,
            "Owner/signature correction: CBattleEngineWalkerPart destructor-base helper drains owned weapon entries, releases primary and augmented weapon pointers, and clears the weapon set. Static source/caller evidence only; destructor completeness, concrete layout, and rebuild parity remain unproven.",
            dryRun,
            new String[] {"CCockpit__DestroyWeaponSetAndOwnedNodes"},
            param("this", voidPtr));
        if (dryRun) { skipped++; } else { updated++; if (result.renamed) { renamed++; } }

        result = applySignature(
            "0x00412d80",
            "CBattleEngineWalkerPart__Forward",
            "__thiscall",
            voidType,
            "Owner/signature correction: WalkerPart forward input helper uses moveY, dash thresholds, dash timing, strafe sound, selected-weapon charge reset, and forward velocity injection. Runtime dash behavior remains unproven.",
            dryRun,
            new String[] {"CGeneralVolume__HandleDashForwardInput"},
            param("this", voidPtr),
            param("moveY", floatType));
        if (dryRun) { skipped++; } else { updated++; if (result.renamed) { renamed++; } }

        result = applySignature(
            "0x00412f70",
            "CBattleEngineWalkerPart__Backward",
            "__thiscall",
            voidType,
            "Owner/signature correction: WalkerPart backward input helper uses moveY, dash thresholds, dash timing, strafe sound, selected-weapon charge reset, and backward velocity injection. Runtime dash behavior remains unproven.",
            dryRun,
            new String[] {"CGeneralVolume__HandleDashBackwardInput"},
            param("this", voidPtr),
            param("moveY", floatType));
        if (dryRun) { skipped++; } else { updated++; if (result.renamed) { renamed++; } }

        result = applySignature(
            "0x00413160",
            "CBattleEngineWalkerPart__StrafeLeft",
            "__thiscall",
            voidType,
            "Owner/signature correction: WalkerPart strafe-left helper uses moveX, dash thresholds, dash timing, strafe sound, selected-weapon charge reset, roll velocity bump, and lateral velocity injection. Runtime dash behavior remains unproven.",
            dryRun,
            new String[] {"CGeneralVolume__HandleDashLeftInput"},
            param("this", voidPtr),
            param("moveX", floatType));
        if (dryRun) { skipped++; } else { updated++; if (result.renamed) { renamed++; } }

        result = applySignature(
            "0x00413360",
            "CBattleEngineWalkerPart__StrafeRight",
            "__thiscall",
            voidType,
            "Owner/signature correction: WalkerPart strafe-right helper uses moveX, dash thresholds, dash timing, strafe sound, selected-weapon charge reset, roll velocity decrement, and lateral velocity injection. Runtime dash behavior remains unproven.",
            dryRun,
            new String[] {"CGeneralVolume__HandleDashRightInput"},
            param("this", voidPtr),
            param("moveX", floatType));
        if (dryRun) { skipped++; } else { updated++; if (result.renamed) { renamed++; } }

        result = applySignature(
            "0x004135d0",
            "CBattleEngineWalkerPart__GetIsDoingSpecialWalkerMove",
            "__thiscall",
            intType,
            "Owner/signature correction: WalkerPart predicate returns whether dash/special-walker counter +0x44 is active, matching the source GetIsDoingSpecialWalkerMove shape. Runtime dash behavior and concrete layout remain unproven.",
            dryRun,
            new String[] {"CGeneralVolume__IsDashLockoutActive"},
            param("this", voidPtr));
        if (dryRun) { skipped++; } else { updated++; if (result.renamed) { renamed++; } }

        result = applySignature(
            "0x004135e0",
            "CBattleEngineWalkerPart__ApplyWalkVelocityLimitAndSetMovementLatch",
            "__thiscall",
            voidType,
            "Correction: WalkerPart helper samples main-part velocity, scales horizontal/vertical components, adds the result back through the movement interface, and sets main-part +0x638. Corrects a stale ActivateLandingJets label; static decompile/callsite evidence only, and runtime movement behavior remains unproven.",
            dryRun,
            new String[] {"CBattleEngineWalkerPart__ActivateLandingJets", "CGeneralVolume__ApplyScaledVelocityAndSetMovementLatch"},
            param("this", voidPtr));
        if (dryRun) { skipped++; } else { updated++; if (result.renamed) { renamed++; } }

        result = applySignature(
            "0x00413760",
            "CMonitor__ProcessTrackingAndSurfaceAlignment",
            "__thiscall",
            voidType,
            "Correction: CMonitor processing helper updates tracked render pairs, handles surface-alignment gates, clamps near-ground velocity response, decrements local movement counters, and refreshes surface alignment angle. Corrects a stale WalkerPart Move label; static decompile/xref evidence only, and runtime movement behavior remains unproven.",
            dryRun,
            new String[] {"CBattleEngineWalkerPart__Move"},
            param("this", voidPtr));
        if (dryRun) { skipped++; } else { updated++; if (result.renamed) { renamed++; } }

        result = applySignature(
            "0x00413a70",
            "CMonitor__ShouldUseSurfaceAlignmentPath",
            "__thiscall",
            intType,
            "Correction: monitor predicate samples current/projected static-shadow height and movement state to choose the surface-alignment path. Corrects a stale WalkerPart GoingIntoWater label; static decompile/xref evidence only, and retail terrain/water semantics remain unproven.",
            dryRun,
            new String[] {"CBattleEngineWalkerPart__GoingIntoWater"},
            param("this", voidPtr));
        if (dryRun) { skipped++; } else { updated++; if (result.renamed) { renamed++; } }

        result = applySignature(
            "0x00413b90",
            "CMonitor__ResolveSurfaceAlignmentIterative",
            "__thiscall",
            voidType,
            "Correction: monitor surface-alignment helper iteratively samples heightfield normals, removes into-slope velocity components, and stops after the slope gate or iteration cap. Corrects stale CCylinder and WalkerPart Slide labels; static decompile/xref evidence only, and runtime slide behavior remains unproven.",
            dryRun,
            new String[] {"CBattleEngineWalkerPart__Slide", "CCylinder__ResolveSurfaceAlignmentIterative"},
            param("this", voidPtr));
        if (dryRun) { skipped++; } else { updated++; if (result.renamed) { renamed++; } }

        result = applySignature(
            "0x00413cc0",
            "CGeneralVolume__ResetState588AndRefreshCurrentEntry",
            "__thiscall",
            voidType,
            "Correction: GeneralVolume helper clears main-part +0x588, resolves the current/fallback entry, and dispatches ProjectileBurst__SpawnFromPercentBucketFallback when the entry +0x9c flag is set. Corrects a stale WalkerPart FireWeapon label; static decompile/xref evidence only, and weapon_fire_breaks_stealth remains unproven.",
            dryRun,
            new String[] {"CBattleEngineWalkerPart__FireWeapon"},
            param("this", voidPtr));
        if (dryRun) { skipped++; } else { updated++; if (result.renamed) { renamed++; } }

        result = applySignature(
            "0x00413cf0",
            "CGeneralVolume__UpdateCurrentEntryProgressAndRefresh",
            "__thiscall",
            voidType,
            "Correction: GeneralVolume helper resolves the current/fallback entry, applies range/progress/charge/overheat-style gates, updates entry progress, and may dispatch ProjectileBurst__SpawnFromPercentBucketFallback. Corrects a stale WalkerPart ChargeWeapon label; static decompile/xref evidence only, and weapon_fire_breaks_stealth remains unproven.",
            dryRun,
            new String[] {"CBattleEngineWalkerPart__ChargeWeapon"},
            param("this", voidPtr));
        if (dryRun) { skipped++; } else { updated++; if (result.renamed) { renamed++; } }

        println("--- SUMMARY ---");
        println("updated=" + updated + " skipped=" + skipped + " renamed=" + renamed + " missing=0 bad=0");
    }
}
