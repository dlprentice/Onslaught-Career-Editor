//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.CharDataType;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.DoubleDataType;
import ghidra.program.model.data.FloatDataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.UnsignedIntegerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.FunctionTag;
import ghidra.program.model.listing.Parameter;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyCWorldTailWave556 extends GhidraScript {
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

    private DataType charPtr() {
        return new PointerDataType(CharDataType.dataType);
    }

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "cworld-tail-wave556",
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
            println("FAIL: " + spec.address + " " + spec.name + " " + ex.getMessage());
        }
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");
        println("Mode: " + (dryRun ? "dry" : "apply"));

        DataType voidType = VoidDataType.dataType;
        DataType intType = IntegerDataType.dataType;
        DataType uintType = UnsignedIntegerDataType.dataType;
        DataType floatType = FloatDataType.dataType;
        DataType doubleType = DoubleDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x0050d680",
                "CWorld__ReleaseSubObject_AndMaybeFree",
                "CWorld__ReleaseSubObject_AndMaybeFree",
                "__thiscall",
                voidPtr(),
                new ParameterImpl[] {
                    param("this", voidPtr()),
                    param("flags", uintType)
                },
                "Wave556 signature/comment hardening: CWorld__ShutdownAndClear calls this helper for the three world-owned LOD/occupancy subobjects at world +0x200, +0x204, and +0x208, always pushing flags=1. The body clears the dynamic occupancy set, optionally frees this when bit 0 is set, and returns the original pointer; the older second explicit parameter was register carryover. Static retail-binary evidence only; exact subobject type, ownership model, runtime visibility behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("cworld", "lod", "occupancy", "phantom-param-removed")
            ),
            new Spec(
                "0x0050d6a0",
                "CWorld__PushWorldTextSlot",
                "CWorld__PushWorldTextSlot",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr()),
                    param("text_id", intType),
                    param("slot_state", intType)
                },
                "Wave556 signature/comment hardening: the script wrapper loads ECX with DAT_00855090 and pushes text_id plus slot_state before this call. The body scans the four CWorld text slots at this +0x20c, fetches the localized string through CText__GetStringById, stores text_id/string/state, and clears the per-slot timing fields. Static retail-binary evidence only; exact slot structure, script opcode identity, text lifetime, HUD runtime behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("cworld", "world-text", "script-wrapper", "phantom-param-removed")
            ),
            new Spec(
                "0x0050d720",
                "CWorld__UpdateWorldTextSlotTiming",
                "CWorld__UpdateWorldTextSlotTiming",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr()),
                    param("text_id", intType),
                    param("primary_time", floatType),
                    param("secondary_time", floatType)
                },
                "Wave556 signature/comment hardening: the script wrapper passes one text id and two float timing values after loading ECX with DAT_00855090. The body finds matching text slots by stored text_id at this +0x21c, writes primary/secondary timing fields at this +0x23c/+0x24c, and treats slot state 3 as an absolute expiry against DAT_00672fd0. Static retail-binary evidence only; exact time-unit semantics, slot-state enum, script opcode identity, HUD runtime behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("cworld", "world-text", "timing", "script-wrapper", "phantom-param-removed")
            ),
            new Spec(
                "0x0050d760",
                "CWorld__GetWorldTextSlotTimerValue",
                "CExplosionInitThing__GetSlotTimerValueByMode",
                "__thiscall",
                doubleType,
                new ParameterImpl[] {
                    param("this", voidPtr()),
                    param("slot_index", intType)
                },
                "Wave556 owner/signature/comment hardening: CHud__RenderControllerSlotStatusPanel and IScript__GetTextWidth call this with CWorld text-slot state, not ExplosionInitThing data. The body reads slot state at this +0x20c + slot_index*4, returns the timer at this +0x23c + slot_index*4, and clamps state-3 absolute expiry against DAT_00672fd0 to zero. Static retail-binary evidence only; exact owner type, slot-state enum, HUD formatting behavior, text timing units, BEA launch, patching, and rebuild parity remain unproven.",
                tags("cworld", "world-text", "hud", "owner-corrected", "phantom-param-removed")
            ),
            new Spec(
                "0x0050d7a0",
                "CWorld__ClearWorldTextSlot",
                "CWorld__ClearWorldTextSlot",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr()),
                    param("text_id", intType)
                },
                "Wave556 signature/comment hardening: the script wrapper loads ECX with DAT_00855090 and passes one text_id argument. The body scans four CWorld text slots, compares stored ids at this +0x21c, and clears the slot state at this +0x20c for matches; the older second explicit parameter was register carryover. Static retail-binary evidence only; exact script opcode identity, slot layout, HUD runtime behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("cworld", "world-text", "script-wrapper", "phantom-param-removed")
            ),
            new Spec(
                "0x0050d7d0",
                "CWorld__IsMultiplayerMode",
                "CWorld__IsMultiplayerMode",
                "__fastcall",
                intType,
                new ParameterImpl[] {
                    param("world", voidPtr())
                },
                "Wave556 signature/comment hardening: CGame__LoadLevel loads ECX with DAT_00855090 before calling this helper. The body returns nonzero when the world mode field at world +0x27c is 1 or 2, otherwise zero. Static retail-binary evidence only; exact enum names, multiplayer feature behavior, runtime load behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("cworld", "mode", "multiplayer")
            ),
            new Spec(
                "0x0050d7f0",
                "CWorld__ClearLinkedObjectPairSet",
                "CWorld__ClearLinkedObjectPairSet",
                "__fastcall",
                voidType,
                new ParameterImpl[] {
                    param("pair_set", voidPtr())
                },
                "Wave556 signature/comment hardening: CWorld__ShutdownAndClear passes the embedded pair set at world +0x120. The body walks each node, dispatches deleting destructors for both pointer fields when present, frees the pair node, and then clears the backing CSPtrSet. Static retail-binary evidence only; exact pair contents, script-event ownership, destructor side effects, runtime shutdown behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("cworld", "pair-set", "script-events", "cleanup")
            ),
            new Spec(
                "0x0050d9a0",
                "CWorldMeshList__Clear",
                "CWorldMeshList__Clear",
                "__cdecl",
                voidType,
                new ParameterImpl[] {},
                "Wave556 signature/comment hardening: CWorld__ShutdownAndClear calls this global WorldMeshList cleanup path. The body drains DAT_00855358, removes each node from its CSPtrSet, frees the owned mesh-name string, and frees the 8-byte list node. Static retail-binary evidence only; exact list container type, ownership lifetime, runtime resource behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("world-mesh-list", "cleanup")
            ),
            new Spec(
                "0x0050d9e0",
                "CWorldMeshList__Add",
                "CWorldMeshList__Add",
                "__cdecl",
                voidType,
                new ParameterImpl[] {
                    param("mesh_name", charPtr())
                },
                "Wave556 signature/comment hardening: CWorld__LoadWorld, CSpawnerThng__Init, CScriptObjectCode__CollectSpawnThings, and recursive self-calls pass one mesh-name pointer. The body skips resource-running mode, deduplicates DAT_00855358, matches mesh_name against thing definitions at DAT_008553fc +0xb0, allocates an 8-byte node plus copied string, and recursively adds child mesh names through DAT_008553f4. Static retail-binary evidence only; exact definition layouts, child-link semantics, runtime spawn behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("world-mesh-list", "load-world", "recursive", "signature-recovered")
            ),
            new Spec(
                "0x0050dc20",
                "CWorldMeshList__MarkUsed",
                "CWorldMeshList__MarkUsed",
                "__cdecl",
                voidType,
                new ParameterImpl[] {
                    param("mesh_name", charPtr())
                },
                "Wave556 signature/comment hardening: CUnit__Init passes one mesh-name pointer to mark an already-instantiated mesh entry. The body scans DAT_00855358 by strcmp and sets the node used flag at +0x04 when mesh_name matches. Static retail-binary evidence only; exact node type, runtime instantiation ordering, mesh ownership, BEA launch, patching, and rebuild parity remain unproven.",
                tags("world-mesh-list", "used-flag", "signature-recovered")
            ),
            new Spec(
                "0x0050dcb0",
                "CWorld__SpawnInitialThings",
                "CWorld__SpawnInitialThings",
                "__cdecl",
                voidType,
                new ParameterImpl[] {},
                "Wave556 signature/comment hardening: CWorld__LoadWorld calls this no-argument global pass after WorldMeshList population. The body walks unused DAT_00855358 mesh entries, resolves their thing-definition index in DAT_008553fc, creates a runtime thing through CWorldPhysicsManager__CreateThingByType, builds init thing type 8 with default 256/256/0 position fields, calls the target init vfunc, then releases the init object. Static retail-binary evidence only; exact init object type, spawn ordering, runtime world behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("cworld", "world-mesh-list", "spawn", "load-world", "signature-recovered")
            ),
            new Spec(
                "0x0050df80",
                "CWorldPhysicsManager__CreateThingByType",
                "CWorldPhysicsManager__CreateThingByType",
                "__cdecl",
                voidPtr(),
                new ParameterImpl[] {
                    param("thing_type_index", intType)
                },
                "Wave556 signature/comment hardening: CWorld__LoadWorld, CWorld__SpawnInitialThings, CSpawnerThng, CSquad, and script/create callsites pass one thing_type_index argument. The body walks DAT_008553fc to the requested definition index, switches on the definition type enum at +0xe0, allocates the matching runtime object, installs class vtables, and returns the created object or null on heap/type failure. Static retail-binary evidence only; exact type enum names, object layouts, constructor side effects, runtime spawn behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("world-physics-manager", "factory", "spawn", "signature-recovered")
            )
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }

        println("SUMMARY: mode=" + (dryRun ? "dry" : "apply")
            + " updated=" + stats.updated
            + " skipped=" + stats.skipped
            + " renamed=" + stats.renamed
            + " would_rename=" + stats.wouldRename
            + " missing=" + stats.missing
            + " bad=" + stats.bad);

        if (stats.missing != 0 || stats.bad != 0) {
            throw new IllegalStateException("Wave556 apply had missing/bad rows");
        }
    }
}
