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
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyEngineOverlayBurstWave425 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final String comment;
        final String[] allowedExistingNames;
        final String[] tags;
        final ParameterImpl[] parameters;

        Spec(
                String address,
                String name,
                String callingConvention,
                DataType returnType,
                String comment,
                String[] allowedExistingNames,
                String[] tags,
                ParameterImpl[] parameters) {
            this.address = address;
            this.name = name;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.comment = comment;
            this.allowedExistingNames = allowedExistingNames;
            this.tags = tags;
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
            "engine-overlay-burst-wave425",
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

    private void applySpec(Spec spec, boolean dryRun, Stats stats) {
        try {
            Function fn = functionAtEntry(spec.address);
            if (fn == null) {
                stats.missing++;
                println("FAIL: " + spec.address + " " + spec.name + " Function not found");
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
        DataType intType = IntegerDataType.dataType;
        DataType floatType = FloatDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x00490220",
                "CEngine__ClearBurstOverlaySlotPayloads",
                "__fastcall",
                voidType,
                "Wave425 owner/name/signature hardening: engine +0x18 burst-overlay state helper clears six active overlay slot payload blocks with a 0x74-byte stride, leaving candidate count/header reset to CEngine__ResetBurstOverlayState. Static retail evidence only; exact state layout, projectile/burst semantics, runtime render behavior and rebuild parity remain unproven.",
                new String[] {"CEngine__ClearNearbyProjectileBurstSlots"},
                tags("engine", "burst-overlay", "overlay", "owner-corrected", "signature-hardened", "comment-hardened"),
                new ParameterImpl[] {param("burst_overlay_state", voidPtr)}),
            new Spec(
                "0x00490280",
                "CEngine__ResetBurstOverlayState",
                "__fastcall",
                intType,
                "Wave425 owner/name/signature hardening: resets the burst-overlay candidate count at +0x1c0, clears 0xae dwords from +0x1c4 through the candidate/active-slot storage, and returns 1 for the CEngine init success gate. Static retail evidence only; exact state layout, projectile/burst semantics, runtime render behavior and rebuild parity remain unproven.",
                new String[] {"CEngine__ResetBurstTrackingState"},
                tags("engine", "burst-overlay", "overlay", "owner-corrected", "signature-hardened", "comment-hardened"),
                new ParameterImpl[] {param("burst_overlay_state", voidPtr)}),
            new Spec(
                "0x004902b0",
                "CEngine__TrackBurstEventIfNearby",
                "__thiscall",
                voidType,
                "Wave425 signature/comment hardening: CEngine__TrackBurstEventFromPreset passes engine +0x18 burst-overlay state as this, a position/vector pointer, engine +0x470 gamut pointer, and two burst parameters. The body gates candidate count at +0x1c0 below 16, computes nearest global tracker distance, appends one 0x1c-byte candidate record when within threshold, and scales intensity into the candidate slot. Static retail evidence only; exact argument semantics, runtime projectile/burst behavior, concrete state layout, and rebuild parity remain unproven.",
                new String[] {},
                tags("engine", "burst-overlay", "projectile-burst", "signature-hardened", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("position", voidPtr),
                    param("gamut", voidPtr),
                    param("burst_type", intType),
                    param("intensity_scale", floatType)}),
            new Spec(
                "0x004903a0",
                "CDXEngine__BuildOverlaySlotFromSortedEntry",
                "__thiscall",
                voidType,
                "Wave425 signature/comment hardening: RET 0x8 proves two stack arguments; builds one 0x74-byte active overlay slot from a 0x1c-byte sorted candidate, samples static-shadow height, copies slot payload into DAT_009c65c0 for slot+2 render state, and marks overlay dirty/enabled flags. Static retail evidence only; exact state layout, runtime render behavior and rebuild parity remain unproven.",
                new String[] {},
                tags("dx-engine", "burst-overlay", "overlay", "signature-hardened", "comment-hardened"),
                new ParameterImpl[] {param("this", voidPtr), param("slot_index", intType), param("candidate_index", intType)}),
            new Spec(
                "0x004905f0",
                "CDXEngine__UpdateOverlaySlotsFromCandidateList",
                "__fastcall",
                voidType,
                "Wave425 signature/comment hardening: ECX-only update decays six active overlay slots, mirrors payloads into global render-state tables, ranks active slots and new candidates through Sort__QuickSortGeneric, calls CDXEngine__BuildOverlaySlotFromSortedEntry for selected candidates, and clears the candidate count at +0x1c0. Static retail evidence only; exact state layout, runtime render behavior and rebuild parity remain unproven.",
                new String[] {},
                tags("dx-engine", "burst-overlay", "overlay", "signature-hardened", "comment-hardened"),
                new ParameterImpl[] {param("burst_overlay_state", voidPtr)}),
            new Spec(
                "0x00490780",
                "CDXEngine__SetOverlaySlotsEnabledForActiveViews",
                "__thiscall",
                voidType,
                "Wave425 signature/comment hardening: RET 0x4 proves one stack argument; toggles global overlay enable flags from enabled, scans active slot flags at +0x1cc with a 0x74-byte stride, and marks the matching render-state slots dirty. Static retail evidence only; exact player-view semantics, state layout, runtime render behavior and rebuild parity remain unproven.",
                new String[] {},
                tags("dx-engine", "burst-overlay", "overlay", "signature-hardened", "comment-hardened"),
                new ParameterImpl[] {param("this", voidPtr), param("enabled", intType)})
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            if (monitor.isCancelled()) {
                break;
            }
            applySpec(spec, dryRun, stats);
        }

        println("--- SUMMARY ---");
        println(
            "SUMMARY updated=" + stats.updated +
            " skipped=" + stats.skipped +
            " created=" + stats.created +
            " would_create=" + stats.wouldCreate +
            " renamed=" + stats.renamed +
            " would_rename=" + stats.wouldRename +
            " missing=" + stats.missing +
            " bad=" + stats.bad
        );
        if (stats.missing != 0 || stats.bad != 0) {
            throw new IllegalStateException("Wave425 engine overlay/burst apply failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
