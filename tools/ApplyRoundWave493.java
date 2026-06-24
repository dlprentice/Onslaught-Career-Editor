//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.DoubleDataType;
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

public class ApplyRoundWave493 extends GhidraScript {
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
            "round-wave493",
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
        DataType doubleType = DoubleDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x004d81e0",
                "CActor__ctor_like_004d81e0",
                "CRound__ctor",
                "__thiscall",
                voidPtr,
                new ParameterImpl[] {param("this", voidPtr), param("init", voidPtr)},
                "Wave493 name/signature/comment hardening: CWorldPhysicsManager__CreateProjectile allocates 0x134 bytes and calls this constructor for both the base CRound path and the CMissile-derived path. RET 0x4 plus ECX/stack use show __thiscall with this and one init argument. The body chains through CThing__ctor_like_004f3e10, temporarily installs CActor vtables, clears the particle/effect link at this+0xe0 and active-reader slots at this+0xe8/this+0xec, pushes the node onto the global list, installs CRound vtable 0x005de82c and render-position table 0x005de7b4, stores init at this+0xf0, seeds this+0xf4 from DAT_00672fd0, clears this+0x120/0x124/0x12c, and sets this+0x130 to 1. Static retail evidence only; exact source constructor name, concrete CRound/init layouts, runtime projectile creation behavior, BEA launch, and rebuild parity remain unproven.",
                tags("name-corrected", "constructor")
            ),
            new Spec(
                "0x004d82a0",
                "VFuncSlot_15_004d82a0",
                "VFuncSlot_15_004d82a0",
                "__fastcall",
                doubleType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave493 signature/comment hardening: CRound vtable 0x005de82c slot 15 and CMissile-style vtable 0x005e3ba4 slot 15 both point here. Register-only ECX receiver; the body calls virtual slot +0xb4 on this, returns the global 1.0-like scalar at 0x005dc568 when that result is nonzero, otherwise returns the float at round-config pointer this+0xf0 plus offset 0x2c. Static retail evidence only; exact source virtual name, scalar meaning, concrete CRound/CMissile layouts, runtime projectile behavior, and rebuild parity remain unproven.",
                tags("shared-vfunc", "config-scalar")
            ),
            new Spec(
                "0x004d8350",
                "CRound__VFunc_01_004d8350",
                "CRound__scalar_deleting_dtor",
                "__thiscall",
                voidPtr,
                new ParameterImpl[] {param("this", voidPtr), param("flags", intType)},
                "Wave493 name/signature/comment hardening: CRound vtable 0x005de82c slot 1 points here. RET 0x8 plus ECX/stack use show the scalar-deleting destructor pattern; the body calls CRound__ShutdownAndDetachReaders(this), conditionally frees this through CDXMemoryManager__Free when flags bit 0 is set, and returns this. Static retail evidence only; allocator ownership, exact source destructor spelling, destructor side-effect completeness, runtime projectile teardown behavior, and rebuild parity remain unproven.",
                tags("name-corrected", "destructor", "scalar-deleting-dtor")
            ),
            new Spec(
                "0x004d8370",
                "CRound__ShutdownAndDetachReaders",
                "CRound__ShutdownAndDetachReaders",
                "__fastcall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave493 signature/comment hardening: called by CRound__scalar_deleting_dtor before optional free. Register-only ECX receiver; the body removes linked active-reader cells at this+0xec and this+0xe8 through CSPtrSet__Remove when present, removes the particle/effect link rooted at this+0xe0 from the global list, then delegates to CActor__dtor_base. Static retail evidence only; concrete reader/link layout, exact source destructor helper name, runtime teardown behavior, and rebuild parity remain unproven.",
                tags("destructor", "active-reader", "particle-effect")
            ),
            new Spec(
                "0x004d8410",
                "CRound__Init",
                "CRound__Init",
                "__thiscall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr), param("init", voidPtr)},
                "Wave493 signature/comment hardening: CRound vtable 0x005de82c slot 9 points here, and CMissile__Init delegates here. RET 0x4 plus ECX/stack use show __thiscall with this and one init argument. The body copies CRoundInitThing-like destination/jump/lifespan fields from init+0x3bc..0x3d8 into this+0x108..0x118/this+0xf0/this+0x11c, mutates collision/render flags on the init object from round-data fields, optionally allocates collision-seeking or CLine helpers from Round.cpp debug-path sites, calls CActor__Init, schedules event 4000, may create a launch particle effect, performs optional heightfield impact timing, registers globally when round-data+0x58 is set, and finally calls CRound__SelectBestTargetReaderAndSyncAimState. Static retail evidence only; exact source method body, concrete CRound/CRoundInitThing/CRoundData layouts, runtime collision/effect behavior, BEA launch, and rebuild parity remain unproven.",
                tags("init", "collision-setup", "event-scheduling", "particle-effect")
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
            throw new IllegalStateException("Wave493 apply had missing/bad rows");
        }
    }
}
