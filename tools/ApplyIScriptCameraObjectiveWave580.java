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

public class ApplyIScriptCameraObjectiveWave580 extends GhidraScript {
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
            "iscript-camera-objective-wave580",
            "retail-binary-evidence",
            "mission-script",
            "iscript",
            "command-handler",
            "signature-corrected",
            "comment-hardened"
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

    private ParameterImpl[] commandParams(DataType voidPtr) throws Exception {
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
                "0x00533b70",
                "IScript__Create3PointPanCamera",
                "__stdcall",
                voidType,
                "Wave580 signature/comment hardening: fixed script command ABI handler for Create3PointPanCamera(thing,pos0,pos1,pos2,duration). RET 0xc confirms three stack arguments even though the body uses script_args only. The body gets the target thing through argument vtable slot +0x40, reports the null-thing fatal string at 0x0064fa9c, transforms three vector arguments through the thing matrix or DAT_0083d9c0 identity fallback, adds the vectors to a CSPtrSet list, constructs a CBSpline, constructs a CPanCamera with duration from vtable slot +0x34, and calls CGame__SetCurrentCamera(&DAT_008a9a98,0,camera,1). Registered by ScriptCommandRegistry__InitBuiltins. Static retail evidence only; runtime mission-script behavior, exact command descriptor layout, and rebuild parity remain unproven.",
                new String[] {"IScript__Create3PointPanCamera"},
                tags("fixed-script-abi", "pan-camera", "camera", "thing-input", "vector-input", "script-command-registry"),
                commandParams(voidPtr)
            ),
            new Spec(
                "0x00533eb0",
                "IScript__Create4PointPanCamera",
                "__stdcall",
                voidType,
                "Wave580 signature/comment hardening: fixed script command ABI handler for Create4PointPanCamera(thing,pos0,pos1,pos2,pos3,duration). RET 0xc confirms three stack arguments even though the body uses script_args only. The body gets the target thing through argument vtable slot +0x40, reports the null-thing fatal string at 0x0064fad8, transforms four vector arguments through the thing matrix or DAT_0083d9c0 identity fallback, adds the vectors to a CSPtrSet list, constructs a CBSpline, constructs a CPanCamera with duration from vtable slot +0x34, and calls CGame__SetCurrentCamera(&DAT_008a9a98,0,camera,1). Registered by ScriptCommandRegistry__InitBuiltins. Static retail evidence only; runtime mission-script behavior, exact command descriptor layout, and rebuild parity remain unproven.",
                new String[] {"IScript__Create4PointPanCamera"},
                tags("fixed-script-abi", "pan-camera", "camera", "thing-input", "vector-input", "script-command-registry"),
                commandParams(voidPtr)
            ),
            new Spec(
                "0x005343e0",
                "IScript__PrimaryObjectiveComplete",
                "__stdcall",
                voidType,
                "Wave580 signature/comment hardening: fixed script command ABI handler for PrimaryObjectiveComplete(objective_index,text_id). RET 0xc confirms three stack arguments even though only script_args is used. The body reads text_id from script_args[1] and objective_index from script_args[0] through datatype vtable slot +0x30, writes text_id to primary objective text storage at DAT_008a9ae0 + index*8, and writes state 1 at DAT_008a9adc + index*8. Registered by ScriptCommandRegistry__InitBuiltins. Static retail evidence only; runtime mission-objective UI behavior and script corpus coverage remain unproven.",
                new String[] {"IScript__PrimaryObjectiveComplete"},
                tags("fixed-script-abi", "objective-state", "primary-objective", "objective-complete", "msl-command", "script-command-registry"),
                commandParams(voidPtr)
            ),
            new Spec(
                "0x00534410",
                "IScript__SecondaryObjectiveComplete",
                "__stdcall",
                voidType,
                "Wave580 signature/comment hardening: fixed script command ABI handler for SecondaryObjectiveComplete(objective_index,text_id). RET 0xc confirms three stack arguments even though only script_args is used. The body reads text_id from script_args[1] and objective_index from script_args[0] through datatype vtable slot +0x30, writes text_id to secondary objective text storage at DAT_008a9b30 + index*8, and writes state 1 at DAT_008a9b2c + index*8. Registered by ScriptCommandRegistry__InitBuiltins. Static retail evidence only; runtime mission-objective UI behavior and script corpus coverage remain unproven.",
                new String[] {"IScript__SecondaryObjectiveComplete"},
                tags("fixed-script-abi", "objective-state", "secondary-objective", "objective-complete", "msl-command", "script-command-registry"),
                commandParams(voidPtr)
            ),
            new Spec(
                "0x00534440",
                "IScript__PrimaryObjectiveFailed",
                "__stdcall",
                voidType,
                "Wave580 signature/comment hardening: fixed script command ABI handler for PrimaryObjectiveFailed(objective_index,text_id). RET 0xc confirms three stack arguments even though only script_args is used. The body reads text_id from script_args[1] and objective_index from script_args[0] through datatype vtable slot +0x30, writes text_id to primary objective text storage at DAT_008a9ae0 + index*8, and writes state 2 at DAT_008a9adc + index*8. Registered by ScriptCommandRegistry__InitBuiltins. Static retail evidence only; runtime mission-objective UI behavior and script corpus coverage remain unproven.",
                new String[] {"IScript__PrimaryObjectiveFailed"},
                tags("fixed-script-abi", "objective-state", "primary-objective", "objective-failed", "msl-command", "script-command-registry"),
                commandParams(voidPtr)
            ),
            new Spec(
                "0x00534470",
                "IScript__SecondaryObjectiveFailed",
                "__stdcall",
                voidType,
                "Wave580 signature/comment hardening: fixed script command ABI handler for SecondaryObjectiveFailed(objective_index,text_id). RET 0xc confirms three stack arguments even though only script_args is used. The body reads text_id from script_args[1] and objective_index from script_args[0] through datatype vtable slot +0x30, writes text_id to secondary objective text storage at DAT_008a9b30 + index*8, and writes state 2 at DAT_008a9b2c + index*8. Registered by ScriptCommandRegistry__InitBuiltins. Static retail evidence only; runtime mission-objective UI behavior and script corpus coverage remain unproven.",
                new String[] {"IScript__SecondaryObjectiveFailed"},
                tags("fixed-script-abi", "objective-state", "secondary-objective", "objective-failed", "msl-command", "script-command-registry"),
                commandParams(voidPtr)
            )
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }

        println(
            "SUMMARY updated=" + stats.updated +
            " skipped=" + stats.skipped +
            " renamed=" + stats.renamed +
            " would_rename=" + stats.wouldRename +
            " missing=" + stats.missing +
            " bad=" + stats.bad
        );
        if (stats.missing > 0 || stats.bad > 0) {
            throw new RuntimeException("Wave580 apply finished with missing/bad counts");
        }
    }
}
