//@category BEA

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionManager;
import ghidra.program.model.listing.FunctionTag;

import java.util.Arrays;
import java.util.HashSet;
import java.util.Set;

public class ApplyParticleDescriptorTokenArchiveCurrentRiskWave1190 extends GhidraScript {
    private static class Target {
        final String address;
        final String name;
        final String signature;
        final String comment;
        final String[] tags;

        Target(String address, String name, String signature, String comment, String[] tags) {
            this.address = address;
            this.name = name;
            this.signature = signature;
            this.comment = comment;
            this.tags = tags;
        }
    }

    private static final String[] COMMON_TAGS = {
        "static-reaudit",
        "wave1190-particle-descriptor-token-archive-current-risk-review",
        "wave1190-readback-verified",
        "retail-binary-evidence",
        "current-risk-review",
        "particle-descriptor",
        "token-archive",
        "token-writer",
        "source-identity-deferred",
        "exact-layout-deferred",
        "rebuild-grade-static-contract",
        "no-noticeable-difference-boundary",
        "comment-hardened",
        "tag-normalized"
    };

    private static final Target[] TARGETS = {
        tokenWriter(
            "0x004c07f0",
            "CPDSimpleSprite__WriteTokenFields",
            "void __fastcall CPDSimpleSprite__WriteTokenFields(void * this)",
            "CPDSimpleSprite",
            "0x005ddf7c",
            "tokens 6 through 0x1b",
            "simple-sprite"
        ),
        tokenWriter(
            "0x004c1970",
            "CPDEmitter__WriteTokenFields",
            "void __fastcall CPDEmitter__WriteTokenFields(void * this)",
            "CPDEmitter",
            "0x005ddf14",
            "tokens 0x1a through 0x28",
            "emitter"
        ),
        tokenWriter(
            "0x004c2220",
            "CPDSelector__WriteTokenFields",
            "void __fastcall CPDSelector__WriteTokenFields(void * this)",
            "CPDSelector",
            "0x005dde44",
            "pointer/int tokens 0x29 through 0x30",
            "selector"
        ),
        tokenWriter(
            "0x004c2400",
            "CPDColourRange__WriteTokenFields",
            "void __fastcall CPDColourRange__WriteTokenFields(void * this)",
            "CPDColourRange",
            "0x005ddddc",
            "float/int tokens 0x31 through 0x3c",
            "colour-range"
        ),
        tokenWriter(
            "0x004c2ca0",
            "CPDShape__WriteTokenFields",
            "void __fastcall CPDShape__WriteTokenFields(void * this)",
            "CPDShape",
            "0x005ddd0c",
            "int/float tokens 0x3f through 0x46 plus token 6",
            "shape"
        ),
        tokenWriter(
            "0x004c3440",
            "CPDTrail__WriteTokenFields",
            "void __fastcall CPDTrail__WriteTokenFields(void * this)",
            "CPDTrail",
            "0x005ddca4",
            "trail tokens 0x47 through 0x54",
            "trail"
        ),
        tokenWriter(
            "0x004c4920",
            "CPDFunction__WriteTokenFields",
            "void __fastcall CPDFunction__WriteTokenFields(void * this)",
            "CPDFunction",
            "0x005ddbd4",
            "function-curve tokens 0x5c through 0x64",
            "function-curve"
        ),
        tokenWriter(
            "0x004c4c70",
            "CPDMesh__WriteTokenFields",
            "void __fastcall CPDMesh__WriteTokenFields(void * this)",
            "CPDMesh",
            "0x005ddb58",
            "mesh tokens 0x65 through 0x68",
            "mesh"
        ),
        tokenWriter(
            "0x004c53b0",
            "CPDFoR__WriteTokenFields",
            "void __fastcall CPDFoR__WriteTokenFields(void * this)",
            "CPDFoR",
            "0x005ddfe4",
            "frame-of-reference pointer tokens 0x69, 0x6a, and 0x28",
            "frame-of-reference"
        ),
        tokenWriter(
            "0x004c59e0",
            "CPDPMesh__WriteTokenFields",
            "void __fastcall CPDPMesh__WriteTokenFields(void * this)",
            "CPDPMesh",
            "0x005de04c",
            "particle-mesh tokens 0x6b through 0x7b",
            "particle-mesh"
        ),
        new Target(
            "0x004f5b70",
            "CTokenArchive__BindIndexedFieldPointer",
            "void __thiscall CTokenArchive__BindIndexedFieldPointer(void * this, int slot_index, void * field_ptr)",
            "Wave1190 static read-back: TokenArchive indexed field-pointer binder retained from the Wave1031 owner/name correction. The body stores field_ptr into the archive slot table at this+0x0c+(slot_index*4) and returns with RET 0x8. Fresh Wave1190 xrefs verify CParticleDescriptor__Load callsites 0x004c57d4/0x004c57e9 plus thirteen adjacent particle descriptor token-load callsites that push descriptor field addresses, push the parsed slot index, load ECX with the TokenArchive receiver, then call this helper. Adjacent CTokenArchive__RegisterReferenceFixup writes fixup_record+4 into the same slot-table shape. Static retail Ghidra metadata/xref/decompile/instruction evidence only; exact TokenArchive concrete layout, exact descriptor field enum/source identity, runtime particle parsing/linking behavior, BEA patching, rebuild parity, and clean-room/no-noticeable-difference parity remain separate proof.",
            withCommon("indexed-field-binder", "ret-0x8", "particle-descriptor-load")
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
            Set<String> requiredTags = new HashSet<>(Arrays.asList(target.tags));
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
                    for (String tag : target.tags) {
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
            throw new IllegalStateException("Wave1190 particle descriptor/token archive normalization failed: missing=" + missing + " bad=" + bad);
        }
        if (!dryRun) {
            println("REPORT: Save succeeded");
        }
    }

    private static Target tokenWriter(String address, String name, String signature, String owner, String vtableRef, String tokenSpan, String specificTag) {
        return new Target(
            address,
            name,
            signature,
            "Wave1190 static read-back: " + owner + " vtable slot 7 token-field writer at DATA vtable ref " + vtableRef + ". Fresh metadata/xref/decompile/instruction evidence keeps the Wave461 token-writer correction intact: this row emits " + tokenSpan + " through CTokenArchive__Write* helpers as part of the particle descriptor serialization spine. Static token serialization metadata only; exact descriptor concrete layout, exact source virtual/source-body identity, runtime particle loading/rendering behavior, BEA patching, rebuild parity, and clean-room/no-noticeable-difference parity remain separate proof.",
            withCommon("slot-7-token-writer", specificTag)
        );
    }

    private static String[] withCommon(String... extraTags) {
        String[] tags = new String[COMMON_TAGS.length + extraTags.length];
        System.arraycopy(COMMON_TAGS, 0, tags, 0, COMMON_TAGS.length);
        System.arraycopy(extraTags, 0, tags, COMMON_TAGS.length, extraTags.length);
        return tags;
    }

    private Set<String> tagNames(Function function) {
        Set<String> names = new HashSet<>();
        for (FunctionTag tag : function.getTags()) {
            names.add(tag.getName());
        }
        return names;
    }
}
