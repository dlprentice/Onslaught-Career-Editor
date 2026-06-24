//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

public class ApplySeekBehaviourStateTranche extends GhidraScript {
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

        boolean disasmOk = disassemble(address);
        fn = createFunction(address, null);
        if (fn == null) {
            throw new IllegalStateException("Function create failed at " + spec.address + " disasmOk=" + disasmOk);
        }
        return fn;
    }

    private ParameterImpl param(String name, DataType type) throws Exception {
        return new ParameterImpl(name, type, currentProgram);
    }

    private String fun(String address) {
        String value = address.startsWith("0x") || address.startsWith("0X") ? address.substring(2) : address;
        return "FUN_" + value.toLowerCase();
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

        boolean changed = !fn.getName().equals(spec.name);
        if (dryRun) {
            println("DRY: " + spec.address + " " + fn.getName() + " -> " + signatureText(spec));
            return changed;
        }

        if (changed) {
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
            "physics-script-wave344",
            "physics-script",
            "seek-behavior-state-tranche",
            "retail-binary-evidence"
        };
        String[] result = new String[common.length + extras.length];
        System.arraycopy(common, 0, result, 0, common.length);
        System.arraycopy(extras, 0, result, common.length, extras.length);
        return result;
    }

    private Spec factory(String address, String name, String family, String ids, String vtables, DataType voidPtr, DataType intType) throws Exception {
        return new Spec(address, name, "__cdecl", voidPtr,
            "Hardened PhysicsScript " + family + " factory: allocates 8-byte nodes for valueType ids " + ids +
            " and installs vtables " + vtables + ". Exact value semantics, class layouts, and runtime script behavior remain unproven.",
            tags("value-factory", family),
            new String[] {fun(address), name},
            false,
            new ParameterImpl[] {param("valueType", intType)});
    }

    private Spec leafDtor(String address, String name, String baseName, String family, DataType voidPtr, DataType intType, String... previous) throws Exception {
        return new Spec(address, name, "__thiscall", voidPtr,
            "Shared scalar-deleting destructor wrapper for PhysicsScript " + family + " leaf vtables: calls " +
            baseName + " and optionally frees this through OID__FreeObject when flags bit 0 is set. Runtime behavior remains unproven.",
            tags("destructor", "shared-vtable-slot", family),
            previous,
            true,
            new ParameterImpl[] {param("this", voidPtr), param("flags", intType)});
    }

    private Spec baseDtor(String address, String name, String vtable, String family, DataType voidPtr, DataType intType, String... previous) throws Exception {
        return new Spec(address, name, "__thiscall", voidPtr,
            "Recovered base scalar-deleting destructor wrapper for PhysicsScript " + family +
            ": restores base vtable " + vtable + " and optionally frees this through OID__FreeObject. Created from vtable read-back; class layout remains unproven.",
            tags("destructor", "function-boundary", family),
            previous,
            true,
            new ParameterImpl[] {param("this", voidPtr), param("flags", intType)});
    }

    private Spec dtorBase(String address, String name, String vtable, String family, DataType voidType, DataType voidPtr, String... previous) throws Exception {
        return new Spec(address, name, "__fastcall", voidType,
            "Destructor base body for PhysicsScript " + family + ": restores base vtable " + vtable +
            ". Corrects earlier constructor-like naming; exact class layout remains unproven.",
            tags("destructor", "value-base", family),
            previous,
            false,
            new ParameterImpl[] {param("this", voidPtr)});
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");
        println("Mode: " + (dryRun ? "dry" : "apply"));

        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);
        DataType intType = IntegerDataType.dataType;

        Spec[] specs = new Spec[] {
            factory("0x0043dcd0", "CPhysicsScriptStatements__CreateStatementType11", "type-11-seek", "1..3", "0x005daafc, 0x005dab08, 0x005dab14", voidPtr, intType),
            baseDtor("0x0043dd60", "CPhysicsSeekType__scalar_deleting_dtor", "0x005dab20", "type-11-seek", voidPtr, intType, fun("0x0043dd60")),
            leafDtor("0x0043dd90", "CPhysicsSeekTypeLeaf__shared_scalar_deleting_dtor", "CPhysicsSeekType__dtor_base", "type-11-seek", voidPtr, intType, "VFuncSlot_00_0043dd90"),
            dtorBase("0x0043ddb0", "CPhysicsSeekType__dtor_base", "0x005dab20", "type-11-seek", voidType, voidPtr, "CPhysicsSeekType__ctor_like_0043ddb0"),

            factory("0x0043ddc0", "CPhysicsScriptStatements__CreateStatementType12", "type-12-behaviour", "0x1..0x19", "0x005dab2c through 0x005dac4c", voidPtr, intType),
            leafDtor("0x0043e2b0", "CPhysicsBehaviourTypeLeaf__shared_scalar_deleting_dtor", "CPhysicsBehaviourType__dtor_base", "type-12-behaviour", voidPtr, intType, fun("0x0043e2b0")),
            baseDtor("0x0043e2d0", "CPhysicsBehaviourType__scalar_deleting_dtor", "0x005dac58", "type-12-behaviour", voidPtr, intType, fun("0x0043e2d0")),
            dtorBase("0x0043e300", "CPhysicsBehaviourType__dtor_base", "0x005dac58", "type-12-behaviour", voidType, voidPtr, "CPhysicsBehaviourType__ctor_like_0043e300"),

            factory("0x0043e310", "CPhysicsScriptStatements__CreateStatementType13", "type-13-alligence", "1..3", "0x005dac64, 0x005dac70, 0x005dac7c", voidPtr, intType),
            leafDtor("0x0043e3a0", "CPhysicsAlligenceTypeLeaf__shared_scalar_deleting_dtor", "CPhysicsAlligenceType__dtor_base", "type-13-alligence", voidPtr, intType, "VFuncSlot_00_0043e3a0"),
            dtorBase("0x0043e3c0", "CPhysicsAlligenceType__dtor_base", "0x005dac88", "type-13-alligence", voidType, voidPtr, "CPhysicsAlligenceType__ctor_like_0043e3c0"),
            baseDtor("0x0043e3d0", "CPhysicsAlligenceType__scalar_deleting_dtor", "0x005dac88", "type-13-alligence", voidPtr, intType, fun("0x0043e3d0")),

            factory("0x0043e400", "CPhysicsScriptStatements__CreateStatementType14", "type-14-navmap", "1..4", "0x005dac94, 0x005daca0, 0x005dacac, 0x005dacb8", voidPtr, intType),
            leafDtor("0x0043e4e0", "CPhysicsNavMapTypeLeaf__shared_scalar_deleting_dtor", "CPhysicsNavMapType__dtor_base", "type-14-navmap", voidPtr, intType, "VFuncSlot_00_0043e4e0"),
            baseDtor("0x0043e500", "CPhysicsNavMapType__scalar_deleting_dtor", "0x005dacc4", "type-14-navmap", voidPtr, intType, fun("0x0043e500")),
            dtorBase("0x0043e530", "CPhysicsNavMapType__dtor_base", "0x005dacc4", "type-14-navmap", voidType, voidPtr, "CPhysicsNavMapType__ctor_like_0043e530"),

            factory("0x0043e540", "CPhysicsScriptStatements__CreateStatementType15", "type-15-state", "1..3", "0x005dacd0, 0x005dacdc, 0x005dace8", voidPtr, intType),
            leafDtor("0x0043e5d0", "CPhysicsStateTypeLeaf__shared_scalar_deleting_dtor", "CPhysicsStateType__dtor_base", "type-15-state", voidPtr, intType, "VFuncSlot_00_0043e5d0"),
            baseDtor("0x0043e5f0", "CPhysicsStateType__scalar_deleting_dtor", "0x005dacf4", "type-15-state", voidPtr, intType, fun("0x0043e5f0")),
            dtorBase("0x0043e620", "CPhysicsStateType__dtor_base", "0x005dacf4", "type-15-state", voidType, voidPtr, "CPhysicsStateType__ctor_like_0043e620"),

            new Spec("0x0043e630", "CFlexArray__SkipBytesFromMemBuffer", "__cdecl", voidType,
                "Skips byteCount bytes by repeatedly reading one byte from memBuffer through CDXMemBuffer__Read. Kept as adjacent shared serialization helper; exact caller data shape remains unproven.",
                tags("shared-serialization", "byte-skip-helper"),
                new String[] {"CFlexArray__SkipBytesFromMemBuffer"},
                false,
                new ParameterImpl[] {param("memBuffer", voidPtr), param("byteCount", intType)})
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
                println("FAIL: " + spec.address + " " + spec.name + " -> " + ex.getMessage());
            }
        }
        println("SUMMARY: targets=" + specs.length + " changed_or_would_change=" + changed + " failed=" + failed);
        if (failed != 0) {
            throw new IllegalStateException("Failed target count: " + failed);
        }
    }
}
