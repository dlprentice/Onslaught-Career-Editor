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

public class ApplyOptionsDetailWave466 extends GhidraScript {
    private static class Spec {
        final String address;
        final String oldName;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final String comment;
        final String[] tags;
        final ParameterImpl[] parameters;

        Spec(
                String address,
                String oldName,
                String name,
                String callingConvention,
                DataType returnType,
                String comment,
                String[] tags,
                ParameterImpl[] parameters) {
            this.address = address;
            this.oldName = oldName;
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
            "options-detail-wave466",
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
                throw new IllegalStateException(
                    "Unexpected function name at " + spec.address + ": " + fn.getName()
                );
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
                "0x004ceef0",
                "LandscapeDetail_SetLevel",
                "LandscapeDetail_SetLevel",
                "__stdcall",
                voidType,
                "Wave466 correction: Options/detail setter that maps detail level 0/1/2 onto the persisted landscape detail bytes at g_LandscapeDetailLevel2 and g_LandscapeDetailLevel1. Static retail-binary evidence only; exact menu item class identity, source identity, runtime rendering behavior, and rebuild parity remain unproven.",
                tags("options-menu", "landscape-detail", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("detail_level", intType)
                }
            ),
            new Spec(
                "0x004cef30",
                "LandscapeDetail_GetLevel",
                "LandscapeDetail_GetLevel",
                "__cdecl",
                intType,
                "Wave466 correction: Options/detail getter that returns 2 when g_LandscapeDetailLevel2 is set, otherwise returns the boolean state of g_LandscapeDetailLevel1. Static retail-binary evidence only; exact menu item class identity, source identity, runtime rendering behavior, and rebuild parity remain unproven.",
                tags("options-menu", "landscape-detail", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {}
            ),
            new Spec(
                "0x004cef50",
                "CTreeDetail__VFunc_14_004cef50",
                "CTreeDetail__SetQualityLevel",
                "__stdcall",
                voidType,
                "Wave466 correction: Tree-detail option setter that forwards the selected quality level directly to CRTMesh__SetQualityLevel. Static retail-binary evidence only; exact virtual slot name, source identity, runtime tree/mesh LOD behavior, and rebuild parity remain unproven.",
                tags("options-menu", "tree-detail", "name-corrected", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("quality_level", intType)
                }
            ),
            new Spec(
                "0x004cf030",
                "CMouseSensitivityMenuItem__VFunc_00_004cf030",
                "CMouseSensitivityMenuItem__scalar_deleting_dtor",
                "__thiscall",
                voidPtr,
                "Wave466 correction: Mouse-sensitivity menu-item scalar-deleting destructor that calls CMenuItem__Destructor, frees this when flags bit 0 is set, and returns this. Static retail-binary evidence only; exact class layout, source identity, runtime UI behavior, and rebuild parity remain unproven.",
                tags("options-menu", "mouse-sensitivity", "destructor", "name-corrected", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("flags", intType)
                }
            ),
            new Spec(
                "0x004cf8e0",
                "CMultiSample__VFunc_17_004cf8e0",
                "CMultiSample__GetSampleCountLabel",
                "__stdcall",
                voidPtr,
                "Wave466 correction: Multisample option label resolver that maps a requested available MSAA ordinal through the active display-profile capability bits and returns the matching static/localized label pointer, falling back through Localization__GetStringById(0xd4). Static retail-binary evidence only; exact D3D profile layout, source identity, runtime device behavior, and rebuild parity remain unproven.",
                tags("options-menu", "multisample", "graphics-profile", "name-corrected", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("available_sample_ordinal", intType)
                }
            ),
            new Spec(
                "0x004cffd0",
                "CVideoDetailLevel__VFunc_15_004cffd0",
                "CVideoDetailLevel__GetCurrentPresetFromItems",
                "__fastcall",
                intType,
                "Wave466 correction: Video-detail preset recognizer that compares child option-item values against active display-profile defaults and texture/multisample globals, returning preset 1, 2, 3, or 0 for no exact preset match. Static retail-binary evidence only; exact object layout, source identity, runtime device/menu behavior, and rebuild parity remain unproven.",
                tags("options-menu", "video-detail", "graphics-profile", "name-corrected", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("video_detail_menu", voidPtr)
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
            " created=" + stats.created +
            " would_create=" + stats.wouldCreate +
            " renamed=" + stats.renamed +
            " would_rename=" + stats.wouldRename +
            " missing=" + stats.missing +
            " bad=" + stats.bad
        );

        if (stats.missing != 0 || stats.bad != 0) {
            throw new IllegalStateException("Wave466 apply had missing/bad targets");
        }
    }
}
