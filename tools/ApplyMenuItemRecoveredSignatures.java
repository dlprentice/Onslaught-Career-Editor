//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.data.ByteDataType;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.ShortDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

public class ApplyMenuItemRecoveredSignatures extends GhidraScript {

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

    private void setThiscallOneParam(Function fn, DataType retType, DataType thisType) throws Exception {
        fn.setCallingConvention("__thiscall");
        fn.setReturnType(retType, SourceType.USER_DEFINED);
        fn.replaceParameters(
            FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS,
            true,
            SourceType.USER_DEFINED,
            param("this", thisType)
        );
    }

    @Override
    protected void run() throws Exception {
        DataType voidPtr = new PointerDataType(VoidDataType.dataType);
        DataType shortPtr = new PointerDataType(ShortDataType.dataType);
        DataType intType = IntegerDataType.dataType;
        DataType byteType = ByteDataType.dataType;

        int updated = 0;

        Function f53a60 = getFunctionOrThrow("0x00453a60");
        setThiscallOneParam(f53a60, intType, voidPtr);
        updated++;

        Function f53a70 = getFunctionOrThrow("0x00453a70");
        setThiscallOneParam(f53a70, intType, voidPtr);
        updated++;

        Function f53a80 = getFunctionOrThrow("0x00453a80");
        setThiscallOneParam(f53a80, byteType, voidPtr);
        updated++;

        Function f53a90 = getFunctionOrThrow("0x00453a90");
        f53a90.setCallingConvention("__thiscall");
        f53a90.setReturnType(voidPtr, SourceType.USER_DEFINED);
        f53a90.replaceParameters(
            FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS,
            true,
            SourceType.USER_DEFINED,
            param("this", voidPtr),
            param("flags", byteType)
        );
        updated++;

        Function f5930 = getFunctionOrThrow("0x00405930");
        setThiscallOneParam(f5930, intType, voidPtr);
        updated++;

        Function f4a3140 = getFunctionOrThrow("0x004a3140");
        setThiscallOneParam(f4a3140, voidPtr, voidPtr);
        updated++;

        Function f4a3190 = getFunctionOrThrow("0x004a3190");
        setThiscallOneParam(f4a3190, shortPtr, voidPtr);
        updated++;

        Function f4a3420 = getFunctionOrThrow("0x004a3420");
        setThiscallOneParam(f4a3420, intType, voidPtr);
        updated++;

        println("ApplyMenuItemRecoveredSignatures: updated=" + updated);
    }
}
