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

public class ApplyWave217SignaturePass2 extends GhidraScript {

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
    }

    @Override
    protected void run() throws Exception {
        DataType voidType = VoidDataType.dataType;
        DataType intType = IntegerDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);

        int updated = 0;

        apply(getFunctionOrThrow("0x004adf80"), "__thiscall", voidType,
            param("this", voidPtr));
        updated++;

        apply(getFunctionOrThrow("0x004f27e0"), "__thiscall", voidType,
            param("this", voidPtr));
        updated++;

        apply(getFunctionOrThrow("0x004cb040"), "__cdecl", voidType,
            param("node", voidPtr));
        updated++;

        apply(getFunctionOrThrow("0x00527de0"), "__cdecl", voidType,
            param("source_ctx", voidPtr));
        updated++;

        apply(getFunctionOrThrow("0x004d05c0"), "__thiscall", intType,
            param("this", voidPtr));
        updated++;

        apply(getFunctionOrThrow("0x004aa4e0"), "__thiscall", intType,
            param("this", voidPtr));
        updated++;

        apply(getFunctionOrThrow("0x004b0cd0"), "__thiscall", voidPtr,
            param("this", voidPtr));
        updated++;

        apply(getFunctionOrThrow("0x0040c5b0"), "__thiscall", intType,
            param("this", voidPtr));
        updated++;

        apply(getFunctionOrThrow("0x0040c5e0"), "__thiscall", intType,
            param("this", voidPtr));
        updated++;

        apply(getFunctionOrThrow("0x00449560"), "__thiscall", voidPtr,
            param("this", voidPtr),
            param("x_bits", intType),
            param("y_bits", intType),
            param("z_bits", intType));
        updated++;

        apply(getFunctionOrThrow("0x00465f00"), "__cdecl", intType);
        updated++;

        apply(getFunctionOrThrow("0x004780f0"), "__thiscall", intType,
            param("this", voidPtr));
        updated++;

        apply(getFunctionOrThrow("0x00465c10"), "__cdecl", voidType);
        updated++;

        apply(getFunctionOrThrow("0x004b6cd0"), "__thiscall", voidType,
            param("this", voidPtr));
        updated++;

        apply(getFunctionOrThrow("0x004fde70"), "__thiscall", voidType,
            param("this", voidPtr));
        updated++;

        apply(getFunctionOrThrow("0x0055e3ea"), "__cdecl", voidType);
        updated++;

        println("ApplyWave217SignaturePass2: updated=" + updated);
    }
}
