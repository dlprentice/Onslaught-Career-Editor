//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.DoubleDataType;
import ghidra.program.model.data.FloatDataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.UnsignedIntegerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

public class ApplyWave217SignaturePass4 extends GhidraScript {

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
        DataType uintType = UnsignedIntegerDataType.dataType;
        DataType floatType = FloatDataType.dataType;
        DataType doubleType = DoubleDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);

        int updated = 0;

        apply(getFunctionOrThrow("0x005234d0"), "__cdecl", voidType,
            param("global_input_state", intType));
        updated++;

        apply(getFunctionOrThrow("0x004048f0"), "__cdecl", intType,
            param("profile_index", intType));
        updated++;

        apply(getFunctionOrThrow("0x00409e60"), "__stdcall", doubleType,
            param("input_value", floatType));
        updated++;

        apply(getFunctionOrThrow("0x004aa6b0"), "__cdecl", voidPtr,
            param("segment_id", intType));
        updated++;

        apply(getFunctionOrThrow("0x004f2790"), "__cdecl", voidType,
            param("surf_node", voidPtr));
        updated++;

        apply(getFunctionOrThrow("0x0050f680"), "__cdecl", intType,
            param("spawn_type", intType));
        updated++;

        apply(getFunctionOrThrow("0x0055f44b"), "__cdecl", uintType,
            param("search_key", intType),
            param("base_offset", uintType),
            param("item_count", uintType),
            param("item_stride", intType),
            param("predicate", voidPtr));
        updated++;

        apply(getFunctionOrThrow("0x0040d320"), "__thiscall", voidType,
            param("this", voidPtr),
            param("out_basis", voidPtr),
            param("lhs_basis", voidPtr),
            param("rhs_basis", voidPtr));
        updated++;

        apply(getFunctionOrThrow("0x00440ad0"), "__stdcall", voidType,
            param("out_indices", voidPtr),
            param("grid_width", intType),
            param("grid_height", intType),
            param("flip_winding", intType));
        updated++;

        apply(getFunctionOrThrow("0x00441b10"), "__cdecl", voidType,
            param("selection_vec4", voidPtr),
            param("selection_mode", intType));
        updated++;

        apply(getFunctionOrThrow("0x004aa500"), "__thiscall", voidType,
            param("this", voidPtr),
            param("material_index", intType),
            param("out_name", voidPtr),
            param("out_material_id", voidPtr),
            param("unused_ctx", voidPtr));
        updated++;

        println("ApplyWave217SignaturePass4: updated=" + updated);
    }
}
