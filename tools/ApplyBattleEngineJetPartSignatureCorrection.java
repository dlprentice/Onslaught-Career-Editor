//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.FloatDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

public class ApplyBattleEngineJetPartSignatureCorrection extends GhidraScript {
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

    private boolean nameAllowed(String currentName, String expectedName, String... priorNames) {
        if (currentName.equals(expectedName)) {
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

    private void applySignature(
            String addr,
            String expectedName,
            String callingConvention,
            DataType returnType,
            String comment,
            boolean dryRun,
            String[] priorNames,
            ParameterImpl... params) throws Exception {
        Function fn = getFunctionOrThrow(addr);
        if (!nameAllowed(fn.getName(), expectedName, priorNames)) {
            throw new IllegalStateException("Unexpected function name at " + addr + ": " + fn.getName() + " != " + expectedName);
        }

        if (dryRun) {
            println("DRY: " + addr + " " + fn.getName() + " -> " + expectedSignature(expectedName, callingConvention, returnType, params));
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
        DataType floatType = FloatDataType.dataType;
        int updated = 0;
        int skipped = 0;

        applySignature(
            "0x00410210",
            "CBattleEngineJetPart__ctor",
            "__thiscall",
            voidPtr,
            "Source/decompile correction: CBattleEngineJetPart constructor stores mainPart at +0x18, zeroes jet-part movement/state fields, seeds -10.0-style timing fields, calls ResetConfiguration, and sets thruster value to 0.5. Corrects the prior CBattleEngine target-set helper label; concrete layout, local names, runtime jet behavior, tags, and rebuild parity remain unproven.",
            dryRun,
            new String[] {"CBattleEngine__InitTargetSetBucketState", "CBattleEngine__Helper_00410210"},
            param("this", voidPtr),
            param("mainPart", voidPtr));
        if (dryRun) { skipped++; } else { updated++; }

        applySignature(
            "0x004102a0",
            "CBattleEngineJetPart__dtor_base",
            "__thiscall",
            voidType,
            "Source/decompile correction: CBattleEngineJetPart destructor-base loop removes weapon entries from the SPtrSet and dispatches the deleting destructor before clearing the set. Corrects the prior CBattleEngine SPtrSet helper label; concrete layout, destructor wrapper pairing, runtime weapon ownership, tags, and rebuild parity remain unproven.",
            dryRun,
            new String[] {"CBattleEngine__DestroySPtrSetElementsAndClear"},
            param("this", voidPtr));
        if (dryRun) { skipped++; } else { updated++; }

        applySignature(
            "0x00410310",
            "CBattleEngineJetPart__Thrust",
            "__thiscall",
            voidType,
            "Source/decompile correction: CBattleEngineJetPart::Thrust updates the thruster value from moveY, tracks hard-forward timing, starts loop state when the forward/backward threshold sequence, energy gate, and velocity gate agree, and stores the last Y input. Runtime input behavior and concrete layout remain unproven.",
            dryRun,
            new String[] {"CGeneralVolume__HandleBoostWindowInput"},
            param("this", voidPtr),
            param("moveY", floatType));
        if (dryRun) { skipped++; } else { updated++; }

        applySignature(
            "0x00410490",
            "CBattleEngineJetPart__Turn",
            "__thiscall",
            voidType,
            "Source/decompile correction: CBattleEngineJetPart::Turn applies yaw and roll velocity from moveX, scales by configuration turn rate, zoom, low-speed grounded movement, slow movement, and transform-start interpolation before updating main-part yaw/roll velocity. Runtime input behavior and concrete layout remain unproven.",
            dryRun,
            new String[] {"CGeneralVolume__ApplyInputDampingToVelocity"},
            param("this", voidPtr),
            param("moveX", floatType));
        if (dryRun) { skipped++; } else { updated++; }

        applySignature(
            "0x00410670",
            "CBattleEngineJetPart__Pitch",
            "__thiscall",
            voidType,
            "Source/decompile correction: CBattleEngineJetPart::Pitch applies pitch velocity from moveY, scales by zoom, slow movement, and transform-start interpolation before updating main-part pitch velocity. Corrects the prior GeneralVolume drain/update label; runtime input behavior and concrete layout remain unproven.",
            dryRun,
            new String[] {"CGeneralVolume__DrainLinkedObjectFromVelocity"},
            param("this", voidPtr),
            param("moveY", floatType));
        if (dryRun) { skipped++; } else { updated++; }

        applySignature(
            "0x00410740",
            "CBattleEngineJetPart__YawLeft",
            "__thiscall",
            voidType,
            "Source/decompile correction: CBattleEngineJetPart::YawLeft tracks hard-left timing, can break a loop from a right/left threshold sequence, can start a left barrel roll with lateral velocity injection, updates last X input, and adds strafing acceleration when energy/input thresholds agree. Runtime input behavior and concrete layout remain unproven.",
            dryRun,
            new String[] {"CGeneralVolume__HandleAxisPositiveThresholdCross"},
            param("this", voidPtr),
            param("moveX", floatType));
        if (dryRun) { skipped++; } else { updated++; }

        applySignature(
            "0x004109d0",
            "CBattleEngineJetPart__YawRight",
            "__thiscall",
            voidType,
            "Source/decompile correction: CBattleEngineJetPart::YawRight tracks hard-right timing, can break a loop from a left/right threshold sequence, can start a right barrel roll with lateral velocity injection, updates last X input, and adds strafing acceleration when energy/input thresholds agree. Runtime input behavior and concrete layout remain unproven.",
            dryRun,
            new String[] {"CGeneralVolume__HandleAxisNegativeThresholdCross"},
            param("this", voidPtr),
            param("moveX", floatType));
        if (dryRun) { skipped++; } else { updated++; }

        applySignature(
            "0x004114d0",
            "CBattleEngineJetPart__Gravity",
            "__thiscall",
            floatType,
            "Source/decompile correction: CBattleEngineJetPart::Gravity returns the small gravity factor when the linked main-part energy field is zero and otherwise returns 0.0. Corrects the prior generic flag-scalar label; runtime flight physics, exact constants, concrete layout, tags, and rebuild parity remain unproven.",
            dryRun,
            new String[] {"CGeneralVolume__GetFlagFCScalar"},
            param("this", voidPtr));
        if (dryRun) { skipped++; } else { updated++; }

        applySignature(
            "0x00411500",
            "CBattleEngineJetPart__HandleSkimming",
            "__thiscall",
            voidType,
            "Source/decompile correction: CBattleEngineJetPart::HandleSkimming samples terrain/water-style height context, checks low-altitude high-speed skimming, damps velocity, applies damage, and calls CBattleEngine__HostileEnvironment. Corrects the prior CMonitor hostile-environment penalty label; runtime skimming behavior, concrete map helper identity, layout, tags, and rebuild parity remain unproven.",
            dryRun,
            new String[] {"CMonitor__ApplyHostileEnvironmentPenalty"},
            param("this", voidPtr));
        if (dryRun) { skipped++; } else { updated++; }

        println("--- SUMMARY ---");
        println("updated=" + updated + " skipped=" + skipped + " missing=0 bad=0");
    }
}
