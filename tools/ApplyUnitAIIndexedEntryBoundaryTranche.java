//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.BooleanDataType;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

public class ApplyUnitAIIndexedEntryBoundaryTranche extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final String comment;
        final String[] tags;
        final ParameterImpl[] parameters;

        Spec(
                String address,
                String name,
                String callingConvention,
                DataType returnType,
                String comment,
                String[] tags,
                ParameterImpl[] parameters) {
            this.address = address;
            this.name = name;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.comment = comment;
            this.tags = tags;
            this.parameters = parameters;
        }
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

    private Function existingFunction(Address address) {
        Function fn = getFunctionAt(address);
        if (fn == null) {
            Function containing = getFunctionContaining(address);
            if (containing != null && containing.getEntryPoint().equals(address)) {
                fn = containing;
            }
        }
        return fn;
    }

    private Function getOrCreate(Spec spec, boolean dryRun) throws Exception {
        Address address = addr(spec.address);
        Function fn = existingFunction(address);
        if (fn != null) {
            if (!fn.getName().equals(spec.name)) {
                throw new IllegalStateException("Unexpected existing function name at " + spec.address + ": " + fn.getName() + " != " + spec.name);
            }
            return fn;
        }
        if (dryRun) {
            return null;
        }

        disassemble(address);
        fn = createFunction(address, spec.name);
        if (fn == null) {
            fn = getFunctionAt(address);
        }
        if (fn == null) {
            throw new IllegalStateException("Function create failed at " + spec.address);
        }
        if (!fn.getName().equals(spec.name)) {
            fn.setName(spec.name, SourceType.USER_DEFINED);
        }
        return fn;
    }

    private ParameterImpl param(String name, DataType type) throws Exception {
        return new ParameterImpl(name, type, currentProgram);
    }

    private String signatureText(Spec spec) {
        StringBuilder sb = new StringBuilder();
        sb.append(spec.returnType.getDisplayName()).append(" ")
            .append(spec.callingConvention).append(" ")
            .append(spec.name).append("(");
        for (int i = 0; i < spec.parameters.length; i++) {
            if (i > 0) {
                sb.append(", ");
            }
            sb.append(spec.parameters[i].getDataType().getDisplayName())
                .append(" ")
                .append(spec.parameters[i].getName());
        }
        if (spec.parameters.length == 0) {
            sb.append("void");
        }
        sb.append(")");
        return sb.toString();
    }

    private boolean applySpec(Spec spec, boolean dryRun) throws Exception {
        Function fn = getOrCreate(spec, dryRun);
        if (fn == null) {
            println("DRY: " + spec.address + " <missing> -> create " + signatureText(spec));
            return true;
        }

        if (dryRun) {
            println("DRY: " + spec.address + " " + fn.getName() + " -> " + signatureText(spec));
            return true;
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

        Function readBack = getOrCreate(spec, false);
        if (readBack == null || !readBack.getName().equals(spec.name)) {
            throw new IllegalStateException("Read-back name mismatch at " + spec.address);
        }
        println("OK: " + spec.address + " " + spec.name + " -> " + readBack.getSignature().toString());
        Thread.sleep(50);
        return true;
    }

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "unitai-indexed-entry-wave354",
            "retail-binary-evidence"
        };
        String[] result = new String[common.length + extras.length];
        System.arraycopy(common, 0, result, 0, common.length);
        System.arraycopy(extras, 0, result, common.length, extras.length);
        return result;
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");
        println("Mode: " + (dryRun ? "dry" : "apply"));

        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);
        DataType intType = IntegerDataType.dataType;
        DataType intPtr = new PointerDataType(intType);
        DataType boolType = BooleanDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec("0x00444f00", "CUnitAI__CallIndexedEntryVFunc10", "__thiscall", intType,
                "Signature/comment/tag hardening: resolves an indexed entry pointer from the UnitAI entry table and invokes the entry vfunc slot +0x10 when present. Static retail evidence only; exact source virtual name, concrete entry layout, runtime motion-controller behavior, and rebuild parity remain unproven.",
                tags("unitai-system", "signature-hardened", "indexed-entry"),
                new ParameterImpl[] {param("this", voidPtr), param("entryIndex", intType)}),
            new Spec("0x00444f20", "CUnitAI__CanUseIndexedSegmentEntry", "__thiscall", boolType,
                "Signature/comment/tag hardening: indexed segment eligibility predicate that resolves per-index entry pointers, checks linked segment/core-child gates, compares active segment value, and returns whether the entry can continue. Static retail evidence only; exact source virtual name, concrete segment-entry layout, runtime behavior, and rebuild parity remain unproven.",
                tags("unitai-system", "signature-hardened", "indexed-entry"),
                new ParameterImpl[] {param("this", voidPtr), param("entryIndex", intType)}),
            new Spec("0x00494fa0", "SharedMotionController__VFunc_UpdateUnitAIIndexedEntryFlag", "__thiscall", voidType,
                "Recovered vtable target shared by CMCBuggy slot 17 and CMCHiveBoss slot 6: if stateContext field +0xa4 is set it ORs bit 0 into outFlags; otherwise it reads an entry index from stateContext+0x88, calls CUnitAI__CanUseIndexedSegmentEntry through this+0x0c, and sets or clears bit 0 based on the result. Static retail evidence only; exact source virtual name, concrete motion-controller layouts, runtime mesh/core optimization behavior, and rebuild parity remain unproven.",
                tags("motion-controller", "function-boundary", "vtable-slot", "shared-vfunc"),
                new ParameterImpl[] {param("this", voidPtr), param("stateContext", voidPtr), param("outFlags", intPtr)}),
            new Spec("0x00494ff0", "SharedMotionController__VFunc_CallUnitAIIndexedEntryVFunc10", "__thiscall", intType,
                "Recovered vtable target shared by CMCBuggy slot 18 and CMCHiveBoss slot 7: returns zero while stateContext field +0xa4 is set; otherwise it reads an entry index from stateContext+0x88 and calls CUnitAI__CallIndexedEntryVFunc10 through this+0x0c. Static retail evidence only; exact source virtual name, concrete motion-controller layouts, runtime mesh/core optimization behavior, and rebuild parity remain unproven.",
                tags("motion-controller", "function-boundary", "vtable-slot", "shared-vfunc"),
                new ParameterImpl[] {param("this", voidPtr), param("stateContext", voidPtr)}),
            new Spec("0x00495020", "CMCBuggy__VFunc_GetUnitAIEntryTableRoot", "__thiscall", voidPtr,
                "Recovered CMCBuggy vtable slot 19 getter: follows field +0x0c and returns that pointed-to block's first pointer. Static retail evidence only; exact source virtual name, concrete CMCBuggy/UnitAI layout meaning, runtime behavior, and rebuild parity remain unproven.",
                tags("motion-controller", "function-boundary", "vtable-slot", "cmcbuggy"),
                new ParameterImpl[] {param("this", voidPtr)})
        };

        int changedOrWouldChange = 0;
        int failed = 0;
        for (Spec spec : specs) {
            try {
                if (applySpec(spec, dryRun)) {
                    changedOrWouldChange++;
                }
            } catch (Exception ex) {
                failed++;
                println("FAIL: " + spec.address + " " + spec.name + " " + ex.getClass().getSimpleName() + ": " + ex.getMessage());
            }
        }

        println("--- SUMMARY ---");
        println("targets=" + specs.length + " changed_or_would_change=" + changedOrWouldChange + " failed=" + failed + " dry=" + dryRun);
        if (failed > 0) {
            throw new IllegalStateException("UnitAI indexed-entry boundary tranche failed for " + failed + " target(s)");
        }
    }
}
