//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionTag;

import java.util.HashSet;
import java.util.Set;

public class ApplyTextureFilterMmxDispatchWave890 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String signature;
        final String comment;
        final String[] tags;

        Spec(String address, String name, String signature, String comment, String[] tags) {
            this.address = address;
            this.name = name;
            this.signature = signature;
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

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "texture-filter-mmx-dispatch-wave890",
            "wave890-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "signature-verified",
            "texture-filter-mmx-dispatch",
            "important-render-infrastructure",
            "raw-commentless-tail",
            "owner-identity-deferred"
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

    private boolean hasAllTags(Function fn, String[] tags) {
        Set<String> existing = tagNames(fn);
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
        if (!fn.getSignature().toString().equals(spec.signature)) {
            return true;
        }
        String existingComment = fn.getComment();
        if (existingComment == null || !existingComment.equals(spec.comment)) {
            return true;
        }
        return !hasAllTags(fn, spec.tags);
    }

    private void verifyReadBack(Spec spec) throws Exception {
        Function fn = functionAtEntry(spec.address);
        if (fn == null) {
            throw new IllegalStateException("MISSING_READBACK: " + spec.address);
        }
        if (!fn.getName().equals(spec.name)) {
            throw new IllegalStateException("BADNAME_READBACK: " + spec.address + " got " + fn.getName());
        }
        if (!fn.getSignature().toString().equals(spec.signature)) {
            throw new IllegalStateException("BADSIG_READBACK: " + spec.address + " got " + fn.getSignature());
        }
        String comment = fn.getComment();
        if (comment == null || !comment.equals(spec.comment)) {
            throw new IllegalStateException("BADCOMMENT_READBACK: " + spec.address);
        }
        if (!hasAllTags(fn, spec.tags)) {
            throw new IllegalStateException("BADTAGS_READBACK: " + spec.address);
        }
    }

    private void applySpec(Spec spec, boolean dryRun, Stats stats) {
        try {
            Function fn = functionAtEntry(spec.address);
            if (fn == null) {
                stats.missing++;
                println("MISSING: " + spec.address);
                return;
            }
            if (!fn.getName().equals(spec.name)) {
                if (dryRun) {
                    stats.wouldRename++;
                    println("WOULD_RENAME: " + spec.address + " " + fn.getName() + " -> " + spec.name);
                    return;
                }
                stats.renamed++;
                println("RENAME_BLOCKED_BY_POLICY: " + spec.address + " " + fn.getName() + " -> " + spec.name);
                stats.bad++;
                return;
            }
            if (!fn.getSignature().toString().equals(spec.signature)) {
                println("BADSIG: " + spec.address + " got " + fn.getSignature() + " expected " + spec.signature);
                stats.bad++;
                return;
            }
            if (!needsUpdate(fn, spec)) {
                stats.skipped++;
                println("SKIP: " + spec.address + " " + fn.getSignature());
                return;
            }
            if (dryRun) {
                stats.skipped++;
                println("DRY: " + spec.address + " " + spec.signature);
                return;
            }

            fn.setComment(spec.comment);
            for (String tag : spec.tags) {
                fn.addTag(tag);
            }
            verifyReadBack(spec);
            stats.updated++;
            println("OK: " + spec.address + " " + spec.signature);
            Thread.sleep(50);
        } catch (Exception ex) {
            stats.bad++;
            println("FAIL: " + spec.address + " " + ex.getMessage());
        }
    }

    private Spec[] specs() {
        return new Spec[] {
            new Spec(
                "0x0057d0ee",
                "CWaypointManager__BoxBlurPackedColorRows_Scalar",
                "int CWaypointManager__BoxBlurPackedColorRows_Scalar(void)",
                "Wave890 static read-back: scalar packed-color 2x2 row filter/downsample fallback reached from CWaypointManager__BoxBlurPackedColorRows_SIMD and the CPU-selected dispatch pointer at 0x00657974. Static retail Ghidra evidence only: xrefs show pointer-slot DATA writes from 0x0057d446 CWaypointManager__InitMmxDispatchAndRun and 0x0057d47e CDXTexture__InitMmxDispatchAndRun, plus computed dispatch through CFastVB__DispatchMmxKernel_00657974. Current CWaypointManager owner label is preserved as existing Ghidra state; exact owner/source identity, surface/context layout, hidden stack ABI, runtime filtering behavior, BEA patching, and rebuild parity remain unproven.",
                tags("scalar-filter", "dispatch-slot-00657974")
            ),
            new Spec(
                "0x0057d244",
                "CDXTexture__Downsample2x2Average32",
                "int CDXTexture__Downsample2x2Average32(void)",
                "Wave890 static read-back: scalar 32-bit 2x2 average/downsample fallback used by CPU dispatch slot 0x00657978 when MMX support is disabled. Static retail Ghidra evidence only: CFastVB__DispatchMmxKernel_00657978 reaches this row through the slot, while initializer rows 0x0057d446/0x0057d47e write the function pointer alongside the alternate SIMD target. Exact surface/context layout, hidden stack ABI, channel rounding policy, runtime mip/downscale behavior, BEA patching, and rebuild parity remain unproven.",
                tags("scalar-filter", "dispatch-slot-00657978")
            ),
            new Spec(
                "0x0057d32e",
                "CWaypointManager__BoxBlurPackedColorRows_SIMD",
                "int CWaypointManager__BoxBlurPackedColorRows_SIMD(void)",
                "Wave890 static read-back: MMX/SIMD packed-color row filter/downsample kernel selected for dispatch slots 0x00657974 and 0x00657978 when CDXTexture__IsMmxEnabledBySystemConfig returns enabled. Static retail Ghidra evidence only: the body handles 4-aligned row widths with packed word averaging/saturation and falls back to 0x0057d0ee CWaypointManager__BoxBlurPackedColorRows_Scalar otherwise. Current CWaypointManager owner label is preserved as existing Ghidra state; exact owner/source identity, surface/context layout, hidden stack ABI, runtime filtering behavior, BEA patching, and rebuild parity remain unproven.",
                tags("simd-filter", "dispatch-slot-00657974", "dispatch-slot-00657978")
            ),
            new Spec(
                "0x0057d446",
                "CWaypointManager__InitMmxDispatchAndRun",
                "void CWaypointManager__InitMmxDispatchAndRun(void)",
                "Wave890 static read-back: CPU-feature dispatch initializer for slot 0x00657974. Static retail Ghidra evidence only: calls CDXTexture__IsMmxEnabledBySystemConfig, writes 0x00657974 to either CWaypointManager__BoxBlurPackedColorRows_Scalar or CWaypointManager__BoxBlurPackedColorRows_SIMD, also writes the paired 0x00657978 slot, then computed-dispatches slot 0x00657974. Current CWaypointManager owner label is preserved as existing Ghidra state; exact owner/source identity, pointer-table ownership, hidden dispatch ABI, runtime CPU selection behavior, BEA patching, and rebuild parity remain unproven.",
                tags("dispatch-initializer", "dispatch-slot-00657974")
            ),
            new Spec(
                "0x0057d47e",
                "CDXTexture__InitMmxDispatchAndRun",
                "void CDXTexture__InitMmxDispatchAndRun(void)",
                "Wave890 static read-back: CPU-feature dispatch initializer for slot 0x00657978. Static retail Ghidra evidence only: calls CDXTexture__IsMmxEnabledBySystemConfig, selects CDXTexture__Downsample2x2Average32 or CWaypointManager__BoxBlurPackedColorRows_SIMD as the active slot target, mirrors the paired 0x00657974 slot, then computed-dispatches slot 0x00657978. Exact pointer-table ownership, hidden dispatch ABI, runtime CPU selection behavior, runtime texture filtering behavior, BEA patching, and rebuild parity remain unproven.",
                tags("dispatch-initializer", "dispatch-slot-00657978")
            )
        };
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = true;
        if (args != null && args.length > 0) {
            dryRun = isDryRun(args[0]);
        }
        Stats stats = new Stats();
        for (Spec spec : specs()) {
            applySpec(spec, dryRun, stats);
        }
        println("SUMMARY: updated=" + stats.updated + " skipped=" + stats.skipped +
            " renamed=" + stats.renamed + " would_rename=" + stats.wouldRename +
            " missing=" + stats.missing + " bad=" + stats.bad);
        if (!dryRun && stats.bad == 0 && stats.missing == 0) {
            println("REPORT: Save succeeded");
        }
        if (stats.bad != 0 || stats.missing != 0) {
            throw new IllegalStateException("Wave890 apply failed: bad=" + stats.bad + " missing=" + stats.missing);
        }
    }
}
