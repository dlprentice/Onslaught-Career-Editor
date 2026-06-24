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

public class ApplyTransitionTargetingSignatureTranche extends GhidraScript {

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
            throw new IllegalStateException("Unexpected function name at " + addr + ": " + fn.getName() + " != " + expectedName);
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
            "0x0040a580",
            "CBattleEngine__Morph",
            "CMonitor__UpdateFlightWalkerTransitionState",
            "__fastcall",
            voidType,
            "Source bridge/name correction: body matches Stuart CBattleEngine::Morph() by state gates, special-move lockouts, weapon-charge loss, BECOME_WALKER/BECOME_JET events 0x1771/6000, flytowalk/walktofly animation paths, cockpit/part transition calls, and transform audio hooks. Runtime behavior, concrete layout, tags, locals, and rebuild parity remain unproven.",
            dryRun,
            param("battleEngine", voidPtr));
        if (dryRun) { skipped++; } else { updated++; }

        applySignature(
            "0x0040ac50",
            "CBattleEngine__Rearm",
            "CGeneralVolume__IntegrateSlotAccumulators",
            "__thiscall",
            voidType,
            "Source bridge/name correction: ret 0x4 and decompile body match Stuart CBattleEngine::Rearm(float inAmount), iterating six stores, skipping heated stores, adding inAmount * configuration store value, and clamping at the configured maximum. Runtime behavior, concrete layout, tags, locals, and rebuild parity remain unproven.",
            dryRun,
            param("this", voidPtr),
            param("inAmount", floatType));
        if (dryRun) { skipped++; } else { updated++; }

        applySignature(
            "0x0040acc0",
            "CBattleEngine__CalcUnitOverCrossHair",
            "CBattleEngine__SelectBestAimTargetAndMaybeQueueEvent",
            "__thiscall",
            voidPtr,
            "Source bridge/name correction: ret 0xc and body match Stuart CBattleEngine::CalcUnitOverCrossHair(CEvent *, BOOL, BOOL): optional current-target reader reset, auto-aim matrix/view ray construction, mesh/outer-sphere trace selection, range-filtered unit result, regardless-of-range reader update, and event 0x1772 reschedule. Runtime behavior, concrete layout, tags, locals, and rebuild parity remain unproven.",
            dryRun,
            param("this", voidPtr),
            param("event", voidPtr),
            param("useMeshCollision", intType),
            param("updateReaders", intType));
        if (dryRun) { skipped++; } else { updated++; }

        applySignature(
            "0x0040b100",
            "CGeneralVolume__ctor_base",
            "CGeneralVolume__ctor_zero_fields",
            "__fastcall",
            voidType,
            "Owner/name correction: body installs the CGeneralVolume vtable and zeroes +0x4/+0x8/+0xc; ResolveVtableTypeNames confirms CGeneralVolume RTTI at vtable 0x005d892c. Runtime behavior, concrete layout, exact constructor/source identity, tags, locals, and rebuild parity remain unproven.",
            dryRun,
            param("generalVolume", voidPtr));
        if (dryRun) { skipped++; } else { updated++; }

        applySignature(
            "0x0040b120",
            "CBattleEngine__UpdateAutoAim",
            "CMonitor__UpdateTargetTrackingAimOffsets",
            "__fastcall",
            voidType,
            "Source bridge/name correction: body matches Stuart CBattleEngine::UpdateAutoAim(), refreshing current weapon/target reader state, computing predictive and direct target yaw/pitch offsets, latching desired offsets, and smoothing +0x4e8/+0x4f4 using AngleDifference. Runtime behavior, concrete layout, tags, locals, and rebuild parity remain unproven.",
            dryRun,
            param("battleEngine", voidPtr));
        if (dryRun) { skipped++; } else { updated++; }

        applySignature(
            "0x0040b660",
            "AngleDifference",
            "Math__GetSignedWrappedAngleDelta",
            "__cdecl",
            floatType,
            "Source bridge/name correction: free math helper matches Stuart AngleDifference-style signed wrapped angular delta between two float inputs and is not CGeneralVolume-owned in the checked caller evidence. Runtime behavior, exact calling provenance, tags, locals, and rebuild parity remain unproven.",
            dryRun,
            param("currentAngle", floatType),
            param("targetAngle", floatType));
        if (dryRun) { skipped++; } else { updated++; }

        applySignature(
            "0x0040b6d0",
            "CBattleEngine__HandleAutoAim",
            "CBattleEngine__AcquireTargetWithBallisticConstraints",
            "__thiscall",
            voidType,
            "Source bridge/name correction: ret 0x4 and body match Stuart CBattleEngine::HandleAutoAim(CEvent *), clearing target reader +0x4e0, honoring the allowed-auto-aim gate, scanning MapWho candidates, filtering weapon/mount/range/angle/stealth context, confirming line trace, and rescheduling event 0x1773. Runtime behavior, concrete layout, tags, locals, and rebuild parity remain unproven.",
            dryRun,
            param("this", voidPtr),
            param("event", voidPtr));
        if (dryRun) { skipped++; } else { updated++; }

        println("--- SUMMARY ---");
        println("updated=" + updated + " skipped=" + skipped + " missing=0 bad=0");
    }
}
