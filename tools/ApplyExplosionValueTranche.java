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

public class ApplyExplosionValueTranche extends GhidraScript {
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

    private Address parseTargetAddress(String addrText) {
        if (!addrText.startsWith("0x") && !addrText.startsWith("0X")) {
            addrText = "0x" + addrText;
        }
        Address addr = toAddr(addrText);
        if (addr == null) {
            throw new IllegalArgumentException("Bad address: " + addrText);
        }
        return addr;
    }

    private Function getExistingFunction(Address addr) {
        Function fn = getFunctionAt(addr);
        if (fn == null) {
            Function containing = getFunctionContaining(addr);
            if (containing != null && containing.getEntryPoint().equals(addr)) {
                fn = containing;
            }
        }
        return fn;
    }

    private Function getOrCreateFunction(Spec spec, boolean dryRun) throws Exception {
        Address addr = parseTargetAddress(spec.address);
        Function fn = getExistingFunction(addr);
        if (fn != null) {
            return fn;
        }
        if (!spec.createIfMissing) {
            throw new IllegalStateException("Function not found at " + spec.address);
        }
        if (dryRun) {
            return null;
        }

        boolean disasmOk = disassemble(addr);
        fn = createFunction(addr, null);
        if (fn == null) {
            throw new IllegalStateException("Function create failed at " + spec.address + " disassembleOk=" + disasmOk);
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
        Function fn = getOrCreateFunction(spec, dryRun);
        if (fn == null) {
            println("DRY: " + spec.address + " <missing> -> create " + expectedSignature(spec));
            return true;
        }
        if (!nameAllowed(fn.getName(), spec)) {
            throw new IllegalStateException("Unexpected function name at " + spec.address + ": " + fn.getName() + " != " + spec.name);
        }

        boolean needsRename = !fn.getName().equals(spec.name);
        if (dryRun) {
            println("DRY: " + spec.address + " " + fn.getName() + " -> " + expectedSignature(spec));
            return needsRename;
        }

        if (needsRename) {
            fn.setName(spec.name, SourceType.USER_DEFINED);
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

        Function readBack = getOrCreateFunction(spec, false);
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
            "physics-script-wave340",
            "physics-script",
            "explosion-value-tranche",
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
            new Spec("0x0043a860", "CPhysicsScriptStatements__CreateStatementType7", "__cdecl", voidPtr,
                "Signature/comment correction: type-7 explosion-value factory over observed value ids 0x1..0xf; allocates CExplosionBasedOn/effect/sound string values plus scalar offset-backed explosion values and installs vtables from 0x005da6c4 through 0x005da7dc. Exact class layouts, field semantics for scalar offsets, and runtime physics-script behavior remain unproven.",
                tags("value-factory", "explosion-value"),
                new String[] {"CPhysicsScriptStatements__CreateStatementType7"},
                false,
                new ParameterImpl[] {param("valueType", intType)}),

            new Spec("0x0043abd0", "CExplosionBasedOn__ApplyToExplosionByName", "__thiscall", voidType,
                "Name/signature correction: searches DAT_008553f8 by target explosionName and by source/base name at this+0x8, then copies selected owned effect/sound strings and scalar fields from the source explosion record. Exact source identity, record layout, and runtime physics-script behavior remain unproven.",
                tags("explosion-apply", "based-on-copy", "owned-string-copy"),
                new String[] {"CExplosionBasedOn__VFunc_01_0043abd0"},
                false,
                new ParameterImpl[] {param("this", voidPtr), param("explosionName", charPtr)}),

            new Spec("0x0043aea0", "CExplosionBasedOn__CopySoundString28", "__thiscall", voidType,
                "Name/signature correction: helper used by CExplosionBasedOn; if sourceString is non-null, frees the destination explosion record string at +0x28 and clones sourceString there. The +0x28 label is inferred from CExplosionSound vtable context; exact record layout remains unproven.",
                tags("explosion-apply", "based-on-copy", "owned-string-copy"),
                new String[] {"CExplosionBasedOn__ReallocateObjectSlot", "CExplosionBasedOn__Helper_0043aea0"},
                false,
                new ParameterImpl[] {param("this", voidPtr), param("sourceString", charPtr)}),

            new Spec("0x0043af10", "CExplosionBasedOn__CopyWaterSoundString2C", "__thiscall", voidType,
                "Name/signature correction: helper used by CExplosionBasedOn; if sourceString is non-null, frees the destination explosion record string at +0x2c and clones sourceString there. The +0x2c label is inferred from CExplosionWaterSound vtable context; exact record layout remains unproven.",
                tags("explosion-apply", "based-on-copy", "owned-string-copy"),
                new String[] {"CExplosionBasedOn__ReallocateObjectSlot_0043af10", "CExplosionBasedOn__Helper_0043af10"},
                false,
                new ParameterImpl[] {param("this", voidPtr), param("sourceString", charPtr)}),

            new Spec("0x0043af80", "CPhysicsExplosionValue__dtor_base", "__fastcall", voidType,
                "Name/signature correction: base destructor body restores vtable 0x005da7f0; that base vtable slot 0 points at recovered scalar-deleting destructor wrapper 0x0043af90. Exact source destructor identity and runtime lifetime behavior remain unproven.",
                tags("destructor", "value-base"),
                new String[] {"CPhysicsExplosionValue__ctor_like_0043af80"},
                false,
                new ParameterImpl[] {param("this", voidPtr)}),

            new Spec("0x0043af90", "CPhysicsExplosionValue__scalar_deleting_dtor", "__thiscall", voidPtr,
                "Recovered function boundary: CPhysicsExplosionValue base scalar-deleting destructor wrapper reached from vtable 0x005da7f0 slot 0; resets the base vtable and optionally calls OID__FreeObject when flags bit 0 is set. Exact source destructor identity and runtime lifetime behavior remain unproven.",
                tags("function-boundary", "destructor", "value-base"),
                new String[] {"FUN_0043af90"},
                true,
                new ParameterImpl[] {param("this", voidPtr), param("flags", intType)}),

            new Spec("0x0043afc0", "CExplosionAirEffect__ApplyToExplosionByName", "__thiscall", voidType,
                "Name/signature correction: searches DAT_008553f8 by explosionName and replaces the owned air-effect string at explosion record +0x18 from this+0x8. Exact record layout and runtime effect behavior remain unproven.",
                tags("explosion-apply", "owned-string-copy"),
                new String[] {"CExplosionAirEffect__VFunc_01_0043afc0"},
                false,
                new ParameterImpl[] {param("this", voidPtr), param("explosionName", charPtr)}),

            new Spec("0x0043b0b0", "CExplosionGroundEffect__ApplyToExplosionByName", "__thiscall", voidType,
                "Name/signature correction: searches DAT_008553f8 by explosionName and replaces the owned ground-effect string at explosion record +0x20 from this+0x8. Exact record layout and runtime effect behavior remain unproven.",
                tags("explosion-apply", "owned-string-copy"),
                new String[] {"CExplosionGroundEffect__VFunc_01_0043b0b0"},
                false,
                new ParameterImpl[] {param("this", voidPtr), param("explosionName", charPtr)}),

            new Spec("0x0043b1c0", "CExplosionWaterEffect__ApplyToExplosionByName", "__thiscall", voidType,
                "Name/signature correction: searches DAT_008553f8 by explosionName and replaces the owned water-effect string at explosion record +0x1c from this+0x8. Exact record layout and runtime effect behavior remain unproven.",
                tags("explosion-apply", "owned-string-copy"),
                new String[] {"CExplosionWaterEffect__VFunc_01_0043b1c0"},
                false,
                new ParameterImpl[] {param("this", voidPtr), param("explosionName", charPtr)}),

            new Spec("0x0043b2b0", "CExplosionUnitEffect__ApplyToExplosionByName", "__thiscall", voidType,
                "Name/signature correction: searches DAT_008553f8 by explosionName and replaces the owned unit-effect string at explosion record +0x24 from this+0x8. Exact record layout and runtime effect behavior remain unproven.",
                tags("explosion-apply", "owned-string-copy"),
                new String[] {"CExplosionUnitEffect__VFunc_01_0043b2b0"},
                false,
                new ParameterImpl[] {param("this", voidPtr), param("explosionName", charPtr)}),

            new Spec("0x0043b3a0", "CExplosionScalar34__ApplyToExplosionByName", "__thiscall", voidType,
                "Recovered function boundary: searches DAT_008553f8 by explosionName and writes the raw scalar at this+0x8 to explosion record +0x34. The field semantic is not yet proven beyond offset-backed scalar behavior.",
                tags("function-boundary", "explosion-apply", "offset-backed-scalar"),
                new String[] {"FUN_0043b3a0"},
                true,
                new ParameterImpl[] {param("this", voidPtr), param("explosionName", charPtr)}),

            new Spec("0x0043b430", "CExplosionScalar38__ApplyToExplosionByName", "__thiscall", voidType,
                "Recovered function boundary: searches DAT_008553f8 by explosionName and writes the raw scalar at this+0x8 to explosion record +0x38. The field semantic is not yet proven beyond offset-backed scalar behavior.",
                tags("function-boundary", "explosion-apply", "offset-backed-scalar"),
                new String[] {"FUN_0043b430"},
                true,
                new ParameterImpl[] {param("this", voidPtr), param("explosionName", charPtr)}),

            new Spec("0x0043b4c0", "CExplosionScalar3C__ApplyToExplosionByName", "__thiscall", voidType,
                "Recovered function boundary: searches DAT_008553f8 by explosionName and writes the raw scalar at this+0x8 to explosion record +0x3c. The field semantic is not yet proven beyond offset-backed scalar behavior.",
                tags("function-boundary", "explosion-apply", "offset-backed-scalar"),
                new String[] {"FUN_0043b4c0"},
                true,
                new ParameterImpl[] {param("this", voidPtr), param("explosionName", charPtr)}),

            new Spec("0x0043b550", "CExplosionScalar44__ApplyToExplosionByName", "__thiscall", voidType,
                "Recovered function boundary: searches DAT_008553f8 by explosionName and writes the raw scalar at this+0x8 to explosion record +0x44. The field semantic is not yet proven beyond offset-backed scalar behavior.",
                tags("function-boundary", "explosion-apply", "offset-backed-scalar"),
                new String[] {"FUN_0043b550"},
                true,
                new ParameterImpl[] {param("this", voidPtr), param("explosionName", charPtr)}),

            new Spec("0x0043b5e0", "CExplosionScalar48__ApplyToExplosionByName", "__thiscall", voidType,
                "Recovered function boundary: searches DAT_008553f8 by explosionName and writes the raw scalar at this+0x8 to explosion record +0x48. The field semantic is not yet proven beyond offset-backed scalar behavior.",
                tags("function-boundary", "explosion-apply", "offset-backed-scalar"),
                new String[] {"FUN_0043b5e0"},
                true,
                new ParameterImpl[] {param("this", voidPtr), param("explosionName", charPtr)}),

            new Spec("0x0043b670", "CExplosionScalar4C__ApplyToExplosionByName", "__thiscall", voidType,
                "Recovered function boundary: searches DAT_008553f8 by explosionName and writes the raw scalar at this+0x8 to explosion record +0x4c. The field semantic is not yet proven beyond offset-backed scalar behavior.",
                tags("function-boundary", "explosion-apply", "offset-backed-scalar"),
                new String[] {"FUN_0043b670"},
                true,
                new ParameterImpl[] {param("this", voidPtr), param("explosionName", charPtr)}),

            new Spec("0x0043b700", "CExplosionScalar40__ApplyToExplosionByName", "__thiscall", voidType,
                "Recovered function boundary: searches DAT_008553f8 by explosionName and writes the raw scalar at this+0x8 to explosion record +0x40. The field semantic is not yet proven beyond offset-backed scalar behavior.",
                tags("function-boundary", "explosion-apply", "offset-backed-scalar"),
                new String[] {"FUN_0043b700"},
                true,
                new ParameterImpl[] {param("this", voidPtr), param("explosionName", charPtr)}),

            new Spec("0x0043b790", "CExplosionSound__ApplyToExplosionByName", "__thiscall", voidType,
                "Name/signature correction: searches DAT_008553f8 by explosionName and replaces the owned sound string at explosion record +0x28 from this+0x8. Exact record layout and runtime audio behavior remain unproven.",
                tags("explosion-apply", "owned-string-copy"),
                new String[] {"CExplosionSound__VFunc_01_0043b790"},
                false,
                new ParameterImpl[] {param("this", voidPtr), param("explosionName", charPtr)}),

            new Spec("0x0043b880", "CExplosionWaterSound__ApplyToExplosionByName", "__thiscall", voidType,
                "Name/signature correction: searches DAT_008553f8 by explosionName and replaces the owned water-sound string at explosion record +0x2c from this+0x8. Exact record layout and runtime audio behavior remain unproven.",
                tags("explosion-apply", "owned-string-copy"),
                new String[] {"CExplosionWaterSound__VFunc_01_0043b880"},
                false,
                new ParameterImpl[] {param("this", voidPtr), param("explosionName", charPtr)}),

            new Spec("0x0043b970", "CPhysicsExplosionValueLeaf__shared_scalar_deleting_dtor", "__thiscall", voidPtr,
                "Name/signature correction: shared scalar-deleting destructor wrapper used by leaf explosion-value vtables; calls CPhysicsExplosionValue__dtor_base at 0x0043af80, optionally frees this via OID__FreeObject, and returns this. Specific leaf owner, concrete layouts, and runtime lifetime behavior remain unproven.",
                tags("destructor", "shared-vtable-slot"),
                new String[] {"VFuncSlot_00_0043b970"},
                false,
                new ParameterImpl[] {param("this", voidPtr), param("flags", intType)}),
        };

        int changed = 0;
        int failed = 0;
        for (Spec spec : specs) {
            try {
                if (applySpec(spec, dryRun)) {
                    changed++;
                }
            } catch (Exception ex) {
                failed++;
                println("FAIL: " + spec.address + " " + spec.name + " :: " + ex.getMessage());
                if (!dryRun) {
                    throw ex;
                }
            }
        }

        println("SUMMARY: mode=" + (dryRun ? "dry" : "apply")
            + " targets=" + specs.length
            + " changed_or_would_change=" + changed
            + " failed=" + failed);
        if (failed > 0) {
            throw new IllegalStateException("Failed specs: " + failed);
        }
    }
}
