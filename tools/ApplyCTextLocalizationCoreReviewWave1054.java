//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionTag;

import java.util.HashSet;
import java.util.Set;

public class ApplyCTextLocalizationCoreReviewWave1054 extends GhidraScript {
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
        int commentUpdated = 0;
        int tagsAdded = 0;
        int missing = 0;
        int bad = 0;
    }

    private static final String[] COMMON_TAGS = {
        "static-reaudit",
        "ctext-localization-core-review-wave1054",
        "wave1054-readback-verified",
        "retail-binary-evidence",
        "comment-hardened",
        "text-localization",
        "ctext-core"
    };

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

    private Function functionAtEntry(String addressText) {
        if (!addressText.startsWith("0x") && !addressText.startsWith("0X")) {
            addressText = "0x" + addressText;
        }
        Address address = toAddr(addressText);
        Function fn = getFunctionAt(address);
        if (fn != null) {
            return fn;
        }
        Function containing = getFunctionContaining(address);
        if (containing != null && containing.getEntryPoint().equals(address)) {
            return containing;
        }
        return null;
    }

    private Set<String> tagNames(Function fn) {
        Set<String> names = new HashSet<>();
        for (FunctionTag tag : fn.getTags()) {
            names.add(tag.getName());
        }
        return names;
    }

    private String[] tags(String... extraTags) {
        String[] result = new String[COMMON_TAGS.length + extraTags.length];
        System.arraycopy(COMMON_TAGS, 0, result, 0, COMMON_TAGS.length);
        System.arraycopy(extraTags, 0, result, COMMON_TAGS.length, extraTags.length);
        return result;
    }

    private int missingTagCount(Function fn, String[] tags) {
        Set<String> actual = tagNames(fn);
        int count = 0;
        for (String tag : tags) {
            if (!actual.contains(tag)) {
                count++;
            }
        }
        return count;
    }

    private void verifyReadBack(Spec spec) {
        Function readBack = functionAtEntry(spec.address);
        if (readBack == null) {
            throw new IllegalStateException("Read-back missing at " + spec.address);
        }
        if (!spec.name.equals(readBack.getName())) {
            throw new IllegalStateException("Read-back name mismatch at " + spec.address + ": " + readBack.getName());
        }
        if (!spec.signature.equals(readBack.getSignature().toString())) {
            throw new IllegalStateException("Read-back signature mismatch at " + spec.address + ": " + readBack.getSignature());
        }
        if (!spec.comment.equals(readBack.getComment())) {
            throw new IllegalStateException("Read-back comment mismatch at " + spec.address);
        }
        Set<String> actual = tagNames(readBack);
        for (String tag : spec.tags) {
            if (!actual.contains(tag)) {
                throw new IllegalStateException("Read-back missing tag at " + spec.address + ": " + tag);
            }
        }
    }

    private void applySpec(Spec spec, boolean dryRun, Stats stats) {
        try {
            Function fn = functionAtEntry(spec.address);
            if (fn == null) {
                println("MISSING: " + spec.address);
                stats.missing++;
                return;
            }
            if (!spec.name.equals(fn.getName())) {
                println("BADNAME: " + spec.address + " expected=" + spec.name + " actual=" + fn.getName());
                stats.bad++;
                return;
            }
            if (!spec.signature.equals(fn.getSignature().toString())) {
                println("BADSIG: " + spec.address + " expected=" + spec.signature + " actual=" + fn.getSignature());
                stats.bad++;
                return;
            }

            boolean commentNeedsUpdate = !spec.comment.equals(fn.getComment());
            int tagsToAdd = missingTagCount(fn, spec.tags);
            if (!commentNeedsUpdate && tagsToAdd == 0) {
                println("SKIP: " + spec.address + " " + spec.name);
                stats.skipped++;
                return;
            }

            if (dryRun) {
                println("DRY: " + spec.address + " " + spec.name
                    + " commentNeedsUpdate=" + commentNeedsUpdate
                    + " tagsToAdd=" + tagsToAdd);
                stats.skipped++;
                if (commentNeedsUpdate) {
                    stats.commentUpdated++;
                }
                stats.tagsAdded += tagsToAdd;
                return;
            }

            if (commentNeedsUpdate) {
                fn.setComment(spec.comment);
                stats.commentUpdated++;
            }
            for (String tag : spec.tags) {
                if (!tagNames(fn).contains(tag)) {
                    fn.addTag(tag);
                    stats.tagsAdded++;
                }
            }
            verifyReadBack(spec);
            currentProgram.flushEvents();
            Thread.sleep(50L);
            println("OK: " + spec.address + " " + spec.name + " comment/tags");
            stats.updated++;
        } catch (Exception ex) {
            println("FAIL: " + spec.address + " " + ex.getMessage());
            stats.bad++;
        }
    }

    private Spec[] specs() {
        return new Spec[] {
            new Spec(
                "0x004f2140",
                "CText__ResetCoreFields",
                "void __fastcall CText__ResetCoreFields(void * this)",
                "Wave1054 CText localization-core read-back: reset helper clears the version, backing-buffer pointer, loaded flag, and file-size fields while preserving the current language id. Static retail Ghidra metadata/decompile/instruction/xref evidence only; exact text.cpp source-body identity, concrete CText layout beyond observed fields, runtime localization behavior, BEA patching, and rebuild parity remain separate proof.",
                tags("reset", "language-preserving")
            ),
            new Spec(
                "0x004f2150",
                "CText__Ctor",
                "void __fastcall CText__Ctor(void * this)",
                "Wave1054 CText localization-core read-back: constructor-style reset clears the core CText fields, initializes the language id to -1, and falls through the same lightweight state used before language-file loading. Static retail Ghidra metadata/decompile/instruction/xref evidence only; exact text.cpp source-body identity, concrete CText layout beyond observed fields, runtime localization behavior, BEA patching, and rebuild parity remain separate proof.",
                tags("constructor", "reset")
            ),
            new Spec(
                "0x004f2170",
                "CText__FreeBuffer",
                "void __fastcall CText__FreeBuffer(void * this)",
                "Wave1054 CText localization-core read-back: cleanup helper frees the current backing buffer through CDXMemoryManager__Free when this+0x04 is non-null, then clears the buffer pointer. Static retail Ghidra metadata/decompile/instruction/xref evidence only; exact allocator ownership, concrete CText layout, runtime localization behavior, BEA patching, and rebuild parity remain separate proof.",
                tags("cleanup", "buffer-free", "allocator")
            ),
            new Spec(
                "0x004f2190",
                "CText__GetLanguageName",
                "char * __fastcall CText__GetLanguageName(void * this)",
                "Wave1054 CText localization-core read-back: maps the saved language id to lowercase language-name strings for english, french, german, spanish, and italian; unknown ids log an error and fall back to english. Static retail Ghidra metadata/decompile/instruction/xref evidence only; runtime language selection behavior, exact source-body identity, BEA patching, and rebuild parity remain separate proof.",
                tags("language-name", "fallback-english")
            ),
            new Spec(
                "0x004f21f0",
                "CText__Init",
                "void __thiscall CText__Init(void * this, uint language)",
                "Wave1054 CText localization-core read-back: loads data\\\\LANGUAGE\\\\<language>.DAT, or american.DAT when the global american-language flag is set, through a stack CDXMemBuffer and CDXMemBuffer__GetFileSize. The loader recognizes the 0xffffffbb header, v1/v2/v3 entry tables, UTF-16 text-pool offsets, v2/v3 audio-name offsets, and extra-flag fields when the header high bit is set. Static retail Ghidra metadata/decompile/instruction/xref evidence only; exact shipped language-file semantics, concrete CText layout, runtime localization/audio behavior, BEA patching, and rebuild parity remain separate proof.",
                tags("language-loader", "language-dat", "text-format", "audio-name-pool", "cdxmembuffer")
            ),
            new Spec(
                "0x004f24b0",
                "CText__GetAudioNameById",
                "char * __thiscall CText__GetAudioNameById(void * this, int text_id)",
                "Wave1054 CText localization-core read-back: v2/v3 audio lookup scans the 3-dword entry table from the loaded backing buffer, matches text_id, rejects 0xffffffff audio offsets, and returns an ASCII audio-name pointer from the audio pool. Static retail Ghidra metadata/decompile/instruction/xref evidence only; exact language/audio table semantics, runtime voice/audio behavior, BEA patching, and rebuild parity remain separate proof.",
                tags("audio-name", "entry-table", "text-format-v2-v3")
            ),
            new Spec(
                "0x004f2500",
                "CText__GetStringByIdAfter",
                "short * __thiscall CText__GetStringByIdAfter(void * this, int text_id, int after_index)",
                "Wave1054 CText localization-core read-back: grouped-string lookup scans the loaded text entry table for text_id, advances by after_index, reads the target entry's UTF-16 word offset, and returns the corresponding string-pool pointer; miss paths log an error and return the base text pool. Static retail Ghidra metadata/decompile/instruction/xref evidence only; exact grouped text semantics, runtime frontend/briefing behavior, BEA patching, and rebuild parity remain separate proof.",
                tags("string-lookup", "after-index", "utf16-text-pool")
            ),
            new Spec(
                "0x004f2580",
                "CText__GetStringById",
                "short * __thiscall CText__GetStringById(void * this, int text_id)",
                "Wave1054 CText localization-core read-back: localized string lookup handles legacy v0 offset-table conversion through MultiByteToWideChar and v1/v2/v3 id-table lookup through UTF-16 text-pool offsets, logging an error when no string exists for the requested id. Static retail Ghidra metadata/decompile/instruction/xref evidence only; exact language-file semantics, runtime text rendering/localization behavior, BEA patching, and rebuild parity remain separate proof.",
                tags("string-lookup", "utf16-text-pool", "legacy-v0", "multibytetowidechar")
            )
        };
    }

    @Override
    protected void run() throws Exception {
        boolean dryRun = isDryRun(getScriptArgs().length > 0 ? getScriptArgs()[0] : "dry");
        println("ApplyCTextLocalizationCoreReviewWave1054 mode=" + (dryRun ? "dry" : "apply"));

        Stats stats = new Stats();
        for (Spec spec : specs()) {
            applySpec(spec, dryRun, stats);
        }

        println(
            "SUMMARY: updated=" + stats.updated
            + " skipped=" + stats.skipped
            + " comment_updated=" + stats.commentUpdated
            + " tags_added=" + stats.tagsAdded
            + " missing=" + stats.missing
            + " bad=" + stats.bad
        );
        if (stats.missing != 0 || stats.bad != 0) {
            throw new IllegalStateException("Wave1054 apply encountered missing/bad rows");
        }
        if (!dryRun) {
            println("REPORT: Save succeeded");
        }
    }
}
