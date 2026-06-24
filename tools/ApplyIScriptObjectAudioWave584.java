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

public class ApplyIScriptObjectAudioWave584 extends GhidraScript {
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
            "iscript-object-audio-wave584",
            "retail-binary-evidence",
            "mission-script",
            "iscript",
            "command-handler",
            "signature-corrected",
            "comment-hardened",
            "script-context-abi",
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

    private ParameterImpl[] commandStackParams(DataType voidPtr) throws Exception {
        return new ParameterImpl[] {
            param("script_args", voidPtr),
            param("unused_state", voidPtr),
            param("out_result", voidPtr)
        };
    }

    private Spec[] specs() throws Exception {
        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);

        return new Spec[] {
            new Spec(
                "0x00535670",
                "IScript__GetThingName",
                "__thiscall",
                voidType,
                "Wave584 signature/comment hardening: script-context IScript command handler. ECX carries the command context, RET 0xc confirms three stack arguments, and this returner writes a CStringDataType to out_result. If the selected thing/context lacks flag bit +0x34 & 0x08 it returns an empty string; otherwise it calls CBattleEngine__GetWeaponPhysicsName(context+0x10) before CStringDataType__InitFromString. Registered by ScriptCommandRegistry__InitBuiltins. Static retail evidence only; exact script command descriptor layout, runtime mission-script behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {"IScript__GetThingName"},
                tags("object-name", "string-result", "cstring-datatype", "flag-guard-08", "weapon-physics-name"),
                commandStackParams(voidPtr)
            ),
            new Spec(
                "0x005357b0",
                "IScript__GetThingTypeName",
                "__thiscall",
                voidType,
                "Wave584 signature/comment hardening: script-context IScript command handler. ECX carries the command context, RET 0xc confirms three stack arguments, and this returner writes a CStringDataType to out_result. If the selected thing/context lacks flag bit +0x34 & 0x08 it returns an empty string; otherwise it reads the type/name string through the context object's +0x4b0/+0xa8 path before CStringDataType__InitFromString. Registered by ScriptCommandRegistry__InitBuiltins. Static retail evidence only; exact script command descriptor layout, runtime mission-script behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {"IScript__GetThingTypeName"},
                tags("object-type-name", "string-result", "cstring-datatype", "flag-guard-08"),
                commandStackParams(voidPtr)
            ),
            new Spec(
                "0x00535fa0",
                "IScript__Attack",
                "__thiscall",
                voidType,
                "Wave584 signature/comment hardening: script-context IScript command handler. ECX carries the command context, RET 0xc confirms three stack arguments, and the body reads the first script argument through datatype vtable slot +0x40 as a target thing. It warns on null target, then routes combat target assignment through the current context thing: CBattleEngine-style contexts call slot +0x154, and Unit-style contexts call CUnit__PropagateTargetUnitToHierarchy(context+0x10, target_unit), with flag checks on +0x34 bits 0x10 and 0x20000000. Registered by ScriptCommandRegistry__InitBuiltins. Static retail evidence only; exact target ownership semantics, runtime mission-script behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {"IScript__Attack"},
                tags("attack-command", "target-thing", "argument-getter-40", "unit-target-propagation", "flag-guards"),
                commandStackParams(voidPtr)
            ),
            new Spec(
                "0x005362a0",
                "IScript__GetTextWidth",
                "__thiscall",
                voidType,
                "Wave584 signature/comment hardening: script-context IScript command handler. ECX carries the command context, RET 0xc confirms three stack arguments, and this returner writes a CFloatDataType-style result to out_result. The body reads the first script argument through datatype getter vtable slot +0x30, calls CWorld__GetWorldTextSlotTimerValue(&DAT_00855090, slot_index), and stores the float result under vtable 0x005e4ea4. Registered by ScriptCommandRegistry__InitBuiltins. Static retail evidence only; exact UI/text command semantics, runtime mission-script behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {"IScript__GetTextWidth"},
                tags("text-width", "float-result", "argument-getter-30", "world-text-slot"),
                commandStackParams(voidPtr)
            ),
            new Spec(
                "0x005363e0",
                "IScript__GetPlayerBattleEngine",
                "__thiscall",
                voidType,
                "Wave584 signature/comment hardening: script-context IScript command handler. ECX carries the command context, RET 0xc confirms three stack arguments, and this returner writes a CThingPtrDataType to out_result. The body reads the player index through datatype getter vtable slot +0x30, clamps/warns for values below one, checks the player table at DAT_008a9d3c, logs the fatal no-battle-engine message on a missing entry, and otherwise returns the player's battle-engine pointer from +0x1c. Registered by ScriptCommandRegistry__InitBuiltins. Static retail evidence only; exact player table layout, runtime mission-script behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {"IScript__GetPlayerBattleEngine"},
                tags("player-battle-engine", "thing-pointer-result", "argument-getter-30", "player-table"),
                commandStackParams(voidPtr)
            ),
            new Spec(
                "0x00536ca0",
                "IScript__TriggerHitEffect",
                "__thiscall",
                voidType,
                "Wave584 signature/comment hardening: script-context IScript command handler. ECX carries the command context, RET 0xc confirms three stack arguments, and the body gates on context flag bit +0x34 & 0x10. When allowed, it reads a float from the first script argument through datatype getter vtable slot +0x34 and dispatches the current context object's vtable slot +0x1ac with that float. Registered by ScriptCommandRegistry__InitBuiltins. Static retail evidence only; exact effect parameter semantics, runtime mission-script behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {"IScript__TriggerHitEffect"},
                tags("trigger-hit-effect", "float-input", "argument-getter-34", "thing-vfunc-1ac", "flag-guard-10"),
                commandStackParams(voidPtr)
            ),
            new Spec(
                "0x00537410",
                "IScript__PlaySound",
                "__thiscall",
                voidType,
                "Wave584 signature/comment hardening: script-context IScript command handler. ECX carries the command context, RET 0xc confirms three stack arguments, and the body enqueues a message/audio request when DAT_008a9d84 is present. It seeds the default wide text from string 0x0064fd30, reads a text id from script_args[0] through datatype getter vtable slot +0x30, reads a float payload from script_args[1] through slot +0x34, allocates a CMessage-sized object, and inserts it through CMessageBox__InsertQueuedMessageSortedAndMaybeAdvance. Registered by ScriptCommandRegistry__InitBuiltins. Static retail evidence only; exact audio/message runtime behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {"IScript__PlaySound"},
                tags("audio-command", "message-box", "default-text", "argument-getter-30", "argument-getter-34"),
                commandStackParams(voidPtr)
            ),
            new Spec(
                "0x00537500",
                "IScript__PlaySoundWithCallback",
                "__thiscall",
                voidType,
                "Wave584 signature/comment hardening: script-context IScript command handler. ECX carries the command context, RET 0xc confirms three stack arguments, and the body enqueues a message/audio request when DAT_008a9d84 is present. It reads text ids from script_args[0] and script_args[1] through datatype getter vtable slot +0x30, reads a float payload from script_args[2] through slot +0x34, preserves an active-reader target when context flag bit +0x34 & 0x10 is set, allocates a CMessage-sized object, and inserts it through CMessageBox__InsertQueuedMessageSortedAndMaybeAdvance. Registered by ScriptCommandRegistry__InitBuiltins. Static retail evidence only; exact callback semantics, audio/message runtime behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {"IScript__PlaySoundWithCallback"},
                tags("audio-command", "callback-message", "message-box", "argument-getter-30", "argument-getter-34"),
                commandStackParams(voidPtr)
            ),
            new Spec(
                "0x005375f0",
                "IScript__PlaySoundWithFade",
                "__thiscall",
                voidType,
                "Wave584 signature/comment hardening: script-context IScript command handler. ECX carries the command context, RET 0xc confirms three stack arguments, and the body creates a fade/tracking object, adds it to the context list at +0x28, schedules event 0x7d1 through CEventManager__GetNextFreeEvent and CScheduledEvent__Set, then enqueues a CMessage when possible. The command reads text ids from script_args[0]/[1] through datatype getter slot +0x30 and a float payload from script_args[2] through slot +0x34. Registered by ScriptCommandRegistry__InitBuiltins. Static retail evidence only; exact fade/callback timing, audio/message runtime behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {"IScript__PlaySoundWithFade"},
                tags("audio-command", "fade-event", "message-box", "scheduled-event-7d1", "argument-getter-30", "argument-getter-34"),
                commandStackParams(voidPtr)
            ),
            new Spec(
                "0x005377e0",
                "IScript__PlaySoundWithPriority",
                "__thiscall",
                voidType,
                "Wave584 signature/comment hardening: script-context IScript command handler. ECX carries the command context, RET 0xc confirms three stack arguments, and the body enqueues a message/audio request when DAT_008a9d84 is present. It reads text ids from script_args[0] and script_args[1] through datatype getter slot +0x30, reads a float payload from script_args[2] through slot +0x34, reads a priority value from script_args[3] through slot +0x30, allocates a CMessage-sized object, and inserts it through CMessageBox__InsertQueuedMessageSortedAndMaybeAdvance. Registered by ScriptCommandRegistry__InitBuiltins. Static retail evidence only; exact priority semantics, audio/message runtime behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {"IScript__PlaySoundWithPriority"},
                tags("audio-command", "priority-message", "message-box", "argument-getter-30", "argument-getter-34"),
                commandStackParams(voidPtr)
            ),
            new Spec(
                "0x005378e0",
                "IScript__PlaySoundWithFadeAndPriority",
                "__thiscall",
                voidType,
                "Wave584 signature/comment hardening: script-context IScript command handler. ECX carries the command context, RET 0xc confirms three stack arguments, and the body combines the fade-event setup with priority message enqueue. It reads text ids from script_args[0]/[1] through datatype getter slot +0x30, reads a float payload from script_args[2] through slot +0x34, reads a priority value from script_args[3] through slot +0x30, creates a fade/tracking object, schedules event 0x7d1, and inserts a CMessage when DAT_008a9d84 is present. Registered by ScriptCommandRegistry__InitBuiltins. Static retail evidence only; exact fade/priority semantics, audio/message runtime behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {"IScript__PlaySoundWithFadeAndPriority"},
                tags("audio-command", "fade-event", "priority-message", "message-box", "scheduled-event-7d1", "argument-getter-30", "argument-getter-34"),
                commandStackParams(voidPtr)
            )
        };
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");
        Stats stats = new Stats();

        println("Mode: " + (dryRun ? "dry" : "apply"));
        for (Spec spec : specs()) {
            applySpec(spec, dryRun, stats);
        }

        println("SUMMARY updated=" + stats.updated
            + " skipped=" + stats.skipped
            + " renamed=" + stats.renamed
            + " would_rename=" + stats.wouldRename
            + " missing=" + stats.missing
            + " bad=" + stats.bad);

        if (stats.missing > 0 || stats.bad > 0) {
            throw new IllegalStateException("ApplyIScriptObjectAudioWave584 failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
