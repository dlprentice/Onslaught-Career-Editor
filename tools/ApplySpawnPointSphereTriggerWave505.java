//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.BooleanDataType;
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

public class ApplySpawnPointSphereTriggerWave505 extends GhidraScript {
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
            "spawnpoint-spheretrigger-wave505",
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
        DataType boolType = BooleanDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x004e46c0",
                "CSpawnPoint__VFunc_09_004e46c0",
                "CSpawnPoint__Init",
                "__thiscall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr), param("init", voidPtr)},
                "Wave505 name/signature/comment hardening: CSpawnPoint init helper. RET 0x4 proves one explicit init argument after ECX; the body clamps the init position against static shadow height, calls CComplexThing__Init, links this into the global spawn-point set DAT_00855110, copies player/position/orientation/config fields, handles the multiplayer player-number swap, and stores respawn mode/effect fields. Static retail/source-respawn evidence only; exact CSpawnPoint/CStart/init layouts, runtime respawn behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("spawnpoint", "init", "respawn", "static-shadow", "global-list", "rename-corrected")
            ),
            new Spec(
                "0x004e47c0",
                "CSpawnPoint__VFunc_02_004e47c0",
                "CSpawnPoint__VFuncSlot02_RemoveFromSpawnPointList",
                "__fastcall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave505 name/signature/comment hardening: CSpawnPoint vtable slot 2 cleanup wrapper. The register-only body removes this from the global spawn-point set DAT_00855110 and then delegates to shared VFuncSlot_02_004f41b0. Static retail evidence only; exact source virtual name, shutdown/destructor ordering, runtime respawn behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("spawnpoint", "cleanup", "global-list", "vtable", "rename-corrected")
            ),
            new Spec(
                "0x004e47e0",
                "CGame__CreateRespawnBattleEngineAndEffect",
                "CSpawnPoint__SpawnBattleEngine",
                "__thiscall",
                voidPtr,
                new ParameterImpl[] {param("this", voidPtr), param("play_effect", intType)},
                "Wave505 stale-owner correction: this is the CSpawnPoint/CStart-style SpawnBattleEngine helper reached from CGame__RespawnPlayer, not a CGame method. RET 0x4 proves one explicit play_effect argument after ECX; the body creates OID type 3, initializes it from this+0x80, seeds respawn state fields, optionally spawns BE_Respawn_Ground_Effect or BE_Respawn_Air_Effect, and moves the effect to the spawn-point position. Static retail/source-respawn evidence only; exact BattleEngine/init/effect layouts, runtime respawn behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("spawnpoint", "respawn", "battleengine", "particle-effect", "stale-owner-corrected", "rename-corrected")
            ),
            new Spec(
                "0x004e49f0",
                "CGame__IsSpawnAreaClearWithinRadius",
                "CSpawnPoint__Available",
                "__fastcall",
                boolType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave505 stale-owner correction: CSpawnPoint availability predicate reached from CGame__RespawnPlayer spawn-point selection. The register-only body checks the enabled flag at this+0x448, queries CMapWho entries around this+0x1c with radius 1.0, filters active non-excluded owners, and rejects occupants within the squared clearance threshold at 0x005d8bc0. Static retail/source-respawn evidence only; exact map-who flags, radius semantics, runtime spawn clearance behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("spawnpoint", "respawn", "availability", "mapwho", "stale-owner-corrected", "rename-corrected")
            ),
            new Spec(
                "0x004e5540",
                "CSphereTrigger__OnTriggered",
                "CSphereTrigger__OnTriggered",
                "__fastcall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave505 signature/comment hardening: CSphereTrigger triggered-effect helper. The body calls this vtable slot +0x68 as a trigger gate, clears/reuses the particle-effect link at this+0x7c, resolves Sphere_Trigger_Effect, creates the effect, and moves the linked effect object to the trigger position while preserving previous/current transform buffers. Static retail evidence only; exact trigger/effect layout, runtime trigger behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("sphere-trigger", "trigger-effect", "particle-effect", "signature-corrected")
            ),
            new Spec(
                "0x004e5700",
                "CSphereTrigger__Update",
                "CSphereTrigger__Hit",
                "__thiscall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr), param("other_thing", voidPtr), param("collision_report", voidPtr)},
                "Wave505 stale-name correction: CSphereTrigger hit/contact override, not a frame update loop. The body calls CComplexThing__Hit(this, other_thing, collision_report), requires the other thing active flag, clears the per-frame contained-object set when the global timestamp changes, allocates a monitored reader cell for other_thing, ensures the target monitor set exists, and appends the reader to this+0x8c. Static retail evidence only; exact trigger/list/monitor layout, runtime trigger behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("sphere-trigger", "hit", "active-reader", "monitor", "stale-name-corrected", "rename-corrected")
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
            "SUMMARY updated=%d skipped=%d created=%d would_create=%d renamed=%d would_rename=%d missing=%d bad=%d",
            stats.updated, stats.skipped, stats.created, stats.wouldCreate, stats.renamed, stats.wouldRename,
            stats.missing, stats.bad));
    }
}
