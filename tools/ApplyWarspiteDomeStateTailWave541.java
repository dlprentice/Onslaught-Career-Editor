//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.BooleanDataType;
import ghidra.program.model.data.DataType;
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

public class ApplyWarspiteDomeStateTailWave541 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] parameters;
        final String comment;
        final String[] tags;
        final String[] allowedExistingNames;

        Spec(String address, String name, String callingConvention, DataType returnType,
                ParameterImpl[] parameters, String comment, String[] tags,
                String[] allowedExistingNames) {
            this.address = address;
            this.name = name;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.parameters = parameters;
            this.comment = comment;
            this.tags = tags;
            this.allowedExistingNames = allowedExistingNames;
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
            "warspite-dome-state-wave541",
            "retail-binary-evidence",
            "owner-corrected",
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

    private void applySpec(Spec spec, boolean dryRun, Stats stats) throws Exception {
        Function fn = functionAtEntry(spec.address);
        if (fn == null) {
            println("MISSING: " + spec.address);
            stats.missing++;
            return;
        }
        if (!allowedName(spec, fn.getName())) {
            println("BADNAME: " + spec.address + " " + fn.getName() + " expected " + spec.name);
            stats.bad++;
            return;
        }

        boolean needsRename = !fn.getName().equals(spec.name);
        boolean update = needsUpdate(fn, spec);
        if (dryRun) {
            if (needsRename) {
                println("DRYRENAME: " + spec.address + " " + fn.getName() + " -> " + expectedSignature(spec));
                stats.wouldRename++;
            } else {
                println((update ? "DRY: " : "SKIP: ") + spec.address + " " + expectedSignature(spec));
            }
            stats.skipped++;
            return;
        }
        if (!update) {
            println("SKIP: " + spec.address + " already current");
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
        verifyReadBack(spec);
        println("OK: " + spec.address + " " + functionAtEntry(spec.address).getSignature());
        stats.updated++;
        Thread.sleep(50);
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");
        println("Mode: " + (dryRun ? "dry" : "apply"));

        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);
        DataType boolType = BooleanDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x00504a50",
                "CWarspiteDome__UpdatePitchStateAndBlendTracks",
                "__fastcall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave541 WarspiteDome state-tail owner/signature correction: vtable 0x005e02c0 slot 9 and fields initialized by CWarspiteDome__Init identify the prior CVBufTexture owner prefix as stale. The register-only body calls CGroundUnit__UpdateLinkedEffectsByHeightClearance, refreshes tracked pitch through CWarspiteDome__UpdateTrackedPitchWithClamp, advances fields +0x260/+0x280/+0x284 when state +0x214 is active, and updates six blend/track entries at +0x268/+0x288. Static retail evidence only; exact dome state names, animation/blend semantics, runtime behavior, and rebuild parity remain unproven.",
                tags("warspite-dome", "state-update", "blend-tracks", "renamed"),
                new String[] {"CVBufTexture__UpdatePitchStateAndBlendTracks"}
            ),
            new Spec(
                "0x00504b40",
                "CWarspiteDome__UpdateTrackedPitchWithClamp",
                "__fastcall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave541 WarspiteDome state-tail owner/signature correction: internal register-only helper called by CWarspiteDome__UpdatePitchStateAndBlendTracks. The body skips when flag bit +0x2c bit 2 is set, refreshes field +0xec from target/ballistic pitch context through OID__SolveBallisticPitchToTarget when linked objects are present, resets timer +0x20c to global time plus a static interval, and clamps +0xec between observed constants. Static retail evidence only; exact pitch-field meaning, target context layout, runtime aiming behavior, and rebuild parity remain unproven.",
                tags("warspite-dome", "pitch-clamp", "ballistic-context", "renamed"),
                new String[] {"CVBufTexture__UpdateTrackedPitchWithClamp"}
            ),
            new Spec(
                "0x00504cf0",
                "CWarspiteDome__ShouldSkipUpdateByStateFlags",
                "__fastcall",
                boolType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave541 WarspiteDome state-tail owner/signature correction: vtable 0x005e02c0 slot 19 and Unit-family caller/field context identify the prior CVBufTexture owner prefix as stale. The register-only predicate returns true when CUnit__HasAnyLinkedUnitBeforeTargetTimeout succeeds, when state +0x168 is zero and +0x214 is active, or when flag bit +0x2c bit 2 is set; otherwise it returns false. Static retail evidence only; exact state/flag names, runtime update gating, and rebuild parity remain unproven.",
                tags("warspite-dome", "state-gate", "linked-timeout", "renamed"),
                new String[] {"CVBufTexture__ShouldSkipUpdateByStateFlags"}
            ),
            new Spec(
                "0x00504d30",
                "CWarspiteDome__IsTransitionAllowedByState",
                "__fastcall",
                boolType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave541 WarspiteDome state-tail owner/signature correction: vtable 0x005e0380 slot 4 and Unit-family field context identify the prior CVBufTexture owner prefix as stale. The register-only predicate returns true when CUnit__HasAnyLinkedUnitBeforeTargetTimeout succeeds, otherwise it allows the transition only when state field +0x168 is zero. Static retail evidence only; exact transition meaning, linked-timeout semantics, runtime behavior, and rebuild parity remain unproven.",
                tags("warspite-dome", "transition-gate", "linked-timeout", "renamed"),
                new String[] {"CVBufTexture__IsTransitionAllowedByState"}
            )
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }
        println("SUMMARY updated=" + stats.updated + " skipped=" + stats.skipped +
            " renamed=" + stats.renamed + " would_rename=" + stats.wouldRename +
            " missing=" + stats.missing + " bad=" + stats.bad);
        if (!dryRun && stats.missing == 0 && stats.bad == 0) {
            println("REPORT: Save succeeded");
        }
        if (stats.missing != 0 || stats.bad != 0) {
            throw new IllegalStateException("Wave541 apply failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
