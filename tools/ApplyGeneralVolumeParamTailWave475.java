//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.CharDataType;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.ShortDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.FunctionTag;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyGeneralVolumeParamTailWave475 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final String comment;
        final String[] tags;
        final ParameterImpl[] parameters;

        Spec(
                String address,
                String name,
                String callingConvention,
                DataType returnType,
                String comment,
                String[] tags,
                ParameterImpl[] parameters) {
            this.address = address;
            this.name = name;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.comment = comment;
            this.tags = tags;
            this.parameters = parameters;
        }
    }

    private static class Stats {
        int updated = 0;
        int skipped = 0;
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
            "generalvolume-param-tail-wave475",
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
            if (!fn.getName().equals(spec.name)) {
                throw new IllegalStateException(
                    "Unexpected function name at " + spec.address + ": " + fn.getName()
                );
            }

            if (dryRun) {
                println("DRY: " + spec.address + " " + fn.getName() + " -> " + expectedSignature(spec));
                stats.skipped++;
                return;
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
        DataType charPtr = new PointerDataType(CharDataType.dataType);
        DataType shortPtr = new PointerDataType(ShortDataType.dataType);

        Spec[] specs = new Spec[] {
            new Spec(
                "0x00411b90",
                "CGeneralVolume__DispatchSelectedBurstPreset",
                "__fastcall",
                voidType,
                "Wave475 signature hardening: ECX is the CGeneralVolume-like list context. The body clears linked owner +0x588, walks the selected index at +0x10 through the current node field +0x8, and spawns the selected entry through ProjectileBurst__SpawnFromPercentBucketFallback when entry +0x9c is enabled. Static retail-binary evidence only; exact source identity, concrete layout, runtime weapon behavior, and rebuild parity remain unproven.",
                tags("general-volume", "mode3-burst", "selected-entry", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("general_volume", voidPtr)
                }
            ),
            new Spec(
                "0x00411bf0",
                "CGeneralVolume__DispatchMode3BurstProgressAndSpawn",
                "__fastcall",
                voidType,
                "Wave475 signature hardening: ECX is the CGeneralVolume-like list context. The body walks the selected entry, gates mode-3 burst progress through entry +0xa4 slot fields and owner ammo/progress fields at +0x52c/+0x544/+0x55c/+0x588, then can spawn through ProjectileBurst__SpawnFromPercentBucketFallback. Static retail-binary evidence only; exact source identity, concrete layout, runtime weapon behavior, and rebuild parity remain unproven.",
                tags("general-volume", "mode3-burst", "progress", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("general_volume", voidPtr)
                }
            ),
            new Spec(
                "0x00412240",
                "CGeneralVolume__GetMode3CurrentEntryRoundedSlotValue",
                "__fastcall",
                intType,
                "Wave475 signature hardening: ECX is the CGeneralVolume-like list context. The body walks to the selected entry, reads entry +0xa4 slot index +0x24, returns zero when owner +0x55c slot state is set, otherwise rounds owner +0x52c slot progress through FISTP. Static retail-binary evidence only; exact source identity, concrete layout, runtime HUD behavior, and rebuild parity remain unproven.",
                tags("general-volume", "mode3-burst", "hud-value", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("general_volume", voidPtr)
                }
            ),
            new Spec(
                "0x00412420",
                "CGeneralVolume__GetMode3CurrentEntryDisplayString",
                "__fastcall",
                shortPtr,
                "Wave475 signature hardening: ECX is the CGeneralVolume-like list context. The body walks to the selected entry and returns CText__GetStringById(g_Text, entry +0xa4 +0x3c), or null when no selected entry is available. Static retail-binary evidence only; exact source identity, text table meaning, concrete layout, runtime HUD behavior, and rebuild parity remain unproven.",
                tags("general-volume", "mode3-burst", "hud-string", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("general_volume", voidPtr)
                }
            ),
            new Spec(
                "0x00412830",
                "CGeneralVolume__DisableLinkedEntriesByNameAndReselect",
                "__thiscall",
                voidType,
                "Wave475 signature correction: RET 0x4 proves one stack argument. The body compares entry_name byte-by-byte against each linked entry-name pointer at entry +0xa4, clears entry +0x9c on matches, and calls the reselect/change-weapon helper at 0x00411e70 when the disabled entry was selected. Static retail-binary evidence only; exact helper identity, source identity, concrete layout, runtime selected-weapon behavior, and rebuild parity remain unproven.",
                tags("general-volume", "entry-selection", "string-compare", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("entry_name", charPtr)
                }
            ),
            new Spec(
                "0x00413660",
                "CGeneralVolume__ApplyYawInputByWeaponClass",
                "__thiscall",
                voidType,
                "Wave475 signature correction: RET 0x4 and caller 0x004d337b prove one stack argument. The body reads the BattleEngine-like owner at this +0x20, applies a weapon-class multiplier for table tokens 0xb/0xc, scales axis_input by owner +0x4b0 +0x18, DAT_005d8cd8, and CGeneralVolume__ToDoubleIdentity(owner +0x2c8), then subtracts into owner yaw field +0x278. Static retail-binary evidence only; exact source identity, concrete layout, runtime control behavior, and rebuild parity remain unproven.",
                tags("general-volume", "axis-input", "yaw", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("axis_input", intType)
                }
            ),
            new Spec(
                "0x004136e0",
                "CGeneralVolume__ApplyPitchInputByWeaponClass",
                "__thiscall",
                voidType,
                "Wave475 signature correction: RET 0x4 and caller 0x004d3390 prove one stack argument. The body reads the BattleEngine-like owner at this +0x20, applies a weapon-class multiplier for table tokens 0xb/0xc, scales axis_input by DAT_005d8c90 and CGeneralVolume__ToDoubleIdentity(owner +0x2c8), then subtracts into owner pitch field +0x280. Static retail-binary evidence only; exact source identity, concrete layout, runtime control behavior, and rebuild parity remain unproven.",
                tags("general-volume", "axis-input", "pitch", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("axis_input", intType)
                }
            )
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
            "updated=" + stats.updated +
            " skipped=" + stats.skipped +
            " created=0 would_create=0 renamed=0 would_rename=0" +
            " missing=" + stats.missing +
            " bad=" + stats.bad
        );

        if (stats.missing != 0 || stats.bad != 0) {
            throw new IllegalStateException("Wave475 apply had missing/bad targets");
        }
    }
}
