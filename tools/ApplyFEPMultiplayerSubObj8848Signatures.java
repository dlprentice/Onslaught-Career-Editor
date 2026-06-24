//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.FloatDataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

public class ApplyFEPMultiplayerSubObj8848Signatures extends GhidraScript {

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

        Function fInit = getFunctionOrThrow("0x004599a0");
        apply(fInit, IntegerDataType.dataType,
            param("this", voidPtr)
        );
        updated++;

        Function fActive = getFunctionOrThrow("0x00459a60");
        apply(fActive, VoidDataType.dataType,
            param("this", voidPtr),
            param("from_page", IntegerDataType.dataType)
        );
        updated++;

        Function fTransition = getFunctionOrThrow("0x00459aa0");
        apply(fTransition, VoidDataType.dataType,
            param("this", voidPtr),
            param("from_page", IntegerDataType.dataType)
        );
        updated++;

        Function fProcess = getFunctionOrThrow("0x00459b00");
        apply(fProcess, VoidDataType.dataType,
            param("this", voidPtr),
            param("menu_state", IntegerDataType.dataType)
        );
        updated++;

        Function fButton = getFunctionOrThrow("0x00459c10");
        apply(fButton, VoidDataType.dataType,
            param("this", voidPtr),
            param("button", IntegerDataType.dataType)
        );
        updated++;

        Function fPre = getFunctionOrThrow("0x00459e50");
        apply(fPre, VoidDataType.dataType,
            param("this", voidPtr),
            param("transition", FloatDataType.dataType)
        );
        updated++;

        Function fRender = getFunctionOrThrow("0x00459ee0");
        apply(fRender, VoidDataType.dataType,
            param("this", voidPtr),
            param("transition", FloatDataType.dataType),
            param("dest", IntegerDataType.dataType)
        );
        updated++;

        println("ApplyFEPMultiplayerSubObj8848Signatures: updated=" + updated);
    }
}
