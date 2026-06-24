//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionTag;

import java.util.HashSet;
import java.util.Set;

public class ApplyFEPDirectoryPageWave856 extends GhidraScript {
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
        int signatureChecked = 0;
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

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "fepdirectory-page-wave856",
            "wave856-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "frontend",
            "fepdirectory",
            "save-file-list",
            "directory-page"
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
        Set<String> actual = tagNames(fn);
        for (String tag : tags) {
            if (!actual.contains(tag)) {
                return false;
            }
        }
        return true;
    }

    private String normalizeSignature(String signature) {
        StringBuilder result = new StringBuilder();
        boolean lastWasSpace = false;
        for (int i = 0; i < signature.length(); i++) {
            char ch = signature.charAt(i);
            if (ch == 0x200b || ch == 0x200c || ch == 0x200d || ch == 0xfeff) {
                continue;
            }
            if (ch == 0x00a0 || Character.isWhitespace(ch)) {
                if (!lastWasSpace) {
                    result.append(' ');
                    lastWasSpace = true;
                }
                continue;
            }
            result.append(ch);
            lastWasSpace = false;
        }
        return result.toString().trim();
    }

    private boolean sameSignatureText(Function fn, Spec spec) {
        return normalizeSignature(fn.getSignature().toString()).equals(normalizeSignature(spec.signature));
    }

    private boolean readBackMatches(Function fn, Spec spec, Stats stats) {
        boolean ok = true;
        if (!fn.getName().equals(spec.name)) {
            println("BADNAME: " + spec.address + " expected=" + spec.name + " actual=" + fn.getName());
            ok = false;
        }
        if (!sameSignatureText(fn, spec)) {
            println("BADSIG: " + spec.address + " expected=" + spec.signature + " actual=" + fn.getSignature());
            ok = false;
        }
        if (!spec.comment.equals(fn.getComment())) {
            println("BADCOMMENT: " + spec.address);
            ok = false;
        }
        if (!hasAllTags(fn, spec.tags)) {
            println("BADTAGS: " + spec.address);
            ok = false;
        }
        if (!ok) {
            stats.bad++;
        }
        return ok;
    }

    private void applySpec(Spec spec, boolean dryRun, Stats stats) {
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
        if (!sameSignatureText(fn, spec)) {
            println("BADSIG: " + spec.address + " expected=" + spec.signature + " actual=" + fn.getSignature());
            stats.bad++;
            return;
        }

        stats.signatureChecked++;
        boolean needsCommentOrTags = !spec.comment.equals(fn.getComment()) || !hasAllTags(fn, spec.tags);
        if (needsCommentOrTags) {
            stats.commentOnlyUpdated++;
        }

        if (!needsCommentOrTags) {
            println((dryRun ? "DRY" : "SKIP") + ": " + spec.address + " " + fn.getName() + " already matched");
            stats.skipped++;
            return;
        }
        if (dryRun) {
            println("DRY: " + spec.address + " " + fn.getName()
                + " needsRename=false needsSignature=false needsCommentOrTags=true");
            stats.skipped++;
            return;
        }

        fn.setComment(spec.comment);
        for (String tag : spec.tags) {
            fn.addTag(tag);
        }
        if (readBackMatches(fn, spec, stats)) {
            println("APPLY_OK: " + spec.address + " " + spec.name + " " + fn.getSignature());
        }
        stats.updated++;
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = args == null || args.length == 0 || isDryRun(args[0]);

        Spec[] specs = new Spec[] {
            new Spec(
                "0x0051aa90",
                "CFEPDirectory__Init",
                "int __fastcall CFEPDirectory__Init(void * this)",
                "Wave856 static read-back: CFEPDirectory page init vtable slot 2 from vtable 0x005db800 (DATA xref 0x005db808). The body clears observed directory state: the 0x1000-entry save-name pointer array at this+0x04, save count at this+0x4004, selected index at this+0x4008, scroll offset at this+0x400c, and last-selection/input timestamp at this+0x4010, then returns 1. Static retail Ghidra evidence only; exact CFEPDirectory layout, runtime frontend save-directory behavior, filesystem state, source identity, BEA patching, and rebuild parity remain unproven.",
                tags("vtable-slot", "page-init", "save-list-state")
            ),
            new Spec(
                "0x0051aac0",
                "CFEPDirectory__Shutdown",
                "void __fastcall CFEPDirectory__Shutdown(void * this)",
                "Wave856 static read-back: CFEPDirectory shutdown vtable slot 3 from vtable 0x005db800 (DATA xref 0x005db80c). The body walks the 0x1000 save-name pointer entries at this+0x04, frees each non-null buffer with CDXMemoryManager__Free(&DAT_009c3df0, entry), and clears the slot. Static retail Ghidra evidence only; exact CFEPDirectory layout, allocator ownership beyond the observed buffers, runtime save-directory behavior, source identity, BEA patching, and rebuild parity remain unproven.",
                tags("vtable-slot", "page-shutdown", "save-list-buffer-free")
            ),
            new Spec(
                "0x0051aaf0",
                "CFEPDirectory__ButtonPressed",
                "void __thiscall CFEPDirectory__ButtonPressed(void * this, int button, float val)",
                "Wave856 static read-back: CFEPDirectory button handler vtable slot 5 from vtable 0x005db800 (DATA xref 0x005db814). The switch handles button 0x2a/0x2b as bounded save-list selection movement around this+0x4008 and this+0x4004, button 0x2c as selected-save activation/delete-confirmation flow, and button 0x2e as return to frontend page 0 with fade 0x32. In non-delete mode it stores the selected index at DAT_008a1168, copies the selected wide save name to DAT_008a116c, and sets page 10. In delete mode it creates FEMessBox question id 6 using localized token 0x2a. Static retail Ghidra evidence only; exact button-label mapping, runtime UI behavior, save-file effects, source identity, BEA patching, and rebuild parity remain unproven.",
                tags("vtable-slot", "button-handler", "save-list-selection", "delete-confirmation")
            ),
            new Spec(
                "0x0051ac40",
                "CFEPDirectory__Process",
                "void __thiscall CFEPDirectory__Process(void * this, int state)",
                "Wave856 static read-back: CFEPDirectory process vtable slot 4 from vtable 0x005db800 (DATA xref 0x005db810). When state is not 3 the body refreshes the save-file list, then watches the global FEMessBox result fields for question id 6 and affirmative answer 1. If the selected save-name pointer is non-null, it shows localized token 0x78 through CFrontEndPage__Process_NoOp, calls PCPlatform__DeleteSaveFile(DAT_008a9694, selected_index, selected_name), and on success creates a follow-up FEMessBox with localized token 0x21. Static retail Ghidra evidence only; exact message text, runtime delete behavior, filesystem state, source identity, BEA patching, and rebuild parity remain unproven.",
                tags("vtable-slot", "page-process", "delete-save-flow", "message-box-result")
            ),
            new Spec(
                "0x0051ad30",
                "CFEPDirectory__RefreshSaveFileList",
                "void __thiscall CFEPDirectory__RefreshSaveFileList(void * this, int force_refresh)",
                "Wave856 static read-back: CFEPDirectory save-list refresh helper called by CFEPDirectory__Process and CFEPVirtualKeyboard__Process. The body checks PCPlatform__GetStorageDeviceInfo(DAT_008a9694, &inserted, null, null, null), returns to frontend page 0 with fade 0x32 when force_refresh is 0 and no device is inserted, counts saves through EnumerateSaveFiles_1 into this+0x4004, allocates 0x200-byte buffers from CDXMemoryManager for missing entries using the FEPDirectory.cpp debug path 0x0063fb4c, fills names with EnumerateSaveFiles_2, frees stale trailing buffers, and clamps the selected index at this+0x4008. Static retail Ghidra evidence only; exact CFEPDirectory layout, runtime filesystem enumeration, save-name encoding, source identity, BEA patching, and rebuild parity remain unproven.",
                tags("refresh-save-list", "save-enumeration", "storage-device", "buffer-allocation")
            ),
            new Spec(
                "0x0051b460",
                "CFEPDirectory__Render",
                "void __thiscall CFEPDirectory__Render(void * this, float transition, int dest)",
                "Wave856 static read-back: CFEPDirectory render vtable slot 7 from vtable 0x005db800 (DATA xref 0x005db81c). The body calls CFEPDirectory__RenderSaveFileList(this, transition, dest); when that shared renderer returns a non-zero selection result, it dispatches this vtable slot 3 with button 0x2c and 1.0f, reusing the activation/delete-confirmation path. It then draws a title bar with localized token 0x0f or 0x0e depending on DAT_008a9580 and applies frontend overlay fade math before CFrontEnd__RenderOverlayEffects. Static retail Ghidra evidence only; exact title text, runtime render behavior, source identity, BEA patching, and rebuild parity remain unproven.",
                tags("vtable-slot", "page-render", "save-list-render", "overlay-effects")
            )
        };

        Stats stats = new Stats();
        println("MODE: " + (dryRun ? "dry" : "apply"));
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }
        println("SUMMARY: updated=" + stats.updated
            + " skipped=" + stats.skipped
            + " renamed=" + stats.renamed
            + " would_rename=" + stats.wouldRename
            + " signature_checked=" + stats.signatureChecked
            + " comment_only_updated=" + stats.commentOnlyUpdated
            + " missing=" + stats.missing
            + " bad=" + stats.bad);
        if (stats.missing > 0 || stats.bad > 0) {
            throw new RuntimeException("Wave856 apply failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
