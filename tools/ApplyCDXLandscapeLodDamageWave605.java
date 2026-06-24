//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
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

public class ApplyCDXLandscapeLodDamageWave605 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] parameters;
        final String comment;
        final String[] allowedExistingNames;
        final String[] tags;

        Spec(
                String address,
                String name,
                String callingConvention,
                DataType returnType,
                ParameterImpl[] parameters,
                String comment,
                String[] allowedExistingNames,
                String[] tags) {
            this.address = address;
            this.name = name;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.parameters = parameters;
            this.comment = comment;
            this.allowedExistingNames = allowedExistingNames;
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
        Address address = toAddr(addressText);
        if (address == null) {
            throw new IllegalArgumentException("Bad address: " + addressText);
        }
        return address;
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
            "cdxlandscape-lod-damage-wave605",
            "retail-binary-evidence",
            "signature-corrected",
            "comment-hardened"
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
        Set<String> existing = tagNames(fn);
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

    private void verifyReadBack(Spec spec) throws Exception {
        Function readBack = functionAtEntry(spec.address);
        if (readBack == null) {
            throw new IllegalStateException("Read-back missing at " + spec.address);
        }
        if (!readBack.getName().equals(spec.name)) {
            throw new IllegalStateException("Read-back name mismatch at " + spec.address + ": " + readBack.getName());
        }
        if (!signatureMatches(readBack, spec)) {
            throw new IllegalStateException("Read-back signature mismatch at " + spec.address + ": " + readBack.getSignature());
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
                throw new IllegalStateException("Unexpected function name: " + fn.getName());
            }

            if (!needsUpdate(fn, spec)) {
                stats.skipped++;
                println("SKIP: " + spec.address + " already " + expectedSignature(spec));
                return;
            }

            boolean needsRename = !fn.getName().equals(spec.name);
            if (dryRun) {
                if (needsRename) {
                    stats.wouldRename++;
                }
                stats.skipped++;
                println("DRY: " + spec.address + " " + fn.getName() + " -> " + expectedSignature(spec));
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
            verifyReadBack(spec);
            stats.updated++;
            println("OK: " + spec.address + " " + expectedSignature(spec));
        } catch (Exception ex) {
            stats.bad++;
            println("FAIL: " + spec.address + " " + spec.name + " " + ex.getMessage());
        }
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");
        VoidDataType voidType = VoidDataType.dataType;
        PointerDataType voidPtr = new PointerDataType(voidType);
        IntegerDataType intType = IntegerDataType.dataType;
        DataType floatType = FloatDataType.dataType;
        DataType doubleType = DoubleDataType.dataType;
        DataType uintType = UnsignedIntegerDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x00546b10",
                "CDXLandscape__ResetCameraPosition",
                "__fastcall",
                voidType,
                new ParameterImpl[] { param("this", voidPtr) },
                "Wave605 CDXLandscape LOD/damage hardening: plain RET and all five fresh callsites load ECX from DAT_0089c9b0 before calling, confirming an ECX-only helper. The body checks this+0x24, writes float bits 0x4996b438 (1234567.0f) into the first resource-record camera/cache slot at +0x14, and when CGame__IsMultiplayer(DAT_008a9a98) is nonzero writes the same sentinel into the second record slot at +0x48. Callers are CGame restart/update/death/debug-camera/respawn paths, so the saved name is retained as a camera-position invalidation label. Static retail evidence only; exact resource-record layout, camera math semantics, runtime LOD behavior, source-body identity, BEA patching, and rebuild parity remain unproven.",
                new String[] {"CDXLandscape__ResetCameraPosition"},
                tags("cdxlandscape", "camera-reset", "ret-c3", "resource-record", "multiplayer")
            ),
            new Spec(
                "0x00546b40",
                "CDXLandscape__UpdateLOD",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("engine_context_470", voidPtr),
                    param("record_index", intType)
                },
                "Wave605 CDXLandscape LOD/damage hardening: RET 0x8 and callsite instruction read-back show two stack arguments after ECX. CDXEngine__Render pushes the active viewpoint/record index and engine+0x470 before calling with ECX=engine+0x10, and CDXLandscape__Render forwards its engine_context_470 and record_index stack arguments after reset. The body computes this+0x24 + record_index*0x34, samples the resource view/camera object through vtable slots 0 and 4, smooths cached camera vectors unless the 1234567.0f sentinel or DAT_008aa468[record_index] forces replacement, locks this+0x2c, iterates the 64x64 tile records, invalidates stale patch slots, allocates patch slots through CDXPatchManager__AllocatePatchSlot, queues CLandscapeTexture updates, writes LOD ranges into the index buffer, unlocks it, and flushes the texture update queue. Static retail evidence only; exact engine_context_470 class semantics, resource/tile/patch layouts, runtime LOD rendering, source-body identity, BEA patching, and rebuild parity remain unproven.",
                new String[] {"CDXLandscape__UpdateLOD"},
                tags("cdxlandscape", "update-lod", "ret-0x8", "tile-records", "patch-slots", "texture-update-queue")
            ),
            new Spec(
                "0x005475d0",
                "CDXEngine__ApplyLandscapeDamageStamp",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("world_x", floatType),
                    param("world_z", floatType),
                    param("stamp_value", intType)
                },
                "Wave605 CDXLandscape LOD/damage hardening: RET 0xc confirms three stack arguments, and callsites pass world_x/world_z float values plus a stamp_value from tree/rubble/world-load contexts. The body rate-limits against globals at 0x00650ab0/0x00650ab4, derives a stamp width from 1 << abs(stamp_value), maps world coordinates into 64x64 landscape cells and 0x80-local subcell coordinates, calls CDamage__RemoveCellEntryByCoords when stamp_value < 1 or CDamage__InsertCellEntry otherwise, then marks affected landscape texture/patch records under DAT_0089c9b0 for refresh. Static retail evidence only; the orphan 0x004da4fd callsite is treated as supplemental call evidence, and exact damage-entry layout, terrain deformation semantics, runtime damage behavior, source-body identity, BEA patching, and rebuild parity remain unproven.",
                new String[] {"CDXEngine__ApplyLandscapeDamageStamp"},
                tags("cdxlandscape", "damage-stamp", "ret-0xc", "damage-cells", "tile-refresh")
            ),
            new Spec(
                "0x00547a60",
                "CDXEngine__ComputeLandscapeTileComplexityScore",
                "__stdcall",
                doubleType,
                new ParameterImpl[] { param("tile_index", uintType) },
                "Wave605 CDXLandscape LOD/damage hardening: RET 0x4 and the CDXLandscape__Reset callsite prove one stack tile_index argument; the caller leaves ECX as the landscape object, but the body uses global heightfield pointers/scales and not ECX. The body maps tile_index through DAT_006fbdf0 into 0x9 by 0x9 packed height samples, evaluates midpoint-height deltas over three subdivision levels, tracks the maximum averaged absolute-delta score, multiplies by DAT_006fbdf4, and returns the value through the existing double return. CDXLandscape__Reset casts the result to float before storing it in each tile record. Static retail evidence only; exact heightfield sample format, terrain complexity formula naming, runtime LOD behavior, source-body identity, BEA patching, and rebuild parity remain unproven.",
                new String[] {"CDXEngine__ComputeLandscapeTileComplexityScore"},
                tags("cdxlandscape", "tile-complexity", "ret-0x4", "heightfield", "reset-helper")
            )
        };

        println("MODE: " + (dryRun ? "dry" : "apply"));
        Stats stats = new Stats();
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }
        println(
            "SUMMARY: updated=" + stats.updated +
            " skipped=" + stats.skipped +
            " renamed=" + stats.renamed +
            " would_rename=" + stats.wouldRename +
            " missing=" + stats.missing +
            " bad=" + stats.bad);
        if (!dryRun) {
            if (stats.bad == 0 && stats.missing == 0) {
                println("REPORT: Save succeeded");
            } else {
                println("REPORT: Save blocked by bad/missing rows");
            }
        } else {
            println("REPORT: Save succeeded");
        }
    }
}
