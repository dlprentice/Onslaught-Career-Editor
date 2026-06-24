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

public class ApplyLinkedMonitorSignatureTranche extends GhidraScript {

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
        int updated = 0;
        int skipped = 0;

        applySignature(
            "0x00409760",
            "LinkedPtrCursor__MoveFirstAndGet",
            null,
            "__fastcall",
            voidPtr,
            "Signature hardening: iterator/cursor First helper reads list pointer at +0x4, stores the first node as current, and returns the node item pointer. Exact list layout, source identity, runtime behavior, and rebuild parity remain unproven.",
            dryRun,
            param("cursor", voidPtr));
        if (dryRun) { skipped++; } else { updated++; }

        applySignature(
            "0x00409780",
            "LinkedPtrCursor__MoveNextAndGet",
            null,
            "__fastcall",
            voidPtr,
            "Signature hardening: iterator/cursor Next helper advances the current node through +0x4 and returns the node item pointer. Exact list layout, source identity, runtime behavior, and rebuild parity remain unproven.",
            dryRun,
            param("cursor", voidPtr));
        if (dryRun) { skipped++; } else { updated++; }

        applySignature(
            "0x004097a0",
            "CUnit__PushTransformHistoryAndSetCurrent",
            null,
            "__thiscall",
            voidType,
            "Signature hardening: ret 0x4 shows one transform pointer; body pushes current/old transform rows and refreshes timestamp-like +0xac from DAT_00672fd0 when enabled. Exact CUnit layout, source identity, runtime behavior, and rebuild parity remain unproven.",
            dryRun,
            param("this", voidPtr),
            param("transform", voidPtr));
        if (dryRun) { skipped++; } else { updated++; }

        applySignature(
            "0x00409880",
            "CMonitor__GetLastValidRangeStep100",
            null,
            "__fastcall",
            intType,
            "Signature hardening: monitor range-step helper scans five 100-step slots from monitor +0xa4 and returns the last slot whose entry is not -1. Exact monitor/range layout, source identity, runtime behavior, and rebuild parity remain unproven.",
            dryRun,
            param("monitor", voidPtr));
        if (dryRun) { skipped++; } else { updated++; }

        applySignature(
            "0x004098e0",
            "CLine__ctor_copy",
            "CGeneralVolume__ctor_like_004098e0",
            "__thiscall",
            voidType,
            "Owner correction: body installs the CGeneralVolume base vtable then the CLine vtable while copying three 16-byte rows from sourceLine; ResolveVtableTypeNames confirms CGeneralVolume and CLine RTTI. Exact constructor identity, concrete CLine/CGeneralVolume layout, source identity, runtime behavior, and rebuild parity remain unproven.",
            dryRun,
            param("this", voidPtr),
            param("sourceLine", voidPtr));
        if (dryRun) { skipped++; } else { updated++; }

        applySignature(
            "0x00409950",
            "CMonitor__UpdateSoundEventPlaybackForReader",
            null,
            "__fastcall",
            voidType,
            "Signature hardening: monitor sound-event helper updates engine/health/energy/lock/walk sound chains, active-reader state at +0x5e8, and walk-sound counters. Runtime audio behavior, exact source identity, concrete layout, tags, locals, and rebuild parity remain unproven.",
            dryRun,
            param("monitor", voidPtr));
        if (dryRun) { skipped++; } else { updated++; }

        println("--- SUMMARY ---");
        println("updated=" + updated + " skipped=" + skipped + " missing=0 bad=0");
    }
}
