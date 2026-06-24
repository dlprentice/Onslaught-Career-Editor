//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.CharDataType;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.FloatDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

public class ApplyBattleEngineCloakHudInterpolationSignatureTranche extends GhidraScript {

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
        DataType charPtr = new PointerDataType(CharDataType.dataType);
        DataType floatType = FloatDataType.dataType;
        int updated = 0;
        int skipped = 0;

        applySignature(
            "0x0040d4d0",
            "CBattleEngine__HandleCloak",
            "CGeneralVolume__Update4ACLatchFromHeightAndA0",
            "__thiscall",
            voidType,
            "Owner/signature re-audit: source-aligned CBattleEngine::HandleCloak. The body toggles BattleEngine +0x4ac as the cloaked flag, clears +0x5dc desired-stealth state on decloak, and gates cloak activation on configuration +0x2c <= energy +0xfc plus configuration +0xa0 stealth > 0 before copying +0xa0 into +0x5dc. Static source/decompile/input-dispatch evidence only; runtime cloak activation and fire-while-cloaked behavior remain unproven.",
            dryRun,
            param("this", voidPtr));
        if (dryRun) { skipped++; } else { updated++; }

        applySignature(
            "0x0040d5b0",
            "CLockInfo__GetLockPercentage",
            "CExplosionInitThing__ComputeNormalizedTimeInRange",
            "__thiscall",
            floatType,
            "Owner/signature re-audit: source-aligned CLockInfo::GetLockPercentage. The body computes a normalized lock timer from EVENT_MANAGER time plus frame-render fraction against start/finish fields and clamps the upper bound to 1.0. Static source/decompile evidence only; runtime lock UI behavior remains unproven.",
            dryRun,
            param("this", voidPtr));
        if (dryRun) { skipped++; } else { updated++; }

        applySignature(
            "0x0040d5f0",
            "CBattleEngine__PlayHudSampleByName",
            "CBattleEngine__AttachHudSoundEventListener",
            "__thiscall",
            voidType,
            "Owner/signature re-audit: source-aligned CBattleEngine::PlayHudSample(char *). The body formats the hud\\\\%s effect name, resolves it through the global sound manager, and plays it on the BattleEngine instance with HUD-volume context. Static source/decompile/caller evidence only; runtime HUD audio behavior remains unproven.",
            dryRun,
            param("this", voidPtr),
            param("sampleName", charPtr));
        if (dryRun) { skipped++; } else { updated++; }

        applySignature(
            "0x0040d660",
            "CBattleEngine__GetInterpolatedEulerOrientation",
            "CExplosionInitThing__InterpolateWrappedEulerFromHistory",
            "__thiscall",
            voidType,
            "Owner/signature re-audit: source-aligned CBattleEngine::GetInterpolatedEulerOrientation. The retail ABI writes the source CEulerAngles return value through an output buffer; the body interpolates current/old yaw, pitch, and roll with wraparound handling and frame-render fraction. Static source/decompile evidence only; runtime camera/HUD transform behavior remains unproven.",
            dryRun,
            param("this", voidPtr),
            param("outEuler", voidPtr));
        if (dryRun) { skipped++; } else { updated++; }

        applySignature(
            "0x0040d7c0",
            "CBattleEngine__GetInterpolatedAutoAimPos",
            "CExplosionInitThing__BuildInterpolatedViewpointTransform",
            "__thiscall",
            voidPtr,
            "Owner/signature re-audit: source-aligned CBattleEngine::GetInterpolatedAutoAimPos. The retail ABI writes the source FVector return value through an output buffer; the body reads current/old player view point and orientation from the BattleEngine player pointer, interpolates by frame-render fraction, then applies auto-aim yaw/pitch offsets. Static source/decompile/caller evidence only; runtime auto-aim transform behavior remains unproven.",
            dryRun,
            param("this", voidPtr),
            param("outPos", voidPtr));
        if (dryRun) { skipped++; } else { updated++; }

        println("--- SUMMARY ---");
        println("updated=" + updated + " skipped=" + skipped + " missing=0 bad=0");
    }
}
