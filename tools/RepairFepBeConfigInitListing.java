//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.app.cmd.disassemble.DisassembleCommand;
import ghidra.app.cmd.function.CreateFunctionCmd;
import ghidra.app.cmd.function.DeleteFunctionCmd;
import ghidra.app.plugin.core.clear.ClearCmd;
import ghidra.app.plugin.core.clear.ClearOptions;
import ghidra.app.plugin.core.clear.ClearOptions.ClearType;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.AddressSet;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.FunctionManager;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

public class RepairFepBeConfigInitListing extends GhidraScript {
    private static final String NAME = "CFEPBEConfig__Init";
    private static final String COMMENT =
        "Recovered CFEPBEConfig init boundary: starts at the SEH prologue before the beconf::init() 0-5 trace strings, initializes page/config state, and ends before CFEPBEConfig__Cleanup. This corrects the old mid-prologue 0x0044fa93 note. Static retail evidence only; exact source identity, call path, runtime frontend behavior, and rebuild parity remain unproven.";

    private Address addr(String addressText) {
        if (!addressText.startsWith("0x") && !addressText.startsWith("0X")) {
            addressText = "0x" + addressText;
        }
        Address result = toAddr(addressText);
        if (result == null) {
            throw new IllegalArgumentException("Bad address: " + addressText);
        }
        return result;
    }

    private ParameterImpl param(String name, DataType type) throws Exception {
        return new ParameterImpl(name, type, currentProgram);
    }

    private void applySignature(Function fn) throws Exception {
        DataType voidPtr = new PointerDataType(VoidDataType.dataType);
        if (!fn.getName().equals(NAME)) {
            fn.setName(NAME, SourceType.USER_DEFINED);
        }
        fn.setCallingConvention("__thiscall");
        fn.setReturnType(VoidDataType.dataType, SourceType.USER_DEFINED);
        fn.replaceParameters(
            FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS,
            true,
            SourceType.USER_DEFINED,
            new ParameterImpl[] {param("this", voidPtr)}
        );
        fn.setComment(COMMENT);
        fn.addTag("static-reaudit");
        fn.addTag("fep-beconfig-wave367");
        fn.addTag("retail-binary-evidence");
        fn.addTag("fep-beconfig");
        fn.addTag("function-boundary");
        fn.addTag("init");
        fn.addTag("boundary-corrected");
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        String mode = args != null && args.length > 0 ? args[0].trim().toLowerCase() : "dry";
        Address start = addr("0x0044fa90");
        Address end = addr("0x0044fd9f");
        FunctionManager fm = currentProgram.getFunctionManager();
        Function fn = getFunctionAt(start);
        boolean hasInstruction = getInstructionAt(start) != null;

        if (mode.equals("dry")) {
            println("Mode: dry");
            println("function=" + (fn == null ? "<none>" : fn.getName()));
            println("has_instruction=" + hasInstruction);
            println("body_contains_start=" + (fn != null && fn.getBody().contains(start)));
            println("body=" + (fn == null ? "<none>" : fn.getBody().toString()));
            println("would_remove=" + (fn != null));
            println("would_clear_range=0x0044fa90-0x0044fd9f");
            println("would_disassemble_and_create=" + NAME);
            return;
        }

        if (mode.equals("body")) {
            println("Mode: body");
            AddressSet range = new AddressSet(start, end);
            if (fn == null) {
                throw new IllegalStateException("No function present at 0x0044fa90; run decode first");
            }
            if (getInstructionAt(start) == null) {
                throw new IllegalStateException("No decoded instruction at 0x0044fa90; run decode first");
            }
            fn.setBody(range);
            applySignature(fn);
            if (!fn.getBody().contains(start)) {
                throw new IllegalStateException("Function body still does not contain 0x0044fa90");
            }
            println("OK: set body for 0x0044fa90 to 0x0044fa90-0x0044fd9f " + fn.getSignature().toString());
            return;
        }

        if (mode.equals("remove")) {
            println("Mode: remove");
            if (fn == null) {
                println("OK: no function present at 0x0044fa90");
                return;
            }
            DeleteFunctionCmd delete = new DeleteFunctionCmd(start, true);
            boolean removed = delete.applyTo(currentProgram);
            if (!removed) {
                throw new IllegalStateException("Failed to remove function at 0x0044fa90: " + delete.getStatusMsg());
            }
            println("OK: removed function metadata at 0x0044fa90");
            return;
        }

        if (mode.equals("recreate")) {
            println("Mode: recreate");
            if (getFunctionAt(start) != null) {
                throw new IllegalStateException("Function still present at 0x0044fa90; run remove first");
            }
            AddressSet range = new AddressSet(start, end);
            ClearCmd clear = new ClearCmd(range);
            boolean clearOk = clear.applyTo(currentProgram, monitor);
            if (!clearOk) {
                throw new IllegalStateException("ClearCmd failed for 0x0044fa90-0x0044fd9f");
            }
            DisassembleCommand disassemble = new DisassembleCommand(start, range, true);
            boolean disasmOk = disassemble.applyTo(currentProgram, monitor);
            CreateFunctionCmd create = new CreateFunctionCmd(NAME, start, null, SourceType.USER_DEFINED);
            boolean createOk = create.applyTo(currentProgram, monitor);
            Function recreated = create.getFunction();
            if (recreated == null && createOk) {
                recreated = getFunctionAt(start);
            }
            if (recreated == null) {
                throw new IllegalStateException("CreateFunctionCmd returned null at 0x0044fa90; disassemble=" + disasmOk);
            }
            applySignature(recreated);
            if (getInstructionAt(start) == null) {
                throw new IllegalStateException("No decoded instruction at 0x0044fa90 after recreate; disassemble=" + disasmOk);
            }
            println("OK: recreated decoded function at 0x0044fa90 " + recreated.getSignature().toString());
            return;
        }

        if (mode.equals("decode")) {
            println("Mode: decode");
            AddressSet range = new AddressSet(start, end);
            ClearOptions options = new ClearOptions(false);
            options.setShouldClear(ClearType.DATA, true);
            options.setShouldClear(ClearType.INSTRUCTIONS, true);
            ClearCmd clear = new ClearCmd(range, options);
            boolean clearOk = clear.applyTo(currentProgram, monitor);
            if (!clearOk) {
                throw new IllegalStateException("Instruction/data clear failed for 0x0044fa90-0x0044fd9f");
            }
            DisassembleCommand disassemble = new DisassembleCommand(start, range, true);
            boolean disasmOk = disassemble.applyTo(currentProgram, monitor);
            Function decodedFn = getFunctionAt(start);
            if (decodedFn == null) {
                CreateFunctionCmd create = new CreateFunctionCmd(NAME, start, null, SourceType.USER_DEFINED);
                boolean createOk = create.applyTo(currentProgram, monitor);
                decodedFn = create.getFunction();
                if (decodedFn == null && createOk) {
                    decodedFn = getFunctionAt(start);
                }
            }
            if (decodedFn == null) {
                throw new IllegalStateException("No function at 0x0044fa90 after decode; disassemble=" + disasmOk);
            }
            applySignature(decodedFn);
            if (getInstructionAt(start) == null) {
                throw new IllegalStateException("No decoded instruction at 0x0044fa90 after decode; disassemble=" + disasmOk);
            }
            println("OK: decoded listing at 0x0044fa90 " + decodedFn.getSignature().toString() + " disassemble=" + disasmOk + " clear=" + clearOk);
            return;
        }

        throw new IllegalArgumentException("Unrecognized mode: " + mode + " (use dry/body/remove/recreate/decode)");
    }
}
