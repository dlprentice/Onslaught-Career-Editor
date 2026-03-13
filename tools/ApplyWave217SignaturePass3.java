//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.DoubleDataType;
import ghidra.program.model.data.FloatDataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

public class ApplyWave217SignaturePass3 extends GhidraScript {

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
        DataType floatType = FloatDataType.dataType;
        DataType doubleType = DoubleDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);

        int updated = 0;

        apply(getFunctionOrThrow("0x00441730"), "__thiscall", voidType,
            param("this", voidPtr),
            param("field04_value", intType),
            param("unused_flags", intType));
        updated++;

        apply(getFunctionOrThrow("0x004f5b70"), "__thiscall", voidType,
            param("this", voidPtr),
            param("field_index", intType),
            param("field_value", intType),
            param("unused_flags", intType));
        updated++;

        apply(getFunctionOrThrow("0x004fc3a0"), "__thiscall", voidType,
            param("this", voidPtr),
            param("cooldown_ticks", intType),
            param("unused_scale", floatType));
        updated++;

        apply(getFunctionOrThrow("0x0041ad10"), "__thiscall", voidType,
            param("this", voidPtr),
            param("lhs_vec3", voidPtr),
            param("rhs_vec3", voidPtr));
        updated++;

        apply(getFunctionOrThrow("0x0053f010"), "__thiscall", voidType,
            param("this", voidPtr),
            param("track_slot", intType),
            param("track_flag", intType),
            param("track_value", intType));
        updated++;

        apply(getFunctionOrThrow("0x00465dd0"), "__thiscall", intType,
            param("this", voidPtr),
            param("input_ctx", voidPtr),
            param("key_code", intType));
        updated++;

        apply(getFunctionOrThrow("0x004404f0"), "__thiscall", voidType,
            param("this", voidPtr),
            param("src_vec3", voidPtr),
            param("out_vec3", voidPtr));
        updated++;

        apply(getFunctionOrThrow("0x004f3c80"), "__thiscall", doubleType,
            param("this", voidPtr),
            param("sampler_id", intType),
            param("default_index", intType),
            param("mode_flags", intType));
        updated++;

        apply(getFunctionOrThrow("0x00403650"), "__thiscall", voidType,
            param("this", voidPtr),
            param("src_basis", voidPtr),
            param("dst_basis", voidPtr));
        updated++;

        apply(getFunctionOrThrow("0x00445010"), "__thiscall", doubleType,
            param("this", voidPtr),
            param("target_id", intType),
            param("fallback_id", intType));
        updated++;

        apply(getFunctionOrThrow("0x004aa8a0"), "__thiscall", voidPtr,
            param("this", voidPtr),
            param("child_name", voidPtr),
            param("unused_ctx", voidPtr));
        updated++;

        apply(getFunctionOrThrow("0x004cd7a0"), "__thiscall", voidPtr,
            param("this", voidPtr),
            param("node_name", voidPtr),
            param("unused_ctx", voidPtr));
        updated++;

        apply(getFunctionOrThrow("0x004cdba0"), "__thiscall", voidType,
            param("this", voidPtr),
            param("node", voidPtr),
            param("unused_ctx", intType));
        updated++;

        apply(getFunctionOrThrow("0x00442890"), "__thiscall", doubleType,
            param("this", voidPtr));
        updated++;

        apply(getFunctionOrThrow("0x00449ef0"), "__thiscall", voidType,
            param("this", voidPtr));
        updated++;

        apply(getFunctionOrThrow("0x0044d560"), "__thiscall", voidType,
            param("this", voidPtr));
        updated++;

        apply(getFunctionOrThrow("0x0046baf0"), "__thiscall", voidType,
            param("this", voidPtr));
        updated++;

        apply(getFunctionOrThrow("0x004a25c0"), "__thiscall", voidType,
            param("this", voidPtr));
        updated++;

        apply(getFunctionOrThrow("0x004d6e00"), "__thiscall", intType,
            param("this", voidPtr),
            param("candidate_unit", voidPtr),
            param("unused_ctx", intType));
        updated++;

        apply(getFunctionOrThrow("0x004f0ba0"), "__thiscall", voidType,
            param("this", voidPtr),
            param("out_anchor", voidPtr),
            param("unused_ctx", voidPtr));
        updated++;

        println("ApplyWave217SignaturePass3: updated=" + updated);
    }
}
