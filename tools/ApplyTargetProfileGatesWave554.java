//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.DataType;
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

public class ApplyTargetProfileGatesWave554 extends GhidraScript {
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
            "target-profile-gates-wave554",
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

        Spec[] specs = new Spec[] {
            new Spec(
                "0x00509e40",
                "TargetSet__GetEntryByIndex",
                "CBattleEngine__GetTargetSetEntryByIndex",
                "__cdecl",
                voidPtr(),
                new ParameterImpl[] {
                    param("target_entry_index", intType)
                },
                "Wave554 owner/signature/comment hardening: cdecl one-index helper over the global target/profile set at DAT_008553ec. The body resets the set iterator, advances by target_entry_index, and returns the selected entry pointer or null; Stuart-source GenericSPtrSet::At provides structural list-indexing parity, but this retail helper is fixed to the DAT_008553ec target/profile set. Static retail-binary evidence only; exact target-set ownership, concrete entry/layout types, runtime targeting behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("target-set", "target-profile", "owner-neutral-correction")
            ),
            new Spec(
                "0x00509e90",
                "ProjectileBurst__ResolvePresetByPercentBucketFallback",
                "CEngine__ResolvePresetByPercentBucketFallback",
                "__fastcall",
                voidPtr(),
                new ParameterImpl[] {
                    param("burst_context", voidPtr())
                },
                "Wave554 owner/signature/comment hardening: exclusive caller ProjectileBurst__SpawnFromPercentBucketFallback and body evidence show a burst-context helper, not a CEngine method. It rounds burst_context +0x60 into a percent bucket, reads the +0xa4 bucket table from offset +0xc, walks DAT_008553ec, and falls back to lower buckets until an entry pointer or null is found. Static retail-binary evidence only; exact burst/profile layout, preset identity, runtime projectile behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("projectile-burst", "target-profile", "percent-bucket", "owner-neutral-correction")
            ),
            new Spec(
                "0x00509f70",
                "TargetProfileContext__IsEligibleByDistanceBucketOrRange",
                "CUnit__IsEligibleByDistanceBucketOrRange",
                "__fastcall",
                intType,
                new ParameterImpl[] {
                    param("target_context", voidPtr())
                },
                "Wave554 owner/signature/comment hardening: broad callers from BattleEngine auto-targeting, Unit deploy/support, Sentinel flamethrower, and projectile-burst boundaries show a shared target/profile context gate rather than a CUnit-only method. If target_context +0xa0 is active it rejects expired range time at +0x64; otherwise it resolves +0x60 percent-bucket entries through the +0xa4 table and DAT_008553ec fallback scan. Static retail-binary evidence only; exact context/profile layouts, boolean contract, runtime targeting/projectile behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("target-profile", "range-gate", "percent-bucket", "owner-neutral-correction")
            ),
            new Spec(
                "0x0050a080",
                "TargetProfileContext__CanProceedByTargetRangeGate",
                "CEngine__CanProceedByTargetRangeGate",
                "__fastcall",
                intType,
                new ParameterImpl[] {
                    param("target_context", voidPtr())
                },
                "Wave554 owner/signature/comment hardening: callers from CGeneralVolume__DispatchMode3BurstProgressAndSpawn and CBattleEngineWalkerPart__ChargeWeapon pass a burst/target context, while the body only checks target_context +0xa0 and the range-time field at +0x64 against DAT_00672fd0. It returns false only for an active profile whose range-time gate has not elapsed. Static retail-binary evidence only; exact context/profile layout, boolean contract, runtime weapon behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("target-profile", "range-gate", "owner-neutral-correction")
            ),
            new Spec(
                "0x0050a0b0",
                "CSquadNormal__HasActiveMaskMatchWithTarget",
                "CSquadNormal__HasActiveMaskMatchWithTarget",
                "__thiscall",
                uintType,
                new ParameterImpl[] {
                    param("this", voidPtr()),
                    param("target_unit", voidPtr())
                },
                "Wave554 signature/comment hardening: RET 0x4 proves one explicit target_unit argument after ECX; the older second explicit parameter was register carryover. The body requires this +0x9c to be non-null and returns the active mask intersection between this +0xa8 and target_unit +0x34. Static retail-binary evidence only; exact CSquadNormal/support-list layouts, mask semantics, runtime squad behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("squad", "support-targeting", "mask-gate", "phantom-param-removed")
            ),
            new Spec(
                "0x0050a0d0",
                "CUnit__HasMaskBitsA8",
                "CUnit__HasMaskBitsA8",
                "__thiscall",
                uintType,
                new ParameterImpl[] {
                    param("this", voidPtr()),
                    param("mask_bits", uintType)
                },
                "Wave554 signature/comment hardening: RET 0x4 proves one explicit mask_bits argument after ECX; the older second explicit parameter was register carryover. The body returns this +0xa8 masked by mask_bits, and the checked caller is CSquadNormal__SelectBestSupportOrEscort. Static retail-binary evidence only; exact CUnit flag layout, mask semantics, runtime squad/support behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("cunit", "support-targeting", "mask-gate", "phantom-param-removed")
            ),
            new Spec(
                "0x0050a0e0",
                "OID__ComputeForwardProjectedPointTowardTarget",
                "OID__ComputeForwardProjectedPointTowardTarget",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr()),
                    param("out_point", voidPtr()),
                    param("target_unit", voidPtr())
                },
                "Wave554 signature/comment hardening: RET 0x8 and callsites from both OID ballistic fire checks prove two explicit stack arguments after ECX: out_point and target_unit; the older third explicit parameter was a decompiler artifact. With an active profile carrying +0xb0 the body samples this attachment/origin, target transform vfunc +0x168, target velocity vfunc +0x6c, profile speed/forward-vector fields, and DAT_005d857c to write a forward-projected target point. Without that profile path it copies the target transform vector into out_point. Static retail-binary evidence only; exact vector width, concrete OID/profile/target layouts, runtime aiming behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("oid", "projectile-ballistics", "target-projection", "phantom-param-removed")
            ),
            new Spec(
                "0x0050a290",
                "CUnit__IsTargetTimeoutBeforeProfileLimit",
                "CUnit__IsTargetTimeoutBeforeProfileLimit",
                "__fastcall",
                intType,
                new ParameterImpl[] {
                    param("unit", voidPtr())
                },
                "Wave554 signature/comment hardening: ECX-only predicate used by TargetSet__AnyUnitTargetTimeoutBeforeProfileLimit, CUnit__HasAnyLinkedUnitBeforeTargetTimeout, and CSquadNormal__SelectBestSupportOrEscort. The body returns true only when unit +0xa0 has a profile, unit +0x6c is nonzero, and the unit timeout is below profile +0x44. Static retail-binary evidence only; exact unit/profile layouts, timeout units, runtime squad/targeting behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("cunit", "target-profile", "timeout-gate")
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
            throw new IllegalStateException("Wave554 apply had missing/bad rows");
        }
    }
}
