//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

public class ApplyControllerDefinitionSignatures extends GhidraScript {

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

    @Override
    protected void run() throws Exception {
        DataType voidPtr = new PointerDataType(VoidDataType.dataType);
        int updated = 0;

        Function fInit = getFunctionOrThrow("0x00453970");
        fInit.setCallingConvention("__thiscall");
        fInit.setReturnType(VoidDataType.dataType, SourceType.USER_DEFINED);
        fInit.replaceParameters(
            FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS,
            true,
            SourceType.USER_DEFINED,
            param("this", voidPtr)
        );
        updated++;

        Function fDtor = getFunctionOrThrow("0x004539d0");
        fDtor.setCallingConvention("__thiscall");
        fDtor.setReturnType(VoidDataType.dataType, SourceType.USER_DEFINED);
        fDtor.replaceParameters(
            FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS,
            true,
            SourceType.USER_DEFINED,
            param("this", voidPtr)
        );
        updated++;

        Function fScalar = getFunctionOrThrow("0x004539b0");
        fScalar.setCallingConvention("__thiscall");
        fScalar.setReturnType(voidPtr, SourceType.USER_DEFINED);
        fScalar.replaceParameters(
            FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS,
            true,
            SourceType.USER_DEFINED,
            param("this", voidPtr),
            param("flags", IntegerDataType.dataType)
        );
        updated++;

        println("ApplyControllerDefinitionSignatures: updated=" + updated);
    }
}
