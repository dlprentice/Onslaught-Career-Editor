//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.symbol.SourceType;

public class ApplyOptionsEntryTableInitSignatures extends GhidraScript {

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

    private void applyVoidNoArgs(Function fn) throws Exception {
        fn.setCallingConvention("__cdecl");
        fn.setReturnType(VoidDataType.dataType, SourceType.USER_DEFINED);
        fn.replaceParameters(
            FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS,
            true,
            SourceType.USER_DEFINED
        );
    }

    @Override
    protected void run() throws Exception {
        int updated = 0;

        Function fDual = getFunctionOrThrow("0x00453460");
        applyVoidNoArgs(fDual);
        updated++;

        Function fSingle = getFunctionOrThrow("0x00514210");
        applyVoidNoArgs(fSingle);
        updated++;

        println("ApplyOptionsEntryTableInitSignatures: updated=" + updated);
    }
}

