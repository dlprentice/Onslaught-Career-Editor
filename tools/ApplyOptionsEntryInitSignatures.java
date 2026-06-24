//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.ByteDataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.ShortDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

public class ApplyOptionsEntryInitSignatures extends GhidraScript {

    private Function getFunctionOrThrow(String addrText) throws Exception {
        if (!addrText.startsWith("0x") && !addrText.startsWith("0X")) {
            addrText = "0x" + addrText;
        }
        ghidra.program.model.address.Address addr = toAddr(addrText);
        if (addr == null) {
            throw new IllegalArgumentException("Bad address: " + addrText);
        }
        Function fn = getFunctionAt(addr);
        if (fn == null) {
            Function cf = getFunctionContaining(addr);
            if (cf != null && cf.getEntryPoint().equals(addr)) {
                fn = cf;
            }
        }
        if (fn == null) {
            throw new IllegalStateException("Function not found at " + addrText);
        }
        return fn;
    }

    private ParameterImpl param(String name, DataType dt) throws Exception {
        return new ParameterImpl(name, dt, currentProgram);
    }

    private void apply(Function fn, DataType ret, ParameterImpl... params) throws Exception {
        fn.setCallingConvention("__thiscall");
        fn.setReturnType(ret, SourceType.USER_DEFINED);
        fn.replaceParameters(
            FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS,
            true,
            SourceType.USER_DEFINED,
            params
        );
    }

    @Override
    protected void run() throws Exception {
        DataType voidPtr = new PointerDataType(VoidDataType.dataType);
        int updated = 0;

        Function fSingle = getFunctionOrThrow("0x0042d260");
        apply(fSingle, voidPtr,
            param("this", voidPtr),
            param("active", ByteDataType.dataType),
            param("entry_id", IntegerDataType.dataType),
            param("slot0_device_code", IntegerDataType.dataType),
            param("slot0_scan", ShortDataType.dataType),
            param("slot0_vk", ShortDataType.dataType)
        );
        updated++;

        Function fDual = getFunctionOrThrow("0x0042d2b0");
        apply(fDual, voidPtr,
            param("this", voidPtr),
            param("active", ByteDataType.dataType),
            param("entry_id", IntegerDataType.dataType),
            param("slot0_device_code", IntegerDataType.dataType),
            param("slot0_scan", ShortDataType.dataType),
            param("slot1_device_code", IntegerDataType.dataType),
            param("slot1_scan", ShortDataType.dataType),
            param("slot0_vk", ShortDataType.dataType),
            param("slot1_vk", ShortDataType.dataType)
        );
        updated++;

        Function fSentinel = getFunctionOrThrow("0x0042d300");
        apply(fSentinel, VoidDataType.dataType,
            param("this", voidPtr)
        );
        updated++;

        println("ApplyOptionsEntryInitSignatures: updated=" + updated);
    }
}
