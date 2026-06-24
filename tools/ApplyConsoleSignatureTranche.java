//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.BooleanDataType;
import ghidra.program.model.data.CharDataType;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

public class ApplyConsoleSignatureTranche extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final String comment;
        final String[] previousNames;
        final String[] tags;
        final ParameterImpl[] parameters;

        Spec(
                String address,
                String name,
                String callingConvention,
                DataType returnType,
                String comment,
                String[] previousNames,
                String[] tags,
                ParameterImpl[] parameters) {
            this.address = address;
            this.name = name;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.comment = comment;
            this.previousNames = previousNames;
            this.tags = tags;
            this.parameters = parameters;
        }
    }

    private static class Stats {
        int updated = 0;
        int skipped = 0;
        int renamed = 0;
        int missing = 0;
        int bad = 0;
    }

    private static boolean isDryRun(String mode) {
        if (mode == null || mode.trim().isEmpty()) {
            return true;
        }
        String normalized = mode.trim().toLowerCase();
        if (normalized.equals("dry") || normalized.equals("dry-run") || normalized.equals("true") || normalized.equals("1")) {
            return true;
        }
        if (normalized.equals("apply") || normalized.equals("no-dry") || normalized.equals("false") || normalized.equals("0")) {
            return false;
        }
        throw new IllegalArgumentException("Unrecognized mode: " + mode + " (use dry/apply)");
    }

    private Address addr(String addrText) {
        if (!addrText.startsWith("0x") && !addrText.startsWith("0X")) {
            addrText = "0x" + addrText;
        }
        Address addr = toAddr(addrText);
        if (addr == null) {
            throw new IllegalArgumentException("Bad address: " + addrText);
        }
        return addr;
    }

    private Function getFunctionOrThrow(String addrText) throws Exception {
        Address addr = addr(addrText);
        Function fn = getFunctionAt(addr);
        if (fn == null) {
            Function containing = getFunctionContaining(addr);
            if (containing != null && containing.getEntryPoint().equals(addr)) {
                fn = containing;
            }
        }
        if (fn == null) {
            throw new IllegalStateException("Function not found at " + addrText);
        }
        return fn;
    }

    private ParameterImpl param(String name, DataType dataType) throws Exception {
        return new ParameterImpl(name, dataType, currentProgram);
    }

    private boolean nameAllowed(String currentName, Spec spec) {
        if (currentName.equals(spec.name)) {
            return true;
        }
        for (String previousName : spec.previousNames) {
            if (currentName.equals(previousName)) {
                return true;
            }
        }
        return false;
    }

    private String expectedSignature(Spec spec) {
        StringBuilder sb = new StringBuilder();
        sb.append(spec.returnType.getDisplayName()).append(" ").append(spec.callingConvention).append(" ").append(spec.name).append("(");
        for (int i = 0; i < spec.parameters.length; i++) {
            if (i > 0) {
                sb.append(", ");
            }
            sb.append(spec.parameters[i].getDataType().getDisplayName()).append(" ").append(spec.parameters[i].getName());
        }
        sb.append(")");
        return sb.toString();
    }

    private void applySpec(Spec spec, boolean dryRun, Stats stats) {
        try {
            Function fn = getFunctionOrThrow(spec.address);
            if (!nameAllowed(fn.getName(), spec)) {
                throw new IllegalStateException("Unexpected function name at " + spec.address + ": " + fn.getName() + " != " + spec.name);
            }
            boolean needsRename = !fn.getName().equals(spec.name);
            if (dryRun) {
                println("DRY: " + spec.address + " " + fn.getName() + " -> " + expectedSignature(spec));
                stats.skipped++;
                return;
            }

            if (needsRename) {
                fn.setName(spec.name, SourceType.USER_DEFINED);
                stats.renamed++;
            }
            fn.setCallingConvention(spec.callingConvention);
            fn.setReturnType(spec.returnType, SourceType.USER_DEFINED);
            fn.replaceParameters(
                FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS,
                true,
                SourceType.USER_DEFINED,
                spec.parameters
            );
            fn.setComment(spec.comment);
            for (String tag : spec.tags) {
                fn.addTag(tag);
            }
            Function readBack = getFunctionOrThrow(spec.address);
            if (!readBack.getName().equals(spec.name)) {
                throw new IllegalStateException("Read-back name mismatch at " + spec.address + ": " + readBack.getName());
            }
            println("OK: " + spec.address + " " + spec.name + " -> " + readBack.getSignature().toString());
            stats.updated++;
            Thread.sleep(50);
        } catch (IllegalStateException ex) {
            if (ex.getMessage() != null && ex.getMessage().startsWith("Function not found")) {
                stats.missing++;
            } else {
                stats.bad++;
            }
            println("FAIL: " + spec.address + " " + spec.name + " " + ex.getMessage());
        } catch (Exception ex) {
            stats.bad++;
            println("FAIL: " + spec.address + " " + spec.name + " " + ex.getMessage());
        }
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");
        println("Mode: " + (dryRun ? "dry" : "apply"));

        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);
        DataType charType = CharDataType.dataType;
        DataType charPtr = new PointerDataType(charType);
        DataType intType = IntegerDataType.dataType;
        DataType boolType = BooleanDataType.dataType;

        String[] commonTags = new String[] {"static-reaudit", "console-wave326", "console-system", "signature-hardened"};
        String[] menuTags = new String[] {"static-reaudit", "console-wave326", "console-system", "signature-hardened", "console-menu"};
        String[] behaviorTags = new String[] {"static-reaudit", "console-wave326", "console-system", "signature-hardened", "console-menu", "behavior-named"};

        Spec[] specs = new Spec[] {
            new Spec("0x00429bc0", "CConsole__Init", "__fastcall", voidType,
                "Signature/comment/tag correction: initializes the retail Console object defaults, command/variable list heads, menu/list nodes, output line/history buffers, key-name table, key sink state, and startup console text. Exact source-body identity, concrete CConsole layout, runtime console behavior, and rebuild parity remain unproven.",
                new String[] {}, commonTags, new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x00429ef0", "CConsole__RegisterBuiltinCommands", "__fastcall", voidType,
                "Signature/comment/tag correction: registers built-in console commands and the cg_consolealpha variable by creating/reusing CConsoleCmd/CConsoleVar entries and assigning callback pointers. Some callback identities remain label-level static evidence; runtime command behavior, exact source-body identity, concrete layouts, and rebuild parity remain unproven.",
                new String[] {}, commonTags, new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x0042a410", "CConsole__ResetLayoutForWindowHeight", "__fastcall", voidType,
                "Signature/comment/tag correction: recomputes Console layout metrics from PLATFORM__GetWindowHeight, including visible line window bounds and the loading-screen stride field. Runtime layout behavior, exact source identity, concrete layout names, and rebuild parity remain unproven.",
                new String[] {}, commonTags, new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x0042a4f0", "CConsole__ExecuteBufferedCommandSlot", "__thiscall", voidType,
                "Signature/comment/tag correction: derives a buffered command line slot from slotIndex and bankSelector under the this+0x23bc line-buffer region, checks for non-empty text, and dispatches CConsole__ExecuteCommandLine. Runtime command dispatch behavior, exact buffer semantics, and rebuild parity remain unproven.",
                new String[] {}, commonTags, new ParameterImpl[] {param("this", voidPtr), param("slotIndex", charType), param("bankSelector", intType)}),
            new Spec("0x0042a540", "CConsoleVar__GetTypeName", "__stdcall", voidType,
                "Signature/comment/tag correction: maps the CConsoleVar type enum at +0xa0 to printable type labels including DWORD, string, bool, float, fvector, fmatrix, and an unknown fallback. Concrete enum ownership, buffer bounds, runtime UI behavior, and rebuild parity remain unproven.",
                new String[] {}, commonTags, new ParameterImpl[] {param("var", voidPtr), param("outTypeName", charPtr)}),
            new Spec("0x0042a5f0", "CConsoleVar__FormatValueToString", "__stdcall", voidType,
                "Signature/comment/tag correction: formats a CConsoleVar value using the type enum and value pointer, including boolean True/False text and vector/matrix formatting paths. Concrete value storage types, runtime formatting behavior, and rebuild parity remain unproven.",
                new String[] {}, commonTags, new ParameterImpl[] {param("var", voidPtr), param("outValueText", charPtr)}),
            new Spec("0x0042a770", "CConsole__FindCommandByName", "__thiscall", charPtr,
                "Signature/comment/tag correction: walks the command list head at this+0x2394 and performs a case-insensitive name compare to return the matching CConsoleCmd entry or null. Concrete CConsoleCmd type, runtime command behavior, and rebuild parity remain unproven.",
                new String[] {}, commonTags, new ParameterImpl[] {param("this", voidPtr), param("commandName", charPtr)}),
            new Spec("0x0042ae70", "CConsole__ShutdownAndFreeAllLists", "__fastcall", voidType,
                "Signature/comment/tag correction: full Console teardown helper that frees command and variable linked lists, clears their heads, and releases owned aux menu/list pointers. Runtime shutdown behavior, exact ownership model, and rebuild parity remain unproven.",
                new String[] {}, commonTags, new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x0042af20", "CConsole__ClearCommandAndVariableLists", "__fastcall", voidType,
                "Signature/comment/tag correction: frees and clears only the Console command and variable linked lists, leaving the auxiliary menu/list pointers untouched. Runtime lifecycle behavior, exact ownership model, and rebuild parity remain unproven.",
                new String[] {}, commonTags, new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x0042af80", "CConsole__RegisterCommand", "__thiscall", voidType,
                "Signature/comment/tag correction: registers or updates a CConsoleCmd entry by case-insensitive name, allocating a 0xac-byte command node when absent, copying name/description text, storing callback at +0xa0, flags at +0xa4, and next at +0xa8. Callback ABI, runtime command behavior, concrete layout type, and rebuild parity remain unproven.",
                new String[] {}, commonTags, new ParameterImpl[] {param("this", voidPtr), param("name", charPtr), param("description", charPtr), param("callback", voidPtr), param("flags", charType)}),
            new Spec("0x0042b040", "CConsole__RegisterVariable", "__thiscall", voidType,
                "Signature/comment/tag correction: registers or updates a CConsoleVar entry by case-insensitive name, allocating a 0xb0-byte variable node when absent, copying name/description text, storing type/value pointer fields, two flag bytes, and next at +0xac. Concrete value types, runtime cvar behavior, and rebuild parity remain unproven.",
                new String[] {}, commonTags, new ParameterImpl[] {param("this", voidPtr), param("name", charPtr), param("description", charPtr), param("varType", intType), param("valuePtr", voidPtr), param("flags1", charType), param("flags2", charType)}),
            new Spec("0x0042ba90", "CConsole__MenuUp", "__fastcall", boolType,
                "Signature/comment/tag correction: when the Console menu active flag is set, decrements the menu selection index and clamps it at zero; returns false when menu mode is inactive. Runtime menu behavior, exact field names, and rebuild parity remain unproven.",
                new String[] {}, menuTags, new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x0042bac0", "CConsole__MenuDown", "__fastcall", boolType,
                "Signature/comment/tag correction: when the Console menu active flag is set, increments the menu selection index and clamps against the current menu node child/action count. Runtime menu behavior, exact field names, and rebuild parity remain unproven.",
                new String[] {}, menuTags, new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x0042bb30", "CConsole__MenuSelect", "__fastcall", boolType,
                "Signature/comment/tag correction: when Console menu mode is active, either descends into the selected child node or dispatches the current menu node action through vtable slot 0x0c, then resets selection cursor fields. Runtime menu/action behavior, exact virtual identity, and rebuild parity remain unproven.",
                new String[] {}, menuTags, new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x0042c420", "CConsoleMenu__ctor_like_0042c420", "__fastcall", voidPtr,
                "Signature/comment/tag correction: initializes a Console menu node vtable and clears first-child, next-sibling, parent, and child-count style fields before returning this. Exact class name/source identity, concrete layout, destructor behavior, and rebuild parity remain unproven.",
                new String[] {}, menuTags, new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x0042c440", "CConsoleMenu__LinkChildAtHead", "__thiscall", voidType,
                "Behavior-name/signature/comment/tag correction: replaces the generic VFuncSlot_05_0042c440 label with a Console menu helper that links a child menu node at the parent head, stores the parent pointer, chains the previous first child, and increments the child count. Exact virtual/source name, class hierarchy, runtime menu behavior, and rebuild parity remain unproven.",
                new String[] {"VFuncSlot_05_0042c440"}, behaviorTags, new ParameterImpl[] {param("this", voidPtr), param("child", voidPtr)}),
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }
        println("SUMMARY: updated=" + stats.updated + " skipped=" + stats.skipped + " renamed=" + stats.renamed + " missing=" + stats.missing + " bad=" + stats.bad);
        if (stats.missing != 0 || stats.bad != 0) {
            throw new IllegalStateException("Console signature tranche failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
