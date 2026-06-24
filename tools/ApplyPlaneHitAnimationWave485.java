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
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyPlaneHitAnimationWave485 extends GhidraScript {
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
            "plane-wave485",
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

        Spec[] specs = new Spec[] {
            new Spec(
                "0x004d1f10",
                "CUnitAI__Hit_CheckFatalDamageAndDie",
                "CPlane__Hit_CheckFatalDamageAndDie",
                "__thiscall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr), param("hit_thing", voidPtr), param("hit_context", voidPtr)},
                "Wave485 owner/signature/comment correction: CPlane vtable 0x005e1930 slot 39 points here, while CDiveBomber, CGroundAttackAircraft, and CBomber use different slot-39 hit handlers. The body gates on this+0x164->0x11c, hit_thing+0x34 flags, and the +0x138 ownership/team comparison; when the fatal plane-specific path is selected it may call hit_thing vfunc +0x194, calls CExplosionInitThing__ctor_like_004fd230, dispatches this vfunc +0x38, then always tails to CThing__Hit_TriggerDieOnUnitOrTypeMask02100000(this, hit_thing, hit_context). Plane.cpp/CPlane source body is absent from the current Stuart source snapshot; exact layout, runtime hit/death behavior, and rebuild parity remain unproven.",
                tags("cplane", "hit", "damage", "vtable-readback", "renamed", "signature-corrected", "comment-hardened")
            ),
            new Spec(
                "0x004d1f90",
                "CExplosionInitThing__PlayWingOpenAnimationOnce",
                "CPlane__PlayWingOpenAnimationOnce",
                "__fastcall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave485 owner/signature/comment correction: raw caller instruction context passes [ESI+0x8] in ECX and the helper updates CPlane launch/wing animation state field this+0x27c from 1 to 2. The body selects string wingopen at 0x00624420, calls the mesh vfunc +0x24 with (wingopen, 1, 0), resolves the animation through CMesh__FindAnimationIndexByName, and dispatches this vfunc +0xf0 with that animation index. Plane.cpp/CPlane source body is absent from the current Stuart source snapshot; exact animation-state layout, runtime animation behavior, and rebuild parity remain unproven.",
                tags("cplane", "animation", "wing-open", "renamed", "signature-corrected", "comment-hardened")
            ),
            new Spec(
                "0x004d1fd0",
                "CExplosionInitThing__PlayWingCloseAnimationOnce",
                "CPlane__PlayWingCloseAnimationOnce",
                "__fastcall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave485 owner/signature/comment correction: raw caller instruction context passes [ESI+0x8] in ECX and the helper updates CPlane launch/wing animation state field this+0x27c from 4 to 3. The body selects string wingclose at 0x0062442c, calls the mesh vfunc +0x24 with (wingclose, 1, 0), resolves the animation through CMesh__FindAnimationIndexByName, and dispatches this vfunc +0xf0 with that animation index. Plane.cpp/CPlane source body is absent from the current Stuart source snapshot; exact animation-state layout, runtime animation behavior, and rebuild parity remain unproven.",
                tags("cplane", "animation", "wing-close", "renamed", "signature-corrected", "comment-hardened")
            ),
            new Spec(
                "0x004d2010",
                "CExplosionInitThing__UpdateAttackLaunchAnimationState",
                "CPlane__UpdateAttackLaunchAnimationState",
                "__fastcall",
                intType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave485 owner/signature/comment correction: CPlane vtable 0x005e1930 slot 59 points here, while CDiveBomber, CGroundAttackAircraft, and CBomber use different slot-59 animation handlers. The body checks the linked object at this+0x8 through vfunc +0x58, then advances this+0x27c from 2 to 4 by playing attack string 0x00624438 or from 3 to 1 by playing launch string 0x006243f8; both paths use mesh vfunc +0x24, CMesh__FindAnimationIndexByName, and this vfunc +0xf0, and the function returns 0. Plane.cpp/CPlane source body is absent from the current Stuart source snapshot; exact animation-state layout, runtime animation behavior, and rebuild parity remain unproven.",
                tags("cplane", "animation", "attack-launch", "vtable-readback", "renamed", "signature-corrected", "comment-hardened")
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
            throw new IllegalStateException("ApplyPlaneHitAnimationWave485 failed; see log");
        }
    }
}
