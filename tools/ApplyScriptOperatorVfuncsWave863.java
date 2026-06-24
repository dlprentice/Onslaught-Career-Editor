//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
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

public class ApplyScriptOperatorVfuncsWave863 extends GhidraScript {
    private static class Spec {
        final String address;
        final String expectedName;
        final String expectedPrototype;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] parameters;
        final String comment;
        final String[] tags;

        Spec(String address, String expectedName, String expectedPrototype, String callingConvention,
                DataType returnType, ParameterImpl[] parameters, String comment, String[] tags) {
            this.address = address;
            this.expectedName = expectedName;
            this.expectedPrototype = expectedPrototype;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.parameters = parameters;
            this.comment = comment;
            this.tags = tags;
        }
    }

    private static class Stats {
        int updated = 0;
        int skipped = 0;
        int renamed = 0;
        int wouldRename = 0;
        int signatureUpdated = 0;
        int commentOnlyUpdated = 0;
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
        Address result = toAddr(addressText);
        if (result == null) {
            throw new IllegalArgumentException("Bad address: " + addressText);
        }
        return result;
    }

    private Function functionAtEntry(String addressText) {
        Address entry = addr(addressText);
        Function fn = getFunctionAt(entry);
        if (fn != null) {
            return fn;
        }
        Function containing = getFunctionContaining(entry);
        if (containing != null && containing.getEntryPoint().equals(entry)) {
            return containing;
        }
        return null;
    }

    private ParameterImpl param(String name, DataType dataType) throws Exception {
        return new ParameterImpl(name, dataType, currentProgram);
    }

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "script-operator-vfuncs-wave863",
            "wave863-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "signature-hardened",
            "important-connective-infrastructure",
            "mission-script",
            "bytecode-vm",
            "opcode-executor"
        };
        String[] result = new String[common.length + extras.length];
        System.arraycopy(common, 0, result, 0, common.length);
        System.arraycopy(extras, 0, result, common.length, extras.length);
        return result;
    }

    private Spec signature(String address, String name, String prototype, String comment, String... extraTags) throws Exception {
        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(VoidDataType.dataType);
        return new Spec(
            address,
            name,
            prototype,
            "__thiscall",
            voidType,
            new ParameterImpl[] {
                param("this", voidPtr),
                param("script_state", voidPtr),
                param("data_stack", voidPtr),
                param("object_code", voidPtr)
            },
            comment,
            tags(extraTags)
        );
    }

    private Spec[] specs() throws Exception {
        return new Spec[] {
            signature(
                "0x0052e180",
                "CInstructionOP_PLUS__VFunc_00_0052e180",
                "void CInstructionOP_PLUS__VFunc_00_0052e180(void * this, void * script_state, void * data_stack, void * object_code)",
                "Wave863 static read-back/signature hardening: PLUS opcode executor at DATA dispatch-table/vtable ref 0x005e4d30. Body uses the shared MissionScript bytecode data stack: pops two datatype operands from data_stack, dispatches the second popped operand's datatype vtable slot +0x04 with the first popped operand, releases both operands through vtable slot +0 with flag 1 when non-null, and pushes the produced datatype result back to data_stack. Static retail Ghidra metadata/decompile/xref evidence only; exact operand order naming, exact VM/data-stack/datatype layouts, runtime MissionScript behavior, source identity, BEA patching, and rebuild parity remain unproven.",
                "plus",
                "datatype-vtable"
            ),
            signature(
                "0x0052e1d0",
                "CInstructionOP_MINUS__VFunc_00_0052e1d0",
                "void CInstructionOP_MINUS__VFunc_00_0052e1d0(void * this, void * script_state, void * data_stack, void * object_code)",
                "Wave863 static read-back/signature hardening: MINUS opcode executor at DATA dispatch-table/vtable ref 0x005e4d20. Body uses the shared MissionScript bytecode data stack: pops two datatype operands from data_stack, dispatches the second popped operand's datatype vtable slot +0x08 with the first popped operand, releases both operands through vtable slot +0 with flag 1 when non-null, and pushes the produced datatype result back to data_stack. Static retail Ghidra metadata/decompile/xref evidence only; exact operand order naming, exact VM/data-stack/datatype layouts, runtime MissionScript behavior, source identity, BEA patching, and rebuild parity remain unproven.",
                "minus",
                "datatype-vtable"
            ),
            signature(
                "0x0052e220",
                "CInstructionOP_MULTIPLY__VFunc_00_0052e220",
                "void CInstructionOP_MULTIPLY__VFunc_00_0052e220(void * this, void * script_state, void * data_stack, void * object_code)",
                "Wave863 static read-back/signature hardening: MULTIPLY opcode executor at DATA dispatch-table/vtable ref 0x005e4d10. Body uses the shared MissionScript bytecode data stack: pops two datatype operands from data_stack, dispatches the second popped operand's datatype vtable slot +0x0c with the first popped operand, releases both operands through vtable slot +0 with flag 1 when non-null, and pushes the produced datatype result back to data_stack. Static retail Ghidra metadata/decompile/xref evidence only; exact operand order naming, exact VM/data-stack/datatype layouts, runtime MissionScript behavior, source identity, BEA patching, and rebuild parity remain unproven.",
                "multiply",
                "datatype-vtable"
            ),
            signature(
                "0x0052e270",
                "CInstructionOP_DIVIDE__VFunc_00_0052e270",
                "void CInstructionOP_DIVIDE__VFunc_00_0052e270(void * this, void * script_state, void * data_stack, void * object_code)",
                "Wave863 static read-back/signature hardening: DIVIDE opcode executor at DATA dispatch-table/vtable ref 0x005e4d00. Body uses the shared MissionScript bytecode data stack: pops two datatype operands from data_stack, dispatches the second popped operand's datatype vtable slot +0x10 with the first popped operand, releases both operands through vtable slot +0 with flag 1 when non-null, and pushes the produced datatype result back to data_stack. Static retail Ghidra metadata/decompile/xref evidence only; exact operand order naming, exact VM/data-stack/datatype layouts, runtime MissionScript behavior, source identity, BEA patching, and rebuild parity remain unproven.",
                "divide",
                "datatype-vtable"
            ),
            signature(
                "0x0052e330",
                "CInstructionOP_CMP__VFunc_00_0052e330",
                "void CInstructionOP_CMP__VFunc_00_0052e330(void * this, void * script_state, void * data_stack, void * object_code)",
                "Wave863 static read-back/signature hardening: CMP opcode executor at DATA dispatch-table/vtable ref 0x005e4c50. Body reads the top two datatype operands from data_stack through CScriptObjectCode__GetTop(data_stack,0/1), dispatches datatype vtable slot +0x18 for equality-style comparison, then sets or clears bit 0 of script_state+0x218. Unlike the arithmetic operator executors it observes stack values without popping them. Static retail Ghidra metadata/decompile/xref evidence only; exact comparison-flag semantics, exact VM/data-stack/datatype layouts, runtime MissionScript behavior, source identity, BEA patching, and rebuild parity remain unproven.",
                "compare",
                "script-state-flag"
            )
        };
    }

    private Set<String> currentTags(Function fn) {
        Set<String> result = new HashSet<>();
        for (FunctionTag tag : fn.getTags()) {
            result.add(tag.getName());
        }
        return result;
    }

    private boolean hasAllTags(Function fn, String[] expected) {
        Set<String> actual = currentTags(fn);
        for (String tag : expected) {
            if (!actual.contains(tag)) {
                return false;
            }
        }
        return true;
    }

    private boolean applyTags(Function fn, String[] expected, boolean dryRun) {
        boolean changed = false;
        Set<String> actual = currentTags(fn);
        for (String tag : expected) {
            if (!actual.contains(tag)) {
                changed = true;
                if (!dryRun) {
                    fn.addTag(tag);
                }
            }
        }
        return changed;
    }

    private boolean conventionOk(Function fn, String expectedConvention) throws Exception {
        if (expectedConvention == null) {
            return true;
        }
        return expectedConvention.equals(fn.getCallingConventionName());
    }

    private void applySpec(Spec spec, boolean dryRun, Stats stats) throws Exception {
        Function fn = functionAtEntry(spec.address);
        if (fn == null) {
            println("MISSING: " + spec.address + " " + spec.expectedName);
            stats.missing++;
            stats.bad++;
            return;
        }

        boolean nameOk = fn.getName().equals(spec.expectedName);
        boolean prototypeOk = fn.getSignature().getPrototypeString().equals(spec.expectedPrototype);
        boolean conventionOk = conventionOk(fn, spec.callingConvention);
        boolean signatureOk = prototypeOk && conventionOk;
        boolean commentOk = spec.comment.equals(fn.getComment());
        boolean tagsOk = hasAllTags(fn, spec.tags);

        if (!nameOk && !dryRun) {
            fn.setName(spec.expectedName, SourceType.USER_DEFINED);
        }
        if (!nameOk) {
            stats.wouldRename++;
            if (!dryRun) {
                stats.renamed++;
            }
        }

        if (!signatureOk) {
            if (!dryRun) {
                fn.setCallingConvention(spec.callingConvention);
                fn.setReturnType(spec.returnType, SourceType.USER_DEFINED);
                fn.replaceParameters(
                    FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS,
                    true,
                    SourceType.USER_DEFINED,
                    spec.parameters
                );
            }
            stats.signatureUpdated++;
        }

        if (!commentOk && !dryRun) {
            fn.setComment(spec.comment);
        }
        if (!tagsOk) {
            applyTags(fn, spec.tags, dryRun);
        }

        if (commentOk && tagsOk && signatureOk && nameOk) {
            stats.skipped++;
            println("SKIP_OK: " + spec.address + " " + spec.expectedName);
        } else {
            stats.updated++;
            println((dryRun ? "DRY_UPDATE: " : "APPLY_UPDATE: ") + spec.address + " " + spec.expectedName);
        }

        if (!dryRun) {
            Function readback = functionAtEntry(spec.address);
            String actualSignature = readback.getSignature().getPrototypeString();
            boolean readbackOk = readback.getName().equals(spec.expectedName)
                && actualSignature.equals(spec.expectedPrototype)
                && conventionOk(readback, spec.callingConvention)
                && spec.comment.equals(readback.getComment())
                && hasAllTags(readback, spec.tags);
            if (readbackOk) {
                println("READBACK_OK: " + spec.address + " " + actualSignature + " convention=" + readback.getCallingConventionName());
            } else {
                println("READBACK_BAD: " + spec.address + " name=" + readback.getName() + " signature=" + actualSignature + " convention=" + readback.getCallingConventionName());
                stats.bad++;
            }
        }
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");
        Stats stats = new Stats();
        for (Spec spec : specs()) {
            applySpec(spec, dryRun, stats);
        }
        println(
            "SUMMARY: updated=" + stats.updated +
            " skipped=" + stats.skipped +
            " renamed=" + stats.renamed +
            " would_rename=" + stats.wouldRename +
            " signature_updated=" + stats.signatureUpdated +
            " comment_only_updated=" + stats.commentOnlyUpdated +
            " missing=" + stats.missing +
            " bad=" + stats.bad
        );
    }
}
