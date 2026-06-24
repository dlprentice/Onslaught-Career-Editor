//@category Symbol

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

public class ApplyStartRespawnWave510 extends GhidraScript {
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
            "start-respawn-wave510",
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
        DataType boolType = BooleanDataType.dataType;
        DataType intType = IntegerDataType.dataType;
        DataType byteType = ByteDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x004ea8d0",
                "CRelaxedSquad__Create",
                "CRelaxedSquad__CreateIterator",
                "__fastcall",
                voidPtr,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave510 stale-purpose/signature correction: CRelaxedSquad member iterator/set snapshot creator. The ECX-only body allocates a 0x10-byte CSPtrSet, initializes it, walks this+0xa4 member nodes, adds non-null members with CSPtrSet__AddToHead, and returns the new set pointer; this mirrors the CSquadNormal iterator pattern rather than constructing a CRelaxedSquad. Static retail evidence only; exact source body, iterator ownership/lifetime, member-node layout, runtime AI behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("relaxed-squad", "member-set", "iterator", "stale-purpose-corrected")
            ),
            new Spec(
                "0x004eacc0",
                "CStart__ctor_like_004eacc0",
                "CStart__Constructor",
                "__thiscall",
                voidPtr,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave510 signature/comment hardening: CStart constructor-like body reached by OID__CreateObject. The ECX-only body calls the CThing constructor, initializes the active-reader cell at this+0x7c, constructs embedded CStartInitThing storage at this+0x84, clears respawn/player fields at +0x440/+0x444/+0x448, installs CStart vtables 0x005df2ec and 0x005df274, and clears the active reader. Static retail evidence only; exact CStart/CStartInitThing layout, source identity, runtime respawn behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("start", "constructor", "respawn", "init-thing")
            ),
            new Spec(
                "0x004ead70",
                "CStart__VFunc_01_004ead70",
                "CStart__ScalarDeletingDestructor",
                "__thiscall",
                voidPtr,
                new ParameterImpl[] {param("this", voidPtr), param("flags", byteType)},
                "Wave510 stale-vfunc/signature correction: CStart scalar-deleting destructor wrapper. RET 0x4 proves one flags argument; the body calls CStart__Destructor, conditionally frees this through CDXMemoryManager__Free when flags&1 is set, and returns this. Static retail evidence only; allocator ownership, exact destructor side effects, runtime behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("start", "destructor", "scalar-deleting", "vfunc-slot-1")
            ),
            new Spec(
                "0x004ead90",
                "CStart__ctor_like_004ead90",
                "CStart__Destructor",
                "__fastcall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave510 stale-name/signature correction: CStart destructor body. The ECX-only body restores CStart vtables, removes this from the global start set DAT_00855100, unregisters the active-reader cell from its current target deletion set when linked, then delegates to CComplexThing__dtor_base. Static retail evidence only; exact CStart/global-list/reader layout, runtime behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("start", "destructor", "global-list", "active-reader")
            ),
            new Spec(
                "0x004eae10",
                "CStart__VFunc_09_004eae10",
                "CStart__Init",
                "__thiscall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr), param("init", voidPtr)},
                "Wave510 stale-vfunc/signature correction: CStart init vfunc at vtable 0x005df2ec slot 9. RET 0x4 proves one init argument; the body clamps init height through CStaticShadows__SampleShadowHeightBilinear, calls CComplexThing__Init, links this into DAT_00855100, copies player number/position/orientation/config/plane-mode fields from CStartInitThing, chooses player-object globals DAT_008a9bb8/DAT_008a9bbc, and seeds an initial BattleEngine via CStart__SpawnBattleEngine(play_effect=0). Static retail evidence only; exact CStart/CStartInitThing layout, runtime spawn behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("start", "init", "vfunc-slot-9", "respawn", "static-shadows")
            ),
            new Spec(
                "0x004eaf20",
                "CGame__SetupRespawnReaderAndEffect",
                "CStart__SpawnBattleEngine",
                "__thiscall",
                voidPtr,
                new ParameterImpl[] {param("this", voidPtr), param("play_effect", intType)},
                "Wave510 stale-owner/signature correction: CStart BattleEngine spawn helper used by CStart init and CGame::RespawnPlayer fallback. RET 0x4 proves one play_effect argument; the body creates OID type 3, binds it through the active-reader cell at this+0x7c, initializes the embedded CStartInitThing copy at this+0x84 through the new engine vfunc, seeds respawn/default fields, and optionally creates/moves BE_Respawn_Ground_Effect or BE_Respawn_Air_Effect to this position. Static retail evidence only; exact BattleEngine/init/effect layout, runtime respawn behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("start", "respawn", "spawn-battleengine", "stale-owner-corrected")
            ),
            new Spec(
                "0x004eb130",
                "CGame__HasNearbyHostileWithinRadius",
                "CStart__Available",
                "__fastcall",
                boolType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave510 stale-owner/signature correction: CStart availability predicate used by CGame::RespawnPlayer when falling back to start points. The ECX-only body queries CMapWho around this+0x1c with radius 1.0, rejects active hostile/non-excluded owners within the observed distance threshold, returns false when a nearby hostile is found, and returns true when the start is clear. Static retail evidence only; exact CStart/map-who/flag/radius semantics, runtime respawn behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("start", "respawn", "availability", "stale-owner-corrected", "predicate")
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
