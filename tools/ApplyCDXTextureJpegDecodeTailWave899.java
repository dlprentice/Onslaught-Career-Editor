//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionTag;

import java.util.HashSet;
import java.util.Set;

public class ApplyCDXTextureJpegDecodeTailWave899 extends GhidraScript {
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
            "cdxtexture-jpeg-decode-tail-wave899",
            "wave899-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "signature-verified",
            "important-image-decode-infrastructure",
            "raw-commentless-tail",
            "jpeg-decode-tail"
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
        }
        catch (Exception ex) {
            stats.bad++;
            println("FAIL: " + spec.address + " " + ex.getMessage());
        }
    }

    private Spec[] specs() {
        return new Spec[] {
            new Spec(
                "0x005b7770",
                "CDXTexture__ValidateJpegFrameAndComputeMcuLayout",
                "void CDXTexture__ValidateJpegFrameAndComputeMcuLayout(void)",
                "Wave899 static read-back: JPEG frame validator/MCU-layout helper called by CDXTexture__InitJpegScanController at 0x005b8142. Static retail Ghidra evidence only: preserves the current name/signature while the hidden ESI JPEG-state body validates frame width/height, precision 8, component count <=10, and per-component sampling factors in 1..4, then computes max horizontal/vertical sampling at state+0xf0/+0xf4, fills 0x54-byte component descriptors with block and sample geometry through CDXTexture__CeilDiv, and stores a frame MCU-row count at state+0xf8. Exact JPEG state/component descriptor layout, MCU naming, runtime JPEG/image decode behavior, BEA patching, and rebuild parity remain unproven.",
                tags("jpeg-frame-validator", "mcu-layout", "hidden-esi-state", "scan-controller")
            ),
            new Spec(
                "0x005b7920",
                "CDXTexture__ValidateJpegScanScript",
                "void CDXTexture__ValidateJpegScanScript(void)",
                "Wave899 static read-back: JPEG scan-script validator called by CDXTexture__InitJpegScanController at 0x005b814f. Static retail Ghidra evidence only: preserves the current name/signature while the hidden ESI state body validates scan count, component references, sorted component order, spectral-selection bounds 0..0x3f, successive-approximation bounds 0..10, baseline/full-range scan coverage, progressive scan coverage across a 10x64 stack table, and emits observed diagnostic/event ids 0x11, 0x13, 0x1a, and 0x2d. Exact scan-script descriptor schema, baseline/progressive mode naming, runtime JPEG/image decode behavior, BEA patching, and rebuild parity remain unproven.",
                tags("jpeg-scan-script", "progressive-jpeg", "hidden-esi-state", "scan-controller")
            ),
            new Spec(
                "0x005b7c50",
                "CDXTexture__LoadCurrentJpegScanDescriptor",
                "void CDXTexture__LoadCurrentJpegScanDescriptor(void)",
                "Wave899 static read-back: current JPEG scan-descriptor loader called by CDXTexture__ProcessJpegScanStateMachine at 0x005b7f0f, 0x005b7f4f, and 0x005b7fb5. Static retail Ghidra evidence only: preserves the current name/signature while the hidden ESI state body either builds a default scan over all frame components or loads the active 0x24-byte scan-script entry, fills selected component pointers at state+0x100, and copies spectral/successive approximation fields into state+0x144/+0x148/+0x14c/+0x150. Exact scan-state layout, active-scan index ownership, runtime JPEG/image decode behavior, BEA patching, and rebuild parity remain unproven.",
                tags("jpeg-scan-descriptor", "scan-state-machine", "hidden-esi-state")
            ),
            new Spec(
                "0x005b7d30",
                "CDXTexture__BuildCurrentScanMcuLayout",
                "uint CDXTexture__BuildCurrentScanMcuLayout(void)",
                "Wave899 static read-back: current-scan MCU-layout builder called by CDXTexture__ProcessJpegScanStateMachine at 0x005b7f14, 0x005b7f54, and 0x005b7fba. Static retail Ghidra evidence only: preserves the current name/signature while the hidden ESI state body handles single-component and multi-component scans, computes scan MCU dimensions at state+0x110/+0x114, fills selected component layout fields +0x34/+0x38/+0x3c/+0x40/+0x44/+0x48, builds the component index table at state+0x11c, enforces the observed 10-block limit with event id 0x0d, and caps a restart/row span value at 0xffff. Exact scan MCU table schema, return-value role, restart-interval semantics, runtime JPEG/image decode behavior, BEA patching, and rebuild parity remain unproven.",
                tags("jpeg-current-scan-layout", "mcu-layout", "hidden-esi-state", "scan-state-machine")
            ),
            new Spec(
                "0x005bce60",
                "CDXTexture__ConvertYCbCrToRgb24_Mmx",
                "int CDXTexture__ConvertYCbCrToRgb24_Mmx(void)",
                "Wave899 static read-back: MMX-style YCbCr-to-RGB24 converter reached from raw callsite 0x005afb05. Static retail Ghidra evidence only: preserves the current name/signature while the locked stack-ABI body consumes a pixel count and Y/Cb/Cr/output pointers, processes four pixels per loop, subtracts chroma bias through DAT_005f5000, applies packed multiply/add conversion constants at 0x005f5008/0x005f5010/0x005f5018, clamps each channel to 0..255, writes three packed output dwords per four RGB24 pixels, advances the source/output pointers, and returns the advanced Y pointer. Exact hidden stack parameter names, color coefficient identity, lane packing, runtime image decode/render behavior, BEA patching, and rebuild parity remain unproven.",
                tags("ycbcr-to-rgb24", "mmx-converter", "locked-stack-abi", "raw-callsite-005afb05")
            ),
            new Spec(
                "0x005bd53b",
                "CDXTexture__BuildInflateHuffmanTable",
                "int CDXTexture__BuildInflateHuffmanTable(void)",
                "Wave899 static read-back: inflate Huffman table builder called by CDXTexture__InflateDynamicTree_BuildBitLengthTree at 0x005bd8f6 and CDXTexture__InflateDynamicTree_BuildLitDistTrees at 0x005bd982/0x005bd9b9. Static retail Ghidra evidence only: preserves the current name/signature while the hidden EAX/stack-ABI body counts code lengths, derives min/max bit widths, checks oversubscribed or incomplete trees, fills sorted symbol work buffers, allocates subtables with a 0x5a0 entry cap, writes table entries for literals and extra-bit cases, and returns observed status values 0, -3, and -5. Exact zlib/source identity, table-entry schema, hidden ABI completeness, runtime decompression behavior, BEA patching, and rebuild parity remain unproven.",
                tags("inflate-huffman-table", "dynamic-tree-helper", "hidden-eax-stack-abi", "zlib-style-status")
            )
        };
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        String mode = (args == null || args.length == 0) ? "dry" : args[0];
        boolean dryRun = isDryRun(mode);
        println("ApplyCDXTextureJpegDecodeTailWave899 mode=" + (dryRun ? "dry" : "apply"));

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
            throw new IllegalStateException("ApplyCDXTextureJpegDecodeTailWave899 had failures");
        }
    }
}
