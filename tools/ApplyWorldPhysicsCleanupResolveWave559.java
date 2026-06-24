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

public class ApplyWorldPhysicsCleanupResolveWave559 extends GhidraScript {
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
            "worldphysics-cleanup-resolve-wave559",
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
        DataType charPtr = new PointerDataType(CharDataType.dataType);

        Spec[] specs = new Spec[] {
            new Spec(
                "0x00510e60",
                "CWorldPhysicsManager__FreeEntryOwnedPtrs_00_0C_20",
                "CWorldPhysicsManager__FreeEntryOwnedPtrs_00_0C_20",
                "__fastcall",
                voidType,
                new ParameterImpl[] {
                    param("entry", voidPtr())
                },
                "Wave559 signature/comment hardening: CWorldPhysicsManager__ClearAndFreeAllDefinitionLists passes each DAT_00855404 entry in ECX after unlinking it from its list. The body frees and zeroes owned pointer fields at entry+0x00, entry+0x20, and entry+0x0c. Static retail-binary evidence only; exact entry schema, source method identity, runtime reload behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("world-physics-manager", "definition-cleanup", "owned-pointer-free", "signature-recovered")
            ),
            new Spec(
                "0x00510eb0",
                "CWorldPhysicsManager__FreeRoundStatement",
                "CWorldPhysicsManager__FreeRoundStatement",
                "__fastcall",
                voidType,
                new ParameterImpl[] {
                    param("round_statement", voidPtr())
                },
                "Wave559 signature/comment hardening: CWorldPhysicsManager__ClearAndFreeAllDefinitionLists calls this with a DAT_008553f0 round-statement entry in ECX. The body frees and zeroes owned fields at +0x18, +0x08, +0x0c, +0x10, and +0x14. Static retail-binary evidence only; exact round-statement schema, source method identity, runtime round reload behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("world-physics-manager", "round", "definition-cleanup", "signature-recovered")
            ),
            new Spec(
                "0x00510f10",
                "CWorldPhysicsManager__FreeWeaponModeStatement",
                "CWorldPhysicsManager__FreeWeaponModeStatement",
                "__fastcall",
                voidType,
                new ParameterImpl[] {
                    param("weapon_mode_statement", voidPtr())
                },
                "Wave559 signature/comment hardening: CWorldPhysicsManager__ClearAndFreeAllDefinitionLists calls this with a DAT_008553ec weapon-mode entry in ECX. The body drains embedded sets at +0x5c and +0x4c, frees owned fields at +0x30, +0x00, and +0x1c through +0x2c, then clears both embedded CSPtrSet members. Static retail-binary evidence only; exact weapon-mode schema, source method identity, runtime weapon-mode behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("world-physics-manager", "weapon-mode", "definition-cleanup", "embedded-set-clear", "signature-recovered")
            ),
            new Spec(
                "0x00511040",
                "CWorldPhysicsManager__FreeWeaponStatement",
                "CWorldPhysicsManager__FreeWeaponStatement",
                "__fastcall",
                voidType,
                new ParameterImpl[] {
                    param("weapon_statement", voidPtr())
                },
                "Wave559 signature/comment hardening: CWorldPhysicsManager__ClearAndFreeAllDefinitionLists calls this with a DAT_008553e8 weapon-statement entry in ECX. The body frees and zeroes the two owned pointer fields at +0x00 and +0x04. Static retail-binary evidence only; exact weapon-statement schema, source method identity, runtime weapon reload behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("world-physics-manager", "weapon", "definition-cleanup", "signature-recovered")
            ),
            new Spec(
                "0x00511070",
                "CWorldPhysicsManager__FreeTagDefinitionEntry",
                "CWorldPhysicsManager__FreeTagDefinitionEntry",
                "__fastcall",
                voidType,
                new ParameterImpl[] {
                    param("tag_definition", voidPtr())
                },
                "Wave559 signature/comment hardening: CWorldPhysicsManager__ClearAndFreeAllDefinitionLists calls this with a DAT_008553f8 tag-definition entry in ECX. The body frees and zeroes the name field at +0x30 and owned fields at +0x18 through +0x2c. Static retail-binary evidence only; exact tag-definition schema, source method identity, runtime tag resolution behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("world-physics-manager", "tag-definition", "definition-cleanup", "signature-recovered")
            ),
            new Spec(
                "0x005110f0",
                "CWorldPhysicsManager__FreeThingOrComponentDefinitionEntry",
                "CWorldPhysicsManager__FreeThingOrComponentDefinitionEntry",
                "__fastcall",
                voidType,
                new ParameterImpl[] {
                    param("definition_entry", voidPtr())
                },
                "Wave559 signature/comment hardening: CWorldPhysicsManager__ClearAndFreeAllDefinitionLists calls this for both DAT_008553fc thing entries and DAT_00855400 component entries. The body frees many owned fields, drains embedded sets at +0x3c, +0x4c, +0x5c, and +0x6c, then clears those CSPtrSet members. Static retail-binary evidence only; exact thing/component definition schema, source method identity, runtime reload behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("world-physics-manager", "thing-definition", "component-definition", "definition-cleanup", "embedded-set-clear", "signature-recovered")
            ),
            new Spec(
                "0x005113a0",
                "CWorldPhysicsManager__ClearEntryWorkSets_40_50",
                "CWorldPhysicsManager__ClearEntryWorkSets_40_50",
                "__fastcall",
                voidType,
                new ParameterImpl[] {
                    param("definition_entry", voidPtr())
                },
                "Wave559 signature/comment hardening: CWorldPhysicsManager__ClearAndFreeAllDefinitionLists calls this after an entry-specific virtual/free path. The body clears two embedded CSPtrSet work sets at definition_entry+0x50 and definition_entry+0x40. Static retail-binary evidence only; exact work-set semantics, source method identity, runtime reload behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("world-physics-manager", "definition-cleanup", "embedded-set-clear", "signature-recovered")
            ),
            new Spec(
                "0x00511440",
                "CWorldPhysicsManager__IsSpawnerThingTypeAllowedByName",
                "CWorldPhysicsManager__IsSpawnerThingTypeAllowedByName",
                "__cdecl",
                intType,
                new ParameterImpl[] {
                    param("thing_name", charPtr)
                },
                "Wave559 signature/comment hardening: CSpawnerThng__ProcessSpawnWave pushes one thing_name pointer from the spawn-wave entry before calling this gate. The body searches DAT_008553fc by entry+0xb0 name and returns true only for allowed thing type enums 0, 2, 3, 4, 7, 0xb, 0xd, 0x11, 0x13, 0x14, 0x15, and 0x17. Static retail-binary evidence only; exact enum names, source method identity, runtime spawning behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("world-physics-manager", "spawner", "thing-definition", "allowlist-gate", "signature-recovered")
            ),
            new Spec(
                "0x005115b0",
                "CWorldPhysicsManager__MapGunOrSpawnerTagToIndex",
                "CWorldPhysicsManager__MapGunOrSpawnerTagToIndex",
                "__cdecl",
                intType,
                new ParameterImpl[] {
                    param("tag_name", charPtr)
                },
                "Wave559 signature/comment hardening: callers push one tag_name pointer. The body maps GunA..GunI to 1..9 and SpawnerA..SpawnerE to 10..14, returning 0 when the tag is not recognized. It is used by destroyable-segment break handling plus AddWeaponByName and AddSpawnerByName. Static retail-binary evidence only; exact script grammar, source method identity, runtime tag behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("world-physics-manager", "tag-map", "gun-tag", "spawner-tag", "signature-recovered")
            ),
            new Spec(
                "0x00511720",
                "CWorldPhysicsManager__ResolveTagListNameToIndex_E8",
                "CWorldPhysicsManager__ResolveTagListNameToIndex_E8",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr()),
                    param("tag_name", charPtr)
                },
                "Wave559 signature/comment hardening: callsites push one tag_name/name pointer and place the destination object in ECX; the prior extra Ghidra stack parameter was phantom. The body searches DAT_008553f8 by entry+0x30, stores the resolved zero-based index at this+0xe8, and stores -1 on null/miss. Static retail-binary evidence only; exact destination layout, source method identity, runtime tag semantics, BEA launch, patching, and rebuild parity remain unproven.",
                tags("world-physics-manager", "tag-definition", "name-resolve", "phantom-param-removed", "signature-recovered")
            ),
            new Spec(
                "0x005117c0",
                "CWorldPhysicsManager__ResolveTagListNameToIndex_EC",
                "CWorldPhysicsManager__ResolveTagListNameToIndex_EC",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr()),
                    param("tag_name", charPtr)
                },
                "Wave559 signature/comment hardening: callsites push one tag_name/name pointer and place the destination object in ECX; the prior extra Ghidra stack parameter was phantom. The body searches DAT_008553f8 by entry+0x30, stores the resolved zero-based index at this+0xec, and stores -1 on null/miss. Static retail-binary evidence only; exact destination layout, source method identity, runtime tag semantics, BEA launch, patching, and rebuild parity remain unproven.",
                tags("world-physics-manager", "tag-definition", "name-resolve", "phantom-param-removed", "signature-recovered")
            ),
            new Spec(
                "0x00511860",
                "CWorldPhysicsManager__ResolveTagListNameToIndex_F0",
                "CWorldPhysicsManager__ResolveTagListNameToIndex_F0",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr()),
                    param("tag_name", charPtr)
                },
                "Wave559 signature/comment hardening: callsites push one tag_name/name pointer and place the destination object in ECX; the prior extra Ghidra stack parameter was phantom. The body searches DAT_008553f8 by entry+0x30, stores the resolved zero-based index at this+0xf0, and stores -1 on null/miss. Static retail-binary evidence only; exact destination layout, source method identity, runtime tag semantics, BEA launch, patching, and rebuild parity remain unproven.",
                tags("world-physics-manager", "tag-definition", "name-resolve", "phantom-param-removed", "signature-recovered")
            ),
            new Spec(
                "0x00511900",
                "CWorldPhysicsManager__AddComponentByName",
                "CWorldPhysicsManager__AddComponentByName",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr()),
                    param("link_value", intType),
                    param("component_name", charPtr)
                },
                "Wave559 signature/comment hardening: loader/apply callsites pass ECX as the destination owner, then link_value and component_name on the stack. The body allocates an 8-byte item, searches DAT_00855400 by component definition name at entry+0xb0, stores the found index or -1, stores link_value, warns on a miss, and appends the item to this+0x5c. Static retail-binary evidence only; exact owner/list schema, source method identity, runtime component binding behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("world-physics-manager", "component-definition", "add-by-name", "signature-recovered")
            ),
            new Spec(
                "0x005119e0",
                "CWorldPhysicsManager__AddWeaponByName",
                "CWorldPhysicsManager__AddWeaponByName",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr()),
                    param("weapon_name", charPtr),
                    param("tag_name", charPtr),
                    param("link_value", intType)
                },
                "Wave559 signature/comment hardening: CComponentValue02 apply/load callsites pass ECX as the destination owner, then weapon_name, tag_name, and link_value on the stack. The body allocates a 0x0c item, searches DAT_008553e8 by weapon name, stores the found index or -1, stores link_value, maps tag_name through CWorldPhysicsManager__MapGunOrSpawnerTagToIndex, warns on a miss, and appends to this+0x3c. Static retail-binary evidence only; exact owner/list schema, source method identity, runtime weapon binding behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("world-physics-manager", "weapon", "add-by-name", "tag-map", "signature-recovered")
            ),
            new Spec(
                "0x00511ad0",
                "CWorldPhysicsManager__AddSpawnerByName",
                "CWorldPhysicsManager__AddSpawnerByName",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr()),
                    param("spawner_name", charPtr),
                    param("tag_name", charPtr),
                    param("link_value", intType)
                },
                "Wave559 signature/comment hardening: CComponentValue13 apply/load callsites pass ECX as the destination owner, then spawner_name, tag_name, and link_value on the stack. The body allocates a 0x0c item, searches DAT_008553f4 by spawner name at entry+0x08, stores the found index or -1, stores link_value, maps tag_name through CWorldPhysicsManager__MapGunOrSpawnerTagToIndex, warns on a miss, and appends to this+0x4c. Static retail-binary evidence only; exact owner/list schema, source method identity, runtime spawner binding behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("world-physics-manager", "spawner", "add-by-name", "tag-map", "signature-recovered")
            )
        };

        Stats stats = new Stats();
        println("ApplyWorldPhysicsCleanupResolveWave559 mode=" + (dryRun ? "dry" : "apply") + " targets=" + specs.length);
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
            throw new IllegalStateException("Wave559 had bad=" + stats.bad + " missing=" + stats.missing);
        }
    }
}
