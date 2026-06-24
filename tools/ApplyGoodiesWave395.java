//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionTag;

import java.util.HashSet;
import java.util.Set;

public class ApplyGoodiesWave395 extends GhidraScript {
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

    private Function functionAtEntry(String addressText) {
        if (!addressText.startsWith("0x") && !addressText.startsWith("0X")) {
            addressText = "0x" + addressText;
        }
        Address address = toAddr(addressText);
        Function fn = getFunctionAt(address);
        if (fn == null) {
            fn = getFunctionContaining(address);
            if (fn != null && !fn.getEntryPoint().equals(address)) {
                fn = null;
            }
        }
        return fn;
    }

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "goodies-wave395",
            "frontend-goodies",
            "retail-binary-evidence"
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

    private void applySpec(Spec spec, boolean dryRun, Stats stats) {
        try {
            Function fn = functionAtEntry(spec.address);
            if (fn == null) {
                stats.missing++;
                println("FAIL: missing function at " + spec.address + " for " + spec.name);
                return;
            }
            if (!fn.getName().equals(spec.name)) {
                throw new IllegalStateException("Unexpected function name at " + spec.address + ": " + fn.getName());
            }
            String actualSignature = fn.getSignature().toString();
            if (!actualSignature.equals(spec.signature)) {
                throw new IllegalStateException("Unexpected signature at " + spec.address + ": " + actualSignature);
            }

            if (dryRun) {
                println("DRY: " + spec.address + " " + spec.name + " -> comment/tags");
                stats.skipped++;
                return;
            }

            fn.setComment(spec.comment);
            for (String tag : spec.tags) {
                fn.addTag(tag);
            }

            Function readBack = functionAtEntry(spec.address);
            if (readBack == null) {
                throw new IllegalStateException("Read-back missing at " + spec.address);
            }
            if (!spec.comment.equals(readBack.getComment())) {
                throw new IllegalStateException("Read-back comment mismatch at " + spec.address);
            }
            Set<String> readBackTags = tagNames(readBack);
            for (String tag : spec.tags) {
                if (!readBackTags.contains(tag)) {
                    throw new IllegalStateException("Read-back missing tag " + tag + " at " + spec.address);
                }
            }

            println("OK: " + spec.address + " " + spec.name + " -> comment/tags");
            stats.updated++;
            Thread.sleep(50);
        } catch (Exception ex) {
            stats.bad++;
            println("FAIL: " + spec.address + " " + spec.name + " " + ex.getMessage());
        }
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");
        println("Mode: " + (dryRun ? "dry" : "apply"));

        Spec[] specs = new Spec[] {
            new Spec(
                "0x0045ac30",
                "CFEPGoodies__BuildStaticGoodieDataTable",
                "void CFEPGoodies__BuildStaticGoodieDataTable(void)",
                "Wave395 comment/tag hardening: materializes the retail Goodies metadata table by writing contiguous CGoodieData-style records and repeatedly calling CGoodieData__ctor for the tail entries. Static/source-parity evidence only; exact table ownership/layout, runtime unlock/display behavior, and rebuild parity remain unproven.",
                tags("goodie-data-table", "comment-hardened")
            ),
            new Spec(
                "0x0045c770",
                "CGoodieData__ctor",
                "void __thiscall CGoodieData__ctor(void * this, int method, int method2, int number, int number2, int t1, int t2)",
                "Wave395 comment/tag hardening: writes Method, Method2, Number, Number2, mT1, and mT2 into the six 4-byte CGoodieData fields used by the Goodies metadata table. Static/source-parity evidence only; enum names and concrete structure typing remain unproven.",
                tags("goodie-data-table", "goodie-record", "comment-hardened")
            ),
            new Spec(
                "0x0045c870",
                "CFEPGoodies__Deserialise",
                "void __thiscall CFEPGoodies__Deserialise(void * this, void * chunk_reader)",
                "Wave395 comment/tag hardening: frees any current payload, reads the GDAT payload type from the chunk reader, then deserializes image/mesh Goodie resources into texture pointer array, texture count/height, and mesh slot state with refcount increments. Static retail evidence only; exact chunk structs, asset payload completeness, runtime playback/viewer behavior, and rebuild parity remain unproven.",
                tags("resource-deserialise", "gdatie-gdat", "comment-hardened")
            ),
            new Spec(
                "0x0045c9f0",
                "CFEPGoodies__StartLoadingGoody",
                "void __fastcall CFEPGoodies__StartLoadingGoody(void * this)",
                "Wave395 comment/tag hardening: resets image pan offsets, maps current grid coordinates through get_goodie_number, builds the -1000-goodie resource filename, stores current Goodie type, and either starts the async 5MB resource load or marks FMV/level/cheat types loaded. Static/source-parity evidence only; runtime load timing and asset coverage remain unproven.",
                tags("async-goodie-load", "goodie-resource-filename", "comment-hardened")
            ),
            new Spec(
                "0x0045cb80",
                "get_goodie_number",
                "int __cdecl get_goodie_number(int x, int y)",
                "Wave395 comment/tag hardening: maps Goodies wall grid coordinates to retail Goodie ids: row 0 covers bios/race/dev ids, row 1 unit ids, row 2 FMV ids, row 3 artwork/model ids, returning -1 for invalid cells. Static/source-parity evidence only; hidden reachability and UI navigation behavior remain unproven.",
                tags("goodie-grid", "goodie-id-map", "comment-hardened")
            ),
            new Spec(
                "0x0045cc10",
                "CFEPGoodies__LoadingGoodyPoll",
                "void __fastcall CFEPGoodies__LoadingGoodyPoll(void * this)",
                "Wave395 comment/tag hardening: when the async Goodie load has completed and a membuffer exists, reads the -1000-goodie resource, closes/frees the buffer, clears loader state, and marks the current Goodie loaded. Static/source-parity evidence only; runtime async behavior and asset decode success remain unproven.",
                tags("async-goodie-load", "resource-poll", "comment-hardened")
            ),
            new Spec(
                "0x0045cd10",
                "CFEPGoodies__FreeUpGoodyResources",
                "void __fastcall CFEPGoodies__FreeUpGoodyResources(void * this)",
                "Wave395 comment/tag hardening: releases current Goodie mesh and texture payloads, destroys texture backing resources, frees the texture pointer array, clears counters/slots, and resets Goodie state to NO_GOODY. Static retail evidence only; allocator/layout/runtime completeness remain unproven.",
                tags("resource-cleanup", "goodie-resource-lifetime", "comment-hardened")
            ),
            new Spec(
                "0x0045cde0",
                "CFEPGoodies__ButtonPressed",
                "void __thiscall CFEPGoodies__ButtonPressed(void * this, int button, float val)",
                "Wave395 comment/tag hardening: handles Goodies wall navigation and display controls, updates mCX/mCY-style grid coordinates through get_goodie_number, starts loading selectable unlocked/cheat-overridden Goodies, marks viewed entries old, and frees resources on back/close paths. Static/source-parity evidence only; runtime input behavior, hidden reachability, and asset-viewer parity remain unproven.",
                tags("goodies-input", "goodie-grid", "comment-hardened")
            )
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }

        println(
            "SUMMARY updated=" + stats.updated +
            " skipped=" + stats.skipped +
            " missing=" + stats.missing +
            " bad=" + stats.bad
        );
    }
}
