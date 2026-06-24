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

public class ApplyUnitAIDeploySignatureCorrection extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final String comment;
        final String[] previousNames;
        final ParameterImpl[] parameters;

        Spec(
                String address,
                String name,
                String callingConvention,
                DataType returnType,
                String comment,
                String[] previousNames,
                ParameterImpl[] parameters) {
            this.address = address;
            this.name = name;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.comment = comment;
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
        println("OK: " + spec.address + " " + spec.name + " -> " + fn.getSignature().toString());
        return needsRename;
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
            new Spec("0x00415140", "CUnitAI__HandleLandedStateTransition", "__fastcall", voidType,
                "Name/signature correction: CUnitAI landed-state transition emits the landed trace once, clears transient field +0x12c, dispatches vfunc slots +0x110/+0x100 and optional +0x148, then sets landed-state flag +0x264 to 1. Exact source identity, concrete layout, runtime AI behavior, and rebuild parity remain unproven.",
                new String[] {"CUnitAI__HandleLandedStateTransition_00415140"},
                new ParameterImpl[] {param("unitAI", voidPtr)}),
            new Spec("0x00415780", "CUnitAI__PlayDeployingAnimationIfState0", "__fastcall", voidType,
                "Signature/comment correction: CUnitAI deploy helper plays the deploying animation when deploy state +0x260 is 0, dispatches the animation index through vfunc slot +0xf0, and advances +0x260 to 1. Exact source identity, animation table layout, runtime AI behavior, and rebuild parity remain unproven.",
                new String[] {},
                new ParameterImpl[] {param("unitAI", voidPtr)}),
            new Spec("0x004157c0", "CUnitAI__PlayUndeployingAnimation", "__fastcall", voidType,
                "Signature/comment correction: CUnitAI undeploy helper clears deploy timer/state field +0x1f0, resolves the undeploying animation, and dispatches the animation index through vfunc slot +0xf0. Exact source identity, animation table layout, runtime AI behavior, and rebuild parity remain unproven.",
                new String[] {},
                new ParameterImpl[] {param("unitAI", voidPtr)}),
            new Spec("0x00415970", "CUnitAI__HandleDeployUndeployAnimationCompletion", "__fastcall", intType,
                "Signature/comment correction: CUnitAI completion helper compares the current animation index against deploying and undeploying, transitions to deployed/normal animations, updates +0x1f0 or +0x260, and otherwise falls back to CUnitAI__HandleDeployAndFireAnimationCompletion. Exact source identity, animation table layout, runtime AI behavior, and rebuild parity remain unproven.",
                new String[] {},
                new ParameterImpl[] {param("unitAI", voidPtr)}),
            new Spec("0x00415a50", "CUnitAI__CanCompleteDeployUndeployTransition", "__fastcall", intType,
                "Signature/comment correction: CUnitAI transition predicate blocks while vfunc slot +0x10c is active, then checks target/flag gates at +0x168, +0x214, and flag byte +0x2c before allowing deploy/undeploy completion. Exact source identity, concrete layout, runtime AI behavior, and rebuild parity remain unproven.",
                new String[] {},
                new ParameterImpl[] {param("unitAI", voidPtr)})
        };

        int updated = 0;
        int skipped = 0;
        int renamed = 0;
        for (Spec spec : specs) {
            boolean didRename = applySpec(spec, dryRun);
            if (dryRun) {
                skipped++;
            }
            else {
                updated++;
                if (didRename) {
                    renamed++;
                }
            }
        }

        println("--- SUMMARY ---");
        println("updated=" + updated + " skipped=" + skipped + " renamed=" + renamed + " missing=0 bad=0");
    }
}
