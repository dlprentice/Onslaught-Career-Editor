//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.FunctionTag;
import ghidra.program.model.listing.Parameter;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyWorldPhysicsLoadResolveWave846 extends GhidraScript {
    private static final String CALLING_CONVENTION = "__cdecl";

    private static class Spec {
        final String address;
        final String name;
        final String comment;
        final String[] tags;

        Spec(String address, String name, String comment, String[] tags) {
            this.address = address;
            this.name = name;
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
            "worldphysics-load-resolve-wave846",
            "wave846-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "signature-hardened",
            "worldphysicsmanager",
            "definition-list",
            "load-resolve"
        };
        String[] result = new String[common.length + extras.length];
        System.arraycopy(common, 0, result, 0, common.length);
        System.arraycopy(extras, 0, result, common.length, extras.length);
        return result;
    }

    private boolean sameDataType(DataType actual, DataType expected) {
        if (actual == null || expected == null) {
            return actual == expected;
        }
        return actual.isEquivalent(expected) || actual.getDisplayName().equals(expected.getDisplayName());
    }

    private ParameterImpl[] noParams() {
        return new ParameterImpl[] {};
    }

    private String expectedSignature(Spec spec) {
        return "void " + CALLING_CONVENTION + " " + spec.name + "(void)";
    }

    private boolean signatureMatches(Function fn, Spec spec) {
        if (!CALLING_CONVENTION.equals(fn.getCallingConventionName())) {
            return false;
        }
        if (!sameDataType(fn.getReturnType(), VoidDataType.dataType)) {
            return false;
        }
        if (fn.getParameterCount() != 0) {
            return false;
        }
        for (Parameter ignored : fn.getParameters()) {
            return false;
        }
        return fn.getSignature().toString().equals(expectedSignature(spec));
    }

    private boolean hasAllTags(Function fn, String[] tags) {
        Set<String> existing = new HashSet<>();
        for (FunctionTag tag : fn.getTags()) {
            existing.add(tag.getName());
        }
        for (String tag : tags) {
            if (!existing.contains(tag)) {
                return false;
            }
        }
        return true;
    }

    private boolean alreadyApplied(Function fn, Spec spec) {
        return fn.getName().equals(spec.name)
            && signatureMatches(fn, spec)
            && spec.comment.equals(fn.getComment())
            && hasAllTags(fn, spec.tags);
    }

    private void verifyReadBack(Spec spec) throws Exception {
        Function readback = functionAtEntry(spec.address);
        if (readback == null) {
            throw new IllegalStateException("Readback missing function at " + spec.address);
        }
        if (!alreadyApplied(readback, spec)) {
            throw new IllegalStateException("Readback mismatch at " + spec.address + ": " +
                readback.getName() + " " + readback.getSignature().toString() + " convention=" +
                readback.getCallingConventionName());
        }
    }

    private void applySpec(Spec spec, boolean dryRun, Stats stats) {
        try {
            Function fn = functionAtEntry(spec.address);
            if (fn == null) {
                println("MISSING: " + spec.address + " " + spec.name);
                stats.missing++;
                return;
            }
            if (!fn.getName().equals(spec.name)) {
                println("BADNAME: " + spec.address + " " + fn.getName() + " expected " + spec.name);
                stats.bad++;
                return;
            }

            boolean needsSignature = !signatureMatches(fn, spec);
            boolean needsComment = !spec.comment.equals(fn.getComment());
            boolean needsTags = !hasAllTags(fn, spec.tags);
            if (!needsSignature && !needsComment && !needsTags) {
                println("SKIP: " + spec.address + " " + spec.name + " already current");
                stats.skipped++;
                return;
            }

            if (dryRun) {
                println("DRY: " + spec.address + " " + fn.getName()
                    + " needsRename=false"
                    + " needsSignature=" + needsSignature
                    + " needsComment=" + needsComment
                    + " needsTags=" + needsTags);
                stats.skipped++;
                if (needsSignature) {
                    stats.signatureUpdated++;
                } else if (needsComment || needsTags) {
                    stats.commentOnlyUpdated++;
                }
                return;
            }

            if (needsSignature) {
                fn.setCallingConvention(CALLING_CONVENTION);
                fn.setReturnType(VoidDataType.dataType, SourceType.USER_DEFINED);
                fn.replaceParameters(
                    FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS,
                    true,
                    SourceType.USER_DEFINED,
                    noParams()
                );
                stats.signatureUpdated++;
            } else if (needsComment || needsTags) {
                stats.commentOnlyUpdated++;
            }
            if (needsComment) {
                fn.setComment(spec.comment);
            }
            for (String tag : spec.tags) {
                fn.addTag(tag);
            }

            verifyReadBack(spec);
            println("READBACK_OK: " + spec.address + " " + spec.name + " " + functionAtEntry(spec.address).getSignature().toString());
            stats.updated++;
        } catch (Exception ex) {
            println("FAIL: " + spec.address + " " + spec.name + " " + ex.getClass().getSimpleName() + ": " + ex.getMessage());
            stats.bad++;
        }
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = true;
        if (args != null && args.length > 0) {
            dryRun = isDryRun(args[0]);
        }

        Spec[] specs = new Spec[] {
            new Spec(
                "0x00510520",
                "CWorldPhysicsManager__ResolveLoadedDefinitionReferences",
                "Wave846 static read-back/signature/comment hardening: post-load WorldPhysicsManager definition-reference resolver reached from CGame__LoadResources at 0x0046cdd7 with no pushed arguments or ECX receiver setup. The body iterates loaded definition lists DAT_008553ec, DAT_008553f0, DAT_008553f8, DAT_008553fc, DAT_00855400, DAT_00855404, and DAT_00855408; calls the Wave560 resolver helpers for weapon-mode, tag, thing, and component definitions; resolves particle-set names through CParticleSet__FindByNameAndTrackLinkSlot; and resolves sound-effect names through CSoundManager__GetEffectByName. Static retail Ghidra evidence only; exact definition schemas, source method identity, runtime resolve behavior, BEA patching, and rebuild parity remain deferred.",
                tags("resolve-pass", "particle-set-link", "sound-effect-link", "wave560-context")
            ),
            new Spec(
                "0x00510740",
                "CWorldPhysicsManager__FreeNestedThingSets_6C",
                "Wave846 static read-back/signature/comment hardening: shutdown helper reached from CGame__ShutdownRestartLoop at 0x0046cc61 with no pushed arguments or ECX receiver setup. The body walks DAT_008553fc thing definitions and DAT_00855400 component definitions, drains each entry's nested CSPtrSet at +0x6c with CSPtrSet__Remove, and frees every removed child through CDXMemoryManager__Free. Static retail Ghidra evidence only; exact child object schema, runtime shutdown ordering, source method identity, BEA patching, and rebuild parity remain deferred.",
                tags("nested-set-drain", "thing-definition", "component-definition", "shutdown-cleanup")
            ),
            new Spec(
                "0x00510800",
                "CWorldPhysicsManager__ReloadDefaultPhysicsAndBattleEngineData",
                "Wave846 static read-back/signature/comment hardening: reload entry reached from CLTShell__InitializeRuntimeAndLoadCoreResources at 0x004f0092 with no pushed arguments or ECX receiver setup. The body clears all WorldPhysicsManager definition lists via CWorldPhysicsManager__ClearAndFreeAllDefinitionLists, reinitializes them via CWorldPhysicsManager__InitializeLists, loads data/default_physics.dat through CDXMemBuffer and CPhysicsScript, drains DAT_006602a0 BattleEngineData entries, creates a default CBattleEngineData entry, then loads data/battle_engine_configuration into replacement CBattleEngineData rows. Static retail Ghidra evidence only; exact BattleEngineData schema, runtime reload behavior, source method identity, BEA patching, and rebuild parity remain deferred.",
                tags("reload-path", "default-physics", "battle-engine-data", "mem-buffer")
            ),
            new Spec(
                "0x00510a90",
                "CWorldPhysicsManager__ClearAndFreeAllDefinitionLists",
                "Wave846 static read-back/signature/comment hardening: global WorldPhysicsManager teardown entry reached from CLTShell__ShutdownRuntimeAndReleaseResources at 0x004f00e0 and CWorldPhysicsManager__ReloadDefaultPhysicsAndBattleEngineData at 0x0051081e with no pushed arguments or ECX receiver setup. The body drains DAT_006602a0 BattleEngineData entries, then removes and frees entries from definition-list globals DAT_008553e8 through DAT_00855408 using the Wave559 per-entry cleanup helpers, the spawner-node vfunc scalar delete path, direct owned-pointer frees for DAT_00855408, and final CSPtrSet__Clear/free/null operations for every list container. Static retail Ghidra evidence only; exact list/container schemas, runtime teardown behavior, source method identity, BEA patching, and rebuild parity remain deferred.",
                tags("global-teardown", "battle-engine-data", "definition-cleanup", "wave559-context")
            )
        };

        Stats stats = new Stats();
        println("ApplyWorldPhysicsLoadResolveWave846 mode=" + (dryRun ? "dry" : "apply") + " targets=" + specs.length);
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
        if (stats.bad != 0 || stats.missing != 0) {
            throw new IllegalStateException("Wave846 had bad=" + stats.bad + " missing=" + stats.missing);
        }
    }
}
