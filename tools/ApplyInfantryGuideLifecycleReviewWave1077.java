//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
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

public class ApplyInfantryGuideLifecycleReviewWave1077 extends GhidraScript {
    private static final String WAVE_TAG = "infantryguide-lifecycle-review-wave1077";

    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] parameters;
        final String nextAddress;
        final String comment;
        final String[] tags;

        Spec(String address, String name, String callingConvention, DataType returnType,
                ParameterImpl[] parameters, String nextAddress, String comment, String[] tags) {
            this.address = address;
            this.name = name;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.parameters = parameters;
            this.nextAddress = nextAddress;
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
        int commentUpdated = 0;
        int tagUpdated = 0;
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

    private DataType voidPtr() {
        return new PointerDataType(VoidDataType.dataType);
    }

    private ParameterImpl param(String name, DataType dataType) throws Exception {
        return new ParameterImpl(name, dataType, currentProgram);
    }

    private Function functionAtEntry(Address address) {
        Function fn = getFunctionAt(address);
        if (fn != null) {
            return fn;
        }
        Function containing = getFunctionContaining(address);
        if (containing != null && containing.getEntryPoint().equals(address)) {
            return containing;
        }
        return null;
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

    private boolean needsUpdate(Function fn, Spec spec) {
        if (!fn.getName().equals(spec.name)) {
            return true;
        }
        if (!signatureMatches(fn, spec)) {
            return true;
        }
        if (fn.getComment() == null || !fn.getComment().equals(spec.comment)) {
            return true;
        }
        return !hasAllTags(fn, spec);
    }

    private void applySignature(Function fn, Spec spec) throws Exception {
        fn.setCallingConvention(spec.callingConvention);
        fn.setReturnType(spec.returnType, SourceType.USER_DEFINED);
        fn.replaceParameters(FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS, true,
            SourceType.USER_DEFINED, spec.parameters);
    }

    private Function getOrCreate(Spec spec, boolean dryRun, Stats stats) throws Exception {
        Address address = addr(spec.address);
        Function fn = functionAtEntry(address);
        if (fn != null) {
            return fn;
        }
        Function containing = getFunctionContaining(address);
        if (containing != null) {
            throw new IllegalStateException("Address is inside existing function "
                + containing.getName() + " at " + containing.getEntryPoint());
        }
        if (dryRun) {
            stats.wouldCreate++;
            println("DRY_CREATE: " + spec.address + " -> " + expectedSignature(spec));
            return null;
        }

        boolean disasmOk = disassemble(address);
        Function created = createFunction(address, spec.name);
        if (created == null) {
            throw new IllegalStateException("createFunction returned null at " + spec.address
                + " (disassemble=" + disasmOk + ")");
        }
        stats.created++;
        return created;
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
            throw new IllegalStateException("Read-back signature mismatch at " + spec.address
                + ": expected " + expectedSignature(spec) + " got " + fn.getSignature());
        }
        if (fn.getComment() == null || !fn.getComment().equals(spec.comment)) {
            throw new IllegalStateException("Read-back comment mismatch at " + spec.address);
        }
        if (!hasAllTags(fn, spec)) {
            throw new IllegalStateException("Read-back tag mismatch at " + spec.address);
        }
        if (fn.getBody().contains(addr(spec.nextAddress))) {
            throw new IllegalStateException("Read-back body for " + spec.address
                + " unexpectedly absorbed next address " + spec.nextAddress);
        }
    }

    private void applySpec(Spec spec, boolean dryRun, Stats stats) {
        try {
            Function fn = getOrCreate(spec, dryRun, stats);
            if (fn == null) {
                stats.signatureUpdated++;
                stats.commentUpdated++;
                stats.tagUpdated++;
                stats.updated++;
                return;
            }

            boolean renameNeeded = !fn.getName().equals(spec.name);
            boolean signatureNeedsUpdate = !signatureMatches(fn, spec);
            boolean commentNeedsUpdate = fn.getComment() == null || !fn.getComment().equals(spec.comment);
            boolean tagsNeedUpdate = !hasAllTags(fn, spec);

            if (!needsUpdate(fn, spec)) {
                stats.skipped++;
                println("SKIP: " + spec.address + " " + spec.name);
                return;
            }
            if (dryRun) {
                stats.skipped++;
                if (renameNeeded) {
                    stats.wouldRename++;
                }
                if (signatureNeedsUpdate) {
                    stats.signatureUpdated++;
                }
                if (commentNeedsUpdate) {
                    stats.commentUpdated++;
                }
                if (tagsNeedUpdate) {
                    stats.tagUpdated++;
                }
                println("DRY: " + spec.address + " actual=" + fn.getSignature()
                    + " expected=" + expectedSignature(spec));
                return;
            }

            if (renameNeeded) {
                fn.setName(spec.name, SourceType.USER_DEFINED);
                stats.renamed++;
            }
            if (signatureNeedsUpdate) {
                applySignature(fn, spec);
                stats.signatureUpdated++;
            }
            if (commentNeedsUpdate) {
                fn.setComment(spec.comment);
                stats.commentUpdated++;
            }
            if (tagsNeedUpdate) {
                Set<String> existingTags = tagNames(fn);
                for (String tag : spec.tags) {
                    if (!existingTags.contains(tag)) {
                        fn.addTag(tag);
                    }
                }
                stats.tagUpdated++;
            }
            verifyReadBack(spec);
            stats.updated++;
            println("OK: " + spec.address + " " + spec.name + " :: " + expectedSignature(spec));
            Thread.sleep(75L);
        }
        catch (Exception ex) {
            stats.bad++;
            println("FAIL: " + spec.address + " " + spec.name + " :: " + ex.getMessage());
        }
    }

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            WAVE_TAG,
            "wave1077-readback-verified",
            "retail-binary-evidence",
            "function-boundary-recovered",
            "guide-shared-vtable",
            "vtable-slot",
            "signature-hardened",
            "comment-hardened"
        };
        String[] result = new String[common.length + extras.length];
        System.arraycopy(common, 0, result, 0, common.length);
        System.arraycopy(extras, 0, result, common.length, extras.length);
        return result;
    }

    private String comment(String slot, String slotAddrs, String body) {
        return "Wave1077 boundary recovery: CInfantryGuide vtable 0x005dbfa8 and/or " +
            "CGroundVehicleGuide vtable 0x005dbd90 DATA-xref this previously missing " +
            "guide-family slot " + slot + " body at slot address(es) " + slotAddrs + ". " +
            body + " Static retail Ghidra vtable/instruction/xref evidence only; exact " +
            "source method name, concrete guide/vector/layout semantics, runtime targeting " +
            "or movement behavior, BEA patching, gameplay outcomes, and rebuild parity " +
            "remain separate proof.";
    }

    private Spec[] specs() throws Exception {
        DataType voidPtr = voidPtr();
        DataType intType = IntegerDataType.dataType;
        return new Spec[] {
            new Spec(
                "0x0047d750",
                "CGroundVehicleGuide__VFunc03_UpdateGuidanceState_0047d750",
                "__fastcall",
                VoidDataType.dataType,
                new ParameterImpl[] { param("this", voidPtr) },
                "0x0047e290",
                comment("3", "0x005dbd9c",
                    "The body uses ECX as the guide object, owner pointer at this+0x18, " +
                    "tests owner flag byte +0x2c bit 0x4 for an early owner-vtable dispatch, " +
                    "then runs a large guidance/vector/pathing update body before the adjacent " +
                    "0x0047e290 CGuide__ctor_base entry. "),
                tags("cgroundvehicleguide", "slot3", "guidance-update")
            ),
            new Spec(
                "0x0047e2d0",
                "SharedGuide__VFunc04_SetVectorMode1_0047e2d0",
                "__thiscall",
                VoidDataType.dataType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("lane0_raw", intType),
                    param("lane1_raw", intType),
                    param("lane2_raw", intType),
                    param("lane3_raw", intType),
                    param("mode_gate", intType)
                },
                "0x0047e310",
                comment("4", "0x005dbfb8 and 0x005dbda0",
                    "The compact RET 0x14 body conditionally sets this+0x1c to mode 1, " +
                    "copies four raw vector lanes into the this+0x8 block, and can suppress " +
                    "the state write based on owner+0x13c/+0x20. "),
                tags("shared-guide-slot4", "vector-state")
            ),
            new Spec(
                "0x0047e310",
                "SharedGuide__VFunc05_SetVectorMode2_0047e310",
                "__thiscall",
                VoidDataType.dataType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("lane0_raw", intType),
                    param("lane1_raw", intType),
                    param("lane2_raw", intType),
                    param("lane3_raw", intType)
                },
                "0x0047e340",
                comment("5", "0x005dbfbc and 0x005dbda4",
                    "The compact RET 0x10 body sets this+0x1c to mode 2 and copies four " +
                    "raw vector lanes into the this+0x8 block. "),
                tags("shared-guide-slot5", "vector-state")
            ),
            new Spec(
                "0x0047e340",
                "SharedGuide__VFunc06_SetVectorMode3_0047e340",
                "__thiscall",
                VoidDataType.dataType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("lane0_raw", intType),
                    param("lane1_raw", intType),
                    param("lane2_raw", intType),
                    param("lane3_raw", intType)
                },
                "0x0047e370",
                comment("6", "0x005dbfc0 and 0x005dbda8",
                    "The compact RET 0x10 body sets this+0x1c to mode 3 and copies four " +
                    "raw vector lanes into the this+0x8 block. "),
                tags("shared-guide-slot6", "vector-state")
            ),
            new Spec(
                "0x0047e370",
                "SharedGuide__VFunc07_SetVectorModeFromOwnerState_0047e370",
                "__thiscall",
                VoidDataType.dataType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("lane0_raw", intType),
                    param("lane1_raw", intType),
                    param("lane2_raw", intType),
                    param("lane3_raw", intType)
                },
                "0x0047e3d0",
                comment("7", "0x005dbfc4 and 0x005dbdac",
                    "The RET 0x10 body checks owner+0x13c/+0x20 and owner+0x140/+0x94, " +
                    "selects state 0 or 3 at this+0x1c, then copies four raw vector lanes " +
                    "into the this+0x8 block. "),
                tags("shared-guide-slot7", "vector-state", "owner-state")
            ),
            new Spec(
                "0x0047e3d0",
                "SharedGuide__VFunc08_ResetVectorsFromOwner_0047e3d0",
                "__fastcall",
                VoidDataType.dataType,
                new ParameterImpl[] { param("this", voidPtr) },
                "0x0047e440",
                comment("8", "0x005dbfc8 and 0x005dbdb0",
                    "The RET body sets this+0x1c to 0, copies four owner lanes from " +
                    "owner+0x1c into the this+0x8 block, and clears the owner+0x14c vector " +
                    "block through stack-local zero lanes. "),
                tags("shared-guide-slot8", "vector-reset", "owner-vector")
            )
        };
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");
        println("Mode: " + (dryRun ? "dry" : "apply"));

        Stats stats = new Stats();
        for (Spec spec : specs()) {
            applySpec(spec, dryRun, stats);
        }

        println("--- SUMMARY ---");
        println("updated=" + stats.updated +
            " skipped=" + stats.skipped +
            " created=" + stats.created +
            " would_create=" + stats.wouldCreate +
            " renamed=" + stats.renamed +
            " would_rename=" + stats.wouldRename +
            " signature_updated=" + stats.signatureUpdated +
            " comment_updated=" + stats.commentUpdated +
            " tag_updated=" + stats.tagUpdated +
            " missing=" + stats.missing +
            " bad=" + stats.bad);
    }
}
