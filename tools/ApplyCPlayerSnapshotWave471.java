//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.FunctionTag;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyCPlayerSnapshotWave471 extends GhidraScript {
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
        return getFunctionAt(addr(addressText));
    }

    private ParameterImpl param(String name, DataType type) throws Exception {
        return new ParameterImpl(name, type, currentProgram);
    }

    private String expectedSignature(Spec spec) {
        StringBuilder sb = new StringBuilder();
        sb.append(spec.returnType.getDisplayName())
            .append(" ")
            .append(spec.callingConvention)
            .append(" ")
            .append(spec.name)
            .append("(");
        for (int i = 0; i < spec.parameters.length; i++) {
            if (i != 0) {
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
            "cplayer-snapshot-wave471",
            "retail-binary-evidence",
            "source-bridge"
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

        Spec[] specs = new Spec[] {
            new Spec(
                "0x004d2a70",
                "CPlayer__GetCurrentViewPoint",
                "CPlayer__GetCurrentViewPoint",
                "__thiscall",
                voidType,
                "Wave471 signature/comment hardening: CPlayer::GetCurrentViewPoint source bridge. Retail body uses the player number field at +0x2c to find the active camera table entry, writes a zero FVector-style 16-byte fallback when no camera exists, otherwise calls the camera slot 0 getter and copies the returned 16 bytes into out_current_view_point. The function returns with RET 0x4, confirming a single hidden-return/output pointer stack argument. Static retail/source evidence only; exact FVector layout, camera-table indexing, runtime camera behavior, and rebuild parity remain unproven.",
                tags("cplayer", "camera-view", "snapshot", "view-point", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("out_current_view_point", voidPtr)
                }
            ),
            new Spec(
                "0x004d2ae0",
                "CPlayer__GetCurrentViewOrientation",
                "CPlayer__GetCurrentViewOrientation",
                "__thiscall",
                voidType,
                "Wave471 signature/comment hardening: CPlayer::GetCurrentViewOrientation source bridge. Retail body seeds a 48-byte orientation buffer from the identity matrix at DAT_0082b5c0, uses the player number field at +0x2c to find the active camera table entry, optionally calls camera slot +0x4 to replace the matrix, then copies 12 dwords into out_current_view_orientation. RET 0x4 confirms a single hidden-return/output pointer stack argument. Static retail/source evidence only; exact FMatrix layout, camera-table indexing, runtime camera behavior, and rebuild parity remain unproven.",
                tags("cplayer", "camera-view", "snapshot", "view-orientation", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("out_current_view_orientation", voidPtr)
                }
            ),
            new Spec(
                "0x004d2b40",
                "CPlayer__GetOldCurrentViewPoint",
                "CPlayer__GetOldCurrentViewPoint",
                "__thiscall",
                voidType,
                "Wave471 signature/comment hardening: CPlayer::GetOldCurrentViewPoint source bridge. Retail body mirrors the current-view point helper but calls camera slot +0x8 for the old-position path, falling back to a zero FVector-style 16-byte output when no camera exists. RET 0x4 confirms a single hidden-return/output pointer stack argument. Static retail/source evidence only; exact FVector layout, camera-table indexing, runtime camera behavior, and rebuild parity remain unproven.",
                tags("cplayer", "camera-view", "snapshot", "old-view-point", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("out_old_view_point", voidPtr)
                }
            ),
            new Spec(
                "0x004d2bb0",
                "CPlayer__GetOldCurrentViewOrientation",
                "CPlayer__GetOldCurrentViewOrientation",
                "__thiscall",
                voidType,
                "Wave471 signature/comment hardening: CPlayer::GetOldCurrentViewOrientation source bridge. Retail body mirrors the current-orientation helper, seeds the 48-byte identity matrix from DAT_0082b5c0, optionally calls camera slot +0xc for the old-orientation path, then copies 12 dwords into out_old_view_orientation. Raw disassembly confirms the epilogue at 0x004d2c02 returns with RET 0x4. Static retail/source evidence only; exact FMatrix layout, camera-table indexing, runtime camera behavior, and rebuild parity remain unproven.",
                tags("cplayer", "camera-view", "snapshot", "old-view-orientation", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("out_old_view_orientation", voidPtr)
                }
            )
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }

        println(
            "SUMMARY updated=" + stats.updated +
            " skipped=" + stats.skipped +
            " created=" + stats.created +
            " would_create=" + stats.wouldCreate +
            " renamed=" + stats.renamed +
            " would_rename=" + stats.wouldRename +
            " missing=" + stats.missing +
            " bad=" + stats.bad
        );
        if (stats.bad != 0 || stats.missing != 0) {
            throw new RuntimeException("Wave471 CPlayer snapshot apply failed: bad=" + stats.bad + " missing=" + stats.missing);
        }
    }
}
