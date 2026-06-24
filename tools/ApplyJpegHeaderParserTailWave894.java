//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionTag;

import java.util.HashSet;
import java.util.Set;

public class ApplyJpegHeaderParserTailWave894 extends GhidraScript {
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
            "jpeg-header-parser-tail-wave894",
            "wave894-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "signature-verified",
            "jpeg-decode-header",
            "important-image-decode-infrastructure",
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
                "0x005913b0",
                "CFastVB__JpegParser_ResetFrameState",
                "int CFastVB__JpegParser_ResetFrameState(void)",
                "Wave894 static read-back: JPEG frame/parser state reset helper with a raw no-function callsite xref at 0x00592617. Static retail Ghidra evidence only: preserves the current name/signature while the hidden ESI state body emits status/event id 0x66 through the state callback, conditionally emits id 0x3d when controller slot +0x0c is nonzero, initializes sixteen per-component/default bytes to 0/1/5, clears frame counters and flags around state slots +0x28/+0x118/+0x12c/+0x11c/+0x122/+0x128, seeds flag bytes at +0x120/+0x121 and words at +0x124/+0x126, writes controller slot +0x0c to 1, and returns 1. Exact JPEG parser state layout, controller slot ownership, caller function boundary, runtime JPEG decode behavior, BEA patching, and rebuild parity remain unproven.",
                tags("jpeg-frame-reset", "hidden-esi-state", "raw-callsite")
            ),
            new Spec(
                "0x00591720",
                "CFastVB__JpegParser_ParseSOFComponents",
                "int CFastVB__JpegParser_ParseSOFComponents(void)",
                "Wave894 static read-back: JPEG SOF component parser with a raw no-function callsite xref at 0x0059274a. Static retail Ghidra evidence only: preserves the current name/signature while the hidden EBX/ESI body reads the byte stream through the state+0x18 source cursor, validates SOF length as component_count*2+6 with component_count in 1..4, stores the component count at state+0x14c, maps component ids through the descriptor table at state+0xdc using 0x15-dword descriptor stride, splits sampling-factor nibbles into descriptor fields +0x14/+0x18, emits status/event ids 0x67/0x68/0x69, records precision/dimension/sampling bytes at state+0x194/+0x198/+0x19c/+0x1a0, clears controller slot +0x14, advances the source cursor, and increments state+0x94. Exact JPEG SOF descriptor layout, sampling enum names, hidden register ABI, caller function boundary, runtime JPEG decode behavior, BEA patching, and rebuild parity remain unproven.",
                tags("jpeg-sof-parser", "component-descriptor", "hidden-register-abi")
            ),
            new Spec(
                "0x0059364c",
                "CDXTexture__GetImageHeaderInfo",
                "int CDXTexture__GetImageHeaderInfo(void)",
                "Wave894 static read-back: image/decode header descriptor query helper called by CDXTexture__DecodePngFromMemory at 0x0057ba81. Static retail Ghidra evidence only: preserves the current name/signature while the body validates required output pointers, copies descriptor width/height and byte fields from offsets +0x18/+0x19/+0x1a/+0x1b/+0x1c, derives the channel/component count from the color/format flag byte at +0x19, optionally returns ancillary descriptor bytes, checks row-size overflow against 0x7fffffff, reports warning string/id 0x5eea60 on overflow risk, and returns 1 on success or 0 on invalid required pointers. Exact descriptor field names, PNG/JPEG shared header schema, color-mode enum names, runtime image decode behavior, BEA patching, and rebuild parity remain unproven.",
                tags("image-header-info", "png-callsite", "descriptor-query")
            ),
            new Spec(
                "0x00594f15",
                "CTexture__FinalizeDecodeFormatDescriptor",
                "int CTexture__FinalizeDecodeFormatDescriptor(void)",
                "Wave894 static read-back: decode format descriptor finalizer called by CDXTexture__ParsePngChunk_IHDR at 0x0059d86d. Static retail Ghidra evidence only: preserves the current name/signature while the body writes width/height, bit-depth and format bytes into the descriptor, derives component count at descriptor+0x1d as 1/3 plus optional alpha, computes bits-per-pixel at descriptor+0x1e, checks row-byte overflow against 0x7fffffff, reports warning string/id 0x5eeaec and clears descriptor dword +0x0c on overflow risk, otherwise stores the computed row-byte count, and returns the hidden EAX value observed by Ghidra. Exact descriptor layout, color/alpha enum names, row-stride contract, hidden EAX return semantics, runtime image decode behavior, BEA patching, and rebuild parity remain unproven.",
                tags("decode-format-descriptor", "png-ihdr", "row-stride")
            )
        };
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        String mode = (args == null || args.length == 0) ? "dry" : args[0];
        boolean dryRun = isDryRun(mode);
        println("ApplyJpegHeaderParserTailWave894 mode=" + (dryRun ? "dry" : "apply"));

        Stats stats = new Stats();
        for (Spec spec : specs()) {
            applySpec(spec, dryRun, stats);
        }

        println(String.format(
            "SUMMARY: updated=%d skipped=%d renamed=%d would_rename=%d missing=%d bad=%d",
            stats.updated,
            stats.skipped,
            stats.renamed,
            stats.wouldRename,
            stats.missing,
            stats.bad
        ));
        if (stats.missing != 0 || stats.bad != 0 || stats.renamed != 0) {
            throw new IllegalStateException("ApplyJpegHeaderParserTailWave894 had failures");
        }
    }
}
