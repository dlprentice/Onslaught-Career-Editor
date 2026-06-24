//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionTag;

import java.util.HashSet;
import java.util.Set;

public class ApplyPcPlatformResourceTailWave852 extends GhidraScript {
    private static class Spec {
        final String address;
        final String expectedName;
        final String expectedSignature;
        final String comment;
        final String[] tags;

        Spec(String address, String expectedName, String expectedSignature, String comment, String[] tags) {
            this.address = address;
            this.expectedName = expectedName;
            this.expectedSignature = expectedSignature;
            this.comment = comment;
            this.tags = tags;
        }
    }

    private static class Stats {
        int updated = 0;
        int skipped = 0;
        int renamed = 0;
        int wouldRename = 0;
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
            "pc-platform-resource-tail-wave852",
            "wave852-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "signature-verified"
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

    private boolean signatureMatches(Function fn, Spec spec) {
        return fn.getSignature().toString().equals(spec.expectedSignature);
    }

    private boolean readBackMatches(Function fn, Spec spec, Stats stats) {
        boolean ok = true;
        if (!fn.getName().equals(spec.expectedName)) {
            println("BADNAME: " + spec.address + " expected=" + spec.expectedName + " actual=" + fn.getName());
            ok = false;
        }
        if (!signatureMatches(fn, spec)) {
            println("BADSIG: " + spec.address + " expected=" + spec.expectedSignature + " actual=" + fn.getSignature());
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
            println("MISSING: " + spec.address + " " + spec.expectedName);
            stats.missing++;
            return;
        }
        if (!fn.getName().equals(spec.expectedName)) {
            println("BADNAME: " + spec.address + " expected=" + spec.expectedName + " actual=" + fn.getName());
            stats.bad++;
            return;
        }
        if (!signatureMatches(fn, spec)) {
            println("BADSIG: " + spec.address + " expected=" + spec.expectedSignature + " actual=" + fn.getSignature());
            stats.bad++;
            return;
        }

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
            println("DRY: " + spec.address + " " + fn.getName() + " needsCommentOrTags=true");
            stats.skipped++;
            return;
        }

        fn.setComment(spec.comment);
        for (String tag : spec.tags) {
            fn.addTag(tag);
        }
        if (readBackMatches(fn, spec, stats)) {
            println("APPLY_OK: " + spec.address + " " + spec.expectedName + " " + fn.getSignature());
        }
        stats.updated++;
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = args == null || args.length == 0 || isDryRun(args[0]);

        Spec[] specs = new Spec[] {
            new Spec(
                "0x00515ab0",
                "D3DDevice__SetViewport",
                "void __stdcall D3DDevice__SetViewport(void * viewport)",
                "Wave852 static read-back/comment hardening: important PC render connector called by CDXEngine pre/render/post paths, CEngine__SelectViewpoint, and CHud target-indicator overlay. The body copies CViewport-like fields into a D3DVIEWPORT-style stack record, then calls the global D3D device at DAT_00888a50 through vtable slot 0xbc. Source CPCPlatform::SetViewport and LT.D3D_SetViewport support the D3D SetViewport role. Static retail/source-reference evidence only; exact viewport field schema, runtime D3D behavior, BEA patching, and rebuild parity remain deferred.",
                tags("pc-platform", "d3d-viewport", "render-connector")
            ),
            new Spec(
                "0x00515b10",
                "PCPlatform__DeserializeFontsAndAssets",
                "void __thiscall PCPlatform__DeserializeFontsAndAssets(void * this, int chunk_reader)",
                "Wave852 static read-back/comment hardening: important PC font/resource deserialize connector called by CResourceAccumulator__ReadResourceFile. The body frees existing font slots around this+0x18/0x1c/0x20/0x24/0x28/0x2c, emits the retail warning string \"Warning : deserializing font twice!\", allocates four 0x1180 CDXBitmapFont-like objects, calls CDXBitmapFont__Deserialize on the chunk reader, and sets the main-font swap flag at +0x168. Source CPCPlatform::InitFonts supports the font-slot ownership but not exact serialized chunk layout. Static retail/source-reference evidence only; exact font class layout, resource chunk schema, runtime load behavior, BEA patching, and rebuild parity remain deferred.",
                tags("pc-platform", "font-resources", "resource-deserialize")
            ),
            new Spec(
                "0x00515db0",
                "Registry__SetStringValue_HKCU",
                "void __stdcall Registry__SetStringValue_HKCU(char * value_name, uchar * value_text)",
                "Wave852 static read-back/comment hardening: important PC registry persistence helper called by CConsole__Init and CConsole__AddString. The body opens/creates HKEY_CURRENT_USER Software\\Lost Toys\\Battle Engine Aquila as REG_SZ/volatile/key-all-access, computes the NUL-terminated value length, writes value_text with RegSetValueExA type 1, and closes the key. Source PCPlatform registry helpers match the HKCU Battle Engine Aquila path. Static retail/source-reference evidence only; exact caller value contract, runtime registry side effects, BEA patching, and rebuild parity remain deferred.",
                tags("pc-platform", "registry", "console")
            ),
            new Spec(
                "0x00515f60",
                "CResourceDescriptorTable__ctor",
                "void * __fastcall CResourceDescriptorTable__ctor(void * this)",
                "Wave852 static read-back/comment hardening: important resource-descriptor table constructor reached from DATA xref 0x00515f35. The body vector-constructs one 0x41c-byte CResourceDescriptor-like entry at this+0x08 with CResourceDescriptor__ctor/CResourceDescriptor__dtor, then sets this+0x424 to 1. Static retail evidence only; exact global object identity, descriptor field schema, runtime initialization order, BEA patching, and rebuild parity remain deferred.",
                tags("resource-descriptor", "constructor", "global-table")
            ),
            new Spec(
                "0x00515fb0",
                "CResourceDescriptorTable__InitDefaultMeshNames",
                "void CResourceDescriptorTable__InitDefaultMeshNames(void)",
                "Wave852 static read-back/comment hardening: important default render-resource descriptor initializer called by CLTShell__InitializeRuntimeAndLoadCoreResources. The body initializes a global 0x428-byte-stride descriptor table with mesh/resource names including default.msh, cannon1.msh, radar1.msh, plane1.msh, tree2.msh, tank1.msh, Enemymech.msh, bloke.msh, EnemyT~1.msh, shell.msh, cockpit2.msh, and carrier.msh, plus descriptor ids/flags and DAT_00896488 count 0x17. Static retail/source-reference evidence only; exact descriptor schema, full asset taxonomy, runtime resource loading, BEA patching, and rebuild parity remain deferred.",
                tags("resource-descriptor", "default-mesh", "global-table")
            ),
            new Spec(
                "0x00516450",
                "CResourceDescriptorTable__FreeAllEntries",
                "void CResourceDescriptorTable__FreeAllEntries(void)",
                "Wave852 static read-back/comment hardening: important resource-descriptor shutdown helper called by CLTShell__ShutdownRuntimeAndReleaseResources. The body walks the global descriptor records from DAT_0088a510 toward 0x00896868 in 0x428-byte strides, frees each populated pointer in the per-descriptor entry array through CDXMemoryManager__Free, nulls those pointers, frees the array pointer, and nulls it. Static retail evidence only; exact descriptor ownership schema, runtime shutdown behavior, BEA patching, and rebuild parity remain deferred.",
                tags("resource-descriptor", "resource-lifetime", "shutdown")
            ),
            new Spec(
                "0x005164b0",
                "CResourceDescriptorTable__InstantiateChain",
                "void * __cdecl CResourceDescriptorTable__InstantiateChain(void * descriptor_table, int owner_tag)",
                "Wave852 static read-back/comment hardening: important render-resource instantiation connector called by CThing__InitRenderThing. The body scans the global 0x428-byte-stride descriptor table up to DAT_00896488, matches descriptor_table, skips disabled (-1) descriptors, walks the descriptor chain backward, creates objects through PCRTID__CreateObject, stores owner_tag into the descriptor payload at +0x400, calls the created object's init vfunc slot +4, and links created objects into a local chain. Static retail evidence only; exact descriptor payload schema, returned chain/list-head semantics, runtime render-object behavior, BEA patching, and rebuild parity remain deferred.",
                tags("resource-descriptor", "render-thing", "pcrtid")
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
            + " signature_updated=" + stats.signatureUpdated
            + " comment_only_updated=" + stats.commentOnlyUpdated
            + " missing=" + stats.missing
            + " bad=" + stats.bad);
        if (stats.missing != 0 || stats.bad != 0) {
            throw new RuntimeException("Wave852 apply failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
        if (!dryRun) {
            currentProgram.flushEvents();
        }
    }
}
