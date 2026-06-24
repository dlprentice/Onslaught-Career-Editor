//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
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

public class ApplyCollisionRoundTailWave494 extends GhidraScript {
    private static class Spec {
        final String address;
        final String oldName;
        final String newName;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] parameters;
        final String comment;
        final String[] tags;

        Spec(
                String address,
                String oldName,
                String newName,
                String callingConvention,
                DataType returnType,
                ParameterImpl[] parameters,
                String comment,
                String[] tags) {
            this.address = address;
            this.oldName = oldName;
            this.newName = newName;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.parameters = parameters;
            this.comment = comment;
            this.tags = tags;
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

    private void applySpec(Spec spec, boolean dryRun, Stats stats) throws Exception {
        Function fn = functionAtEntry(spec.address);
        if (fn == null) {
            println("MISSING: " + spec.address);
            stats.missing++;
            return;
        }
        String currentName = fn.getName();
        if (!currentName.equals(spec.oldName) && !currentName.equals(spec.newName)) {
            println("BADNAME: " + spec.address + " " + currentName + " expected " + spec.oldName + " or " + spec.newName);
            stats.bad++;
            return;
        }
        boolean renameNeeded = !currentName.equals(spec.newName);
        boolean updateNeeded = needsUpdate(fn, spec);
        if (!updateNeeded) {
            println("SKIP: " + spec.address + " " + spec.newName);
            stats.skipped++;
            return;
        }
        if (dryRun) {
            println("DRY: " + spec.address + " " + currentName + " -> " + spec.newName + " :: " + expectedSignature(spec));
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
        println("OK: " + spec.address + " " + spec.newName + " :: " + expectedSignature(spec));
        stats.updated++;
    }

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "round-wave494",
            "round",
            "projectile",
            "retail-binary-evidence",
            "signature-corrected",
            "comment-hardened"
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
        DataType intType = IntegerDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x004d8a50",
                "CCollisionSeekingRound__VFunc_01_004d8a50",
                "CCollisionSeekingRound__ScalarDeletingDestructor_004d8a50",
                "__thiscall",
                voidPtr,
                new ParameterImpl[] {param("this", voidPtr), param("deleteFlags", intType)},
                "Wave494 name/signature/comment hardening: vtable 0x005de950 slot 1 points here. RET 0x4 plus ECX/stack use show a scalar-deleting destructor wrapper; the body calls CCollisionSeekingRound__ShutdownMonitorAndDestruct(this), frees this through CDXMemoryManager__Free when deleteFlags bit 0 is set, and returns this. Static retail evidence only; exact source destructor spelling, relationship to older recovered helper wrappers, concrete layout, runtime collision/projectile teardown behavior, and rebuild parity remain unproven.",
                tags("name-corrected", "destructor", "scalar-deleting-dtor", "collision-seeking")
            ),
            new Spec(
                "0x004d8a70",
                "CCollisionSeekingRound__ShutdownMonitorAndDestruct",
                "CCollisionSeekingRound__ShutdownMonitorAndDestruct",
                "__fastcall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave494 signature/comment hardening: called by the 0x004d8a50 scalar-deleting wrapper. Register-only ECX receiver; the SEH-wrapped body shuts down the monitor subobject at this+0x24 via CMonitor__Shutdown, then calls CCollisionSeekingRound__Destructor(this). Static retail evidence only; concrete monitor/subobject layout, exact source helper name, destructor side-effect completeness, runtime teardown behavior, and rebuild parity remain unproven.",
                tags("destructor", "monitor", "collision-seeking")
            ),
            new Spec(
                "0x004d8dc0",
                "VFuncSlot_02_004d8dc0",
                "VFuncSlot_02_004d8dc0",
                "__fastcall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave494 signature/comment hardening: CRound vtable 0x005de82c slot 2 and CMissile-style vtable 0x005e3ba4 slot 2 both point here. Register-only ECX receiver; the body conditionally removes this from global active-reader sets using round-config this+0xf0 fields, clears the particle/effect link at this+0xe0, removes monitor reader ids from this+0xec/this+0xe8 contexts, clears the active reader at this+0xe8, then delegates to VFuncSlot_02_004f41b0. Static retail evidence only; exact source virtual name, owner coverage, concrete reader/effect layout, runtime projectile behavior, and rebuild parity remain unproven.",
                tags("shared-vfunc", "active-reader", "particle-effect")
            ),
            new Spec(
                "0x004d9d60",
                "CEngine__InitRoundLaunchStateDefaults",
                "CEngine__InitRoundLaunchStateDefaults",
                "__fastcall",
                voidType,
                new ParameterImpl[] {param("state", voidPtr)},
                "Wave494 signature/comment hardening: register-only ECX receiver initializes a 0x38-byte round launch/config state record. The body clears offsets 0x00/0x04/0x08/0x0c/0x14/0x24/0x28/0x30/0x34, sets 0x10 and 0x20 to 1, sets 0x18 and 0x1c to 2, and stores -1.0f bits at 0x2c. Static retail evidence only; exact source type, CEngine owner spelling, field names, runtime projectile launch behavior, and rebuild parity remain unproven.",
                tags("launch-state", "config-defaults")
            ),
            new Spec(
                "0x004d9da0",
                "CCSRay__VFunc_01_004d9da0",
                "CCSRay__ScalarDeletingDestructor_004d9da0",
                "__thiscall",
                voidPtr,
                new ParameterImpl[] {param("this", voidPtr), param("deleteFlags", intType)},
                "Wave494 name/signature/comment hardening: adjacent CCSRay-style vtable 0x005de980 slot 1 points here. RET 0x4 plus ECX/stack use show a scalar-deleting destructor wrapper; the body calls CCSRay__DestructorBody_004d9dc0(this), frees this through CDXMemoryManager__Free when deleteFlags bit 0 is set, and returns this. Static retail evidence only; exact CCSRay source type/name, concrete layout, runtime ray/effect behavior, and rebuild parity remain unproven.",
                tags("name-corrected", "destructor", "scalar-deleting-dtor", "ccsray", "collision-seeking")
            ),
            new Spec(
                "0x004d9dc0",
                "CCollisionSeekingRound__Destructor",
                "CCSRay__DestructorBody_004d9dc0",
                "__fastcall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave494 name/signature/comment hardening: called by CCSRay__ScalarDeletingDestructor_004d9da0 and sits behind adjacent CCSRay-style vtable evidence. Register-only ECX receiver; the body installs vtable pointer 0x005d9608, conditionally calls delete virtuals for helper pointers at this+0x14 and this+0x18, then calls CMonitor__Shutdown(this). Static retail evidence only; exact CCSRay source destructor name, relationship to CCollisionSeekingRound helper layouts, runtime ray/effect behavior, and rebuild parity remain unproven.",
                tags("name-corrected", "destructor", "ccsray", "collision-seeking")
            ),
            new Spec(
                "0x004d9ef0",
                "CEngine__UpdateRoundAndTriggerLaunchEffect",
                "CEngine__UpdateRoundAndTriggerLaunchEffect",
                "__fastcall",
                voidType,
                new ParameterImpl[] {param("round", voidPtr)},
                "Wave494 signature/comment hardening: vtable/data references at 0x005de940 and 0x005e3cb8 point here. Register-only ECX receiver; the body calls CEngine__ArmProjectileAndSpawnTrailEffect(round), resets the CUnit-style timestamp at +0xd0, checks round-config fields this+0xf0+0x5c and +0x6c, and when both are zero builds a CExplosionInitThing-like stack payload with type 2 before dispatching virtual slot +0xc8. Static retail evidence only; exact source owner/name, concrete round/config/effect layouts, runtime launch/effect behavior, and rebuild parity remain unproven.",
                tags("launch-effect", "event-dispatch", "particle-effect")
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
            " created=0 would_create=0" +
            " renamed=" + stats.renamed +
            " would_rename=" + stats.wouldRename +
            " missing=" + stats.missing +
            " bad=" + stats.bad
        );
        if (stats.missing != 0 || stats.bad != 0) {
            throw new IllegalStateException("Wave494 apply had missing/bad rows");
        }
    }
}
