//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

public class ApplyBattleEngineD0TailSignatureTranche extends GhidraScript {

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

        DataType intType = IntegerDataType.dataType;
        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);
        int updated = 0;
        int skipped = 0;

        applySignature(
            "0x0040d0f0",
            "CWeaponStatement__UsesBallisticArcNoLocks",
            "CEngine__CanUseBallisticArcNoLocks",
            "__thiscall",
            intType,
            "Owner/name correction: weapon-definition ballistic gate used by CUnit min/max ballistic range and OID aim/fire checks. The body returns true when projectile gravity is non-zero and lock-style fields +0x50/+0x6c are clear. Static caller/decompile evidence only; not runtime weapon-fire, stealth, or exact source CWeapon identity proof.",
            dryRun,
            param("weaponStatement", voidPtr));
        if (dryRun) { skipped++; } else { updated++; }

        applySignature(
            "0x0040d470",
            "CLine__ctor_fromEndpoints",
            "CGeneralVolume__ctor_like_0040d470",
            "__thiscall",
            voidType,
            "Owner/name correction: CLine constructor shape. The body writes the CGeneralVolume base vtable, copies two 16-byte endpoint/vector blocks, then writes the CLine vtable confirmed by RTTI read-back. Static vtable/decompile evidence only; runtime collision behavior remain unproven.",
            dryRun,
            param("this", voidPtr),
            param("startPoint", voidPtr),
            param("endPoint", voidPtr));
        if (dryRun) { skipped++; } else { updated++; }

        applySignature(
            "0x0040da30",
            "CBattleEngine__BuildInterpolatedWorldTransform",
            "CExplosionInitThing__BuildInterpolatedWorldTransform",
            "__thiscall",
            voidPtr,
            "Owner/name correction from the target-marker caller: CExplosionInitThing__RenderTargetMarkers3D passes the BattleEngine pointer at +0x50, and the body builds an interpolated BattleEngine world transform into the output buffer from current/old position and orientation fields. Static render-path evidence only; runtime render behavior remain unproven.",
            dryRun,
            param("this", voidPtr),
            param("outWorldTransform", voidPtr),
            param("unusedContext", voidPtr));
        if (dryRun) { skipped++; } else { updated++; }

        applySignature(
            "0x0040dc90",
            "CBattleEngine__CountFlag9CBySelectionMode",
            "CExplosionInitThing__CountFlag9CBySelectionMode",
            "__thiscall",
            intType,
            "Owner/name correction: BattleEngine selection-state helper. If +0x260 == 3 it tail-calls LinkedObjectList__CountFlag9C on +0x57c; otherwise it counts the +0x578 list with the extra-entry variant. Static objective-panel caller evidence only; not objective completion runtime proof.",
            dryRun,
            param("this", voidPtr));
        if (dryRun) { skipped++; } else { updated++; }

        applySignature(
            "0x0040dcb0",
            "CBattleEngine__SetFlag58CEnabled",
            "CCockpit__SetFlag58C_Enabled",
            "__thiscall",
            voidType,
            "Owner correction: tiny BattleEngine state setter that writes 1 to +0x58c, adjacent to the +0x260/+0x58c transition-selection context used by neighboring BattleEngine helpers. Static object-layout evidence only; runtime behavior remain unproven.",
            dryRun,
            param("this", voidPtr));
        if (dryRun) { skipped++; } else { updated++; }

        applySignature(
            "0x0040dce0",
            "CBattleEngine__HostileEnvironment",
            "CBattleEngine__HostileEnvironment",
            "__thiscall",
            voidType,
            "Source bridge: source CBattleEngine::HostileEnvironment emits hud_hostile_environment/log context after the mLastTimeInHostileEnviroment throttle and updates the timestamp; retail decompile mirrors HUD sample lookup/play and timestamp write at +0x510. Static source/decompile/caller evidence only; not runtime HUD audio proof.",
            dryRun,
            param("this", voidPtr));
        if (dryRun) { skipped++; } else { updated++; }

        println("--- SUMMARY ---");
        println("updated=" + updated + " skipped=" + skipped + " missing=0 bad=0");
    }
}
