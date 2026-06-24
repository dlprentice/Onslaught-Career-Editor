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

public class ApplySignatureDebtWave789 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] params;
        final String comment;
        final String[] tags;

        Spec(String address, String name, String callingConvention, DataType returnType,
                ParameterImpl[] params, String comment, String[] tags) {
            this.address = address;
            this.name = name;
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
        int signatureUpdated = 0;
        int commentOnlyUpdated = 0;
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

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "signature-debt-wave789",
            "wave789-readback-verified",
            "retail-binary-evidence",
            "signature-hardened",
            "param-name-hardened"
        };
        String[] all = new String[common.length + extras.length];
        System.arraycopy(common, 0, all, 0, common.length);
        System.arraycopy(extras, 0, all, common.length, extras.length);
        return all;
    }

    private Set<String> tagNames(Function fn) {
        Set<String> names = new HashSet<>();
        for (FunctionTag tag : fn.getTags()) {
            names.add(tag.getName());
        }
        return names;
    }

    private String expectedSignature(Spec spec) {
        StringBuilder sb = new StringBuilder();
        sb.append(spec.returnType.getDisplayName())
            .append(" ")
            .append(spec.callingConvention)
            .append(" ")
            .append(spec.name)
            .append("(");
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

    private void verifyReadBack(Spec spec) {
        Function fn = functionAtEntry(spec.address);
        if (fn == null) {
            throw new IllegalStateException("Read-back missing function at " + spec.address);
        }
        if (!fn.getName().equals(spec.name)) {
            throw new IllegalStateException("Read-back name mismatch at " + spec.address + ": " + fn.getName());
        }
        String signature = fn.getSignature().toString();
        if (!signature.equals(expectedSignature(spec))) {
            throw new IllegalStateException("Read-back signature mismatch at " + spec.address + ": " + signature);
        }
        if (fn.getComment() == null || !fn.getComment().equals(spec.comment)) {
            throw new IllegalStateException("Read-back comment mismatch at " + spec.address);
        }
        Set<String> actualTags = tagNames(fn);
        for (String tag : spec.tags) {
            if (!actualTags.contains(tag)) {
                throw new IllegalStateException("Read-back missing tag at " + spec.address + ": " + tag);
            }
        }
    }

    private void applySpec(Spec spec, boolean dryRun, Stats stats) {
        try {
            Function fn = functionAtEntry(spec.address);
            if (fn == null) {
                println("MISSING: " + spec.address + " " + spec.name);
                stats.missing++;
                return;
            }
            if (!fn.getName().equals(spec.name)) {
                println("BADNAME: " + spec.address + " expected=" + spec.name + " actual=" + fn.getName());
                stats.bad++;
                return;
            }

            String signature = fn.getSignature().toString();
            boolean signatureNeedsUpdate = !signature.equals(expectedSignature(spec));
            boolean commentNeedsUpdate = fn.getComment() == null || !fn.getComment().equals(spec.comment);
            Set<String> actualTags = tagNames(fn);
            boolean tagsNeedUpdate = false;
            for (String tag : spec.tags) {
                if (!actualTags.contains(tag)) {
                    tagsNeedUpdate = true;
                    break;
                }
            }

            if (!signatureNeedsUpdate && !commentNeedsUpdate && !tagsNeedUpdate) {
                println("SKIP: " + spec.address + " " + spec.name);
                stats.skipped++;
                return;
            }

            if (dryRun) {
                println("DRY: " + spec.address + " " + spec.name + " signature=" + signature + " -> " + expectedSignature(spec));
                if (signatureNeedsUpdate) {
                    stats.signatureUpdated++;
                } else {
                    stats.commentOnlyUpdated++;
                }
                stats.skipped++;
                return;
            }

            fn.setCallingConvention(spec.callingConvention);
            fn.setReturnType(spec.returnType, SourceType.USER_DEFINED);
            fn.replaceParameters(
                FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS,
                true,
                SourceType.USER_DEFINED,
                spec.params
            );
            fn.setComment(spec.comment);
            for (String tag : spec.tags) {
                fn.addTag(tag);
            }
            verifyReadBack(spec);
            println("OK: " + spec.address + " " + spec.name + " signature=" + expectedSignature(spec));
            if (signatureNeedsUpdate) {
                stats.signatureUpdated++;
            } else {
                stats.commentOnlyUpdated++;
            }
            stats.updated++;
            Thread.sleep(50L);
        } catch (Exception ex) {
            println("FAIL: " + spec.address + " " + spec.name + " " + ex.getMessage());
            stats.bad++;
        }
    }

    @Override
    protected void run() throws Exception {
        boolean dryRun = isDryRun(getScriptArgs().length > 0 ? getScriptArgs()[0] : "dry");
        println("ApplySignatureDebtWave789 mode=" + (dryRun ? "dry" : "apply"));

        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);
        DataType intType = IntegerDataType.dataType;
        DataType floatType = FloatDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x00410c50",
                "CMonitor__UpdateMovementTransitionAndEffects",
                "__fastcall",
                voidType,
                new ParameterImpl[] { param("monitor", voidPtr) },
                "Source-aligned owner/behavior correction without source-exact Monitor method identity. Evidence: only checked caller is CMonitor__Process; body updates tracked render pairs, movement/terrain integration, transition timers, impact effects, and hostile-environment penalty through CMonitor__UpdateTrackedRenderPair, CMonitor__IntegrateMovementAgainstTerrain, CMonitor__ComputeTerrainVelocityScalar, CMonitor__SpawnGroundOrAirImpactEffect, and CMonitor__ApplyHostileEnvironmentPenalty. Wave789 signature-debt hardening names the ECX/fastcall object parameter monitor from the sole CMonitor__Process caller and the repeated monitor-field decompile use. Static retail evidence only; exact source method identity, concrete CMonitor layout, runtime behavior, and rebuild parity remain unproven.",
                tags("monitor", "movement-transition", "param-name")
            ),
            new Spec(
                "0x00412ad0",
                "CMonitor__UpdateSurfaceAlignmentAngle",
                "__fastcall",
                voidType,
                new ParameterImpl[] { param("monitor", voidPtr) },
                "Monitor surface-alignment angle update helper. Copies the linked transform basis, samples the linked object's orientation callback, chooses the smaller ABS-derived turn component, updates monitor+0x24, and wraps the angle through the pi/two-pi constants. Wave789 signature-debt hardening names the ECX/fastcall object parameter monitor from the CBattleEngineWalkerPart__Move caller and monitor field accesses at +0x20/+0x24/+0x28. Static retail evidence only; exact source method identity, concrete type layout, runtime behavior, and rebuild parity remain unproven.",
                tags("monitor", "surface-alignment", "param-name")
            ),
            new Spec(
                "0x00414b30",
                "TargetSet__AnyUnitTargetTimeoutBeforeProfileLimit",
                "__fastcall",
                intType,
                new ParameterImpl[] { param("target_set", voidPtr) },
                "Behavior-backed rename from weak CVBufTexture wrapper. Evidence: scans a linked target/unit set, calls CUnit__IsTargetTimeoutBeforeProfileLimit on each entry, and is called twice by CBattleEngine__UpdateAutoTargetSetAndFireProjectiles. Wave789 signature-debt hardening names the ECX/fastcall object parameter target_set from the linked-list traversal rooted at param_1. Static retail evidence only; exact source identity, concrete target-set layout, runtime behavior, and rebuild parity remain unproven.",
                tags("target-set", "weapon-fire", "param-name")
            ),
            new Spec(
                "0x00418090",
                "OpeningAnimationStateCallback__StartOpeningIfPending",
                "__fastcall",
                intType,
                new ParameterImpl[] { param("state_record", voidPtr) },
                "Opening-animation state callback semantic rename. Evidence: state field +0x254, timer field +0x25c, s_opening_00623ba4, FindAnimationIndex call, animation start vcall +0xf0, and DATA xref from mixed table slot 0x005d9080. Wave789 signature-debt hardening names the ECX/fastcall object parameter state_record from those state/timer fields while preserving the unresolved table-owner boundary. Static retail evidence only; exact owner, source identity, concrete state layout, runtime behavior, and rebuild parity remain unproven.",
                tags("opening-animation", "callback", "param-name")
            ),
            new Spec(
                "0x004879e0",
                "CHud__RenderOverlayForViewpoint",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("viewpoint", voidPtr),
                    param("viewpoint_index", intType),
                    param("unused_overlay_param", floatType)
                },
                "Wave410 owner/signature correction: per-viewpoint CHud overlay renderer. The body validates viewpoint target/camera context, selects the viewpoint, clips the overlay marker rectangle against window dimensions, stores active target/viewpoint state in CHud fields +0x50/+0x54/+0x58, applies overlay sprite state, and dispatches world-target, target-indicator, controller status, 3D marker, objective, slot-fill, and tactical radar overlay helpers. Wave789 signature-debt hardening names the fourth float unused_overlay_param because the exported decompile shows no body reads of that parameter while viewpoint and viewpoint_index drive the observed overlay state. Static retail evidence only; exact source body identity, concrete CHud layout, runtime HUD overlay behavior, and rebuild parity remain unproven.",
                tags("hud", "overlay", "param-name")
            ),
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }

        println(
            "SUMMARY: updated=" + stats.updated
            + " skipped=" + stats.skipped
            + " renamed=0 would_rename=0"
            + " signature_updated=" + stats.signatureUpdated
            + " comment_only_updated=" + stats.commentOnlyUpdated
            + " missing=" + stats.missing
            + " bad=" + stats.bad
        );
        if (stats.missing != 0 || stats.bad != 0) {
            throw new IllegalStateException("Wave789 apply encountered missing/bad rows");
        }
    }
}
