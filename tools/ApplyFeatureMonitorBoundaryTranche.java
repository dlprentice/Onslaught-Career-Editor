//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.BooleanDataType;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

public class ApplyFeatureMonitorBoundaryTranche extends GhidraScript {
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

    private Function getOrCreate(Address address, String name, boolean dryRun) throws Exception {
        Function fn = existingFunction(address);
        if (fn != null) {
            return fn;
        }
        if (dryRun) {
            return null;
        }

        disassemble(address);
        fn = createFunction(address, name);
        if (fn == null) {
            fn = existingFunction(address);
        }
        if (fn == null) {
            throw new IllegalStateException("Function create failed at " + address);
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
        Address address = addr(spec.address);
        Function fn = getOrCreate(address, spec.name, dryRun);
        if (fn == null) {
            println("DRY: " + spec.address + " <missing> -> create " + signatureText(spec));
            return true;
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

        Function readBack = existingFunction(address);
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
            "feature-monitor-boundary-wave369",
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
        DataType boolType = BooleanDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec("0x0044dfb0", "FenrirEffects__InitBurningAndEngineHandles_0044dfb0", "__thiscall", voidType,
                "Recovered function boundary from data/vtable slot context: initializes fields around +0x27c/+0x280, calls the shared init helper with one stack argument, and resolves the Fenrir Inside Burning and Fenrir Engines effect strings into object fields. Static retail evidence only; exact owner class, source identity, concrete layout, runtime effect behavior, and rebuild parity remain unproven.",
                tags("function-boundary", "fenrir-effects", "owner-deferred"),
                new ParameterImpl[] {param("this", voidPtr), param("initOrContext", voidPtr)}),

            new Spec("0x0044e4e0", "PickupSpawn__UpdateAttachedPickupBurst_0044e4e0", "__fastcall", voidType,
                "Recovered function boundary from adjacent pickup-spawn context: calls transform/animation virtual slots through this+0x08 and this+0x30, conditionally calls CThing-style helper 0x004b24d0, then invokes PickupSpawn__MaybeSpawnAttachedPickupFromFrame_0044e300 twice. Static retail evidence only; exact owner class, source identity, concrete layout, runtime pickup behavior, and rebuild parity remain unproven.",
                tags("function-boundary", "pickup-spawn", "owner-deferred"),
                new ParameterImpl[] {param("object", voidPtr)}),

            new Spec("0x0044e550", "GlobalCallback__ClearMatrixBlock006776E8", "__cdecl", voidType,
                "Recovered zero-argument callback boundary from table 0x00622230: clears the three dwords at 0x006776e8, 0x006776ec, and 0x006776f0, then returns. Static retail evidence only; exact owner table, source identity, matrix semantics, runtime behavior, and rebuild parity remain unproven.",
                tags("function-boundary", "global-callback", "matrix-block"),
                new ParameterImpl[] {}),

            new Spec("0x0044e570", "GlobalCallback__InitMatrixBlock006776B8", "__cdecl", voidType,
                "Recovered zero-argument callback boundary from table 0x00622230: writes a matrix-like block spanning 0x006776b8 through 0x006776e4 using 1.0 and zero constants plus stack-sourced slots, then returns. Static retail evidence only; exact owner table, source identity, concrete matrix layout, runtime behavior, and rebuild parity remain unproven.",
                tags("function-boundary", "global-callback", "matrix-block"),
                new ParameterImpl[] {}),

            new Spec("0x0044e640", "ComponentTargeting__ScanListsAndMaybeTriggerAction_0044e640", "__fastcall", boolType,
                "Recovered owner-deferred function boundary from data slot 0x005d96ac: scans global list heads selected from object state, compares candidate positions/ranges against the owner object at this+0x08, uses vector-distance helper calls, and conditionally dispatches action helper 0x004ffdd0 before returning a boolean-like result. Static retail evidence only; exact owner class, source identity, concrete target-list layout, runtime behavior, and rebuild parity remain unproven.",
                tags("function-boundary", "component-targeting", "owner-deferred"),
                new ParameterImpl[] {param("this", voidPtr)}),

            new Spec("0x0044e9c0", "GlobalCallback__ClearMatrixBlock00677768", "__cdecl", voidType,
                "Recovered zero-argument callback boundary from table 0x00622230: clears the three dwords at 0x00677768, 0x0067776c, and 0x00677770, then returns. Static retail evidence only; exact owner table, source identity, matrix semantics, runtime behavior, and rebuild parity remain unproven.",
                tags("function-boundary", "global-callback", "matrix-block"),
                new ParameterImpl[] {}),

            new Spec("0x0044e9e0", "GlobalCallback__InitMatrixBlock00677738", "__cdecl", voidType,
                "Recovered zero-argument callback boundary from table 0x00622230: writes a matrix-like block spanning 0x00677738 through 0x00677764 using 1.0 and zero constants plus stack-sourced slots, then returns. Static retail evidence only; exact owner table, source identity, concrete matrix layout, runtime behavior, and rebuild parity remain unproven.",
                tags("function-boundary", "global-callback", "matrix-block"),
                new ParameterImpl[] {})
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
            throw new IllegalStateException("Feature/monitor boundary tranche failed for " + failed + " target(s)");
        }
    }
}
