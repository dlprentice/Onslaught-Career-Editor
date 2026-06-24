//@category Symbol

import ghidra.app.cmd.disassemble.DisassembleCommand;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.ByteDataType;
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

public class ApplyRadarWarningWave488 extends GhidraScript {
    private static class Spec {
        final String address;
        final String oldName;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] parameters;
        final String comment;
        final boolean createIfMissing;
        final String[] tags;

        Spec(
                String address,
                String oldName,
                String name,
                String callingConvention,
                DataType returnType,
                ParameterImpl[] parameters,
                String comment,
                boolean createIfMissing,
                String[] tags) {
            this.address = address;
            this.oldName = oldName;
            this.name = name;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.parameters = parameters;
            this.comment = comment;
            this.createIfMissing = createIfMissing;
            this.tags = tags;
        }
    }

    private static class Stats {
        int updated = 0;
        int skipped = 0;
        int created = 0;
        int wouldCreate = 0;
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
        Address result = toAddr(addressText);
        if (result == null) {
            throw new IllegalArgumentException("Bad address: " + addressText);
        }
        return result;
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

    private ParameterImpl param(String name, DataType dataType) throws Exception {
        return new ParameterImpl(name, dataType, currentProgram);
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
            "radar-warning-wave488",
            "radar-warning-receiver",
            "retail-binary-evidence"
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

    private Function createFunctionAt(Spec spec, Address address) throws Exception {
        DisassembleCommand cmd = new DisassembleCommand(address, null, true);
        cmd.applyTo(currentProgram, monitor);
        Function fn = createFunction(address, spec.name);
        if (fn == null) {
            fn = functionAtEntry(address);
        }
        if (fn == null) {
            throw new IllegalStateException("Function create failed at " + spec.address);
        }
        if (!fn.getName().equals(spec.name)) {
            fn.setName(spec.name, SourceType.USER_DEFINED);
        }
        return fn;
    }

    private void applySpec(Spec spec, boolean dryRun, Stats stats) {
        try {
            Address address = addr(spec.address);
            Function fn = functionAtEntry(address);
            boolean createdNow = false;

            if (fn == null) {
                if (!spec.createIfMissing) {
                    stats.missing++;
                    println("FAIL: " + spec.address + " " + spec.name + " Function not found");
                    return;
                }
                if (dryRun) {
                    stats.wouldCreate++;
                    println("DRY: " + spec.address + " <missing> -> create " + expectedSignature(spec));
                    return;
                }
                fn = createFunctionAt(spec, address);
                createdNow = true;
                stats.created++;
            }

            boolean needsRename = !fn.getName().equals(spec.name);
            if (needsRename && spec.oldName != null && !spec.oldName.isEmpty() && !fn.getName().equals(spec.oldName)) {
                throw new IllegalStateException("Unexpected function name at " + spec.address + ": " + fn.getName());
            }

            if (dryRun) {
                println("DRY: " + spec.address + " " + fn.getName() + " -> " + expectedSignature(spec));
                if (needsRename) {
                    stats.wouldRename++;
                }
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

            Function readBack = functionAtEntry(address);
            if (readBack == null) {
                throw new IllegalStateException("Read-back missing at " + spec.address);
            }
            if (!readBack.getName().equals(spec.name)) {
                throw new IllegalStateException("Read-back name mismatch at " + spec.address + ": " + readBack.getName());
            }
            String actualSignature = readBack.getSignature().toString();
            String expectedSignature = expectedSignature(spec);
            if (!actualSignature.equals(expectedSignature)) {
                throw new IllegalStateException(
                    "Read-back signature mismatch at " + spec.address + ": " + actualSignature + " != " + expectedSignature
                );
            }
            if (!spec.comment.equals(readBack.getComment())) {
                throw new IllegalStateException("Read-back comment mismatch at " + spec.address);
            }
            Set<String> actualTags = tagNames(readBack);
            for (String tag : spec.tags) {
                if (!actualTags.contains(tag)) {
                    throw new IllegalStateException("Read-back missing tag at " + spec.address + ": " + tag);
                }
            }

            stats.updated++;
            println("OK: " + spec.address + " " + readBack.getName() + " -> " + actualSignature + (createdNow ? " created" : ""));
            Thread.sleep(50);
        } catch (Exception ex) {
            stats.bad++;
            println("FAIL: " + spec.address + " " + spec.name + " " + ex.getClass().getSimpleName() + ": " + ex.getMessage());
        }
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");
        println("Mode: " + (dryRun ? "dry" : "apply"));

        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);
        DataType byteType = ByteDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x00405a20",
                "CRadarWarningReceiver__scalar_deleting_dtor",
                "CRadarWarningReceiver__scalar_deleting_dtor",
                "__thiscall",
                voidPtr,
                new ParameterImpl[] {param("this", voidPtr), param("flags", byteType)},
                "Wave488 tag/comment refresh for the CRadarWarningReceiver scalar deleting destructor. Vtable 0x005d8810 slot 1 points here; the wrapper calls CRadarWarningReceiver__dtor, tests delete flag bit 0 from the RET 0x4 stack byte, optionally frees this through CDXMemoryManager__Free(&DAT_009c3df0, this), and returns this. Static retail evidence only; exact class layout, runtime lifetime behavior, and rebuild parity remain unproven.",
                false,
                tags("destructor", "scalar-deleting-dtor", "vtable-readback", "signature-preserved", "comment-hardened")
            ),
            new Spec(
                "0x004d65a0",
                "CRadarWarningReceiver__Init",
                "CRadarWarningReceiver__Init",
                "__thiscall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr), param("config_record", voidPtr)},
                "Wave488 signature/comment hardening: CBattleEngine__Init calls this RWR initializer. RET 0x4 plus ECX/stack use show a this pointer and one config_record argument. The body calls VFuncSlot_03_0044a830 to copy the first three config dwords into this+0x08..0x10, copies range/update interval from config_record+0x0c/+0x10 into this+0x14/+0x18, schedules event 4000 through CEventManager__AddEvent_AtTime, clears this+0x2c, and seeds this+0x30 to -1.0. Static retail evidence only; exact config layout, runtime scheduling behavior, and rebuild parity remain unproven.",
                false,
                tags("init", "event-4000", "signature-corrected", "comment-hardened")
            ),
            new Spec(
                "0x004d6600",
                "CRadarWarningReceiver__dtor",
                "CRadarWarningReceiver__dtor",
                "__fastcall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave488 signature/comment hardening: destructor body called by CRadarWarningReceiver__scalar_deleting_dtor. It restores vtable 0x005d8810, walks the tracked-threat list rooted around this+0x1c/this+0x24, tears down each threat entry's active reader at entry+0x0c, frees each entry through CDXMemoryManager__Free(&DAT_009c3df0, entry), clears the pointer set, and delegates to CMonitor__Shutdown. Static retail evidence only; exact list layout, exception-cleanup semantics, runtime lifetime behavior, and rebuild parity remain unproven.",
                false,
                tags("destructor", "tracked-threat-list", "signature-corrected", "comment-hardened")
            ),
            new Spec(
                "0x004d66b0",
                "CRadarWarningReceiver__Update",
                "CRadarWarningReceiver__Update",
                "__fastcall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave488 signature/comment hardening: event 4000 dispatch calls this RWR update loop. The body clears existing threat-entry active flags, scans the DAT_008551a0 candidate list, computes source-to-target distance and bearing, filters by range this+0x14, owner pointer this+0x08, and weapon/lock state, creates or updates 0x18-byte threat entries with CGenericActiveReader state, sets the owner forward-threat flag at owner+0x5e4 for player-owned threats within the angle window, reschedules event 4000 using this+0x18, plays event 0x0fa2 when the threat count grows, and removes stale entries. Static retail evidence only; exact candidate-list ownership, concrete CRadarWarningReceiver/threat layouts, runtime HUD/audio behavior, and rebuild parity remain unproven.",
                false,
                tags("update-loop", "event-4000", "event-0fa2", "tracked-threat-list", "signature-corrected", "comment-hardened")
            ),
            new Spec(
                "0x004d6a10",
                "",
                "CRadarWarningReceiver__VFunc_00_UpdateOnEvent4000",
                "__thiscall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr), param("message", voidPtr)},
                "Wave488 function-boundary recovery and signature/comment hardening: CRadarWarningReceiver vtable 0x005d8810 slot 0 points to this previously missing 5-instruction body. It reads the stack message pointer, compares message+0x04 against event id 4000/0x0fa0, calls CRadarWarningReceiver__Update with the preserved ECX receiver only on a match, and returns with RET 0x4. Static retail vtable/instruction evidence only; exact virtual interface name, message layout, runtime scheduler behavior, and rebuild parity remain unproven.",
                true,
                tags("vfunc-slot-00", "event-4000", "function-created", "signature-corrected", "comment-hardened")
            )
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }

        println("--- SUMMARY ---");
        println(
            "updated=" + stats.updated +
            " skipped=" + stats.skipped +
            " created=" + stats.created +
            " would_create=" + stats.wouldCreate +
            " renamed=" + stats.renamed +
            " would_rename=" + stats.wouldRename +
            " missing=" + stats.missing +
            " bad=" + stats.bad
        );
        if (stats.bad > 0 || stats.missing > 0) {
            throw new IllegalStateException("ApplyRadarWarningWave488 failed; see log");
        }
    }
}
