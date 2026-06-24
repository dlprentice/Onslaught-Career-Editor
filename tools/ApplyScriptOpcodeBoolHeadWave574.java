//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.BooleanDataType;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.FunctionTag;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyScriptOpcodeBoolHeadWave574 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final String comment;
        final String[] allowedExistingNames;
        final String[] tags;
        final ParameterImpl[] parameters;

        Spec(
                String address,
                String name,
                String callingConvention,
                DataType returnType,
                String comment,
                String[] allowedExistingNames,
                String[] tags,
                ParameterImpl[] parameters) {
            this.address = address;
            this.name = name;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.comment = comment;
            this.allowedExistingNames = allowedExistingNames;
            this.tags = tags;
            this.parameters = parameters;
        }
    }

    private static class Stats {
        int updated = 0;
        int skipped = 0;
        int renamed = 0;
        int wouldRename = 0;
        int missing = 0;
        int bad = 0;
    }

    private boolean isDryRun(String mode) {
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

    private Address addr(String addressText) {
        if (!addressText.startsWith("0x") && !addressText.startsWith("0X")) {
            addressText = "0x" + addressText;
        }
        Address address = toAddr(addressText);
        if (address == null) {
            throw new IllegalArgumentException("Bad address: " + addressText);
        }
        return address;
    }

    private Function functionAtEntry(Address address) {
        Function fn = getFunctionAt(address);
        if (fn == null) {
            Function containing = getFunctionContaining(address);
            if (containing != null && containing.getEntryPoint().equals(address)) {
                fn = containing;
            }
        }
        return fn;
    }

    private Function getFunctionOrReport(Spec spec, Stats stats) {
        Function fn = functionAtEntry(addr(spec.address));
        if (fn == null) {
            stats.missing++;
            println("FAIL: " + spec.address + " " + spec.name + " Function not found");
        }
        return fn;
    }

    private ParameterImpl param(String name, DataType dataType) throws Exception {
        return new ParameterImpl(name, dataType, currentProgram);
    }

    private boolean allowedName(Spec spec, String actual) {
        if (actual.equals(spec.name)) {
            return true;
        }
        for (String allowed : spec.allowedExistingNames) {
            if (actual.equals(allowed)) {
                return true;
            }
        }
        return false;
    }

    private String expectedSignature(Spec spec) {
        StringBuilder sb = new StringBuilder();
        sb.append(spec.returnType.getDisplayName())
            .append(" ")
            .append(spec.callingConvention)
            .append(" ")
            .append(spec.name)
            .append("(");
        if (spec.parameters.length == 0) {
            sb.append("void");
        }
        for (int i = 0; i < spec.parameters.length; i++) {
            if (i > 0) {
                sb.append(", ");
            }
            sb.append(spec.parameters[i].getDataType().getDisplayName())
                .append(" ")
                .append(spec.parameters[i].getName());
        }
        sb.append(")");
        return sb.toString();
    }

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "script-opcode-bool-head-wave574",
            "retail-binary-evidence"
        };
        String[] result = new String[common.length + extras.length];
        System.arraycopy(common, 0, result, 0, common.length);
        System.arraycopy(extras, 0, result, common.length, extras.length);
        return result;
    }

    private Set<String> tagNames(Function fn) {
        Set<String> names = new HashSet<>();
        for (FunctionTag tag : fn.getTags()) {
            names.add(tag.getName());
        }
        return names;
    }

    private void applySpec(Spec spec, boolean dryRun, Stats stats) {
        try {
            Function fn = getFunctionOrReport(spec, stats);
            if (fn == null) {
                stats.skipped++;
                return;
            }

            String currentName = fn.getName();
            if (!allowedName(spec, currentName)) {
                throw new IllegalStateException("Unexpected function name at " + spec.address + ": " + currentName);
            }

            boolean needsRename = !currentName.equals(spec.name);
            if (dryRun) {
                if (needsRename) {
                    stats.wouldRename++;
                }
                println("DRY: " + spec.address + " " + currentName + " -> " + expectedSignature(spec));
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

            Function readBack = functionAtEntry(addr(spec.address));
            if (readBack == null) {
                throw new IllegalStateException("Read-back missing at " + spec.address);
            }
            if (!readBack.getName().equals(spec.name)) {
                throw new IllegalStateException("Read-back name mismatch at " + spec.address + ": " + readBack.getName());
            }
            if (!spec.comment.equals(readBack.getComment())) {
                throw new IllegalStateException("Read-back comment mismatch at " + spec.address);
            }
            Set<String> readBackTags = tagNames(readBack);
            for (String tag : spec.tags) {
                if (!readBackTags.contains(tag)) {
                    throw new IllegalStateException("Read-back missing tag " + tag + " at " + spec.address);
                }
            }

            println("OK: " + spec.address + " " + readBack.getSignature());
            stats.updated++;
            Thread.sleep(50);
        } catch (Exception ex) {
            stats.bad++;
            println("FAIL: " + spec.address + " " + spec.name + " " + ex.getClass().getSimpleName() + ": " + ex.getMessage());
        }
    }

    private ParameterImpl[] instructionVfuncParams(DataType voidPtr) throws Exception {
        return new ParameterImpl[] {
            param("this", voidPtr),
            param("script_state", voidPtr),
            param("data_stack", voidPtr),
            param("object_code", voidPtr)
        };
    }

    private String[] instructionTags(String... extras) {
        String[] base = new String[] {
            "mission-script",
            "asm-instruction",
            "bytecode-vm",
            "opcode-executor",
            "signature-corrected",
            "comment-hardened"
        };
        String[] result = new String[base.length + extras.length];
        System.arraycopy(base, 0, result, 0, base.length);
        System.arraycopy(extras, 0, result, base.length, extras.length);
        return tags(result);
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");
        println("Mode: " + (dryRun ? "dry" : "apply"));

        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);
        DataType boolType = BooleanDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x0052e0f0",
                "CAsmInstruction__ExecutePop",
                "__thiscall",
                voidType,
                "Wave574 signature/comment hardening: opcode vtable executor at dispatch-table slot 0x005e4bd0 for POP. The method is called in the instruction-vfunc shape with ECX unused and RET 0x0c stack arguments; it decrements script_state+0x224 when positive, pops a datatype object from data_stack, reads its scalar value through datatype vtable slot +0x30 into script_state+0x214, releases the popped object, then pushes a one-valued CIntDataType status object or null on allocation failure. Static retail evidence only; exact VM state layout, opcode enum, source identity, runtime script behavior, and rebuild parity remain unproven.",
                new String[] {"CAsmInstruction__ExecutePop"},
                instructionTags("pop", "stack", "datatype-dispatch"),
                instructionVfuncParams(voidPtr)
            ),
            new Spec(
                "0x0052e2c0",
                "CInstructionOP_PUSH__VFunc_00_0052e2c0",
                "__thiscall",
                voidType,
                "Wave574 signature/comment hardening: OP_PUSH vtable executor at dispatch-table slot 0x005e4cf0. It uses this+0x04 as an instruction attribute index, asks object_code for that instruction, resolves the attribute value through CAsmInstruction__GetAttributeValue, and pushes the returned datatype object onto data_stack. Static retail evidence only; exact instruction layout, object_code layout, source identity, runtime script behavior, and rebuild parity remain unproven.",
                new String[] {"CInstructionOP_PUSH__VFunc_00_0052e2c0"},
                instructionTags("push", "stack", "instruction-vfunc"),
                instructionVfuncParams(voidPtr)
            ),
            new Spec(
                "0x0052e380",
                "CAsmInstruction__ExecuteCompareEqual",
                "__thiscall",
                voidType,
                "Wave574 signature/comment hardening: equality comparison opcode executor at dispatch-table slot 0x005e4c40. It pops two datatype objects from data_stack, dispatches the top operand's vtable slot +0x18 with the other operand, allocates an 8-byte boolean result object carrying 0 or 1, pushes that result, and releases both operands. Static retail evidence only; exact operand order, boolean result class label, source identity, runtime script behavior, and rebuild parity remain unproven.",
                new String[] {"CAsmInstruction__ExecuteCompareEqual"},
                instructionTags("comparison", "boolean-result", "datatype-dispatch"),
                instructionVfuncParams(voidPtr)
            ),
            new Spec(
                "0x0052e420",
                "CBoolDataType__Equals",
                "__thiscall",
                boolType,
                "Wave574 semantic rename plus signature/comment hardening: CBoolDataType equality vtable slot at data pointer 0x005e4d68. ECX is this, RET 0x4 confirms one rhs stack argument, and the body reads rhs through datatype vtable slot +0x3c before comparing it with the byte stored at this+0x04. Static retail evidence only; exact bool ABI, exact datatype layout, source identity, runtime script behavior, and rebuild parity remain unproven.",
                new String[] {"CBoolDataType__VFunc_06_0052e420"},
                tags("mission-script", "datatype", "bool-datatype", "vtable-slot", "comparison", "semantic-rename", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("rhs", voidPtr)
                }
            ),
            new Spec(
                "0x0052e440",
                "CBoolDataType__NotEquals",
                "__thiscall",
                boolType,
                "Wave574 semantic rename plus signature/comment hardening: CBoolDataType inequality vtable slot at data pointer 0x005e4d6c. ECX is this, RET 0x4 confirms one rhs stack argument, and the body reads rhs through datatype vtable slot +0x3c before comparing it with the byte stored at this+0x04. Static retail evidence only; exact bool ABI, exact datatype layout, source identity, runtime script behavior, and rebuild parity remain unproven.",
                new String[] {"CBoolDataType__VFunc_07_0052e440"},
                tags("mission-script", "datatype", "bool-datatype", "vtable-slot", "comparison", "semantic-rename", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("rhs", voidPtr)
                }
            ),
            new Spec(
                "0x0052e460",
                "CBoolDataType__Assign",
                "__thiscall",
                voidType,
                "Wave574 semantic rename plus signature/comment hardening: CBoolDataType assignment vtable slot at data pointer 0x005e4d64. ECX is this, RET 0x4 confirms one rhs stack argument, and the body reads rhs through datatype vtable slot +0x3c before storing the returned byte at this+0x04. Static retail evidence only; exact datatype layout, assignment ownership, source identity, runtime script behavior, and rebuild parity remain unproven.",
                new String[] {"CBoolDataType__VFunc_05_0052e460"},
                tags("mission-script", "datatype", "bool-datatype", "vtable-slot", "semantic-rename", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("rhs", voidPtr)
                }
            ),
            new Spec(
                "0x0052e4d0",
                "CAsmInstruction__ExecuteOr",
                "__thiscall",
                voidType,
                "Wave574 signature/comment hardening: OR opcode executor at dispatch-table slot 0x005e4cd0. It pops two datatype objects from data_stack, reads boolean values through datatype vtable slot +0x3c, allocates an 8-byte boolean result object carrying logical OR, pushes the result, and releases both operands. Static retail evidence only; exact operand order, boolean result class label, source identity, runtime script behavior, and rebuild parity remain unproven.",
                new String[] {"CAsmInstruction__ExecuteOr"},
                instructionTags("boolean-op", "or", "datatype-dispatch"),
                instructionVfuncParams(voidPtr)
            ),
            new Spec(
                "0x0052e580",
                "CAsmInstruction__ExecuteAnd",
                "__thiscall",
                voidType,
                "Wave574 signature/comment hardening: AND opcode executor at dispatch-table slot 0x005e4cc0. It pops two datatype objects from data_stack, reads boolean values through datatype vtable slot +0x3c, allocates an 8-byte boolean result object carrying logical AND, pushes the result, and releases both operands. Static retail evidence only; exact operand order, boolean result class label, source identity, runtime script behavior, and rebuild parity remain unproven.",
                new String[] {"CAsmInstruction__ExecuteAnd"},
                instructionTags("boolean-op", "and", "datatype-dispatch"),
                instructionVfuncParams(voidPtr)
            ),
            new Spec(
                "0x0052e630",
                "CAsmInstruction__ExecuteGreaterThan",
                "__thiscall",
                voidType,
                "Wave574 signature/comment hardening: greater-than comparison opcode executor at dispatch-table slot 0x005e4cb0. It pops two datatype operands from data_stack, dispatches the left operand through datatype vtable slot +0x24 with the right operand, allocates an 8-byte boolean result object, pushes the result, and releases both operands. Static retail evidence only; exact operand order, boolean result class label, source identity, runtime script behavior, and rebuild parity remain unproven.",
                new String[] {"CAsmInstruction__ExecuteGreaterThan"},
                instructionTags("comparison", "greater-than", "datatype-dispatch"),
                instructionVfuncParams(voidPtr)
            ),
            new Spec(
                "0x0052e6d0",
                "CAsmInstruction__ExecuteLessThan",
                "__thiscall",
                voidType,
                "Wave574 signature/comment hardening: less-than comparison opcode executor at dispatch-table slot 0x005e4ca0. It pops two datatype operands from data_stack, dispatches the left operand through datatype vtable slot +0x20 with the right operand, allocates an 8-byte boolean result object, pushes the result, and releases both operands. Static retail evidence only; exact operand order, boolean result class label, source identity, runtime script behavior, and rebuild parity remain unproven.",
                new String[] {"CAsmInstruction__ExecuteLessThan"},
                instructionTags("comparison", "less-than", "datatype-dispatch"),
                instructionVfuncParams(voidPtr)
            ),
            new Spec(
                "0x0052e770",
                "CAsmInstruction__ExecuteGreaterOrEqual",
                "__thiscall",
                voidType,
                "Wave574 signature/comment hardening: greater-or-equal comparison opcode executor at dispatch-table slot 0x005e4c90. It pops two datatype operands from data_stack, dispatches the left operand through datatype vtable slot +0x2c with the right operand, allocates an 8-byte boolean result object, pushes the result, and releases both operands. Static retail evidence only; exact operand order, boolean result class label, source identity, runtime script behavior, and rebuild parity remain unproven.",
                new String[] {"CAsmInstruction__ExecuteGreaterOrEqual"},
                instructionTags("comparison", "greater-or-equal", "datatype-dispatch"),
                instructionVfuncParams(voidPtr)
            ),
            new Spec(
                "0x0052e810",
                "CAsmInstruction__ExecuteLessOrEqual",
                "__thiscall",
                voidType,
                "Wave574 signature/comment hardening: less-or-equal comparison opcode executor at dispatch-table slot 0x005e4c80. It pops two datatype operands from data_stack, dispatches the left operand through datatype vtable slot +0x28 with the right operand, allocates an 8-byte boolean result object, pushes the result, and releases both operands. Static retail evidence only; exact operand order, boolean result class label, source identity, runtime script behavior, and rebuild parity remain unproven.",
                new String[] {"CAsmInstruction__ExecuteLessOrEqual"},
                instructionTags("comparison", "less-or-equal", "datatype-dispatch"),
                instructionVfuncParams(voidPtr)
            ),
            new Spec(
                "0x0052e8b0",
                "CAsmInstruction__ExecuteCompareNotEqual",
                "__thiscall",
                voidType,
                "Wave574 signature/comment hardening: inequality comparison opcode executor at dispatch-table slot 0x005e4c30. It pops two datatype objects from data_stack, dispatches the top operand's vtable slot +0x1c with the other operand, allocates an 8-byte boolean result object carrying 0 or 1, pushes that result, and releases both operands. Static retail evidence only; exact operand order, boolean result class label, source identity, runtime script behavior, and rebuild parity remain unproven.",
                new String[] {"CAsmInstruction__ExecuteCompareNotEqual"},
                instructionTags("comparison", "boolean-result", "datatype-dispatch"),
                instructionVfuncParams(voidPtr)
            ),
            new Spec(
                "0x0052e950",
                "CInstructionOP_JMPFALSE__VFunc_00_0052e950",
                "__thiscall",
                voidType,
                "Wave574 signature/comment hardening: JMPFALSE vtable executor at dispatch-table slot 0x005e4c10. It pops a datatype object from data_stack, reads its boolean value through datatype vtable slot +0x3c, writes this+0x04 into script_state+0x214 when the value is false, then releases the popped object. Static retail evidence only; exact branch-target encoding, VM state layout, source identity, runtime script behavior, and rebuild parity remain unproven.",
                new String[] {"CInstructionOP_JMPFALSE__VFunc_00_0052e950"},
                instructionTags("control-flow", "jump-false", "instruction-vfunc", "datatype-dispatch"),
                instructionVfuncParams(voidPtr)
            ),
            new Spec(
                "0x0052ea40",
                "CAsmInstruction__ExecuteCall",
                "__thiscall",
                voidType,
                "Wave574 signature/comment hardening: CALL opcode executor at dispatch-table slot 0x005e4bc0. It uses this+0x05 as the argument count and this+0x04 as function-table/type metadata, pops arguments into the global call scratch array around 0x0089c300, checks function availability from the active script/event state, dispatches through the function descriptor table at 0x0064ce50, handles missing or unexpected return values, pushes the resulting datatype object, and releases temporary argument objects. Static retail evidence only; exact descriptor layout, return-type encoding, source identity, runtime script behavior, and rebuild parity remain unproven.",
                new String[] {"CAsmInstruction__ExecuteCall"},
                instructionTags("call", "function-call-dispatch", "global-scratch", "datatype-dispatch"),
                instructionVfuncParams(voidPtr)
            )
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }

        println("SUMMARY updated=" + stats.updated
            + " skipped=" + stats.skipped
            + " renamed=" + stats.renamed
            + " would_rename=" + stats.wouldRename
            + " missing=" + stats.missing
            + " bad=" + stats.bad);
        if (stats.bad > 0 || stats.missing > 0) {
            throw new IllegalStateException("Wave574 script opcode/bool head tranche failed");
        }
    }
}
