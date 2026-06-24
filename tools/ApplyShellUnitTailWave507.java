//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.BooleanDataType;
import ghidra.program.model.data.CharDataType;
import ghidra.program.model.data.DataType;
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

public class ApplyShellUnitTailWave507 extends GhidraScript {
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
            "shell-unit-tail-wave507",
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
        DataType charPtr = new PointerDataType(CharDataType.dataType);
        DataType boolType = BooleanDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x004df4c0",
                "CShell__ctor_like_004df4c0",
                "CShell__Constructor",
                "__thiscall",
                voidPtr,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave507 signature/name hardening: CShell constructor-like body. OID__CreateObject xref reaches this entry; the body calls CThing__ctor_like_004f3e10, installs the CShell/CActor-adjacent vtables at 0x005ded48 and 0x005decd0, clears the inline 0x100-byte resource/name buffer at this+0x110, and returns this. Static retail evidence only; exact source file, full class layout, runtime projectile-shell behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("cshell", "constructor", "vtable-backed", "projectile-burst-shell")
            ),
            new Spec(
                "0x004df530",
                "CEngine__CopyCStringToObjectLabel110",
                "CShell__CopyResourceNameToInlineBuffer",
                "__thiscall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr), param("resource_name", charPtr)},
                "Wave507 stale-owner correction: direct CShell helper, not CEngine-owned logic. RET 0x4 proves one explicit resource_name argument after ECX; ProjectileBurst__SpawnFromCurrentPreset calls this after OID__CreateObject(0x15), and the body copies a non-empty C string into the constructor-cleared inline buffer at this+0x110. Static retail evidence only; source identity, buffer-size contract, caller preconditions, runtime projectile-shell behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("cshell", "resource-name", "projectile-burst-shell", "stale-owner-corrected", "rename-corrected")
            ),
            new Spec(
                "0x004df550",
                "CShell__VFunc_09_004df550",
                "CShell__Init",
                "__thiscall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr), param("init", voidPtr)},
                "Wave507 signature/name hardening: CShell init vfunc reached from vtable 0x005ded48 slot 9 and direct virtual call after ProjectileBurst__SpawnFromCurrentPreset creates a type-0x15 object. RET 0x4 proves one explicit init argument after ECX; the body builds a CResourceDescriptor from this+0x110, creates a PCRTID render object, clears flag bit 1 at this+0x2c, calls CActor__Init(this, init), randomizes an orientation matrix at this+0xe0, and schedules event 2000 through CEventManager__AddEvent_AtTime. Static retail evidence only; exact source file, event semantics, resource/render-object type, runtime shell behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("cshell", "init", "vtable-slot-9", "projectile-burst-shell", "resource-descriptor", "event-2000")
            ),
            new Spec(
                "0x004dfce0",
                "CUnit__TryActivateAndEnableShadows",
                "CUnit__TryActivateAndEnableShadows",
                "__thiscall",
                boolType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave507 signature/comment hardening: unit-family predicate/update helper. The ECX-only body calls CUnit__MarkDestroyedAndCleanupLinks(this), returns false on failure, otherwise calls CStaticShadows__UpdateVisibility with global static-shadow manager 0x009c8010, this, and enable flag 1 before returning true. Vtable evidence includes table 0x005dfe04 slot 0 and the CUnit-family table 0x005dfd84 slot 32. Static retail evidence only; exact source virtual name, lifecycle semantics, runtime shadow behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("unit", "static-shadows", "predicate", "vtable-backed")
            ),
            new Spec(
                "0x004dfd10",
                "VFuncSlot_18_004dfd10",
                "CUnit__VFunc18_SyncOldVectorAndClampHeight",
                "__thiscall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave507 signature/name hardening: unit-family vfunc-slot-18 override. The ECX-only body calls CActor__VFunc_18_SyncOldVectorAfterBaseCall(this), then clamps current Z at this+0x24 and old/render Z at this+0x94 down to global ceiling 0x006fbdfc when that global is below the current Z. Vtable evidence includes unit-family tables 0x005d8efc and 0x005dfd84 slot 0. Static retail evidence only; exact source virtual name, concrete height/ceiling semantics, runtime movement behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("unit", "vfunc-slot-18", "height-clamp", "old-vector-sync", "rename-corrected")
            )
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
            if (!dryRun) {
                Thread.sleep(5L);
            }
        }

        println(String.format(
            "SUMMARY updated=%d skipped=%d renamed=%d would_rename=%d missing=%d bad=%d",
            stats.updated, stats.skipped, stats.renamed, stats.wouldRename, stats.missing, stats.bad));
    }
}
