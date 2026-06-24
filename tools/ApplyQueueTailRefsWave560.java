//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.CharDataType;
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

public class ApplyQueueTailRefsWave560 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String previousName;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] params;
        final String comment;
        final String[] tags;

        Spec(String address, String name, String previousName, String callingConvention,
                DataType returnType, ParameterImpl[] params, String comment, String[] tags) {
            this.address = address;
            this.name = name;
            this.previousName = previousName;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.params = params;
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

    private DataType voidPtr() {
        return new PointerDataType(VoidDataType.dataType);
    }

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "queue-tail-refs-wave560",
            "retail-binary-evidence",
            "signature-corrected",
            "comment-hardened"
        };
        String[] result = new String[common.length + extras.length];
        System.arraycopy(common, 0, result, 0, common.length);
        System.arraycopy(extras, 0, result, common.length, extras.length);
        return result;
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
        if (fn.getParameterCount() != spec.params.length) {
            return false;
        }
        for (int i = 0; i < spec.params.length; i++) {
            Parameter actual = fn.getParameter(i);
            ParameterImpl expected = spec.params[i];
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
        if (!fn.getName().equals(spec.name)) {
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

    private String expectedSignature(Spec spec) {
        StringBuilder sb = new StringBuilder();
        sb.append(spec.returnType.getDisplayName()).append(" ")
            .append(spec.callingConvention).append(" ")
            .append(spec.name).append("(");
        if (spec.params.length == 0) {
            sb.append("void");
        }
        for (int i = 0; i < spec.params.length; i++) {
            if (i > 0) {
                sb.append(", ");
            }
            sb.append(spec.params[i].getDataType().getDisplayName())
                .append(" ")
                .append(spec.params[i].getName());
        }
        sb.append(")");
        return sb.toString();
    }

    private void verifyReadBack(Spec spec) throws Exception {
        Function fn = functionAtEntry(spec.address);
        if (fn == null) {
            throw new IllegalStateException("Readback missing function at " + spec.address);
        }
        if (!fn.getName().equals(spec.name)) {
            throw new IllegalStateException("Readback name mismatch at " + spec.address + ": " + fn.getName());
        }
        if (!signatureMatches(fn, spec)) {
            throw new IllegalStateException("Readback signature mismatch at " + spec.address +
                ": expected " + expectedSignature(spec) + " got " + fn.getSignature());
        }
        String existingComment = fn.getComment();
        if (existingComment == null || !existingComment.equals(spec.comment)) {
            throw new IllegalStateException("Readback comment mismatch at " + spec.address);
        }
        if (!hasAllTags(fn, spec.tags)) {
            throw new IllegalStateException("Readback missing tags at " + spec.address);
        }
    }

    private void applySpec(Spec spec, boolean dryRun, Stats stats) {
        try {
            Function fn = functionAtEntry(spec.address);
            if (fn == null) {
                stats.missing++;
                println("FAIL: " + spec.address + " " + spec.name + " Function not found");
                return;
            }
            if (!fn.getName().equals(spec.name) && !fn.getName().equals(spec.previousName)) {
                throw new IllegalStateException("Unexpected function name at " + spec.address + ": " + fn.getName());
            }
            boolean renameNeeded = !fn.getName().equals(spec.name);
            boolean updateNeeded = needsUpdate(fn, spec);
            if (dryRun) {
                if (renameNeeded) {
                    stats.wouldRename++;
                }
                if (updateNeeded) {
                    println("DRY: " + spec.address + " " + fn.getName() + " -> " + expectedSignature(spec));
                } else {
                    println("SKIP: " + spec.address + " already matches " + spec.name);
                }
                stats.skipped++;
                return;
            }
            if (!updateNeeded) {
                stats.skipped++;
                println("SKIP: " + spec.address + " already matches " + spec.name);
                verifyReadBack(spec);
                return;
            }
            if (renameNeeded) {
                fn.setName(spec.name, SourceType.USER_DEFINED);
                stats.renamed++;
            }
            fn.setCallingConvention(spec.callingConvention);
            fn.setReturnType(spec.returnType, SourceType.USER_DEFINED);
            fn.replaceParameters(
                FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS,
                true,
                SourceType.USER_DEFINED,
                spec.params);
            fn.setComment(spec.comment);
            for (String tag : spec.tags) {
                fn.addTag(tag);
            }
            verifyReadBack(spec);
            stats.updated++;
            println("APPLY: " + spec.address + " -> " + expectedSignature(spec));
        } catch (Exception ex) {
            stats.bad++;
            println("FAIL: " + spec.address + " " + spec.name + " " + ex.getClass().getSimpleName() + ": " + ex.getMessage());
        }
    }

    @Override
    protected void run() throws Exception {
        boolean dryRun = isDryRun(getScriptArgs().length > 0 ? getScriptArgs()[0] : "dry");
        DataType voidType = VoidDataType.dataType;
        DataType intType = IntegerDataType.dataType;
        DataType intPtr = new PointerDataType(IntegerDataType.dataType);
        DataType charPtr = new PointerDataType(CharDataType.dataType);

        Spec[] specs = new Spec[] {
            new Spec(
                "0x005113f0",
                "CWeaponRound__SetReaderFromGlobalListByIndex",
                "CWeaponRound__SetReaderFromGlobalListByIndex",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr()),
                    param("round_index", intType)
                },
                "Wave560 signature/comment hardening: CWeaponRound__ApplyToWeaponModeByName passes the selected DAT_008553f0 round-statement list index or -1. The body walks DAT_008553f0 by round_index and stores the selected entry pointer, or null on a miss, at this+0x18. Static retail-binary evidence only; exact weapon-mode/round record schema, runtime weapon-round behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("weapon-round", "world-physics-manager", "phantom-param-removed", "signature-recovered")
            ),
            new Spec(
                "0x00511510",
                "CUnit__GetTypePriorityWeight",
                "CUnit__GetTypePriorityWeight",
                "__cdecl",
                intType,
                new ParameterImpl[] {
                    param("unit_or_definition", voidPtr())
                },
                "Wave560 signature/comment hardening: CSpawnerThng__UpdateSpawnCount, CUnit__MarkDestroyedAndCleanupLinks, and CUnit__UpdateSpawnCountAccounting pass a unit/profile definition pointer here. The body switches on unit_or_definition+0xe0 and returns priority weights 1, 5, 10, 20, 100, or 0 for spawn/destroy accounting. Static retail-binary evidence only; exact enum names, counter semantics, runtime spawning/destruction behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("unit", "spawn-accounting", "priority-weight", "signature-recovered")
            ),
            new Spec(
                "0x00511bc0",
                "CVBufTexture__FindListEntryByPair",
                "CVBufTexture__FindListEntryByPair",
                "__thiscall",
                intPtr,
                new ParameterImpl[] {
                    param("this", voidPtr()),
                    param("emitter_slot_tag", intType),
                    param("cache_key", intType)
                },
                "Wave560 signature/comment hardening: CUnit__UpdateTransform calls this on the profile/cache object at unit+0x164. The body scans the linked cache list rooted at this+0x6c, updates the iterator at this+0x74, and returns the first entry whose first two dwords match emitter_slot_tag and cache_key. Static retail-binary evidence only; exact cache-entry owner/layout, slot enum names, runtime transform caching behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("unit-transform", "cache-lookup", "phantom-param-removed", "signature-recovered")
            ),
            new Spec(
                "0x00511c10",
                "CFeatureTexture__SetTagListIndexOrMinusOne",
                "CVBufTexture__SetNameListIndexOrMinusOne",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr()),
                    param("tag_name", charPtr)
                },
                "Wave560 rename/signature/comment hardening: CFeatureTexture__ApplyToFeatureByName calls this on the matched DAT_00855404 feature record and passes this+0x8 from the caller as tag_name. The body searches DAT_008553f8 by tag-definition entry+0x30, writes the zero-based index to this+0x8, and writes -1 on null/miss. Static retail-binary evidence only; exact feature/tag schema, runtime feature texture behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("feature-texture", "tag-definition", "name-resolve", "phantom-param-removed", "renamed", "signature-recovered")
            ),
            new Spec(
                "0x00511ca0",
                "CWorldPhysicsManager__ResolveWeaponModeStatementRefs",
                "CWorldPhysicsManager__ResolveLoadedDefRefLinks_TypeA",
                "__fastcall",
                voidType,
                new ParameterImpl[] {
                    param("weapon_mode_statement", voidPtr())
                },
                "Wave560 rename/signature/comment hardening: CWorldPhysicsManager__ResolveLoadedDefinitionReferences calls this while iterating DAT_008553ec weapon-mode statements. The body resolves node-name fields at +0x1c and +0x20 into pointers at +0x04 and +0x08, then resolves sound-effect name fields at +0x24, +0x28, and +0x2c through CSoundManager__GetEffectByName into +0x0c, +0x10, and +0x14. Static retail-binary evidence only; exact weapon-mode schema, runtime resolve behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("world-physics-manager", "weapon-mode", "definition-resolve", "sound-ref", "renamed", "signature-recovered")
            ),
            new Spec(
                "0x00511d20",
                "CWorldPhysicsManager__ResolveTagDefinitionRefs",
                "CWorldPhysicsManager__ResolveLoadedDefRefLinks_TypeB",
                "__fastcall",
                voidType,
                new ParameterImpl[] {
                    param("tag_definition", voidPtr())
                },
                "Wave560 rename/signature/comment hardening: CWorldPhysicsManager__ResolveLoadedDefinitionReferences calls this while iterating DAT_008553f8 tag-definition entries. The body resolves node-name fields at +0x18, +0x1c, +0x20, and +0x24 into pointer fields at +0x00, +0x04, +0x08, and +0x0c, then resolves sound-effect names at +0x28 and +0x2c into +0x10 and +0x14 through CSoundManager__GetEffectByName. Static retail-binary evidence only; exact tag-definition schema, runtime resolve behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("world-physics-manager", "tag-definition", "definition-resolve", "sound-ref", "renamed", "signature-recovered")
            ),
            new Spec(
                "0x00511db0",
                "CWorldPhysicsManager__ResolveThingOrComponentDefinitionRefs",
                "CWorldPhysicsManager__FindSoundEventByNameIfEnabled",
                "__fastcall",
                voidType,
                new ParameterImpl[] {
                    param("definition_entry", voidPtr())
                },
                "Wave560 rename/signature/comment hardening: CWorldPhysicsManager__ResolveLoadedDefinitionReferences calls this for both DAT_008553fc thing definitions and DAT_00855400 component definitions. The body resolves multiple node-name fields from +0x7c through +0xa4 into pointer fields at +0x00 through +0x28, and resolves sound-effect names at +0xa8 and +0xac into +0x34 and +0x38 through CSoundManager__GetEffectByName. Static retail-binary evidence only; exact thing/component schema, runtime resolve behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("world-physics-manager", "thing-definition", "component-definition", "definition-resolve", "sound-ref", "renamed", "signature-recovered")
            )
        };

        Stats stats = new Stats();
        println("ApplyQueueTailRefsWave560 mode=" + (dryRun ? "dry" : "apply") + " targets=" + specs.length);
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }
        println("SUMMARY: mode=" + (dryRun ? "dry" : "apply") +
            " updated=" + stats.updated +
            " skipped=" + stats.skipped +
            " renamed=" + stats.renamed +
            " would_rename=" + stats.wouldRename +
            " missing=" + stats.missing +
            " bad=" + stats.bad);
        if (stats.bad != 0 || stats.missing != 0) {
            throw new IllegalStateException("Wave560 had bad=" + stats.bad + " missing=" + stats.missing);
        }
    }
}
