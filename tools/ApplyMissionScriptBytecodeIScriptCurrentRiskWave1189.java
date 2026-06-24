//@category BEA

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionManager;
import ghidra.program.model.listing.FunctionTag;

import java.util.Arrays;
import java.util.HashSet;
import java.util.Set;

public class ApplyMissionScriptBytecodeIScriptCurrentRiskWave1189 extends GhidraScript {
    private static class Target {
        final String address;
        final String name;
        final String signature;
        final String comment;
        final String[] tags;

        Target(String address, String name, String signature, String comment, String[] tags) {
            this.address = address;
            this.name = name;
            this.signature = signature;
            this.comment = comment;
            this.tags = tags;
        }
    }

    private static final String[] COMMON_TAGS = {
        "static-reaudit",
        "wave1189-missionscript-bytecode-iscript-current-risk-review",
        "wave1189-readback-verified",
        "retail-binary-evidence",
        "current-risk-review",
        "mission-script",
        "bytecode-vm",
        "source-identity-deferred",
        "exact-layout-deferred",
        "rebuild-grade-static-contract",
        "no-noticeable-difference-boundary",
        "comment-hardened",
        "tag-normalized"
    };

    private static final Target[] TARGETS = {
        new Target(
            "0x0052e180",
            "CInstructionOP_PLUS__VFunc_00_0052e180",
            "void __thiscall CInstructionOP_PLUS__VFunc_00_0052e180(void * this, void * script_state, void * data_stack, void * object_code)",
            "Wave1189 static read-back: MissionScript PLUS opcode executor at DATA dispatch/vtable ref 0x005e4d30. The body uses the shared bytecode VM data stack, pops two datatype operands, dispatches the second popped operand's datatype vtable slot +0x04 with the first operand, releases both operands through datatype vtable slot +0 with flag 1 when non-null, and pushes the produced datatype result back to data_stack. Static retail Ghidra metadata/xref/decompile/instruction evidence only; exact operand order naming, VM/data-stack/datatype concrete layouts, runtime MissionScript behavior, exact source-body identity, BEA patching, rebuild parity, and clean-room/no-noticeable-difference parity remain separate proof.",
            withCommon("opcode-executor", "datatype-vtable", "plus", "arithmetic-operator")
        ),
        new Target(
            "0x0052e1d0",
            "CInstructionOP_MINUS__VFunc_00_0052e1d0",
            "void __thiscall CInstructionOP_MINUS__VFunc_00_0052e1d0(void * this, void * script_state, void * data_stack, void * object_code)",
            "Wave1189 static read-back: MissionScript MINUS opcode executor at DATA dispatch/vtable ref 0x005e4d20. The body uses the shared bytecode VM data stack, pops two datatype operands, dispatches the second popped operand's datatype vtable slot +0x08 with the first operand, releases both operands through datatype vtable slot +0 with flag 1 when non-null, and pushes the produced datatype result back to data_stack. Static retail Ghidra metadata/xref/decompile/instruction evidence only; exact operand order naming, VM/data-stack/datatype concrete layouts, runtime MissionScript behavior, exact source-body identity, BEA patching, rebuild parity, and clean-room/no-noticeable-difference parity remain separate proof.",
            withCommon("opcode-executor", "datatype-vtable", "minus", "arithmetic-operator")
        ),
        new Target(
            "0x0052e220",
            "CInstructionOP_MULTIPLY__VFunc_00_0052e220",
            "void __thiscall CInstructionOP_MULTIPLY__VFunc_00_0052e220(void * this, void * script_state, void * data_stack, void * object_code)",
            "Wave1189 static read-back: MissionScript MULTIPLY opcode executor at DATA dispatch/vtable ref 0x005e4d10. The body uses the shared bytecode VM data stack, pops two datatype operands, dispatches the second popped operand's datatype vtable slot +0x0c with the first operand, releases both operands through datatype vtable slot +0 with flag 1 when non-null, and pushes the produced datatype result back to data_stack. Static retail Ghidra metadata/xref/decompile/instruction evidence only; exact operand order naming, VM/data-stack/datatype concrete layouts, runtime MissionScript behavior, exact source-body identity, BEA patching, rebuild parity, and clean-room/no-noticeable-difference parity remain separate proof.",
            withCommon("opcode-executor", "datatype-vtable", "multiply", "arithmetic-operator")
        ),
        new Target(
            "0x0052e270",
            "CInstructionOP_DIVIDE__VFunc_00_0052e270",
            "void __thiscall CInstructionOP_DIVIDE__VFunc_00_0052e270(void * this, void * script_state, void * data_stack, void * object_code)",
            "Wave1189 static read-back: MissionScript DIVIDE opcode executor at DATA dispatch/vtable ref 0x005e4d00. The body uses the shared bytecode VM data stack, pops two datatype operands, dispatches the second popped operand's datatype vtable slot +0x10 with the first operand, releases both operands through datatype vtable slot +0 with flag 1 when non-null, and pushes the produced datatype result back to data_stack. Static retail Ghidra metadata/xref/decompile/instruction evidence only; exact operand order naming, VM/data-stack/datatype concrete layouts, runtime MissionScript behavior, exact source-body identity, BEA patching, rebuild parity, and clean-room/no-noticeable-difference parity remain separate proof.",
            withCommon("opcode-executor", "datatype-vtable", "divide", "arithmetic-operator")
        ),
        new Target(
            "0x0052e330",
            "CInstructionOP_CMP__VFunc_00_0052e330",
            "void __thiscall CInstructionOP_CMP__VFunc_00_0052e330(void * this, void * script_state, void * data_stack, void * object_code)",
            "Wave1189 static read-back: MissionScript CMP opcode executor at DATA dispatch/vtable ref 0x005e4c50. The body reads the top two datatype operands through CScriptObjectCode__GetTop(data_stack,0) and CScriptObjectCode__GetTop(data_stack,1), dispatches datatype vtable slot +0x18 for equality-style comparison, then sets or clears bit 0 of script_state+0x218 without popping the operands. Static retail Ghidra metadata/xref/decompile/instruction evidence only; exact comparison-flag semantics, VM/data-stack/datatype concrete layouts, runtime MissionScript behavior, exact source-body identity, BEA patching, rebuild parity, and clean-room/no-noticeable-difference parity remain separate proof.",
            withCommon("opcode-executor", "datatype-vtable", "compare", "script-state-flag")
        ),
        new Target(
            "0x005333b0",
            "IScript__Constructor",
            "void * __thiscall IScript__Constructor(void * this, void * owner_complex_thing, void * script_object_code)",
            "Wave1189 static read-back: IScript constructor called by CComplexThing__SetScript at 0x004f42a8 after a 0x3c-byte mission-script object allocation. RET 0x8 proves ECX=this plus owner_complex_thing and script_object_code stack arguments. The body initializes the CMonitor base/list state, installs vtable 0x005e4f08, stores owner_complex_thing at this+0x08 and this+0x10, stores script_object_code at this+0x0c, writes the script back-pointer at script_object_code+0x68, and clears local listener/state slots through this+0x38. Static retail Ghidra metadata/xref/decompile/instruction evidence only; exact IScript/CMonitor concrete layouts, exact source-body identity, runtime mission-script startup behavior, BEA patching, rebuild parity, and clean-room/no-noticeable-difference parity remain separate proof.",
            withCommon("iscript", "constructor", "monitor-base", "script-back-pointer")
        ),
        new Target(
            "0x00539f30",
            "CMissionScriptObjectCode__ClearFields_Thunk",
            "void __fastcall CMissionScriptObjectCode__ClearFields_Thunk(void * field_block)",
            "Wave1189 static read-back: CMissionScriptObjectCode ClearFields one-instruction JMP thunk reached from CHud__ShutDown at 0x00481b44. The thunk forwards the supplied ECX field_block to CMissionScriptObjectCode__ClearFields at 0x00539f40, keeping this row as a HUD script-field-block teardown bridge rather than a second ClearFields body. Static retail Ghidra metadata/xref/decompile/instruction evidence only; exact field-block/object-code concrete layout, exact source-body identity, runtime HUD/script teardown behavior, BEA patching, rebuild parity, and clean-room/no-noticeable-difference parity remain separate proof.",
            withCommon("mission-script-object-code", "clear-fields-thunk", "hud-shutdown", "jmp-thunk")
        )
    };

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        String mode = args != null && args.length > 0 ? args[0].trim().toLowerCase() : "dry";
        boolean dryRun = true;
        if ("apply".equals(mode)) {
            dryRun = false;
        } else if (!"dry".equals(mode)) {
            throw new IllegalArgumentException("Expected mode dry|apply, got: " + mode);
        }

        FunctionManager functionManager = currentProgram.getFunctionManager();
        int updated = 0;
        int skipped = 0;
        int commentOnlyUpdated = 0;
        int tagsAdded = 0;
        int missing = 0;
        int bad = 0;

        for (Target target : TARGETS) {
            Address address = toAddr(target.address);
            Function function = functionManager.getFunctionAt(address);
            if (function == null) {
                println("MISSING: " + target.address + " " + target.name);
                missing++;
                continue;
            }

            boolean targetBad = false;
            if (!target.name.equals(function.getName())) {
                println("BADNAME: " + target.address + " expected=" + target.name + " actual=" + function.getName());
                targetBad = true;
            }
            if (!target.signature.equals(function.getSignature().toString())) {
                println("BADSIG: " + target.address + " expected=" + target.signature + " actual=" + function.getSignature());
                targetBad = true;
            }
            if (targetBad) {
                bad++;
                continue;
            }

            Set<String> actualTags = tagNames(function);
            Set<String> requiredTags = new HashSet<>(Arrays.asList(target.tags));
            requiredTags.removeAll(actualTags);
            boolean commentNeedsUpdate = function.getComment() == null || !target.comment.equals(function.getComment());
            boolean tagsNeedUpdate = !requiredTags.isEmpty();

            if (!commentNeedsUpdate && !tagsNeedUpdate) {
                println("SKIP: " + target.address + " " + target.name + " comment/tags already current");
                skipped++;
            } else if (dryRun) {
                println("WOULD_UPDATE: " + target.address + " " + target.name + " comment=" + commentNeedsUpdate + " tags=+" + String.join(",", requiredTags));
                if (commentNeedsUpdate) {
                    commentOnlyUpdated++;
                }
                tagsAdded += requiredTags.size();
            } else {
                if (commentNeedsUpdate) {
                    function.setComment(target.comment);
                    commentOnlyUpdated++;
                }
                for (String tag : requiredTags) {
                    function.addTag(tag);
                }
                tagsAdded += requiredTags.size();
                updated++;
                currentProgram.flushEvents();
                Thread.sleep(50L);

                Function readBack = functionManager.getFunctionAt(address);
                if (readBack == null) {
                    println("VERIFY_MISSING: " + target.address);
                    bad++;
                } else {
                    if (!target.comment.equals(readBack.getComment())) {
                        println("VERIFY_BAD_COMMENT: " + target.address);
                        bad++;
                    }
                    Set<String> readBackTags = tagNames(readBack);
                    for (String tag : target.tags) {
                        if (!readBackTags.contains(tag)) {
                            println("VERIFY_MISSING_TAG: " + target.address + " " + tag);
                            bad++;
                        }
                    }
                }
                println("UPDATED: " + target.address + " " + target.name + " comment=" + commentNeedsUpdate + " tags_added=" + requiredTags.size());
            }
        }

        println("SUMMARY: updated=" + updated
            + " skipped=" + skipped
            + " renamed=0"
            + " would_rename=0"
            + " signature_updated=0"
            + " comment_only_updated=" + commentOnlyUpdated
            + " tags_added=" + tagsAdded
            + " missing=" + missing
            + " bad=" + bad);

        if (missing != 0 || bad != 0) {
            throw new IllegalStateException("Wave1189 MissionScript/IScript normalization failed: missing=" + missing + " bad=" + bad);
        }
        if (!dryRun) {
            println("REPORT: Save succeeded");
        }
    }

    private static String[] withCommon(String... extraTags) {
        String[] tags = new String[COMMON_TAGS.length + extraTags.length];
        System.arraycopy(COMMON_TAGS, 0, tags, 0, COMMON_TAGS.length);
        System.arraycopy(extraTags, 0, tags, COMMON_TAGS.length, extraTags.length);
        return tags;
    }

    private Set<String> tagNames(Function function) {
        Set<String> names = new HashSet<>();
        for (FunctionTag tag : function.getTags()) {
            names.add(tag.getName());
        }
        return names;
    }
}
