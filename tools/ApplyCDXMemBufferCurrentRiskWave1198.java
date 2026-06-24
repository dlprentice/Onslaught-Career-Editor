//@category BEA

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionManager;
import ghidra.program.model.listing.FunctionTag;

import java.util.Arrays;
import java.util.HashSet;
import java.util.Set;

public class ApplyCDXMemBufferCurrentRiskWave1198 extends GhidraScript {
    private static class Target {
        final String address;
        final String name;
        final String signature;
        final String comment;

        Target(String address, String name, String signature, String comment) {
            this.address = address;
            this.name = name;
            this.signature = signature;
            this.comment = comment;
        }
    }

    private static final String[] COMMON_TAGS = {
        "static-reaudit",
        "wave1198-cdxmembuffer-current-risk-review",
        "wave1198-readback-verified",
        "retail-binary-evidence",
        "current-risk-review",
        "score15-16",
        "cdxmembuffer-resource-buffer",
        "resource-buffer",
        "source-identity-deferred",
        "exact-layout-deferred",
        "runtime-behavior-deferred",
        "rebuild-grade-static-contract",
        "no-noticeable-difference-boundary",
        "comment-hardened",
        "signature-hardened",
        "tag-normalized"
    };

    private static final Target[] TARGETS = {
        new Target(
            "0x00547d70",
            "CDXMemBuffer__ctor",
            "void * __fastcall CDXMemBuffer__ctor(void * this)",
            "Wave1198 static current-risk read-back: score16 CDXMemBuffer resource-buffer constructor retained from earlier name/signature correction with normalized rebuild-grade tags. Fresh metadata/decompile evidence keeps the this-only fastcall signature; body clears file/data/CRC pointer and buffered reader state fields used by CDXMemBuffer file IO. This corrects the stale CChunker-owner direction without proving a concrete retail layout. Static rebuild contract only; exact source-body identity, concrete CDXMemBuffer/file/CRC layouts, runtime IO behavior, BEA patching, rebuild parity, and clean-room/no-noticeable-difference parity remain separate proof."
        ),
        new Target(
            "0x00547ec0",
            "CDXMemBuffer__InitFromFile",
            "bool __thiscall CDXMemBuffer__InitFromFile(void * this, char * filename, int memType, int mungePath, uint startSkip)",
            "Wave1198 static current-risk read-back: score16 CDXMemBuffer file-open/init helper retained from earlier name/signature correction with normalized rebuild-grade tags. Fresh xrefs include frontend/config, texture/resource, particle, mesh, and archive-style consumers; fresh body evidence keeps the filename/memType/mungePath/startSkip RET 0x10 contract. Static contract: allocates the active read buffer, opens the target file, initializes cursor/EOF/read-mode state, optionally skips start bytes, and handles CRC-style side data through the same buffer state. Static rebuild contract only; exact source-body identity, concrete CDXMemBuffer/file/CRC/path-munge layouts, runtime IO behavior, BEA patching, rebuild parity, and clean-room/no-noticeable-difference parity remain separate proof."
        ),
        new Target(
            "0x005482d0",
            "CDXMemBuffer__Skip",
            "int __thiscall CDXMemBuffer__Skip(void * this, int size)",
            "Wave1198 static current-risk read-back: score16 CDXMemBuffer skip helper retained from earlier name/signature correction with normalized rebuild-grade tags. Fresh metadata/decompile evidence keeps the RET 0x4 size argument; body advances the buffered read cursor, reloads blocks as needed, and returns the observed skipped byte count. Static rebuild contract only; exact source-body identity, concrete cursor/buffer/handle layouts, runtime IO behavior, BEA patching, rebuild parity, and clean-room/no-noticeable-difference parity remain separate proof."
        ),
        new Target(
            "0x00548570",
            "CDXMemBuffer__Read",
            "int __thiscall CDXMemBuffer__Read(void * this, void * data, int size)",
            "Wave1198 static current-risk read-back: score16 CDXMemBuffer read helper retained from earlier name/signature correction with normalized rebuild-grade tags. Fresh xref evidence shows broad archive/resource consumers, and fresh body evidence keeps the data/size RET 0x8 contract. Static contract: copies available bytes from the active buffer into caller storage, reloads backing file blocks when needed, updates cursor/position state, preserves short-read/EOF behavior, and includes CRC-side-data checks on the same stream state. Static rebuild contract only; exact source-body identity, concrete file/buffer/CRC layouts, runtime IO behavior, BEA patching, rebuild parity, and clean-room/no-noticeable-difference parity remain separate proof."
        ),
        new Target(
            "0x00548c00",
            "CDXMemBuffer__Close",
            "bool __fastcall CDXMemBuffer__Close(void * this)",
            "Wave1198 static current-risk read-back: score16 CDXMemBuffer close helper retained from earlier name/signature correction with normalized rebuild-grade tags. Fresh body evidence keeps the this-only fastcall signature and the split read/write cleanup contract. Static contract: in read mode closes the file handle and frees read/CRC buffers; in write mode flushes buffered bytes and CRC side data before cleanup, then clears owned state and returns a boolean-style success value. Static rebuild contract only; exact source-body identity, concrete file/buffer/CRC/write-mode layouts, runtime IO behavior, BEA patching, rebuild parity, and clean-room/no-noticeable-difference parity remain separate proof."
        ),
        new Target(
            "0x004cdb90",
            "CDXMemBuffer__dtor_base_Thunk",
            "void __fastcall CDXMemBuffer__dtor_base_Thunk(void)",
            "Wave1198 static current-risk read-back: score15 CDXMemBuffer destructor thunk retained from Wave823 with normalized rebuild-grade tags. Fresh xref evidence keeps the ParticleSet.cpp unwind cleanup at 0x005d4230, where a stack-local CDXMemBuffer at EBP-0x140 is destroyed after particle-set file loading; fresh body evidence keeps this as a single-instruction jump thunk to 0x00547d90 CDXMemBuffer__dtor_base, not the destructor body itself. Static rebuild contract only; exact unwind parent identity, concrete stack-local buffer lifetime, runtime particle archive behavior, BEA patching, rebuild parity, and clean-room/no-noticeable-difference parity remain separate proof."
        )
    };

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        String mode = args != null && args.length > 0 ? args[0].trim().toLowerCase() : "dry";
        boolean dryRun = true;
        if ("apply".equals(mode)) {
            dryRun = false;
        } else if (!"dry".equals(mode)) {
            throw new IllegalArgumentException("Expected mode dry|apply, got: " + mode);
        }

        FunctionManager functionManager = currentProgram.getFunctionManager();
        int updated = 0;
        int skipped = 0;
        int commentOnlyUpdated = 0;
        int tagsAdded = 0;
        int missing = 0;
        int bad = 0;

        for (Target target : TARGETS) {
            Address address = toAddr(target.address);
            Function function = functionManager.getFunctionAt(address);
            if (function == null) {
                println("MISSING: " + target.address + " " + target.name);
                missing++;
                continue;
            }

            boolean targetBad = false;
            if (!target.name.equals(function.getName())) {
                println("BADNAME: " + target.address + " expected=" + target.name + " actual=" + function.getName());
                targetBad = true;
            }
            if (!target.signature.equals(function.getSignature().toString())) {
                println("BADSIG: " + target.address + " expected=" + target.signature + " actual=" + function.getSignature());
                targetBad = true;
            }
            if (targetBad) {
                bad++;
                continue;
            }

            Set<String> actualTags = tagNames(function);
            Set<String> requiredTags = new HashSet<>(Arrays.asList(COMMON_TAGS));
            requiredTags.removeAll(actualTags);
            boolean commentNeedsUpdate = function.getComment() == null || !target.comment.equals(function.getComment());
            boolean tagsNeedUpdate = !requiredTags.isEmpty();

            if (!commentNeedsUpdate && !tagsNeedUpdate) {
                println("SKIP: " + target.address + " " + target.name + " comment/tags already current");
                skipped++;
            } else if (dryRun) {
                println("WOULD_UPDATE: " + target.address + " " + target.name + " comment=" + commentNeedsUpdate + " tags=+" + String.join(",", requiredTags));
                if (commentNeedsUpdate) {
                    commentOnlyUpdated++;
                }
                tagsAdded += requiredTags.size();
            } else {
                if (commentNeedsUpdate) {
                    function.setComment(target.comment);
                    commentOnlyUpdated++;
                }
                for (String tag : requiredTags) {
                    function.addTag(tag);
                }
                tagsAdded += requiredTags.size();
                updated++;
                currentProgram.flushEvents();
                Thread.sleep(50L);

                Function readBack = functionManager.getFunctionAt(address);
                if (readBack == null) {
                    println("VERIFY_MISSING: " + target.address);
                    bad++;
                } else {
                    if (!target.comment.equals(readBack.getComment())) {
                        println("VERIFY_BAD_COMMENT: " + target.address);
                        bad++;
                    }
                    Set<String> readBackTags = tagNames(readBack);
                    for (String tag : COMMON_TAGS) {
                        if (!readBackTags.contains(tag)) {
                            println("VERIFY_MISSING_TAG: " + target.address + " " + tag);
                            bad++;
                        }
                    }
                }
                println("UPDATED: " + target.address + " " + target.name + " comment=" + commentNeedsUpdate + " tags_added=" + requiredTags.size());
            }
        }

        println("SUMMARY: updated=" + updated
            + " skipped=" + skipped
            + " renamed=0"
            + " would_rename=0"
            + " signature_updated=0"
            + " comment_only_updated=" + commentOnlyUpdated
            + " tags_added=" + tagsAdded
            + " missing=" + missing
            + " bad=" + bad);

        if (missing != 0 || bad != 0) {
            throw new IllegalStateException("Wave1198 CDXMemBuffer normalization failed: missing=" + missing + " bad=" + bad);
        }
        if (!dryRun) {
            println("REPORT: Save succeeded");
        }
    }

    private Set<String> tagNames(Function function) {
        Set<String> names = new HashSet<>();
        for (FunctionTag tag : function.getTags()) {
            names.add(tag.getName());
        }
        return names;
    }
}
