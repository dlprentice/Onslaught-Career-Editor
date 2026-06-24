//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionTag;

import java.util.HashSet;
import java.util.Set;

public class ApplySPtrSetClearWave797 extends GhidraScript {
    private static final String ADDRESS = "0x0042f220";
    private static final String NAME = "CSPtrSet__Clear";
    private static final String SIGNATURE = "void __fastcall CSPtrSet__Clear(void * this)";
    private static final String COMMENT =
        "Wave797 static read-back: near-entry CSPtrSet__Clear thunk/wrapper. Instruction evidence at 0x0042f220 is a 5-byte unconditional JMP to the canonical CSPtrSet__Clear body at 0x004e5c60. Decompile/read-back follows that target: if mSize(+0xc) is non-zero, it links mLast->next to g_SPtrSet_FreeListHead when mLast is non-null, moves mFirst into g_SPtrSet_FreeListHead, and zeros mFirst(+0), mLast(+4), and mSize(+0xc) without touching the iterator field at +0x08. Static retail Ghidra evidence only; exact embedded-list owners, runtime pool behavior, source identity, BEA patching, and rebuild parity remain unproven.";
    private static final String[] TAGS = {
        "static-reaudit",
        "sptrset-clear-wave797",
        "wave797-readback-verified",
        "retail-binary-evidence",
        "comment-hardened",
        "sptrset",
        "thunk-wrapper",
        "free-list"
    };

    private static class Stats {
        int updated = 0;
        int skipped = 0;
        int signatureUpdated = 0;
        int commentOnlyUpdated = 0;
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

    private Set<String> tagNames(Function fn) {
        Set<String> names = new HashSet<>();
        for (FunctionTag tag : fn.getTags()) {
            names.add(tag.getName());
        }
        return names;
    }

    private void verifyReadBack() throws Exception {
        Function fn = functionAtEntry(ADDRESS);
        if (fn == null) {
            throw new IllegalStateException("Read-back missing function at " + ADDRESS);
        }
        if (!fn.getName().equals(NAME)) {
            throw new IllegalStateException("Read-back name mismatch at " + ADDRESS + ": " + fn.getName());
        }
        String signature = fn.getSignature().toString();
        if (!signature.equals(SIGNATURE)) {
            throw new IllegalStateException("Read-back signature mismatch at " + ADDRESS + ": " + signature);
        }
        if (fn.getComment() == null || !fn.getComment().equals(COMMENT)) {
            throw new IllegalStateException("Read-back comment mismatch at " + ADDRESS);
        }
        Set<String> actualTags = tagNames(fn);
        for (String tag : TAGS) {
            if (!actualTags.contains(tag)) {
                throw new IllegalStateException("Read-back missing tag at " + ADDRESS + ": " + tag);
            }
        }
    }

    @Override
    protected void run() throws Exception {
        boolean dryRun = isDryRun(getScriptArgs().length > 0 ? getScriptArgs()[0] : "dry");
        println("ApplySPtrSetClearWave797 mode=" + (dryRun ? "dry" : "apply"));

        Stats stats = new Stats();
        try {
            Function fn = functionAtEntry(ADDRESS);
            if (fn == null) {
                println("MISSING: " + ADDRESS + " " + NAME);
                stats.missing++;
            } else if (!fn.getName().equals(NAME)) {
                println("BADNAME: " + ADDRESS + " expected=" + NAME + " actual=" + fn.getName());
                stats.bad++;
            } else {
                String actualSignature = fn.getSignature().toString();
                boolean signatureMismatch = !actualSignature.equals(SIGNATURE);
                boolean commentNeedsUpdate = fn.getComment() == null || !fn.getComment().equals(COMMENT);
                Set<String> actualTags = tagNames(fn);
                boolean tagsNeedUpdate = false;
                for (String tag : TAGS) {
                    if (!actualTags.contains(tag)) {
                        tagsNeedUpdate = true;
                        break;
                    }
                }

                if (signatureMismatch) {
                    println("BADSIG: " + ADDRESS + " expected=" + SIGNATURE + " actual=" + actualSignature);
                    stats.bad++;
                } else if (!commentNeedsUpdate && !tagsNeedUpdate) {
                    println("SKIP: " + ADDRESS + " " + NAME);
                    stats.skipped++;
                } else if (dryRun) {
                    println("DRY: " + ADDRESS + " " + NAME + " comment/tags update only");
                    stats.commentOnlyUpdated++;
                    stats.skipped++;
                } else {
                    fn.setComment(COMMENT);
                    for (String tag : TAGS) {
                        fn.addTag(tag);
                    }
                    verifyReadBack();
                    println("OK: " + ADDRESS + " " + NAME + " signature=" + SIGNATURE);
                    stats.commentOnlyUpdated++;
                    stats.updated++;
                    Thread.sleep(50L);
                }
            }
        } catch (Exception ex) {
            println("FAIL: " + ADDRESS + " " + NAME + " " + ex.getMessage());
            stats.bad++;
        }

        println(
            "SUMMARY: updated=" + stats.updated
            + " skipped=" + stats.skipped
            + " renamed=0 would_rename=0"
            + " signature_updated=" + stats.signatureUpdated
            + " comment_only_updated=" + stats.commentOnlyUpdated
            + " missing=" + stats.missing
            + " bad=" + stats.bad
        );
        if (stats.missing != 0 || stats.bad != 0) {
            throw new IllegalStateException("Wave797 apply encountered missing/bad rows");
        }
    }
}
