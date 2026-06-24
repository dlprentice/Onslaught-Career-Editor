//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.CharDataType;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

public class ApplyDebrisSignatureBoundaryTranche extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final String comment;
        final String[] tags;
        final String[] previousNames;
        final boolean createIfMissing;
        final ParameterImpl[] parameters;

        Spec(
                String address,
                String name,
                String callingConvention,
                DataType returnType,
                String comment,
                String[] tags,
                String[] previousNames,
                boolean createIfMissing,
                ParameterImpl[] parameters) {
            this.address = address;
            this.name = name;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.comment = comment;
            this.tags = tags;
            this.previousNames = previousNames;
            this.createIfMissing = createIfMissing;
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

    private Address addr(String addrText) {
        if (!addrText.startsWith("0x") && !addrText.startsWith("0X")) {
            addrText = "0x" + addrText;
        }
        Address result = toAddr(addrText);
        if (result == null) {
            throw new IllegalArgumentException("Bad address: " + addrText);
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
            return fn;
        }
        if (!spec.createIfMissing) {
            throw new IllegalStateException("Function not found at " + spec.address);
        }
        if (dryRun) {
            return null;
        }

        disassemble(address);
        fn = createFunction(address, spec.name);
        if (fn == null) {
            throw new IllegalStateException("Function create failed at " + spec.address);
        }
        return fn;
    }

    private ParameterImpl param(String name, DataType type) throws Exception {
        return new ParameterImpl(name, type, currentProgram);
    }

    private boolean allowedName(Function fn, Spec spec) {
        if (fn.getName().equals(spec.name)) {
            return true;
        }
        for (String previous : spec.previousNames) {
            if (fn.getName().equals(previous)) {
                return true;
            }
        }
        return false;
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
        if (!allowedName(fn, spec)) {
            throw new IllegalStateException("Unexpected function name at " + spec.address + ": " + fn.getName());
        }

        if (dryRun) {
            println("DRY: " + spec.address + " " + fn.getName() + " -> " + signatureText(spec));
            return true;
        }

        if (!fn.getName().equals(spec.name)) {
            fn.setName(spec.name, SourceType.USER_DEFINED);
        }
        fn.setCallingConvention(spec.callingConvention);
        fn.setReturnType(spec.returnType, SourceType.USER_DEFINED);
        fn.replaceParameters(FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS, true, SourceType.USER_DEFINED, spec.parameters);
        fn.setComment(spec.comment);
        for (String tag : spec.tags) {
            fn.addTag(tag);
        }

        Function readBack = getOrCreate(spec, false);
        if (!readBack.getName().equals(spec.name)) {
            throw new IllegalStateException("Read-back name mismatch at " + spec.address + ": " + readBack.getName());
        }
        println("OK: " + spec.address + " " + spec.name + " -> " + readBack.getSignature().toString());
        Thread.sleep(50);
        return true;
    }

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "debris-wave347",
            "debris",
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
        DataType charPtr = new PointerDataType(CharDataType.dataType);
        DataType intType = IntegerDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec("0x004411a0", "CDebris__Init", "__thiscall", voidType,
                "Initializes CDebris: builds a temporary resource descriptor for grs_tuft1.MSH, creates/stores the render object at this+0x30, marks the init object at +0x70, delegates to CComplexThing__Init, registers cg_debrisarea/cg_debrisfadestart/cg_debrisfadeend console variables, and links this into the global debris list at DAT_0066eb78. Static retail evidence only; exact source identity, class layout, runtime render behavior, and rebuild parity remain unproven.",
                tags("init", "vtable-slot", "name-correction"),
                new String[] {"CDebris__VFunc_09_004411a0", "CDebris__Init"},
                false,
                new ParameterImpl[] {param("this", voidPtr), param("init", voidPtr)}),
            new Spec("0x00441320", "CDebris__dtor_base", "__fastcall", voidType,
                "Destructor body for CDebris: restores observed vtable pointers, unlinks this from the DAT_0066eb78 global debris list through the next pointer at this+0x7c, then chains to CComplexThing__dtor_base. Static retail evidence only; exact source identity, class layout, runtime behavior, and rebuild parity remain unproven.",
                tags("destructor", "name-correction"),
                new String[] {"CDebris__ctor_like_00441320", "CDebris__dtor_base"},
                false,
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x00441360", "CDebris__GetClassName", "__cdecl", charPtr,
                "Recovered function boundary: returns the class-name string CDebris from 0x006283e0. Static retail evidence only; exact source macro identity and rebuild parity remain unproven.",
                tags("function-boundary", "class-metadata"),
                new String[] {"CDebris__GetClassName"},
                true,
                new ParameterImpl[] {}),
            new Spec("0x00441370", "CDebris__GetClassId", "__cdecl", intType,
                "Recovered function boundary: returns constant 0x1f, a likely CDebris class/OID id used by the class metadata table. Static retail evidence only; exact source enum identity and rebuild parity remain unproven.",
                tags("function-boundary", "class-metadata"),
                new String[] {"CDebris__GetClassId"},
                true,
                new ParameterImpl[] {}),
            new Spec("0x00441380", "CDebris__scalar_deleting_dtor", "__thiscall", voidPtr,
                "CDebris scalar-deleting destructor wrapper: calls CDebris__dtor_base, frees this through OID__FreeObject when flags bit 0 is set, and returns this. Static retail evidence only; exact source identity, class layout, runtime behavior, and rebuild parity remain unproven.",
                tags("destructor", "vtable-slot", "name-correction"),
                new String[] {"CDebris__VFunc_01_00441380", "CDebris__scalar_deleting_dtor"},
                false,
                new ParameterImpl[] {param("this", voidPtr), param("flags", intType)}),
            new Spec("0x004413a0", "CDebris__Render", "__thiscall", voidType,
                "Recovered function boundary: CDebris render path checks visibility/render flags and the render object at this+0x30, computes a debris fade alpha from this+0x80 against cg_debrisfadestart/cg_debrisfadeend, writes DAT_0063012c as temporary RF alpha state, dispatches the render-object flags path, and restores alpha to 0xff. Static retail evidence only; exact source identity, class layout, runtime render behavior, and rebuild parity remain unproven.",
                tags("function-boundary", "render"),
                new String[] {"CDebris__Render"},
                true,
                new ParameterImpl[] {param("this", voidPtr), param("renderFlags", intType)}),
            new Spec("0x00441420", "CDebris__RenderImposter", "__fastcall", voidType,
                "Recovered function boundary: CDebris imposter render path checks the render object at this+0x30 and TF_DONT_RENDER, computes the same debris fade alpha from this+0x80 against cg_debrisfadestart/cg_debrisfadeend, dispatches the render-object imposter path, and restores DAT_0063012c to 0xff. Static retail evidence only; exact source identity, class layout, runtime render behavior, and rebuild parity remain unproven.",
                tags("function-boundary", "render", "imposter"),
                new String[] {"CDebris__RenderImposter"},
                true,
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
            throw new IllegalStateException("Debris tranche failed for " + failed + " target(s)");
        }
    }
}
