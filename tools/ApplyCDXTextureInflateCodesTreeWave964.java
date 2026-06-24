//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionTag;

import java.util.HashSet;
import java.util.Set;

public class ApplyCDXTextureInflateCodesTreeWave964 extends GhidraScript {
    private static final String ADDRESS = "0x0059c8c1";
    private static final String NAME = "CDXTexture__InflateStream_ProcessZlibState";
    private static final String SIGNATURE =
        "int __stdcall CDXTexture__InflateStream_ProcessZlibState(void * inflate_stream, int flush_mode)";
    private static final String COMMENT =
        "Wave964 re-audit correction: refreshes the Wave713 inflate stream caveat after the Wave731 block-header signature/read-back. "
        + "Fresh Wave964 decompile for this body assigns the CDXTexture__InflateProcessBlockHeader return to the local status value and no longer contains an extraout_ variable at that call; "
        + "body-instruction evidence includes callsite 0x0059c9ce to 0x005b1e94, whose saved signature is int __stdcall CDXTexture__InflateProcessBlockHeader(void * inflate_state, void * inflate_stream, int status_code). "
        + "The function remains a RET 0x8 inflate stream/flush-mode state machine that validates stream/state/input pointers, handles zlib CMF/FLG, dictionary/data-check states, block processing, ResetDecodeWindowState on stream-end, and returns zlib-style status values. "
        + "Static retail Ghidra metadata/decompile/instruction/xref evidence only; exact z_stream layout, inflate-state layout, callback ABI, zlib source identity, runtime inflate behavior, BEA patching, and rebuild parity remain unproven.";
    private static final String[] TAGS = {
        "static-reaudit",
        "cdxtexture-inflate-codes-tree-review-wave964",
        "wave964-readback-verified",
        "retail-binary-evidence",
        "comment-hardened",
        "signature-verified",
        "inflate",
        "zlib",
        "inflate-stream",
        "state-machine",
        "ret-0x8",
        "extraout-eax-gap-resolved"
    };
    private static final String[] REMOVE_TAGS = {
        "extraout-eax-gap"
    };

    private static class Stats {
        int updated = 0;
        int skipped = 0;
        int missing = 0;
        int bad = 0;
        int commentOnlyUpdated = 0;
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

    private Set<String> tagNames(Function fn) {
        Set<String> result = new HashSet<>();
        for (FunctionTag tag : fn.getTags()) {
            result.add(tag.getName());
        }
        return result;
    }

    private boolean hasAllTags(Function fn) {
        Set<String> actual = tagNames(fn);
        for (String tag : TAGS) {
            if (!actual.contains(tag)) {
                return false;
            }
        }
        return true;
    }

    private boolean hasAnyTags(Function fn) {
        Set<String> actual = tagNames(fn);
        for (String tag : REMOVE_TAGS) {
            if (actual.contains(tag)) {
                return true;
            }
        }
        return false;
    }

    private boolean needsUpdate(Function fn) {
        String existingComment = fn.getComment();
        return existingComment == null
            || !existingComment.equals(COMMENT)
            || !hasAllTags(fn)
            || hasAnyTags(fn);
    }

    private void verifyReadBack() throws Exception {
        Function fn = functionAtEntry(ADDRESS);
        if (fn == null) {
            throw new IllegalStateException("Read-back missing at " + ADDRESS);
        }
        if (!NAME.equals(fn.getName())) {
            throw new IllegalStateException("Read-back name mismatch at " + ADDRESS + ": " + fn.getName());
        }
        String signature = fn.getSignature().toString();
        if (!SIGNATURE.equals(signature)) {
            throw new IllegalStateException("Read-back signature mismatch at " + ADDRESS + ": " + signature);
        }
        String comment = fn.getComment();
        if (comment == null || !COMMENT.equals(comment)) {
            throw new IllegalStateException("Read-back comment mismatch at " + ADDRESS);
        }
        if (!hasAllTags(fn)) {
            throw new IllegalStateException("Read-back missing Wave964 tags at " + ADDRESS);
        }
        if (hasAnyTags(fn)) {
            throw new IllegalStateException("Read-back still has stale extraout tag at " + ADDRESS);
        }
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");
        println("ApplyCDXTextureInflateCodesTreeWave964 mode=" + (dryRun ? "dry" : "apply"));

        Stats stats = new Stats();
        try {
            Function fn = functionAtEntry(ADDRESS);
            if (fn == null) {
                println("MISSING: " + ADDRESS);
                stats.missing++;
            } else if (!NAME.equals(fn.getName())) {
                println("BADNAME: " + ADDRESS + " actual=" + fn.getName() + " expected=" + NAME);
                stats.bad++;
            } else if (!SIGNATURE.equals(fn.getSignature().toString())) {
                println("BADSIG: " + ADDRESS + " actual=" + fn.getSignature());
                stats.bad++;
            } else if (!needsUpdate(fn)) {
                println("SKIP: " + ADDRESS + " " + NAME);
                stats.skipped++;
            } else if (dryRun) {
                println("DRY: " + ADDRESS + " comment/tag refresh for " + NAME);
                stats.skipped++;
                stats.commentOnlyUpdated++;
            } else {
                fn.setComment(COMMENT);
                for (String tag : REMOVE_TAGS) {
                    fn.removeTag(tag);
                }
                for (String tag : TAGS) {
                    fn.addTag(tag);
                }
                verifyReadBack();
                println("OK: " + ADDRESS + " " + NAME);
                stats.updated++;
                stats.commentOnlyUpdated++;
                Thread.sleep(50L);
            }
        } catch (Exception ex) {
            println("FAIL: " + ADDRESS + " " + ex.getMessage());
            stats.bad++;
        }

        println("SUMMARY: updated=" + stats.updated
            + " skipped=" + stats.skipped
            + " renamed=0 would_rename=0 signature_updated=0"
            + " comment_only_updated=" + stats.commentOnlyUpdated
            + " missing=" + stats.missing
            + " bad=" + stats.bad);
        if (stats.missing != 0 || stats.bad != 0) {
            throw new IllegalStateException("Wave964 apply encountered missing/bad rows");
        }
        if (!dryRun) {
            println("REPORT: Save succeeded");
        }
    }
}
