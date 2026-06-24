//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.ByteDataType;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.DoubleDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

public class ApplyCockpitCompassSignatureCorrection extends GhidraScript {

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

    private boolean applyCorrection(
            String addr,
            String oldName,
            String newName,
            String callingConvention,
            DataType returnType,
            String comment,
            boolean dryRun,
            ParameterImpl... params) throws Exception {
        Function fn = getFunctionOrThrow(addr);
        String currentName = fn.getName();
        if (!currentName.equals(oldName) && !currentName.equals(newName)) {
            throw new IllegalStateException("Unexpected function name at " + addr + ": " + currentName + " != " + oldName + " or " + newName);
        }

        if (dryRun) {
            println("DRY: " + addr + " " + currentName + " -> " + newName);
            return false;
        }

        boolean changed = !currentName.equals(newName);
        if (changed) {
            fn.setName(newName, SourceType.USER_DEFINED);
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
        println("OK: " + addr + " " + currentName + " -> " + fn.getSignature().toString());
        return true;
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");
        println("Mode: " + (dryRun ? "dry" : "apply"));

        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);
        DataType byteType = ByteDataType.dataType;
        DataType doubleType = DoubleDataType.dataType;
        int updated = 0;
        int skipped = 0;

        if (applyCorrection(
            "0x00405970",
            "CDXCockpit__VFunc_01_00405970",
            "CDXCockpit__scalar_deleting_dtor",
            "__thiscall",
            voidPtr,
            "Signature correction for CDXCockpit scalar-deleting destructor. Decompile/instruction evidence calls CDXCockpit__dtor_base_thunk, tests the delete flag, optionally calls OID__FreeObject, and returns this. Exact source virtual name, concrete layout, tags, locals, and runtime behavior remain unproven.",
            dryRun,
            param("this", voidPtr),
            param("flags", byteType))) { updated++; } else { skipped++; }

        if (applyCorrection(
            "0x00405990",
            "CCockpit__ctor_like_00424730",
            "CDXCockpit__dtor_base_thunk",
            "__fastcall",
            voidType,
            "Signature correction for a CDXCockpit destructor-base jump thunk. Instruction/xref evidence shows this entry jumps to CCockpit__dtor_base and is called by CDXCockpit__scalar_deleting_dtor. Exact CDXCockpit destructor side effects, concrete layout, tags, locals, and runtime behavior remain unproven.",
            dryRun,
            param("this", voidPtr))) { updated++; } else { skipped++; }

        if (applyCorrection(
            "0x00406040",
            "CDXCompass__GetTrackedPositionX",
            "CDXCompass__GetTrackedPositionX",
            "__fastcall",
            doubleType,
            "Signature correction for CDXCompass tracked-position X getter. Decompile evidence reads a tracked pointer from context +0x4b0 and returns the +0x1c float via the FPU; xrefs include CDXCompass__Render and dynamic overlay update. Exact context layout, return precision, tags, locals, and runtime behavior remain unproven.",
            dryRun,
            param("context", voidPtr))) { updated++; } else { skipped++; }

        if (applyCorrection(
            "0x0040c630",
            "CDXCompass__GetTrackedPositionY",
            "CDXCompass__GetTrackedPositionY",
            "__fastcall",
            doubleType,
            "Signature correction for CDXCompass tracked-position Y getter. Decompile evidence reads a tracked pointer from context +0x4b0 and returns the +0x20 float via the FPU; xrefs include CDXCompass__Render and dynamic overlay update. Exact context layout, return precision, tags, locals, and runtime behavior remain unproven.",
            dryRun,
            param("context", voidPtr))) { updated++; } else { skipped++; }

        if (applyCorrection(
            "0x00424710",
            "CCockpit__VFunc_01_00424710",
            "CCockpit__scalar_deleting_dtor",
            "__thiscall",
            voidPtr,
            "Signature correction for CCockpit scalar-deleting destructor. Decompile/instruction evidence calls CCockpit__dtor_base, tests the delete flag, optionally calls OID__FreeObject, and returns this. Exact source virtual name, concrete layout, tags, locals, and runtime behavior remain unproven.",
            dryRun,
            param("this", voidPtr),
            param("flags", byteType))) { updated++; } else { skipped++; }

        if (applyCorrection(
            "0x00424730",
            "CCockpit__ctor_like_00424730",
            "CCockpit__dtor_base",
            "__fastcall",
            voidType,
            "Signature correction for CCockpit destructor base. Decompile/instruction evidence resets CCockpit vtable slots 0x005d9524 and 0x005d94ac, releases the +0x8c owned object through a vcall when present, and calls CMonitor__Shutdown. Concrete CCockpit layout, exact source identity, tags, locals, runtime behavior, and destructor side-effect completeness remain unproven.",
            dryRun,
            param("this", voidPtr))) { updated++; } else { skipped++; }

        println("--- SUMMARY ---");
        println("updated=" + updated + " skipped=" + skipped + " missing=0 bad=0");
    }
}
