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
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyInfluenceMapWave418 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final String comment;
        final String[] allowedExistingNames;
        final String[] tags;
        final boolean createIfMissing;
        final ParameterImpl[] parameters;

        Spec(
                String address,
                String name,
                String callingConvention,
                DataType returnType,
                String comment,
                String[] allowedExistingNames,
                String[] tags,
                boolean createIfMissing,
                ParameterImpl[] parameters) {
            this.address = address;
            this.name = name;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.comment = comment;
            this.allowedExistingNames = allowedExistingNames;
            this.tags = tags;
            this.createIfMissing = createIfMissing;
            this.parameters = parameters;
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

    private boolean allowedName(Spec spec, String actual) {
        if (actual.equals(spec.name)) {
            return true;
        }
        for (String allowed : spec.allowedExistingNames) {
            if (actual.equals(allowed)) {
                return true;
            }
        }
        return false;
    }

    private String expectedSignature(Spec spec) {
        StringBuilder sb = new StringBuilder();
        sb.append(spec.returnType.getDisplayName())
            .append(" ")
            .append(spec.callingConvention)
            .append(" ")
            .append(spec.name)
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

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "influencemap-wave418",
            "retail-binary-evidence"
        };
        String[] result = new String[common.length + extras.length];
        System.arraycopy(common, 0, result, 0, common.length);
        System.arraycopy(extras, 0, result, common.length, extras.length);
        return result;
    }

    private Set<String> tagNames(Function fn) {
        Set<String> names = new HashSet<>();
        for (FunctionTag tag : fn.getTags()) {
            names.add(tag.getName());
        }
        return names;
    }

    private Function getOrCreate(Spec spec, boolean dryRun, Stats stats) throws Exception {
        Function fn = functionAtEntry(spec.address);
        if (fn != null) {
            return fn;
        }
        if (!spec.createIfMissing) {
            stats.missing++;
            println("FAIL: " + spec.address + " " + spec.name + " Function not found");
            return null;
        }
        if (dryRun) {
            println("DRY: would create " + spec.address + " " + spec.name);
            stats.wouldCreate++;
            return null;
        }

        Address address = addr(spec.address);
        disassemble(address);
        fn = createFunction(address, null);
        if (fn == null) {
            fn = functionAtEntry(spec.address);
        }
        if (fn == null) {
            throw new IllegalStateException("Function create failed at " + spec.address);
        }
        fn.setName(spec.name, SourceType.USER_DEFINED);
        stats.created++;
        println("OK: created " + spec.address + " " + spec.name);
        return fn;
    }

    private void applySpec(Spec spec, boolean dryRun, Stats stats) {
        try {
            Function fn = getOrCreate(spec, dryRun, stats);
            if (fn == null) {
                return;
            }
            if (!allowedName(spec, fn.getName())) {
                throw new IllegalStateException("Unexpected function name at " + spec.address + ": " + fn.getName());
            }

            boolean needsRename = !fn.getName().equals(spec.name);
            if (dryRun) {
                if (needsRename) {
                    stats.wouldRename++;
                }
                println("DRY: " + spec.address + " " + fn.getName() + " -> " + expectedSignature(spec));
                stats.skipped++;
                return;
            }

            if (needsRename) {
                fn.setName(spec.name, SourceType.USER_DEFINED);
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

            Function readBack = functionAtEntry(spec.address);
            if (readBack == null) {
                throw new IllegalStateException("Read-back missing at " + spec.address);
            }
            if (!readBack.getName().equals(spec.name)) {
                throw new IllegalStateException("Read-back name mismatch at " + spec.address + ": " + readBack.getName());
            }
            String actualSignature = readBack.getSignature().toString();
            if (!actualSignature.equals(expectedSignature(spec))) {
                throw new IllegalStateException("Read-back signature mismatch at " + spec.address + ": " + actualSignature + " != " + expectedSignature(spec));
            }
            if (!spec.comment.equals(readBack.getComment())) {
                throw new IllegalStateException("Read-back comment mismatch at " + spec.address);
            }
            Set<String> readBackTags = tagNames(readBack);
            for (String tag : spec.tags) {
                if (!readBackTags.contains(tag)) {
                    throw new IllegalStateException("Read-back missing tag " + tag + " at " + spec.address);
                }
            }

            println("OK: " + spec.address + " " + readBack.getSignature().toString());
            stats.updated++;
            Thread.sleep(50);
        } catch (Exception ex) {
            stats.bad++;
            println("FAIL: " + spec.address + " " + spec.name + " " + ex.getClass().getSimpleName() + ": " + ex.getMessage());
        }
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");
        println("Mode: " + (dryRun ? "dry" : "apply"));

        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);
        DataType charPtr = new PointerDataType(CharDataType.dataType);
        DataType byteType = ByteDataType.dataType;
        DataType intType = IntegerDataType.dataType;
        DataType floatType = FloatDataType.dataType;
        DataType boolType = BooleanDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x0048afb0",
                "CInfluenceMap__FreeObjectIfPresent",
                "__fastcall",
                voidType,
                "Wave418 signature/comment hardening: frees all objects in the manager/map-owned object sets at +0x08 and +0x18, dispatching the first set through the pointed vtable slot and the second through OID__FreeObject. Static cleanup evidence only; runtime influence behavior and concrete set ownership remain unproven.",
                new String[] {},
                tags("influencemap", "cleanup", "signature-hardened", "comment-hardened"),
                false,
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec(
                "0x0048b010",
                "CInfluenceMapManager__Load",
                "__thiscall",
                voidType,
                "Wave418 signature/comment hardening: clears existing influence maps and temporary influence records, reads level influence-map versions 0/1 from a CDXMemBuffer-style stream, allocates 0xc4-byte map nodes and 8-byte neighbor links, then seeds update/decay scheduling. Static load-format evidence only; concrete layout and runtime AI behavior remain unproven.",
                new String[] {},
                tags("influencemap", "load", "signature-hardened", "comment-hardened"),
                false,
                new ParameterImpl[] {param("this", voidPtr), param("mem_buffer", voidPtr)}),
            new Spec(
                "0x0048b5f0",
                "CInfluenceMap__GetTypeName_0048b5f0",
                "__fastcall",
                charPtr,
                "Wave418 recovered CInfluenceMap vtable 0x005dc050 slot 7: returns the static type-name string at 0x0062d658, read back as CInfluenceNode. Static vtable/string evidence only; exact source virtual name remains unproven.",
                new String[] {},
                tags("influencemap", "vtable-slot", "function-boundary", "string-return", "signature-hardened", "comment-hardened"),
                true,
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec(
                "0x0048b600",
                "CInfluenceMap__GetTypeId_0048b600",
                "__fastcall",
                intType,
                "Wave418 recovered CInfluenceMap vtable 0x005dc050 slot 8: returns constant 0x1e for the InfluenceMap/CInfluenceNode type family. Static vtable evidence only; exact source enum label remains unproven.",
                new String[] {},
                tags("influencemap", "vtable-slot", "function-boundary", "type-id", "signature-hardened", "comment-hardened"),
                true,
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec(
                "0x0048b610",
                "CInfluenceMap__GetInfluenceRadius_0048b610",
                "__fastcall",
                floatType,
                "Wave418 recovered CInfluenceMap vtable 0x005dc050 slot 16: returns float field this+0x94, the radius used by manager nearest-map distance tests. Static vtable/field evidence only; exact source field name remains unproven.",
                new String[] {},
                tags("influencemap", "vtable-slot", "function-boundary", "radius-getter", "signature-hardened", "comment-hardened"),
                true,
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec(
                "0x0048b620",
                "CInfluenceMap__ResetInfluence",
                "__fastcall",
                voidType,
                "Wave418 signature/comment hardening: clears influence accumulators at +0x9c/+0xa0/+0xa4/+0xa8 and target influence at +0xb8, then seeds distance counters +0xac/+0xb0 to 99999. Static field-write evidence only; concrete layout names and runtime AI behavior remain unproven.",
                new String[] {},
                tags("influencemap", "reset", "signature-hardened", "comment-hardened"),
                false,
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec(
                "0x0048b660",
                "CInfluenceMapManager__SkipLoad",
                "__stdcall",
                voidType,
                "Wave418 signature/comment hardening: reads and discards influence-map versions 0/1 from a CDXMemBuffer-style stream without allocating map nodes or links. Static skip-loader evidence only; concrete file-format field names remain unproven.",
                new String[] {},
                tags("influencemap", "load", "skip-load", "signature-hardened", "comment-hardened"),
                false,
                new ParameterImpl[] {param("mem_buffer", voidPtr)}),
            new Spec(
                "0x0048b7d0",
                "CInfluenceMapManager__PropagateDistances",
                "__fastcall",
                voidType,
                "Wave418 signature/comment hardening: calls CInfluenceMap__CalculateInfluence with smoothing enabled, relaxes neighbor distance counters for 0x14 passes, and schedules event 0x3e9 through CEventManager__AddEvent_AtTime. Static scheduling evidence only; runtime AI behavior remains unproven.",
                new String[] {},
                tags("influencemap", "distance-propagation", "event-scheduled", "signature-hardened", "comment-hardened"),
                false,
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec(
                "0x0048b8e0",
                "CInfluenceMapManager__Update",
                "__thiscall",
                voidType,
                "Wave418 signature/comment hardening: resets all maps, scans two live object lists for eligible actors, adds faction/channel influence to nearest map regions, applies temporary influence records, diffuses empty regions for 10 passes, relaxes distances for 0x14 passes, recalculates influence, and reschedules event 1000. Static evidence only; runtime AI behavior and concrete unit taxonomy remain unproven.",
                new String[] {},
                tags("influencemap", "update", "event-scheduled", "signature-hardened", "comment-hardened"),
                false,
                new ParameterImpl[] {param("this", voidPtr), param("event_time", floatType)}),
            new Spec(
                "0x0048bf70",
                "CInfluenceMapManager__DecayInfluence",
                "__fastcall",
                voidType,
                "Wave418 signature/comment hardening: walks temporary influence records at manager+0x18, decrements each amount by the decay constant, frees depleted records, and reschedules event 0x3ea. Static scheduling evidence only; runtime influence behavior remains unproven.",
                new String[] {},
                tags("influencemap", "temporary-influence", "event-scheduled", "signature-hardened", "comment-hardened"),
                false,
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec(
                "0x0048c000",
                "CInfluenceMapManager__FindNearestMap",
                "__thiscall",
                voidType,
                "Wave418 signature/comment hardening: allocates a 12-byte temporary influence record, finds the nearest loaded map using Manhattan distance minus map radius, stores the influence amount and channel, and queues the record at manager+0x18. Static nearest-map evidence only; concrete channel semantics and runtime AI behavior remain unproven.",
                new String[] {},
                tags("influencemap", "temporary-influence", "nearest-map", "signature-hardened", "comment-hardened"),
                false,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("x", floatType),
                    param("z", floatType),
                    param("influence_amount", floatType),
                    param("influence_channel", intType)}),
            new Spec(
                "0x0048c2d0",
                "CInfluenceMapManager__IsEmpty",
                "__fastcall",
                boolType,
                "Wave418 signature/comment hardening: returns whether the map list count at manager+0x14 is less than one. Static manager-list evidence only; runtime AI behavior remains unproven.",
                new String[] {},
                tags("influencemap", "predicate", "signature-hardened", "comment-hardened"),
                false,
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec(
                "0x0048c2e0",
                "CInfluenceMap__scalar_deleting_dtor",
                "__thiscall",
                voidPtr,
                "Wave418 name/signature correction: CInfluenceMap scalar-deleting destructor wrapper calls CInfluenceMap__dtor, checks flags bit 0, optionally frees this through OID__FreeObject, and returns this. Static destructor evidence only; runtime cleanup behavior remains unproven.",
                new String[] {"CInfluenceMap__ScalarDelete"},
                tags("influencemap", "destructor", "owner-corrected", "signature-corrected", "comment-hardened"),
                false,
                new ParameterImpl[] {param("this", voidPtr), param("flags", byteType)}),
            new Spec(
                "0x0048c300",
                "CInfluenceMap__dtor",
                "__fastcall",
                voidType,
                "Wave418 name/signature correction: CInfluenceMap destructor clears the neighbor set at this+0x7c and delegates to CComplexThing__dtor_base. Static destructor evidence only; runtime cleanup behavior remains unproven.",
                new String[] {"CInfluenceMap__Destructor"},
                tags("influencemap", "destructor", "owner-corrected", "signature-corrected", "comment-hardened"),
                false,
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec(
                "0x0048c350",
                "CInfluenceMap__DetachNeighborLinks_0048c350",
                "__fastcall",
                voidType,
                "Wave418 recovered CInfluenceMap vtable 0x005dc050 slot 2: drains neighbor-link records from this+0x7c, removes each linked record from CSPtrSet, frees it through OID__FreeObject, then delegates to the CComplexThing slot-2 handler. Static vtable/cleanup evidence only; exact source virtual name remains unproven.",
                new String[] {},
                tags("influencemap", "vtable-slot", "function-boundary", "cleanup", "signature-hardened", "comment-hardened"),
                true,
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec(
                "0x0048c390",
                "CInfluenceMap__InitFromComplexThingInit_0048c390",
                "__thiscall",
                voidType,
                "Wave418 name/signature correction: CInfluenceMap vtable 0x005dc050 slot 9 is an init-forwarding wrapper, not a list-removal body; it marks init+0x70 as -1, clears bit 1 in this+0x2c, and delegates to CComplexThing__Init. Static init/vtable evidence only; concrete init layout remains unproven.",
                new String[] {"CInfluenceMap__RemoveFromList"},
                tags("influencemap", "vtable-slot", "init-wrapper", "owner-corrected", "signature-corrected", "comment-hardened"),
                false,
                new ParameterImpl[] {param("this", voidPtr), param("init", voidPtr)}),
            new Spec(
                "0x0048c3b0",
                "CInfluenceMap__CalculateInfluence",
                "__thiscall",
                voidType,
                "Wave418 signature/comment hardening: computes target influence ratio from +0x9c and +0xa4, derives neutral/faction state at +0xbc from self and neighbor totals, clamps zero-ratio faction cases to -1 or +1, and optionally smooths +0xb4 toward +0xb8. Static field evidence only; runtime AI behavior remains unproven.",
                new String[] {},
                tags("influencemap", "influence-calculation", "signature-hardened", "comment-hardened"),
                false,
                new ParameterImpl[] {param("this", voidPtr), param("smooth", intType)})
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            if (monitor.isCancelled()) {
                throw new RuntimeException("Cancelled");
            }
            applySpec(spec, dryRun, stats);
        }

        println(
            "SUMMARY updated=" + stats.updated
            + " skipped=" + stats.skipped
            + " created=" + stats.created
            + " would_create=" + stats.wouldCreate
            + " renamed=" + stats.renamed
            + " would_rename=" + stats.wouldRename
            + " missing=" + stats.missing
            + " bad=" + stats.bad
        );

        if (stats.missing != 0 || stats.bad != 0) {
            throw new IllegalStateException("Wave418 InfluenceMap apply had failures");
        }
    }
}
