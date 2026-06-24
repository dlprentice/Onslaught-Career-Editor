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

public class ApplyPhysicsScriptStatementTranche3 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final String comment;
        final String[] tags;
        final String[] previousNames;
        final ParameterImpl[] parameters;

        Spec(
                String address,
                String name,
                String callingConvention,
                DataType returnType,
                String comment,
                String[] tags,
                String[] previousNames,
                ParameterImpl[] parameters) {
            this.address = address;
            this.name = name;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.comment = comment;
            this.tags = tags;
            this.previousNames = previousNames;
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

    private Function getFunctionOrThrow(String addrText) throws Exception {
        if (!addrText.startsWith("0x") && !addrText.startsWith("0X")) {
            addrText = "0x" + addrText;
        }
        Address addr = toAddr(addrText);
        if (addr == null) {
            throw new IllegalArgumentException("Bad address: " + addrText);
        }
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
        if (spec.parameters.length == 0) {
            sb.append("void");
        }
        sb.append(")");
        return sb.toString();
    }

    private boolean applySpec(Spec spec, boolean dryRun) throws Exception {
        Function fn = getFunctionOrThrow(spec.address);
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

        Function readBack = getFunctionOrThrow(spec.address);
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
            "physics-script-wave333",
            "physics-script",
            "statement-tranche",
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
            new Spec("0x00431290", "CComponentStatement__scalar_deleting_dtor", "__thiscall", voidPtr,
                "Name/signature correction: scalar-deleting destructor wrapper for CComponentStatement; it calls CComponentStatement__dtor, tests the scalar-delete flag, optionally calls OID__FreeObject, and returns this. Exact class hierarchy and runtime lifetime behavior remain unproven.",
                tags("destructor"),
                new String[] {"CComponentStatement__VFunc_00_00431290"},
                new ParameterImpl[] {param("this", voidPtr), param("flags", intType)}),
            new Spec("0x004312b0", "CComponentStatement__dtor", "__fastcall", voidType,
                "Name/signature correction: CComponentStatement destructor body sets the derived vtable, deletes the child pointer at +0x10c through vtable slot 0 when present, then restores the CPhysicsScriptStatement base vtable. Exact layout and runtime lifetime behavior remain unproven.",
                tags("destructor"),
                new String[] {"CComponentStatement__ctor_like_004312b0"},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x00431310", "CFeatureStatement__CreateFeatureAndRecurse", "__fastcall", voidType,
                "Name/signature correction: CFeatureStatement vtable slot +0x4 body creates/registers feature data from the statement name, then propagates that context through child statement slot +0x4/list traversal. Exact statement layout, feature data layout, runtime physics behavior, and rebuild parity remain unproven.",
                tags("statement-update"),
                new String[] {"CFeatureStatement__VFunc_01_00431310"},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x00431350", "CFeatureStatement__CreateAndRegisterByName", "__cdecl", voidType,
                "Name/signature correction: creates a 0x24 feature-like record by name, stores the copied name pointer, initializes default feature fields, and appends it to DAT_00855404. Exact class layout, source identity, runtime feature behavior, and rebuild parity remain unproven.",
                tags("physics-object-registry"),
                new String[] {"CFeatureStatement__AllocObjectAndAddToSet"},
                new ParameterImpl[] {param("name", charPtr)}),
            new Spec("0x00431420", "CFeatureStatement__GetSerializedSize", "__fastcall", intType,
                "Boundary/signature correction: recovered missing top-level CFeatureStatement serialized-size body. It counts the statement name string, includes the first feature value-list node payload size, and recursively adds chained value-list sizes. Exact serialized format completeness, concrete statement layout, and rebuild parity remain unproven.",
                tags("statement-boundary", "serialized-size"),
                new String[] {},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x00431470", "CPhysicsFeatureValueList__GetSerializedSize", "__fastcall", intType,
                "Name/signature correction: recursive CPhysicsFeatureValueList serialized-size helper, not a UnitAI recursive-node helper or top-level feature statement size body. It adds child statement slot +0x8 size and recurses through next value-list nodes. Exact node layout and rebuild parity remain unproven.",
                tags("value-list", "serialized-size"),
                new String[] {"CUnitAI__ComputeRecursiveNodeSize_NodeTreeB"},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x004314a0", "CFeatureStatement__LoadFromMemBuffer", "__thiscall", voidType,
                "Boundary/signature correction: recovered missing CFeatureStatement load body. It reads the statement name from CDXMemBuffer, creates the first CPhysicsFeatureValueList node, dispatches CreateStatementType8 load slot +0xc when available, skips unknown payload bytes otherwise, and handles recursive value-list loading. Exact file format, layout, and runtime behavior remain unproven.",
                tags("statement-boundary", "statement-load"),
                new String[] {},
                new ParameterImpl[] {param("this", voidPtr), param("memBuffer", voidPtr)}),
            new Spec("0x004315c0", "CPhysicsFeatureValueList__LoadFromMemBuffer", "__thiscall", voidType,
                "Name/signature correction: CPhysicsFeatureValueList node load helper reads child statement type and serialized size, dispatches CreateStatementType8 load slot +0xc when present, skips unknown payload bytes otherwise, and recursively loads the next node when the terminator permits. Exact node layout and rebuild parity remain unproven.",
                tags("value-list", "statement-load"),
                new String[] {"CPhysicsFeatureValueList__ctor_like_004315c0"},
                new ParameterImpl[] {param("this", voidPtr), param("memBuffer", voidPtr)}),
            new Spec("0x004316a0", "CPhysicsFeatureValueList__scalar_deleting_dtor", "__thiscall", voidPtr,
                "Name/signature correction: scalar-deleting destructor wrapper for CPhysicsFeatureValueList nodes; it destroys child and next-node links through vtable slot 0, tests the scalar-delete flag, optionally calls OID__FreeObject, and returns this. Exact class layout and runtime lifetime behavior remain unproven.",
                tags("value-list", "destructor"),
                new String[] {"CPhysicsFeatureValueList__VFunc_00_004316a0"},
                new ParameterImpl[] {param("this", voidPtr), param("flags", intType)}),
            new Spec("0x004316e0", "CFeatureStatement__scalar_deleting_dtor", "__thiscall", voidPtr,
                "Name/signature correction: scalar-deleting destructor wrapper for CFeatureStatement; it calls CFeatureStatement__dtor, tests the scalar-delete flag, optionally calls OID__FreeObject, and returns this. Exact class hierarchy and runtime lifetime behavior remain unproven.",
                tags("destructor"),
                new String[] {"CFeatureStatement__VFunc_00_004316e0"},
                new ParameterImpl[] {param("this", voidPtr), param("flags", intType)}),
            new Spec("0x00431700", "CFeatureStatement__dtor", "__fastcall", voidType,
                "Name/signature correction: CFeatureStatement destructor body sets the derived vtable, deletes the child pointer at +0x10c through vtable slot 0 when present, then restores the CPhysicsScriptStatement base vtable. Exact layout and runtime lifetime behavior remain unproven.",
                tags("destructor"),
                new String[] {"CFeatureStatement__ctor_like_00431700"},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x00431760", "CHazardStatement__CreateHazardAndRecurse", "__fastcall", voidType,
                "Name/signature correction: CHazardStatement vtable slot +0x4 body creates/registers hazard data from the statement name, then propagates that context through child statement slot +0x4/list traversal. Exact statement layout, hazard data layout, runtime physics behavior, and rebuild parity remain unproven.",
                tags("statement-update"),
                new String[] {"CHazardStatement__VFunc_01_00431760"},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x004317a0", "CHazardStatement__CreateAndRegisterByName", "__cdecl", voidType,
                "Name/signature correction: creates a 0x1c hazard-like record by name, stores the copied name pointer, initializes default hazard fields including a 1.0 scalar, and appends it to DAT_00855408. Exact class layout, source identity, runtime hazard behavior, and rebuild parity remain unproven.",
                tags("physics-object-registry"),
                new String[] {"CHazardStatement__AllocObjectAndAddToSet"},
                new ParameterImpl[] {param("name", charPtr)}),
            new Spec("0x00431870", "CHazardStatement__GetSerializedSize", "__fastcall", intType,
                "Boundary/signature correction: recovered missing top-level CHazardStatement serialized-size body. It counts the statement name string, includes the first hazard value-list node payload size, and recursively adds chained value-list sizes. Exact serialized format completeness, concrete statement layout, and rebuild parity remain unproven.",
                tags("statement-boundary", "serialized-size"),
                new String[] {},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x004318c0", "CPhysicsHazardValueList__GetSerializedSize", "__fastcall", intType,
                "Name/signature correction: recursive CPhysicsHazardValueList serialized-size helper, not a UnitAI recursive-node helper or top-level hazard statement size body. It adds child statement slot +0x8 size and recurses through next value-list nodes. Exact node layout and rebuild parity remain unproven.",
                tags("value-list", "serialized-size"),
                new String[] {"CUnitAI__ComputeRecursiveNodeSize_NodeTreeC"},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x004318f0", "CHazardStatement__LoadFromMemBuffer", "__thiscall", voidType,
                "Boundary/signature correction: recovered missing CHazardStatement load body. It reads the statement name from CDXMemBuffer, creates the first CPhysicsHazardValueList node, dispatches CreateStatementType9 load slot +0xc when available, skips unknown payload bytes otherwise, and handles recursive value-list loading. Exact file format, layout, and runtime behavior remain unproven.",
                tags("statement-boundary", "statement-load"),
                new String[] {},
                new ParameterImpl[] {param("this", voidPtr), param("memBuffer", voidPtr)}),
            new Spec("0x00431a10", "CPhysicsHazardValueList__LoadFromMemBuffer", "__thiscall", voidType,
                "Name/signature correction: CPhysicsHazardValueList node load helper reads child statement type and serialized size, dispatches CreateStatementType9 load slot +0xc when present, skips unknown payload bytes otherwise, and recursively loads the next node when the terminator permits. Exact node layout and rebuild parity remain unproven.",
                tags("value-list", "statement-load"),
                new String[] {"CPhysicsHazardValueList__ctor_like_00431a10"},
                new ParameterImpl[] {param("this", voidPtr), param("memBuffer", voidPtr)}),
            new Spec("0x00431af0", "CPhysicsHazardValueList__scalar_deleting_dtor", "__thiscall", voidPtr,
                "Name/signature correction: scalar-deleting destructor wrapper for CPhysicsHazardValueList nodes; it destroys child and next-node links through vtable slot 0, tests the scalar-delete flag, optionally calls OID__FreeObject, and returns this. Exact class layout and runtime lifetime behavior remain unproven.",
                tags("value-list", "destructor"),
                new String[] {"CPhysicsHazardValueList__VFunc_00_00431af0"},
                new ParameterImpl[] {param("this", voidPtr), param("flags", intType)}),
            new Spec("0x00431b30", "CHazardStatement__scalar_deleting_dtor", "__thiscall", voidPtr,
                "Name/signature correction: scalar-deleting destructor wrapper for CHazardStatement; it calls CHazardStatement__dtor, tests the scalar-delete flag, optionally calls OID__FreeObject, and returns this. Exact class hierarchy and runtime lifetime behavior remain unproven.",
                tags("destructor"),
                new String[] {"CHazardStatement__VFunc_00_00431b30"},
                new ParameterImpl[] {param("this", voidPtr), param("flags", intType)}),
            new Spec("0x00431b50", "CHazardStatement__dtor", "__fastcall", voidType,
                "Name/signature correction: CHazardStatement destructor body sets the derived vtable, deletes the child pointer at +0x10c through vtable slot 0 when present, then restores the CPhysicsScriptStatement base vtable. Exact layout and runtime lifetime behavior remain unproven.",
                tags("destructor"),
                new String[] {"CHazardStatement__ctor_like_00431b50"},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x00431bb0", "CPhysicsScriptStatements__CreateStatementType2", "__cdecl", voidPtr,
                "Signature/comment/tag hardening: factory for PhysicsScript type-2/unit value records; it switches over value type ids through 0x46, allocates typed value objects, assigns value vtables, and returns null for unsupported ids. Exact value class names, complete layout, source identity, runtime behavior, and rebuild parity remain unproven.",
                tags("value-factory"),
                new String[] {},
                new ParameterImpl[] {param("valueType", intType)}),
        };

        int changedNames = 0;
        for (Spec spec : specs) {
            if (monitor.isCancelled()) {
                break;
            }
            if (applySpec(spec, dryRun)) {
                changedNames++;
            }
        }

        println("ApplyPhysicsScriptStatementTranche3 complete: mode=" + (dryRun ? "dry" : "apply") +
            " targets=" + specs.length +
            " changedNames=" + changedNames);
    }
}
