//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.ByteDataType;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.FunctionManager;
import ghidra.program.model.listing.FunctionTag;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyInfantryGuideWave417 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final String comment;
        final String[] allowedExistingNames;
        final String[] tags;
        final String boundaryMoveFrom;
        final boolean createIfMissing;
        final ParameterImpl[] parameters;

        Spec(
                String address,
                String name,
                String callingConvention,
                DataType returnType,
                String comment,
                String[] allowedExistingNames,
                String[] tags,
                String boundaryMoveFrom,
                boolean createIfMissing,
                ParameterImpl[] parameters) {
            this.address = address;
            this.name = name;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.comment = comment;
            this.allowedExistingNames = allowedExistingNames;
            this.tags = tags;
            this.boundaryMoveFrom = boundaryMoveFrom;
            this.createIfMissing = createIfMissing;
            this.parameters = parameters;
        }
    }

    private static class Stats {
        int updated = 0;
        int skipped = 0;
        int created = 0;
        int wouldCreate = 0;
        int boundaryMoved = 0;
        int wouldBoundaryMove = 0;
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

    private Function functionAtEntry(String addressText) {
        Address address = addr(addressText);
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
            "infantry-guide-wave417",
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

    private Function moveBoundaryIfNeeded(Spec spec, boolean dryRun, Stats stats) throws Exception {
        Function newFn = functionAtEntry(spec.address);
        if (newFn != null) {
            return newFn;
        }

        Function oldFn = functionAtEntry(spec.boundaryMoveFrom);
        if (oldFn == null) {
            throw new IllegalStateException("Boundary move requires old function at " + spec.boundaryMoveFrom);
        }
        if (!allowedName(spec, oldFn.getName())) {
            throw new IllegalStateException("Unexpected old boundary name at " + spec.boundaryMoveFrom + ": " + oldFn.getName());
        }

        if (dryRun) {
            println("DRY: would remove " + spec.boundaryMoveFrom + " " + oldFn.getName() + " and recreate at " + spec.address);
            stats.wouldBoundaryMove++;
            return oldFn;
        }

        FunctionManager fm = currentProgram.getFunctionManager();
        boolean removed = fm.removeFunction(addr(spec.boundaryMoveFrom));
        if (!removed) {
            throw new IllegalStateException("Failed to remove old function at " + spec.boundaryMoveFrom);
        }

        Address newEntry = addr(spec.address);
        disassemble(newEntry);
        newFn = createFunction(newEntry, null);
        if (newFn == null) {
            newFn = functionAtEntry(spec.address);
        }
        if (newFn == null) {
            throw new IllegalStateException("Function not present after create at " + spec.address);
        }
        newFn.setName(spec.name, SourceType.USER_DEFINED);
        stats.boundaryMoved++;
        println("OK: moved boundary " + spec.boundaryMoveFrom + " -> " + spec.address);
        return newFn;
    }

    private Function getOrCreate(Spec spec, boolean dryRun, Stats stats) throws Exception {
        if (spec.boundaryMoveFrom != null && !spec.boundaryMoveFrom.isEmpty()) {
            return moveBoundaryIfNeeded(spec, dryRun, stats);
        }

        Function fn = functionAtEntry(spec.address);
        if (fn != null) {
            return fn;
        }
        if (!spec.createIfMissing) {
            stats.missing++;
            println("FAIL: " + spec.address + " " + spec.name + " Function not found");
            return null;
        }
        if (dryRun) {
            println("DRY: would create " + spec.address + " " + spec.name);
            stats.wouldCreate++;
            return null;
        }

        Address address = addr(spec.address);
        disassemble(address);
        fn = createFunction(address, null);
        if (fn == null) {
            fn = functionAtEntry(spec.address);
        }
        if (fn == null) {
            throw new IllegalStateException("Function create failed at " + spec.address);
        }
        fn.setName(spec.name, SourceType.USER_DEFINED);
        stats.created++;
        println("OK: created " + spec.address + " " + spec.name);
        return fn;
    }

    private void applySpec(Spec spec, boolean dryRun, Stats stats) {
        try {
            Function fn = getOrCreate(spec, dryRun, stats);
            if (fn == null) {
                return;
            }
            if (!allowedName(spec, fn.getName())) {
                throw new IllegalStateException("Unexpected function name at " + spec.address + ": " + fn.getName());
            }

            boolean needsRename = !fn.getName().equals(spec.name);
            if (dryRun) {
                if (needsRename) {
                    stats.wouldRename++;
                }
                println("DRY: " + spec.address + " " + fn.getName() + " -> " + expectedSignature(spec));
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

            Function readBack = functionAtEntry(spec.address);
            if (readBack == null) {
                throw new IllegalStateException("Read-back missing at " + spec.address);
            }
            if (!readBack.getName().equals(spec.name)) {
                throw new IllegalStateException("Read-back name mismatch at " + spec.address + ": " + readBack.getName());
            }
            String actualSignature = readBack.getSignature().toString();
            if (!actualSignature.equals(expectedSignature(spec))) {
                throw new IllegalStateException("Read-back signature mismatch at " + spec.address + ": " + actualSignature + " != " + expectedSignature(spec));
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

            println("OK: " + spec.address + " " + readBack.getSignature().toString());
            stats.updated++;
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
                "0x0048a3c0",
                "CInfantryGuide__ctor",
                "__thiscall",
                voidPtr,
                "Wave417 signature/name hardening: CInfantryGuide constructor calls CGuide__ctor_base with owner_unit, installs vtable 0x005dbfa8, allocates two 0x54 guide buffers, initializes the reader field, schedules event 2000, and keeps runtime guide behavior and rebuild parity remain unproven.",
                new String[] {"CInfantryGuide__ctor_like_0048a3c0"},
                tags("infantry-guide", "constructor", "signature-corrected", "comment-hardened"),
                "",
                false,
                new ParameterImpl[] {param("this", voidPtr), param("owner_unit", voidPtr)}),
            new Spec(
                "0x0048a4b0",
                "SharedGuide__GetField24Block_0048a4b0",
                "__fastcall",
                voidPtr,
                "Wave417 recovered shared guide vtable helper: returns this+0x24 and is referenced by CInfantryGuide and CGroundVehicleGuide vtables. Exact field semantics, runtime guide behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("guide", "shared-helper", "function-boundary", "signature-hardened", "comment-hardened"),
                "",
                true,
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec(
                "0x0048a4c0",
                "CInfantryGuide__scalar_deleting_dtor",
                "__thiscall",
                voidPtr,
                "Wave417 name/signature correction: scalar-deleting destructor wrapper calls CInfantryGuide__dtor, checks flags bit 0, optionally frees through OID__FreeObject, returns this, and keeps runtime cleanup behavior unproven.",
                new String[] {"CInfantryGuide__VFunc_01_0048a4c0"},
                tags("infantry-guide", "destructor", "owner-corrected", "signature-corrected", "comment-hardened"),
                "",
                false,
                new ParameterImpl[] {param("this", voidPtr), param("flags", byteType)}),
            new Spec(
                "0x0048a4e0",
                "CInfantryGuide__dtor",
                "__fastcall",
                voidType,
                "Wave417 signature/comment hardening: destructor body reached by CInfantryGuide scalar deleting destructor removes the reader link at this+0x44, frees guide buffers +0x3c/+0x34, calls CMonitor__Shutdown, and keeps runtime cleanup behavior unproven.",
                new String[] {},
                tags("infantry-guide", "destructor", "signature-hardened", "comment-hardened"),
                "",
                false,
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec(
                "0x0048a570",
                "CInfantryGuide__UpdateGuidanceState_0048a570",
                "__fastcall",
                voidType,
                "Wave417 recovered CInfantryGuide vtable slot 3 body: updates guide state and target line using owner/reader positions. Stuart source body is absent; runtime guide behavior and rebuild parity remain unproven.",
                new String[] {},
                tags("infantry-guide", "vtable-slot", "function-boundary", "signature-hardened", "comment-hardened"),
                "",
                true,
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec(
                "0x0048ac70",
                "CInfantryGuide__HandleTargetRecheckEvent",
                "__thiscall",
                voidType,
                "Wave417 function-boundary correction: CInfantryGuide event handler starts at 0x0048ac70, not stale mid-body 0x0048ac80. It checks event id 0x7d0, calls CInfantryGuide__SelectNearestTargetReader, reschedules event 2000, and keeps runtime guide behavior unproven.",
                new String[] {"CInfantryGuide__SelectTargetAndScheduleRecheck"},
                tags("infantry-guide", "event-handler", "function-boundary", "signature-corrected", "comment-hardened"),
                "0x0048ac80",
                false,
                new ParameterImpl[] {param("this", voidPtr), param("event", voidPtr)}),
            new Spec(
                "0x0048ace0",
                "CInfantryGuide__SelectNearestTargetReader",
                "__fastcall",
                voidType,
                "Wave417 signature/comment hardening: clears active reader at +0x44, scans MapWho radius 1.0, filters candidate flags/team, chooses nearest hostile/preferred reader using threshold constants 0x005d8568/0x005dbfd0, and keeps runtime target behavior unproven.",
                new String[] {},
                tags("infantry-guide", "target-selection", "signature-hardened", "comment-hardened"),
                "",
                false,
                new ParameterImpl[] {param("this", voidPtr)})
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            if (monitor.isCancelled()) {
                throw new RuntimeException("Cancelled");
            }
            applySpec(spec, dryRun, stats);
        }

        println(
            "SUMMARY updated=" + stats.updated
            + " skipped=" + stats.skipped
            + " created=" + stats.created
            + " would_create=" + stats.wouldCreate
            + " boundary_moved=" + stats.boundaryMoved
            + " would_boundary_move=" + stats.wouldBoundaryMove
            + " renamed=" + stats.renamed
            + " would_rename=" + stats.wouldRename
            + " missing=" + stats.missing
            + " bad=" + stats.bad
        );

        if (stats.missing != 0 || stats.bad != 0) {
            throw new IllegalStateException("Wave417 InfantryGuide apply had failures");
        }
    }
}
