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

public class ApplyMovementJetPartSignatureCorrection extends GhidraScript {
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
        DataType charPtr = new PointerDataType(CharDataType.dataType);
        DataType floatType = FloatDataType.dataType;
        DataType intType = IntegerDataType.dataType;
        int updated = 0;
        int skipped = 0;

        applySignature(
            "0x00411630",
            "CMonitor__IntegrateMovementAgainstTerrain",
            "__thiscall",
            voidType,
            "Signature hardening: monitor movement helper integrates terrain/static-shadow constraints, pushes near-ground velocity response into the attached movement object, and adjusts orientation accumulators through Vec3 cross/normalize helpers. Caller evidence is CMonitor__UpdateMovementTransitionAndEffects; exact source identity, concrete layout, local names, runtime behavior, and rebuild parity remain unproven.",
            dryRun,
            param("this", voidPtr));
        if (dryRun) { skipped++; } else { updated++; }

        applySignature(
            "0x00411a60",
            "Vec3__Cross",
            "__thiscall",
            voidType,
            "Signature hardening: ret 0x8 vector helper writes this x rhs into outCross. Broad xrefs include camera, mesh, collision, particle, and monitor terrain paths; exact source file identity and full math-library typing remain unproven.",
            dryRun,
            param("this", voidPtr),
            param("outCross", voidPtr),
            param("rhs", voidPtr));
        if (dryRun) { skipped++; } else { updated++; }

        applySignature(
            "0x00411aa0",
            "CMonitor__ComputeTerrainVelocityScalar",
            "__thiscall",
            floatType,
            "Signature hardening: monitor scalar helper samples terrain/static-shadow height, compares against movement-object height, and gates by vcall velocity magnitude before returning a terrain/velocity factor. Caller evidence is CMonitor__UpdateMovementTransitionAndEffects; exact source identity, concrete layout, runtime behavior, and rebuild parity remain unproven.",
            dryRun,
            param("this", voidPtr));
        if (dryRun) { skipped++; } else { updated++; }

        applySignature(
            "0x00411b70",
            "CBattleEngineJetPart__IsStateMachineActive",
            "__thiscall",
            intType,
            "Owner/signature correction: CBattleEngine::Morph calls this through battleEngine +0x57c before jet/walker transition work; body returns non-zero when local +0x2c or +0x48 state is active. Exact source method name, concrete JetPart layout, runtime morph behavior, and rebuild parity remain unproven.",
            dryRun,
            param("this", voidPtr));
        if (dryRun) { skipped++; } else { updated++; }

        applySignature(
            "0x00411e70",
            "CBattleEngineJetPart__ChangeWeapon",
            "__thiscall",
            voidType,
            "Owner/signature correction: +0x57c JetPart weapon-cycle body matches Stuart CBattleEngineJetPart::ChangeWeapon shape by counting weapons, selecting the next active/usable weapon, clearing slow movement, losing weapon charge, and auto-zooming when zoom mode changes. Static source/caller evidence only; runtime weapon switching remains unproven.",
            dryRun,
            param("this", voidPtr));
        if (dryRun) { skipped++; } else { updated++; }

        applySignature(
            "0x00412000",
            "CBattleEngineJetPart__LoseWeaponCharge",
            "__thiscall",
            voidType,
            "Owner/signature correction: CBattleEngine::Morph calls this through battleEngine +0x57c; body walks the selected JetPart weapon entry and clears weapon +0x60 charge/progress. Source-aligned with CBattleEngineJetPart::LoseWeaponCharge, but exact CWeapon layout, runtime behavior, and rebuild parity remain unproven.",
            dryRun,
            param("this", voidPtr));
        if (dryRun) { skipped++; } else { updated++; }

        applySignature(
            "0x00412050",
            "CBattleEngineJetPart__WeaponFired",
            "__thiscall",
            intType,
            "Owner/signature correction: CBattleEngine__CanSpawnBurstForResolvedEntry calls this through battleEngine +0x57c with the resolved weapon context; ret 0x4 and source/decompile evidence match JetPart weapon-fired quota, ammo depletion, heat/overheat, and cooldown bookkeeping. It does not prove CBattleEngine::WeaponFired stealth reset identity or runtime cloak behavior.",
            dryRun,
            param("this", voidPtr),
            param("weapon", voidPtr));
        if (dryRun) { skipped++; } else { updated++; }

        applySignature(
            "0x004121b0",
            "CBattleEngineJetPart__GetWeaponAmmoPercentage",
            "__thiscall",
            floatType,
            "Owner/signature correction: CBattleEngine__GetWeaponAmmoPercentage routes state-3/+0x57c calls here; body walks the selected JetPart weapon, divides store value +0x52c by configuration store capacity +0x88, and clamps to 1.0. Static source/caller evidence only; runtime HUD behavior remains unproven.",
            dryRun,
            param("this", voidPtr));
        if (dryRun) { skipped++; } else { updated++; }

        applySignature(
            "0x004122b0",
            "CBattleEngineJetPart__IsWeaponOverheated",
            "__thiscall",
            intType,
            "Owner/signature correction: CBattleEngine__IsWeaponOverheated routes state-3/+0x57c calls here; body returns selected weapon store overheat flag at battleEngine +0x55c[store]. Static source/caller evidence only; runtime HUD behavior remains unproven.",
            dryRun,
            param("this", voidPtr));
        if (dryRun) { skipped++; } else { updated++; }

        applySignature(
            "0x00412310",
            "CBattleEngineJetPart__IsEnergyWeapon",
            "__thiscall",
            intType,
            "Owner/signature correction: CBattleEngine__IsEnergyWeapon routes state-3/+0x57c calls here; body returns selected weapon store heat/energy flag at battleEngine +0x544[store]. Static source/caller evidence only; runtime HUD behavior remains unproven.",
            dryRun,
            param("this", voidPtr));
        if (dryRun) { skipped++; } else { updated++; }

        applySignature(
            "0x00412370",
            "CBattleEngineJetPart__GetWeaponCharge",
            "__thiscall",
            floatType,
            "Owner/signature correction: CBattleEngine__GetWeaponCharge routes state-3/+0x57c calls here; body walks the selected weapon and divides weapon +0x60 progress by the last valid definition threshold bucket. Static source/caller evidence only; exact CWeapon layout and runtime charge behavior remain unproven.",
            dryRun,
            param("this", voidPtr));
        if (dryRun) { skipped++; } else { updated++; }

        applySignature(
            "0x00412480",
            "CBattleEngineJetPart__GetWeaponPhysicsName",
            "__thiscall",
            charPtr,
            "Owner/signature correction: CBattleEngine__GetWeaponPhysicsName routes state-3/+0x57c calls here; body returns the selected weapon definition/context field at +0x00, matching source GetWeaponPhysicsName/GetName intent. Exact retail field layout and runtime script behavior remain unproven.",
            dryRun,
            param("this", voidPtr));
        if (dryRun) { skipped++; } else { updated++; }

        applySignature(
            "0x004124d0",
            "CBattleEngineJetPart__GetCurrentWeaponNameField04",
            "__thiscall",
            charPtr,
            "Owner/signature correction: CBattleEngine__ChangeWeapon routes state-3/+0x57c calls here before HUD weapon-sample string matching; body returns selected weapon definition/context field +0x04. The exact source accessor name, string ownership, runtime audio behavior, and rebuild parity remain unproven.",
            dryRun,
            param("this", voidPtr));
        if (dryRun) { skipped++; } else { updated++; }

        applySignature(
            "0x00412520",
            "CBattleEngineJetPart__GetWeaponIconName",
            "__thiscall",
            charPtr,
            "Owner/signature correction: CBattleEngine__GetWeaponIconName routes state-3/+0x57c calls here; body returns selected weapon definition/context field +0x38, matching source GetWeaponIconName intent. Exact retail CWeapon layout and runtime HUD behavior remain unproven.",
            dryRun,
            param("this", voidPtr));
        if (dryRun) { skipped++; } else { updated++; }

        applySignature(
            "0x00412570",
            "CBattleEngineJetPart__CanWeaponFire",
            "__thiscall",
            intType,
            "Owner/signature correction: projectile/targeting helper calls this through the JetPart selected weapon set; body mirrors source CanWeaponFire-style ammo/heat/overheat gates for the current weapon. It does not prove weapon-fired stealth reset identity or runtime fire-while-cloaked behavior.",
            dryRun,
            param("this", voidPtr));
        if (dryRun) { skipped++; } else { updated++; }

        applySignature(
            "0x00412610",
            "CBattleEngineJetPart__GetCurrentWeapon",
            "__thiscall",
            voidPtr,
            "Owner/signature correction: projectile/targeting and state helpers call this through battleEngine +0x57c JetPart selected weapon set; body walks the selected index and returns the current weapon pointer, source-aligned with GetCurrentWeapon. Exact CWeapon layout, source inlining/folding, runtime behavior, and rebuild parity remain unproven.",
            dryRun,
            param("this", voidPtr));
        if (dryRun) { skipped++; } else { updated++; }

        println("--- SUMMARY ---");
        println("updated=" + updated + " skipped=" + skipped + " missing=0 bad=0");
    }
}
