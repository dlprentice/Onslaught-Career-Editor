//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
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

public class ApplySharedUnitVtableBoundaryWave1083 extends GhidraScript {
    private static final String WAVE_TAG = "shared-unit-vtable-boundary-review-wave1083";

    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] parameters;
        final String[] excludedBodyAddresses;
        final String comment;
        final String[] tags;

        Spec(String address, String name, String callingConvention, DataType returnType,
                ParameterImpl[] parameters, String[] excludedBodyAddresses, String comment, String[] tags) {
            this.address = address;
            this.name = name;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.parameters = parameters;
            this.excludedBodyAddresses = excludedBodyAddresses;
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
        int signatureUpdated = 0;
        int commentOnlyUpdated = 0;
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

    private Function functionAtEntry(Address address) {
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

    private String expectedSignature(Spec spec) {
        StringBuilder sb = new StringBuilder();
        sb.append(spec.returnType.getDisplayName()).append(" ")
            .append(spec.callingConvention).append(" ")
            .append(spec.name).append("(");
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

    private Set<String> tagNames(Function fn) {
        Set<String> result = new HashSet<>();
        for (FunctionTag tag : fn.getTags()) {
            result.add(tag.getName());
        }
        return result;
    }

    private boolean hasAllTags(Function fn, Spec spec) {
        Set<String> actual = tagNames(fn);
        for (String tag : spec.tags) {
            if (!actual.contains(tag)) {
                return false;
            }
        }
        return true;
    }

    private Function getOrCreate(Spec spec, boolean dryRun, Stats stats) throws Exception {
        Address address = addr(spec.address);
        Function existing = functionAtEntry(address);
        if (existing != null) {
            return existing;
        }
        Function containing = getFunctionContaining(address);
        if (containing != null) {
            throw new IllegalStateException("Address is inside existing function "
                + containing.getName() + " at " + containing.getEntryPoint());
        }
        if (getInstructionAt(address) == null) {
            throw new IllegalStateException("No instruction at " + spec.address);
        }
        if (dryRun) {
            stats.wouldCreate++;
            println("DRY_CREATE: " + spec.address + " -> " + expectedSignature(spec));
            return null;
        }

        boolean disasmOk = disassemble(address);
        Function created = createFunction(address, spec.name);
        if (created == null) {
            throw new IllegalStateException("createFunction returned null at " + spec.address + " (disassemble=" + disasmOk + ")");
        }
        stats.created++;
        return created;
    }

    private void applySpec(Spec spec, boolean dryRun, Stats stats) throws Exception {
        Function fn = getOrCreate(spec, dryRun, stats);
        if (fn == null) {
            return;
        }

        boolean renameNeeded = !fn.getName().equals(spec.name);
        boolean signatureNeedsUpdate = !signatureMatches(fn, spec);
        boolean commentOrTagsNeedUpdate = fn.getComment() == null
            || !fn.getComment().equals(spec.comment)
            || !hasAllTags(fn, spec);

        if (!renameNeeded && !signatureNeedsUpdate && !commentOrTagsNeedUpdate) {
            println("SKIP: " + spec.address + " " + spec.name);
            stats.skipped++;
            return;
        }
        if (dryRun) {
            println("DRY: " + spec.address + " " + fn.getName() + " -> " + expectedSignature(spec));
            stats.skipped++;
            if (renameNeeded) {
                stats.wouldRename++;
            }
            if (signatureNeedsUpdate) {
                stats.signatureUpdated++;
            } else if (commentOrTagsNeedUpdate) {
                stats.commentOnlyUpdated++;
            }
            return;
        }

        if (renameNeeded) {
            fn.setName(spec.name, SourceType.USER_DEFINED);
            stats.renamed++;
        }
        if (signatureNeedsUpdate) {
            fn.setCallingConvention(spec.callingConvention);
            fn.setReturnType(spec.returnType, SourceType.USER_DEFINED);
            fn.replaceParameters(
                FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS,
                true,
                SourceType.USER_DEFINED,
                spec.parameters
            );
            stats.signatureUpdated++;
        }
        fn.setComment(spec.comment);
        Set<String> existingTags = tagNames(fn);
        for (String tag : spec.tags) {
            if (!existingTags.contains(tag)) {
                fn.addTag(tag);
            }
        }
        if (!signatureNeedsUpdate && commentOrTagsNeedUpdate) {
            stats.commentOnlyUpdated++;
        }
        verifyReadBack(spec);
        println("OK: " + spec.address + " " + spec.name + " -> " + expectedSignature(spec));
        stats.updated++;
        Thread.sleep(50L);
    }

    private void verifyReadBack(Spec spec) throws Exception {
        Function fn = functionAtEntry(addr(spec.address));
        if (fn == null) {
            throw new IllegalStateException("Read-back missing at " + spec.address);
        }
        if (!fn.getName().equals(spec.name)) {
            throw new IllegalStateException("Read-back name mismatch at " + spec.address + ": " + fn.getName());
        }
        if (!signatureMatches(fn, spec)) {
            throw new IllegalStateException("Read-back signature mismatch at " + spec.address + ": " + fn.getSignature());
        }
        if (fn.getComment() == null || !fn.getComment().equals(spec.comment)) {
            throw new IllegalStateException("Read-back comment mismatch at " + spec.address);
        }
        if (!hasAllTags(fn, spec)) {
            throw new IllegalStateException("Read-back tag mismatch at " + spec.address);
        }
        for (String excluded : spec.excludedBodyAddresses) {
            if (fn.getBody().contains(addr(excluded))) {
                throw new IllegalStateException("Read-back body for " + spec.address
                    + " unexpectedly absorbed " + excluded);
            }
        }
    }

    private String[] tags(String... extra) {
        String[] base = new String[] {
            "static-reaudit",
            WAVE_TAG,
            "wave1083-readback-verified",
            "retail-binary-evidence",
            "function-boundary-recovered",
            "comment-hardened",
            "signature-hardened",
            "shared-vfunc",
            "unit-family-vtable"
        };
        String[] result = new String[base.length + extra.length];
        System.arraycopy(base, 0, result, 0, base.length);
        System.arraycopy(extra, 0, result, base.length, extra.length);
        return result;
    }

    @Override
    protected void run() throws Exception {
        boolean dryRun = isDryRun(getScriptArgs().length > 0 ? getScriptArgs()[0] : "dry");
        PointerDataType voidPtr = new PointerDataType(VoidDataType.dataType);
        DataType intType = IntegerDataType.dataType;
        DataType floatType = FloatDataType.dataType;
        DataType voidType = VoidDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x00405d90",
                "SharedUnitVFunc__ReturnField130ColorMask_00405d90",
                "__thiscall",
                intType,
                new ParameterImpl[] { param("this", voidPtr) },
                new String[] { "0x00405db0" },
                "Wave1083 shared unit-family vtable-boundary recovery: CAirUnit, CRadar, and multiple neighboring unit-derived vtables point at this previously functionless body. It reads this+0x130 and returns one of two packed color/mask constants through a short branch path. Static retail Ghidra listing/xref/vtable evidence only; exact source virtual name, concrete field semantics, runtime behavior, BEA patching, and rebuild parity remain separate proof.",
                tags("color-mask", "field130")
            ),
            new Spec(
                "0x00405e60",
                "SharedUnitVFunc__ReturnFloat005d8ba0_00405e60",
                "__thiscall",
                floatType,
                new ParameterImpl[] { param("this", voidPtr) },
                new String[] { "0x00405e70" },
                "Wave1083 shared unit-family vtable-boundary recovery: CAirUnit, CRadar, and related unit-family vtables point at this previously functionless float-return stub. The body loads the static float at 0x005d8ba0 and returns before the adjacent null-check helper at 0x00405e70. Static retail Ghidra listing/xref/vtable evidence only; exact source virtual name, runtime behavior, BEA patching, and rebuild parity remain separate proof.",
                tags("float-return", "constant-return")
            ),
            new Spec(
                "0x004f9260",
                "SharedUnitVFunc__BuildField164TargetVectorContext_004f9260",
                "__thiscall",
                voidType,
                new ParameterImpl[] { param("this", voidPtr) },
                new String[] { "0x004f9430" },
                "Wave1083 shared unit-family vtable-boundary recovery: CAirUnit and CRadar-style vtable slots point at this previously functionless body. The body builds a large stack-local vector/context block when this+0x164 is present, samples owner/vector state, and stops before CUnit__ApplyRandomDestructibleDamageBurst at 0x004f9430. Static retail Ghidra listing/xref/vtable evidence only; exact source virtual name, concrete layout semantics, runtime targeting/render behavior, BEA patching, and rebuild parity remain separate proof.",
                tags("target-context", "field164", "large-stack")
            ),
            new Spec(
                "0x004fda90",
                "SharedUnitVFunc__FindActiveMemberByField18c_004fda90",
                "__thiscall",
                intType,
                new ParameterImpl[] { param("this", voidPtr) },
                new String[] { "0x004fdad0" },
                "Wave1083 shared unit-family vtable-boundary recovery: CAirUnit/CRadar/GillMHead style vtable rows point at this previously functionless boolean body. It walks a linked list at this+0x18c, calls 0x004e43d0 on entries, returns 1 on a qualifying entry, and stops before CUnit__TrySpawnMembersForTarget at 0x004fdad0. Static retail Ghidra listing/xref/vtable evidence only; exact source virtual name, concrete list semantics, runtime behavior, BEA patching, and rebuild parity remain separate proof.",
                tags("linked-list", "field18c", "boolean")
            ),
            new Spec(
                "0x004fdd00",
                "SharedUnitVFunc__SetField244ModeAndDispatchF4_004fdd00",
                "__thiscall",
                voidType,
                new ParameterImpl[] { param("this", voidPtr) },
                new String[] { "0x004fdd60" },
                "Wave1083 shared unit-family vtable-boundary recovery: repeated unit-derived vtable rows point at this previously functionless body. It checks this+0x244 mode, builds a small vector/context argument through 0x004fd910, dispatches virtual slot +0xf4, stores mode 1 at this+0x244, and returns before the adjacent 0x004fdd60 body. Static retail Ghidra listing/xref/vtable evidence only; exact source virtual name, concrete mode/context semantics, runtime behavior, BEA patching, and rebuild parity remain separate proof.",
                tags("field244", "virtual-dispatch", "mode")
            ),
            new Spec(
                "0x004fe2b0",
                "SharedUnitVFunc__MarkField17cEntriesForName_004fe2b0",
                "__thiscall",
                voidType,
                new ParameterImpl[] { param("this", voidPtr), param("name", voidPtr) },
                new String[] { "0x004fe310" },
                "Wave1083 shared unit-family vtable-boundary recovery: several unit-family vtable rows point at this previously functionless RET 0x4 body. It walks the this+0x17c entry list, compares each entry name-like field through 0x00568390, sets entry+0x9c when the supplied stack argument does not match, and returns before 0x004fe310. Static retail Ghidra listing/xref/vtable evidence only; exact source virtual name, concrete list/name semantics, runtime behavior, BEA patching, and rebuild parity remain separate proof.",
                tags("field17c", "name-filter", "ret4")
            ),
            new Spec(
                "0x004fe310",
                "SharedUnitVFunc__TestField17cEntryNameMatch_004fe310",
                "__thiscall",
                intType,
                new ParameterImpl[] { param("this", voidPtr), param("name", voidPtr) },
                new String[] { "0x004fe390" },
                "Wave1083 shared unit-family vtable-boundary recovery: several unit-family vtable rows point at this previously functionless RET 0x4 boolean body. It walks the this+0x17c entry list, compares an entry name-like field through 0x00568390, returns a boolean-style result, and stops before CEngine__EnableThingByNameFlag at 0x004fe390. Static retail Ghidra listing/xref/vtable evidence only; exact source virtual name, concrete list/name semantics, runtime behavior, BEA patching, and rebuild parity remain separate proof.",
                tags("field17c", "name-filter", "ret4", "boolean")
            ),
            new Spec(
                "0x00417630",
                "SharedUnitVFunc__ReturnObject114OrOne_00417630",
                "__thiscall",
                intType,
                new ParameterImpl[] { param("this", voidPtr) },
                new String[] { "0x004176a0" },
                "Wave1083 shared unit-family vtable-boundary recovery: repeated unit-family vtable rows point at this previously functionless small helper. It reads an object pointer, returns object+0x114 when present, returns 1 otherwise, and stops before CBuilding__scalar_deleting_dtor at 0x004176a0. Static retail Ghidra listing/xref/vtable evidence only; exact source virtual name, concrete field semantics, runtime behavior, BEA patching, and rebuild parity remain separate proof.",
                tags("field114", "fallback-one")
            ),
            new Spec(
                "0x00405e70",
                "SharedUnitVFunc__IsField168Null_00405e70",
                "__thiscall",
                intType,
                new ParameterImpl[] { param("this", voidPtr) },
                new String[] { "0x00405e80" },
                "Wave1083 shared unit-family vtable-boundary recovery: repeated unit-family vtable rows point at this previously functionless boolean stub. It tests this+0x168 and returns whether that field is null, stopping before the existing SharedVFunc__WriteZeroVectorRet04_00405e80 body. Static retail Ghidra listing/xref/vtable evidence only; exact source virtual name, concrete field semantics, runtime behavior, BEA patching, and rebuild parity remain separate proof.",
                tags("field168", "boolean")
            ),
            new Spec(
                "0x004fe5c0",
                "SharedUnitVFunc__ReturnField164B4ScaledByMode_004fe5c0",
                "__thiscall",
                floatType,
                new ParameterImpl[] { param("this", voidPtr) },
                new String[] { "0x004fe5f0" },
                "Wave1083 shared unit-family vtable-boundary recovery: repeated unit-family vtable rows point at this previously functionless float-return body. It checks this+0x244 mode, returns float field this+0x164+0xb4 directly for most modes, or multiplies it by static float 0x005d8bd8 for modes 1/2, stopping before 0x004fe5f0. Static retail Ghidra listing/xref/vtable evidence only; exact source virtual name, concrete mode/field semantics, runtime behavior, BEA patching, and rebuild parity remain separate proof.",
                tags("field164", "field244", "float-return")
            ),
            new Spec(
                "0x00405ea0",
                "SharedUnitVFunc__ReturnFloat005d8578_00405ea0",
                "__thiscall",
                floatType,
                new ParameterImpl[] { param("this", voidPtr) },
                new String[] { "0x00405eb0" },
                "Wave1083 shared unit-family vtable-boundary recovery: repeated unit-family vtable rows point at this previously functionless float-return stub. The body loads the static float at 0x005d8578 and returns before the vector-copy helper at 0x00405eb0. Static retail Ghidra listing/xref/vtable evidence only; exact source virtual name, runtime behavior, BEA patching, and rebuild parity remain separate proof.",
                tags("float-return", "constant-return")
            ),
            new Spec(
                "0x00405eb0",
                "SharedUnitVFunc__CopyVector1cToOut_00405eb0",
                "__thiscall",
                voidType,
                new ParameterImpl[] { param("this", voidPtr), param("outVector", voidPtr) },
                new String[] { "0x00405ed0" },
                "Wave1083 shared unit-family vtable-boundary recovery: repeated unit-family vtable rows point at this previously functionless RET 0x4 vector-copy body. It copies four dwords from this+0x1c into the caller output buffer and returns before the adjacent class-name stub at 0x00405ed0. Static retail Ghidra listing/xref/vtable evidence only; exact source virtual name, concrete vector semantics, runtime behavior, BEA patching, and rebuild parity remain separate proof.",
                tags("vector-copy", "field1c", "ret4")
            ),
            new Spec(
                "0x004fe5f0",
                "SharedUnitVFunc__ScheduleEvent7d0WithMinusOne_004fe5f0",
                "__thiscall",
                voidType,
                new ParameterImpl[] { param("this", voidPtr) },
                new String[] { "0x004fe620" },
                "Wave1083 shared unit-family vtable-boundary recovery: repeated unit-family vtable rows point at this previously functionless event-scheduling helper. It builds a small stack payload with -1.0, calls the event manager-like object at 0x00672fc8 with event id 0x7d0, returns, and stops before the adjacent global-vector clear body at 0x004fe620. Static retail Ghidra listing/xref/vtable evidence only; exact source virtual name, event meaning, runtime behavior, BEA patching, and rebuild parity remain separate proof.",
                tags("event-schedule", "event7d0")
            )
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            try {
                applySpec(spec, dryRun, stats);
            } catch (Exception ex) {
                println("FAIL: " + spec.address + " " + spec.name + " "
                    + ex.getClass().getSimpleName() + ": " + ex.getMessage());
                stats.bad++;
            }
        }

        println(
            "SUMMARY: updated=" + stats.updated
            + " skipped=" + stats.skipped
            + " created=" + stats.created
            + " would_create=" + stats.wouldCreate
            + " renamed=" + stats.renamed
            + " would_rename=" + stats.wouldRename
            + " signature_updated=" + stats.signatureUpdated
            + " comment_only_updated=" + stats.commentOnlyUpdated
            + " bad=" + stats.bad
        );
        if (stats.bad != 0) {
            throw new IllegalStateException("Wave1083 shared unit-family vtable-boundary recovery encountered bad rows");
        }
    }
}
