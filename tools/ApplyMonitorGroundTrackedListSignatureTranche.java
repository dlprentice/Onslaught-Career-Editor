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

public class ApplyMonitorGroundTrackedListSignatureTranche extends GhidraScript {
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
        DataType floatType = FloatDataType.dataType;
        int updated = 0;
        int skipped = 0;

        applySignature(
            "0x0040e1b0",
            "VFuncSlot_00_0040e1b0",
            "__thiscall",
            voidType,
            "Signature hardening: owner-unresolved vfunc slot body copies/clones sourceObject fields into this, including matrix/transform blocks and +0x14..+0x3b0 state. Xrefs include spawner and squad contexts, but exact owner/source identity, tags, structures, local names, runtime behavior, and rebuild parity remain unproven.",
            dryRun,
            param("this", voidPtr),
            param("sourceObject", voidPtr));
        if (dryRun) { skipped++; } else { updated++; }

        applySignature(
            "0x0040e840",
            "CMonitor__ToggleAttachedObjectFlag300",
            "__fastcall",
            voidType,
            "Signature hardening: monitor helper reads attached object pointer at +0x528 and toggles the attached object's +0x12c integer flag. Exact attached-object type, source identity, local names, runtime behavior, and rebuild parity remain unproven.",
            dryRun,
            param("monitor", voidPtr));
        if (dryRun) { skipped++; } else { updated++; }

        applySignature(
            "0x0040e860",
            "CGeneralVolume__OffsetPointByForwardScaled",
            "__thiscall",
            voidType,
            "Signature hardening: ret 0x8 preserves two stack slots; body mutates point by adding the current forward vector from vcall +0x6c scaled by _DAT_005d85ec and optionally runs attached-object +0x528 transform context. The second stack slot is currently unused by decompile. Exact source identity, point type, local names, runtime behavior, and rebuild parity remain unproven.",
            dryRun,
            param("this", voidPtr),
            param("point", voidPtr),
            param("unusedContext", voidPtr));
        if (dryRun) { skipped++; } else { updated++; }

        applySignature(
            "0x0040e8e0",
            "CUnit__IsNearGroundByTerrainProbe",
            "__fastcall",
            floatType,
            "Signature hardening: unit terrain/shadow height predicate calls CStaticShadows__SampleShadowHeightBilinear with unit position context at +0x1c and compares sampled height against unit +0x24. Exact source identity, unit layout, local names, runtime behavior, and rebuild parity remain unproven.",
            dryRun,
            param("unit", voidPtr));
        if (dryRun) { skipped++; } else { updated++; }

        applySignature(
            "0x0040e910",
            "CUnit__GetGroundedControlFactor",
            "__fastcall",
            floatType,
            "Signature hardening: grounded-control factor checks vtable +0x10c and HeightDelta__Below015_D4 before returning one of two global float factors. Exact source identity, unit layout, local names, runtime behavior, and rebuild parity remain unproven.",
            dryRun,
            param("unit", voidPtr));
        if (dryRun) { skipped++; } else { updated++; }

        applySignature(
            "0x0040e940",
            "CMonitor__UpdateTrackedList_59C",
            "__fastcall",
            voidType,
            "Signature hardening: monitor tracked-list update walks +0x1d4 entries, uses +0x59c/+0x614 sound/effect context, dispatches selector 0x1a through vtable +0x160, and marks +0x1e4 active. Exact source identity, list node layout, local names, runtime behavior, and rebuild parity remain unproven.",
            dryRun,
            param("monitor", voidPtr));
        if (dryRun) { skipped++; } else { updated++; }

        applySignature(
            "0x0040eb50",
            "CMonitor__FlushTrackedList_1D4",
            "__fastcall",
            voidType,
            "Signature hardening: monitor flushes tracked list +0x1d4 when +0x1e4 is set, finalizes linked unit state, touches +0x59c sound-event context, and clears +0x1e4. Exact source identity, list node layout, local names, runtime behavior, and rebuild parity remain unproven.",
            dryRun,
            param("monitor", voidPtr));
        if (dryRun) { skipped++; } else { updated++; }

        applySignature(
            "0x0040ebf0",
            "CMonitor__UpdateTrackedList_620",
            "__fastcall",
            voidType,
            "Signature hardening: secondary monitor tracked-list update walks +0x620 entries, gates by +0x630/+0x634 mode state, uses +0x618/+0x61c effects, and dispatches selector 0x17 through vtable +0x160. Exact source identity, list node layout, local names, runtime behavior, and rebuild parity remain unproven.",
            dryRun,
            param("monitor", voidPtr));
        if (dryRun) { skipped++; } else { updated++; }

        println("--- SUMMARY ---");
        println("updated=" + updated + " skipped=" + skipped + " missing=0 bad=0");
    }
}
