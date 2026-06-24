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

public class ApplyRoundValueTailTranche extends GhidraScript {
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
            return false;
        }
        if (!nameAllowed(fn.getName(), spec)) {
            throw new IllegalStateException("Unexpected function name at " + spec.address + ": " + fn.getName() + " != " + spec.name);
        }

        boolean needsRename = !fn.getName().equals(spec.name);
        if (dryRun) {
            println("DRY: " + spec.address + " " + fn.getName() + " -> " + expectedSignature(spec));
            return false;
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
            "physics-script-wave338",
            "physics-script",
            "round-value-tail-tranche",
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
            new Spec("0x00437fe0", "CPhysicsRoundValue__SetOwnedAuxStringAt0C", "__thiscall", voidType,
                "Name/signature correction: owned string copy helper for round/value records; frees this+0xc and copies sourceString into storage newly allocated by OID__AllocObject using the WorldPhysicsManager allocation tag 0x23c. Exact source owner, concrete layout, and runtime script behavior remain unproven.",
                tags("owned-string-copy", "round-value"),
                new String[] {"CPhysicsScriptStatements__SetOwnedString"},
                false,
                new ParameterImpl[] {param("this", voidPtr), param("sourceString", charPtr)}),

            new Spec("0x00438050", "CPhysicsRoundValue__SetOwnedValueStringAt08", "__thiscall", voidType,
                "Name/signature correction: supersedes the stale CUnitAI owner label; frees this+0x8 and copies sourceString into the owned value string slot used by round-value handlers. Exact source owner, concrete layout, and runtime script behavior remain unproven.",
                tags("owned-string-copy", "round-value", "supersedes-stale-unitai-owner"),
                new String[] {"CUnitAI__SetOwnedDebugString"},
                false,
                new ParameterImpl[] {param("this", voidPtr), param("sourceString", charPtr)}),

            new Spec("0x004380c0", "CPhysicsRoundValue__dtor_base", "__fastcall", voidType,
                "Name/signature correction: destructor body installs the CPhysicsRoundValue base vtable at 0x005da584; that vtable slot 0 points at recovered scalar-deleting destructor 0x004380d0. Exact source destructor identity and runtime lifetime behavior remain unproven.",
                tags("destructor", "round-value"),
                new String[] {"CPhysicsRoundValue__ctor_like_004380c0"},
                false,
                new ParameterImpl[] {param("this", voidPtr)}),

            new Spec("0x004380d0", "CPhysicsRoundValue__scalar_deleting_dtor", "__thiscall", voidPtr,
                "Recovered function boundary: CPhysicsRoundValue base scalar-deleting destructor wrapper reached from vtable 0x005da584 slot 0; resets the base vtable and optionally calls OID__FreeObject when flags bit 0 is set. Exact source destructor identity and runtime lifetime behavior remain unproven.",
                tags("function-boundary", "destructor", "round-value"),
                new String[] {"FUN_004380d0"},
                true,
                new ParameterImpl[] {param("this", voidPtr), param("flags", intType)}),

            new Spec("0x00438400", "CPhysicsRoundValueLeaf__shared_scalar_deleting_dtor", "__thiscall", voidPtr,
                "Name/signature correction: shared scalar-deleting destructor wrapper used by many leaf round-value vtables; it calls CPhysicsRoundValue__dtor_base at 0x004380c0, optionally frees this via OID__FreeObject, and returns this. Specific leaf owner, concrete layouts, and runtime lifetime behavior remain unproven.",
                tags("destructor", "round-value", "shared-vtable-slot"),
                new String[] {"VFuncSlot_00_00438400"},
                false,
                new ParameterImpl[] {param("this", voidPtr), param("flags", intType)}),

            new Spec("0x00438b40", "CRoundGridOfFear__ApplyToRoundByName", "__thiscall", voidType,
                "Name/signature correction: searches DAT_008553f0 by roundName at round record+0x18 and writes ROUND(this+0x8) into round record+0x58. Exact round record layout, source identity, and runtime physics behavior remain unproven.",
                tags("round-apply", "numeric-round-value"),
                new String[] {"CRoundGridOfFear__VFunc_01_00438b40"},
                false,
                new ParameterImpl[] {param("this", voidPtr), param("roundName", charPtr)}),

            new Spec("0x004394e0", "CRoundSeek__ApplyToRoundByName", "__thiscall", voidType,
                "Recovered function boundary: searches DAT_008553f0 by roundName and writes the nested child value result from this+0x8 into round record+0x48. Exact child value type, round record layout, source identity, and runtime physics behavior remain unproven.",
                tags("function-boundary", "round-apply", "nested-round-value"),
                new String[] {"FUN_004394e0"},
                true,
                new ParameterImpl[] {param("this", voidPtr), param("roundName", charPtr)}),

            new Spec("0x00439580", "CRoundSeek__LoadFromMemBuffer", "__thiscall", voidType,
                "Name/signature correction: CDXMemBuffer load helper reads a nested value type id, dispatches CPhysicsScriptStatements__CreateStatementType11, and stores the child value at this+0x8. Exact serialized format, child type semantics, and rebuild parity remain unproven.",
                tags("statement-load", "nested-round-value"),
                new String[] {"CRoundSeek__VFunc_03_00439580"},
                false,
                new ParameterImpl[] {param("this", voidPtr), param("memBuffer", voidPtr)}),

            new Spec("0x004395b0", "CRoundSeek__scalar_deleting_dtor", "__thiscall", voidPtr,
                "Name/signature correction: scalar-deleting destructor wrapper calls CRoundSeek__dtor_base at 0x004395d0, optionally frees this via OID__FreeObject when flags bit 0 is set, and returns this. Exact source destructor identity and runtime lifetime behavior remain unproven.",
                tags("destructor", "nested-round-value"),
                new String[] {"CRoundSeek__VFunc_00_004395b0"},
                false,
                new ParameterImpl[] {param("this", voidPtr), param("flags", intType)}),

            new Spec("0x004395d0", "CRoundSeek__dtor_base", "__fastcall", voidType,
                "Name/signature correction: destructor body sets the CRoundSeek vtable, destroys the owned child value at this+0x8 through its vtable slot 0 when present, then restores the CPhysicsRoundValue base vtable. Exact source destructor identity and runtime lifetime behavior remain unproven.",
                tags("destructor", "nested-round-value"),
                new String[] {"CRoundSeek__ctor_like_004395d0"},
                false,
                new ParameterImpl[] {param("this", voidPtr)}),

            new Spec("0x00439620", "CRoundMesh__ApplyToRoundByName", "__thiscall", voidType,
                "Name/signature correction: searches DAT_008553f0 by roundName and replaces the owned mesh string at round record+0xc from the value string at this+0x8. Exact round record layout, string ownership, and runtime physics behavior remain unproven.",
                tags("round-apply", "owned-string-copy"),
                new String[] {"CRoundMesh__VFunc_01_00439620"},
                false,
                new ParameterImpl[] {param("this", voidPtr), param("roundName", charPtr)}),

            new Spec("0x00439710", "CRoundEffect__ApplyToRoundByName", "__thiscall", voidType,
                "Name/signature correction: searches DAT_008553f0 by roundName and replaces the owned effect string at round record+0x10 from the value string at this+0x8. Exact round record layout, string ownership, and runtime physics behavior remain unproven.",
                tags("round-apply", "owned-string-copy"),
                new String[] {"CRoundEffect__VFunc_01_00439710"},
                false,
                new ParameterImpl[] {param("this", voidPtr), param("roundName", charPtr)}),

            new Spec("0x00439800", "CRoundWaterEffect__ApplyToRoundByName", "__thiscall", voidType,
                "Name/signature correction: searches DAT_008553f0 by roundName and replaces the owned water-effect string at round record+0x14 from the value string at this+0x8. Exact round record layout, string ownership, and runtime physics behavior remain unproven.",
                tags("round-apply", "owned-string-copy"),
                new String[] {"CRoundWaterEffect__VFunc_01_00439800"},
                false,
                new ParameterImpl[] {param("this", voidPtr), param("roundName", charPtr)}),

            new Spec("0x00439910", "CRoundExplosion__ApplyToRoundByName", "__thiscall", voidType,
                "Name/signature correction: searches DAT_008553f0 by roundName and replaces the owned explosion string at round record+0x8 from the value string at this+0x8. Exact round record layout, string ownership, and runtime physics behavior remain unproven.",
                tags("round-apply", "owned-string-copy"),
                new String[] {"CRoundExplosion__VFunc_01_00439910"},
                false,
                new ParameterImpl[] {param("this", voidPtr), param("roundName", charPtr)}),

            new Spec("0x00439a00", "CRoundTreeCollision__ApplyToRoundByName", "__thiscall", voidType,
                "Recovered function boundary: searches DAT_008553f0 by roundName and writes the nested child value result from this+0x8 into round record+0xa4. Exact child value type, round record layout, source identity, and runtime physics behavior remain unproven.",
                tags("function-boundary", "round-apply", "nested-round-value"),
                new String[] {"FUN_00439a00"},
                true,
                new ParameterImpl[] {param("this", voidPtr), param("roundName", charPtr)}),

            new Spec("0x00439aa0", "CRoundTreeCollision__LoadFromMemBuffer", "__thiscall", voidType,
                "Name/signature correction: CDXMemBuffer load helper reads a nested value type id, dispatches CPhysicsScriptStatements__CreateStatementType15, and stores the child value at this+0x8. Exact serialized format, child type semantics, and rebuild parity remain unproven.",
                tags("statement-load", "nested-round-value"),
                new String[] {"CRoundTreeCollision__VFunc_03_00439aa0"},
                false,
                new ParameterImpl[] {param("this", voidPtr), param("memBuffer", voidPtr)}),

            new Spec("0x00439ad0", "CRoundTreeCollision__scalar_deleting_dtor", "__thiscall", voidPtr,
                "Name/signature correction: scalar-deleting destructor wrapper calls CRoundTreeCollision__dtor_base at 0x00439af0, optionally frees this via OID__FreeObject when flags bit 0 is set, and returns this. Exact source destructor identity and runtime lifetime behavior remain unproven.",
                tags("destructor", "nested-round-value"),
                new String[] {"CRoundTreeCollision__VFunc_00_00439ad0"},
                false,
                new ParameterImpl[] {param("this", voidPtr), param("flags", intType)}),

            new Spec("0x00439af0", "CRoundTreeCollision__dtor_base", "__fastcall", voidType,
                "Name/signature correction: destructor body sets the CRoundTreeCollision vtable, destroys the owned child value at this+0x8 through its vtable slot 0 when present, then restores the CPhysicsRoundValue base vtable. Exact source destructor identity and runtime lifetime behavior remain unproven.",
                tags("destructor", "nested-round-value"),
                new String[] {"CRoundTreeCollision__ctor_like_00439af0"},
                false,
                new ParameterImpl[] {param("this", voidPtr)}),
        };

        int updated = 0;
        int skipped = 0;
        int renamed = 0;
        int missing = 0;
        int bad = 0;

        for (Spec spec : specs) {
            try {
                boolean didRename = applySpec(spec, dryRun);
                updated++;
                if (didRename) {
                    renamed++;
                }
            } catch (IllegalStateException ex) {
                println("FAIL: " + spec.address + " " + ex.getMessage());
                if (ex.getMessage().contains("Function not found")) {
                    missing++;
                } else {
                    bad++;
                }
            }
        }

        println("SUMMARY: updated=" + updated + " skipped=" + skipped + " renamed=" + renamed + " missing=" + missing + " bad=" + bad);
        if (!dryRun && (missing > 0 || bad > 0)) {
            throw new IllegalStateException("Apply failed: missing=" + missing + " bad=" + bad);
        }
    }
}
