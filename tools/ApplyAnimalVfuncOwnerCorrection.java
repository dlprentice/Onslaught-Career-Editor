//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.ByteDataType;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

public class ApplyAnimalVfuncOwnerCorrection extends GhidraScript {

    private static class ParamSpec {
        final String name;
        final DataType dataType;

        ParamSpec(String name, DataType dataType) {
            this.name = name;
            this.dataType = dataType;
        }
    }

    private static class Target {
        final String address;
        final String newName;
        final String callingConvention;
        final DataType returnType;
        final String comment;
        final ParamSpec[] params;

        Target(String address, String newName, String callingConvention, DataType returnType, String comment, ParamSpec[] params) {
            this.address = address;
            this.newName = newName;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.comment = comment;
            this.params = params;
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

    private ParameterImpl toParam(ParamSpec spec) throws Exception {
        return new ParameterImpl(spec.name, spec.dataType, currentProgram);
    }

    private String expectedParamText(Target target) {
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < target.params.length; i++) {
            if (i > 0) {
                sb.append(", ");
            }
            sb.append(target.params[i].dataType.getDisplayName()).append(" ").append(target.params[i].name);
        }
        return sb.toString();
    }

    private void applyTarget(Target target, boolean dryRun) throws Exception {
        Function fn = getFunctionOrThrow(target.address);
        ParameterImpl[] params = new ParameterImpl[target.params.length];
        for (int i = 0; i < target.params.length; i++) {
            params[i] = toParam(target.params[i]);
        }

        if (dryRun) {
            println("DRY: " + target.address + " " + fn.getName() + " -> " +
                target.returnType.getDisplayName() + " " + target.callingConvention + " " + target.newName +
                "(" + expectedParamText(target) + ")");
            return;
        }

        if (!fn.getName().equals(target.newName)) {
            fn.setName(target.newName, SourceType.USER_DEFINED);
        }
        fn.setCallingConvention(target.callingConvention);
        fn.setReturnType(target.returnType, SourceType.USER_DEFINED);
        fn.replaceParameters(
            FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS,
            true,
            SourceType.USER_DEFINED,
            params
        );
        fn.setComment(target.comment);

        Function readBack = getFunctionOrThrow(target.address);
        if (!readBack.getName().equals(target.newName)) {
            throw new IllegalStateException("Read-back name mismatch at " + target.address);
        }
        String signature = readBack.getSignature().toString();
        if (!signature.contains(target.callingConvention) || !signature.contains(target.newName)) {
            throw new IllegalStateException("Read-back signature mismatch at " + target.address + ": " + signature);
        }
        for (ParamSpec param : target.params) {
            String token = param.dataType.getDisplayName() + " " + param.name;
            if (!signature.contains(token)) {
                throw new IllegalStateException("Read-back signature missing param at " + target.address + ": " + token + " in " + signature);
            }
        }
        String comment = readBack.getComment();
        if (comment == null || comment.trim().isEmpty()) {
            throw new IllegalStateException("Read-back comment missing at " + target.address);
        }
        println("OK: " + target.address + " " + target.newName + " -> " + signature);
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");
        println("Mode: " + (dryRun ? "dry" : "apply"));

        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);
        DataType byteType = ByteDataType.dataType;

        Target[] targets = new Target[] {
            new Target(
                "0x00403d30",
                "CAnimal__Init",
                "__thiscall",
                voidType,
                "CAnimal init correction: CAnimal RTTI/vtable slot 9 points here. Copies init transform/vector state, handles type from init+0x3bc, uses bird_msh for type 1, creates the model/resource object, delegates to CComplexThing__Init, links the animal list, and schedules event 3000 when active. Exact source virtual name and concrete CAnimal/CAnimalInitThing layout remain provisional.",
                new ParamSpec[] {
                    new ParamSpec("this", voidPtr),
                    new ParamSpec("init", voidPtr),
                }
            ),
            new Target(
                "0x00404010",
                "CAnimal__dtor_base",
                "__fastcall",
                voidType,
                "CAnimal destructor-base correction: resets CAnimal vtable 0x005d8698, clears linked animal-list references through DAT_00660130/DAT_00660134, then delegates to CComplexThing__dtor_base. Corrects the stale CAtmospheric__Destructor label; runtime side-effect completeness and concrete layout remain provisional.",
                new ParamSpec[] {
                    new ParamSpec("this", voidPtr),
                }
            ),
            new Target(
                "0x004041f0",
                "CAnimal__scalar_deleting_dtor",
                "__thiscall",
                voidPtr,
                "CAnimal scalar-deleting destructor: calls CAnimal__dtor_base, optionally frees this when flags&1, and returns this. Corrects the generic vfunc slot label; allocator ownership and destructor completeness remain provisional.",
                new ParamSpec[] {
                    new ParamSpec("this", voidPtr),
                    new ParamSpec("flags", byteType),
                }
            ),
        };

        int updated = 0;
        int skipped = 0;
        for (Target target : targets) {
            applyTarget(target, dryRun);
            if (dryRun) {
                skipped++;
            } else {
                updated++;
            }
        }

        println("--- SUMMARY ---");
        println("updated=" + updated + " skipped=" + skipped + " missing=0 bad=0");
    }
}
