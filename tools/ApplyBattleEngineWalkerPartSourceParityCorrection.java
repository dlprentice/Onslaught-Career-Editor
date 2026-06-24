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

public class ApplyBattleEngineWalkerPartSourceParityCorrection extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final String comment;
        final String[] previousNames;
        final ParameterImpl[] parameters;

        Spec(
                String address,
                String name,
                String callingConvention,
                DataType returnType,
                String comment,
                String[] previousNames,
                ParameterImpl[] parameters) {
            this.address = address;
            this.name = name;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.comment = comment;
            this.previousNames = previousNames;
            this.parameters = parameters;
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

    private boolean nameAllowed(String currentName, Spec spec) {
        if (currentName.equals(spec.name)) {
            return true;
        }
        for (String previousName : spec.previousNames) {
            if (currentName.equals(previousName)) {
                return true;
            }
        }
        return false;
    }

    private String expectedSignature(Spec spec) {
        StringBuilder sb = new StringBuilder();
        sb.append(spec.returnType.getDisplayName()).append(" ").append(spec.callingConvention).append(" ").append(spec.name).append("(");
        for (int i = 0; i < spec.parameters.length; i++) {
            if (i > 0) {
                sb.append(", ");
            }
            sb.append(spec.parameters[i].getDataType().getDisplayName()).append(" ").append(spec.parameters[i].getName());
        }
        sb.append(")");
        return sb.toString();
    }

    private boolean applySpec(Spec spec, boolean dryRun) throws Exception {
        Function fn = getFunctionOrThrow(spec.address);
        if (!nameAllowed(fn.getName(), spec)) {
            throw new IllegalStateException("Unexpected function name at " + spec.address + ": " + fn.getName() + " != " + spec.name);
        }

        boolean needsRename = !fn.getName().equals(spec.name);
        if (dryRun) {
            println("DRY: " + spec.address + " " + fn.getName() + " -> " + expectedSignature(spec));
            return false;
        }

        if (needsRename) {
            fn.setName(spec.name, SourceType.USER_DEFINED);
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
        println("OK: " + spec.address + " " + spec.name + " -> " + fn.getSignature().toString());
        return needsRename;
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");
        println("Mode: " + (dryRun ? "dry" : "apply"));

        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);
        DataType charPtr = new PointerDataType(CharDataType.dataType);
        DataType wcharPtr = new PointerDataType(ShortDataType.dataType);
        DataType floatType = FloatDataType.dataType;
        DataType intType = IntegerDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec("0x00409e80", "CBattleEngine__AutoZoomOut", "__thiscall", voidType,
                "Source-parity correction: CBattleEngine::AutoZoomOut writes MAX_ZOOM_OUT/1.0 to the +0x2cc desired-zoom field and is called by WalkerPart/JetPart ChangeWeapon after zoom-mode changes. Static source/decompile/xref evidence only; exact layout and runtime zoom behavior remain unproven.",
                new String[] {"CGeneralVolume__SetParam2CC_ToOne"},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x00409e90", "CBattleEngine__ZoomOut", "__thiscall", voidType,
                "Source-parity correction: CBattleEngine::ZoomOut resolves the current weapon, checks the weapon-data +0x34 normal-zoom mode, and writes MAX_ZOOM_OUT/1.0 to +0x2cc. Static source/decompile evidence only; exact enum/layout and runtime zoom behavior remain unproven.",
                new String[] {"CGeneralVolume__SetParam2CC_ToOne_IfCurrentState1"},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x00409ec0", "CBattleEngine__ZoomIn", "__thiscall", voidType,
                "Source-parity correction: CBattleEngine::ZoomIn resolves the current weapon, checks the weapon-data +0x34 normal-zoom mode, and writes MAX_ZOOM_IN/0.4 to +0x2cc. Static source/decompile evidence only; exact enum/layout and runtime zoom behavior remain unproven.",
                new String[] {"CGeneralVolume__SetParam2CC_ToPoint4_IfCurrentState1"},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x0040c3a0", "CBattleEngine__IsWeaponOverheated", "__thiscall", intType,
                "Source-parity correction: CBattleEngine::IsWeaponOverheated routes by BattleEngine state to walker +0x578 or jet +0x57c part helpers that read the +0x544 store-overheat flag. Corrects a stale IsEnergyWeapon label/comment; static source/decompile/xref evidence only, and runtime HUD behavior remains unproven.",
                new String[] {"CBattleEngine__IsEnergyWeapon"},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x0040c480", "CBattleEngine__IsEnergyWeapon", "__thiscall", intType,
                "Source-parity correction: CBattleEngine::IsEnergyWeapon routes by BattleEngine state to walker +0x578 or jet +0x57c part helpers that read the +0x55c store-heat/energy flag. Corrects a stale IsWeaponOverheated label/comment; static source/decompile/xref evidence only, and runtime HUD behavior remains unproven.",
                new String[] {"CBattleEngine__IsWeaponOverheated"},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x004122b0", "CBattleEngineJetPart__IsEnergyWeapon", "__thiscall", intType,
                "Source-parity correction: JetPart IsEnergyWeapon returns the selected weapon store heat/energy flag at battleEngine +0x55c[store]. Corrects a stale IsWeaponOverheated label/comment; static source/decompile evidence only, and runtime HUD behavior remains unproven.",
                new String[] {"CBattleEngineJetPart__IsWeaponOverheated"},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x00412310", "CBattleEngineJetPart__IsWeaponOverheated", "__thiscall", intType,
                "Source-parity correction: JetPart IsWeaponOverheated returns the selected weapon store overheat flag at battleEngine +0x544[store]. Corrects a stale IsEnergyWeapon label/comment; static source/decompile evidence only, and runtime HUD behavior remains unproven.",
                new String[] {"CBattleEngineJetPart__IsEnergyWeapon"},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x004135e0", "CBattleEngineWalkerPart__ActivateLandingJets", "__thiscall", voidType,
                "Source-parity correction: WalkerPart ActivateLandingJets samples main-part velocity, applies walk velocity limiting, and sets the main-part +0x638 movement latch. Static source/decompile evidence only; concrete layout, runtime landing-jets behavior, and rebuild parity remain unproven.",
                new String[] {"CBattleEngineWalkerPart__ApplyWalkVelocityLimitAndSetMovementLatch"},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x00413760", "CBattleEngineWalkerPart__Move", "__thiscall", voidType,
                "Source-parity correction: WalkerPart Move handles tracked render pairs plus surface-alignment movement response and calls GoingIntoWater/Slide-style helpers. Static source/decompile/xref evidence only; runtime movement behavior remains unproven.",
                new String[] {"CMonitor__ProcessTrackingAndSurfaceAlignment"},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x00413a70", "CBattleEngineWalkerPart__GoingIntoWater", "__thiscall", intType,
                "Source-parity correction: WalkerPart GoingIntoWater-style predicate samples static-shadow/height context before the surface-alignment path. Static source/decompile evidence only; runtime water behavior remains unproven.",
                new String[] {"CMonitor__ShouldUseSurfaceAlignmentPath"},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x00413b90", "CBattleEngineWalkerPart__Slide", "__thiscall", voidType,
                "Source-parity correction: WalkerPart Slide-style surface-alignment helper iteratively samples heightfield normals and removes into-slope velocity components. Static source/decompile evidence only; runtime slide behavior remains unproven.",
                new String[] {"CMonitor__ResolveSurfaceAlignmentIterative"},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x00413cc0", "CBattleEngineWalkerPart__FireWeapon", "__thiscall", voidType,
                "Source-parity correction: WalkerPart FireWeapon resolves the current/fallback weapon entry, clears main-part +0x588 state, and may dispatch projectile-burst fallback. Static source/decompile evidence only; exact retail CBattleEngine::WeaponFired, weapon_fire_breaks_stealth, runtime firing behavior, and rebuild parity remain unproven.",
                new String[] {"CGeneralVolume__ResetState588AndRefreshCurrentEntry"},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x00413cf0", "CBattleEngineWalkerPart__ChargeWeapon", "__thiscall", voidType,
                "Source-parity correction: WalkerPart ChargeWeapon updates current-entry charge/overheat gates and may dispatch projectile-burst fallback. Static source/decompile evidence only; exact retail CBattleEngine::WeaponFired, weapon_fire_breaks_stealth, runtime charge behavior, and rebuild parity remain unproven.",
                new String[] {"CGeneralVolume__UpdateCurrentEntryProgressAndRefresh"},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x00413eb0", "CBattleEngineWalkerPart__ChangeWeapon", "__thiscall", voidType,
                "Source-parity correction: WalkerPart ChangeWeapon walks active weapon entries, changes the current weapon slot, loses charge, and may call CBattleEngine__AutoZoomOut when zoom mode changes. Static source/decompile evidence only; runtime weapon switching remains unproven.",
                new String[] {"CGeneralVolume__SelectNextEnabledEntry"},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x00414030", "CBattleEngineWalkerPart__GetCurrentWeapon", "__thiscall", voidPtr,
                "Source-parity correction: WalkerPart GetCurrentWeapon resolves primary/augmented/fallback weapon entries and may reset current index to zero. Static source/decompile evidence only; concrete layout and runtime weapon selection remain unproven.",
                new String[] {"CGeneralVolume__ResolveCurrentOrFallbackEntry"},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x004140d0", "CBattleEngineWalkerPart__WeaponFired", "__thiscall", intType,
                "Source-parity correction: WalkerPart WeaponFired has one stack argument (ret 0x4) for the weapon pointer and updates store value/heat/overheat state for list, primary, and augmented weapons. Static source/decompile/instruction evidence only; exact retail CBattleEngine::WeaponFired, weapon_fire_breaks_stealth, runtime firing behavior, and rebuild parity remain unproven.",
                new String[] {"CEngine__ProcessBurstQuotaInSecondaryEntrySet"},
                new ParameterImpl[] {param("this", voidPtr), param("weapon", voidPtr)}),
            new Spec("0x00414410", "CBattleEngineWalkerPart__GetWeaponAmmoPercentage", "__thiscall", floatType,
                "Source-parity correction: WalkerPart GetWeaponAmmoPercentage resolves the current weapon store and returns the +0x52c store value over configuration +0x4b0/+0x88, clamped to 1.0. Static source/decompile evidence only; concrete layout and runtime HUD behavior remain unproven.",
                new String[] {"CGeneralVolume__GetCurrentEntrySlotFillRatio"},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x00414470", "CBattleEngineWalkerPart__GetWeaponAmmoCount", "__thiscall", intType,
                "Source-parity correction: WalkerPart GetWeaponAmmoCount returns the rounded +0x52c store value for non-heat stores. Static source/decompile evidence only; concrete layout and runtime HUD behavior remain unproven.",
                new String[] {"CGeneralVolume__GetCurrentEntryRoundedSlotValue"},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x004144c0", "CBattleEngineWalkerPart__IsEnergyWeapon", "__thiscall", intType,
                "Source-parity correction: WalkerPart IsEnergyWeapon reads the current weapon store heat flag at main-part +0x55c. Static source/decompile evidence only; concrete layout and runtime HUD behavior remain unproven.",
                new String[] {"CGeneralVolume__GetCurrentEntrySlotFlag_55C"},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x004144f0", "CBattleEngineWalkerPart__IsWeaponOverheated", "__thiscall", intType,
                "Source-parity correction: WalkerPart IsWeaponOverheated reads the current weapon store overheat flag at main-part +0x544. Static source/decompile evidence only; concrete layout and runtime HUD behavior remain unproven.",
                new String[] {"CCockpit__GetCurrentEntryFlag_544"},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x00414520", "CBattleEngineWalkerPart__GetWeaponCharge", "__thiscall", floatType,
                "Source-parity correction: WalkerPart GetWeaponCharge reads current weapon +0x60 charge/progress context from the resolved weapon entry. Static source/decompile evidence only; exact CWeapon layout and runtime charge behavior remain unproven.",
                new String[] {"CGeneralVolume__GetCurrentEntryDistanceProgressRatio"},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x004145a0", "CBattleEngineWalkerPart__GetWeaponName", "__thiscall", wcharPtr,
                "Source-parity correction: WalkerPart GetWeaponName resolves the current weapon language-name id and passes it to CText__GetStringById. Static source/decompile evidence only; runtime localization behavior remains unproven.",
                new String[] {"CGeneralVolume__GetCurrentEntryDisplayString"},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x004145d0", "CBattleEngineWalkerPart__GetWeaponPhysicsName", "__thiscall", charPtr,
                "Source-parity correction: WalkerPart GetWeaponPhysicsName returns the current weapon data name pointer. Static source/decompile evidence only; concrete CWeaponData layout remains unproven.",
                new String[] {"CGeneralVolume__GetCurrentEntryPayload"},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x004145f0", "CBattleEngineWalkerPart__GetCurrentWeaponZoomMode", "__thiscall", intType,
                "Source-parity correction: WalkerPart GetCurrentWeaponZoomMode returns the current weapon zoom-mode-like field used by ChangeWeapon before/after slot switching. Static source/decompile/xref evidence only; exact CWeaponData field name and runtime zoom behavior remain unproven.",
                new String[] {"CGeneralVolume__GetSelectedWeaponDef_CachedPath"},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x00414610", "CBattleEngineWalkerPart__GetWeaponIconName", "__thiscall", charPtr,
                "Source-parity correction: WalkerPart GetWeaponIconName returns the current weapon icon-name-like field at weapon data +0x38. Static source/decompile evidence only; concrete CWeaponData layout remains unproven.",
                new String[] {"CGeneralVolume__GetCurrentEntryFieldA4_38"},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x00414630", "CBattleEngineWalkerPart__CanWeaponFire", "__thiscall", intType,
                "Source-parity correction: WalkerPart CanWeaponFire checks active current weapon +0x9c state plus store +0x52c value, +0x55c heat, and +0x544 overheat gates. Static source/decompile/xref evidence only; runtime firing behavior and weapon_fire_breaks_stealth remain unproven.",
                new String[] {"CBattleEngine__IsResolvedEntryUsable"},
                new ParameterImpl[] {param("this", voidPtr)})
        };

        int updated = 0;
        int skipped = 0;
        int renamed = 0;
        for (Spec spec : specs) {
            boolean didRename = applySpec(spec, dryRun);
            if (dryRun) {
                skipped++;
            } else {
                updated++;
                if (didRename) {
                    renamed++;
                }
            }
        }

        println("--- SUMMARY ---");
        println("updated=" + updated + " skipped=" + skipped + " renamed=" + renamed + " missing=0 bad=0");
    }
}
