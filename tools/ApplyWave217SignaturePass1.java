//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.data.ByteDataType;
import ghidra.program.model.data.CharDataType;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.DoubleDataType;
import ghidra.program.model.data.FloatDataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.ShortDataType;
import ghidra.program.model.data.UnsignedIntegerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

public class ApplyWave217SignaturePass1 extends GhidraScript {

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

    private void applySignature(Function fn, String callingConvention, DataType retType, ParameterImpl... params)
            throws Exception {
        fn.setCallingConvention(callingConvention);
        fn.setReturnType(retType, SourceType.USER_DEFINED);
        fn.replaceParameters(
            FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS,
            true,
            SourceType.USER_DEFINED,
            params
        );
    }

    @Override
    protected void run() throws Exception {
        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);
        DataType intType = IntegerDataType.dataType;
        DataType uintType = UnsignedIntegerDataType.dataType;
        DataType floatType = FloatDataType.dataType;
        DataType doubleType = DoubleDataType.dataType;
        DataType byteType = ByteDataType.dataType;
        DataType intPtr = new PointerDataType(IntegerDataType.dataType);
        DataType floatPtr = new PointerDataType(FloatDataType.dataType);
        DataType shortPtr = new PointerDataType(ShortDataType.dataType);
        DataType charPtr = new PointerDataType(CharDataType.dataType);

        int updated = 0;

        Function f4239b0 = getFunctionOrThrow("0x004239b0");
        applySignature(
            f4239b0,
            "__thiscall",
            intType,
            param("this", voidPtr)
        );
        updated++;

        Function f441e20 = getFunctionOrThrow("0x00441e20");
        applySignature(
            f441e20,
            "__thiscall",
            voidType,
            param("this", voidPtr)
        );
        updated++;

        Function f441e30 = getFunctionOrThrow("0x00441e30");
        applySignature(
            f441e30,
            "__thiscall",
            intType,
            param("this", voidPtr)
        );
        updated++;

        Function f441e40 = getFunctionOrThrow("0x00441e40");
        applySignature(
            f441e40,
            "__thiscall",
            voidType,
            param("this", voidPtr)
        );
        updated++;

        Function f40acc0 = getFunctionOrThrow("0x0040acc0");
        applySignature(
            f40acc0,
            "__thiscall",
            intType,
            param("this", voidPtr),
            param("event_payload", voidPtr),
            param("query_context", voidPtr),
            param("reset_readers", intType),
            param("trace_mode", intType)
        );
        updated++;

        Function f44c440 = getFunctionOrThrow("0x0044c440");
        applySignature(
            f44c440,
            "__thiscall",
            voidType,
            param("this", voidPtr)
        );
        updated++;

        Function f47eb80 = getFunctionOrThrow("0x0047eb80");
        applySignature(
            f47eb80,
            "__thiscall",
            doubleType,
            param("this", voidPtr),
            param("world_pos", voidPtr)
        );
        updated++;

        Function f47eff0 = getFunctionOrThrow("0x0047eff0");
        applySignature(
            f47eff0,
            "__thiscall",
            intType,
            param("this", voidPtr),
            param("lod_shift", byteType),
            param("tile_ctx", intPtr),
            param("src_base", intType),
            param("dst_stride", intType),
            param("tile_flags", uintType),
            param("min_x", intType),
            param("min_y", intType),
            param("max_x", intType),
            param("max_y", intType)
        );
        updated++;

        Function f4c0370 = getFunctionOrThrow("0x004c0370");
        applySignature(
            f4c0370,
            "__thiscall",
            voidType,
            param("this", voidPtr),
            param("value_vec4", voidPtr),
            param("context", voidPtr)
        );
        updated++;

        Function f4c0450 = getFunctionOrThrow("0x004c0450");
        applySignature(
            f4c0450,
            "__thiscall",
            voidType,
            param("this", voidPtr),
            param("src_block", voidPtr),
            param("context", voidPtr)
        );
        updated++;

        Function f4c0510 = getFunctionOrThrow("0x004c0510");
        applySignature(
            f4c0510,
            "__thiscall",
            voidType,
            param("this", voidPtr),
            param("node", voidPtr),
            param("context", voidPtr)
        );
        updated++;

        Function f4c10c0 = getFunctionOrThrow("0x004c10c0");
        applySignature(
            f4c10c0,
            "__thiscall",
            doubleType,
            param("this", voidPtr),
            param("x_value", voidPtr),
            param("time_scale", floatType),
            param("eval_flags", intType)
        );
        updated++;

        Function f4d3b10 = getFunctionOrThrow("0x004d3b10");
        applySignature(
            f4d3b10,
            "__cdecl",
            intType,
            param("rect_x", floatType),
            param("rect_y", floatType),
            param("rect_w", floatType),
            param("rect_h", floatType),
            param("seg_p0", floatPtr),
            param("seg_p1", floatPtr)
        );
        updated++;

        Function f4daff0 = getFunctionOrThrow("0x004daff0");
        applySignature(
            f4daff0,
            "__thiscall",
            doubleType,
            param("this", voidPtr)
        );
        updated++;

        Function f4e1260 = getFunctionOrThrow("0x004e1260");
        applySignature(
            f4e1260,
            "__thiscall",
            voidType,
            param("this", voidPtr),
            param("track_id", intType),
            param("sample_value", intType),
            param("delta_step", floatType),
            param("sample_key", floatType),
            param("flags", intType)
        );
        updated++;

        Function f4f8140 = getFunctionOrThrow("0x004f8140");
        applySignature(
            f4f8140,
            "__thiscall",
            voidType,
            param("this", voidPtr),
            param("out_matrix", voidPtr),
            param("yaw_deg", intType),
            param("pitch_deg", intType),
            param("roll_deg", intType)
        );
        updated++;

        Function f552f2a7 = getFunctionOrThrow("0x0055f2a7");
        applySignature(
            f552f2a7,
            "__cdecl",
            shortPtr,
            param("haystack", shortPtr),
            param("needle", shortPtr)
        );
        updated++;

        Function f55214d0 = getFunctionOrThrow("0x005214d0");
        applySignature(
            f55214d0,
            "__thiscall",
            intType,
            param("this", voidPtr)
        );
        updated++;

        // keep function visible to static import so the type is not optimized out
        if (charPtr == null) {
            throw new IllegalStateException("char* type init failed");
        }

        println("ApplyWave217SignaturePass1: updated=" + updated);
    }
}
