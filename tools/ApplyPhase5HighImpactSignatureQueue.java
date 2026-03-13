//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.data.BooleanDataType;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.FloatDataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

public class ApplyPhase5HighImpactSignatureQueue extends GhidraScript {

    private Function getFunctionOrThrow(String addrText) throws Exception {
        if (!addrText.startsWith("0x") && !addrText.startsWith("0X")) {
            addrText = "0x" + addrText;
        }
        Function fn = getFunctionAt(toAddr(addrText));
        if (fn == null) {
            Function cf = getFunctionContaining(toAddr(addrText));
            if (cf != null && cf.getEntryPoint().equals(toAddr(addrText))) {
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

    private void apply(Function fn, String cc, DataType ret, ParameterImpl... ps) throws Exception {
        fn.setCallingConvention(cc);
        fn.setReturnType(ret, SourceType.USER_DEFINED);
        fn.replaceParameters(
            FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS,
            true,
            SourceType.USER_DEFINED,
            ps
        );
        println("UPDATED: 0x" + fn.getEntryPoint().toString() + " " + fn.getName() + " -> " + fn.getSignature().toString());
    }

    @Override
    protected void run() throws Exception {
        DataType voidType = VoidDataType.dataType;
        DataType intType = IntegerDataType.dataType;
        DataType floatType = FloatDataType.dataType;
        DataType boolType = BooleanDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);
        int updated = 0;

        apply(getFunctionOrThrow("0x00402ad0"), "__thiscall", voidType,
            param("this", voidPtr),
            param("param_1", intType));
        updated++;

        apply(getFunctionOrThrow("0x00421a80"), "__thiscall", voidType,
            param("this", voidPtr),
            param("param_1", intType));
        updated++;

        apply(getFunctionOrThrow("0x00445070"), "__thiscall", voidPtr,
            param("this", voidPtr));
        updated++;

        apply(getFunctionOrThrow("0x00488bb0"), "__thiscall", voidType,
            param("this", voidPtr),
            param("param_1", intType));
        updated++;

        apply(getFunctionOrThrow("0x0049f940"), "__thiscall", voidType,
            param("this", voidPtr));
        updated++;

        apply(getFunctionOrThrow("0x004f4730"), "__thiscall", voidType,
            param("this", voidPtr),
            param("param_1", voidPtr));
        updated++;

        apply(getFunctionOrThrow("0x004f86d0"), "__thiscall", voidType,
            param("this", voidPtr));
        updated++;

        apply(getFunctionOrThrow("0x004f9a90"), "__thiscall", voidType,
            param("this", voidPtr),
            param("damageAmount", floatType),
            param("damageType", intType));
        updated++;

        apply(getFunctionOrThrow("0x0050b9c0"), "__thiscall", boolType,
            param("this", voidPtr),
            param("levelName", voidPtr));
        updated++;

        println("ApplyPhase5HighImpactSignatureQueue: updated=" + updated);
    }
}
