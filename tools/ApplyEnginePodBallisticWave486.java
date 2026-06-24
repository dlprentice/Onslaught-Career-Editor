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

public class ApplyEnginePodBallisticWave486 extends GhidraScript {
    private static class Spec {
        final String address;
        final String oldName;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] parameters;
        final String comment;
        final String[] tags;

        Spec(
                String address,
                String oldName,
                String name,
                String callingConvention,
                DataType returnType,
                ParameterImpl[] parameters,
                String comment,
                String[] tags) {
            this.address = address;
            this.oldName = oldName;
            this.name = name;
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
            "engine-pod-ballistic-wave486",
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
            if (!fn.getName().equals(spec.oldName) && !fn.getName().equals(spec.name)) {
                throw new IllegalStateException("Unexpected function name at " + spec.address + ": " + fn.getName());
            }

            boolean needsRename = !fn.getName().equals(spec.name);
            if (dryRun) {
                println("DRY: " + spec.address + " " + fn.getName() + " -> " + expectedSignature(spec));
                if (needsRename) {
                    stats.wouldRename++;
                }
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
            String expectedSignature = expectedSignature(spec);
            if (!actualSignature.equals(expectedSignature)) {
                throw new IllegalStateException(
                    "Read-back signature mismatch at " + spec.address + ": " + actualSignature + " != " + expectedSignature
                );
            }
            if (!spec.comment.equals(readBack.getComment())) {
                throw new IllegalStateException("Read-back comment mismatch at " + spec.address);
            }
            Set<String> actualTags = tagNames(readBack);
            for (String tag : spec.tags) {
                if (!actualTags.contains(tag)) {
                    throw new IllegalStateException("Read-back missing tag at " + spec.address + ": " + tag);
                }
            }

            stats.updated++;
            println("OK: " + spec.address + " " + readBack.getName() + " -> " + actualSignature);
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
        DataType voidPtr = new PointerDataType(voidType);
        DataType intType = IntegerDataType.dataType;
        DataType floatType = FloatDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x004d3020",
                "CEngine__SetOptionValueAndNotifyTarget",
                "CEngine__SetOptionValueAndNotifyTarget",
                "__thiscall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr), param("option_value", intType)},
                "Wave486 signature/comment hardening: instruction read-back shows one stack argument and RET 0x4, correcting the stale extra float parameter. The helper stores option_value at this+0x20, mirrors it through the this+0x2c-indexed global dword array at 0x00662ab0, notifies the optional target pointer at this+0x1c through vfunc +0xe0 with the inverse of (option_value == 1) and vfunc +0x154 with (option_value == 1), then increments this+0x3c when option_value is nonzero. Xrefs include CGame, CGameInterface, CPauseMenu, and raw no-function callers 0x004d113a/0x004d114a that pass 0/1 in the god/options path. Exact owner/source identity, target vfunc identities, concrete layout, runtime behavior, and rebuild parity remain unproven.",
                tags("engine-option", "god-mode-adjacent", "signature-corrected", "comment-hardened")
            ),
            new Spec(
                "0x004d3630",
                "CEngine__AdvanceAndAccumulateMotionScalar",
                "CPod__VFunc_66_UpdateMotionAndAccumulateScalar",
                "__fastcall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave486 owner/signature/comment correction: CPOD RTTI resolves vtable 0x005dff8c, whose slot 66 at 0x005e0094 points here; this supersedes the stale CEngine owner label. The body calls CUnit__UpdateMotionAttachmentsAndEffects(this), dispatches this vfunc +0xb4, and accumulates the returned float into this+0x84. CPod source/body text is absent from the current Stuart source snapshot; exact slot contract, scalar meaning, concrete layout, runtime motion behavior, and rebuild parity remain unproven.",
                tags("cpod", "vfunc-slot-66", "motion", "renamed", "signature-corrected", "comment-hardened", "vtable-readback")
            ),
            new Spec(
                "0x004d36c0",
                "CUnit__InitBallisticAimState",
                "CUnit__InitBallisticAimState",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("target_x", floatType),
                    param("target_y", floatType),
                    param("target_z", floatType),
                    param("target_w", floatType)
                },
                "Wave486 signature/comment hardening: instruction read-back shows ECX as this, four stack dwords/floats, and RET 0x10. If this+0x254 is zero, the helper copies the target vector into this+0x258..0x264, samples height through CStaticShadows__SampleShadowHeightBilinear(&DAT_006fadc8, target_vector), overwrites this+0x260 with the sampled height, calls CUnit__ComputeBallisticLaunchVelocity(this), then sets this+0x254=1 and this+0x250=0. Raw no-function caller 0x005344f0 passes a 4-dword vector copied from a vfunc +0x44 result. Exact ballistic-state layout, source identity, runtime aim behavior, and rebuild parity remain unproven.",
                tags("cunit", "ballistic", "signature-corrected", "comment-hardened", "raw-caller-readback")
            ),
            new Spec(
                "0x004d3730",
                "CUnit__ComputeBallisticLaunchVelocity",
                "CUnit__ComputeBallisticLaunchVelocity",
                "__fastcall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave486 signature/comment hardening: ECX is the unit pointer and the only explicit parameter. The body computes yaw from target position this+0x258/0x25c minus current position this+0x1c/0x20, compares target height this+0x260 against current height this+0x24, reads a unit-data speed-like field at this+0x164+0xb4 scaled by global 0x005d8584, dispatches this vfunc +0xb4, scans launch angles from global 0x005d85c8 in steps of 0x005d8cb8, chooses the angle with the smallest horizontal-distance error, builds an orientation matrix through CSquadNormal__BuildOrientationMatrixFromEuler, and writes the scaled launch vector into this+0x7c/0x80/0x84 plus this+0x88. Exact constants, ballistic-state layout, runtime projectile/aim behavior, and rebuild parity remain unproven.",
                tags("cunit", "ballistic", "signature-corrected", "comment-hardened")
            )
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }

        println("--- SUMMARY ---");
        println(
            "updated=" + stats.updated +
            " skipped=" + stats.skipped +
            " created=0 would_create=0 renamed=" + stats.renamed +
            " would_rename=" + stats.wouldRename +
            " missing=" + stats.missing +
            " bad=" + stats.bad
        );
        if (stats.bad > 0 || stats.missing > 0) {
            throw new IllegalStateException("ApplyEnginePodBallisticWave486 failed; see log");
        }
    }
}
