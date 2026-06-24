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

public class ApplyIScriptLevelEventWave585 extends GhidraScript {
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
            "iscript-level-event-wave585",
            "retail-binary-evidence",
            "mission-script",
            "iscript",
            "command-handler",
            "signature-corrected",
            "comment-hardened",
            "script-command-registry"
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
                "0x00537fd0",
                "IScript__IsFriendly",
                "__thiscall",
                voidType,
                "Wave585 rename/signature/comment hardening: script-context IScript command handler for the registered IsFriendly command. ScriptCommandRegistry__InitBuiltins stores string s_IsFriendly_0064f9d4 with this function pointer at command slot +0x30, ECX carries the command context, and RET 0xc confirms three stack arguments. The body checks context+0x10 flag bit +0x34 & 0x10 and context+0x10 field +0x138 == 0, then allocates a CEventFunctionParam bool result into out_result; allocation source lines differ between the true and false paths. Static retail evidence only; exact descriptor layout, exact flag/team semantics, runtime mission-script behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {"CBoolDataType__ctor_like_00537fd0", "IScript__IsFriendly"},
                tags("script-context-abi", "bool-result", "ceventfunctionparam", "isfriendly", "thing-flag-10"),
                commandParams(voidPtr)
            ),
            new Spec(
                "0x005381a0",
                "IScript__LevelLost",
                "__stdcall",
                voidType,
                "Wave585 signature/comment hardening: fixed script command ABI handler for LevelLost(). RET 0xc confirms three stack arguments even though the tiny thunk ignores them. The body sets ECX=&DAT_008a9a98 and calls CGame__DeclareLevelLost(0,0), producing the no-message non-death loss path. Registered by ScriptCommandRegistry__InitBuiltins. Static retail evidence only; exact descriptor layout, runtime mission-script behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {"IScript__LevelLost"},
                tags("fixed-script-abi", "level-result", "level-lost", "no-message", "non-death-loss"),
                commandParams(voidPtr)
            ),
            new Spec(
                "0x005381c0",
                "IScript__LevelLostString",
                "__stdcall",
                voidType,
                "Wave585 signature/comment hardening: fixed script command ABI handler for LevelLostString(message_id). RET 0xc confirms three stack arguments; the body reads message_id from script_args via vtable slot +0x30, pushes player_died=0, and calls CGame__DeclareLevelLost(&DAT_008a9a98,message_id,0). ScriptCommandRegistry__InitBuiltins registers the command name s_LevelLostString_0064f478 with one argument and this function pointer. Static retail evidence only; exact descriptor layout, runtime mission-script behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {"IScript__LevelLostString"},
                tags("fixed-script-abi", "level-result", "level-lost-string", "message-id", "non-death-loss"),
                commandParams(voidPtr)
            ),
            new Spec(
                "0x005381e0",
                "IScript__LevelWon",
                "__stdcall",
                voidType,
                "Wave585 signature/comment hardening: fixed script command ABI handler for LevelWon(). RET 0xc confirms three stack arguments even though the tiny thunk ignores them. The body sets ECX=&DAT_008a9a98 and calls CGame__DeclareLevelWon. Registered by ScriptCommandRegistry__InitBuiltins. Static retail evidence only; exact descriptor layout, runtime mission-script behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {"IScript__LevelWon"},
                tags("fixed-script-abi", "level-result", "level-won"),
                commandParams(voidPtr)
            ),
            new Spec(
                "0x005383c0",
                "IScript__ScheduleEvent",
                "__stdcall",
                voidType,
                "Wave585 signature/comment hardening: fixed script command ABI handler for PostEvent(event_name). RET 0xc confirms three stack arguments. The body allocates a 0xc-byte event payload, reads the event name/reference through script_args vtable slot +0x48, links the payload into DAT_00855190 with CSPtrSet__AddToHead, then schedules CEventManager__AddEvent_AtTime(&EVENT_MANAGER,2000,&DAT_0089c590,-1.0,0,payload,0). ScriptCommandRegistry__InitBuiltins registers s_PostEvent_0064f9e8 with this function pointer. Static retail evidence only; exact descriptor layout, event payload layout, runtime mission-script behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {"IScript__ScheduleEvent"},
                tags("fixed-script-abi", "post-event", "scheduled-event", "event-manager", "ceventfunctionparam"),
                commandParams(voidPtr)
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
            throw new RuntimeException("Wave585 apply encountered missing/bad rows");
        }
    }
}
