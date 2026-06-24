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

public class ApplyAtmosphericsLifecycleSignatureTranche extends GhidraScript {

    private static class Target {
        final String address;
        final String expectedName;
        final String callingConvention;
        final DataType returnType;
        final String comment;
        final ParameterImpl[] params;

        Target(
                String address,
                String expectedName,
                String callingConvention,
                DataType returnType,
                String comment,
                ParameterImpl... params) {
            this.address = address;
            this.expectedName = expectedName;
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

    private ParameterImpl param(String name, DataType dataType) throws Exception {
        return new ParameterImpl(name, dataType, currentProgram);
    }

    private String expectedSignature(Target target) {
        StringBuilder sb = new StringBuilder();
        sb.append(target.returnType.getDisplayName()).append(" ").append(target.callingConvention).append(" ");
        sb.append(target.expectedName).append("(");
        for (int i = 0; i < target.params.length; i++) {
            if (i > 0) {
                sb.append(", ");
            }
            sb.append(target.params[i].getDataType().getDisplayName()).append(" ").append(target.params[i].getName());
        }
        sb.append(")");
        return sb.toString();
    }

    private void applyTarget(Target target, boolean dryRun) throws Exception {
        Function fn = getFunctionOrThrow(target.address);
        if (!fn.getName().equals(target.expectedName)) {
            throw new IllegalStateException(
                "Unexpected function name at " + target.address + ": " + fn.getName() + " != " + target.expectedName);
        }

        if (dryRun) {
            println("DRY: " + target.address + " " + target.expectedName + " -> " + expectedSignature(target));
            return;
        }

        fn.setCallingConvention(target.callingConvention);
        fn.setReturnType(target.returnType, SourceType.USER_DEFINED);
        fn.replaceParameters(
            FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS,
            true,
            SourceType.USER_DEFINED,
            target.params
        );
        fn.setComment(target.comment);
        println("OK: " + target.address + " " + target.expectedName + " -> " + fn.getSignature().toString());
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");
        println("Mode: " + (dryRun ? "dry" : "apply"));

        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);
        DataType intType = IntegerDataType.dataType;

        Target[] targets = new Target[] {
            new Target(
                "0x004046d0",
                "CAtmospheric__Constructor",
                "__thiscall",
                voidPtr,
                "Signature/comment correction for CAtmospheric constructor. Corrects the prior float parameter: CThing__AddTrail passes the owning thing pointer, the constructor stores that dword at +0x20, behavior helpers later use +0x20 as the sampler/owner pointer, and event 3000 is scheduled. Concrete layout, exact source identity, and runtime behavior remain unproven.",
                param("this", voidPtr),
                param("ownerThing", voidPtr)
            ),
            new Target(
                "0x00404a00",
                "Atmospherics__Init",
                "__cdecl",
                voidType,
                "Signature/comment hardening for global Atmospherics init. Evidence zeroes wind/density globals, loads the snow layer texture, allocates profile/cloud objects, and registers the ListAtmospherics command plus atm_* console variables. Concrete global layout, exact source identity, and runtime behavior remain unproven."
            ),
            new Target(
                "0x00404b90",
                "Atmospherics__ResetAndUpdate",
                "__cdecl",
                voidType,
                "Signature/comment hardening for global Atmospherics reset/update. Evidence clears the prevailing wind vector globals and walks the atmospheric list at DAT_006601a8, dispatching the +0xc virtual slot. Concrete vtable names, list layout, and runtime behavior remain unproven."
            ),
            new Target(
                "0x00404bd0",
                "Atmospherics__UpdateAll",
                "__cdecl",
                voidType,
                "Signature/comment hardening for global Atmospherics update-all helper. Evidence walks the atmospheric list at DAT_006601a8 and dispatches each entry's +0x8 virtual slot. Concrete vtable names, list layout, and runtime behavior remain unproven."
            ),
            new Target(
                "0x00404bf0",
                "Atmospherics__RenderAll",
                "__cdecl",
                voidType,
                "Signature/comment hardening for global Atmospherics render-all helper. Evidence walks the atmospheric list at DAT_006601a8 and dispatches each entry's +0x4 virtual slot. Concrete vtable names, list layout, and runtime behavior remain unproven."
            ),
            new Target(
                "0x00404c10",
                "Atmospherics__Shutdown",
                "__cdecl",
                voidType,
                "Signature/comment hardening for global Atmospherics shutdown. Evidence releases the cached snow texture handle, walks DAT_006601a8, dispatches the +0x10 virtual slot, unlinks entries, and frees objects. Concrete ownership/layout and runtime behavior remain unproven."
            ),
            new Target(
                "0x00404c90",
                "Atmospherics__NotifyAll",
                "__cdecl",
                voidType,
                "Signature/comment hardening for global Atmospherics notify helper. Evidence walks DAT_006601a8 and dispatches the +0x14 virtual slot with eventCode. Concrete event semantics, vtable names, list layout, and runtime behavior remain unproven.",
                param("eventCode", intType)
            ),
            new Target(
                "0x004f44a0",
                "CThing__AddTrail",
                "__thiscall",
                voidType,
                "Signature/comment correction for CThing trail setup. Evidence checks this+0x6c, allocates a 0x24-byte CAtmospheric when missing, passes this to CAtmospheric__Constructor, stores the result back at +0x6c, then calls CAtmospheric__ConfigureTrail with samplerIndex/resetBlendPosition/blendMode; ret 0xc confirms three stack arguments. Concrete CThing layout and runtime trail behavior remain unproven.",
                param("this", voidPtr),
                param("samplerIndex", intType),
                param("resetBlendPosition", intType),
                param("blendMode", intType)
            )
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
