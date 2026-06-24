//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionTag;

import java.util.HashSet;
import java.util.Set;

public class ApplyParticleEffectLinkCommentRefreshWave477 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String comment;

        Spec(String address, String name, String comment) {
            this.address = address;
            this.name = name;
            this.comment = comment;
        }
    }

    private static final String[] TAGS = {
        "particle-effect-link-wave477",
        "comment-hardened",
        "retail-binary-evidence"
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

    private Set<String> tagNames(Function fn) {
        Set<String> names = new HashSet<>();
        for (FunctionTag tag : fn.getTags()) {
            names.add(tag.getName());
        }
        return names;
    }

    private boolean needsUpdate(Function fn, Spec spec) {
        if (!spec.comment.equals(fn.getComment())) {
            return true;
        }
        Set<String> actualTags = tagNames(fn);
        for (String tag : TAGS) {
            if (!actualTags.contains(tag)) {
                return true;
            }
        }
        return false;
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");
        println("Mode: " + (dryRun ? "dry" : "apply"));

        Spec[] specs = new Spec[] {
            new Spec(
                "0x0047cea0",
                "CGroundUnit__ClearLinkedThingFlagsAndResetCounter",
                "Wave477 comment refresh: walks the GroundUnit linked set at +0x1d4, calls ParticleEffectLink__SetHandleStateAndClear for each particle/effect owner-link cell, and clears +0x1e4. This supersedes the older CUnitAI owner label and the older CUnit-specific callee wording. Static retail-binary evidence only; exact source identity, concrete linked-set layout, runtime behavior, and rebuild parity remain unproven."
            ),
            new Spec(
                "0x004ba490",
                "CMine__VFunc02_CleanupLinkedParticleAndForward",
                "Wave477 comment refresh after callee owner correction: CMine virtual cleanup checks this+0x264, clears the linked particle/effect owner-link cell through ParticleEffectLink__SetHandleStateAndClear, removes the node from the particle manager/global list, frees it, then forwards to VFuncSlot_02_004f95d0. Static retail evidence only; exact virtual slot, linked-cell layout, and runtime cleanup behavior remain unproven."
            ),
            new Spec(
                "0x004f84e0",
                "CUnit__dtor_base",
                "Wave477 comment refresh: CUnit destructor-base resets CUnit vtable pointers, tears down observed particle/effect owner-link cells through ParticleEffectLink__SetHandleStateAndClear, clears several CSPtrSet-style lists, removes owner links at observed offsets, then delegates to CActor__dtor_base. Runtime unit cleanup behavior, exact CUnit/owner-link layouts, exact source identity, and rebuild parity remain unproven."
            )
        };

        int updated = 0;
        int skipped = 0;
        int missing = 0;
        int bad = 0;

        for (Spec spec : specs) {
            try {
                Function fn = functionAtEntry(spec.address);
                if (fn == null) {
                    missing++;
                    println("FAIL: " + spec.address + " Function not found");
                    continue;
                }
                if (!fn.getName().equals(spec.name)) {
                    throw new IllegalStateException("Unexpected function name: " + fn.getName());
                }

                if (dryRun) {
                    println("DRY: " + spec.address + " " + fn.getName() + " comment refresh");
                    skipped++;
                    continue;
                }

                if (needsUpdate(fn, spec)) {
                    fn.setComment(spec.comment);
                    for (String tag : TAGS) {
                        fn.addTag(tag);
                    }
                    updated++;
                } else {
                    skipped++;
                }

                Function readBack = functionAtEntry(spec.address);
                if (readBack == null) {
                    throw new IllegalStateException("Read-back missing");
                }
                if (!spec.comment.equals(readBack.getComment())) {
                    throw new IllegalStateException("Read-back comment mismatch");
                }
                Set<String> actualTags = tagNames(readBack);
                for (String tag : TAGS) {
                    if (!actualTags.contains(tag)) {
                        throw new IllegalStateException("Read-back missing tag: " + tag);
                    }
                }
                println("OK: " + spec.address + " " + readBack.getName() + " comment refreshed");
            } catch (Exception ex) {
                bad++;
                println("FAIL: " + spec.address + " " + ex.getMessage());
            }
        }

        println("--- SUMMARY ---");
        println(
            "updated=" + updated +
            " skipped=" + skipped +
            " created=0 would_create=0 renamed=0 would_rename=0" +
            " missing=" + missing +
            " bad=" + bad
        );

        if (missing != 0 || bad != 0) {
            throw new IllegalStateException("Wave477 comment refresh had missing/bad targets");
        }
    }
}
