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

public class ApplyComponentSignatureCorrection extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final String comment;
        final String[] previousNames;
        final String[] tags;
        final ParameterImpl[] parameters;

        Spec(
                String address,
                String name,
                String callingConvention,
                DataType returnType,
                String comment,
                String[] previousNames,
                String[] tags,
                ParameterImpl[] parameters) {
            this.address = address;
            this.name = name;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.comment = comment;
            this.previousNames = previousNames;
            this.tags = tags;
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
        for (String tag : spec.tags) {
            fn.addTag(tag);
        }
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
        DataType byteType = ByteDataType.dataType;
        String[] commonTags = new String[] {"static-reaudit", "component-wave324", "component-system", "signature-hardened"};
        String[] correctedDtorTags = new String[] {"static-reaudit", "component-wave324", "component-system", "signature-hardened", "owner-corrected", "destructor"};

        Spec[] specs = new Spec[] {
            new Spec("0x00427b80", "CComponent__VFunc_09_00427b80", "__thiscall", voidType,
                "Signature/comment/tag correction: init-like CComponent virtual body clears active-reader/component transform fields, initializes the config/init record, applies the Thunderhead Main Gun special case, selects Normal or Activated animation state, and clears cached state fields. Current source body is absent; exact virtual slot name, concrete layout, runtime activation behavior, and rebuild parity remain unproven.",
                new String[] {},
                commonTags,
                new ParameterImpl[] {param("this", voidPtr), param("init", voidPtr)}),
            new Spec("0x00427cd0", "CComponent__CreateSubComponent1", "__fastcall", voidType,
                "Signature/comment/tag correction: allocates a 0x14-byte Component.cpp line 0x4d helper object and stores the initialized result at this+0x70, passing this+8 when this is non-null. Exact helper class identity, field layout, ownership semantics, and rebuild parity remain unproven.",
                new String[] {},
                commonTags,
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x00427d50", "CComponent__CreateSubComponent2", "__fastcall", voidType,
                "Signature/comment/tag correction: allocates a 0x20-byte Component.cpp line 0x53 helper, initializes it through the guide constructor path, assigns the CComponentGuide vtable, and stores it at this+0x208. Exact guide layout, source method identity, runtime behavior, and rebuild parity remain unproven.",
                new String[] {},
                commonTags,
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x00427dd0", "CComponent__CreateWeaponComponent", "__thiscall", voidType,
                "Signature/comment/tag correction: weapon-component factory compares the owner/config name against Fenrir Bomb Launcher, Fenrir Main Gun, and Carrier Health Pad, allocates 0x60-byte AI/weapon components, calls CWarspite__Init, stores the result at this+0x13c, and uses the CRepairPadAI/default branch field +0x14 clear. Exact source identity, subclass layout, runtime weapon behavior, and rebuild parity remain unproven.",
                new String[] {},
                commonTags,
                new ParameterImpl[] {param("this", voidPtr), param("initOrContext", voidPtr)}),
            new Spec("0x00427f90", "CComponentBomberAI__scalar_deleting_dtor", "__thiscall", voidPtr,
                "Owner/signature/comment/tag correction: RTTI read-back resolves vtable 0x005d96b4 as CComponentBomberAI; this scalar-delete wrapper calls CComponentBomberAI__dtor_base, checks flags bit 0, optionally frees this through OID__FreeObject, and returns this. Exact source method name, allocator ownership, runtime destruction behavior, and rebuild parity remain unproven.",
                new String[] {"CComponentBomberAI__VFunc_01_00427f90"},
                correctedDtorTags,
                new ParameterImpl[] {param("this", voidPtr), param("flags", byteType)}),
            new Spec("0x00427fb0", "CComponentBomberAI__dtor_base", "__fastcall", voidType,
                "Owner/signature/comment/tag correction: destructor-base body used by the CComponentBomberAI scalar-delete wrapper resets the base CUnitAI vtable, removes linked set slots at +0x28/+0x24/+0xc through CSPtrSet__Remove, then calls CMonitor__Shutdown. Corrects the stale ctor-like label; concrete CComponentBomberAI layout, exact source identity, runtime cleanup behavior, and rebuild parity remain unproven.",
                new String[] {"CUnitAI__ctor_like_00427fb0"},
                correctedDtorTags,
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x00428050", "CFenrirMainGunAI__scalar_deleting_dtor", "__thiscall", voidPtr,
                "Owner/signature/comment/tag correction: RTTI read-back resolves vtable 0x005d9680 as CFenrirMainGunAI; this scalar-delete wrapper calls CFenrirMainGunAI__dtor_base, checks flags bit 0, optionally frees this through OID__FreeObject, and returns this. Exact source method name, allocator ownership, runtime destruction behavior, and rebuild parity remain unproven.",
                new String[] {"CFenrirMainGunAI__VFunc_01_00428050"},
                correctedDtorTags,
                new ParameterImpl[] {param("this", voidPtr), param("flags", byteType)}),
            new Spec("0x00428070", "CFenrirMainGunAI__dtor_base", "__fastcall", voidType,
                "Owner/signature/comment/tag correction: destructor-base body used by the CFenrirMainGunAI scalar-delete wrapper resets the base CUnitAI vtable, removes linked set slots at +0x28/+0x24/+0xc through CSPtrSet__Remove, then calls CMonitor__Shutdown. Corrects the stale ctor-like label; concrete CFenrirMainGunAI layout, exact source identity, runtime cleanup behavior, and rebuild parity remain unproven.",
                new String[] {"CUnitAI__ctor_like_00428070"},
                correctedDtorTags,
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x00428110", "CUnitAI__UpdateActivationStateAndSpawnPickup", "__fastcall", voidType,
                "Signature/comment/tag correction: update body handles component activation/deactivation animations via Activate and Deactivated names, crash/explosion fall checks, Gill_M_Claw_Hit pickup lookup, CWorldPhysicsManager__CreatePickup dispatch, motion/attachment update, and randomized cached-transform refresh. Current owner label remains behavior-backed but source identity, concrete layout, runtime behavior, and rebuild parity remain unproven.",
                new String[] {},
                commonTags,
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x00428500", "CUnitAI__RefreshCachedComponentTransform", "__fastcall", voidType,
                "Signature/comment/tag correction: cached Component transform refresher skips work when this+0x278 equals DAT_008a9aac, builds orientation from this+0x250/0x254, optionally reads the Component transform through the active reader, combines matrix rows, writes a Mat34 via Mat34__SetRows, then stores the current tick. Concrete layout, exact source identity, runtime transform behavior, and rebuild parity remain unproven.",
                new String[] {},
                commonTags,
                new ParameterImpl[] {param("this", voidPtr)})
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
