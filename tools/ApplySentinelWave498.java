//@category Symbol

import ghidra.app.cmd.disassemble.DisassembleCommand;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.BooleanDataType;
import ghidra.program.model.data.ByteDataType;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.FunctionTag;
import ghidra.program.model.listing.Parameter;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplySentinelWave498 extends GhidraScript {
    private static class Spec {
        final String address;
        final String[] allowedExistingNames;
        final String newName;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] parameters;
        final String comment;
        final boolean createIfMissing;
        final String[] tags;

        Spec(
                String address,
                String[] allowedExistingNames,
                String newName,
                String callingConvention,
                DataType returnType,
                ParameterImpl[] parameters,
                String comment,
                boolean createIfMissing,
                String[] tags) {
            this.address = address;
            this.allowedExistingNames = allowedExistingNames;
            this.newName = newName;
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

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "sentinel-wave498",
            "retail-binary-evidence"
        };
        String[] result = new String[common.length + extras.length];
        System.arraycopy(common, 0, result, 0, common.length);
        System.arraycopy(extras, 0, result, common.length, extras.length);
        return result;
    }

    private boolean allowedName(Spec spec, String actual) {
        if (actual.equals(spec.newName)) {
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
            .append(spec.newName)
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

    private boolean sameDataType(DataType actual, DataType expected) {
        if (actual == null || expected == null) {
            return actual == expected;
        }
        return actual.isEquivalent(expected) || actual.getDisplayName().equals(expected.getDisplayName());
    }

    private boolean signatureMatches(Function fn, Spec spec) {
        if (!spec.callingConvention.equals(fn.getCallingConventionName())) {
            return false;
        }
        if (!sameDataType(fn.getReturnType(), spec.returnType)) {
            return false;
        }
        if (fn.getParameterCount() != spec.parameters.length) {
            return false;
        }
        for (int i = 0; i < spec.parameters.length; i++) {
            Parameter actual = fn.getParameter(i);
            ParameterImpl expected = spec.parameters[i];
            if (!actual.getName().equals(expected.getName())) {
                return false;
            }
            if (!sameDataType(actual.getDataType(), expected.getDataType())) {
                return false;
            }
        }
        return true;
    }

    private boolean hasAllTags(Function fn, String[] tags) {
        Set<String> existing = new HashSet<>();
        for (FunctionTag tag : fn.getTags()) {
            existing.add(tag.getName());
        }
        for (String tag : tags) {
            if (!existing.contains(tag)) {
                return false;
            }
        }
        return true;
    }

    private boolean needsUpdate(Function fn, Spec spec) {
        if (!fn.getName().equals(spec.newName)) {
            return true;
        }
        if (!signatureMatches(fn, spec)) {
            return true;
        }
        String existingComment = fn.getComment();
        if (existingComment == null || !existingComment.equals(spec.comment)) {
            return true;
        }
        return !hasAllTags(fn, spec.tags);
    }

    private Function createFunctionAt(Spec spec, Address address) throws Exception {
        DisassembleCommand cmd = new DisassembleCommand(address, null, true);
        cmd.applyTo(currentProgram, monitor);
        Function fn = createFunction(address, spec.newName);
        if (fn == null) {
            fn = functionAtEntry(address);
        }
        if (fn == null) {
            throw new IllegalStateException("Function create failed at " + spec.address);
        }
        if (!fn.getName().equals(spec.newName)) {
            fn.setName(spec.newName, SourceType.USER_DEFINED);
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
                    println("MISSING: " + spec.address + " " + spec.newName);
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

            if (!allowedName(spec, fn.getName())) {
                throw new IllegalStateException("Unexpected function name at " + spec.address + ": " + fn.getName());
            }

            boolean renameNeeded = !fn.getName().equals(spec.newName);
            boolean updateNeeded = needsUpdate(fn, spec);
            if (!updateNeeded) {
                println("SKIP: " + spec.address + " " + spec.newName);
                stats.skipped++;
                return;
            }
            if (dryRun) {
                println("DRY: " + spec.address + " " + fn.getName() + " -> " + expectedSignature(spec));
                stats.skipped++;
                if (renameNeeded) {
                    stats.wouldRename++;
                }
                return;
            }

            if (renameNeeded) {
                fn.setName(spec.newName, SourceType.USER_DEFINED);
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
            if (!readBack.getName().equals(spec.newName)) {
                throw new IllegalStateException("Read-back name mismatch at " + spec.address + ": " + readBack.getName());
            }
            if (!signatureMatches(readBack, spec)) {
                throw new IllegalStateException("Read-back signature mismatch at " + spec.address + ": " + readBack.getSignature());
            }
            if (!spec.comment.equals(readBack.getComment())) {
                throw new IllegalStateException("Read-back comment mismatch at " + spec.address);
            }
            if (!hasAllTags(readBack, spec.tags)) {
                throw new IllegalStateException("Read-back missing one or more tags at " + spec.address);
            }

            stats.updated++;
            println("OK: " + spec.address + " " + readBack.getSignature() + (createdNow ? " created" : ""));
            Thread.sleep(50);
        } catch (Exception ex) {
            stats.bad++;
            println("FAIL: " + spec.address + " " + spec.newName + " " + ex.getMessage());
        }
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");
        println("Mode: " + (dryRun ? "dry" : "apply"));

        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);
        DataType boolType = BooleanDataType.dataType;
        DataType byteType = ByteDataType.dataType;
        DataType intType = IntegerDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x004dea50",
                new String[] {"CSentinel__Constructor"},
                "CSentinel__Init",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("init_data", voidPtr)
                },
                "Wave498 boundary/name correction: CSentinel primary table 0x005e0904 slot 0 points here and RET 0x4 confirms one init_data stack argument after this. The body edits init_data flags/fields, delegates to CGroundUnit__Init, optionally selects the inactive animation, allocates Sentinel.cpp line-backed helper objects, attaches CMCSentinel motion control at this+0x70, stores additional helper pointers at this+0x208 and this+0x13c, clears a this+0x12c record, and registers through DAT_00855090. Static retail-binary evidence only; exact source body identity, concrete helper layouts, runtime sentinel behavior, and rebuild parity remain unproven.",
                true,
                tags("sentinel", "init", "boundary-recovered", "vtable-slot-0", "name-corrected")
            ),
            new Spec(
                "0x004dec00",
                new String[] {"CSentinel__scalar_deleting_dtor"},
                "CSentinel__ScalarDeletingDestructor",
                "__thiscall",
                voidPtr,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("flags", byteType)
                },
                "Wave498 signature/name/comment hardening: secondary Sentinel table 0x005deca0 slot 0 points here. The wrapper calls CSentinel__Destructor(this), frees this through CDXMemoryManager__Free(&DAT_009c3df0, this) when flags bit 0 is set, returns this, and RET 0x4 confirms one delete-flags stack argument. Static retail-binary evidence only; allocator ownership, runtime destruction behavior, and rebuild parity remain unproven.",
                false,
                tags("sentinel", "scalar-deleting-destructor", "vtable-slot-0", "name-corrected", "signature-corrected")
            ),
            new Spec(
                "0x004dec20",
                new String[] {},
                "CSentinel__Destructor",
                "__fastcall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr)
                },
                "Wave498 signature/comment hardening: destructor body restores the base CMonitor-style vtable 0x005d8d1c, removes CSPtrSet-linked cells at this+0x28, this+0x24, and this+0x0c when populated, then calls CMonitor__Shutdown. Static retail-binary evidence only; concrete Sentinel layout, runtime cleanup behavior, exact base identity, and rebuild parity remain unproven.",
                false,
                tags("sentinel", "destructor", "signature-corrected", "comment-hardened")
            ),
            new Spec(
                "0x004decc0",
                new String[] {},
                "CSentinel__UpdateFlamethrowers",
                "__fastcall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr)
                },
                "Wave498 signature/comment hardening: Sentinel table 0x005e0904 slot 57 points here. The body updates ground-unit linked effects by height clearance, walks the this+0x17c linked list, filters entries named Sentinel Flamethrower, checks distance/range eligibility, calls CSentinel__CheckWeaponSlot(this, burst_context), and spawns a projectile burst only when all gates pass. Static retail-binary evidence only; concrete list/weapon layouts, runtime firing behavior, and rebuild parity remain unproven.",
                false,
                tags("sentinel", "flamethrower", "vtable-slot-57", "signature-corrected", "comment-hardened")
            ),
            new Spec(
                "0x004ded30",
                new String[] {},
                "CSentinel__Activate",
                "__fastcall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr)
                },
                "Wave498 signature/comment hardening: Sentinel table 0x005e0904 slot 13 points here. The body resolves the activate animation through the render/model object at this+0x30, finds its animation index, and dispatches that index through the vtable slot at +0xf0. Static retail-binary evidence only; exact animation owner layout, runtime state transition behavior, and rebuild parity remain unproven.",
                false,
                tags("sentinel", "activate", "animation", "vtable-slot-13", "signature-corrected", "comment-hardened")
            ),
            new Spec(
                "0x004ded60",
                new String[] {},
                "CSentinel__Deactivate",
                "__fastcall",
                intType,
                new ParameterImpl[] {
                    param("this", voidPtr)
                },
                "Wave498 signature/comment hardening: Sentinel table 0x005e0904 slot 50 points here. The body reads the current animation state, compares it to the activate animation index, switches to the looping inactive animation when appropriate, calls the slot-22 state-change helper, and returns 0. Static retail-binary evidence only; exact return contract, runtime animation behavior, and rebuild parity remain unproven.",
                false,
                tags("sentinel", "deactivate", "animation", "vtable-slot-50", "signature-corrected", "comment-hardened")
            ),
            new Spec(
                "0x004dee00",
                new String[] {},
                "CSentinel__CheckWeaponSlot",
                "__thiscall",
                intType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("weapon_context", voidPtr)
                },
                "Wave498 signature/comment hardening: CSentinel__UpdateFlamethrowers calls this with each candidate burst/weapon context. The body maps weapon_context+0xac values 2..9 to slot ids 9..16, walks the this+0x19c linked list, returns 0 when an occupied entry has +0x270 matching that slot id, and returns 1 otherwise. Static retail-binary evidence only; exact weapon/list layouts, runtime firing behavior, and rebuild parity remain unproven.",
                false,
                tags("sentinel", "weapon-slot", "flamethrower", "signature-corrected", "comment-hardened")
            )
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }

        println(
            "SUMMARY: updated=" + stats.updated +
            " skipped=" + stats.skipped +
            " created=" + stats.created +
            " would_create=" + stats.wouldCreate +
            " renamed=" + stats.renamed +
            " would_rename=" + stats.wouldRename +
            " missing=" + stats.missing +
            " bad=" + stats.bad
        );
        if (stats.bad > 0 || stats.missing > 0) {
            throw new IllegalStateException("Wave498 Sentinel apply had failures");
        }
        if (!dryRun) {
            currentProgram.flushEvents();
            Thread.sleep(250);
        }
    }
}
