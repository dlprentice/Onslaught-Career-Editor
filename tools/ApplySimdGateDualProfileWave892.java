//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionTag;

import java.util.HashSet;
import java.util.Set;

public class ApplySimdGateDualProfileWave892 extends GhidraScript {
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
            "simd-gate-dual-profile-wave892",
            "wave892-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "signature-verified",
            "texture-simd",
            "important-render-infrastructure",
            "raw-commentless-tail"
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
                "0x005888bc",
                "CFastVB__InterpolateDualProfileStreams",
                "int CFastVB__InterpolateDualProfileStreams(void)",
                "Wave892 static read-back: dual-profile stream interpolation callback reached only by DATA dispatch slot 0x00657164 in current xref evidence. Static retail Ghidra evidence only: RET 0x30 body handles single-profile and multi-profile modes, accumulates weighted vector triples after __ftol phase reduction against DAT_005e6a3c, calls CFastVB__DispatchIndirectByGlobalTable and CFastVB__DispatchIndirect_00656f48, copies payload bytes before or after vector writes depending on the flag at stack+0x30, advances output pointer arrays and strides, and returns the last advanced pointer context. Exact stream/profile descriptor layout, hidden stack ABI, dispatch-slot ownership, interpolation math equivalence, runtime render behavior, BEA patching, and rebuild parity remain unproven.",
                tags("dual-profile-interpolation", "dispatch-slot-00657164", "ret-0x30")
            ),
            new Spec(
                "0x00589116",
                "CDXTexture__IsMmxEnabledBySystemConfig",
                "int CDXTexture__IsMmxEnabledBySystemConfig(void)",
                "Wave892 static read-back: CDXTexture MMX enable gate called by CDXTexture__DecodeJpegFromMemory, CWaypointManager__InitMmxDispatchAndRun, and CDXTexture__InitMmxDispatchAndRun. Static retail Ghidra evidence only: opens Software\\\\Microsoft\\\\Direct3D, checks DWORD DisableMMX, forces cache global DAT_00657a80 to 0 when disabled, otherwise lazily initializes DAT_00657a80 after GetSystemInfo confirms x86 architecture and processor level greater than 4 and CDXTexture__CpuHasMmxFeature reports true. Exact Windows registry policy, cache lifetime, CPU-feature policy, runtime dispatch behavior, BEA patching, and rebuild parity remain unproven.",
                tags("mmx-registry-gate", "disablemmx", "cpu-feature-cache")
            ),
            new Spec(
                "0x005891c6",
                "CDXTexture__InitCpuVendorAndSimdFlags",
                "void CDXTexture__InitCpuVendorAndSimdFlags(void)",
                "Wave892 static read-back: CPU vendor/SIMD flag initializer called by CFastVB__InitDispatchTableByCpuFeature at 0x00589327. Static retail Ghidra evidence only: initializes a local SEH frame, seeds a GenuineIntel vendor string, captures cpuid_basic_info(0) leaf/vendor values into locals, and jumps into the existing split continuation CDXTexture__DetectCpuSimdFlags at 0x0058920c, which Wave679 tied to CPUID leaf-1 feature bits 0x02000000 and 0x04000000. Exact split-continuation ownership, MSVC SEH model, feature-bit naming, OS feature gating, runtime CPU dispatch behavior, BEA patching, and rebuild parity remain unproven.",
                tags("cpuid-vendor-init", "cpu-feature-init", "split-continuation")
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
            throw new IllegalStateException("Wave892 apply failed: bad=" + stats.bad + " missing=" + stats.missing);
        }
    }
}
