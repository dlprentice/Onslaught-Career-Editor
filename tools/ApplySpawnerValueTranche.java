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

public class ApplySpawnerValueTranche extends GhidraScript {
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
        return needsRename;
    }

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "physics-script-wave339",
            "physics-script",
            "spawner-value-tranche",
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
            new Spec("0x004014c0", "SharedVFunc__NoOpOneArg_004014c0", "__thiscall", voidType,
                "Name/signature correction: supersedes the stale CFrontEndPage owner-specific label; this is a shared ret 0x4 one-argument no-op vtable target also referenced by non-frontend tables, including the CSpawnerRecall vtable. Exact owner coverage, virtual contracts, and runtime behavior remain unproven.",
                tags("shared-vtable-slot", "no-op"),
                new String[] {"CFrontEndPage__ActiveNotification_NoOp"},
                false,
                new ParameterImpl[] {param("this", voidPtr), param("arg0", intType)}),

            new Spec("0x00405930", "SharedVFunc__ReturnZero_00405930", "__thiscall", intType,
                "Name/signature correction: supersedes the stale CControllerDefinition owner-specific label; this is a shared vtable target that returns 0 and is referenced by many unrelated tables, including the CSpawnerRecall vtable. Exact owner coverage, virtual contracts, and runtime behavior remain unproven.",
                tags("shared-vtable-slot", "return-zero"),
                new String[] {"CControllerDefinition__VFunc_03_00405930"},
                false,
                new ParameterImpl[] {param("this", voidPtr)}),

            new Spec("0x00434b60", "CPhysicsScriptValue__LoadScalarAt08FromMemBuffer", "__thiscall", voidType,
                "Recovered shared serialization helper: reads one 4-byte scalar from CDXMemBuffer into this+0x8; referenced by many PhysicsScript numeric value vtables, including spawner numeric values. Exact source owner, scalar type, and runtime script behavior remain unproven.",
                tags("function-boundary", "shared-serialization", "scalar-value"),
                new String[] {"FUN_00434b60"},
                true,
                new ParameterImpl[] {param("this", voidPtr), param("memBuffer", voidPtr)}),

            new Spec("0x004398f0", "CPhysicsScriptValue__GetOwnedStringAt08SerializedSize", "__fastcall", intType,
                "Recovered shared serialization helper: returns the serialized byte count for a null-terminated owned string at this+0x8, including the terminator. Exact source owner and runtime script behavior remain unproven.",
                tags("function-boundary", "shared-serialization", "owned-string-size"),
                new String[] {"FUN_004398f0"},
                true,
                new ParameterImpl[] {param("this", voidPtr)}),

            new Spec("0x00439b40", "CPhysicsScriptStatements__CreateStatementType6", "__cdecl", voidPtr,
                "Signature/comment correction: type-6 spawner-value factory over observed value ids 0x1..0xe; allocates CSpawnerUnit/BasedOn string-sized values, numeric/boolean spawner values, and installs vtables from 0x005da598 through 0x005da6b0. Exact class layouts and runtime physics-script behavior remain unproven.",
                tags("value-factory", "spawner-value"),
                new String[] {"CPhysicsScriptStatements__CreateStatementType6"},
                false,
                new ParameterImpl[] {param("valueType", intType)}),

            new Spec("0x00439e70", "CSpawnerBasedOn__ApplyToSpawnerByName", "__thiscall", voidType,
                "Name/signature correction: searches DAT_008553f4 by target spawnerName and by source/base name at this+0x8, then copies selected spawner fields and owned string state from the source record. Exact source identity, record layout, and runtime physics-script behavior remain unproven.",
                tags("spawner-apply", "based-on-copy"),
                new String[] {"CSpawnerBasedOn__VFunc_01_00439e70"},
                false,
                new ParameterImpl[] {param("this", voidPtr), param("spawnerName", charPtr)}),

            new Spec("0x0043a040", "CPhysicsSpawnerValue__dtor_base", "__fastcall", voidType,
                "Name/signature correction: base destructor body restores vtable 0x005da6b0; that base vtable slot 0 points at recovered scalar-deleting destructor 0x0043a050. Exact source destructor identity and runtime lifetime behavior remain unproven.",
                tags("destructor", "value-base"),
                new String[] {"CPhysicsSpawnerValue__ctor_like_0043a040"},
                false,
                new ParameterImpl[] {param("this", voidPtr)}),

            new Spec("0x0043a050", "CPhysicsSpawnerValue__scalar_deleting_dtor", "__thiscall", voidPtr,
                "Recovered function boundary: CPhysicsSpawnerValue base scalar-deleting destructor wrapper reached from vtable 0x005da6b0 slot 0; resets the base vtable and optionally calls OID__FreeObject when flags bit 0 is set. Exact source destructor identity and runtime lifetime behavior remain unproven.",
                tags("function-boundary", "destructor", "value-base"),
                new String[] {"FUN_0043a050"},
                true,
                new ParameterImpl[] {param("this", voidPtr), param("flags", intType)}),

            new Spec("0x0043a080", "CSpawnerUnit__ApplyToSpawnerByName", "__thiscall", voidType,
                "Name/signature correction: searches DAT_008553f4 by spawnerName and replaces/copies the owned unit string from this+0x8 into spawner record+0x4. Exact source identity, record layout, and runtime physics-script behavior remain unproven.",
                tags("spawner-apply", "owned-string-copy"),
                new String[] {"CSpawnerUnit__VFunc_01_0043a080"},
                false,
                new ParameterImpl[] {param("this", voidPtr), param("spawnerName", charPtr)}),

            new Spec("0x0043a170", "CSpawnerDelay__ApplyToSpawnerByName", "__thiscall", voidType,
                "Recovered function boundary: searches DAT_008553f4 by spawnerName and writes the scalar at this+0x8 to spawner record+0x18. Exact source identity, record layout, scalar type, and runtime physics-script behavior remain unproven.",
                tags("function-boundary", "spawner-apply", "numeric-spawner-value"),
                new String[] {"FUN_0043a170"},
                true,
                new ParameterImpl[] {param("this", voidPtr), param("spawnerName", charPtr)}),

            new Spec("0x0043a200", "CSpawnerAmount__ApplyToSpawnerByName", "__thiscall", voidType,
                "Recovered function boundary: searches DAT_008553f4 by spawnerName and writes the scalar at this+0x8 to spawner record+0xc. Exact source identity, record layout, scalar type, and runtime physics-script behavior remain unproven.",
                tags("function-boundary", "spawner-apply", "numeric-spawner-value"),
                new String[] {"FUN_0043a200"},
                true,
                new ParameterImpl[] {param("this", voidPtr), param("spawnerName", charPtr)}),

            new Spec("0x0043a290", "CSpawnerConditions__ApplyToSpawnerByName", "__thiscall", voidType,
                "Recovered function boundary: searches DAT_008553f4 by spawnerName and writes the scalar at this+0x8 to spawner record+0x14. Exact source identity, record layout, scalar type, and runtime physics-script behavior remain unproven.",
                tags("function-boundary", "spawner-apply", "numeric-spawner-value"),
                new String[] {"FUN_0043a290"},
                true,
                new ParameterImpl[] {param("this", voidPtr), param("spawnerName", charPtr)}),

            new Spec("0x0043a320", "CSpawnerSquadSize__ApplyToSpawnerByName", "__thiscall", voidType,
                "Recovered function boundary: searches DAT_008553f4 by spawnerName and writes the scalar at this+0x8 to spawner record+0x10. Exact source identity, record layout, scalar type, and runtime physics-script behavior remain unproven.",
                tags("function-boundary", "spawner-apply", "numeric-spawner-value"),
                new String[] {"FUN_0043a320"},
                true,
                new ParameterImpl[] {param("this", voidPtr), param("spawnerName", charPtr)}),

            new Spec("0x0043a3b0", "CSpawnerSquadDelay__ApplyToSpawnerByName", "__thiscall", voidType,
                "Recovered function boundary: searches DAT_008553f4 by spawnerName and writes the scalar at this+0x8 to spawner record+0x20. Exact source identity, record layout, scalar type, and runtime physics-script behavior remain unproven.",
                tags("function-boundary", "spawner-apply", "numeric-spawner-value"),
                new String[] {"FUN_0043a3b0"},
                true,
                new ParameterImpl[] {param("this", voidPtr), param("spawnerName", charPtr)}),

            new Spec("0x0043a440", "CSpawnerSeekDelay__ApplyToSpawnerByName", "__thiscall", voidType,
                "Recovered function boundary: searches DAT_008553f4 by spawnerName and writes the scalar at this+0x8 to spawner record+0x1c. Exact source identity, record layout, scalar type, and runtime physics-script behavior remain unproven.",
                tags("function-boundary", "spawner-apply", "numeric-spawner-value"),
                new String[] {"FUN_0043a440"},
                true,
                new ParameterImpl[] {param("this", voidPtr), param("spawnerName", charPtr)}),

            new Spec("0x0043a4d0", "CSpawnerRecall__ApplyToSpawnerByName", "__thiscall", voidType,
                "Recovered function boundary: searches DAT_008553f4 by spawnerName and writes constant 1 to spawner record+0x28. Exact source identity, record layout, boolean semantics, and runtime physics-script behavior remain unproven.",
                tags("function-boundary", "spawner-apply", "boolean-spawner-value"),
                new String[] {"FUN_0043a4d0"},
                true,
                new ParameterImpl[] {param("this", voidPtr), param("spawnerName", charPtr)}),

            new Spec("0x0043a570", "CSpawnerMinRange__ApplyToSpawnerByName", "__thiscall", voidType,
                "Recovered function boundary: searches DAT_008553f4 by spawnerName and writes the scalar at this+0x8 to spawner record+0x2c. Exact source identity, record layout, scalar type, and runtime physics-script behavior remain unproven.",
                tags("function-boundary", "spawner-apply", "numeric-spawner-value"),
                new String[] {"FUN_0043a570"},
                true,
                new ParameterImpl[] {param("this", voidPtr), param("spawnerName", charPtr)}),

            new Spec("0x0043a600", "CSpawnerMaxRange__ApplyToSpawnerByName", "__thiscall", voidType,
                "Recovered function boundary: searches DAT_008553f4 by spawnerName and writes the scalar at this+0x8 to spawner record+0x30. Exact source identity, record layout, scalar type, and runtime physics-script behavior remain unproven.",
                tags("function-boundary", "spawner-apply", "numeric-spawner-value"),
                new String[] {"FUN_0043a600"},
                true,
                new ParameterImpl[] {param("this", voidPtr), param("spawnerName", charPtr)}),

            new Spec("0x0043a690", "CSpawnerPreSpawnDelay__ApplyToSpawnerByName", "__thiscall", voidType,
                "Recovered function boundary: searches DAT_008553f4 by spawnerName and writes the scalar at this+0x8 to spawner record+0x34. Exact source identity, record layout, scalar type, and runtime physics-script behavior remain unproven.",
                tags("function-boundary", "spawner-apply", "numeric-spawner-value"),
                new String[] {"FUN_0043a690"},
                true,
                new ParameterImpl[] {param("this", voidPtr), param("spawnerName", charPtr)}),

            new Spec("0x0043a720", "CSpawnerPostSpawnDelay__ApplyToSpawnerByName", "__thiscall", voidType,
                "Recovered function boundary: searches DAT_008553f4 by spawnerName and writes the scalar at this+0x8 to spawner record+0x38. Exact source identity, record layout, scalar type, and runtime physics-script behavior remain unproven.",
                tags("function-boundary", "spawner-apply", "numeric-spawner-value"),
                new String[] {"FUN_0043a720"},
                true,
                new ParameterImpl[] {param("this", voidPtr), param("spawnerName", charPtr)}),

            new Spec("0x0043a7b0", "CSpawnerInfinite__ApplyToSpawnerByName", "__thiscall", voidType,
                "Recovered function boundary: searches DAT_008553f4 by spawnerName and writes the scalar at this+0x8 to spawner record+0x24. Exact source identity, record layout, scalar type, and runtime physics-script behavior remain unproven.",
                tags("function-boundary", "spawner-apply", "numeric-spawner-value"),
                new String[] {"FUN_0043a7b0"},
                true,
                new ParameterImpl[] {param("this", voidPtr), param("spawnerName", charPtr)}),

            new Spec("0x0043a840", "CPhysicsSpawnerValueLeaf__shared_scalar_deleting_dtor", "__thiscall", voidPtr,
                "Name/signature correction: shared scalar-deleting destructor wrapper used by many leaf spawner-value vtables; calls CPhysicsSpawnerValue__dtor_base at 0x0043a040, optionally frees this via OID__FreeObject, and returns this. Specific leaf owner, concrete layouts, and runtime lifetime behavior remain unproven.",
                tags("destructor", "shared-vtable-slot"),
                new String[] {"VFuncSlot_00_0043a840"},
                false,
                new ParameterImpl[] {param("this", voidPtr), param("flags", intType)}),

            new Spec("0x0043b1a0", "CPhysicsScriptValue__LoadOwnedStringAt08FromMemBuffer", "__thiscall", voidType,
                "Recovered shared serialization helper: reads a null-terminated owned string from CDXMemBuffer into storage at this+0x8; referenced by string-valued PhysicsScript value vtables including CSpawnerUnit and CSpawnerBasedOn. Exact source owner and runtime script behavior remain unproven.",
                tags("function-boundary", "shared-serialization", "owned-string-load"),
                new String[] {"FUN_0043b1a0"},
                true,
                new ParameterImpl[] {param("this", voidPtr), param("memBuffer", voidPtr)}),

            new Spec("0x004db8c0", "CPhysicsScriptValue__GetScalarSerializedSize4", "__fastcall", intType,
                "Recovered shared serialization helper: returns the fixed serialized size 4 for scalar PhysicsScript values; referenced by many numeric value vtables including spawner numeric values. Exact source owner, scalar type, and runtime script behavior remain unproven.",
                tags("function-boundary", "shared-serialization", "scalar-value"),
                new String[] {"FUN_004db8c0"},
                true,
                new ParameterImpl[] {param("this", voidPtr)})
        };

        int changed = 0;
        int failures = 0;
        for (Spec spec : specs) {
            try {
                if (applySpec(spec, dryRun)) {
                    changed++;
                }
            } catch (Exception ex) {
                failures++;
                println("FAIL: " + spec.address + " " + ex.getMessage());
            }
        }

        println("SUMMARY: targets=" + specs.length + " changed_or_would_change=" + changed + " failed=" + failures);
        if (failures != 0) {
            throw new IllegalStateException("Spawner value tranche failed for " + failures + " target(s)");
        }
    }
}
