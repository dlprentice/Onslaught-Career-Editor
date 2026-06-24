//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.BooleanDataType;
import ghidra.program.model.data.CharDataType;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

public class ApplyCareerSaveHelperSignatureTranche extends GhidraScript {
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

    private static class Stats {
        int updated = 0;
        int skipped = 0;
        int missing = 0;
        int bad = 0;
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

    private Address addr(String addrText) {
        if (!addrText.startsWith("0x") && !addrText.startsWith("0X")) {
            addrText = "0x" + addrText;
        }
        Address addr = toAddr(addrText);
        if (addr == null) {
            throw new IllegalArgumentException("Bad address: " + addrText);
        }
        return addr;
    }

    private Function getFunctionOrThrow(String addrText) throws Exception {
        Address addr = addr(addrText);
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

    private String expectedSignature(Spec spec) {
        StringBuilder sb = new StringBuilder();
        sb.append(spec.returnType.getDisplayName()).append(" ").append(spec.callingConvention).append(" ").append(spec.name).append("(");
        for (int i = 0; i < spec.parameters.length; i++) {
            if (i > 0) {
                sb.append(", ");
            }
            sb.append(spec.parameters[i].getDataType().getDisplayName()).append(" ").append(spec.parameters[i].getName());
        }
        if (spec.parameters.length == 0) {
            sb.append("void");
        }
        sb.append(")");
        return sb.toString();
    }

    private void applySpec(Spec spec, boolean dryRun, Stats stats) {
        try {
            Function fn = getFunctionOrThrow(spec.address);
            if (!fn.getName().equals(spec.name)) {
                throw new IllegalStateException("Unexpected function name at " + spec.address + ": " + fn.getName() + " != " + spec.name);
            }
            if (dryRun) {
                println("DRY: " + spec.address + " " + spec.name + " -> " + expectedSignature(spec));
                stats.skipped++;
                return;
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
            stats.updated++;
            Thread.sleep(50);
        } catch (IllegalStateException ex) {
            if (ex.getMessage() != null && ex.getMessage().startsWith("Function not found")) {
                stats.missing++;
            } else {
                stats.bad++;
            }
            println("FAIL: " + spec.address + " " + spec.name + " " + ex.getMessage());
        } catch (Exception ex) {
            stats.bad++;
            println("FAIL: " + spec.address + " " + spec.name + " " + ex.getMessage());
        }
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");
        println("Mode: " + (dryRun ? "dry" : "apply"));

        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);
        DataType charType = CharDataType.dataType;
        DataType charPtr = new PointerDataType(charType);
        DataType intType = IntegerDataType.dataType;
        DataType boolType = BooleanDataType.dataType;

        String[] sourceTags = new String[] {"static-reaudit", "career-save-wave329", "career-save", "signature-hardened", "source-parity"};
        String[] graphTags = new String[] {"static-reaudit", "career-save-wave329", "career-save", "signature-hardened", "source-parity", "career-graph"};
        String[] baseThingTags = new String[] {"static-reaudit", "career-save-wave329", "career-save", "signature-hardened", "source-parity", "base-things"};
        String[] goodieTags = new String[] {"static-reaudit", "career-save-wave329", "career-save", "signature-hardened", "goodies"};
        String[] gradeTags = new String[] {"static-reaudit", "career-save-wave329", "career-save", "signature-hardened", "goodies", "grade-system"};
        String[] saveTags = new String[] {"static-reaudit", "career-save-wave329", "career-save", "signature-hardened", "save-format"};
        String[] serializeTags = new String[] {"static-reaudit", "career-save-wave329", "career-save", "signature-hardened", "save-format", "serialization"};

        Spec[] specs = new Spec[] {
            new Spec("0x0041b770", "CCareerNode__SetBaseThingExistTo", "__thiscall", voidType,
                "Signature/comment/tag hardening: source-parity CCareerNode::SetBaseThingExistTo computes offset >> 5 and offset & 31, then sets or clears the base-things-exist bit at node +0x14. Mission-object meaning, runtime carry-forward behavior, and rebuild parity remain unproven.",
                baseThingTags, new ParameterImpl[] {param("this", voidPtr), param("offset", intType), param("val", intType)}),
            new Spec("0x0041b7b0", "CCareer__GetLevelStructure", "__cdecl", voidPtr,
                "Signature/comment/tag hardening: returns the static Career.cpp level_structure table at 0x00623e28. The 43x5 rows encode world id, lower/higher child indices, and primary/secondary base-update worlds; exact runtime progression behavior and rebuild parity remain unproven.",
                graphTags, new ParameterImpl[] {}),
            new Spec("0x0041b940", "CCareerNode__GetChildLinks", "__thiscall", voidPtr,
                "Signature/comment/tag hardening: source-parity CCareerNode::GetChildLinks builds an output SPtrSet containing the lower and higher link pointers resolved from node fields +0x8/+0xc. Concrete SPtrSet layout and runtime UI/progression behavior remain unproven.",
                graphTags, new ParameterImpl[] {param("this", voidPtr), param("out_set", voidPtr)}),
            new Spec("0x0041b9f0", "CCareerNode__GetParentLinks", "__thiscall", voidPtr,
                "Signature/comment/tag hardening: source-parity CCareerNode::GetParentLinks scans the career node array and appends child links whose mToNode resolves back to this node. Concrete SPtrSet layout, exact parent-link ordering, and runtime progression behavior remain unproven.",
                graphTags, new ParameterImpl[] {param("this", voidPtr), param("out_set", voidPtr)}),
            new Spec("0x0041bb20", "CCareer__DoesBaseThingExist", "__thiscall", boolType,
                "Signature/comment/tag hardening: source-parity CCareer::DoesBaseThingExist resolves world_number to a node, respects the retail multiplayer/context gate that returns true early, then tests the requested base-things bit. Concrete gate identity, mission-object labels, and runtime behavior remain unproven.",
                baseThingTags, new ParameterImpl[] {param("this", voidPtr), param("world_number", intType), param("offset", intType)}),
            new Spec("0x0041bbb0", "CCareer__IsWorldLater", "__thiscall", boolType,
                "Signature/comment/tag hardening: source-parity CCareer::IsWorldLater resolves both world numbers to career nodes and delegates ancestry testing to CCareer__Later when both nodes exist and differ. Runtime mission-dependency behavior and rebuild parity remain unproven.",
                graphTags, new ParameterImpl[] {param("this", voidPtr), param("current_world", intType), param("dies_on_world", intType)}),
            new Spec("0x0041bc60", "CCareer__Later", "__thiscall", boolType,
                "Signature/comment/tag hardening: source-parity recursive descendant test that walks lower and higher child links from in_dies_on_node until it reaches in_current_node or exhausts both branches. Stack depth, malformed graph behavior, and runtime use remain unproven.",
                graphTags, new ParameterImpl[] {param("this", voidPtr), param("in_dies_on_node", voidPtr), param("in_current_node", voidPtr)}),
            new Spec("0x0041bdf0", "CCareer__ReCalcLinks", "__fastcall", voidType,
                "Signature/comment/tag correction: source-parity CCareer::ReCalcLinks uses END_LEVEL_DATA world completion, child links, secondary-objective gates, and the world 500 mSlots branch at career +0x240c bits 29/30 for source slots 61/62. These mSlots checks are not god-mode flags; runtime progression behavior, script semantics, and rebuild parity remain unproven.",
                new String[] {"static-reaudit", "career-save-wave329", "career-save", "signature-hardened", "source-parity", "career-graph", "save-format"},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x0041c240", "TOTAL_S_GRADES", "__cdecl", boolType,
                "Signature/comment/tag hardening: source-parity TOTAL_S_GRADES iterates num_nodes, converts each career ranking to a grade, counts S-grade nodes, and compares the count with the selected goodie threshold. Runtime unlock recomputation and full goodie coverage remain unproven.",
                gradeTags, new ParameterImpl[] {param("goodie_num", intType)}),
            new Spec("0x0041c330", "CCareer__GetGradeForWorld", "__cdecl", charPtr,
                "Signature/comment/tag hardening: resolves a world to its career node and returns E for incomplete or missing worlds; otherwise converts the node ranking float into the S/A-D/E grade ladder. The decompiler still models the small grade return through out_grade; runtime presentation and exact source identity remain unproven.",
                gradeTags, new ParameterImpl[] {param("out_grade", charPtr), param("world_num", intType)}),
            new Spec("0x0041c450", "CCareer__CountGoodies", "__fastcall", intType,
                "Signature/comment/tag hardening: source-parity CountGoodies scans 300 goodie states at career +0x1f44 and counts entries greater than GS_INSTRUCTIONS, matching GS_NEW/GS_OLD unlocked semantics. Runtime unlock recomputation and hidden Goodie reachability remain unproven.",
                new String[] {"static-reaudit", "career-save-wave329", "career-save", "signature-hardened", "goodies", "save-format"},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x00420ab0", "CGrade__ctor_char", "__thiscall", charPtr,
                "Signature/comment/tag hardening: CGrade inline helper stores the supplied grade byte into the one-byte grade wrapper and returns this. Compiler-inlining provenance and all source callsite identities remain unproven.",
                gradeTags, new ParameterImpl[] {param("this", voidPtr), param("grade", charType)}),
            new Spec("0x00420ac0", "CGrade__operator_gte", "__thiscall", boolType,
                "Signature/comment/tag hardening: CGrade operator >= treats S as the best grade, treats a right-hand S as harder than any non-S grade, and otherwise compares grade characters in ascending rank order. Runtime presentation and every callsite context remain unproven.",
                gradeTags, new ParameterImpl[] {param("this", voidPtr), param("right_grade", charType)}),
            new Spec("0x00420af0", "CCareer__GetNode", "__thiscall", voidPtr,
                "Signature/comment/tag hardening: source-parity CCareer::GetNode returns NULL for negative indices and otherwise returns the node array entry at this+4 plus node_index stride 0x40. Bounds behavior above MAX_NODES and runtime caller safety remain unproven.",
                new String[] {"static-reaudit", "career-save-wave329", "career-save", "signature-hardened", "source-parity", "career-graph", "save-format"},
                new ParameterImpl[] {param("this", voidPtr), param("node_index", intType)}),
            new Spec("0x004213c0", "CCareer__SaveWithFlag", "__thiscall", voidType,
                "Signature/comment/tag hardening: retail save-with-progress helper sets mCareerInProgress at +0x2488, writes the version word, copies the fixed CCareer dump, serializes active options entries, and finishes with OptionsTail_Write. Save-file byte preservation rules, runtime save success, and rebuild parity remain unproven.",
                serializeTags, new ParameterImpl[] {param("this", voidPtr), param("dest", voidPtr)}),
            new Spec("0x00421430", "CCareer__GetSaveSize", "__cdecl", intType,
                "Signature/comment/tag hardening: retail save-size helper starts at the version+fixed-career size, adds 0x20 for each active options entry, then adds the 0x56-byte tail; current Steam saves are observed as 0x2714 bytes. Other option-table states and runtime save allocation remain unproven.",
                serializeTags, new ParameterImpl[] {}),
            new Spec("0x00421550", "CCareer__GetAndResetGoodieNewCount", "__cdecl", intType,
                "Signature/comment/tag hardening: debriefing helper returns the global new_goodie_count value and clears it to zero. Runtime debriefing display behavior, thread-safety, and full unlock recomputation remain unproven.",
                new String[] {"static-reaudit", "career-save-wave329", "career-save", "signature-hardened", "goodies", "debriefing"},
                new ParameterImpl[] {}),
            new Spec("0x00421560", "CCareer__GetAndResetFirstGoodie", "__cdecl", boolType,
                "Signature/comment/tag hardening: debriefing helper returns the global first_goodie flag and clears it to false. Runtime first-goodie presentation behavior and full unlock recomputation remain unproven.",
                new String[] {"static-reaudit", "career-save-wave329", "career-save", "signature-hardened", "goodies", "debriefing"},
                new ParameterImpl[] {}),
            new Spec("0x00421570", "CCareer__IsEpisodeAvailable", "__stdcall", boolType,
                "Signature/comment/tag hardening: source-parity episode gate used by goodie instruction logic; episode 0/1 are always available and later cases test completion of episode-boundary worlds. Runtime frontend availability behavior and every world-id branch label remain unproven.",
                new String[] {"static-reaudit", "career-save-wave329", "career-save", "signature-hardened", "goodies", "career-graph"},
                new ParameterImpl[] {param("ep", intType)}),
            new Spec("0x004218f0", "CCareer__GetKillCounterTopByte_23F4", "__fastcall", intType,
                "Signature/comment/tag hardening: options/profile helper reads the top byte at in-memory career offset 0x23f4 and subtracts 0x80; this is not the lower 24-bit kill-count payload and should not be used as a true-view save patch offset. Runtime menu use and exact display semantics remain unproven.",
                new String[] {"static-reaudit", "career-save-wave329", "career-save", "signature-hardened", "save-format", "kill-counters"},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x00421970", "CCareer__NodeArrayAt", "__thiscall", voidPtr,
                "Signature/comment/tag hardening: node-array accessor returns this + node_index * 0x40 for callers that already pass the node-array base rather than the CCareer object base. Caller ownership, bounds behavior, and runtime safety remain unproven.",
                graphTags, new ParameterImpl[] {param("this", voidPtr), param("node_index", intType)}),
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }
        println("SUMMARY: updated=" + stats.updated + " skipped=" + stats.skipped + " renamed=0 missing=" + stats.missing + " bad=" + stats.bad);
        if (stats.missing != 0 || stats.bad != 0) {
            throw new IllegalStateException("Career save helper signature tranche failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
