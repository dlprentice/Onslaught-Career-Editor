//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionTag;

import java.util.HashSet;
import java.util.Set;

public class ApplyCrtFmodHeadWave630 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String comment;
        final String[] tags;

        Spec(String address, String name, String comment, String[] tags) {
            this.address = address;
            this.name = name;
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
            "crt-fmod-head-wave630",
            "retail-binary-evidence",
            "comment-hardened"
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
        String existingComment = fn.getComment();
        if (existingComment == null || !existingComment.equals(spec.comment)) {
            return true;
        }
        return !hasAllTags(fn, spec.tags);
    }

    private void verifyReadBack(Spec spec) throws Exception {
        Function readBack = functionAtEntry(spec.address);
        if (readBack == null) {
            throw new IllegalStateException("Read-back missing at " + spec.address);
        }
        if (!readBack.getName().equals(spec.name)) {
            throw new IllegalStateException("Read-back name mismatch at " + spec.address + ": " + readBack.getName());
        }
        String readComment = readBack.getComment();
        if (readComment == null || !readComment.equals(spec.comment)) {
            throw new IllegalStateException("Read-back comment mismatch at " + spec.address);
        }
        if (!hasAllTags(readBack, spec.tags)) {
            throw new IllegalStateException("Read-back tag mismatch at " + spec.address);
        }
    }

    private void applySpec(Spec spec, boolean dryRun, Stats stats) {
        try {
            Function fn = functionAtEntry(spec.address);
            if (fn == null) {
                stats.missing++;
                println("MISSING: " + spec.address + " " + spec.name);
                return;
            }
            if (!fn.getName().equals(spec.name)) {
                stats.bad++;
                println("BADNAME: " + spec.address + " actual=" + fn.getName() + " expected=" + spec.name);
                return;
            }
            if (!needsUpdate(fn, spec)) {
                stats.skipped++;
                println("SKIP: " + spec.address + " " + fn.getSignature());
                return;
            }
            if (dryRun) {
                stats.skipped++;
                println("DRY: " + spec.address + " " + fn.getSignature() + " comment/tag update only");
                return;
            }

            fn.setComment(spec.comment);
            for (String tag : spec.tags) {
                fn.addTag(tag);
            }
            verifyReadBack(spec);
            stats.updated++;
            println("OK: " + spec.address + " " + fn.getSignature());
            Thread.sleep(50);
        } catch (Exception ex) {
            stats.bad++;
            println("BAD: " + spec.address + " " + spec.name + " " + ex.getMessage());
        }
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");

        Spec[] specs = new Spec[] {
            new Spec(
                "0x00563ada",
                "CRT__FpuIntDispatch2_Handle",
                "Wave630 CRT fmod/FPU head hardening: custom FPU dispatch helper reached from __cintrindisp2 and __cintrindisp1. It gates on DAT_009d08b4, snapshots ST0, classifies denormal/Inf/NaN/precision status through saved control/status words, rescales ST0 for denormal and Inf/NaN cases, builds a compact EBP-relative error record, and calls CRT__HandleFloatingPointException. Static FPU-dispatch evidence only; custom stack-frame layout, exact CRT version, runtime floating-point side effects, and rebuild parity remain unproven.",
                tags("crt-runtime", "fpu-dispatch", "fpu-exception", "custom-stack")
            ),
            new Spec(
                "0x00563c0b",
                "__ctrandisp1",
                "Wave630 CRT fmod/FPU head hardening: Visual Studio library-match __ctrandisp1 helper. The body loads a caller-provided split double through __fload, calls __trandisp1, then routes through CRT__FpuTransDispatch2_ClearStatusAndHandle; the current saved xref export has no direct callers. Static library-helper evidence only; exact transcendental helper semantics, runtime FPU status effects, and rebuild parity remain unproven.",
                tags("crt-runtime", "fpu-transcendental", "library-match", "fpu-dispatch")
            ),
            new Spec(
                "0x00563c3e",
                "__fload",
                "Wave630 CRT fmod/FPU head hardening: Visual Studio library-match __fload helper. Instruction and decompile read-back show a standard EBP frame that reads two caller stack dwords as a split IEEE-754 double, expands 0x7ff0 exponent patterns into an 80-bit payload, otherwise FLDs the double payload, and returns with caller stack cleanup. Static library-helper evidence only; exact CRT version, NaN payload semantics, runtime FPU behavior, and rebuild parity remain unproven.",
                tags("crt-runtime", "fpu-load", "library-match", "split-double")
            ),
            new Spec(
                "0x00564486",
                "CRT__FmodReduceCore",
                "Wave630 CRT fmod/FPU head hardening: custom-stack long-double remainder reduction helper called twice from CRT__FmodCore. It saves EAX/EBX/ECX, works over extended-double scratch slots on the caller stack, filters exponent/zero/Inf/NaN cases, iterates FPREM-based reductions, adjusts the FPU control word, and restores the FPU environment before returning through the custom path. Static FPU remainder evidence only; exact stack payload layout, CRT helper identity, runtime rounding behavior, and rebuild parity remain unproven.",
                tags("crt-runtime", "fmod-core", "fpu-remainder", "custom-stack")
            ),
            new Spec(
                "0x0056468c",
                "CRT__FmodCore",
                "Wave630 CRT fmod/FPU head hardening: fmod-family core with locked/unknown FPU calling convention. It stores incoming ST0/ST1 into extended-double stack scratch space, takes the direct FPREM path for simple nonzero divisors, and calls CRT__FmodReduceCore for high-exponent or scaled divisor paths before restoring EDX and returning the FPU result. Static FPU remainder evidence only; exact CRT helper identity, runtime fmod edge cases, floating-point ABI details, and rebuild parity remain unproven.",
                tags("crt-runtime", "fmod-core", "fpu-remainder", "custom-stack")
            )
        };

        Stats stats = new Stats();
        println("MODE: " + (dryRun ? "dry" : "apply"));
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }
        println(
            "SUMMARY: updated=" + stats.updated +
            " skipped=" + stats.skipped +
            " renamed=" + stats.renamed +
            " would_rename=" + stats.wouldRename +
            " missing=" + stats.missing +
            " bad=" + stats.bad);
        if (stats.missing != 0 || stats.bad != 0) {
            throw new IllegalStateException("Wave630 apply encountered missing/bad rows");
        }
    }
}
