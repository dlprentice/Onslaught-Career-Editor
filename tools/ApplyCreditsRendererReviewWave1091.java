//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionTag;

import java.util.HashSet;
import java.util.Set;

public class ApplyCreditsRendererReviewWave1091 extends GhidraScript {
    private static final String WAVE_TAG = "credits-renderer-review-wave1091";

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
        Address result = toAddr(addressText);
        if (result == null) {
            throw new IllegalArgumentException("Bad address: " + addressText);
        }
        return result;
    }

    private Function functionAtEntry(String addressText) {
        Address entry = addr(addressText);
        Function fn = getFunctionAt(entry);
        if (fn != null) {
            return fn;
        }
        Function containing = getFunctionContaining(entry);
        if (containing != null && containing.getEntryPoint().equals(entry)) {
            return containing;
        }
        return null;
    }

    private Set<String> tagNames(Function fn) {
        Set<String> result = new HashSet<>();
        for (FunctionTag tag : fn.getTags()) {
            result.add(tag.getName());
        }
        return result;
    }

    private boolean hasAllTags(Function fn, String[] tags) {
        Set<String> actual = tagNames(fn);
        for (String tag : tags) {
            if (!actual.contains(tag)) {
                return false;
            }
        }
        return true;
    }

    private String commentOrEmpty(Function fn) {
        String comment = fn.getComment();
        return comment == null ? "" : comment;
    }

    private boolean signatureMatches(Function fn, Spec spec) {
        return fn.getSignature().toString().equals(spec.signature);
    }

    private void verifyReadBack(Spec spec) throws Exception {
        Function fn = functionAtEntry(spec.address);
        if (fn == null) {
            throw new IllegalStateException("Read-back missing at " + spec.address);
        }
        if (!fn.getName().equals(spec.name)) {
            throw new IllegalStateException("Read-back name mismatch at " + spec.address + ": " + fn.getName());
        }
        if (!signatureMatches(fn, spec)) {
            throw new IllegalStateException("Read-back signature mismatch at " + spec.address + ": " + fn.getSignature());
        }
        if (!commentOrEmpty(fn).equals(spec.comment)) {
            throw new IllegalStateException("Read-back comment mismatch at " + spec.address);
        }
        if (!hasAllTags(fn, spec.tags)) {
            throw new IllegalStateException("Read-back tag mismatch at " + spec.address);
        }
    }

    private void applySpec(Spec spec, boolean dryRun, Stats stats) throws Exception {
        Function fn = functionAtEntry(spec.address);
        if (fn == null) {
            println("MISSING: " + spec.address + " " + spec.name);
            stats.missing++;
            return;
        }
        if (!fn.getName().equals(spec.name)) {
            println("BADNAME: " + spec.address + " expected=" + spec.name + " actual=" + fn.getName());
            stats.bad++;
            return;
        }
        if (!signatureMatches(fn, spec)) {
            println("BADSIG: " + spec.address + " expected=" + spec.signature + " actual=" + fn.getSignature());
            stats.bad++;
            return;
        }

        boolean needsCommentOrTags = !commentOrEmpty(fn).equals(spec.comment) || !hasAllTags(fn, spec.tags);
        if (!needsCommentOrTags) {
            println("SKIP: " + spec.address + " " + spec.name);
            stats.skipped++;
            return;
        }
        if (dryRun) {
            println("DRY: " + spec.address + " " + spec.name + " needsCommentOrTags=true");
            stats.commentOnlyUpdated++;
            stats.skipped++;
            return;
        }

        fn.setComment(spec.comment);
        Set<String> existingTags = tagNames(fn);
        for (String tag : spec.tags) {
            if (!existingTags.contains(tag)) {
                fn.addTag(tag);
            }
        }
        verifyReadBack(spec);
        println("OK: " + spec.address + " " + spec.name + " " + fn.getSignature());
        stats.commentOnlyUpdated++;
        stats.updated++;
        Thread.sleep(50L);
    }

    private String[] tags(String... extra) {
        String[] base = new String[] {
            "static-reaudit",
            WAVE_TAG,
            "wave1091-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "credits-renderer"
        };
        String[] result = new String[base.length + extra.length];
        System.arraycopy(base, 0, result, 0, base.length);
        System.arraycopy(extra, 0, result, base.length, extra.length);
        return result;
    }

    private String bounded(String bodyEvidence) {
        return "Wave1091 static read-back: " + bodyEvidence
            + " Static retail Ghidra metadata/tag/xref/instruction/decompile evidence only; runtime credits presentation, exact source-layout identity, BEA patching, gameplay outcomes, and rebuild parity remain separate proof.";
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = args == null || args.length == 0 || isDryRun(args[0]);

        Spec[] specs = new Spec[] {
            new Spec("0x00518bf0", "CCredits__BuildDefaultEntries",
                "void CCredits__BuildDefaultEntries(void)",
                bounded("credits table initializer. Startup thunk 0x00518be0 jumps to this body; the function fills the hard-coded global credits-entry table beginning at DAT_00896ca8 with mixed localized text IDs and literal string rows before credits rendering."),
                tags("credits-table", "startup-thunk", "localized-text")),
            new Spec("0x00519ff0", "CCredits__WriteEntry_TextId",
                "void __thiscall CCredits__WriteEntry_TextId(void * this, int section, int text_id, int style)",
                bounded("localized text-id credits-row helper. It writes one row as {section,text_id,0,style} at the destination entry pointer in ECX/this and is called repeatedly by CCredits__BuildDefaultEntries."),
                tags("credits-row-writer", "localized-text")),
            new Spec("0x0051a010", "CCredits__WriteEntry_String",
                "void __thiscall CCredits__WriteEntry_String(void * this, int section, char * text, int style)",
                bounded("literal-string credits-row helper. It writes one row as {section,-1,text_ptr,style} at the destination entry pointer in ECX/this and is called repeatedly by CCredits__BuildDefaultEntries."),
                tags("credits-row-writer", "literal-text")),
            new Spec("0x0051a030", "CCredits__RenderCredits",
                "bool __stdcall CCredits__RenderCredits(float elapsed, int alpha)",
                bounded("shared per-frame credits renderer. CGame__RollCredits calls it at 0x00472801, and CFEPCredits__Render calls it at 0x0051a92b. It iterates the global credits entries, resolves literal or localized rows, computes style-dependent spacing/alpha, draws via CDXFont__DrawTextDynamic, and returns false when the scroll is finished."),
                tags("credits-render-loop", "frontend-credits", "game-outro")),
            new Spec("0x0046d9f0", "CGame__RunOutroFMV",
                "void __fastcall CGame__RunOutroFMV(void * this)",
                bounded("outro FMV and credits caller context. The level-won outro path handles level-specific cutscene/goodie work and calls CGame__RollCredits for final-level codes 0x2e5 and 800."),
                tags("game-outro", "credits-caller", "source-backed-context")),
            new Spec("0x004726b0", "CGame__RollCredits",
                "void CGame__RollCredits(void)",
                bounded("main-game credits loop used by outro flow. It creates temporary controllers from game.cpp debug allocation sites, plays the credits music selection when enabled, calls CCredits__RenderCredits(elapsed, 0xff) at 0x00472801, updates music/status/render state, and exits on completion or skip before cleanup."),
                tags("game-outro", "credits-caller", "source-backed-context")),
            new Spec("0x0051a7f0", "CFEPCredits__ButtonPressed",
                "void __stdcall CFEPCredits__ButtonPressed(void * this, int button, float val)",
                bounded("frontend credits-page button handler in CFEPCredits vtable slot 3 at 0x005db88c. It handles button 0x2e as back/exit, plays the frontend confirm sound, returns to page 0x11 with transition time 0x1e, and resumes frontend music."),
                tags("frontend-credits", "credits-page", "vtable-slot", "button-handler")),
            new Spec("0x0051a820", "CFEPCredits__Process",
                "void __thiscall CFEPCredits__Process(void * this, int state)",
                bounded("frontend credits-page process hook in CFEPCredits vtable slot 2 at 0x005db888. When state is zero, it checks the completion flag at this+0x08, returns to page 0x11 and resumes frontend music when set, clears the flag, and draws button prompt code 0x2e."),
                tags("frontend-credits", "credits-page", "vtable-slot", "completion-flag")),
            new Spec("0x0051a880", "CFEPCredits__RenderPreCommon",
                "void __stdcall CFEPCredits__RenderPreCommon(void * this, float transition, int dest)",
                bounded("frontend credits-page pre-common render hook in CFEPCredits vtable slot 4 at 0x005db890. When transition reaches 1.0, it dispatches the standard frontend pre-common pass through FUN_004679e0(1.0,0x3fffffff,dest)."),
                tags("frontend-credits", "credits-page", "vtable-slot", "pre-common-render")),
            new Spec("0x0051a8b0", "CFEPCredits__Render",
                "void __thiscall CFEPCredits__Render(void * this, float transition, int dest)",
                bounded("frontend credits-page render hook in CFEPCredits vtable slot 5 at 0x005db894. It derives alpha from transition, calls CCredits__RenderCredits at 0x0051a92b with elapsed time from this+0x04, sets the completion flag at this+0x08 when the shared renderer reports completion, and triggers the full-transition helper path."),
                tags("frontend-credits", "credits-page", "vtable-slot", "completion-flag")),
            new Spec("0x0051a970", "CFEPCredits__TransitionNotification",
                "void __fastcall CFEPCredits__TransitionNotification(void * this, int from_page)",
                bounded("frontend credits-page transition-notification hook in CFEPCredits vtable slot 6 at 0x005db898, rechecking the prior Wave855 row. It reads platform time, adds float delay 0x005d8ba0, stores the timer at this+0x04, calls CMusic__PlaySelection(&DAT_00889a48,1,1), clears the completion flag at this+0x08, ignores from_page, and returns with RET 0x4."),
                tags("frontend-credits", "credits-page", "vtable-slot", "transition-notification", "credits-music", "completion-flag"))
        };

        Stats stats = new Stats();
        println("MODE: " + (dryRun ? "dry" : "apply"));
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }
        println("SUMMARY: updated=" + stats.updated
            + " skipped=" + stats.skipped
            + " renamed=0 would_rename=0 signature_updated=0"
            + " comment_only_updated=" + stats.commentOnlyUpdated
            + " missing=" + stats.missing
            + " bad=" + stats.bad);
        if (stats.missing > 0 || stats.bad > 0) {
            throw new RuntimeException("Wave1091 apply failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
