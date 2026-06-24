//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
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

public class ApplySubmarineTransitionWave512 extends GhidraScript {
    private static class Spec {
        final String address;
        final String oldName;
        final String newName;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] parameters;
        final String comment;
        final String[] tags;

        Spec(String address, String oldName, String newName, String callingConvention,
                DataType returnType, ParameterImpl[] parameters, String comment, String[] tags) {
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

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "submarine-transition-wave512",
            "retail-binary-evidence",
            "signature-corrected",
            "comment-hardened"
        };
        String[] result = new String[common.length + extras.length];
        System.arraycopy(common, 0, result, 0, common.length);
        System.arraycopy(extras, 0, result, common.length, extras.length);
        return result;
    }

    private String expectedSignature(Spec spec) {
        StringBuilder sb = new StringBuilder();
        sb.append(spec.returnType.getDisplayName()).append(" ")
            .append(spec.callingConvention).append(" ")
            .append(spec.newName).append("(");
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
        fn.replaceParameters(FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS, true, SourceType.USER_DEFINED, spec.parameters);
        fn.setComment(spec.comment);
        for (String tag : spec.tags) {
            fn.addTag(tag);
        }
        println("OK: " + spec.address + " " + spec.newName + " :: " + expectedSignature(spec));
        stats.updated++;
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");
        println("Mode: " + (dryRun ? "dry" : "apply"));

        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);
        DataType intType = IntegerDataType.dataType;
        DataType byteType = ByteDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x004eec80",
                "CSubmarine__Init",
                "CSubmarine__Init",
                "__thiscall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr), param("unit_init", voidPtr)},
                "Wave512 signature/comment hardening: CSubmarine init body. RET 0x4 proves one explicit init argument after ECX; the body clears transition state at this+0x250, prepares init flags/height fields, calls CUnit__Init, allocates a 0x60-byte CSubmarineAI-style component at this+0x13c, and allocates a 0x20-byte CSubmarineGuide at this+0x208. Static retail evidence only; exact source body identity, concrete CSubmarine layout, AI helper source name, runtime submarine behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("submarine", "init", "unit-init", "component-allocation")
            ),
            new Spec(
                "0x004eedc0",
                "CSubmarineAI__VFunc_01_004eedc0",
                "CSubmarineAI__ScalarDeletingDestructor",
                "__thiscall",
                voidPtr,
                new ParameterImpl[] {param("this", voidPtr), param("flags", byteType)},
                "Wave512 stale-vfunc/signature correction: CSubmarineAI scalar-deleting destructor wrapper. RET 0x4 proves one flags argument; the body calls CSubmarineAI__DestructorBody, frees this through CDXMemoryManager__Free when flags&1 is set, and returns this. Static retail evidence only; exact CSubmarineAI layout, source virtual slot name, runtime lifetime behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("submarine", "ai", "scalar-deleting", "destructor", "stale-vfunc-corrected")
            ),
            new Spec(
                "0x004eede0",
                "CUnitAI__ctor_like_004eede0",
                "CSubmarineAI__DestructorBody",
                "__fastcall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave512 stale-ctor/owner correction: derived CSubmarineAI destructor body reached by the CSubmarineAI deleting-destructor wrapper. The ECX-only body restores the CUnitAI base vtable, unregisters tracked SPtrSet links at +0x28, +0x24, and +0x0c when present, then calls CMonitor__Shutdown. Static retail evidence only; exact inherited field layout, source destructor identity, runtime lifetime behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("submarine", "ai", "destructor", "monitor", "sptrset", "stale-owner-corrected")
            ),
            new Spec(
                "0x004ef000",
                "CUnit__SetTransitionState1AndNotifyChildren",
                "CUnit__SetTransitionState1AndNotifyChildren",
                "__fastcall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave512 signature/comment hardening: CUnit transition-state helper. The ECX-only body changes state field this+0x250 from 2 or 3 to 1, then walks the child/list field at this+0x19c and dispatches each child vfunc +0x5c when present. Static retail evidence only; exact state enum names, child-list layout, source identity, runtime transition behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("unit", "transition-state", "child-notify")
            ),
            new Spec(
                "0x004ef050",
                "CUnit__SetTransitionState3_IfState0Or1",
                "CUnit__SetTransitionState3_IfState0Or1",
                "__fastcall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave512 signature/comment hardening: CUnit narrow transition-state setter. The ECX-only body writes state field this+0x250 to 3 only when the prior value is 0 or 1. Static retail evidence only; exact state enum name, source identity, runtime transition behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("unit", "transition-state", "state-setter")
            ),
            new Spec(
                "0x004ef0f0",
                "CUnit__SetTransitionState2",
                "CUnit__SetTransitionState2",
                "__fastcall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave512 signature/comment hardening: CUnit narrow transition-state setter. The ECX-only body writes state field this+0x250 to 2; a nearby state-machine body calls this from the state-3 path after height/position checks. Static retail evidence only; exact state enum name, source identity, runtime transition behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("unit", "transition-state", "state-setter")
            ),
            new Spec(
                "0x004ef120",
                "CMonitor__SpawnParticleEffectFromIndexedListInHeightBand",
                "CMonitor__SpawnParticleEffectFromIndexedListInHeightBand",
                "__fastcall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave512 signature/comment hardening: monitor particle-spawn helper. The ECX-only body reads an indexed effect entry through this+0x164/+0xec and global list DAT_008553f8, samples either this+0x1c position or a linked object's vfunc +0x20 output, and attempts up to 100 samples until it creates a particle effect within the global height band. Static retail evidence only; exact monitor layout, particle-list ownership, source identity, runtime effect behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("monitor", "particle", "height-band", "effect-spawn")
            ),
            new Spec(
                "0x004ef570",
                "CSubmarineGuide__CSubmarineGuide",
                "CSubmarineGuide__CSubmarineGuide",
                "__thiscall",
                voidPtr,
                new ParameterImpl[] {param("this", voidPtr), param("owner_submarine", voidPtr)},
                "Wave512 signature/comment hardening: CSubmarineGuide constructor. RET 0x4 proves one owner argument after ECX; the body calls CGuide__ctor_base with the owner, installs the CSubmarineGuide vtable 0x005df438, and returns this. Static retail evidence only; exact guide layout, pathfinding source identity, runtime guidance behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("submarine", "guide", "constructor", "vtable")
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
    }
}
