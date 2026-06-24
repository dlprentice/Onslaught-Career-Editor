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

public class ApplyRoundSoundValueTranche extends GhidraScript {
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
            "physics-script-wave337",
            "physics-script",
            "round-sound-value-tranche",
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
            new Spec("0x004359c0", "CPhysicsWeaponModeValue__dtor_base", "__fastcall", voidType,
                "Name/signature correction: base destructor body installs/restores the CPhysicsWeaponModeValue vtable; adjacent scalar-deleting destructor wrapper at 0x00437080 calls this body before optional OID__FreeObject, superseding the Wave336 constructor-base wording. Exact source destructor identity, concrete layout, and runtime lifetime behavior remain unproven.",
                tags("destructor", "value-base", "weapon-mode-value", "supersedes-wave336-ctor-label"),
                new String[] {"CPhysicsWeaponModeValue__ctor_base", "CPhysicsWeaponModeValue__ctor_like_004359c0"},
                new ParameterImpl[] {param("this", voidPtr)}),

            new Spec("0x00437080", "CPhysicsWeaponModeValue__scalar_deleting_dtor", "__thiscall", voidPtr,
                "Name/signature correction: scalar-deleting destructor wrapper calls 0x004359c0, optionally frees this via OID__FreeObject when flags bit 0 is set, and returns this. Exact source destructor identity and runtime lifetime behavior remain unproven.",
                tags("destructor", "value-base", "weapon-mode-value"),
                new String[] {"VFuncSlot_00_00437080"},
                new ParameterImpl[] {param("this", voidPtr), param("flags", intType)}),

            new Spec("0x004370a0", "CWeaponRound__ApplyToWeaponModeByName", "__thiscall", voidType,
                "Name/signature correction: searches DAT_008553ec by weaponModeName at record+0x30, then searches DAT_008553f0 by the round name stored at this+0x8 and writes the selected round reader/index via CWeaponRound__SetReaderFromGlobalListByIndex using round record names at +0x18. Exact record layouts and runtime behavior remain unproven.",
                tags("round-value", "weapon-mode-apply"),
                new String[] {"CWeaponRound__VFunc_01_004370a0"},
                new ParameterImpl[] {param("this", voidPtr), param("weaponModeName", charPtr)}),

            new Spec("0x004371c0", "CWeaponLaunchSound__ApplyToWeaponModeByName", "__thiscall", voidType,
                "Name/signature correction: searches DAT_008553ec by weaponModeName at record+0x30 and replaces the owned launch-sound string at record+0x24 from the value string at this+0x8. Exact weapon-mode layout, sound ownership, and runtime behavior remain unproven.",
                tags("sound-value", "weapon-mode-apply", "owned-string-copy"),
                new String[] {"CWeaponLaunchSound__VFunc_01_004371c0"},
                new ParameterImpl[] {param("this", voidPtr), param("weaponModeName", charPtr)}),

            new Spec("0x004372b0", "CWeaponPreFireSound__ApplyToWeaponModeByName", "__thiscall", voidType,
                "Name/signature correction: searches DAT_008553ec by weaponModeName at record+0x30 and replaces the owned pre-fire sound string at record+0x28 from the value string at this+0x8. Exact weapon-mode layout, sound ownership, and runtime behavior remain unproven.",
                tags("sound-value", "weapon-mode-apply", "owned-string-copy"),
                new String[] {"CWeaponPreFireSound__VFunc_01_004372b0"},
                new ParameterImpl[] {param("this", voidPtr), param("weaponModeName", charPtr)}),

            new Spec("0x004373a0", "CWeaponPostFireSound__ApplyToWeaponModeByName", "__thiscall", voidType,
                "Name/signature correction: searches DAT_008553ec by weaponModeName at record+0x30 and replaces the owned post-fire sound string at record+0x2c from the value string at this+0x8. Exact weapon-mode layout, sound ownership, and runtime behavior remain unproven.",
                tags("sound-value", "weapon-mode-apply", "owned-string-copy"),
                new String[] {"CWeaponPostFireSound__VFunc_01_004373a0"},
                new ParameterImpl[] {param("this", voidPtr), param("weaponModeName", charPtr)}),

            new Spec("0x00437490", "CPhysicsScriptStatements__CreateStatementType5", "__cdecl", voidPtr,
                "Name/signature correction: type-5/round value factory; allocates round value objects for observed ids 0x1 through 0x26 and returns null for unknown ids. Exact round value classes, concrete layouts, runtime physics-script behavior, and rebuild parity remain unproven.",
                tags("value-factory", "round-value"),
                new String[] {"CPhysicsScriptStatements__CreateStatementType5"},
                new ParameterImpl[] {param("valueType", intType)}),
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
