//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.BooleanDataType;
import ghidra.program.model.data.ByteDataType;
import ghidra.program.model.data.CharDataType;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.FloatDataType;
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

public class ApplySpawnerThngWave504 extends GhidraScript {
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
            "spawnerthng-wave504",
            "retail-binary-evidence",
            "spawner",
            "spawn-system",
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

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");
        println("Mode: " + (dryRun ? "dry" : "apply"));

        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);
        DataType charPtr = new PointerDataType(CharDataType.dataType);
        DataType floatPtr = new PointerDataType(FloatDataType.dataType);
        DataType intType = IntegerDataType.dataType;
        DataType boolType = BooleanDataType.dataType;
        DataType byteType = ByteDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x004e3010",
                "CSpawnerThng__Init",
                "CSpawnerThng__Init",
                "__thiscall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr), param("init", voidPtr)},
                "Wave504 signature/comment hardening: CSpawnerThng initializer. The retail body aligns with the SpawnerThng.cpp debug path and CSpawnerInitThing source fields by initializing the base complex thing, copying spawn/unit/script strings from the init object, setting spawn amount/delay/accounting fields, and scheduling the first spawn event. Static retail/source evidence only; exact CSpawnerThng and CSpawnerInitThing layout, runtime spawn behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("init", "source-parity", "spawn-config", "spawn-event")
            ),
            new Spec(
                "0x004e3330",
                "CSpawnerThng__Shutdown",
                "CSpawnerThng__Shutdown",
                "__fastcall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave504 signature/comment hardening: CSpawnerThng shutdown helper. The retail body releases active-reader owned references and clears spawner-owned strings/resources before returning through the register-this path. Static retail evidence only; exact resource ownership, runtime shutdown ordering, BEA launch, patching, and rebuild parity remain unproven.",
                tags("shutdown", "active-reader", "resource-cleanup")
            ),
            new Spec(
                "0x004e3370",
                "CSpawnerThng__Update",
                "CSpawnerThng__Update",
                "__fastcall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave504 signature/comment hardening: CSpawnerThng update loop. The retail body resolves named spawners, advances spawn timers and squad counters, drives delayed spawn-wave processing, and gates completion/active-reader state from the spawner object. Static retail evidence only; exact timer units, runtime wave scheduling behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("update-loop", "spawn-timing", "active-reader")
            ),
            new Spec(
                "0x004e36c0",
                "CSpawnerThng__FindSpawnerByName",
                "CSpawnerThng__FindSpawnerByName",
                "__cdecl",
                intType,
                new ParameterImpl[] {param("spawner_name", charPtr)},
                "Wave504 signature/comment hardening: name lookup over the global spawner type/name table. The retail body compares the supplied name against indexed table entries and returns the matching index or -1. Static retail evidence only; exact table ownership, string lifetime, runtime mission data coverage, BEA launch, patching, and rebuild parity remain unproven.",
                tags("name-lookup", "spawn-type-table", "query")
            ),
            new Spec(
                "0x004e37f0",
                "CSpawnerThng__Constructor",
                "CSpawnerThng__Constructor",
                "__thiscall",
                voidPtr,
                new ParameterImpl[] {param("this", voidPtr), param("spawner_init", voidPtr), param("owner_context", voidPtr)},
                "Wave504 signature/comment hardening: CSpawnerThng constructor. The retail callsite constructs an allocated 0x3f8-byte object with ECX as this and two stack arguments, while the body installs base/spawner vtables, constructs the embedded CInitThing-like member, stores the init/context pointers, resolves spawn type data, and initializes counters/reader state. Static retail/source evidence only; exact object layout, owner-context type, runtime allocation behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("constructor", "vtable", "source-parity", "world-physics-create")
            ),
            new Spec(
                "0x004e39f0",
                "CSpawnerThng__ScalarDeletingDestructor",
                "CSpawnerThng__ScalarDeletingDestructor",
                "__thiscall",
                voidPtr,
                new ParameterImpl[] {param("this", voidPtr), param("flags", byteType)},
                "Wave504 signature/comment hardening: MSVC scalar deleting destructor wrapper for CSpawnerThng. The retail body calls the real destructor and conditionally frees the object based on the low bit of the flags byte. Static retail evidence only; allocator identity, runtime destructor side effects, BEA launch, patching, and rebuild parity remain unproven.",
                tags("destructor", "scalar-deleting", "vtable")
            ),
            new Spec(
                "0x004e3a10",
                "CSpawnerThng__Destructor",
                "CSpawnerThng__Destructor",
                "__fastcall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave504 signature/comment hardening: real CSpawnerThng destructor. The retail body unwinds owned active readers/resources, resets vtable state, and destructs the embedded init/base members. Static retail evidence only; exact member ownership, exception-unwind behavior, runtime destruction ordering, BEA launch, patching, and rebuild parity remain unproven.",
                tags("destructor", "active-reader", "resource-cleanup")
            ),
            new Spec(
                "0x004e3aa0",
                "CSpawnerThng__CleanupAndDelete",
                "CSpawnerThng__CleanupAndDelete",
                "__fastcall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave504 signature/comment hardening: cleanup/delete helper for CSpawnerThng. The retail body updates spawn-count accounting before dispatching through the object delete/destructor slot. Static retail evidence only; exact virtual slot identity, runtime deletion path, BEA launch, patching, and rebuild parity remain unproven.",
                tags("cleanup-delete", "spawn-accounting", "vtable")
            ),
            new Spec(
                "0x004e3ac0",
                "CSpawnerThng__UpdateSpawnCount",
                "CSpawnerThng__UpdateSpawnCount",
                "__fastcall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave504 signature/comment hardening: spawn-count accounting helper. The retail body reads the spawner init/config pointer and local counters, then adjusts global/accounting state used by unit spawn-list traversal. Static retail evidence only; exact global counter semantics, runtime spawn-count side effects, BEA launch, patching, and rebuild parity remain unproven.",
                tags("spawn-accounting", "global-counter", "unit-spawn-list")
            ),
            new Spec(
                "0x004e3c60",
                "CSpawnerThng__DoSpawn",
                "CSpawnerThng__DoSpawn",
                "__fastcall",
                boolType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave504 signature/comment hardening: boolean spawn dispatcher. The retail callers pass the spawner in ECX and test EAX; the body checks completion, gathers source position/orientation, creates or links spawned units/squads, marks in-progress state, and calls ProcessSpawnWave. Static retail evidence only; exact spawned object ownership, runtime spawn success semantics, BEA launch, patching, and rebuild parity remain unproven.",
                tags("spawn-dispatch", "squad-spawn", "active-reader", "boolean-return")
            ),
            new Spec(
                "0x004e3f90",
                "CSpawnerThng__ProcessSpawnWave",
                "CSpawnerThng__ProcessSpawnWave",
                "__fastcall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave504 signature/comment hardening: active spawn-wave processor. The retail body checks the in-progress flag, validates spawn position clearance, creates the requested thing/init object, applies transform/type mapping, updates spawned counters, and reschedules event-driven wave work. Static retail evidence only; exact type enum mapping, spawned init layout, runtime scheduling behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("spawn-wave", "position-clearance", "type-mapping", "event-scheduler")
            ),
            new Spec(
                "0x004e4430",
                "CSpawnerThng__IsSpawnComplete",
                "CSpawnerThng__IsSpawnComplete",
                "__fastcall",
                boolType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave504 signature/comment hardening: boolean completion query for a spawner. The retail callers pass each spawner through ECX and test EAX while the body compares spawned counts against configured amount and pending-reader state. Static retail evidence only; exact field layout, runtime completion edge cases, BEA launch, patching, and rebuild parity remain unproven.",
                tags("spawn-completion", "query", "boolean-return")
            ),
            new Spec(
                "0x004e44d0",
                "CSpawnerThng__IsSpawnPositionClear",
                "CSpawnerThng__IsSpawnPositionClear",
                "__thiscall",
                boolType,
                new ParameterImpl[] {param("this", voidPtr), param("spawn_position", floatPtr)},
                "Wave504 signature/comment hardening: boolean spawn-position clearance query. The retail callsite passes this in ECX and a position pointer on the stack; the body iterates spawner type entries, skips excluded type values, queries map occupancy within a fixed radius, and rejects occupied unit-like owners other than the spawner source. Static retail evidence only; exact map-who result layout, radius meaning, runtime collision behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("position-clearance", "mapwho", "boolean-return", "collision-query")
            )
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }

        println("SUMMARY: updated=" + stats.updated
            + " skipped=" + stats.skipped
            + " created=" + stats.created
            + " would_create=" + stats.wouldCreate
            + " renamed=" + stats.renamed
            + " would_rename=" + stats.wouldRename
            + " missing=" + stats.missing
            + " bad=" + stats.bad);

        if (stats.missing > 0 || stats.bad > 0) {
            throw new RuntimeException("Wave504 had missing/bad rows");
        }
    }
}
