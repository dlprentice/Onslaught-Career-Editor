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

public class ApplyCThingWaypointResidualVtableBoundaryWave1081 extends GhidraScript {
    private static final String WAVE_TAG = "cthing-waypoint-residual-vtable-boundary-wave1081";

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

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            WAVE_TAG,
            "wave1081-readback-verified",
            "retail-binary-evidence",
            "function-boundary-recovered",
            "signature-hardened",
            "comment-hardened",
            "vtable-slot",
            "thing-family"
        };
        String[] result = new String[common.length + extras.length];
        System.arraycopy(common, 0, result, 0, common.length);
        System.arraycopy(extras, 0, result, common.length, extras.length);
        return result;
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");
        println("ApplyCThingWaypointResidualVtableBoundaryWave1081 mode=" + (dryRun ? "dry" : "apply"));

        DataType intType = IntegerDataType.dataType;
        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);

        Spec[] specs = new Spec[] {
            new Spec(
                "0x004bfa00",
                "SharedVFunc__CopyGlobal829dd0Block30ToOut_004bfa00",
                "__thiscall",
                voidType,
                new ParameterImpl[] { param("this", voidPtr), param("out_block30", voidPtr) },
                new String[] { "0x004bfa20" },
                "Wave1081 CThing/CWaypoint residual vtable-boundary recovery: CThing vtable 0x005df550 slot +0x04 and CWaypoint vtable 0x005dd278 slot +0x04 point at this previously functionless RET 0x4 output-copy body. The body copies 0x30 bytes from global block 0x00829dd0 into the caller output buffer. Static retail Ghidra vtable/xref/listing evidence only; exact source virtual name, concrete global/block identity, runtime behavior, BEA patching, and rebuild parity remain separate proof.",
                tags("shared-vfunc", "block-copy", "output-buffer", "cthing", "cwaypoint")
            ),
            new Spec(
                "0x004bfa20",
                "SharedVFunc__CopyGlobal829dd0Block30ToOut_004bfa20",
                "__thiscall",
                voidType,
                new ParameterImpl[] { param("this", voidPtr), param("out_block30", voidPtr) },
                new String[] { "0x004bfa40" },
                "Wave1081 CThing/CWaypoint residual vtable-boundary recovery: CThing vtable 0x005df550 slot +0x88 and CWaypoint vtable 0x005dd278 slot +0x88 point at this previously functionless RET 0x4 output-copy body adjacent to CThing__GetRenderPos. The body copies 0x30 bytes from global block 0x00829dd0 into the caller output buffer; Stuart-source CThing defaults around this slot include ID_FMATRIX-style orientation returns, but this saved name stays behavior-based. Static retail Ghidra vtable/xref/listing plus source-shape evidence only; exact source virtual name, concrete global/block identity, runtime behavior, BEA patching, and rebuild parity remain separate proof.",
                tags("shared-vfunc", "block-copy", "output-buffer", "cthing", "cwaypoint", "source-shape")
            ),
            new Spec(
                "0x004bfa40",
                "SharedVFunc__CopyGlobal829dd0Block30ToOut_004bfa40",
                "__thiscall",
                voidType,
                new ParameterImpl[] { param("this", voidPtr), param("out_block30", voidPtr) },
                new String[] { "0x004bfa60" },
                "Wave1081 CThing/CWaypoint residual vtable-boundary recovery: CThing vtable 0x005df550 slot +0xf4 and CWaypoint vtable 0x005dd278 slot +0xf4 point at this previously functionless RET 0x4 output-copy body before OID__InitTargetData. The body copies 0x30 bytes from global block 0x00829dd0 into the caller output buffer; Stuart-source CThing defaults around this area include sound/render orientation-style ID_FMATRIX returns, but this saved name stays behavior-based. Static retail Ghidra vtable/xref/listing plus source-shape evidence only; exact source virtual name, concrete global/block identity, runtime behavior, BEA patching, and rebuild parity remain separate proof.",
                tags("shared-vfunc", "block-copy", "output-buffer", "cthing", "cwaypoint", "source-shape")
            ),
            new Spec(
                "0x004f3760",
                "CThing__AddShutdownEvent_004f3760",
                "__thiscall",
                voidType,
                new ParameterImpl[] { param("this", voidPtr) },
                new String[] { "0x004f37a0" },
                "Wave1081 CThing/CWaypoint residual vtable-boundary recovery: CThing vtable 0x005df550 slot +0xb0 and CWaypoint vtable 0x005dd278 slot +0xb0 point at this previously functionless flag/event helper. The body tests this+0x2c bit 0x1, sets it when clear, and calls the event-manager style helper at 0x0044b370 with event id 0x7d0; this matches Stuart-source CThing::AddShutdownEvent shape for TF_DECLARED_SHUTDOWN and SHUTDOWN=2000. Static retail Ghidra vtable/xref/listing plus source-shape evidence only; runtime event delivery, exact layout identity, BEA patching, and rebuild parity remain separate proof.",
                tags("cthing", "cwaypoint", "source-shape", "shutdown-event", "flag-setter")
            ),
            new Spec(
                "0x004f37a0",
                "CThing__StartDieProcess_004f37a0",
                "__thiscall",
                intType,
                new ParameterImpl[] { param("this", voidPtr) },
                new String[] { "0x004f37c0" },
                "Wave1081 CThing/CWaypoint residual vtable-boundary recovery: CThing vtable 0x005df550 slot +0x140 and CWaypoint vtable 0x005dd278 slot +0x140 point at this previously functionless boolean flag helper. The body tests this+0x2c bit 0x4, sets it when clear, calls the same object's vtable slot +0x38, returns 1 on first transition, and returns 0 if already set; this matches Stuart-source CThing::StartDieProcess shape for TF_DYING followed by AddShutdownEvent. Static retail Ghidra vtable/xref/listing plus source-shape evidence only; runtime death-process behavior, exact layout identity, BEA patching, and rebuild parity remain separate proof.",
                tags("cthing", "cwaypoint", "source-shape", "die-process", "flag-setter")
            ),
            new Spec(
                "0x004f3d20",
                "SharedVFunc__ForwardField28Slot10OrNull_004f3d20",
                "__thiscall",
                voidPtr,
                new ParameterImpl[] { param("this", voidPtr) },
                new String[] { "0x004f3d30" },
                "Wave1081 CThing-family residual vtable-boundary recovery: broad CThing-family DATA refs, including CThing/CWaypoint slot +0x54 and CInfantryAI table 0x005dbf14 slot +0x118, point at this previously functionless field-forwarding body. The body loads this+0x28, jumps through that object's vtable slot +0x10 when non-null, and returns null otherwise. Static retail Ghidra vtable/xref/listing evidence only; exact field identity, source virtual name, runtime behavior, BEA patching, and rebuild parity remain separate proof.",
                tags("shared-vfunc", "field-forwarder", "cthing", "cwaypoint", "cinfantryai")
            ),
            new Spec(
                "0x0043e9c0",
                "SharedVFunc__CopyGlobal0066ea10Block10ToOut_0043e9c0",
                "__thiscall",
                voidType,
                new ParameterImpl[] { param("this", voidPtr), param("out_block10", voidPtr) },
                new String[] { "0x0043e9f0" },
                "Wave1081 CThing/CWaypoint residual vtable-boundary recovery: CThing vtable 0x005df550 slot +0xe4 and CWaypoint vtable 0x005dd278 slot +0xe4, with broader CThing-family DATA refs, point at this previously functionless RET 0x4 output-copy body. The body copies four dwords from global block 0x0066ea10 through 0x0066ea1c into the caller output buffer and stops before CThing__GetRenderPos. Static retail Ghidra vtable/xref/listing evidence only; exact source virtual name, concrete global/block identity, runtime behavior, BEA patching, and rebuild parity remain separate proof.",
                tags("shared-vfunc", "block-copy", "output-buffer", "cthing", "cwaypoint")
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
            throw new IllegalStateException("Wave1081 CThing/Waypoint residual vtable-boundary recovery encountered bad rows");
        }
    }
}
