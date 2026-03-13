//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.data.BooleanDataType;
import ghidra.program.model.data.ByteDataType;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.FloatDataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

public class ApplyMenuItemWave2Signatures extends GhidraScript {

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
        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(VoidDataType.dataType);
        DataType intType = IntegerDataType.dataType;
        DataType floatType = FloatDataType.dataType;
        DataType byteType = ByteDataType.dataType;
        DataType boolType = BooleanDataType.dataType;

        int updated = 0;

        Function f4a37c0 = getFunctionOrThrow("0x004a37c0");
        f4a37c0.setCallingConvention("__thiscall");
        f4a37c0.setReturnType(voidType, SourceType.USER_DEFINED);
        f4a37c0.replaceParameters(
            FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS,
            true,
            SourceType.USER_DEFINED,
            param("this", voidPtr),
            param("x", floatType),
            param("y", floatType),
            param("interactive", intType)
        );
        updated++;

        Function f4a3be0 = getFunctionOrThrow("0x004a3be0");
        f4a3be0.setCallingConvention("__thiscall");
        f4a3be0.setReturnType(voidType, SourceType.USER_DEFINED);
        f4a3be0.replaceParameters(
            FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS,
            true,
            SourceType.USER_DEFINED,
            param("this", voidPtr),
            param("x", floatType),
            param("y", floatType),
            param("interactive", intType)
        );
        updated++;

        Function f4a40e0 = getFunctionOrThrow("0x004a40e0");
        setThiscallOneParam(f4a40e0, byteType, voidPtr);
        updated++;

        Function f4a4110 = getFunctionOrThrow("0x004a4110");
        f4a4110.setCallingConvention("__thiscall");
        f4a4110.setReturnType(voidType, SourceType.USER_DEFINED);
        f4a4110.replaceParameters(
            FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS,
            true,
            SourceType.USER_DEFINED,
            param("this", voidPtr),
            param("from_controller", intType),
            param("button", intType)
        );
        updated++;

        Function f4a4290 = getFunctionOrThrow("0x004a4290");
        f4a4290.setCallingConvention("__thiscall");
        f4a4290.setReturnType(voidType, SourceType.USER_DEFINED);
        f4a4290.replaceParameters(
            FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS,
            true,
            SourceType.USER_DEFINED,
            param("this", voidPtr),
            param("from_controller", intType),
            param("button", intType)
        );
        updated++;

        Function f4a42f0 = getFunctionOrThrow("0x004a42f0");
        setThiscallOneParam(f4a42f0, boolType, voidPtr);
        updated++;

        Function f4a4310 = getFunctionOrThrow("0x004a4310");
        f4a4310.setCallingConvention("__thiscall");
        f4a4310.setReturnType(voidType, SourceType.USER_DEFINED);
        f4a4310.replaceParameters(
            FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS,
            true,
            SourceType.USER_DEFINED,
            param("this", voidPtr),
            param("x", floatType),
            param("y", floatType),
            param("alpha", intType)
        );
        updated++;

        Function f4a43a0 = getFunctionOrThrow("0x004a43a0");
        f4a43a0.setCallingConvention("__thiscall");
        f4a43a0.setReturnType(voidType, SourceType.USER_DEFINED);
        f4a43a0.replaceParameters(
            FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS,
            true,
            SourceType.USER_DEFINED,
            param("this", voidPtr),
            param("from_controller", intType),
            param("button", intType)
        );
        updated++;

        Function f4a4450 = getFunctionOrThrow("0x004a4450");
        setThiscallOneParam(f4a4450, intType, voidPtr);
        updated++;

        println("ApplyMenuItemWave2Signatures: updated=" + updated);
    }
}

