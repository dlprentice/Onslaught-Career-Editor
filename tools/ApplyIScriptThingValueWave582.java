//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.FunctionTag;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyIScriptThingValueWave582 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final String comment;
        final String[] allowedExistingNames;
        final String[] tags;
        final ParameterImpl[] parameters;

        Spec(
                String address,
                String name,
                String callingConvention,
                DataType returnType,
                String comment,
                String[] allowedExistingNames,
                String[] tags,
                ParameterImpl[] parameters) {
            this.address = address;
            this.name = name;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.comment = comment;
            this.allowedExistingNames = allowedExistingNames;
            this.tags = tags;
            this.parameters = parameters;
        }
    }

    private static class Stats {
        int updated = 0;
        int skipped = 0;
        int renamed = 0;
        int wouldRename = 0;
        int missing = 0;
        int bad = 0;
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
        Address address = toAddr(addressText);
        if (address == null) {
            throw new IllegalArgumentException("Bad address: " + addressText);
        }
        return address;
    }

    private Function functionAtEntry(Address address) {
        Function fn = getFunctionAt(address);
        if (fn == null) {
            Function containing = getFunctionContaining(address);
            if (containing != null && containing.getEntryPoint().equals(address)) {
                fn = containing;
            }
        }
        return fn;
    }

    private Function getFunctionOrReport(Spec spec, Stats stats) {
        Function fn = functionAtEntry(addr(spec.address));
        if (fn == null) {
            stats.missing++;
            println("FAIL: " + spec.address + " " + spec.name + " Function not found");
        }
        return fn;
    }

    private ParameterImpl param(String name, DataType dataType) throws Exception {
        return new ParameterImpl(name, dataType, currentProgram);
    }

    private boolean allowedName(Spec spec, String actual) {
        if (actual.equals(spec.name)) {
            return true;
        }
        for (String allowed : spec.allowedExistingNames) {
            if (actual.equals(allowed)) {
                return true;
            }
        }
        return false;
    }

    private String expectedSignature(Spec spec) {
        StringBuilder sb = new StringBuilder();
        sb.append(spec.returnType.getDisplayName())
            .append(" ")
            .append(spec.callingConvention)
            .append(" ")
            .append(spec.name)
            .append("(");
        if (spec.parameters.length == 0) {
            sb.append("void");
        }
        for (int i = 0; i < spec.parameters.length; i++) {
            if (i > 0) {
                sb.append(", ");
            }
            sb.append(spec.parameters[i].getDataType().getDisplayName())
                .append(" ")
                .append(spec.parameters[i].getName());
        }
        sb.append(")");
        return sb.toString();
    }

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "iscript-thing-value-wave582",
            "retail-binary-evidence",
            "mission-script",
            "iscript",
            "command-handler",
            "signature-corrected",
            "comment-hardened",
            "script-context-abi",
            "script-command-registry",
            "thing-value"
        };
        String[] result = new String[common.length + extras.length];
        System.arraycopy(common, 0, result, 0, common.length);
        System.arraycopy(extras, 0, result, common.length, extras.length);
        return result;
    }

    private Set<String> tagNames(Function fn) {
        Set<String> names = new HashSet<>();
        for (FunctionTag tag : fn.getTags()) {
            names.add(tag.getName());
        }
        return names;
    }

    private void applySpec(Spec spec, boolean dryRun, Stats stats) {
        try {
            Function fn = getFunctionOrReport(spec, stats);
            if (fn == null) {
                stats.skipped++;
                return;
            }

            String currentName = fn.getName();
            if (!allowedName(spec, currentName)) {
                throw new IllegalStateException("Unexpected function name at " + spec.address + ": " + currentName);
            }

            boolean needsRename = !currentName.equals(spec.name);
            if (dryRun) {
                if (needsRename) {
                    stats.wouldRename++;
                }
                println("DRY: " + spec.address + " " + currentName + " -> " + expectedSignature(spec));
                stats.skipped++;
                return;
            }

            if (needsRename) {
                fn.setName(spec.name, SourceType.USER_DEFINED);
                stats.renamed++;
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

            Function readBack = functionAtEntry(addr(spec.address));
            if (readBack == null) {
                throw new IllegalStateException("Read-back missing at " + spec.address);
            }
            if (!readBack.getName().equals(spec.name)) {
                throw new IllegalStateException("Read-back name mismatch at " + spec.address + ": " + readBack.getName());
            }
            if (!spec.comment.equals(readBack.getComment())) {
                throw new IllegalStateException("Read-back comment mismatch at " + spec.address);
            }
            Set<String> readBackTags = tagNames(readBack);
            for (String tag : spec.tags) {
                if (!readBackTags.contains(tag)) {
                    throw new IllegalStateException("Read-back missing tag " + tag + " at " + spec.address);
                }
            }

            println("OK: " + spec.address + " " + readBack.getSignature());
            stats.updated++;
            Thread.sleep(50);
        } catch (Exception ex) {
            stats.bad++;
            println("FAIL: " + spec.address + " " + spec.name + " " + ex.getClass().getSimpleName() + ": " + ex.getMessage());
        }
    }

    private ParameterImpl[] commandStackParams(DataType voidPtr) throws Exception {
        return new ParameterImpl[] {
            param("script_args", voidPtr),
            param("unused_state", voidPtr),
            param("out_result", voidPtr)
        };
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");
        println("Mode: " + (dryRun ? "dry" : "apply"));

        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);

        Spec[] specs = new Spec[] {
            new Spec(
                "0x00534fb0",
                "IScript__SetThingValueViaVFunc198_FromArg",
                "__thiscall",
                voidType,
                "Wave582 signature/comment hardening: script-context IScript command handler. ECX carries the command context, RET 0xc confirms three stack arguments, and the body gates on the referenced thing/context flag bit +0x34 & 0x10. When allowed, it reads the first script argument through datatype getter vtable slot +0x38 and dispatches the selected thing object's vtable slot +0x198 with that value. Registered by ScriptCommandRegistry__InitBuiltins. Static retail evidence only; exact slot meaning, runtime mission-script behavior, script corpus coverage, BEA patching, and rebuild parity remain unproven.",
                new String[] {"IScript__SetThingValueViaVFunc198_FromArg"},
                tags("thing-vfunc-198", "argument-getter-38", "flag-guard-10"),
                commandStackParams(voidPtr)
            ),
            new Spec(
                "0x00534fe0",
                "IScript__SetThingValueViaVFunc19C_FromArg",
                "__thiscall",
                voidType,
                "Wave582 signature/comment hardening: script-context IScript command handler. ECX carries the command context, RET 0xc confirms three stack arguments, and the body gates on the referenced thing/context flag bit +0x34 & 0x10. When allowed, it reads the first script argument through datatype getter vtable slot +0x38 and dispatches the selected thing object's vtable slot +0x19c with that value. Registered by ScriptCommandRegistry__InitBuiltins. Static retail evidence only; exact slot meaning, runtime mission-script behavior, script corpus coverage, BEA patching, and rebuild parity remain unproven.",
                new String[] {"IScript__SetThingValueViaVFunc19C_FromArg"},
                tags("thing-vfunc-19c", "argument-getter-38", "flag-guard-10"),
                commandStackParams(voidPtr)
            ),
            new Spec(
                "0x00535010",
                "IScript__SetThingValueViaEngineHelper4FE390_FromArg",
                "__thiscall",
                voidType,
                "Wave582 signature/comment hardening: script-context IScript command handler. ECX carries the command context, RET 0xc confirms three stack arguments, and the body gates on the referenced engine/context flag bit +0x34 & 0x10. When allowed, it reads the first script argument through datatype getter vtable slot +0x38 and calls CEngine__EnableThingByNameFlag(context+0x10, thing_name). Registered by ScriptCommandRegistry__InitBuiltins. Static retail evidence only; exact command descriptor layout, runtime mission-script behavior, script corpus coverage, BEA patching, and rebuild parity remain unproven.",
                new String[] {"IScript__SetThingValueViaEngineHelper4FE390_FromArg"},
                tags("engine-helper", "enable-thing-by-name", "argument-getter-38", "flag-guard-10"),
                commandStackParams(voidPtr)
            ),
            new Spec(
                "0x00535040",
                "IScript__SetThingValueViaEngineHelper4FE3F0_FromArg",
                "__thiscall",
                voidType,
                "Wave582 signature/comment hardening: script-context IScript command handler. ECX carries the command context, RET 0xc confirms three stack arguments, and the body gates on the referenced engine/context flag bit +0x34 & 0x10. When allowed, it reads the first script argument through datatype getter vtable slot +0x38 and calls CEngine__DisableThingByNameFlag(context+0x10, thing_name). Registered by ScriptCommandRegistry__InitBuiltins. Static retail evidence only; exact command descriptor layout, runtime mission-script behavior, script corpus coverage, BEA patching, and rebuild parity remain unproven.",
                new String[] {"IScript__SetThingValueViaEngineHelper4FE3F0_FromArg"},
                tags("engine-helper", "disable-thing-by-name", "argument-getter-38", "flag-guard-10"),
                commandStackParams(voidPtr)
            ),
            new Spec(
                "0x00535530",
                "IScript__SetThingFloatViaVFunc1C8_FromArg",
                "__thiscall",
                voidType,
                "Wave582 signature/comment hardening: script-context IScript command handler. ECX carries the command context, RET 0xc confirms three stack arguments, and the body gates on the referenced thing/context flag bit +0x34 & 0x10. When allowed, it reads a float from the first script argument through datatype getter vtable slot +0x34 and dispatches the selected thing object's vtable slot +0x1c8 with that float. Registered by ScriptCommandRegistry__InitBuiltins. Static retail evidence only; exact slot meaning, runtime mission-script behavior, script corpus coverage, BEA patching, and rebuild parity remain unproven.",
                new String[] {"IScript__SetThingFloatViaVFunc1C8_FromArg"},
                tags("thing-vfunc-1c8", "float-input", "argument-getter-34", "flag-guard-10"),
                commandStackParams(voidPtr)
            ),
            new Spec(
                "0x00535560",
                "IScript__SetThingRefViaCUnitHelper4FD830_FromArg",
                "__thiscall",
                voidType,
                "Wave582 signature/comment hardening: script-context IScript command handler. ECX carries the command context, RET 0xc confirms three stack arguments, and the body gates on the referenced Unit/context flag bit +0x34 & 0x10. When allowed, it reads an integer/faction-like state from the first script argument through datatype getter vtable slot +0x30 and calls CUnit__SetFactionForHierarchy(context+0x10, faction_state). Registered by ScriptCommandRegistry__InitBuiltins. Static retail evidence only; exact state enum, runtime mission-script behavior, script corpus coverage, BEA patching, and rebuild parity remain unproven.",
                new String[] {"IScript__SetThingRefViaCUnitHelper4FD830_FromArg"},
                tags("unit-helper", "set-faction-hierarchy", "integer-input", "argument-getter-30", "flag-guard-10"),
                commandStackParams(voidPtr)
            )
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }

        println("SUMMARY updated=" + stats.updated
            + " skipped=" + stats.skipped
            + " renamed=" + stats.renamed
            + " would_rename=" + stats.wouldRename
            + " missing=" + stats.missing
            + " bad=" + stats.bad);

        if (stats.missing > 0 || stats.bad > 0) {
            throw new IllegalStateException("ApplyIScriptThingValueWave582 failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
